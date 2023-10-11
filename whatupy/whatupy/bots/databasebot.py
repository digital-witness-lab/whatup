import logging
import typing as T
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial

import dataset
import phonenumbers
from dataset.util import DatasetException
from google.protobuf.timestamp_pb2 import Timestamp
from phonenumbers.phonenumberutil import region_code_for_number
from sqlalchemy.sql import func

from .. import utils
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
            if obj.server != "g.us" and obj.user:
                try:
                    jid_phone = phonenumbers.parse(f"+{obj.user}")
                    flat.update(
                        {
                            f"{key}_country_code": jid_phone.country_code,
                            f"{key}_country_iso": region_code_for_number(jid_phone),
                            f"{key}_national_number": jid_phone.national_number,
                        }
                    )
                except phonenumbers.NumberParseException:
                    logger.warning("Could not parse phone number: +%s", obj.user)
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
    table = db["group_info"]
    n_groups = query_column_count_unique(db, table.table.columns.JID)
    start_time = query_column_min(db, table.table.columns.first_seen)
    return start_time, n_groups


def query_group_country_codes(db):
    query = """
    SELECT 
        data.*, gi.* 
    FROM (
        SELECT
            chat_jid,
            "JID_country_iso" AS country_iso,
            COUNT(*) AS count
        FROM "group_participants"
        GROUP BY chat_jid, "JID_country_iso"
    ) AS data
    JOIN "group_info" as gi ON gi.id = chat_jid
    """
    results = db.query(query)
    return [dict(row) for row in results]


