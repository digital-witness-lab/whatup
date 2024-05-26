import asyncio
import logging
import typing as T
from collections import abc, defaultdict
from dataclasses import dataclass, field

from ..bots.basebot import BaseBot, InvalidCredentialsException
from ..credentials_manager import Credential, CredentialsManager

logger = logging.getLogger(__name__)


@dataclass
class DeviceObject:
    username: str
    bot: BaseBot
    task: asyncio.Task
    unregistered: bool = field(default=False)


class DeviceManager:
    def __init__(
        self,
        bot_factory: abc.Callable[[], BaseBot],
        credential_managers: T.List[CredentialsManager],
        unregister_invalid_credentials: bool = True,
        logger=logger,
    ):
        self.bot_factory = bot_factory
        self.credential_managers: T.List[CredentialsManager] = credential_managers
        self.devices: T.Dict[str, DeviceObject] = {}
        self.unregister_invalid_credentials = unregister_invalid_credentials
        self.logger = logger.getChild(self.__class__.__name__)
        self.reconnect_backoff = defaultdict(int)

    async def start(self):
        self.logger.info("Starting device manager")
        async with asyncio.TaskGroup() as tg:
            for manager in self.credential_managers:
                tg.create_task(manager.listen(self))
            # figure out how to wait for the bot tasks from the devices list as
            # well. Maybe this is also a good way to have a restart mechanism
            # on error with exp backoff?
        self.logger.critical("Device Manager Closing")

    async def _start_bot(self, bot: BaseBot, username: str):
        try:
            await bot.start()
        except Exception:
            self.logger.exception("Exception running bot")
        await self._on_bot_dead(username)

    async def on_credentials(self, manager: CredentialsManager, credential: Credential):
        username = credential.username
        if username in self.devices:
            self.logger.info(
                "Got credentials for existing bot... skipping: %s", username
            )
            return
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
        try:
            bot = await bot.login(credential)
        except InvalidCredentialsException as e:
            if self.unregister_invalid_credentials:
                self.logger.critical(
                    "Invalid credentials for user... unregistering: %s", username
                )
                await self.unregister(username)
                return
            raise e
        task = asyncio.create_task(self._start_bot(bot, username), name=username)
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
        if backoff_value == 0 or self.reconnect_backoff.get(username) != backoff_value:
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
            if device.unregistered:
                self.logger.critical("Device unregistered. Not trying to reconnect.")
                return
            device.bot.stop()
            self.reconnect_backoff[username] += 1
            for manager in self.credential_managers:
                self.logger.critical("Marking user as dead in: %s", manager)
                manager.mark_dead(username)
            await self.on_bot_dead(device)
        except KeyError:
            self.logger.exception(
                "Bot task finished but we can't find reference to it: %s", username
            )

    async def on_bot_dead(self, device: DeviceObject):
        pass

    async def on_device_start(self, device: DeviceObject):
        pass

    async def unregister(self, username: str):
        self.logger.warning("Calling unregister for user: %s", username)
        for manager in self.credential_managers:
            manager.unregister(username)
        device = self.devices.pop(username, None)
        if device is not None:
            device.unregistered = True
            await device.bot.unregister()
            device.task.cancel()
            device.bot.stop()
            self.reconnect_backoff.pop(device.username, None)
