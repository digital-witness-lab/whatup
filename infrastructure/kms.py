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
