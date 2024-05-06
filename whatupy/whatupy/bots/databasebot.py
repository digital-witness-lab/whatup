import logging
import typing as T
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial, reduce

import dataset
import grpc
from cloudpathlib import AnyPath
from dataset.util import DatasetException
from google.protobuf.timestamp_pb2 import Timestamp
from sqlalchemy.sql import func

from .. import utils
from ..protos import whatupcore_pb2 as wuc
from . import ArchiveData, BaseBot, BotCommandArgs, MediaType

logger = logging.getLogger(__name__)


IGNORED_FIELDS = set(("originalMessage", "mediaMessage"))
RECORD_MTIME_FIELD = "record_mtime"


def flatten_proto_message(
    proto_obj,
    preface_keys=False,
    prev_keys: T.Optional[T.Iterable[str]] = None,
    sep="_",
    skip_keys=None,
):
    prev_keys = prev_keys or []
    skip_keys = skip_keys or set()
    flat = {}
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    key: str
    for key in key_list:
        key_proto = key
        if key_proto in skip_keys:
            continue
        if preface_keys:
            key = sep.join((*prev_keys, key))

        obj: T.Any = getattr(proto_obj, key_proto)
        if isinstance(obj, wuc.JID):
            jid_key = key
            if "jid" not in jid_key.lower():
                jid_key = f"{jid_key}_jid"
            flat[jid_key] = utils.jid_to_str(obj)
            flat[f"{key}_country_iso"] = obj.userGeocode
            continue
        elif isinstance(obj, Timestamp):
            obj = obj.ToDatetime()
        elif hasattr(obj, "items"):
            obj = dict(obj)
        elif hasattr(obj, "append"):
            new_obj = []
            for item in obj:
                if utils.is_filled_pbuf(item):
                    item = flatten_proto_message(
                        item,
                        preface_keys=preface_keys,
                        prev_keys=(*prev_keys, key_proto),
                        sep=sep,
                        skip_keys=skip_keys,
                    )
                elif utils.is_empty_pbuf(item):
                    continue
                if item:
                    new_obj.append(item)
            obj = new_obj
        elif key in IGNORED_FIELDS:
            continue

        if utils.is_filled_pbuf(obj):
            flat.update(
                flatten_proto_message(
                    obj,
                    preface_keys=preface_keys,
                    prev_keys=(*prev_keys, key_proto),
                    sep=sep,
                    skip_keys=skip_keys,
                )
            )
        elif utils.is_empty_pbuf(obj):
            continue
        elif obj:
            flat[key] = obj
    return flat


