from pulumi import Output, ResourceOptions
from pulumi_gcp import kms, projects

from config import location


cloudkms_service = projects.Service(
    "cloudkms.googleapis.com",
    disable_dependent_services=True,
    service="cloudkms.googleapis.com",
)

key_ring = kms.KeyRing(
    "sessions",
    location=location,
    opts=ResourceOptions(depends_on=[cloudkms_service]),
)

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
    sessions_encryption_key.id,
)