class DatabaseBot(BaseBot):
    __version__ = "1.1.0"

    def __init__(
        self,
        database_url: str,
        group_info_refresh_time: timedelta = timedelta(hours=6),
        *args,
        **kwargs,
    ):
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)
        self.group_info_refresh_time = group_info_refresh_time
        self.db: dataset.Database = dataset.connect(database_url)
        self.init_database(self.db)

    def init_database(self, db):
        group_info = db.create_table(
            "group_info",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False,
        )
        try:
            group_info.create_index(["JID"])
        except DatasetException:
            self.logger.warn(
                "Could not create group_participants indicies because table doesn't exist yet"
            )  # is this an incorrect, copy-pasted warning message? ^ 
        db["group_info"].create_column(
            "first_seen", type=db.types.datetime, server_default=func.now()
        )
        db["group_info"].create_column(
            "last_update", type=db.types.datetime, server_default=func.now()
        )

        group_participants = db.create_table("group_participants")
        try:
            group_participants.create_index(["chat_jid"])
            group_participants.create_index(["JID", "chat_jid"])
        except DatasetException:
            self.logger.warn(
                "Could not create group_participants indicies because table doesn't exist yet"
            )
        group_participants.create_column(
            "first_seen", type=db.types.datetime, server_default=func.now()
        )

        community_info = db.create_table(
            "community_info",
            primary_id="id",
            primary_type=db.types.text,
            primary_increment=False
        )
        try:
            community_info.create_index(["JID"])
        except DatasetException:
            self.logger.warn(
                "Could not create JID index because commmunity_info table doesn't exist yet"
            )
        db["community_info"].create_column(
            "first_seen", type=db.types.datetime, server_default=func.now()
        )
        db["community_info"].create_column(
            "last_update", type=db.types.datetime, server_default=func.now()
        )

        community_participants = db.create_table("community_participants")
        try:
            community_participants.create_index(["chat_jid"])
            community_participants.create_index(["JID", "chat_jid"])
        except DatasetException:
            self.logger.warn(
                "Could not create community_participants indices because table doesn't exist yet"
            )
        community_participants.create_column(
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
        db.create_table(
            "media",
            primary_id="filename",
            primary_type=db.types.text,
            primary_increment=False,
        )
        db.create_table(
            "messages_seen",
            primary_id="id",
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

        country_code_distribution = sub_parser.add_parser(
            "country-codes",
            description="Gives the distribution of country codes per group monitored in CSV format",
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
            metadata = self.db["group_info"].find_one(JID=jid)
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
        elif params.command == "country-codes":
            data = query_group_country_codes(self.db)
            content = utils.dict_to_csv_bytes(data)
            await self.send_media_message(
                sender,
                MediaType.MediaDocument,
                content=content,
                caption="Distribution of country codes by group",
                mimetype="text/csv",
                filename="group-country-codes.csv",
            )

    async def on_message(
        self,
        message: wuc.WUMessage,
        is_archive: bool,
        archive_data: ArchiveData,
        **kwargs,
    ):
        msg_id = message.info.id
        if self.db["messages_seen"].count(id=msg_id) > 0:
            self.logger.info("Already seen messages, skipping: %s", msg_id)
            return
        message.provenance["databasebot__timestamp"] = datetime.now().isoformat()
        message.provenance["databasebot__version"] = self.__version__
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
            await self._update_message(message, is_archive, archive_data)

    async def _update_message(
        self, message: wuc.WUMessage, is_archive: bool, archive_data: ArchiveData
    ):
        message_flat = flatten_proto_message(message)
        media_filename = utils.media_message_filename(message)
        with self.db as db:
            if message.info.source.isGroup:
                self.logger.debug("Updating group: %s", message.info.id)
                await self._update_group(
                    db, message.info.source.chat, is_archive, archive_data
                )
                self.logger.debug("Done upading group: %s", message.info.id)
            if media_filename:
                self.logger.debug("Getting media: %s", message.info.id)
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
        self.logger.debug("Done upading message: %s", message.info.id)

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
        if is_archive:
            if archive_data.GroupInfo is None:
                return
            now = archive_data.WUMessage.info.timestamp.ToDatetime()
            self.logger.debug("Replacing date with archived message timestamp: %s", now)

        group_info_prev = db["group_info"].find_one(id=chat_jid) or {}
        last_update: datetime = group_info_prev.get("last_update", datetime.min)
        if not is_archive and last_update + self.group_info_refresh_time > now:
            return

        if is_archive:
            group_info = archive_data.GroupInfo
        else:
            group_info: wuc.GroupInfo = await self.core_client.GetGroupInfo(chat)

        if group_info.isCommunity:
            self.logger.info("Updating community for group: %s", group_info.JID)
            await self._update_community(
                db, chat, is_archive, archive_data
            )
            self.logger.info("Done updating community for group: %s", group_info.JID)
        
        group_info_flat = flatten_proto_message(
            group_info,
            preface_keys=True,
            skip_keys=set(["participants", "participantVersionId"]),
        )
        keys = set(group_info_prev.keys()).intersection(group_info_flat.keys())
        keys.discard("provenance")

        group_info_flat["id"] = chat_jid
        group_info_flat["last_update"] = now
        group_participants = [flatten_proto_message(p) for p in group_info.participants]

        if group_info_prev:
            if changed_keys := [
                k for k in keys if group_info_flat.get(k) != group_info_prev.get(k)
            ]:
                logger.debug(
                    "Found previous out-of-date entry, updating: %s: %s",
                    chat_jid,
                    changed_keys,
                )
                group_info_prev["n_versions"] = group_info_prev.get("n_versions") or 0
                prev_id = group_info_prev["id"]
                N = group_info_flat["n_versions"] = group_info_prev["n_versions"] + 1
                id_ = group_info_prev["id"] = f"{chat_jid}-{N:06d}"
                group_info_prev["last_update"] = now
                group_info_flat["previous_version_id"] = id_
                if first_seen := group_info_prev.get("first_seen"):
                    group_info_flat["first_seen"] = first_seen
                db["group_info"].delete(id=prev_id)
                db["group_info"].insert(group_info_prev)
                db["group_info"].upsert(group_info_flat, ["id"])
            else:
                db["group_info"].update({"id": chat_jid, "last_update": now}, ["id"])
        elif not group_info_prev:
            group_info_flat["first_seen"] = now
            db["group_info"].insert(group_info_flat)

        for participant in group_participants:
            participant["last_seen"] = now
            participant["chat_jid"] = chat_jid

        logger.debug("Updating group info: %s", chat_jid)
        db["group_participants"].upsert_many(group_participants, ["JID", "chat_jid"])

        if group_info.parentJID.ByteSize() > 0 and not is_archive:
            # TODO: this in archive mode
            logger.debug("Updating chat's parent: %s", chat_jid)
            await self._update_group(
                db,
                group_info.parentJID,
                is_archive=is_archive,
                archive_data=archive_data,
            )

    async def _update_community( 
            self,
            db:dataset.Database,
            chat: wuc.JID,
            is_archive: bool,
            archive_data: ArchiveData,
    ):  
        chat_jid = utils.jid_to_str(chat)
        logger = self.logger.getChild(chat_jid)
        now = datetime.now()
        if is_archive:
            if archive_data.CommunityInfo is None:
                return
            now = archive_data.WUMessage.info.timestamp.ToDatetime()
            self.logger.debug("Replacing date with archived message timestamp: %s", now)

        community_info_prev = db["community_info"].find_one(id=chat_jid) or {}
        last_update: datetime = community_info_prev.get("last_update", datetime.min)
        if not is_archive and last_update + self.group_info_refresh_time > now:
            #assume we will use the same refresh time for groups and communities
            return

        if is_archive:
            community_info = archive_data.CommunityInfo
        else:
            community_info: wuc.GroupInfo = await self.core_client.GetCommunityInfo(chat)
        
        community_info_flat = flatten_proto_message(
            community_info,
            preface_keys=True,
            skip_keys=set(["participants", "participantVersionId"]), # similar to group info, this is handled elsewhere below?  
        )
        keys = set(community_info_prev.keys()).intersection(community_info_flat.keys())
        keys.discard("provenance")

        community_info_flat["id"] = chat_jid
        community_info_flat["last_update"] = now
        community_participants = [flatten_proto_message(p) for p in community_info.participants]

        if community_info_prev:
            if changed_keys := [
                k for k in keys if community_info_flat.get(k) != community_info_prev.get(k)
            ]:
                logger.debug(
                    "Found previous out-of-date entry, updating: %s: %s",
                    chat_jid,
                    changed_keys,
                )
                community_info_prev["n_versions"] = community_info_prev.get("n_versions") or 0
                prev_id = community_info_prev["id"]
                N = community_info_flat["n_versions"] = community_info_prev["n_versions"] + 1
                id_ = community_info_prev["id"] = f"{chat_jid}-{N:06d}"
                community_info_prev["last_update"] = now
                community_info_flat["previous_version_id"] = id_
                if first_seen := community_info_prev.get("first_seen"):
                    community_info_flat["first_seen"] = first_seen
                db["community_info"].delete(id=prev_id)
                db["community_info"].insert(community_info_prev)
                db["community_info"].upsert(community_info_flat, ["id"])
            else:
                db["community_info"].update({"id": chat_jid, "last_update": now}, ["id"])
        elif not community_info_prev:
            community_info_flat["first_seen"] = now
            db["community_info"].insert(community_info_flat)

        for participant in community_participants:
            participant["last_seen"] = now
            participant["chat_jid"] = chat_jid

        logger.debug("Updating community info: %s", chat_jid)
        db["community_participants"].upsert_many(community_participants, ["JID", "chat_jid"])

        # communities can't have parent communities right? 

        return

    async def _update_edit(self, message: wuc.WUMessage):
        message_flat = flatten_proto_message(message)
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
                reaction_counts = defaultdict(
                    int, source_message.get("reaction_counts") or {}
                )
            reaction_counts[message.content.text] += 1
            db["reactions"].upsert(message_flat, ["id"])
            db["messages"].upsert(
                {"id": source_message_id, "reaction_counts": reaction_counts},
                ["id"],
            )
