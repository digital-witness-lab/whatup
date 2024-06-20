import logging
import typing as T
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial, reduce

import dataset
import grpc
from cloudpathlib import AnyPath
from dataset.util import DatasetException
from sqlalchemy.sql import func

from .. import utils
from ..protos import whatupcore_pb2 as wuc
from .lib import flatten_proto_message
from . import ArchiveData, BaseBot


logger = logging.getLogger(__name__)
RECORD_MTIME_FIELD = "record_mtime"


class DatabaseBot(BaseBot):
    __version__ = "3.1.0"
    __db_cache: T.Dict[str, dataset.Database] = {}

    def __init__(
        self,
        database_url: str,
        media_base_path: AnyPath,
        group_info_refresh_time: timedelta = timedelta(hours=6),
        *args,
        **kwargs,
    ):
        kwargs["read_historical_messages"] = True
        super().__init__(*args, **kwargs)
        self.media_base_path: AnyPath = media_base_path
        self.group_info_refresh_time = group_info_refresh_time
        self.db: dataset.Database = DatabaseBot.__db_connect(
            database_url, logger=self.logger
        )
        self.init_database(self.db)

    @classmethod
    def __db_connect(cls, database_url, logger=logger) -> dataset.Database:
        url_hash = utils.short_hash(database_url, N=None)
        if url_hash not in cls.__db_cache:
            logger.info("Using new DB connection")
            cls.__db_cache[url_hash] = dataset.connect(database_url)
        else:
            logger.info("Using cached DB connection")
        return cls.__db_cache[url_hash]

    def init_database(self, db):
        device_group_info = db.create_table(
            "device_group_info",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        device_group_info.create_column(
            "JID",
            type=db.types.text,
        )
        device_group_info.create_column(
            "donor_jid",
            type=db.types.text,
        )
        device_group_info.create_column(
            "timestamp",
            type=db.types.datetime,
        )
        device_group_info.create_index(["JID", "timestamp"])

        # <depricated>
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
        group_info.create_index(["JID"])

        db["group_info"].create_column(
            "first_seen", type=db.types.datetime, server_default=func.now()
        )
        db["group_info"].create_column(
            "last_update", type=db.types.datetime, server_default=func.now()
        )
        # </depricated>

        group_participants = db.create_table("group_participants")
        group_participants.create_column("chat_jid", type=db.types.string)
        group_participants.create_column("JID", type=db.types.string)
        group_participants.create_column("first_seen", type=db.types.datetime)
        group_participants.create_column("last_seen", type=db.types.datetime)
        group_participants.create_index(["chat_jid"])
        group_participants.create_index(["chat_jid", "JID"])

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
        donor_messages.create_index(["donor_jid", "message_id"])

    async def post_start(self):
        fields = (None, "isDelete", "isEdit", "isReaction")
        group_info = utils.protobuf_fill_fields(wuc.GroupInfo())
        group_info.JID.user = "filluser"
        group_info.JID.server = "fillmessage.test"
        message = utils.protobuf_fill_fields(
            wuc.WUMessage(), {"originalMessage", "mediaMessage"}
        )
        for i, toggle_field in enumerate(fields):
            message.info.id = f"fillmessage-{i:02d}"
            for field in fields:
                if field:
                    setattr(message.messageProperties, field, field == toggle_field)
            archive_data = ArchiveData(
                WUMessage=message,
                GroupInfo=group_info if i == 0 else None,
                CommunityInfo=None,
                MediaPath=None,
            )
            self.logger.info(
                "Inserting fully filled message into database: %s",
                toggle_field or "Normal Message",
            )
            await self.on_message(
                message,
                is_history=False,
                is_archive=True,
                archive_data=archive_data,
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
            # NOTE: if there is a new case here, make sure to update the
            # `post_start` method to handle it
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
            await self._update_device_group_or_community(
                message.info.source.chat,
                message.info.source.reciever,
                is_archive,
                archive_data,
            )

        # <depricated>
        if message.info.source.isGroup and not is_history:
            self.logger.debug("Updating group or community groups: %s", message.info.id)
            await self._update_group_or_community_old(
                message.info.source.chat,
                is_archive,
                archive_data,
            )
        # </depricated>

    async def _update_media(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        archive_data: ArchiveData,
        media_filename: T.Optional[str] = None,
    ):
        chat_jid = utils.jid_to_str(message.info.source.chat)
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
        content_url = self.media_url(media_filename, [str(chat_jid), "media"])
        try:
            if content_url.exists() and content_url.stat().st_size > 0:
                return await self._handle_media_content(
                    message,
                    content=None,
                    content_url=content_url,
                    datum=datum,
                    error=None,
                )
        except Exception:
            self.logger.exception(
                "Could not check existing content_url for existence or size"
            )

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
                [str(chat_jid), "thumbnail"],
            )
        with self.db as db:
            message_flat["mediaFilename"] = media_filename
            db["messages"].upsert(message_flat, ["id"])
        self.logger.debug("Done updating message: %s", message.info.id)

    def media_url(self, filename: str, path_prefixes: T.List[str]) -> AnyPath:
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
        content: bytes | None,
        filename: str,
        path_prefixes: T.Optional[T.List[str]],
    ) -> str:
        path_prefixes = path_prefixes or []
        filepath = self.media_url(filename, path_prefixes)
        filepath.parent.mkdir(exist_ok=True, parents=True)
        filepath.write_bytes(content)
        return str(filepath)

    async def _handle_media_content(
        self,
        message: wuc.WUMessage,
        content: bytes,
        error: Exception | None,
        datum: dict,
        content_url=None,
    ):
        if content_url is not None:
            datum["content_url"] = str(content_url)
        elif content:
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

    async def _update_device_group_or_community(
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
            table: dataset.Table = self.db.get_table("device_group_info")
            group_info_prev = (
                table.find_one(JID=chat_jid, donor_jid=donor_jid, order_by="-last_seen")
                or {}
            )
            last_seen: datetime = group_info_prev.get("last_seen", datetime.min)
            if not is_archive and last_seen + self.group_info_refresh_time > now:
                self.logger.debug(
                    "Is Archive or Too Soon for new group info: %s: %s: %s",
                    last_seen,
                    self.group_info_refresh_time,
                    now,
                )
                return
            try:
                group_info = await self.core_client.GetGroupInfo(chat)
                if group_info is None:
                    self.logger.debug("Empty group info... stopping")
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
            self.logger.info("Updating community info: %s", chat_jid)
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
                    await self._insert_device_group_info(
                        db,
                        group_from_community,
                        donor,
                        now,
                    )
        elif group_info is not None:
            self.logger.info("Updating group info: %s", chat_jid)
            with self.db as db:
                await self._insert_device_group_info(db, group_info, donor, now)
        elif not is_archive:
            self.logger.critical(
                "Both community_info and group_info are none...: %s", chat_jid
            )

    async def _update_group_participants(
        self,
        db: dataset.Database,
        update_time: datetime,
        chat_jid: str,
        group_participants_proto: T.Sequence[wuc.GroupParticipant],
    ):
        if not group_participants_proto:
            return
        now = datetime.now()
        group_participants = [
            flatten_proto_message(p) for p in group_participants_proto
        ]
        participant_jids = list(p["JID"] for p in group_participants)
        table: dataset.Table = db.get_table("group_participants")
        group_participants_prev = table.find(
            chat_jid=chat_jid, JID={"in": participant_jids}
        )
        group_participants_prev_lookup = {
            gp.get("JID"): gp for gp in group_participants_prev
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

    async def _insert_device_group_info(
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
            self.logger.critical(
                "Could not get chat JID or donor JID string: %s: %s", donor, group_info
            )
            return
        db_provenance = {
            "databasebot__timestamp": datetime.now().isoformat(),
            "databasebot__version": self.__version__,
            "databasebot__donor": donor_jid,
            **self.meta,
        }

        await self._update_group_participants(
            db, update_time, chat_jid, group_info.participants
        )
        table: dataset.Table = db.get_table("device_group_info")
        group_info_hash = utils.group_info_hash(group_info)

        group_info_id = f"{chat_jid}-{donor_jid}-{group_info_hash}"
        previous_row = table.find_one(id=group_info_id)
        if previous_row:
            table.update(
                {
                    "last_seen": max(
                        previous_row.get("last_seen", datetime.min), update_time
                    ),
                    "timestamp": min(
                        previous_row.get("timestamp", datetime.max), update_time
                    ),
                    "id": group_info_id,
                },
                keys=["id"],
            )
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
        group_info_flat["provenance"] = {
            **(group_info_flat.get("provenance") or {}),
            **db_provenance,
        }
        group_info_flat[RECORD_MTIME_FIELD] = now
        table.insert(group_info_flat)

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
                message_flat["previous_version_text"] = source_message.get("text")
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

    # <depricated>
    async def _update_group_or_community_old(
        self,
        chat: wuc.JID,
        is_archive: bool,
        archive_data: ArchiveData,
    ):
        chat_jid = utils.jid_to_str(chat)
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

        group_info_prev = self.db["group_info"].find_one(id=chat_jid) or {}

        if not is_archive:
            last_update: datetime = group_info_prev.get("last_update", datetime.min)
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
            parentJID = next(gi.JID for gi in community_info if gi.isCommunity)
            for gi in community_info:
                if not gi.isCommunity and not gi.parentJID:
                    gi.parentJID.CopyFrom(parentJID)
            for group_from_community in community_info:
                self.logger.debug(
                    "Inserting community group: %s",
                    utils.jid_to_str(group_from_community.JID),
                )
                with self.db as db:
                    await self._insert_group_info_old(
                        db, group_from_community, now, group_info_prev=group_info_prev
                    )
        elif group_info is not None:
            self.logger.debug("Using group info to update group: %s", chat_jid)
            with self.db as db:
                await self._insert_group_info_old(
                    db, group_info, now, group_info_prev=group_info_prev
                )
        elif not is_archive:
            self.logger.critical(
                "Both community_info and group_info are none...: %s", chat_jid
            )

    async def _insert_group_info_old(
        self,
        db: dataset.Database,
        group_info: wuc.GroupInfo,
        update_time: datetime,
        group_info_prev=None,
    ):
        now = datetime.now()
        chat_jid = utils.jid_to_str(group_info.JID)
        logger = self.logger.getChild(chat_jid or "")
        group_info_flat = flatten_proto_message(
            group_info,
            preface_keys=True,
            skip_keys=set(["participants", "participantVersionId"]),
        )

        db_provenance = {
            "databasebot__timestamp": datetime.now().isoformat(),
            "databasebot__version": self.__version__,
            **self.meta,
        }
        group_info_prev = (
            group_info_prev or db["group_info"].find_one(id=chat_jid) or {}
        )
        has_prev_group_info = bool(group_info_prev)

        if has_prev_group_info and group_info_prev["last_update"] > update_time:
            logger.debug("DB group info is more recent. Not updating")
            return

        group_info_flat["id"] = chat_jid
        group_info_flat["last_update"] = update_time

        if group_info_prev.get("provenance") is None:
            group_info_prev.update(provenance=db_provenance)
        else:
            group_info_prev["provenance"].update(db_provenance)

        if group_info_flat.get("provenance") is None:
            group_info_flat.update(provenance=db_provenance)
        else:
            group_info_flat["provenance"].update(db_provenance)

        if has_prev_group_info:
            logger.debug("Has prev group info")
            keys = set(group_info_flat.keys())
            [keys.discard(f) for f in ("provenance", "last_update", "record_mtime")]
            changed_keys = [
                k for k in keys if group_info_flat.get(k) != group_info_prev.get(k)
            ]
            if changed_keys:
                logger.debug(
                    "Found previous out-of-date entry, updating: %s: %s",
                    chat_jid,
                    changed_keys,
                )
                group_info_flat["provenance"]["databasebot__changed_fields"] = ",".join(
                    changed_keys
                )
                n_versions = db["group_info"].count(JID=chat_jid)
                group_info_prev["n_versions"] = n_versions
                prev_id = group_info_prev["id"]
                N = group_info_flat["n_versions"] = n_versions + 1

                n = N
                while db["group_info"].count(id=f"{chat_jid}-{n:06d}") > 0:
                    n += 1
                id_ = f"{chat_jid}-{n:06d}"
                group_info_prev["id"] = id_

                group_info_prev["last_update"] = update_time
                group_info_flat["previous_version_id"] = id_
                if group_first_seen := group_info_prev.get("first_seen"):
                    group_info_flat["first_seen"] = group_first_seen

                group_info_flat[RECORD_MTIME_FIELD] = now
                group_info_prev[RECORD_MTIME_FIELD] = now
                db["group_info"].delete(id=prev_id)
                db["group_info"].insert(group_info_prev)
                db["group_info"].upsert(group_info_flat, ["id"])
            else:
                logger.debug("Updating group info last updated field: %s", changed_keys)
                db["group_info"].update(
                    {
                        "id": chat_jid,
                        "last_update": update_time,
                        "provenance": group_info_prev.get("provenance"),
                        RECORD_MTIME_FIELD: now,
                    },
                    ["id"],
                )
        else:
            logger.debug("Inserting new group info row")
            group_info_flat["first_seen"] = update_time
            group_info_flat[RECORD_MTIME_FIELD] = now
            db["group_info"].insert(group_info_flat)

        logger.info("Updating group: %s", chat_jid)

    # </depricated>
