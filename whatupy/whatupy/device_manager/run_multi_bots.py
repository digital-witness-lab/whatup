from pathlib import Path
from functools import partial
import typing as T

from ..credentials_manager import CredentialsManager
from .device_manager import DeviceManager
from ..bots import BotType


async def run_multi_bots(
    bot: T.Type[BotType], paths: T.List[str | Path], bot_args: dict
):
    bot_factory = partial(bot, **bot_args)
    credential_managers = [CredentialsManager.from_url(str(path)) for path in paths]
    device_manager = DeviceManager(bot_factory, credential_managers)
    await device_manager.start()
