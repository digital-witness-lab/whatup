import re
from dataclasses import asdict, dataclass, field
from typing import List, Any, Dict, Optional


class IncompleteCredentialsException(ValueError):
    pass


@dataclass
class Credential:
    username: str
    passphrase: str
    meta: Optional[Dict[str, Any]] = field(default=None)

    def asdict(self):
        return asdict(self)


class CredentialsManager:
    url_pattern: List[str]
    _registry: List = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry.append(cls)

    def __init__(self, paths: List[str], **kwargs):
        pass

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
