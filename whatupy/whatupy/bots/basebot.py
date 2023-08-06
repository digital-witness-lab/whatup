import argparse
import asyncio
import enum
import glob
import json
import logging
import random
import shlex
import time
import typing as T
from collections import defaultdict, deque, namedtuple
from datetime import datetime, timedelta
from pathlib import Path

from .. import utils
from ..connection import create_whatupcore_clients
from ..protos import whatsappweb_pb2 as waw
from ..protos import whatupcore_pb2 as wuc
from ..protos.whatupcore_pb2_grpc import WhatUpCoreStub

logger = logging.getLogger(__name__)
PinningEntry = namedtuple("PinningEntry", "bot_id expiration_time".split(" "))
ArchiveData = namedtuple("ArchiveData", "GroupInfo MediaContent".split(" "))

COMMAND_PINNING_TTL = timedelta(seconds=60 * 60)
COMMAND_PINNING: T.Dict[bytes, PinningEntry] = {}
BOT_REGISTRY = defaultdict(dict)
CONTROL_CACHE = deque(maxlen=1028)

DownloadMediaCallback = T.Type[T.Callable[[wuc.WUMessage, bytes], T.Awaitable[None]]]
MediaType = enum.Enum("MediaType", wuc.SendMessageMedia.MediaType.items())


class BotCommandArgsException(Exception):
    def __init__(self, error_msg, help_text, *args, **kwargs):
        self.help_text = help_text
        self.error_msg = error_msg
        super().__init__(*args, **kwargs)

    def message(self):
        if self.error_msg:
            return f"{self.error_msg}\n\n{self.help_text}"
        return self.help_text


class BotCommandArgs(argparse.ArgumentParser):
    def error(self, message):
        help_text = self.format_help()
        raise BotCommandArgsException(message, help_text)

    def exit(self, status=0, message=None):
        help_text = self.format_help()
        raise BotCommandArgsException(message, help_text)


