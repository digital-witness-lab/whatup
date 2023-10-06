from os import path

from pulumi import ResourceOptions
from pulumi_gcp import serviceaccount, cloudrunv2, storage

from ..config import create_onboard_bulk_job
from ..job import JobArgs, Job
from ..network import vpc, private_services_network
from ..storage import sessions_bucket

service_name = "whatupy_bot_onboard_bulk"

service_account = serviceaccount.Account(
    "whatupOnboardBulk",
    description=f"Service account for {service_name}",
)

sessions_bucket_perm = storage.BucketIAMMember(
    "botOnboardBulkSessionsAccess",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=f"serviceAccount:{service_account.email}",
        role="roles/storage.objectAdmin",
    ),
)

if create_onboard_bulk_job:
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
                    value=sessions_bucket.name,
                ),
            ],
            timeout="3600s",
        ),
        opts=ResourceOptions(depends_on=sessions_bucket_perm),
    )
