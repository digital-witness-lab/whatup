from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import cloudrunv2, serviceaccount, secretmanager, storage
from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from job import JobArgs, Job
from network import vpc, private_services_network_with_db
from storage import whatupcore2_bucket
from artifact_registry import whatupcore2_image

from dwl_secrets import db_url_secrets, whatup_salt_secret

service_name = "whatupcore-remove-user"

service_account = serviceaccount.Account(
    "remove-user",
    account_id=f"whatupcore-rmuser-{get_stack()}",
    description=f"Service account for {service_name}",
)

bucket_perm = storage.BucketIAMMember(
    "wu-rmu-core-strg-perm",
    storage.BucketIAMMemberArgs(
        bucket=whatupcore2_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

salt_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-rmu-salt-perm",
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

db_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-rmuser-secret-perm",
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

whatupcore2_rmuser_job = Job(
    service_name,
    JobArgs(
        args=["/gcsfuse_run.sh", "remove-user"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="PRIVATE_RANGES_ONLY",
        image=whatupcore2_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        memory="1Gi",
        service_account=service_account,
        envs=[
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
                name="ENC_KEY_SALT",
                value_source=whatup_salt_secret_source,
            ),
        ],
        timeout="3600s",
    ),
    opts=ResourceOptions(
        depends_on=[
            bucket_perm,
            salt_secret_manager_perm,
            db_secret_manager_perm,
        ],
    ),
)
