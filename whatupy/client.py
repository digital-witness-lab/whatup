import asyncio
import logging
import re
import ssl
from pathlib import Path

import aiohttp
import socketio

from . import actions, utils

logger = logging.getLogger(__name__)


class WhatUpBase(socketio.AsyncClientNamespace):
    def __init__(
        self,
        *args,
        name: str | None = None,
        session_locator: dict | None = None,
        timeout=120,
        allow_unauthenticated=False,
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
        return self

    async def disconnect(self):
        if not self._sio:
            raise ValueError("Trying to disconnect a client that hasn't been connected")
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

    async def send_message(
        self, chatid: str, message: str, clear_chat_status=True, vamp_max_seconds=60
    ) -> dict:
        data = {
            "chatId": chatid,
            "message": message,
            "clearChatStatus": clear_chat_status,
            "vampMaxSeconds": vamp_max_seconds,
        }
        self.logger.info(f"Sending message: {data=}")
        return await self.call(actions.write_send_message, data)

    async def messages_subscribe(self):
        self.logger.info("Subscribing to messages")
        await self.emit(actions.read_messages_subscribe)

    async def trigger_event(self, event: str, *args):
        if whatup_event := actions.EVENTS.get(event):
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
