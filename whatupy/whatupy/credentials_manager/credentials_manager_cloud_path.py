import asyncio
import glob
import json
import logging
import typing as T

from cloudpathlib import AnyPath

from .credentials_manager import (Credential, CredentialsManager,
                                  IncompleteCredentialsException)

logger = logging.getLogger(__name__)


class CredentialsManagerCloudPath(CredentialsManager):
    url_patterns = [
        r"^gs://",  # google cloud storage
        r"^/",  # absolute file spec
        r"^\./",  # relative file spec
    ]

    def __init__(self, path: str, timeout: int = 60):
        self.path = AnyPath(path)
        logger.info("Managing credentials for path: %s", self.path)
        self.active_usernames: T.Dict[str, AnyPath] = {}
        self.timeout = timeout
        self.blocker = asyncio.Event()

    def _get_credentials(self) -> T.Tuple[bool, T.List[AnyPath]]:
        should_loop = False
        credentials = []
        path = self.path
        if path.is_file():
            credentials.append(path)
        elif path.is_dir():
            should_loop = True
            credentials.extend(path.glob("*.json"))
        else:
            should_loop = True
            credentials.extend(path / filename for filename in glob.glob(str(path)))
        return should_loop, credentials

    def read_credential(self, path: AnyPath) -> Credential:
        logger.debug("Reading credentials: %s", str(path))
        credential = json.load(path.open())
        try:
            return Credential(**credential)
        except TypeError:
            raise IncompleteCredentialsException(
                f"Incomplete credentials: {credential.keys()}"
            )

    def write_credential(self, credential: Credential):
        self.path.mkdir(parents=True, exist_ok=True)
        path = self.path / f"{credential.username}.json"
        logger.info("Writing credentials: %s", str(path))
        with path.open("w+") as fd:
            json.dump(credential.asdict(), fd)

    async def _handle_credential(self, device_manager, credential_file: AnyPath):
        try:
            credential = self.read_credential(credential_file)
            username = credential.username
            if username not in self.active_usernames:
                logger.info(
                    "Found new credential to connect to: %s: %s",
                    username,
                    credential_file,
                )
                self.active_usernames[username] = credential_file
                await device_manager.on_credentials(self, credential)
        except ValueError:
            logger.exception(f"Could not parse credential: {credential_file}")
            return

    async def listen(self, device_manager):
        logger.info("CredentialsManagerFile listening to path: %s", self.path)
        should_loop = True
        while should_loop or (await self.blocker.wait()):
            self.blocker.clear()
            should_loop, credentials = self._get_credentials()
            for credential_file in credentials:
                await self._handle_credential(device_manager, credential_file)
            await asyncio.sleep(self.timeout)

    def mark_dead(self, username):
        logger.info("Marking user dead: %s", username)
        self.active_usernames.pop(username, None)
        self.blocker.set()

    def unregister(self, username):
        credential_file = self.active_usernames.pop(username)
        logger.info("Removing session file: %s", credential_file)
        try:
            credential_file.unlink(missing_ok=True)
        except OSError as e:
            logger.critical(
                "Could not remove credentials file: %s: %s", credential_file, e
            )
