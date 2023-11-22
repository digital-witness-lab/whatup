from datetime import datetime

from .. import NotRegisteredError, utils
from . import BaseBot
from ..protos import whatupcore_pb2 as wuc
from ..device_manager.credentials_manager import CredentialsManager, Credential


class OnboardBot(BaseBot):
    async def register(
        self,
        username: str,
        credentials_manager: CredentialsManager,
        default_group_permission: wuc.GroupPermission.ValueType,
    ):
        logger = self.logger.getChild(username)
        logger.info("Registering user")
        passphrase = utils.random_passphrase()
        try:
            async for qrcode in self.authenticator.register(
                username, passphrase, default_group_permission
            ):
                print(utils.qrcode_gen(qrcode))
                logger.critical("QRCode: (%s)", qrcode)
        except NotRegisteredError:
            logger.exception("Could not register user")
            return
        logger.info("User registered")

        meta = {
            "onboardbot__timestamp": datetime.now().isoformat(),
            "onboardbot__default_permission": wuc.GroupPermission.Name(
                default_group_permission
            ),
        }
        credential = Credential(username, passphrase, meta=meta)
        credentials_manager.write_credential(credential)

    async def login(self, *args, **kwargs):
        raise NotImplementedError()

    async def start(self, *args, **kwargs):
        raise NotImplementedError()
