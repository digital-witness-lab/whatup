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

    async def on_connection_ready(self, *args, **kwargs):
        self.logger.info(f"Subscribing to messages: {args}: {kwargs}")
        await self.messages_subscribe()

    async def on_read_messages_control(self, message):
        if message["key"]["fromMe"]:
            return
        try:
            command = utils.get_message_text(message) or ""
            self.logger.info(f"Got command: {command}")
        except KeyError:
            self.logger.debug(f"Could not find command in control message: {message}")
            return
        sender = message["key"].get("participant") or message["key"]["remoteJid"]
        if match := re.match("/archive-download", command):
            self.logger.info("Sending archive json")
            buffer = BytesIO()
            with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
                tar.add(self.archive_dir, arcname=self.archive_dir.name)
            await self.send_message(
                sender,
                {
                    "fileName": "archive.tar.gz",
                    "mimetype": "application/gzip",
                    "document": buffer.getvalue(),
                    "disappearingMessagesInChat": 60 * 60 * 10,
                    "caption": "[[ some interesting stats ]]",
                },
                vamp_max_seconds=10,
            )
            await self.send_message(
                sender,
                {"disappearingMessagesInChat": False},
                vamp_max_seconds=5,
            )

    async def on_read_messages(self, message):
        if "messageStubType" in message:
            return
        elif message["key"]["fromMe"]:
            return

        chatid = message["key"]["remoteJid"]
        conversation_dir: Path = self.archive_dir / chatid
        conversation_dir.mkdir(parents=True, exist_ok=True)
        message_id = f"{message['messageTimestamp']}_{message['key']['id']}"
        message["archive_id"] = message_id

        with open(conversation_dir / f"{message_id}.json", "w+") as fd:
            json.dump(message, fd)

        meta_path = conversation_dir / "metadata.json"
        if utils.is_groupchat(message) and not meta_path.exists():
            metadata = await self.group_metadata(chatid)
            with meta_path.open("w+") as fd:
                json.dump(metadata, fd)

        if utils.is_media_message(message):
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            media_filename = utils.media_message_filename(message) or "meida.unk"
            media_bytes = await self.download_message_media(message)
            with open(media_dir / f"{message_id}-{media_filename}", "wb+") as fd:
                fd.write(media_bytes)
