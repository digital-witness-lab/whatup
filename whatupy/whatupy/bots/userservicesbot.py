import json
from pathlib import Path
import asyncio
import typing as T
import logging

import qrcode
import dataset

from .. import NotRegisteredError, utils
from . import BaseBot, BotType
from . import BotCommandArgs, MediaType
from ..protos import whatupcore_pb2 as wuc
from ..connection import WhatUpAuthentication


logger = logging.getLogger(__name__)


class UserServicesBot(DeviceManager, BaseBot):
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)
        self.users: T.Dict[str, UserClient] = {}
        super().__init__(*args, **kwargs)

    def listen_new_sessions(self):
        # look for new files in the session directory that arent currently
        # loaded
