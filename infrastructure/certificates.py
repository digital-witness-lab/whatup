import pulumi_tls as tls
from pulumi import get_stack

from .services.whatupcore2 import whatupcore2_service


ssl_private_key = tls.PrivateKey(
    f"whatup-ssl-pk-{get_stack()}", algorithm="ED25519"
)

ssl_cert = tls.SelfSignedCert(
    f"whatup-ssl-cert-{get_stack()}",
    private_key_pem=ssl_private_key.private_key_pem,
    validity_period_hours=24 * 365,  # 1 year
    early_renewal_hours=24 * 7 * 4 * 2,  # 2 months
    is_ca_certificate=True,
    allowed_uses=[
        "any_extended",
        "cert_signing",
        "client_auth",
        "server_auth",
        "key_encipherment",
        "ocsp_signing",
        "crl_signing",
        "code_signing",
    ],
    ip_addresses=[whatupcore2_service.get_host_output()],
)
