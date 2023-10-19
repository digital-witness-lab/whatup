import logging
import asyncio
import json
import glob
from pathlib import Path
import typing as T

from .credentials_listener import CredentialsListener


logger = logging.getLogger(__name__)


class CredentialsListenerFile(CredentialsListener):
    def __init__(self, paths: T.List[Path], timeout: int = 60):
        self.paths = paths
        self.active_usernames: T.Set[str] = set()
        self.timeout = timeout
        self.blocker = asyncio.Event()

    def _get_credentials(self) -> T.Tuple[bool, T.List[Path]]:
        should_loop = False
        credentials = []
        for path in self.paths:
            if path.is_file():
                credentials.append(path)
            elif path.is_dir():
                should_loop = True
                credentials.extend(path / filename for filename in path.glob("*.json"))
            else:
                should_loop = True
                credentials.extend(path / filename for filename in glob.glob(str(path)))
        return should_loop, credentials

    async def _handle_credential(self, device_manager, credential_file: Path):
        try:
            credential = json.load(credential_file.open())
            if not all(f in credential for f in ("username", "passphrase")):
                logger.critical("Invalid credentials file: %s", credential_file)
                return
            username = credential["username"]
            if username not in self.active_usernames:
                logger.info(
                    "Found new credential to connect to: %s: %s",
                    username,
                    credential_file,
                )
                await device_manager.on_credentials(credential)
                self.active_usernames.add(username)
        except ValueError:
            logger.exception(f"Could not parse credential: {credential_file}")
            return

    async def listen(self, device_manager):
        logger.debug("CredentialsListenerFile listening to paths: %s", self.paths)
        should_loop = True
        while should_loop or (await self.blocker.wait()):
            logger.debug("Looking for new credentials")
            self.blocker.clear()
            should_loop, credentials = self._get_credentials()
            for credential_file in credentials:
                await self._handle_credential(device_manager, credential_file)
            await asyncio.sleep(self.timeout)

    def mark_dead(self, username):
        logger.info("Marking user dead: %s", username)
        self.active_usernames.discard(username)
        self.blocker.set()
