import asyncio
import logging
import re
import ssl
import time
import contextlib
from collections import defaultdict
from pathlib import Path
import typing as T

import aiohttp
import socketio

from .. import actions, utils

logger = logging.getLogger(__name__)

COMMAND_PINNING: T.Dict[bytes, T.List[int]] = {}
COMMAND_PINNING_TTL: int = (
    60 * 60
)  # amount of time in seconds a bot should pin to a sender
BOT_REGISTRY = defaultdict(dict)


class BaseBot(socketio.AsyncClientNamespace):
    def __init__(
        self,
        *args,
        name: str | None = None,
        session_locator: dict | None = None,
        timeout=120,
        allow_unauthenticated=False,
        control_groups: list,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not name and not session_locator:
            raise ValueError(
                "Either name alone (for anonymous connections) or session_locator alone (for authenticated connections) must be provided"
            )

        if name and not re.match(r"[a-zA-Z0-9-:_]{3,}", name):
            raise ValueError(
                f"Client name must be at least 8 characters long with only a-zA-Z0-9-:_: {name}"
            )
        elif not name and session_locator:
            self.name = session_locator["sessionId"]
        else:
            self.name = name

        if not allow_unauthenticated and not session_locator:
            raise SystemError(
                "Attempting to instantiate client that disallows unauthenticated sessions without session_locator"
            )
        self.control_groups = control_groups
        self.session_locator = session_locator
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}:{self.name}")
        self._call_lock = asyncio.Lock()
        self._sio: socketio.AsyncClient | None = None

    @classmethod
    async def start(
        cls, *args, host="localhost", port=3000, cert: Path | None = None, **kwargs
    ):
        logger.info("Opening connection")
        bot = cls(*args, **kwargs)
        await bot.connect(f"https://{host}:{port}/", cert)
        try:
            bot.logger.info("Waiting")
            await bot.wait()
        except KeyboardInterrupt:
            bot.logger.info("Exiting")
        finally:
            await bot.disconnect()

    async def connect(self, url, cert: Path | None = None):
        if self._sio:
            await self.disconnect()

        if cert is not None:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.load_verify_locations(cafile=cert)
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            http_session = aiohttp.ClientSession(connector=connector)
            self._sio = sio = socketio.AsyncClient(http_session=http_session)
        else:
            self._sio = sio = socketio.AsyncClient()

        sio.register_namespace(self)
        await sio.connect(url)
        BOT_REGISTRY[self.__class__.__name__][id(self)] = self
        return self

    async def disconnect(self):
        if not self._sio:
            raise ValueError("Trying to disconnect a client that hasn't been connected")
        BOT_REGISTRY[self.__class__.__name__].pop(id(self), None)
        await self._sio.disconnect()

    async def wait(self):
        if not self._sio:
            raise ValueError("Trying to wait on a client that hasn't been connected")
        await self._sio.wait()

    async def download_message_media(self, message) -> bytes:
        self.logger.info("Downloading message media")
        # TODO: transform `message` to only send back essential properties to
        # whatupcore for the download
        return await self.call(actions.read_download_message, message, timeout=5 * 60)

    async def group_metadata(self, chatid) -> dict:
        self.logger.info("Getting group metadata")
        return await self.call(actions.read_group_metadata, dict(chatId=chatid))

    @contextlib.asynccontextmanager
    async def disappearing_messages(self, sender, message_ttl, **kwargs):
        kwargs.setdefault("vamp_max_seconds", 5)
        await self.send_message(
            sender, {"disappearingMessagesInChat": 60 * 60 * 12}, **kwargs
        )
        yield
        await self.send_message(sender, {"disappearingMessagesInChat": False}, **kwargs)

    async def send_message(
        self,
        chatid: str,
        message_content: dict,
        message_options: dict | None = None,
        clear_chat_status=True,
        vamp_max_seconds=60,
    ) -> dict:
        data = {
            "chatId": chatid,
            "messageContent": message_content,
            "messageOptions": message_options or {},
            "clearChatStatus": clear_chat_status,
            "vampMaxSeconds": vamp_max_seconds,
        }
        self.logger.info(f"Sending message: {chatid=}")
        return await self.call(actions.write_send_message, data)

    async def messages_subscribe(self):
        self.logger.info("Subscribing to messages")
        await self.emit(actions.read_messages_subscribe)

    def dispatch_control_message(self, event_type, message):
        sender = utils.get_message_sender(message)
        if not sender:
            return None
        sender_hash = utils.random_hash(sender)
        t = int(time.time())
        if sender_hash in COMMAND_PINNING and COMMAND_PINNING[sender_hash][1] > t:
            target_bot_id = COMMAND_PINNING[sender_hash][0]
            COMMAND_PINNING[sender_hash][1] = t + COMMAND_PINNING_TTL
        else:
            registry = BOT_REGISTRY[self.__class__.__name__]
            index = (t // COMMAND_PINNING_TTL) % len(registry)
            target_bot_id = list(registry.keys())[index]
            COMMAND_PINNING[sender_hash] = [target_bot_id, t + COMMAND_PINNING_TTL]
        if id(self) == target_bot_id:
            return "read_messages_control"
        else:
            return "read_messages_control_secondary"

    def get_event_type(self, event_type, *args) -> str | None:
        whatup_event = actions.EVENTS.get(event_type)
        if whatup_event == actions.EVENTS.get("read_messages"):
            self.logger.info("got a message event")
            try:
                message = args[0]
                if message["key"]["remoteJid"] in self.control_groups:
                    whatup_event = self.dispatch_control_message(event_type, message)
            except (IndexError, KeyError):
                pass
        return whatup_event

    async def trigger_event(self, event: str, *args):
        if whatup_event := self.get_event_type(event, *args):
            self.logger.info(f"Its a whatup event: {whatup_event}: {event}")
            return await super().trigger_event(whatup_event, *args)
        return await super().trigger_event(event, *args)

    async def call(self, *args, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        async with self._call_lock:
            return await super().call(*args, **kwargs)

    async def on_connect(self):
        self.logger.info("Connected")
        if self.session_locator:
            self.logger.info("Using session locator")
            data = dict(sharedConnection=True, sessionLocator=self.session_locator)
            error = await self.call(actions.connection_auth, data)
            if error["error"] is not None:
                raise ConnectionError(error["error"])
            self.logger.info(f"Authenticated: {error}")
        else:
            self.logger.info(f"Anonymous connection: {self.name=}")
            await self.emit(actions.connection_auth_anonymous, dict(name=self.name))

    async def on_connection_auth_locator(self, session_locator):
        self.logger.debug(f"Recieved session locator: {session_locator['sessionId']}")
        self.session_locator = session_locator

    async def on_connection_qr(self, qr_code):
        print(utils.qrcode_gen(qr_code["qr"]))
