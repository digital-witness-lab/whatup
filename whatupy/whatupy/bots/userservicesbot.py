import json
from pathlib import Path
import typing as T

import qrcode
import dataset

from .. import NotRegisteredError, utils
from . import BaseBot
from . import BotCommandArgs, MediaType
from ..protos import whatupcore_pb2 as wuc
from ..connection import WhatUpAuthentication


class UserClient(BaseBot):
    pass

class BotManager:
    def __init__(self, bot_class):
        # create this bot that does what run_multi_bots and what the self.users
        # in UserServicesBot. This should be able to lazy-instantiate on
        # session dir
        pass


class UserServicesBot(BaseBot):
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)
        self.users: T.Dict[str, UserClient] = {}
        super().__init__(*args, **kwargs)

    def listen_new_sessions():
        # look for new files in the session directory that arent currently
        # loaded
