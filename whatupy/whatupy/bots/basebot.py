import asyncio
import logging
from collections import defaultdict, namedtuple, deque
from pathlib import Path
import time
import typing as T

from ..connection import create_whatupcore_clients
from ..protos.whatupcore_pb2_grpc import WhatUpCoreStub
from ..protos import whatupcore_pb2 as wuc
from ..protos import whatsappweb_pb2 as waw
from .. import utils


logger = logging.getLogger(__name__)
PinningEntry = namedtuple("PinningEntry", "bot_id expiration_time".split(" "))

COMMAND_PINNING_TTL = 60 * 60
COMMAND_PINNING: T.Dict[bytes, PinningEntry] = {}
BOT_REGISTRY = defaultdict(dict)
CONTROL_CACHE = deque(maxlen=1028)


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
        logger=logger,
        **kwargs
    ):
        self.host = host
        self.port = port
        self.cert = cert

        self.control_groups = control_groups
        self.mark_messages_read = mark_messages_read
        self.read_historical_messages = read_historical_messages

        self.logger = logger.getChild(self.__class__.__name__)

    async def start(self, username: str, passphrase: str, **kwargs):
        self.logger.info("Starting bot for user: %s", username)
        self.logger = self.logger.getChild(username)
        self.core_client, self.authenticator = create_whatupcore_clients(
            self.host, self.port, self.cert
        )
        await self.authenticator.login(username, passphrase)

        BOT_REGISTRY[self.__class__.__name__][id(self)] = self
        async with asyncio.TaskGroup() as tg:
            self.logger.info("Starting bot")
            tg.create_task(self.authenticator.start())
            tg.create_task(self.listen_messages())
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
                await self._dispatch_message(message, skip_control=True)

    async def listen_messages(self):
        while True:
            self.logger.info("Reading messages")
            messages: T.AsyncIterator[wuc.WUMessage] = self.core_client.GetMessages(
                wuc.MessagesOptions(markMessagesRead=self.mark_messages_read)
            )
            async for message in messages:
                await self._dispatch_message(message)

    async def _dispatch_message(self, message: wuc.WUMessage, skip_control=False):
        jid_from: wuc.JID = message.info.source.chat
        is_control = any(
            utils.same_jid(jid_from, control) for control in self.control_groups
        )
        if is_control:
            if skip_control:
                self.logger.debug("Skipping control message: %s", message.info)
            else:
                self.logger.debug("Got control message: %s", message.info)
                await self._dispatch_control(message)
        else:
            self.logger.debug("Got normal message: %s", message.info)
            await self.on_message(message)

    async def _dispatch_control(self, message):
        if message.info.source.isFromMe:
            return
        message_id = message.info.id
        if message_id in CONTROL_CACHE:
            return
        source_hash = utils.random_hash(message.info.source.user)
        pinned_bot = COMMAND_PINNING.get(source_hash)
        registry = BOT_REGISTRY[self.__class__.__name__]
        t = int(time.time())
        if (
            pinned_bot is None
            or pinned_bot.bot_id not in registry
            or pinned_bot.expiration_time > t
        ):
            idx: int = (
                message.info.timestamp.ToSeconds() // COMMAND_PINNING_TTL
            ) % len(registry)
            bot_id = list(registry.keys())[idx]
            pinned_bot = PinningEntry(
                bot_id=bot_id, expiration_time=t + COMMAND_PINNING_TTL
            )
            COMMAND_PINNING[source_hash] = pinned_bot
        if id(self) == pinned_bot.bot_id:
            CONTROL_CACHE.append(message_id)
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

    async def send_text_message(
        self, recipient: wuc.JID, text: str, composing_time: int = 5
    ) -> wuc.SendMessageReceipt:
        options = wuc.SendMessageOptions(
            recipient=recipient, simpleText=text, composingTime=composing_time
        )
        return await self.core_client.SendMessage(options)

    async def on_control(self, message: wuc.WUMessage):
        raise NotImplementedError

    async def on_message(self, message: wuc.WUMessage):
        raise NotImplementedError
