from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Dict


@dataclass
class Credential:
    username: str
    passphrase: str
    meta: Optional[Dict[str, Any]] = field(default=None)

    def asdict(self):
        return asdict(self)
