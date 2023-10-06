from os import path

from pulumi import ResourceOptions
from pulumi_gcp import serviceaccount, cloudrunv2, storage

from ..service import Service, ServiceArgs
from ..network import vpc, private_services_network
from ..storage import sessions_bucket, message_archive_bucket

from .whatupcore2 import whatupcore2

service_name = "whatupy_bot_archive"
# cool friends + micha
whatupy_control_groups = "120363104970691776@g.us anon.NlUiJWkTKZtZ7jgGVob9Loe4vkHphhoBJJQ-T-Niuuk.v001@s.whatsapp.net"  # noqa: E501

service_account = serviceaccount.Account(
    "botArchiveServiceAccount",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "botArchiveMessageArchiveAccess",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=f"serviceAccount:{service_account.email}",
        role="roles/storage.objectAdmin",
    ),
)

# whatupy only needs read-only access to the sessions bucket
# objects.
sessions_bucket_perm = storage.BucketIAMMember(
    "botArchiveSessionsAccess",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=f"serviceAccount:{service_account.email}",
        role="roles/storage.objectViewer",
    ),
)

whatupy = Service(
    service_name,
    ServiceArgs(
        app_path=path.join("..", "..", "whatupy"),
        commands=[
            "archivebot",
            "--host",
            "$WHATUPCORE2_HOST",
            "--archive-dir",
            "/usr/src/whatupy-data/message-archive/",
            "/usr/src/whatupy-data/sessions/",
        ],
        concurrency=50,
        container_port=3447,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image_name=service_name,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPY_CONTROL_GROUPS",
                value=whatupy_control_groups,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET",
                value=sessions_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MESSAGE_ARCHIVE_BUCKET",
                value=message_archive_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_HOST",
                value=whatupcore2.service.uri,
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[message_archive_bucket_perm, sessions_bucket_perm]
    ),
)