class DatabaseBot(BaseBot):
    __version__ = "3.0.0"
    __db_cache: T.Dict[str, dataset.Database] = {}

    def __init__(
        self,
        database_url: str,
        media_base_path: AnyPath,
        group_info_refresh_time: timedelta = timedelta(hours=6),
        *args,
        **kwargs,
    ):
        kwargs["mark_messages_read"] = True
        kwargs["read_historical_messages"] = True
        super().__init__(*args, **kwargs)
        self.media_base_path: AnyPath = media_base_path
        self.group_info_refresh_time = group_info_refresh_time
        self.db: dataset.Database = DatabaseBot.__db_connect(database_url)
        self.init_database(self.db)

    @classmethod
    def __db_connect(cls, database_url) -> dataset.Database:
        url_hash = utils.short_hash(database_url, N=None)
        if url_hash not in cls.__db_cache:
            cls.__db_cache[url_hash] = dataset.connect(database_url)
        return cls.__db_cache[url_hash]

    def init_database(self, db):
        group_info = db.create_table(
            "group_info",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        group_info.create_column(
            "JID",
            type=db.types.text,
        )
        group_info.create_column(
            "donor_jid",
            type=db.types.text,
        )
        group_info.create_column(
            "timestamp",
            type=db.types.datetime,
        )
        group_info.create_index(["JID", "timestamp"])

        group_participants = db.create_table("group_participants")
        try:
            group_participants.create_index(["chat_jid"])
            group_participants.create_index(["chat_jid", "JID"])
        except DatasetException:
            self.logger.warn(
                "Could not create group_participants indices because table doesn't exist yet"
            )
        group_participants.create_column(
            "first_seen", type=db.types.datetime, server_default=func.now()
        )

        db.create_table(
            "messages",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        db.create_table(
            "reactions",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        media = db.create_table(
            "media",
            primary_id="filename",
            primary_type=db.types.text,
            primary_increment=False,
        )
        media.create_column(
            "content_url",
            type=db.types.string,
        )
        media.create_column(
            "error",
            type=db.types.string,
        )
        db.create_table(
            "messages_seen",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )

        donor_messages = db.create_table("donor_messages")
        donor_messages.create_column("donor_jid", type=db.types.text)
        donor_messages.create_column("message_id", type=db.types.text)
        donor_messages.create_column(RECORD_MTIME_FIELD, type=db.types.datetime)
        try:
            donor_messages.create_index(["donor_jid", "message_id"])
        except DatasetException:
            self.logger.warn(
                "Could not create donor_messages indices because table doesn't exist yet"
            )

    def _ping_donor_messages(self, message: wuc.WUMessage):
        donor_jid = utils.jid_to_str(message.info.source.reciever)
        datum = {
            "donor_jid": donor_jid,
            "message_id": message.info.id,
            RECORD_MTIME_FIELD: datetime.now(),
        }
        self.db["donor_messages"].upsert(datum, ["donor_jid", "message_id"])

    async def on_message(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        is_history: bool,
        archive_data: ArchiveData,
        **kwargs,
    ):
        msg_id = message.info.id
        media_filename = utils.media_message_filename(message)

        message.provenance["databasebot__timestamp"] = datetime.now().isoformat()
        message.provenance["databasebot__version"] = self.__version__
        # provenance only supports Dict[str, str]
        message.provenance.update({str(k): str(v) for k, v in self.meta.items()})

        self._ping_donor_messages(message)
        if not self.db["messages_seen"].count(id=msg_id):
            self.db["messages_seen"].insert({"id": msg_id, **message.provenance})
            if message.messageProperties.isReaction:
                await self._update_reaction(message)
            elif message.messageProperties.isEdit:
                await self._update_edit(message)
            elif message.messageProperties.isDelete:
                source_message_id = message.content.inReferenceToId
                with self.db as db:
                    db["messages"].upsert(
                        {"id": source_message_id, "isDelete": True}, ["id"]
                    )
            else:
                await self._update_message(
                    message,
                    is_archive,
                    is_history,
                    archive_data,
                    media_filename=media_filename,
                )

        if media_filename:
            existingMedia = self.db["media"].count(
                filename=media_filename, content_url={"not": None}
            )
            if not existingMedia:
                self.logger.debug(
                    "Getting media: %s: %s: %s",
                    utils.jid_to_str(message.info.source.chat),
                    message.info.id,
                    media_filename,
                )
                await self._update_media(
                    message,
                    is_archive,
                    archive_data,
                    media_filename=media_filename,
                )

        if message.info.source.isGroup and not is_history:
            self.logger.debug("Updating group or community groups: %s", message.info.id)
            await self._update_group_or_community(
                message.info.source.chat,
                message.info.source.reciever,
                is_archive,
                archive_data,
            )
            self.logger.debug(
                "Done updating group or community groups: %s", message.info.id
            )

    async def _update_media(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        archive_data: ArchiveData,
        media_filename: T.Optional[str] = None,
    ):
        media_filename = media_filename or utils.media_message_filename(message)
        if not media_filename:
            self.logger.warn(
                "Could not get media filename for media: %s",
                message.content.mediaMessage,
            )
            return
        mimetype = utils.media_message_mimetype(message)
        file_extension = media_filename.rsplit(".", 1)[-1]
        datum = {
            "filename": media_filename,
            "mimetype": mimetype,
            "fileExtension": file_extension,
            "timestamp": message.info.timestamp.ToDatetime(),
        }
        callback = partial(self._handle_media_content, datum=datum)
        if is_archive:
            mp = archive_data.MediaPath
            if mp is not None and mp.exists():
                content = mp.read_bytes()
                await callback(message, content, None)
            else:
                await callback(message, bytes(), Exception("No media in archive"))
        else:
            await self.download_message_media_eventually(message, callback)

    async def _update_message(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        is_history: bool,
        archive_data: ArchiveData,
        media_filename: T.Optional[str] = None,
    ):
        chat_jid = utils.jid_to_str(message.info.source.chat)
        message_flat = flatten_proto_message(message)
        media_filename = media_filename or utils.media_message_filename(message)
        if message_flat.get("thumbnail"):
            thumbnail: bytes = message_flat.pop("thumbnail")
            message_flat["thumbnail_url"] = self.write_media(
                thumbnail,
                f"{message.info.id}.jpg",
                [chat_jid, "thumbnail"],
            )
        with self.db as db:
            message_flat["mediaFilename"] = media_filename
            db["messages"].upsert(message_flat, ["id"])
        self.logger.debug("Done updating message: %s", message.info.id)

    def media_url(self, path_prefixes: T.List[str], filename: str) -> AnyPath:
        path_elements = [
            self.media_base_path,
            *path_prefixes,
            filename[0],
            filename[1],
            filename[2],
            filename[3],
            filename,
        ]
        return reduce(lambda a, b: a / b, path_elements)

    def write_media(
        self,
        content: bytes,
        filename: str,
        path_prefixes: T.Optional[T.List[str]],
    ) -> str:
        path_prefixes = path_prefixes or []
        filepath = self.media_url(path_prefixes, filename)
        filepath.parent.mkdir(exist_ok=True, parents=True)
        filepath.write_bytes(content)
        return str(filepath)

    async def _handle_media_content(
        self,
        message: wuc.WUMessage,
        content: bytes,
        error: Exception | None,
        datum: dict,
    ):
        if content:
            chat_jid = utils.jid_to_str(message.info.source.chat)
            datum["content_url"] = self.write_media(
                content, datum["filename"], [chat_jid, "media"]
            )
        else:
            self.logger.critical(
                "Empty media body... Writing empty media URI: %s", datum
            )
        datum["error"] = None if error is None else str(error)
        datum[RECORD_MTIME_FIELD] = datetime.now()
        self.db["media"].upsert(datum, ["filename"])

    async def _update_group_or_community(
        self,
        chat: wuc.JID,
        donor: wuc.JID,
        is_archive: bool,
        archive_data: ArchiveData,
    ):
        chat_jid = utils.jid_to_str(chat)
        donor_jid = utils.jid_to_str(donor)
        now = datetime.now()

        community_info: T.List[wuc.GroupInfo] | None = None
        group_info: wuc.GroupInfo | None = None
        if is_archive:
            if archive_data.CommunityInfo is not None:
                community_info = archive_data.CommunityInfo
            if archive_data.GroupInfo is not None:
                group_info = archive_data.GroupInfo
            if not (archive_data or community_info):
                return
            now = archive_data.WUMessage.info.timestamp.ToDatetime()
            self.logger.debug("Storing archived message timestamp: %s", now)
        else:
            group_info_prev = (
                self.db["group_info"].find_one(JID=chat_jid, donor_jid=donor_jid, order_by="-timestamp") or {}
            )
            last_update: datetime = group_info_prev.get("timestamp", datetime.min)
            if not is_archive and last_update + self.group_info_refresh_time > now:
                return
            try:
                group_info = await self.core_client.GetGroupInfo(chat)
                if group_info is None:
                    return
                if utils.jid_to_str(group_info.parentJID) is not None:
                    community_info_iterator: T.AsyncIterator[wuc.GroupInfo] = (
                        self.core_client.GetCommunityInfo(group_info.parentJID)
                    )
                    community_info = await utils.aiter_to_list(community_info_iterator)
            except grpc.aio._call.AioRpcError as e:
                if "rate-overlimit" in (e.details() or ""):
                    self.logger.warn("Rate Overlimit for group info: %s", chat_jid)
                    return

        if community_info is not None:
            self.logger.debug("Using community info to update groups for community")
            # FIX for old whatupcore that didn't fill in parentJID
            parentJID = next(gi.JID for gi in community_info if gi.isCommunity)
            for gi in community_info:
                if not gi.isCommunity and not gi.parentJID:
                    gi.parentJID.CopyFrom(parentJID)
            # end of fix
            for group_from_community in community_info:
                community_group_jid = utils.jid_to_str(group_from_community.JID)
                self.logger.debug(
                    "Inserting community group: %s",
                    community_group_jid,
                )
                with self.db as db:
                    await self._insert_group_info(
                        db,
                        group_from_community,
                        donor,
                        now,
                    )
        elif group_info is not None:
            self.logger.debug("Using group info to update group: %s", chat_jid)
            with self.db as db:
                await self._insert_group_info(
                    db, group_info, donor, now
                )
        elif not is_archive:
            self.logger.critical(
                "Both community_info and group_info are none...: %s", chat_jid
            )

    async def _update_group_participants(self, db: dataset.Database, update_time: datetime, chat_jid: str, group_participants_proto: T.Sequence[wuc.GroupParticipant]):
        now = datetime.now()
        group_participants = [flatten_proto_message(p) for p in group_participants_proto]
        participant_jids = list(p["JID"] for p in group_participants)
        table: dataset.Table = db.get_table("group_participants")
        group_participants_prev = table.find(
            chat_jid=chat_jid, JID={"in": participant_jids}
        )
        group_participants_prev_lookup = {
            gp["JID"]: gp for gp in group_participants_prev
        }
        for participant in group_participants:
            pjid = participant["JID"]
            if participant_prev := group_participants_prev_lookup.get(pjid):
                participant["first_seen"] = min(
                    participant_prev.get("first_seen", datetime.max), update_time
                )
                participant["last_seen"] = max(
                    participant_prev.get("last_seen", datetime.min), update_time
                )
            else:
                participant["first_seen"] = update_time
                participant["last_seen"] = update_time
            participant["chat_jid"] = chat_jid
            participant[RECORD_MTIME_FIELD] = now

        logger.debug("Updating participants for group/community: %s", chat_jid)
        table.upsert_many(group_participants, ["JID", "chat_jid"])

    async def _insert_group_info(
        self,
        db: dataset.Database,
        group_info: wuc.GroupInfo,
        donor: wuc.JID,
        update_time: datetime,
    ):
        now = datetime.now()
        chat_jid = utils.jid_to_str(group_info.JID)
        donor_jid = utils.jid_to_str(donor)
        if not chat_jid or not donor_jid:
            self.logger.critical("Could not get chat JID or donor JID string: %s: %s", donor, group_info)
            return
        logger = self.logger.getChild(chat_jid or "")
        db_provenance = {
            "databasebot__timestamp": datetime.now().isoformat(),
            "databasebot__version": self.__version__,
            "databasebot__donor": donor_jid,
            **self.meta,
        }

        await self._update_group_participants(db, update_time, chat_jid, group_info.participants)

        table: dataset.Table = db.get_table("group_info")
        group_info_hash = utils.group_info_hash(group_info)

        group_info_id = f"{chat_jid}-{donor_jid}-{group_info_hash}"
        if table.count(id=group_info_id) > 0:
            table.update({"last_seen": update_time, "id": group_info_id}, keys=["id"])
            return

        group_info_flat = flatten_proto_message(
            group_info,
            preface_keys=True,
            skip_keys=set(["participants", "participantVersionId"]),
        )
        group_info_flat["id"] = group_info_id
        group_info_flat["donor_jid"] = donor_jid
        group_info_flat["timestamp"] = update_time
        group_info_flat["last_seen"] = update_time
        group_info_flat["version_hash"] = group_info_hash
        group_info_flat["provenance"] = {**(group_info_flat.get("provenance") or {}), **db_provenance}
        group_info_flat[RECORD_MTIME_FIELD] = now

        table.insert(group_info_flat)
        logger.info("Updating group: %s", chat_jid)

    async def _update_edit(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
        message_flat[RECORD_MTIME_FIELD] = datetime.now()
        source_message_id = message.content.inReferenceToId
        message_flat["id"] = source_message_id
        with self.db as db:
            source_message = db["messages"].find_one(id=source_message_id)
            if source_message:
                n_edits: int = source_message.get("n_edits", 0) or 0
                N = message_flat["n_edits"] = n_edits + 1
                id_ = source_message["id"] = f"{source_message_id}-{N:03d}"
                message_flat["previous_version_id"] = id_
                message_flat["previous_version_text"] = source_message["text"]
                source_message[RECORD_MTIME_FIELD] = datetime.now()
                db["messages"].insert(source_message)
            db["messages"].upsert(message_flat, ["id"])

    async def _update_reaction(self, message: wuc.WUMessage):
        now = datetime.now()
        message_flat = flatten_proto_message(message)
        message_flat[RECORD_MTIME_FIELD] = now
        source_message_id = message.content.inReferenceToId
        with self.db as db:
            source_message = db["messages"].find_one(id=source_message_id)
            if not source_message:
                reaction_counts = defaultdict(int)
            else:
                reaction_counts = defaultdict(
                    int, source_message.get("reaction_counts") or {}
                )
            reaction_counts[message.content.text] += 1
            db["reactions"].upsert(message_flat, ["id"])
            db["messages"].upsert(
                {
                    "id": source_message_id,
                    "reaction_counts": reaction_counts,
                    RECORD_MTIME_FIELD: now,
                },
                ["id"],
            )

    def delete_groups(self, jids: T.List[str], delete_media=True):
        jids = list(jids)

        with self.db as tx:
            self.logger.info("Clearing messages_seen table")
            tx.query(
                """
                DELETE FROM messages_seen
                WHERE id in (
                    SELECT id
                    FROM messages
                    WHERE chat_jid = ANY( :jids )
                )
            """,
                jids=jids,
            )

            self.logger.info("Clearing reactions table")
            tx.query(
                """
                DELETE FROM reactions
                WHERE id in (
                    SELECT id
                    FROM messages
                    WHERE chat_jid = ANY( :jids )
                )
            """,
                jids=jids,
            )

            self.logger.info("Clearing media table")
            tx.query(
                """
                DELETE FROM media
                WHERE filename in (
                    SELECT filename
                    FROM messages
                    WHERE chat_jid = ANY( :jids ) AND filename IS NOT NULL
                )
            """,
                jids=jids,
            )

            self.logger.info("Clearing group_info table")
            tx.query(
                """
                DELETE FROM group_info
                WHERE "JID" = ANY( :jids )
            """,
                jids=jids,
            )

            self.logger.info("Clearing group_participants table")
            tx.query(
                """
                DELETE FROM group_participants
                WHERE chat_jid = ANY( :jids )
            """,
                jids=jids,
            )

            self.logger.info("Clearing messages table")
            tx.query(
                """
                DELETE FROM messages
                WHERE chat_jid = ANY( :jids )
            """,
                jids=jids,
            )

        if delete_media:
            for jid in jids:
                media_path = self.media_base_path / jid
                self.logger.info("Removing media path: %s", media_path)
                media_path.rmtree()
