import logging
import re
from typing import Any, List

from ..utils import short_hash
from .credential import Credential

logger = logging.getLogger(__name__)


class IncompleteCredentialsException(ValueError):
    pass


class CredentialsManager:
    url_pattern: List[str]
    _registry: List = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry.append(cls)

    def __init__(self, url: str, **kwargs):
        self.logger = logger.getChild(short_hash(f"{url}{id(self)}"))
        self.logger.info("Managing credentials for path: %s", url)

    @classmethod
    def from_url(cls, url, **kwargs):
        for manager in cls._registry:
            for pattern in manager.url_patterns:
                if re.match(pattern, url) is not None:
                    return manager(url, **kwargs)
        raise TypeError(f"Unrecognized credentials url: {url}")

    async def listen(self, device_manager):
        raise NotImplementedError

    def mark_dead(self, username):
        raise NotImplementedError

    def unregister(self, username):
        raise NotImplementedError

    def read_credential(self, locator: Any, **kwargs) -> Credential:
        raise NotImplementedError

    def write_credential(self, credential: Credential, **kwargs):
        raise NotImplementedError
