import base64

from pulumi import get_stack
import pulumi_gcp.compute
from pulumi_google_native import compute
import pulumi_tls as tls

from network_firewall import firewall_policy
from dwl_secrets import create_secret
from config import location
from network import (
    private_services_network,
    private_services_network_with_db,
)


whatupcore2_static_private_ip = compute.v1.Address(
    "whatupcore2-private-ip",
    args=compute.v1.AddressArgs(
        region=location,
        ip_version=compute.v1.AddressIpVersion.IPV4,
        subnetwork=private_services_network_with_db.self_link,
        purpose=compute.v1.AddressPurpose.GCE_ENDPOINT,
        address_type=compute.v1.AddressAddressType.INTERNAL,
    ),
)

# We can't use ED25519 because GRPC needs to be build from sorce with
# GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 for this to work.
ssl_private_key = tls.PrivateKey(
    f"whatup-ssl-pk-{get_stack()}", algorithm="RSA", rsa_bits=4096
)

ssl_cert = tls.SelfSignedCert(
    f"whatup-ssl-cert-{get_stack()}",
    private_key_pem=ssl_private_key.private_key_pem,
    validity_period_hours=24 * 365,  # 1 year
    early_renewal_hours=24 * 7 * 4 * 2,  # 2 months
    is_ca_certificate=True,
    subject=tls.SelfSignedCertSubjectArgs(
        country="US",
        province="NY",
        locality="NY",
        organization="Digital Witness Lab",
        organizational_unit="WhatUp",
        common_name="whatup.digitalwitnesslab.org",
    ),
    allowed_uses=[
        # uses as per https://github.com/grpc/grpc/issues/24129#issuecomment-849202691
        "key_encipherment",
        "data_encipherment",
        "digital_signature",
    ],
    ip_addresses=[whatupcore2_static_private_ip.address],
)

ssl_private_key_pem_secret = create_secret(
    "whatup-ssl-pk-pem", ssl_private_key.private_key_pem
)
ssl_cert_pem_secret = create_secret("whatup-ssl-cert-pem", ssl_cert.cert_pem)
ssl_cert_pem_b64_secret = create_secret(
    "whatup-ssl-cert-pem-b64",
    ssl_cert.cert_pem.apply(
        lambda cert: base64.b64encode(cert.encode("utf8")).decode("utf8")
    ),
)


pulumi_gcp.compute.NetworkFirewallPolicyRule(
    "allow-3447-to-whatupcore",
    pulumi_gcp.compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow connection to whatupcore from internal network",
        direction="INGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=10,
        rule_name="allow-3447-whatupcore",
        match=pulumi_gcp.compute.NetworkFirewallPolicyRuleMatchArgs(
            layer4_configs=[
                pulumi_gcp.compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="tcp", ports=["3447"]
                )
            ],
            dest_ip_ranges=[whatupcore2_static_private_ip.address],
            src_ip_ranges=[
                private_services_network.ip_cidr_range,
                private_services_network_with_db.ip_cidr_range,
            ],
        ),
    ),
)
