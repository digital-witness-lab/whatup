from os import path

from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import cloudrunv2, kms, serviceaccount, storage

from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import vpc, private_services_network
from service import Service, ServiceArgs
from storage import sessions_bucket, message_archive_bucket
from artifact_registry import whatupy_image

from .whatupcore2 import whatupcore2_service

service_name = "bot-archive"
# cool friends + micha
whatupy_control_groups = "120363104970691776@g.us anon.NlUiJWkTKZtZ7jgGVob9Loe4vkHphhoBJJQ-T-Niuuk.v001@s.whatsapp.net"  # noqa: E501

service_account = serviceaccount.Account(
    "bot-archive",
    account_id=f"bot-archive-{get_stack()}",
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

whatupy = Service(
    service_name,
    ServiceArgs(
        args=["archivebot"],
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
            network=vpc.id, subnetwork=private_services_network.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="BUCKET_MNT_DIR_PREFIX",
                value="/usr/src/whatupy-data",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="KEK_URI",
                value=sessions_encryption_key_uri,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MESSAGE_ARCHIVE_BUCKET",
                value=message_archive_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MESSAGE_ARCHIVE_BUCKET_MNT_DIR",
                value="message-archive/",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET",
                value=sessions_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPY_CONTROL_GROUPS",
                value=whatupy_control_groups,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_HOST",
                value=whatupcore2_service.get_host(),
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[
            message_archive_bucket_perm,
            sessions_bucket_perm,
            encryption_key_perm,
        ]
    ),
)
