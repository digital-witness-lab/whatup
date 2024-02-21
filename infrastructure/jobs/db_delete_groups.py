from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, secretmanager, serviceaccount, storage
from pulumi_gcp.cloudrunv2 import (  # noqa: E501
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)

from jobs.db_migrations import migrations_job_complete
from artifact_registry import whatupy_image
from dwl_secrets import db_url_secrets
from job import Job, JobArgs
from network import private_services_network_with_db, vpc
from storage import media_bucket

service_name = "db-del-grp"

service_account = serviceaccount.Account(
    "db-del-grp",
    account_id=f"db-del-grp-{get_stack()}",
    description=f"Service account for {service_name}",
)

media_bucket_perm = storage.BucketIAMMember(
    "db-del-grp-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "db-del-grp-archive-scrt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["messages"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["messages"].name,
        version="latest",
    )
)

bot_onboard_bulk_job = Job(
    service_name,
    JobArgs(
        args=["/usr/src/whatupy/run.sh", "delete-groups"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=whatupy_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="MEDIA_BUCKET",
                value=media_bucket.name,
            ),
            # Create an implicit dependency on the migrations
            # job completing successfully.
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="MIGRATIONS_JOB_COMPLETE",
                value=migrations_job_complete.apply(lambda b: f"{b}"),
            ),
        ],
        timeout="3600s",
    ),
    opts=ResourceOptions(depends_on=[media_bucket_perm, secret_manager_perm]),
)
