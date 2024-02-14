from pulumi import Output, ResourceOptions, get_stack, log
from pulumi_gcp import secretmanager, serviceaccount
from pulumi_google_native import compute

from artifact_registry import whatupcore2_image
from config import is_prod_stack
from dwl_secrets import (
    db_url_secrets,
    whatup_anon_key_secret,
    whatup_salt_secret,
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

log_level = "INFO"  # if is_prod_stack() else "DEBUG"
whatupcore2_service = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        container_spec=Container(
            command=None,
            args=["rpc", f"--log-level={log_level}"],
            image=whatupcore2_image.repo_digest,
            env=[
                ContainerEnv(
                    name="USE_SSL",
                    value="false",
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
