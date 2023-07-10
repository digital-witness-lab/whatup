import re
import json
import logging
import tarfile
from io import BytesIO
from pathlib import Path

from .. import utils
from . import BaseBot

logger = logging.getLogger(__name__)


class ArchiveBot(BaseBot):
    def __init__(
        self,
        archive_dir: Path,
        *args,
        **kwargs,
    ):
        self.archive_dir = archive_dir
        super().__init__(*args, **kwargs)

    async def on_message(self, message):
        if message.info.source.isFromMe:
            return

        chatid = utils.jid_to_str(message.info.source.chat)
        conversation_dir: Path = self.archive_dir / chatid
        conversation_dir.mkdir(parents=True, exist_ok=True)

        timestamp = message.info.timestamp.ToSeconds()
        messageId = message.info.id
        message_id = f"{timestamp}_{messageId}"

        message_dict = utils.protobuf_to_dict(message)
        message_dict["archive_id"] = message_id

        with open(conversation_dir / f"{message_id}.json", "w+") as fd:
            json.dump(message_dict, fd)

        meta_path = conversation_dir / "metadata.json"
        if message.info.source.isGroup and not meta_path.exists():
            group = message.info.source.chat
            metadata = await self.core_client.GetGroupInfo(group)
            metadata_dict = utils.protobuf_to_dict(metadata)
            with meta_path.open("w+") as fd:
                json.dump(metadata_dict, fd)

        if message.content.mediaMessage is not None:
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)

            message.content.mediaMessage.WhichOneof()

            media_filename = utils.media_message_filename(message) or "meida.unk"
            media_bytes = await self.download_message_media(message)
            with open(media_dir / f"{message_id}-{media_filename}", "wb+") as fd:
                fd.write(media_bytes)
