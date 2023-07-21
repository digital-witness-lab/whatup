import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
import typing as T

import dataset
from dataset.util import DatasetException
from sqlalchemy.sql import func
from google.protobuf.timestamp_pb2 import Timestamp

from .. import utils, __version__
from . import BaseBot, BotCommandArgs
from ..protos import whatupcore_pb2 as wuc

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


def query_unique_groups(db):
    table = db["groupInfo"]
    return query_column_count_unique(db, table.table.columns.JID)


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
        sub_parser = parser.add_subparsers()

        num_groups = sub_parser.add_parser("num-groups")
        group_info = sub_parser.add_parser("group-info")
        group_info.add_argument(
            "jid", type=str, help="JID of the group you want info about"
        )
        group_info.add_argument(
            "--format", choices=["csv", "json", "human"], default="human"
        )

        return parser

    async def on_control(self, message):
        params = await self.parse_command(message)
        self.logger.info("Got command: %s", params)
        if params is None:
            return

    async def on_message(self, message: wuc.WUMessage):
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
            await self._update_message(message)

    async def _update_message(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
        if media_filename := utils.media_message_filename(message):
            media_content = await self.download_message_media(message)
        else:
            media_content = None
        with self.db as db:
            if message.info.source.isGroup:
                await self._update_group(db, message.info.source.chat)
            if media_filename and media_content:
                mimetype = utils.media_message_mimetype(message)
                file_extension = media_filename.rsplit(".", 1)[-1]
                db["media"].insert(
                    {
                        "filename": media_filename,
                        "content": media_content,
                        "mimetype": mimetype,
                        "fileExtension": file_extension,
                    }
                )
                message_flat["mediaFilename"] = media_filename
            db["messages"].upsert(message_flat, ["id"])

    async def _update_group(self, db: dataset.Database, chat: wuc.JID, is_history: bool):
        chat_jid = utils.jid_to_str(chat)
        logger = self.logger.getChild(chat_jid)
        now = datetime.now()

        group_info_prev = db["groupInfo"].find_one(JID=chat_jid) or {}
        last_update: datetime = group_info_prev.get("lastUpdate", datetime.min)
        if last_update + self.group_info_refresh_time > now:
            return
        logger.debug("Need to update group info")

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

        if group_info.parentJID.ByteSize() > 0:
            logger.debug("Updating chat's parent")
            await self._update_group(db, group_info.parentJID)

    async def _update_edit(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
        source_message_id = message.content.inReferenceToId
        message_flat["id"] = source_message_id
        with self.db as db:
            source_message = db["messages"].find_one(id=source_message_id)
            if source_message:
                source_message.setdefault("nEdits", 0)
                N = message_flat["nEdits"] = source_message["nEdits"] + 1
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
