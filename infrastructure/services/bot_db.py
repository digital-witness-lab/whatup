from os import path

from pulumi import ResourceOptions
from pulumi_gcp import serviceaccount, cloudrunv2, storage, secretmanager

from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from ..network import vpc, private_services_network_with_db
from ..secrets import messages_db_url_secret
from ..service import Service, ServiceArgs
from ..storage import sessions_bucket

from .whatupcore2 import whatupcore2
from .bot_archive import whatupy_control_groups

service_name = "whatupy_bot_db"

service_account = serviceaccount.Account(
    "botDbServiceAccount",
    description=f"Service account for {service_name}",
)

# whatupy only needs read-only access to the sessions bucket
# objects.
sessions_bucket_perm = storage.BucketIAMMember(
    "botDbSessionsAccess",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=f"serviceAccount:{service_account.email}",
        role="roles/storage.objectViewer",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "botDbSecretManagerAccess",
    secretmanager.SecretIamMemberArgs(
        secret_id=messages_db_url_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=f"serviceAccount:{service_account.email}",
    ),
)

db_url_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=messages_db_url_secret.name,
        version="latest",
    )
)

bot_db = Service(
    service_name,
    ServiceArgs(
        app_path=path.join("..", "..", "whatupy"),
        args=[
            "/usr/src/whatupy/gcsfuse_run.sh",
            "databasebot",
            "--host",
            "$WHATUPCORE2_HOST",
            "--database-url",
            "$DATABASE_URL",
            "$BUCKET_MNT_DIR_PREFIX/$SESSIONS_BUCKET_MNT_DIR",
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
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="BUCKET_MNT_DIR_PREFIX",
                value="/usr/src/whatupy-data",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET",
                value=sessions_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET_MNT_DIR",
                value="sessions/",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPY_CONTROL_GROUPS",
                value=whatupy_control_groups,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_HOST",
                value=whatupcore2.service.uri,
            ),
        ],
    ),
    opts=ResourceOptions(depends_on=sessions_bucket_perm),
)
