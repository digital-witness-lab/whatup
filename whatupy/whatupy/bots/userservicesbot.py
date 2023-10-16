from pathlib import Path
from functools import partial
import typing as T
import logging

import qrcode
import dataset

from .. import NotRegisteredError, utils
from . import BaseBot, BotType
from . import BotCommandArgs, MediaType
from ..protos import whatupcore_pb2 as wuc
from ..connection import WhatUpAuthentication
from ..device_manager import DeviceManager, CredentialsListenerFile


logger = logging.getLogger(__name__)


class _UserBot(BaseBot):
    def __init__(self, host, port, cert, services_bot, **kwargs):
        self.services_bot = services_bot
        super().__init__(host, port, cert, mark_messages_read=False, read_messages=False, read_historical_messages=False)

    async def post_start(self):
        connection_status: wuc.ConnectionStatus = await self.core_client.GetConnectionStatus()
        self.jid = connection_status.JID
        self.jid_anon = connection_status.JIDAnon



class UserServicesBot(BaseBot):
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)

        bot_factory = partial(_UserBot, services_bot=self, **kwargs)
        credential_listener = CredentialsListenerFile([sessions_dir])
        self.device_manager = DeviceManager(
                bot_factory=bot_factory,
                credential_listenrs=[credential_listener]
        )
        super().__init__(*args, **kwargs)

    def listen_new_sessions(self):
        # look for new files in the session directory that arent currently
        # loaded
