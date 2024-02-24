from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import kms, secretmanager, serviceaccount, storage
from pulumi_google_native import compute

from artifact_registry import whatupy_image
from config import control_groups, is_prod_stack
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network_with_db
from storage import media_bucket, sessions_bucket
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
    ContainerSecurityContext,
    SharedCoreMachineType,
)

from .whatupcore2 import ssl_cert_pem_secret, whatupcore2_service

service_name = "bot-db"

service_account = serviceaccount.Account(
    "bot-db",
    account_id=f"whatup-bot-db-vm-{get_stack()}",
    description=f"Service account for {service_name}",
)

# whatupy only needs read-only access to the sessions bucket
# objects.
sessions_bucket_perm = storage.BucketIAMMember(
    "bot-db-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

media_bucket_perm = storage.BucketIAMMember(
    "bot-db-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "bot-db-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["messages"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

encryption_key_perm = kms.CryptoKeyIAMMember(
    "bot-db-enc-key-perm",
    kms.CryptoKeyIAMMemberArgs(
        crypto_key_id=sessions_encryption_key.id,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudkms.cryptoKeyEncrypterDecrypter",
    ),
)

ssl_cert_pem_secret_perm = secretmanager.SecretIamMember(
    "bot-db-ssl-cert-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_cert_pem_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

machine_type = SharedCoreMachineType.E2Medium
if not is_prod_stack():
    machine_type = SharedCoreMachineType.E2Micro

bot_db = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        container_spec=Container(
            args=["/usr/src/whatupy/run.sh", "databasebot"],
            image=whatupy_image.repo_digest,
            env=[
                ContainerEnv(
                    name="KEK_URI",
                    value=sessions_encryption_key_uri,
                ),
                ContainerEnv(
                    name="SESSIONS_BUCKET",
                    value=sessions_bucket.name,
                ),
                ContainerEnv(
                    name="MEDIA_BUCKET",
                    value=media_bucket.name,
                ),
                ContainerEnv(
                    name="WHATUPY_CONTROL_GROUPS",
                    value=" ".join(control_groups),
                ),
                ContainerEnv(
                    name="WHATUPCORE2_HOST",
                    value=whatupcore2_service.get_host(),
                ),
                # Create an implicit dependency on the migrations
                # job completing successfully.
                ContainerEnv(
                    name="MIGRATIONS_JOB_COMPLETE",
                    value=migrations_job_complete.apply(lambda b: f"{b}"),
                ),
            ],
            tty=False,
            securityContext=ContainerSecurityContext(privileged=False),
        ),
        machine_type=machine_type,
        restart_policy="Always",
        secret_env=[
            compute.v1.MetadataItemsItemArgs(
                key="SSL_CERT_PEM",
                value=Output.concat(
                    ssl_cert_pem_secret.id, "/versions/latest"
                ),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="DATABASE_URL",
                value=Output.concat(
                    db_url_secrets["users"].id, "/versions/latest"
                ),
            ),
        ],
        service_account_email=service_account.email,
        subnet=private_services_network_with_db.self_link,
    ),
    opts=ResourceOptions(
        depends_on=[
            sessions_bucket_perm,
            media_bucket_perm,
            encryption_key_perm,
            ssl_cert_pem_secret_perm,
        ]
    ),
)
