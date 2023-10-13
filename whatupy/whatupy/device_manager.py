from dataclasses import dataclass
import asyncio
import logging
from collections import abc
import typing as T

from .bots import BaseBot


logger = logging.getLogger(__name__)


@dataclass
class DeviceObject:
    username: str
    bot: BaseBot
    task: asyncio.Task


class DeviceManager:
    def __init__(self, bot_factory: abc.Callable[[], BaseBot], logger=logger):
        self.bot_factory = bot_factory
        self.credential_listeners: T.List[T.Coroutine] = []
        self.tasks: T.Dict[asyncio.Task, str] = {}
        self.devices: T.Dict[str, DeviceObject] = {}
        self.logger = logger.getChild(self.__class__.__name__)

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            for listener in self.credential_listeners:
                tg.create_task(listener)
            # figure out how to wait for the bot tasks from the devices list as
            # well. Maybe this is also a good way to have a restart mechanism
            # on error with exp backoff?

    async def on_credentials(self, credentials):
        username = credentials["username"]
        bot = await self.bot_factory().login(**credentials)
        task = asyncio.create_task(bot.start(), name=username)
        self.tasks[task] = username
        # TODO: check that this done callback can be a coroutine
        task.add_done_callback(self._on_bot_dead)
        device = DeviceObject(username=username, bot=bot, task=task)
        self.devices[username] = device
        await self.on_device_start(device)

    async def _on_bot_dead(self, task):
        try:
            username = self.tasks.pop(task)
            device = self.devices.pop(username)
            device.bot.stop()
            await self.on_bot_dead(device)
        except KeyError:
            self.logger.exception(
                "Bot task finished but we can't find reference to it: %s", task
            )

    async def on_bot_dead(self, device: DeviceObject):
        pass

    async def on_device_start(self, device: DeviceObject):
        pass
