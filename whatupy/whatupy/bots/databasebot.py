import logging
import typing as T
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial

import dataset
from dataset.util import DatasetException
from google.protobuf.timestamp_pb2 import Timestamp
from sqlalchemy.sql import func

from .. import __version__, utils
from ..protos import whatupcore_pb2 as wuc
from . import ArchiveData, BaseBot, BotCommandArgs, MediaType

logger = logging.getLogger(__name__)


IGNORED_FIELDS = set(("originalMessage", "mediaMessage"))


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
        if key in skip_keys:
            continue
        obj: T.Any = getattr(proto_obj, key)
        if isinstance(obj, wuc.JID):
            obj = utils.jid_to_str(obj)
            if "jid" not in key.lower():
                key = f"{key}_jid"
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
                        prev_keys=(*prev_keys, key),
                        sep=sep,
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
                    prev_keys=(*prev_keys, key),
                    sep=sep,
                )
            )
        elif utils.is_empty_pbuf(obj):
            continue
        elif obj:
            if preface_keys:
                key = sep.join((*prev_keys, key))
            flat[key] = obj
    return flat


def query_column_count_unique(db, column):
    results = db.query(func.count(func.distinct(column)))
    for result in results:
        if "count_1" in result:
            return result["count_1"]
    return None


def query_column_min(db, column):
    results = db.query(func.min(column))
    for result in results:
        if "min_1" in result:
            return result["min_1"]
    return None


def query_num_groups(db):
    table = db["groupInfo"]
    n_groups = query_column_count_unique(db, table.table.columns.JID)
    start_time = query_column_min(db, table.table.columns.firstSeen)
    return start_time, n_groups


