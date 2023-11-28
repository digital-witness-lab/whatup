import os
import logging
import json
import base64
import typing as T

from cloudpathlib import AnyPath
import tink
from tink import aead
from tink.integration import gcpkms

from . import (
    CredentialsManagerCloudPath,
    Credential,
    IncompleteCredentialsException,
)


logger = logging.getLogger(__name__)


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

        logger.debug("Managing encrypted credentials for url: %s", url)
        if url.startswith("kek+"):
            url = url[len("kek+") :]
        super().__init__(url, *args, **kwargs)

    def read_credential(self, path: AnyPath) -> Credential:
        enc_credential = super().read_credential(path)
        return self.decrypt(enc_credential)

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

    def decrypt(self, enc_credential: Credential) -> Credential:
        cipher_bytes: bytes = base64.b64decode(enc_credential.passphrase)
        env_aead = self._get_env_aead()
        passphrase_bytes = env_aead.decrypt(
            cipher_bytes, enc_credential.username.encode("utf8")
        )
        plain_credential = Credential(**enc_credential.asdict())
        plain_credential.passphrase = passphrase_bytes.decode("utf8")
        return plain_credential
