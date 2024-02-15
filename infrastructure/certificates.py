import pulumi_tls as tls
from pulumi import Output, get_stack

from .services.whatupcore2 import whatupcore2_service


cert_private_key = tls.PrivateKey(
    f"whatup-pk-{get_stack()}", algorithm="ED25519"
)

certificate = tls.SelfSignedCert(
    f"whatup-cert-{get_stack()}",
    private_key_pem=cert_private_key.private_key_pem,
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
    ip_address=[whatupcore2_service.get_host_output()],
)
