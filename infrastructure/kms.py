from pulumi import Output
from pulumi_gcp import kms

from config import location

key_ring = kms.KeyRing("sessions", location=location)

sessions_encryption_key = kms.CryptoKey(
    "sessions",
    args=kms.CryptoKeyArgs(
        key_ring=key_ring.id,
        purpose="ENCRYPT_DECRYPT",
        rotation_period="2630000s",  # every month
    ),
)

sessions_encryption_key_version = kms.CryptoKeyVersion(
    "sessions-version", crypto_key=sessions_encryption_key.id, state="ENABLED"
)

sessions_encryption_key_uri = Output.concat(
    "gcp-kms://",
    sessions_encryption_key_version.id,
)
