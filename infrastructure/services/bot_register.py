from os import path

from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import serviceaccount, cloudrunv2, storage, secretmanager

from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from network import vpc, private_services_network_with_db
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from service import Service, ServiceArgs
from storage import sessions_bucket

from .whatupcore2 import whatupcore2_service
from .bot_archive import whatupy_control_groups

service_name = "bot-register"

service_account = serviceaccount.Account(
    "bot-register",
    account_id=f"whatup-bot-reg-{get_stack()}",
    description=f"Service account for {service_name}",
)

# registerbot needs to be able to write new session files
sessions_bucket_perm = storage.BucketIAMMember(
    "bot-reg-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "bot-reg-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["user"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_usr_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["user"].name,
        version="latest",
    )
)

bot_register = Service(
    service_name,
    ServiceArgs(
        app_path=path.join("..", "whatupy"),
        args=["/usr/src/whatupy/gcsfuse_run.sh", "registerbot"],
        concurrency=50,
        container_port=None,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image_name="whatupy",
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
                name="BUCKET_MNT_DIR_PREFIX",
                value="/usr/src/whatupy-data",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_usr_secret_source,
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
                value=whatupcore2_service.get_host(),
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="SESSIONS_USER_SUBDIR",
                value="users",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="ONBOARD_BOT",
                value="gertrude2",
            ),
            # Create an implicit dependency on the migrations
            # job completing successfully.
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MIGRATIONS_JOB_COMPLETE",
                value=migrations_job_complete.apply(lambda b: f"{b}"),
            ),
        ],
    ),
    opts=ResourceOptions(depends_on=sessions_bucket_perm),
)
