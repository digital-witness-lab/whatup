
from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import kms, secretmanager, serviceaccount, storage
from pulumi_google_native import compute

from artifact_registry import whatupy_image
from config import control_groups, primary_bot_name
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
)
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network
from storage import sessions_bucket, temp_bucket

from .whatupcore2 import ssl_cert_pem_secret, whatupcore2_service

service_name = "bot-chat"

service_account = serviceaccount.Account(
    "bot-chat",
    account_id=f"bot-chat-vm-{get_stack()}",
    description=f"Service account for {service_name}",
)

sessions_bucket_perm = storage.BucketIAMMember(
    "bot-chat-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)
encryption_key_perm = kms.CryptoKeyIAMMember(
    "bot-chat-enc-key-perm",
    kms.CryptoKeyIAMMemberArgs(
        crypto_key_id=sessions_encryption_key.id,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudkms.cryptoKeyEncrypterDecrypter",
    ),
)

ssl_cert_pem_secret_perm = secretmanager.SecretIamMember(
    "bot-chat-ssl-cert-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_cert_pem_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

bot_chat = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        container_spec=Container(
            args=["/usr/src/whatupy/run.sh", "chat"],
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
                key="SSL_CERT_PEM",
                value=Output.concat(
                    ssl_cert_pem_secret.id, "/versions/latest"
                ),
            ),
        ],
        service_account_email=service_account.email,
        subnet=private_services_network.self_link,
    ),
    opts=ResourceOptions(
        depends_on=[
            sessions_bucket_perm,
            encryption_key_perm,
            ssl_cert_pem_secret_perm,
        ]
    ),
)
