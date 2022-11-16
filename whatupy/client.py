import asyncio
import typing

import socketio

from . import actions


class WhatUpBase(socketio.AsyncClientNamespace):
    __event_registry: dict[str, typing.Callable] = {}

    def __init__(self, *args, session_locator=None, timeout=120, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_locator = session_locator
        self.timeout = timeout
        self._call_lock = asyncio.Lock()

    @classmethod
    async def connect(cls, url, **kwargs):
        sio = socketio.AsyncClient(logger=True)
        sio.register_namespace(cls(**kwargs))
        await sio.connect(url)
        return sio

    async def download_message_media(self, message) -> bytes:
        # TODO: transform `message` to only send back essential properties to
        # whatupcore for the download
        media: bytes = await self.call(actions.read_download_message, message, timeout=5*60)
        return media

    async def group_metadata(self, chatid) -> dict:
        return await self.call(actions.read_group_metadata, dict(chatId=chatid))

    async def send_message(self, chatid, message, clear_chat_status=True, vamp_max_seconds=60) -> dict:
        data = {
            'chatId': chatid,
            'message': message,
            'clearChatStatus': clear_chat_status,
            'vampMaxSeconds': vamp_max_seconds,
        }
        return await self.call(actions.write_send_message, data)

    async def messages_subscribe(self):
        await self.emit(actions.read_messages_subscribe)

    async def trigger_event(self, event, *args):
        if whatup_event := actions.EVENTS.get(event):
            print(f"Its a whatup event: {whatup_event}: {event}")
            return await super().trigger_event(whatup_event, *args)
        return await super().trigger_event(event, *args)

    async def call(self, *args, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        async with self._call_lock:
            return await super().call(*args, **kwargs)

    async def on_connect(self):
        print("!!!!Connected")
        if self.session_locator:
            print("Using session locator")
            data = dict(sharedConnection=True, sessionLocator=self.session_locator)
            error = await self.call(actions.connection_auth, data)
            if error['error'] is not None:
                raise ConnectionError(error['error'])
        else:
            print("Anonymous connection")
            pass # do anonymous connection + listen for new locator

