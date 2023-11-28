from os import path

from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import serviceaccount, cloudrunv2, storage, secretmanager
from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from service import Service, ServiceArgs
from network import vpc, private_services_network_with_db
from dwl_secrets import db_url_secrets, whatup_salt_secret
from storage import whatupcore2_bucket
from config import is_prod_stack, whatup_salt
from artifact_registry import whatupcore2_image

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "whatupcore",
    account_id=f"whatupcore-{get_stack()}",
    description=f"Service account for {service_name}",
)

bucket_perm = storage.BucketIAMMember(
    "wu-core-strg-perm",
    storage.BucketIAMMemberArgs(
        bucket=whatupcore2_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

db_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["whatupcore"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["whatupcore"].name,
        version="latest",
    )
)

salt_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-salt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_salt_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

whatup_salt_secret_source = (
    cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
        secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
            secret=whatup_salt_secret.name,
            version="latest",
        )
    )
)

whatupcore2_service = Service(
    service_name,
    ServiceArgs(
        args=["/gcsfuse_run.sh", "rpc", "--log-level=DEBUG"],
        concurrency=50,
        container_port=3447,
        cpu="1",
        # Route only egress traffic bound for private IPs
        # via the VPC network. All other traffic will take
        # the default route bound for the internet gateway.
        # Routing all traffic via the VPC for this container
        # will cause the websocket connection to WhatsApp to
        # fail due to dial timeout.
        egress="PRIVATE_RANGES_ONLY",
        image=whatupcore2_image,
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
                name="USE_SSL",
                value="false",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_BUCKET",
                value=whatupcore2_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_BUCKET_MNT_DIR",
                value="/db/",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="APP_NAME_SUFFIX",
                value="" if is_prod_stack() else get_stack(),
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="ENC_KEY_SALT",
                value_source=whatup_salt_secret_source,
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[
            bucket_perm,
            db_secret_manager_perm,
            salt_secret_manager_perm,
        ]
    ),
)
