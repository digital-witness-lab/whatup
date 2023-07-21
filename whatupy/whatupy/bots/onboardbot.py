import json
from pathlib import Path

from .. import NotRegisteredError, utils
from . import BaseBot


class OnboardBot(BaseBot):
    async def register(self, username: str, credentials_file: Path):
        logger = self.logger.getChild(username)
        logger.info("Registering user")
        passphrase = utils.random_passphrase()
        try:
            async for qrcode in self.authenticator.register(username, passphrase):
                print(utils.qrcode_gen(qrcode))
        except NotRegisteredError:
            logger.exception("Could not register user")
            return
        logger.info("User registered")
        credentials = {"username": username, "passphrase": passphrase}
        with credentials_file.open("w+") as fd:
            json.dump(credentials, fd)

    async def login(self, *args, **kwargs):
        raise NotImplementedError()

    async def start(self, *args, **kwargs):
        raise NotImplementedError()
