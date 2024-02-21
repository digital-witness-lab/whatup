from pulumi import Output, ResourceOptions, get_stack, log
from pulumi_gcp import secretmanager, serviceaccount
from pulumi_google_native import compute

import pulumi_tls as tls

from artifact_registry import whatupcore2_image
from config import is_prod_stack, location
from dwl_secrets import (
    db_url_secrets,
    whatup_anon_key_secret,
    whatup_salt_secret,
    create_secret,
)
from network import private_services_network_with_db
from container_vm import (
    ContainerOnVm,
    ContainerOnVmArgs,
    Container,
    ContainerEnv,
    SharedCoreMachineType,
    ContainerSecurityContext,
)

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "whatupcore",
    account_id=f"whatupcore-{get_stack()}",
    description=f"Service account for {service_name}",
)

db_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["whatupcore"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

salt_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-salt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_salt_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

anon_key_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-anon-key-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_anon_key_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

static_private_ip = compute.v1.Address(
    f"{service_name}-private-ip",
    args=compute.v1.AddressArgs(
        region=location,
        ip_version=compute.v1.AddressIpVersion.IPV4,
        subnetwork=private_services_network_with_db.self_link,
        purpose=compute.v1.AddressPurpose.GCE_ENDPOINT,
        address_type=compute.v1.AddressAddressType.INTERNAL,
    ),
)

ssl_private_key = tls.PrivateKey(
    f"whatup-ssl-pk-{get_stack()}", algorithm="ED25519"
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
        "any_extended",
        "cert_signing",
        "client_auth",
        "server_auth",
        "key_encipherment",
        "ocsp_signing",
        "crl_signing",
        "code_signing",
    ],
    ip_addresses=[static_private_ip.address],
)

ssl_private_key_pem_secret = create_secret(
    "whatup-ssl-pk-pem", ssl_private_key.private_key_pem
)
ssl_cert_pem_secret = create_secret("whatup-ssl-cert-pem", ssl_cert.cert_pem)

ssl_private_key_pem_perm = secretmanager.SecretIamMember(
    "whatupcore-ssl-pk-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_private_key_pem_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

ssl_cert_pem_perm = secretmanager.SecretIamMember(
    "whatupcore-ssl-cert-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_cert_pem_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

log_level = "INFO"  # if is_prod_stack() else "DEBUG"
whatupcore2_service = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        private_address=static_private_ip,
        container_spec=Container(
            command=None,
            args=["rpc", f"--log-level={log_level}"],
            image=whatupcore2_image.repo_digest,
            env=[
                ContainerEnv(
                    name="USE_SSL",
                    value="true",
                ),
                ContainerEnv(
                    name="APP_NAME_SUFFIX",
                    value="" if is_prod_stack() else get_stack(),
                ),
                ContainerEnv(
                    name="RAND_STRING",  # change rand string to force deploy
                    value="34943534473298",
                ),
            ],
            tty=False,
            securityContext=ContainerSecurityContext(privileged=False),
        ),
        machine_type=SharedCoreMachineType.E2Small,
        restart_policy="Always",
        secret_env=[
            compute.v1.MetadataItemsItemArgs(
                key="DATABASE_URL",
                value=Output.concat(
                    db_url_secrets["whatupcore"].id, "/versions/latest"
                ),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="ENC_KEY_SALT",
                value=Output.concat(whatup_salt_secret.id, "/versions/latest"),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="ANON_KEY",
                value=Output.concat(
                    whatup_anon_key_secret.id, "/versions/latest"
                ),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="SSL_CERT_PEM",
                value=Output.concat(
                    ssl_cert_pem_secret.id, "/versions/latest"
                ),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="SSL_PRIV_KEY_PEM",
                value=Output.concat(
                    ssl_private_key_pem_secret.id, "/versions/latest"
                ),
            ),
        ],
        service_account_email=service_account.email,
        subnet=private_services_network_with_db.self_link,
    ),
    opts=ResourceOptions(
        depends_on=[
            db_secret_manager_perm,
            salt_secret_manager_perm,
        ]
    ),
)

whatupcore2_service.get_host_output().apply(
    lambda addr: log.info(f"whatupcore2 address: {addr}", whatupcore2_service)
)
