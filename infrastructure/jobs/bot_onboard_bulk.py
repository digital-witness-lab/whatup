from os import path

from pulumi import ResourceOptions, Output
from pulumi_gcp import serviceaccount, cloudrunv2, storage

from config import create_onboard_bulk_job
from job import JobArgs, Job
from network import vpc, private_services_network
from storage import sessions_bucket

from services.whatupcore2 import whatupcore2_service

service_name = "whatupy-bot-onboard-bulk"

service_account = serviceaccount.Account(
    "whatupOnboardBulk",
    account_id="whatupy-bot-onboard-bulk",
    description=f"Service account for {service_name}",
)

sessions_bucket_perm = storage.BucketIAMMember(
    "botOnboardBulkSessionsAccess",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

if create_onboard_bulk_job:
    bot_onboard_bulk_job = Job(
        service_name,
        JobArgs(
            app_path=path.join("..", "whatupy"),
            args=[
                "/usr/src/whatupy/gcsfuse_run.sh",
                "onboard-bulk",
                "--host",
                "$(WHATUPCORE2_HOST)",
                "--credentials-dir",
                "$(BUCKET_MNT_DIR_PREFIX)/$(SESSIONS_BUCKET_MNT_DIR)",
            ],
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
                network=vpc.id, subnetwork=private_services_network.id
            ),
            envs=[
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="BUCKET_MNT_DIR_PREFIX",
                    value="/usr/src/whatupy-data",
                ),
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="SESSIONS_BUCKET",
                    value=sessions_bucket.name,
                ),
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="SESSIONS_BUCKET_MNT_DIR",
                    value="sessions/",
                ),
                cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                    name="WHATUPCORE2_HOST",
                    value=whatupcore2_service.service.uri,
                ),
            ],
            timeout="3600s",
        ),
        opts=ResourceOptions(depends_on=sessions_bucket_perm),
    )
