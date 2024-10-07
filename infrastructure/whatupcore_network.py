from dataclasses import dataclass
import base64

import pulumi_gcp.compute
from pulumi_gcp import secretmanager
import pulumi_tls as tls
from pulumi import get_stack
from pulumi_google_native import compute

from config import location
from dwl_secrets import create_secret
from network import private_services_network, private_services_network_with_db
from network_firewall import firewall_policy

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

photocop_static_private_ip = compute.v1.Address(
    "photocop-private-ip",
    args=compute.v1.AddressArgs(
        region=location,
        ip_version=compute.v1.AddressIpVersion.IPV4,
        subnetwork=private_services_network_with_db.self_link,
        purpose=compute.v1.AddressPurpose.GCE_ENDPOINT,
        address_type=compute.v1.AddressAddressType.INTERNAL,
    ),
)


@dataclass
class TLSKeysSecret:
    key_secret: secretmanager.Secret
    cert_secret: secretmanager.Secret
    cert_b64_secret: secretmanager.Secret


def create_tls_keys(
    service: str, ip_address: compute.v1.Address
) -> TLSKeysSecret:
    # We can't use ED25519 because GRPC needs to be build from sorce with
    # GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 for this to work.
    tls_private_key = tls.PrivateKey(
        f"{service}-tls-pk-{get_stack()}", algorithm="RSA", rsa_bits=4096
    )

    tls_cert = tls.SelfSignedCert(
        f"{service}-tls-cert-{get_stack()}",
        private_key_pem=tls_private_key.private_key_pem,
        validity_period_hours=24 * 365,  # 1 year
        early_renewal_hours=24 * 7 * 4 * 2,  # 2 months
        is_ca_certificate=True,
        subject=tls.SelfSignedCertSubjectArgs(
            country="US",
            province="NY",
            locality="NY",
            organization="Digital Witness Lab",
            organizational_unit="WhatUp",
            common_name="{service}.digitalwitnesslab.org",
        ),
        allowed_uses=[
            # uses as per https://github.com/grpc/grpc/issues/24129#issuecomment-849202691
            "key_encipherment",
            "data_encipherment",
            "digital_signature",
        ],
        ip_addresses=[ip_address.address],
    )

    key_secret = create_secret(
        f"{service}-tls-pk-pem", tls_private_key.private_key_pem
    )
    cert_secret = create_secret(f"{service}-tls-cert-pem", tls_cert.cert_pem)
    cert_b64_secret = create_secret(
        f"{service}-tls-cert-b64-pem",
        tls_cert.cert_pem.apply(
            lambda cert: base64.b64encode(cert.encode("utf8")).decode("utf8")
        ),
    )
    return TLSKeysSecret(
        key_secret, cert_secret, cert_b64_secret=cert_b64_secret
    )


whatupcore_tls_cert = create_tls_keys("whatup", whatupcore2_static_private_ip)
photocop_tls_cert = create_tls_keys("photocop", photocop_static_private_ip)


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
            dest_ip_ranges=[
                whatupcore2_static_private_ip.address,
                photocop_static_private_ip.address,
            ],
            src_ip_ranges=[
                private_services_network.ip_cidr_range,
                private_services_network_with_db.ip_cidr_range,
            ],
        ),
    ),
)

pulumi_gcp.compute.NetworkFirewallPolicyRule(
    "allow-healthprobe-whatupcore-3447",
    pulumi_gcp.compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow connection to whatupcore from GCP health probers",
        direction="INGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=11,
        rule_name="allow-3447-whatupcore-healthcheck",
        match=pulumi_gcp.compute.NetworkFirewallPolicyRuleMatchArgs(
            layer4_configs=[
                pulumi_gcp.compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="tcp", ports=["3447"]
                )
            ],
            dest_ip_ranges=[
                whatupcore2_static_private_ip.address,
                photocop_static_private_ip.address,
            ],
            src_ip_ranges=["35.191.0.0/16", "130.211.0.0/22"],
        ),
    ),
)
