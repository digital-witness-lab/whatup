from pathlib import Path
from functools import partial
import typing as T

from .credentials_listener_file import CredentialsListenerFile
from .device_manager import DeviceManager
from ..bots import BotType


async def run_multi_bots(bot: T.Type[BotType], paths: T.List[Path], bot_args: dict):
    bot_factory = partial(bot, **bot_args)
    credential_listener = CredentialsListenerFile(paths)
    device_manager = DeviceManager(bot_factory, [credential_listener])
    await device_manager.start()
