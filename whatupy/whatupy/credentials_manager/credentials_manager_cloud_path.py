import asyncio
import json
import random
import typing as T

from cloudpathlib import CloudPath

from .credentials_manager import (
    Credential,
    CredentialsManager,
    IncompleteCredentialsException,
)


class CredentialsManagerCloudPath(CredentialsManager):
    url_patterns = [
        r"^gs://",  # google cloud storage
        r"^/",  # absolute file spec
        r"^\./",  # relative file spec
    ]

    def __init__(self, url: str, timeout: int = 60):
        super().__init__(url)
        self.path = CloudPath(url)
        self.active_usernames: T.Dict[str, CloudPath] = {}
        self.timeout = timeout
        self.blocker = asyncio.Event()

    def _get_credentials(self) -> T.Tuple[bool, T.List[CloudPath]]:
        should_loop = False
        credentials = []
        path = self.path
        self._clear_cache()
        if path.is_file():
            credentials.append(path)
        elif path.is_dir():
            should_loop = True
            credentials.extend(path.glob("*.json"))
        else:
            should_loop = True
            base = CloudPath(f"gs://{path.bucket}/")
            pattern = str(path.relative_to(base))
            credentials.extend(base.glob(pattern))
        return should_loop, credentials

    def read_credential(self, locator: CloudPath) -> Credential:
        path = locator
        self.logger.debug("Reading credentials: %s", str(path))
        try:
            with path.open() as fd:
                credential = json.load(fd)
        except json.decoder.JSONDecodeError as e:
            raise IncompleteCredentialsException(
                f"Could not parse credentials: {path}"
            ) from e
        try:
            return Credential(**credential)
        except TypeError as e:
            raise IncompleteCredentialsException(
                f"Incomplete credentials: {credential.keys()}"
            ) from e

    def write_credential(self, credential: Credential):
        self.path.mkdir(parents=True, exist_ok=True)
        path = self.path / f"{credential.username}.json"
        self.logger.info("Writing credentials: %s", str(path))
        with path.open("w+") as fd:
            json.dump(credential.asdict(), fd)

    async def _handle_credential(self, device_manager, credential_file: CloudPath):
        try:
            credential = self.read_credential(credential_file)
            username = credential.username
            if username not in self.active_usernames:
                self.logger.info(
                    "Found new credential to connect to: %s: %s: %s",
                    list(self.active_usernames.keys()),
                    username,
                    credential_file,
                )
                await asyncio.sleep(
                    10 * random.random()
                )  # avoid all bots connecting at once
                self.active_usernames[username] = credential_file
                await device_manager.on_credentials(self, credential)
        except ValueError:
            self.logger.exception(f"Could not parse credential: {credential_file}")
            return

    async def listen(self, device_manager):
        self.logger.info("CredentialsManagerFile listening to path: %s", self.path)
        should_loop = True
        async with asyncio.TaskGroup() as tg:
            while should_loop or (await self.blocker.wait()):
                self.blocker.clear()
                should_loop, credentials = self._get_credentials()
                for credential_file in credentials:
                    tg.create_task(
                        self._handle_credential(device_manager, credential_file)
                    )
                await asyncio.sleep(self.timeout)

    def mark_dead(self, username):
        self.logger.info("Marking user dead: %s", username)
        self.active_usernames.pop(username, None)
        self.blocker.set()

    def unregister(self, username):
        credential_file = self.active_usernames.pop(username)
        self.logger.info("Removing session file: %s", credential_file)
        try:
            credential_file.unlink(missing_ok=True)
        except Exception as e:
            self.logger.critical(
                "Could not remove credentials file: %s: %s", credential_file, e
            )
        self._clear_cache()

    def _clear_cache(self):
        if isinstance(self.path, CloudPath):
            self.path.clear_cache()
