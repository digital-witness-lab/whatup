import base64
import logging
import os
import typing as T
from dataclasses import dataclass, field

import tink
from cloudpathlib import AnyPath
from tink import aead
from tink.integration import gcpkms

from . import Credential, CredentialsManagerCloudPath

logger = logging.getLogger(__name__)


@dataclass
class LazyDecryptedCredential:
    username: str
    passphrase_cipher: str
    decrypt_func: T.Callable[[str, str], str]
    meta: T.Optional[T.Dict[str, T.Any]] = field(default=None)

    @property
    def passphrase(self):
        logger.getChild(self.username).debug("Lazy decrypting credentials")
        return self.decrypt_func(self.username, self.passphrase_cipher)

    @classmethod
    def from_credential(cls, **kwargs):
        kwargs["passphrase_cipher"] = kwargs.pop("passphrase")
        return cls(**kwargs)

    def asdict(self):
        return {
            "username": self.username,
            "passphrase": self.passphrase_cipher,
            "meta": self.meta,
        }


class CredentialsManagerTink(CredentialsManagerCloudPath):
    url_patterns = [
        r"^kek+",  # google cloud storage
    ]

    def __init__(
        self,
        url: str,
        *args,
        kek_uri: T.Optional[str] = None,
        kms_credentials_path: T.Optional[str] = None,
        **kwargs,
    ):
        super().__init__(url, *args, **kwargs)
        if kek_uri is None:
            kek_uri = os.environ.get("KEK_URI")
            if kek_uri is None:
                raise EnvironmentError("Need kek_uri parameter or KEK_URI ENVVAR")
        self.kek_uri = kek_uri

        aead.register()
        try:
            self.client = gcpkms.GcpKmsClient(kek_uri, kms_credentials_path)
        except tink.TinkError as e:
            logging.exception("Error creating GCP KMS client: %s", e)
            raise

        self.logger.debug("Managing encrypted credentials for url: %s", url)
        if url.startswith("kek+"):
            url = url[len("kek+") :]

    def read_credential(self, path: AnyPath) -> LazyDecryptedCredential:
        enc_credential: Credential = super().read_credential(path)
        lazy_plaintext_credential = LazyDecryptedCredential.from_credential(
            decrypt_func=self.decrypt_str,
            **enc_credential.asdict(),
        )
        self.logger.debug(
            "Read and made lazy decryptable credentials: %s",
            lazy_plaintext_credential.username,
        )
        return lazy_plaintext_credential

    def write_credential(self, plain_credential: Credential):
        enc_credential = self.encrypt(plain_credential)
        super().write_credential(enc_credential)

    def _get_env_aead(self) -> aead.KmsEnvelopeAead:
        try:
            remote_aead = self.client.get_aead(self.kek_uri)
            return aead.KmsEnvelopeAead(aead.aead_key_templates.AES256_GCM, remote_aead)
        except tink.TinkError as e:
            logging.exception("Error creating primitive: %s", e)
            raise

    def encrypt(self, plain_credential: Credential) -> Credential:
        env_aead = self._get_env_aead()
        cipher = env_aead.encrypt(
            plain_credential.passphrase.encode("utf8"),
            plain_credential.username.encode("utf8"),
        )
        enc_credential = Credential(**plain_credential.asdict())
        enc_credential.passphrase = base64.b64encode(cipher).decode("utf8")
        return enc_credential

    def decrypt_str(self, username: str, cipher: str) -> str:
        cipher_bytes: bytes = base64.b64decode(cipher)
        env_aead = self._get_env_aead()
        passphrase_bytes = env_aead.decrypt(cipher_bytes, username.encode("utf8"))
        return passphrase_bytes.decode("utf8")
