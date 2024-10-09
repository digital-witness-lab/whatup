from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import kms, secretmanager, serviceaccount, storage
from pulumi_google_native import compute

from artifact_registry import whatupy_image
from config import control_groups
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
)
from jobs.db_migrations import migrations_job_complete
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network
from storage import message_archive_bucket, sessions_bucket

from .whatupcore2 import whatupcore_tls_cert, whatupcore2_service

service_name = "bot-archive"

service_account = serviceaccount.Account(
    "bot-archive",
    account_id=f"bot-archive-vm-{get_stack()}",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "bot-archive-msgarch-perm",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

# whatupy only needs read-only access to the sessions bucket
# objects.
sessions_bucket_perm = storage.BucketIAMMember(
    "bot-archive-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

encryption_key_perm = kms.CryptoKeyIAMMember(
    "bot-archive-enc-key-perm",
    kms.CryptoKeyIAMMemberArgs(
        crypto_key_id=sessions_encryption_key.id,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudkms.cryptoKeyEncrypterDecrypter",
    ),
)

tls_cert_pem_secret_perm = secretmanager.SecretIamMember(
    "bot-archive-tls-cert-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatupcore_tls_cert.cert_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

bot_archive = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        container_spec=Container(
            args=["/usr/src/whatupy/run.sh", "archivebot"],
            image=whatupy_image.repo_digest,
            env=[
                ContainerEnv(
                    name="BUCKET_MNT_DIR_PREFIX",
                    value="/usr/src/whatupy-data",
                ),
                ContainerEnv(
                    name="KEK_URI",
                    value=sessions_encryption_key_uri,
                ),
                ContainerEnv(
                    name="MESSAGE_ARCHIVE_BUCKET",
                    value=message_archive_bucket.name,
                ),
                ContainerEnv(
                    name="MESSAGE_ARCHIVE_BUCKET_MNT_DIR",
                    value="message-archive/",
                ),
                ContainerEnv(
                    name="SESSIONS_BUCKET",
                    value=sessions_bucket.name,
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
                ContainerEnv(
                    name="RAND_STRING",  # change rand string to force deploy
                    value="34932948073298",
                ),
            ],
        ),
        secret_env=[
            compute.v1.MetadataItemsItemArgs(
                key="WHATUP_CERT_PEM",
                value=Output.concat(
                    whatupcore_tls_cert.cert_secret.id, "/versions/latest"
                ),
            ),
        ],
        service_account_email=service_account.email,
        subnet=private_services_network.self_link,
    ),
    opts=ResourceOptions(
        depends_on=[
            message_archive_bucket_perm,
            sessions_bucket_perm,
            encryption_key_perm,
        ]
    ),
)
