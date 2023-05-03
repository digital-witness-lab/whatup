import asyncio
import json
import logging
from pathlib import Path

from . import BaseBot

logger = logging.getLogger(__name__)


class OnboardBot(BaseBot):
    def __init__(
        self,
        name,
        session_path,
        *args,
        **kwargs,
    ):
        self.done = asyncio.Event()
        self.session_path: Path = session_path
        super().__init__(*args, name=name, **kwargs, allow_unauthenticated=True)

    async def on_connection_ready(self, *args, **kwargs):
        self.done.set()
        self.logger.info("Onboarding complete... releasing lock")

    async def on_connection_auth_locator(self, session_locator):
        await super().on_connection_auth_locator(session_locator)
        self.logger.info(f"Saving session data to: {self.session_path}")
        with open(self.session_path, "w+") as fd:
            fd.write(json.dumps(session_locator))

    @classmethod
    async def start(
        cls, *args, host="localhost", port=3000, cert: Path | None = None, **kwargs
    ):
        logger.info("Opening connection")
        bot = cls(*args, **kwargs)
        await bot.connect(f"https://{host}:{port}/", cert)
        try:
            bot.logger.info("Waiting")
            await bot.done.wait()
        except KeyboardInterrupt:
            bot.logger.info("Exiting")
        finally:
            await bot.disconnect()
