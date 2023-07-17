import json
import logging
from pathlib import Path

from .. import utils
from . import BaseBot
from ..protos import whatupcore_pb2 as wuc
from ..protos import whatsappweb_pb2 as waw

logger = logging.getLogger(__name__)


def to_message(mediaMessage: wuc.MediaMessage) -> waw.Message:
    msg = waw.Message()
    msg.ParseFromString(mediaMessage.SerializeToString())
    return msg


class ArchiveBot(BaseBot):
    def __init__(
        self,
        archive_dir: Path,
        *args,
        **kwargs,
    ):
        self.archive_dir = archive_dir
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)

    async def on_message(self, message: wuc.WUMessage):
        if message.info.source.isFromMe:
            return

        chat_id = utils.jid_to_str(message.info.source.chat)
        conversation_dir: Path = self.archive_dir / chat_id
        conversation_dir.mkdir(parents=True, exist_ok=True)

        timestamp = message.info.timestamp.ToSeconds()
        message_id = message.info.id
        archive_id = f"{timestamp}_{message_id}"

        message_dict = utils.protobuf_to_dict(message)
        message_dict["archive_id"] = archive_id

        meta_path = conversation_dir / "metadata.json"
        if message.info.source.isGroup and not meta_path.exists():
            group: wuc.JID = message.info.source.chat
            metadata: wuc.GroupInfo = await self.core_client.GetGroupInfo(group)
            self.logger.debug("Got metadata: %s", metadata)
            with meta_path.open("w+") as fd:
                fd.write(utils.protobuf_to_json(metadata))

        if media_filename := utils.media_message_filename(message):
            self.logger.debug("Found media. Saving to %s", media_filename)
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            media_path = media_dir / f"{media_filename}"
            message_dict["media_path"] = str(media_path.relative_to(self.archive_dir))

            if not media_path.exists():
                self.logger.debug(
                    "Sending download request: %s: %s",
                    message.content.mediaMessage,
                    message.info,
                )
                media_bytes = await self.download_message_media(message)
                with media_path.open("wb+") as fd:
                    fd.write(media_bytes)

        with open(conversation_dir / f"{archive_id}.json", "w+") as fd:
            json.dump(message_dict, fd, cls=utils.WhatUpyJSONEncoder)
