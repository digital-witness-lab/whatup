from pathlib import Path
from functools import partial
import typing as T

from .credentials_manager import CredentialsManagerCloudPath
from .device_manager import DeviceManager
from ..bots import BotType


async def run_multi_bots(bot: T.Type[BotType], paths: T.List[str], bot_args: dict):
    bot_factory = partial(bot, **bot_args)
    credential_managers = [CredentialsManagerCloudPath(path) for path in paths]
    device_manager = DeviceManager(bot_factory, credential_managers)
    await device_manager.start()
