from os import path

from pulumi import ResourceOptions
from pulumi_gcp import serviceaccount, cloudrunv2, storage

from ..config import create_load_archive_job
from ..job import JobArgs, Job
from ..network import vpc, private_services_network
from ..storage import message_archive_bucket

service_name = "whatupy_bot_db_load_archive"

service_account = serviceaccount.Account(
    "whatupDbLoadArchive",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "botDbLoadArchiveAccess",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=f"serviceAccount:{service_account.email}",
        role="roles/storage.objectViewer",
    ),
)

if create_load_archive_job:
    bot_onboard_bulk_job = Job(
        service_name,
        JobArgs(
            app_path=path.join("..", "..", "whatupy"),
            commands=[
                "onboard-bulk",
                "--host",
                "$WHATUPCORE2_HOST",
                "--credentials-dir",
                "/usr/src/whatupy-data/sessions/",
            ],
            concurrency=50,
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
                network=vpc.id, subnetwork=private_services_network.id
            ),
            envs=[
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="SESSIONS_BUCKET",
                    value=message_archive_bucket.name,
                ),
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="POSTGRES_DATABASE",
                    value="messages",
                ),
            ],
            timeout="3600s",
        ),
        opts=ResourceOptions(depends_on=message_archive_bucket_perm),
    )
