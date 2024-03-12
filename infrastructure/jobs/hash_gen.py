from pulumi import Output, get_stack
from pulumi_gcp import cloudrunv2, serviceaccount, storage, projects
from artifact_registry import hash_gen_image
from bigquery import (
    transfers_role,
    bq_dataset_id,
)
from job import Job, JobArgs
from network import private_services_network_with_db, vpc
from storage import media_bucket
from config import project

service_name = "hash-gen"

service_account = serviceaccount.Account(
    "hash-gen",
    account_id=f"hash-gen-{get_stack()}",
    description=f"Service account for {service_name}",
)

transfers_perm = projects.IAMMember(
    "hash-gen-transfers-perm",
    member=Output.concat("serviceAccount:", service_account.email),
    project=project,
    role=Output.concat("roles/").concat(transfers_role.name),
)

media_bucket_perm = storage.BucketIAMMember(
    "hash-gen-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

hash_gen_job = Job(
    service_name,
    JobArgs(
        args=["/run.sh"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=hash_gen_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="2Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="PROJECT_ID",
                value=project,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATASET_ID",
                value=bq_dataset_id,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="MEDIA_BUCKET",
                value=media_bucket.name,
            ),
        ],
        timeout="3600s",
    ),
)
