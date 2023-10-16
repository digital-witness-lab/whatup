from pathlib import Path
from functools import partial
import typing as T
import logging

import dataset

from . import BaseBot
from ..protos import whatupcore_pb2 as wuc
from ..device_manager import DeviceManager, CredentialsListenerFile


logger = logging.getLogger(__name__)


class _UserBot(BaseBot):
    def __init__(self, host, port, cert, services_bot, **kwargs):
        self.services_bot: UserServicesBot = services_bot
        super().__init__(
            host,
            port,
            cert,
            mark_messages_read=False,
            read_messages=False,
            read_historical_messages=False,
        )

    async def post_start(self):
        connection_status: wuc.ConnectionStatus = (
            await self.core_client.GetConnectionStatus()
        )
        self.username = self.authenticator.username
        self.jid = connection_status.JID
        self.jid_anon = connection_status.JIDAnon
        await self.services_bot.new_device(self)


class UserServicesBot(BaseBot):
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)

        self.users: T.Dict[wuc.JID, _UserBot] = {}

        bot_factory = partial(_UserBot, services_bot=self, **kwargs)
        credential_listener = CredentialsListenerFile([sessions_dir])
        self.device_manager = DeviceManager(
            bot_factory=bot_factory, credential_listenrs=[credential_listener]
        )
        super().__init__(*args, **kwargs)

    async def on_message(self, message: wuc.WUMessage):
        sender = message.info.source.sender
        user = self.users.get(sender)
        if user is None:
            return
        await self.send_text_message(user.jid, "i recognize you!")

    async def new_device(self, user: _UserBot):
        self.users[user.jid_anon] = user
        user_state = self.db["registered_users"].find_one(username=username)
        if not user_state.get("is_onboarded", False):
            await self.onboard_user(user)

    async def onboard_user(self, user: _UserBot):
        # send consent inform about how to change ACL
        await self.send_text_message(user.jid, "onboarding time")
