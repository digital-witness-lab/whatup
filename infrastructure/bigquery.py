from pulumi import Output

from pulumi_gcp import projects

from pulumi_google_native import (
    bigquery,
    bigqueryconnection,
    bigquerydatatransfer as dts,
)
from pulumi_google_native.bigqueryconnection.v1beta1 import (
    ConnectionArgs,
    CloudSqlPropertiesArgs,
    CloudSqlPropertiesType,
)

from config import location, project, is_prod_stack
from database import primary_cloud_sql_instance

messages_dataset = bigquery.v2.Dataset(
    "messages",
    bigquery.v2.DatasetArgs(
        description="BigQuery dataset for the messages DB.",
        location=location,
    ),
)

bigquery_sql_connection = bigqueryconnection.v1beta1.Connection(
    "bg-to-sql",
    args=ConnectionArgs(
        location=location,
        friendly_name="messages",
        description="Connection resource for running federated queries in BigQuery.",  # noqa: E501
        cloud_sql=CloudSqlPropertiesArgs(
            instance_id=primary_cloud_sql_instance.id,
            database="messages",
            type=CloudSqlPropertiesType.POSTGRES,
        ),
    ),
)

# Grant access to the service account automatically created
# by GCP when the above connection resource is created in
# the project.
#
# https://cloud.google.com/bigquery/docs/connect-to-sql#access-sql
projects.IAMMember(
    "bq-cloudsql-perm",
    member=Output.concat(
        "serviceAccount:service-",
        projects.get_project_output(filter=f"id:{project}").apply(
            lambda p: p.projects[0].number
        ),
        "@gcp-sa-bigqueryconnection.iam.gserviceaccount.com",
    ),
    project=project,
    role="roles/cloudsql.client",
)

source_tables = [
    "reactions",
    "group_info",
    "group_participants",
    "messages_seen",
    "messages",
    # TODO: Exclude binary objects when dealing
    # with the media table.
    # "media",
]


def create_automated_bq_transfer_jobs():
    """
    Creates data transfer in Big Query (BQ) for
    each table in `source_tables` that need
    to be copied over to BQ. The data
    transfers use scheduled queries.

    https://cloud.google.com/bigquery/docs/scheduling-queries
    """

    for table in source_tables:
        query = (
            Output.concat("SELECT * FROM EXTERNAL_QUERY(")
            .concat(bigquery_sql_connection.id)
            .concat(", ")
            .concat(f"SELECT * FROM {table};")
            .concat(");")
        )
        dts.v1.TransferConfig(
            f"messages-{table}",
            dts.v1.TransferConfigArgs(
                destination_dataset_id=messages_dataset.id,
                display_name=f"Copy messages.{table} data",
                data_source_id="scheduled_query",
                params={
                    "query": query,
                    "write_disposition": "WRITE_TRUNCATE",
                    "partitioning_field": "",
                },
                schedule="every 24 hours",
            ),
        )


if is_prod_stack():
    create_automated_bq_transfer_jobs()
