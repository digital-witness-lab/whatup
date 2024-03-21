import typing as T

from pulumi import get_stack
from pulumi_gcp import projects
from pulumi_google_native import bigquery
from pulumi_google_native.bigqueryconnection.v1beta1 import (
    CloudSqlCredentialArgs,
    CloudSqlPropertiesArgs,
    CloudSqlPropertiesType,
    Connection,
    ConnectionArgs,
)

from config import db_configs, location, db_region, project
from database import primary_cloud_sql_instance
from gcloud import get_project_number

bq_dataset_id = f"messages_{get_stack().replace('-', '_')}"


def create_sql_connection(db_config, bq_region, sql_region) -> Connection:
    connection_credential = CloudSqlCredentialArgs(
        username=db_config.name, password=db_config.password
    )
    return Connection(
        f"bg-to-sql-{db_config.name_short}",
        args=ConnectionArgs(
            location=sql_region,
            connection_id=f"{db_config.name}_{get_stack()}",
            friendly_name=f"{db_config.name}_{get_stack()}",
            description="Connection resource for running federated queries in BigQuery.",  # noqa: E501
            cloud_sql=CloudSqlPropertiesArgs(
                instance_id=primary_cloud_sql_instance.connection_name,
                database=db_config.name,
                type=CloudSqlPropertiesType.POSTGRES,
                credential=connection_credential,
            ),
        ),
    )


messages_dataset = bigquery.v2.Dataset(
    "messages",
    bigquery.v2.DatasetArgs(
        dataset_reference=bigquery.v2.DatasetReferenceArgs(
            dataset_id=bq_dataset_id,
        ),
        description="BigQuery dataset for the messages DB.",
        location=db_region,
        friendly_name=f"messages_{get_stack()}",
    ),
)


sql_connections: T.Dict[str, Connection] = {
    "users": create_sql_connection(db_configs["users"], db_region, location),
    "messages": create_sql_connection(
        db_configs["messages"], db_region, location
    ),
}

# Grant access to the service account automatically created
# by GCP when the above connection resource is created in
# the project.
#
# https://cloud.google.com/bigquery/docs/connect-to-sql#access-sql
default_bq_connection_service_account_email = get_project_number(
    project
).apply(
    lambda proj_number: f"service-{proj_number}@gcp-sa-bigqueryconnection.iam.gserviceaccount.com"
)

# Create a custom role instead of using the broad-scoped
# default role `bigquery.admin`. See that role for
# relevant permissions to add to this role.
transfers_role = projects.IAMCustomRole(
    "bq-transfers-role",
    projects.IAMCustomRoleArgs(
        # GCP wants this to be a camel-cased role id.
        # The regex for this disallows the use of dashes(-).
        role_id=f"bqTransfersRole{get_stack().casefold().replace('-', '_')}",
        permissions=[
            "bigquery.transfers.update",
            "bigquery.transfers.get",
            "bigquery.datasets.get",
            "bigquery.datasets.update",
            "bigquery.jobs.create",
            "bigquery.connections.get",
            "bigquery.connections.use",
            "bigquery.tables.create",
            "bigquery.tables.createIndex",
            "bigquery.tables.delete",
            "bigquery.tables.deleteIndex",
            "bigquery.tables.get",
            "bigquery.tables.getData",
            "bigquery.tables.list",
            "bigquery.tables.update",
            "bigquery.tables.updateData",
        ],
        title="BigQuery Transfers Role",
        stage="GA",
    ),
)