class BaseBot:
    core_client: WhatUpCoreStub

    def __init__(
        self,
        host: str,
        port: int,
        cert: Path,
        mark_messages_read: bool = False,
        read_historical_messages: bool = False,
        control_groups: T.List[wuc.JID] = [],
        archive_files: T.Optional[str] = None,
        connect: bool = True,
        logger=logger,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.cert = cert
        self.logger = logger.getChild(self.__class__.__name__)

        self.control_groups = control_groups
        self.mark_messages_read = mark_messages_read
        self.read_historical_messages = read_historical_messages
        self.archive_files = archive_files

        self.download_queue = asyncio.Queue()
        if connect:
            self.core_client, self.authenticator = create_whatupcore_clients(
                self.host, self.port, self.cert
            )
        self.arg_parser = self.setup_command_args()

    def setup_command_args(self) -> T.Optional[BotCommandArgs]:
        return None

    async def parse_command(
        self, message: wuc.WUMessage
    ) -> T.Optional[argparse.Namespace]:
        if not self.arg_parser:
            return None
        try:
            text = message.content.text
            (_, *args) = shlex.split(text)
            return self.arg_parser.parse_args(args)
        except BotCommandArgsException as e:
            sender = message.info.source.sender
            await self.send_text_message(sender, e.message())
            return None

    async def login(self, username: str, passphrase: str) -> T.Self:
        self.logger = self.logger.getChild(username)
        self.logger.info("Logging in")
        await self.authenticator.login(username, passphrase)
        return self

    async def start(self, **kwargs):
        self.logger.info("Starting bot for user")
        BOT_REGISTRY[self.__class__.__name__][id(self)] = self
        async with asyncio.TaskGroup() as tg:
            self.logger.info("Starting bot")
            tg.create_task(self.authenticator.start())
            tg.create_task(self.listen_messages())
            tg.create_task(self._download_messages_background())
            if self.read_historical_messages:
                tg.create_task(self.listen_historical_messages())
        self.stop()

    def stop(self):
        BOT_REGISTRY[self.__class__.__name__].pop(id(self), None)

    async def listen_historical_messages(self):
        while True:
            self.logger.info("Reading historical messages")
            messages: T.AsyncIterator[
                wuc.WUMessage
            ] = self.core_client.GetPendingHistory(
                wuc.PendingHistoryOptions(historyReadTimeout=60)
            )
            async for message in messages:
                jid_from: wuc.JID = message.info.source.chat
                self.logger.debug(
                    "Got historical message: %s: %s",
                    utils.jid_to_str(jid_from),
                    message.info.id,
                )
                await self._dispatch_message(
                    message, skip_control=True, is_history=True
                )

    async def listen_messages(self):
        while True:
            self.logger.info("Reading messages")
            messages: T.AsyncIterator[wuc.WUMessage] = self.core_client.GetMessages(
                wuc.MessagesOptions(markMessagesRead=self.mark_messages_read)
            )
            async for message in messages:
                await self._dispatch_message(message)

    async def _dispatch_message(
        self,
        message: wuc.WUMessage,
        skip_control=False,
        is_history: bool = False,
        is_archive: bool = False,
        archive_data: T.Optional[ArchiveData] = None,
    ):
        now = datetime.now()
        jid_from: wuc.JID = message.info.source.chat
        source_hash = utils.random_hash(message.info.source.sender.user)
        is_control = any(
            utils.same_jid(jid_from, control) for control in self.control_groups
        ) or any(
            source_hash == sa and pb.expiration_time > now
            for sa, pb in COMMAND_PINNING.items()
        )
        if is_control:
            if skip_control:
                self.logger.info("Skipping control message: %s: %s", utils.jid_to_str(jid_from), message.info.id)
            else:
                self.logger.info("Got control message: %s: %s", utils.jid_to_str(jid_from), message.info.id)
                await self._dispatch_control(message, source_hash)
        else:
                self.logger.info("Got normal message: %s: %s", utils.jid_to_str(jid_from), message.info.id)
            await self.on_message(
                message,
                is_history=is_history,
                is_archive=is_archive,
                archive_data=archive_data,
            )

    async def _dispatch_control(self, message, source_hash):
        if message.info.source.isFromMe:
            return
        message_id = message.info.id
        if message_id in CONTROL_CACHE:
            return
        text = message.content.text
        if not text.startswith(f"@{self.__class__.__name__}"):
            return
        pinned_bot = COMMAND_PINNING.get(source_hash)
        registry = BOT_REGISTRY[self.__class__.__name__]
        t = datetime.now()
        new_pin = False
        if (
            pinned_bot is None
            or pinned_bot.bot_id not in registry
            or pinned_bot.expiration_time > t
        ):
            new_pin = True
            idx: int = int(
                message.info.timestamp.ToSeconds()
                // COMMAND_PINNING_TTL.total_seconds()
            ) % len(registry)
            bot_id = list(registry.keys())[idx]
            pinned_bot = PinningEntry(
                bot_id=bot_id, expiration_time=t + COMMAND_PINNING_TTL
            )
            COMMAND_PINNING[source_hash] = pinned_bot
        if id(self) == pinned_bot.bot_id:
            CONTROL_CACHE.append(message_id)
            if new_pin:
                await self.send_text_message(
                    message.info.source.sender,
                    f"In command mode for the next {COMMAND_PINNING_TTL.total_seconds()} seconds. I will respond to commands for the {self.__class__.__name__} bot until {t + COMMAND_PINNING_TTL} UTC",
                )
            return await self.on_control(message)

    async def download_message_media(self, message: wuc.WUMessage) -> bytes:
        mm = message.content.mediaMessage
        payload = mm.WhichOneof("payload")
        if payload is None:
            return b""
        media_message = utils.convert_protobuf(waw.Message, mm)
        media_content: wuc.MediaContent = await self.core_client.DownloadMedia(
            wuc.DownloadMediaOptions(
                mediaMessage=media_message,
                info=message.info,
            )
        )
        return media_content.Body

    async def _download_messages_background(self):
        while True:
            message, callback = await self.download_queue.get()
            self.logger.info(
                "Download queue processing message: %s: messages left: %d",
                message.info.id,
                self.download_queue.qsize(),
            )
            content: bytes = b""
            try:
                content = await self.download_message_media(message)
            except Exception:
                callback(message, b"")
            try:
                await callback(message, content)
            except Exception:
                self.logger.exception(
                    "Exception calling download_media_message_eventually callback: %s",
                    message.info.id,
                )
            sleep_time = random.randint(1, 10)
            await asyncio.sleep(sleep_time)

    async def download_message_media_eventually(
        self, message: wuc.WUMessage, callback: DownloadMediaCallback
    ):
        await self.download_queue.put((message, callback))

    async def send_text_message(
        self, recipient: wuc.JID, text: str, composing_time: int = 5
    ) -> wuc.SendMessageReceipt:
        recipient_nonad = wuc.JID(user=recipient.user, server=recipient.server)
        options = wuc.SendMessageOptions(
            recipient=recipient_nonad, simpleText=text, composingTime=composing_time
        )
        return await self.core_client.SendMessage(options)

    async def send_media_message(
        self,
        recipient: wuc.JID,
        media_type: MediaType,
        content: bytes,
        title: T.Optional[str] = None,
        caption: T.Optional[str] = None,
        mimetype: T.Optional[str] = None,
        filename: T.Optional[str] = None,
        composing_time: int = 5,
    ) -> wuc.SendMessageReceipt:
        recipient_nonad = wuc.JID(user=recipient.user, server=recipient.server)
        options = wuc.SendMessageOptions(
            recipient=recipient_nonad,
            composingTime=composing_time,
            sendMessageMedia=wuc.SendMessageMedia(
                mediaType=media_type.name,
                caption=caption or "",
                content=content,
                mimetype=mimetype or "",
                title=title or "",
                filename=filename or "",
            ),
        )
        return await self.core_client.SendMessage(options)

    async def on_control(self, message: wuc.WUMessage):
        pass

    async def on_message(
        self,
        message: wuc.WUMessage,
        is_history: bool = False,
        is_archive: bool = False,
        archive_data: T.Optional[ArchiveData] = None,
    ):
        pass

    async def process_archive(self, archive_glob):
        # TODO: this is tightly coupled to ArchiveBot... decouple it somehow
        group_infos = {}
        filenames = list(glob.glob(archive_glob, recursive=True))
        filenames.sort()
        for filename in filenames:
            try:
                await self._process_archive_file(filename, group_infos)
            except Exception:
                self.logger.exception(
                    f"Could not load file: {filename}... trying to continue"
                )

    async def _process_archive_file(
        self, filename, group_infos: T.Dict[str, wuc.GroupInfo]
    ):
        self.logger.info("Loading archive file: %s", filename)
        filename_path = Path(filename)
        with filename_path.open() as fd:
            message: wuc.WUMessage = utils.jsons_to_protobuf(fd.read(), wuc.WUMessage())
        chat_id = utils.jid_to_str(message.info.source.chat)
        metadata = {"GroupInfo": None, "MediaContent": None}
        if chat_id:
            if chat_id in group_infos:
                metadata["GroupInfo"] = group_infos[chat_id]
            elif group_info_filename := message.provenance.get(
                "archivebot__groupInfoPath"
            ):
                group_info_path = filename_path.parent / group_info_filename
                try:
                    with group_info_path.open() as fd:
                        group_info: wuc.GroupInfo = utils.jsons_to_protobuf(
                            fd.read(), wuc.GroupInfo()
                        )
                    metadata["GroupInfo"] = group_info
                    group_infos[chat_id] = group_info
                except FileNotFoundError:
                    self.logger.critical(
                        "Could not find group info in path: %s", group_info_path
                    )

        if media_filename := message.provenance.get("archivebot__mediaPath"):
            media_path = filename_path.parent / media_filename
            try:
                with media_path.open("rb") as fd:
                    media_content = fd.read()
                metadata["MediaContent"] = media_content
            except FileNotFoundError:
                self.logger.critical("Could not find media in path: %s", media_path)
        archive_data = ArchiveData(**metadata)
        await self._dispatch_message(
            message,
            is_history=False,
            is_archive=True,
            archive_data=archive_data,
            skip_control=True,
        )
