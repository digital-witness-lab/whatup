from os import path

from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import cloudrunv2, kms, secretmanager, serviceaccount, storage
from pulumi_gcp.cloudrunv2 import (
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from config import create_load_archive_job
from dwl_secrets import db_url_secrets
from job import JobArgs, Job
from jobs.db_migrations import migrations_job_complete
from network import vpc, private_services_network_with_db
from storage import message_archive_bucket, media_bucket
from artifact_registry import whatupy_image

service_name = "bot-db-load-archive"

service_account = serviceaccount.Account(
    "db-load-archive",
    account_id=f"bot-db-load-archive-{get_stack()}",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "db-ld-archive-arch-perm",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

media_bucket_perm = storage.BucketIAMMember(
    "db-ld-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "db-ld-archive-scrt-perm",
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

if create_load_archive_job:
    db_migrations_job = Job(
        service_name,
        JobArgs(
            args=["/usr/src/whatupy/run.sh", "load-archive"],
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
                    name="MESSAGE_ARCHIVE_BUCKET",
                    value=message_archive_bucket.name,
                ),
                cloudrunv2.ServiceTemplateContainerEnvArgs(
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
        opts=ResourceOptions(
            depends_on=[
                message_archive_bucket_perm,
                media_bucket_perm,
                secret_manager_perm,
            ]
        ),
    )
