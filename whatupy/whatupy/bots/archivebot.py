import json
import logging
from datetime import datetime
from functools import partial
from pathlib import Path

from packaging import version

from .. import __version__, utils
from ..protos import whatsappweb_pb2 as waw
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot

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
        kwargs["read_historical_messages"] = True
        super().__init__(*args, **kwargs)

    async def on_message(self, message: wuc.WUMessage, is_history: bool, **kwargs):
        chat_id = utils.jid_to_str(message.info.source.chat)
        if chat_id is None:
            self.logger.critical("Message has no chat_id")
            return
        conversation_dir: Path = self.archive_dir / chat_id
        conversation_dir.mkdir(parents=True, exist_ok=True)

        timestamp = message.info.timestamp.ToSeconds()
        message_id = message.info.id
        archive_id = f"{timestamp}_{message_id}"
        archive_filename = conversation_dir / f"{archive_id}.json"
        if archive_filename.exists():
            with archive_filename.open() as fd:
                data = json.load(fd)
            if version(data["provenance"]["archivebot__version"]) >= version(
                __version__
            ):
                self.logger.debug(
                    "Message already archived.. skipping: %s", archive_filename
                )
                return
            else:
                self.logger.debug(
                    "Re-processing message because of new archive version"
                )
        self.logger.debug("Archiving message to: %s", archive_id)

        message.provenance["archivebot__timestamp"] = datetime.now().isoformat()
        message.provenance["archivebot__version"] = __version__
        message.provenance["archivebot__archiveId"] = archive_id

        meta_path = conversation_dir / "metadata.json"
        if message.info.source.isGroup and not meta_path.exists():
            group: wuc.JID = message.info.source.chat
            metadata: wuc.GroupInfo = await self.core_client.GetGroupInfo(group)
            self.logger.debug("Got metadata for group: %s", chat_id)
            with meta_path.open("w+") as fd:
                fd.write(utils.protobuf_to_json(metadata))

        if media_filename := utils.media_message_filename(message):
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            media_path = media_dir / f"{media_filename}"
            message.provenance["archivebot__mediaPath"] = str(
                media_path.relative_to(self.archive_dir)
            )

            if not media_path.exists():
                callback = partial(
                    self._handle_media_content,
                    media_path=media_path,
                    media_filename=media_filename,
                )
                await self.download_message_media_eventually(message, callback)

        message_dict = utils.protobuf_to_dict(message)
        with archive_filename.open("w+") as fd:
            json.dump(message_dict, fd, cls=utils.WhatUpyJSONEncoder)

    async def _handle_media_content(
        self,
        message: wuc.WUMessage,
        media_bytes: bytes,
        media_path: Path,
        media_filename: str,
    ):
        self.logger.debug("Found media. Saving to %s", media_filename)
        with media_path.open("wb+") as fd:
            fd.write(media_bytes)
