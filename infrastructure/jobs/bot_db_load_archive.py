from os import path

from pulumi import ResourceOptions, Output
from pulumi_gcp import serviceaccount, cloudrunv2, storage, secretmanager
from pulumi_gcp.cloudrunv2 import (
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from config import create_load_archive_job
from dwl_secrets import messages_db_url_secret
from job import JobArgs, Job
from network import vpc, private_services_network_with_db
from storage import message_archive_bucket

service_name = "whatupy-bot-db-load-archive"

service_account = serviceaccount.Account(
    "whatupDbLoadArchive",
    account_id="whatupy-bot-db-load-archive",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "botDbLoadArchiveAccess",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "dbLoadArchiveJobSecretsAccess",
    secretmanager.SecretIamMemberArgs(
        secret_id=messages_db_url_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=messages_db_url_secret.name,
        version="latest",
    )
)

if create_load_archive_job:
    db_migrations_job = Job(
        service_name,
        JobArgs(
            app_path=path.join("..", "whatupy"),
            args=["/usr/src/whatupy/db_load_archive_job.sh"],
            concurrency=1,
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
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="MESSAGE_ARCHIVE_BUCKET_MNT_DIR",
                    value="message-archive/",
                ),
            ],
            timeout="3600s",
        ),
        opts=ResourceOptions(
            depends_on=[message_archive_bucket_perm, secret_manager_perm]
        ),
    )