class DatabaseBot(BaseBot):
    def __init__(
        self,
        postgres_url: str,
        group_info_refresh_time: timedelta = timedelta(days=1),
        *args,
        **kwargs,
    ):
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)
        self.postgres_url = postgres_url
        self.group_info_refresh_time = group_info_refresh_time
        self.db: dataset.Database = dataset.connect(postgres_url)
        self.init_database(self.db)

    def init_database(self, db):
        group_info = db.create_table(
            "groupInfo",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        try:
            group_info.create_index(["JID"])
        except DatasetException:
            self.logger.warn(
                "Could not create groupParticipants indicies because table doesn't exist yet"
            )
        db["groupInfo"].create_column(
            "firstSeen", type=db.types.datetime, server_default=func.now()
        )
        db["groupInfo"].create_column(
            "lastUpdate", type=db.types.datetime, server_default=func.now()
        )
        group_participants = db.create_table("groupParticipants")
        try:
            group_participants.create_index(["chat_jid"])
            group_participants.create_index(["JID", "chat_jid"])
        except DatasetException:
            self.logger.warn(
                "Could not create groupParticipants indicies because table doesn't exist yet"
            )
        group_participants.create_column(
            "firstSeen", type=db.types.datetime, server_default=func.now()
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
        db.create_table(
            "media",
            primary_id="filename",
            primary_type=db.types.text,
            primary_increment=False,
        )

    def setup_command_args(self):
        parser = BotCommandArgs(
            prog=self.__class__.__name__,
            description="Bot dealing with the clean database representation of our whatsapp data",
        )
        sub_parser = parser.add_subparsers(dest="command")

        num_groups = sub_parser.add_parser(
            "num-groups",
            description="Returns the number of unique groups monitored by the bot",
        )
        group_info = sub_parser.add_parser(
            "group-info",
            description="Returns metadata about a given group",
        )
        group_info.add_argument(
            "jid", type=str, help="JID of the group you want info about"
        )
        group_info.add_argument(
            "--format", choices=["csv", "json", "human"], default="csv"
        )

        return parser

    async def on_control(self, message):
        params = await self.parse_command(message)
        self.logger.info("Got command: %s", params)
        if params is None:
            return
        sender = message.info.source.sender

        if params.command == "num-groups":
            start_time, n_groups = query_num_groups(self.db)
            await self.send_text_message(
                sender,
                f"I've been tracking {n_groups} groups since {start_time.date()}",
            )
        elif params.command == "group-info":
            jid = params.jid
            metadata = self.db["groupInfo"].find_one(JID=jid)
            if metadata is None:
                await self.send_text_message(
                    sender, "I couldn't find that group in our database"
                )
                return
            content = utils.dict_to_csv_bytes([metadata])
            group_name = metadata["groupName_name"]
            await self.send_media_message(
                sender,
                MediaType.MediaDocument,
                content=content,
                caption=f"Information for group {jid} (titled: {group_name})",
                mimetype="text/csv",
                filename=f"group-info_{jid}.csv",
            )

    async def on_message(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        archive_data: ArchiveData,
        **kwargs,
    ):
        message.provenance["databasebot__timestamp"] = datetime.now().isoformat()
        message.provenance["databasebot__version"] = __version__
        if message.messageProperties.isReaction:
            await self._update_reaction(message)
        elif message.messageProperties.isEdit:
            await self._update_edit(message)
        elif message.messageProperties.isDelete:
            source_message_id = message.content.inReferenceToId
            with self.db as db:
                db["messages"].upsert({"id": source_message_id, "isDelete": True})
        else:
            await self._update_message(message, is_archive, archive_data)

    async def _update_message(
        self, message: wuc.WUMessage, is_archive: bool, archive_data: ArchiveData
    ):
        message_flat = flatten_proto_message(message)
        media_filename = utils.media_message_filename(message)
        with self.db as db:
            if message.info.source.isGroup:
                await self._update_group(
                    db, message.info.source.chat, is_archive, archive_data
                )
            if media_filename:
                message_flat["mediaFilename"] = media_filename
                existingMedia = db["media"].count(filename=media_filename)
                if not existingMedia:
                    mimetype = utils.media_message_mimetype(message)
                    file_extension = media_filename.rsplit(".", 1)[-1]
                    datum = {
                        "filename": media_filename,
                        "content": None,
                        "mimetype": mimetype,
                        "fileExtension": file_extension,
                        "timestamp": message.info.timestamp.ToDatetime(),
                    }
                    callback = partial(self._handle_media_content, datum=datum)
                    if is_archive:
                        if archive_data.MediaContent:
                            await callback(message, archive_data.MediaContent)
                    else:
                        await self.download_message_media_eventually(message, callback)
            db["messages"].upsert(message_flat, ["id"])

    async def _handle_media_content(
        self, message: wuc.WUMessage, content: bytes, datum: dict
    ):
        if not content:
            self.logger.critical(
                "Empty media body... skipping writing to database: %s", datum
            )
            return
        datum["content"] = content
        self.db["media"].insert(datum)

    async def _update_group(
        self,
        db: dataset.Database,
        chat: wuc.JID,
        is_archive: bool,
        archive_data: ArchiveData,
    ):
        chat_jid = utils.jid_to_str(chat)
        logger = self.logger.getChild(chat_jid)
        now = datetime.now()

        group_info_prev = db["groupInfo"].find_one(JID=chat_jid) or {}
        last_update: datetime = group_info_prev.get("lastUpdate", datetime.min)
        if last_update + self.group_info_refresh_time > now:
            return
        logger.debug("Need to update group info")

        if is_archive:
            if archive_data.GroupInfo is None:
                return
            group_info = archive_data.GroupInfo
        else:
            group_info: wuc.GroupInfo = await self.core_client.GetGroupInfo(chat)
        group_info_flat = flatten_proto_message(
            group_info,
            preface_keys=True,
            skip_keys=set(["participants", "participantVersionId"]),
        )
        group_info_flat["id"] = chat_jid
        group_participants = [flatten_proto_message(p) for p in group_info.participants]

        keys = set(group_info_prev.keys()).union(group_info_flat.keys())
        if group_info_prev and any(
            group_info_flat.get(k) != group_info_prev.get(k) for k in keys
        ):
            logger.debug("Found previous out-of-date entry, updating")
            db["groupInfo"]
            group_info_prev.setdefault("nVersions", 0)
            prev_id = group_info_prev["id"]
            N = group_info_flat["nVersions"] = group_info_prev["nVersions"] + 1
            id_ = group_info_prev["id"] = f"{prev_id}-{N:06d}"
            group_info_prev["lastUpdate"] = now
            group_info_flat["previousVersionId"] = id_
            if first_seen := group_info_prev.get("firstSeen"):
                group_info_flat["firstSeen"] = first_seen
            db["groupInfo"].insert(group_info_prev)
            db["groupInfo"].delete(id=prev_id)
        group_info_flat["lastUpdate"] = now
        db["groupInfo"].insert(group_info_flat)

        for participant in group_participants:
            participant["lastSeen"] = now
            participant["chat_jid"] = chat_jid

        db["groupParticipants"].upsert_many(group_participants, ["JID", "chat_jid"])
        db["groupInfo"].upsert(group_info_flat, ["JID"])

        if group_info.parentJID.ByteSize() > 0 and not is_archive:
            # TODO: this in archive mode
            logger.debug("Updating chat's parent")
            await self._update_group(db, group_info.parentJID)

    async def _update_edit(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
        source_message_id = message.content.inReferenceToId
        message_flat["id"] = source_message_id
        with self.db as db:
            source_message = db["messages"].find_one(id=source_message_id)
            if source_message:
                n_edits: int = source_message.get("nEdits", 0) or 0
                N = message_flat["nEdits"] = n_edits + 1
                id_ = source_message["id"] = f"{source_message_id}-{N:03d}"
                message_flat["previousVersionId"] = id_
                message_flat["previousVersionText"] = source_message["text"]
                db["messages"].insert(source_message)
            db["messages"].upsert(message_flat, ["id"])

    async def _update_reaction(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
        source_message_id = message.content.inReferenceToId
        with self.db as db:
            source_message = db["messages"].find_one(id=source_message_id)
            if not source_message:
                reaction_counts = defaultdict(int)
            else:
                reaction_counts = source_message.get("reactionCounts", defaultdict(int))
            reaction_counts[message.content.text] += 1
            db["reactions"].upsert(message_flat, ["id"])
            db["messages"].upsert(
                {"id": source_message_id, "reactionCounts": reaction_counts},
                ["id"],
            )
