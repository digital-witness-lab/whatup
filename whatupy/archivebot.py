import logging
from pathlib import Path
import json


from .client import WhatUpBase
from . import utils


logger = logging.getLogger(__name__)


class ArchiveBot(WhatUpBase):
    def __init__(
        self,
        archive_dir: Path,
        *args,
        **kwargs,
    ):
        self.archive_dir = archive_dir
        super().__init__(*args, **kwargs)

    async def on_connection_ready(self, *args, **kwargs):
        self.logger.info(f"Subscribing to messages: {args}: {kwargs}")
        await self.messages_subscribe()

    async def on_read_messages(self, message):
        if "messageStubType" in message:
            return
        elif message["key"]["fromMe"]:
            return

        conversation_dir: Path = self.archive_dir / message["key"]["remoteJid"]
        conversation_dir.mkdir(parents=True, exist_ok=True)
        message_id = f"{message['messageTimestamp']}_{message['key']['id']}"
        message["archive_id"] = message_id

        with open(conversation_dir / f"{message_id}.json", "w+") as fd:
            fd.write(json.dumps(message))

        if utils.is_media_message(message):
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            media_filename = utils.media_message_filename(message) or "meida.unk"
            media_bytes = await self.download_message_media(message)
            with open(media_dir / f"{message_id}-{media_filename}", "wb+") as fd:
                fd.write(media_bytes)
