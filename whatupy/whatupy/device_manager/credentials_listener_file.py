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

    async def listen(self, device_manager):
        logger.debug("CredentialsListenerFile listening to paths: %s", self.paths)
        should_loop = True
        while should_loop or (await self.blocker.wait()):
            logger.debug("Looking for new credentials")
            self.blocker.clear()
            credentials = []
            should_loop = False
            for path in self.paths:
                if path.is_file():
                    credentials.append(path)
                elif path.is_dir():
                    should_loop = True
                    credentials.extend(
                        path / filename for filename in path.glob("*.json")
                    )
                else:
                    should_loop = True
                    credentials.extend(
                        path / filename for filename in glob.glob(str(path))
                    )
            for credential_file in credentials:
                try:
                    credential = json.load(credential_file.open())
                    if not all(f in credential for f in ("username", "passphrase")):
                        logger.critical("Invalid credentials file: %s", credential_file)
                        continue
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
                    continue
            await asyncio.sleep(self.timeout)

    def mark_dead(self, username):
        logger.info("Marking user dead: %s", username)
        self.active_usernames.discard(username)
        self.blocker.set()
