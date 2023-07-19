import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import typing as T

import dataset
from sqlalchemy.sql import func
from google.protobuf.timestamp_pb2 import Timestamp

from .. import utils, __version__
from . import BaseBot
from ..protos import whatupcore_pb2 as wuc
from ..protos import whatsappweb_pb2 as waw

logger = logging.getLogger(__name__)


IGNORED_FIELDS = set(("originalMessage", "mediaMessage"))


def flatten_proto_message(proto_obj):
    flat = {}
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    for key in key_list:
        obj: T.Any = getattr(proto_obj, key)
        if isinstance(obj, wuc.JID):
            obj = utils.jid_to_str(obj)
            if 'jid' not in key.lower():
                key = f'{key}_jid'
        elif isinstance(obj, Timestamp):
            obj = obj.ToDatetime()
        elif hasattr(obj, "items"):
            obj = dict(obj)
        elif hasattr(obj, "append"):
            new_obj = []
            for item in obj:
                if utils.is_filled_pbuf(item)
                    item = flatten_proto_message(item)
                elif utils.is_empty_pbuf(item):
                    continue
                new_obj.append(item)
            obj = new_obj
        elif key in IGNORED_FIELDS:
            continue

        if utils.is_filled_pbuf(obj):
            flat.update(flatten_proto_message(obj))
        elif utils.is_empty_pbuf(obj):
            continue
        elif obj:
            flat[key] = obj
    return flat


class DatabaseBot(BaseBot):
    def __init__(
        self,
        postgres_url: str,
        group_info_refresh_time: timedelta = timedelta(days=1),
        *args,
        **kwargs,
    ):
        self.postgres_url = postgres_url
        self.group_info_refresh_time = group_info_refresh_time
        self.db: dataset.Database = dataset.connect(postgres_url)
        self.db.create_table(
            "groupInfo",
            primary_id="JID",
            primary_type=self.db.types.text,
            primary_increment=False,
        )
        self.db.create_table("groupParticipants")
        self.db['groupParticipants'].create_index('chat_jid')
        self.db['groupParticipants'].create_index(['JID', 'chat_jid'])
        self.db["groupParticipants"].create_column("firstSeen", type=db.types.datetime, server_default=func.now())
        self.db.create_table(
            "messages",
            primary_id="id",
            primary_type=self.db.types.text,
            primary_increment=False,
        )
        self.db.create_table(
            "reactions",
            primary_id="id",
            primary_type=self.db.types.text,
            primary_increment=False,
        )
        self.db.create_table(
            "media",
            primary_id="id",
            primary_type=self.db.types.text,
            primary_increment=False,
        )
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)

    async def on_message(self, message: wuc.WUMessage):
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
        with self.db as db:
            if message.info.source.isGroup:
                await self._update_group(db, message)
            db["messages"].upsert(message_flat, ["id"])
            # TODO: finish this function.... namely add media support

    async def _update_group(self, db: dataset.Database, message: wuc.WUMessage):
        now = datetime.now()
        chat_jid = utils.jid_to_str(message.info.source.chat)
        group_info = db["groupInfo"].find_one(JID=chat_jid)
        if group_info is not None and group_info['last_update'] + self.group_info_refresh_time > now:
            return
        group_info: wuc.GroupInfo = await self.core_client.GetGroupInfo(chat_jid)

        group_info_flat = flatten_proto_message(group_info)
        group_participants = group_info_flat.pop("participants", [])
        for participant in group_participants:
            participant["lastSeen"] = now
            participant["chat_jid"] = chat_jid

        db['groupParticipants'].upsert_many(group_participants, ['JID', 'chat_jid'])
        db['groupInfo'].upsert(group_info_flat, ['JID'])
        # TODO: finish this function... namely, deal with TOPIC or NAME changes to group

    async def _update_edit(self, message: wuc.WUMessage):
            message_flat = flatten_proto_message(message)
            source_message_id = message.content.inReferenceToId
            message_flat["id"] = source_message_id
            with self.db as db:
                source_message = db["messages"].find_one(id=source_message_id)
                if source_message:
                    N = message_flat["n_edits"] = source_message.get("n_edits", 0) + 1
                    id_ = source_message["id"] = f"source_message_id-{N:03d}"
                    message_flat["previous_version_id"] = id_
                    message_flat["previous_version_text"] = source_message["text"]
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
                reaction_counts = source_message.get(
                    "reaction_counts", defaultdict(int)
                )
            reaction_counts[message.content.text] += 1
            db["reactions"].upsert(message_flat, ["id"])
            db["messages"].upsert(
                {"id": source_message_id, "reaction_counts": reaction_counts},
                ["id"],
            )
