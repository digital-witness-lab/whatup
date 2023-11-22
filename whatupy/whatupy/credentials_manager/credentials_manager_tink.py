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
            print(kek_uri)
            self.client = gcpkms.GcpKmsClient(kek_uri, kms_credentials_path)
        except tink.TinkError as e:
            logging.exception("Error creating GCP KMS client: %s", e)
            raise

        if url.startswith("kek+"):
            url = url[len("kek+") :]
        super().__init__(url, *args, **kwargs)

    def read_credential(self, path: AnyPath) -> Credential:
        enc_credential_data = json.load(path.open())
        try:
            enc_credential = Credential(**enc_credential_data)
        except TypeError:
            raise IncompleteCredentialsException(
                f"Incomplete credentials: {credential.keys()}"
            )
        return self.decrypt(enc_credential)

    def write_credential(self, plain_credential: Credential):
        self.path.mkdir(parents=True, exist_ok=True)
        path = self.path / f"{plain_credential.username}.json"
        enc_credential = self.encrypt(plain_credential)
        with path.open("w+") as fd:
            json.dump(enc_credential.asdict(), fd)

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
        plain_credential = Credential(**plain_credential.asdict())
        plain_credential.passphrase = passphrase_bytes.decode("utf8")
        return plain_credential
