from pulumi import get_stack, Output, export

from pulumi_gcp import serviceaccount, cloudrunv2, projects

from job import JobArgs, Job
from network import vpc, private_services_network_with_db
from artifact_registry import bq_init_schema_image
from bigquery import (
    bq_dataset_id,
    messages_tables,
    bigquery_sql_connection,
    transfers_role,
)
from config import project

from .execute_job import run_job_sync
from .db_migrations import migrations_job_complete


job_name = "bq-init-schema"

service_account = serviceaccount.Account(
    "bq-init-schema",
    account_id=f"db-init-schema-{get_stack()}",
    description=f"Service account for {job_name}",
)

transfers_perm = projects.IAMMember(
    "bq-init-transfers-perm",
    member=Output.concat("serviceAccount:", service_account.email),
    project=project,
    role=Output.concat("roles/").concat(transfers_role.name),
)


bq_init_schema_job = Job(
    job_name,
    JobArgs(
        args=["/run.sh"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=bq_init_schema_image,
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
                name="BQ_DATASET_ID",
                value=bq_dataset_id,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="BQ_PSQL_CONNECTION",
                value=bigquery_sql_connection.name,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="TABLES",
                value=",".join(messages_tables),
            ),
            # Create an implicit dependency on the migrations
            # job completing successfully.
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="MIGRATIONS_JOB_COMPLETE",
                value=migrations_job_complete.apply(lambda b: f"{b}"),
            ),
        ],
        timeout="60s",
    ),
)
