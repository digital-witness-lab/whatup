from pulumi import Output, get_stack, ResourceOptions

from pulumi_gcp import projects

from pulumi_google_native import (
    bigquery,
    bigquerydatatransfer as dts,
)
from pulumi_google_native.bigqueryconnection.v1beta1 import (
    Connection,
    ConnectionArgs,
    CloudSqlPropertiesArgs,
    CloudSqlPropertiesType,
)

from config import location, project, is_prod_stack
from database import primary_cloud_sql_instance

dataset_id = f"messages_{get_stack()}"

messages_dataset = bigquery.v2.Dataset(
    "messages",
    bigquery.v2.DatasetArgs(
        dataset_reference=bigquery.v2.DatasetReferenceArgs(
            dataset_id=dataset_id,
        ),
        description="BigQuery dataset for the messages DB.",
        location=location,
        friendly_name=f"messages_{get_stack()}",
    ),
)

bigquery_sql_connection = Connection(
    "bg-to-sql",
    args=ConnectionArgs(
        location=location,
        connection_id=f"messages_{get_stack()}",
        friendly_name=f"messages_{get_stack()}",
        description="Connection resource for running federated queries in BigQuery.",  # noqa: E501
        cloud_sql=CloudSqlPropertiesArgs(
            instance_id=primary_cloud_sql_instance.connection_name,
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
service_account_name = projects.get_project_output(
    filter=f"id:{project}"
).apply(
    lambda p: f"serviceAccount:service-{p.projects[0].number}@gcp-sa-bigqueryconnection.iam.gserviceaccount.com"
)

service_account = projects.IAMMember(
    "bq-cloudsql-perm",
    member=service_account_name,
    project=project,
    role="roles/cloudsql.client",
    opts=ResourceOptions(
        depends_on=[bigquery_sql_connection],
    ),
)

source_tables = [
    "reactions",
    "group_info",
    "group_participants",
    "messages_seen",
    "messages",
    "media",
]

# Creates data transfer in Big Query (BQ) for
# each table in `source_tables` that need
# to be copied over to BQ. The data
# transfers use scheduled queries.
#
# https://cloud.google.com/bigquery/docs/scheduling-queries

for table in source_tables:
    query = Output.all(table=table, conn_id=bigquery_sql_connection.id).apply(
        lambda args: f"""
    MERGE INTO
        messages.{args['table']} AS bq
    USING
        SELECT *
        FROM
            EXTERNAL_QUERY(
                "{args['conn_id']}",
                "SELECT * FROM {args['table']};"
            ) AS pg
    ON
        bq.id = pg.id AND bq.record_mtime = pg.record_mtime
    WHEN NOT MATCHED BY SOURCE
    THEN
        DELETE
    WHEN NOT MATCHED BY TARGET
    THEN
        INSERT ROW;""".strip()
    )

    dts.v1.TransferConfig(
        f"msg-{table}-{get_stack()}-trans",
        dts.v1.TransferConfigArgs(
            destination_dataset_id=dataset_id,
            display_name=f"Copy messages.{table} data",
            data_source_id="scheduled_query",
            params={
                "query": query,
                # "partitioning_field": "",
            },
            schedule="every 24 hours" if is_prod_stack() else None,
            service_account_name=service_account_name,
        ),
        opts=ResourceOptions(
            depends_on=[bigquery_sql_connection, service_account]
        ),
    )
