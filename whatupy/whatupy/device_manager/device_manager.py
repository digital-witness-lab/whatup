from dataclasses import dataclass
import asyncio
import logging
from collections import abc, defaultdict
import typing as T

from ..bots import BaseBot
from .credentials_listener import CredentialsListener


logger = logging.getLogger(__name__)


@dataclass
class DeviceObject:
    username: str
    bot: BaseBot
    task: asyncio.Task


class DeviceManager:
    def __init__(
        self,
        bot_factory: abc.Callable[[], BaseBot],
        credential_listeners: T.List[CredentialsListener],
        logger=logger,
    ):
        self.bot_factory = bot_factory
        self.credential_listeners: T.List[CredentialsListener] = credential_listeners
        self.devices: T.Dict[str, DeviceObject] = {}
        self.logger = logger.getChild(self.__class__.__name__)
        self.reconnect_backoff = defaultdict(int)

    async def start(self):
        self.logger.info("Starting device manager")
        async with asyncio.TaskGroup() as tg:
            for listener in self.credential_listeners:
                tg.create_task(listener.listen(self))
            # figure out how to wait for the bot tasks from the devices list as
            # well. Maybe this is also a good way to have a restart mechanism
            # on error with exp backoff?

    async def _start_bot(self, bot: BaseBot, username: str, credentials):
        try:
            bot = await bot.login(**credentials)
            await bot.start()
        except Exception:
            self.logger.exception("Exception running bot")
        await self._on_bot_dead(username)

    async def on_credentials(self, credentials):
        username = credentials["username"]
        if backoff := self.reconnect_backoff[username]:
            t = 2 ** min(backoff, 11)  # max of 35min backoff time
            self.logger.critical(
                "Backingoff for device reconnection: %s: %d: %f seconds",
                username,
                backoff,
                t,
            )
            await asyncio.sleep(t)
        bot = self.bot_factory()
        task = asyncio.create_task(
            self._start_bot(bot, username, credentials), name=username
        )
        device = DeviceObject(username=username, bot=bot, task=task)
        self.devices[username] = device
        asyncio.get_event_loop().call_later(
            60,
            self._reset_backoff,
            username,
            self.reconnect_backoff.get(username),
        )
        await self.on_device_start(device)

    def _reset_backoff(self, username, backoff_value):
        if self.reconnect_backoff.get(username) != backoff_value:
            return
        if username not in self.devices:
            return
        self.logger.info("Resetting bot backoff to 0: %d: %s", backoff_value, username)
        self.reconnect_backoff[username] = 0

    def get_device(self, username: str) -> DeviceObject:
        return self.devices[username]

    async def _on_bot_dead(self, username):
        try:
            self.logger.critical("Bot dead: %s", username)
            device = self.devices.pop(username)
            device.bot.stop()
            self.reconnect_backoff[username] += 1
            for listener in self.credential_listeners:
                listener.mark_dead(username)
            await self.on_bot_dead(device)
        except KeyError:
            self.logger.exception(
                "Bot task finished but we can't find reference to it: %s", task
            )

    async def on_bot_dead(self, device: DeviceObject):
        pass

    async def on_device_start(self, device: DeviceObject):
        pass
