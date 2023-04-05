import asyncio
import logging
import json
from pathlib import Path


from .client import WhatUpBase


logger = logging.getLogger(__name__)


class OnboardBot(WhatUpBase):
    def __init__(
        self,
        name,
        session_path,
        *args,
        **kwargs,
    ):
        self.onboarding = asyncio.Lock()
        self.session_path: Path = session_path
        super().__init__(*args, name=name, **kwargs, allow_unauthenticated=True)

    async def on_connection_ready(self, *args, **kwargs):
        self.onboarding.release()

    async def on_connection_auth_locator(self, session_locator):
        await super().on_connection_auth_locator(session_locator)
        self.logger.info(f"Saving session data to: {self.session_path}")
        with open(self.session_path, "w+") as fd:
            fd.write(json.dumps(session_locator))
