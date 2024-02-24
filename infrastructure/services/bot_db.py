from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, kms, secretmanager, serviceaccount, storage
from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from artifact_registry import whatupy_image
from config import control_groups
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network_with_db, vpc
from service import Service, ServiceArgs
from storage import media_bucket, sessions_bucket

from .whatupcore2 import ssl_cert_pem_b64_secret, whatupcore2_service

service_name = "bot-db"

service_account = serviceaccount.Account(
    "bot-db",
    account_id=f"whatup-bot-db-{get_stack()}",
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

db_url_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["messages"].name,
        version="latest",
    )
)

ssl_cert_pem_b64_secret_perm = secretmanager.SecretIamMember(
    "bot-db-ssl-cert-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_cert_pem_b64_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)
ssl_cert_pem_b64_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=ssl_cert_pem_b64_secret.name,
        version="latest",
    ),
)

bot_db = Service(
    service_name,
    ServiceArgs(
        args=["/usr/src/whatupy/run.sh", "databasebot"],
        concurrency=50,
        container_port=None,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=whatupy_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        public_access=True,
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="KEK_URI",
                value=sessions_encryption_key_uri,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET",
                value=sessions_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MEDIA_BUCKET",
                value=media_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPY_CONTROL_GROUPS",
                value=" ".join(control_groups),
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_HOST",
                value=whatupcore2_service.get_host(),
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SSL_CERT_PEM_B64",
                value_source=ssl_cert_pem_b64_source,
            ),
            # Create an implicit dependency on the migrations
            # job completing successfully.
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MIGRATIONS_JOB_COMPLETE",
                value=migrations_job_complete.apply(lambda b: f"{b}"),
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[
            sessions_bucket_perm,
            media_bucket_perm,
            encryption_key_perm,
        ]
    ),
)
