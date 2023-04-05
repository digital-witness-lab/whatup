import asyncio
import logging

import socketio

from . import actions
from . import utils


logger = logging.getLogger(__name__)


class WhatUpBase(socketio.AsyncClientNamespace):
    def __init__(
        self,
        *args,
        name=None,
        session_locator=None,
        timeout=120,
        logger=logger,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name or utils.random_name()
        self.session_locator = session_locator
        self.timeout = timeout
        self.logger = logger
        self._call_lock = asyncio.Lock()

    @classmethod
    async def connect(cls, url, **kwargs):
        sio = socketio.AsyncClient()
        sio.register_namespace(cls(**kwargs))
        await sio.connect(url)
        return sio

    async def download_message_media(self, message) -> bytes:
        self.logger.info("Downloading message media")
        # TODO: transform `message` to only send back essential properties to
        # whatupcore for the download
        media: bytes = await self.call(
            actions.read_download_message, message, timeout=5 * 60
        )
        return media

    async def group_metadata(self, chatid) -> dict:
        self.logger.info("Getting group metadata")
        return await self.call(actions.read_group_metadata, dict(chatId=chatid))

    async def send_message(
        self, chatid: str, message: str, clear_chat_status=True, vamp_max_seconds=60
    ) -> dict:
        self.logger.info("Sending message")
        data = {
            "chatId": chatid,
            "message": message,
            "clearChatStatus": clear_chat_status,
            "vampMaxSeconds": vamp_max_seconds,
        }
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
