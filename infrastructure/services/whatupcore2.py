from pulumi import Output, ResourceOptions, get_stack, log
from pulumi_gcp import secretmanager, serviceaccount
from pulumi_google_native import compute

from artifact_registry import whatupcore2_image
from config import is_prod_stack
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
    SharedCoreMachineType,
)
from dwl_secrets import (
    db_url_secrets,
    whatup_anon_key_secret,
    whatup_salt_secret,
)
from network import private_services_network_with_db
from whatupcore_network import (
    ssl_cert_pem_secret,
    ssl_private_key_pem_secret,
    whatupcore2_static_private_ip,
)

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "whatupcore",
    account_id=f"whatupcore2-vm-{get_stack()}",
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

machine_type = SharedCoreMachineType.E2Medium
if not is_prod_stack():
    machine_type = SharedCoreMachineType.E2Small

log_level = "INFO" if is_prod_stack() else "DEBUG"
whatupcore2_service = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        private_address=whatupcore2_static_private_ip,
        tcp_healthcheck_port=3447,
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
        ),
        machine_type=machine_type,
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

whatupcore2_service.get_host().apply(
    lambda addr: log.info(f"whatupcore2 address: {addr}", whatupcore2_service)
)
