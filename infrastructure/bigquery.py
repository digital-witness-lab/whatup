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
    CloudSqlCredentialArgs,
)

from config import location, project, is_prod_stack, db_configs
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

connection_credential = CloudSqlCredentialArgs(
    username="messages", password=db_configs["messages"].password
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
            credential=connection_credential,
        ),
    ),
)

# Grant access to the service account automatically created
# by GCP when the above connection resource is created in
# the project.
#
# https://cloud.google.com/bigquery/docs/connect-to-sql#access-sql
default_bq_service_account_email = projects.get_project_output(
    filter=f"id:{project}"
).apply(
    lambda p: f"service-{p.projects[0].number}@gcp-sa-bigqueryconnection.iam.gserviceaccount.com"
)

bq_cloudsql_perm = projects.IAMMember(
    "bq-cloudsql-perm",
    member=Output.concat("serviceAccount:").concat(
        default_bq_service_account_email
    ),
    project=project,
    role="roles/cloudsql.client",
    opts=ResourceOptions(
        depends_on=[bigquery_sql_connection],
    ),
)

# Create a custom role instead of using the broad-scoped
# default role `bigquery.admin`. See that role for
# relevant permissions to add to this role.
transfers_role = projects.IAMCustomRole(
    "bq-transfers-role",
    projects.IAMCustomRoleArgs(
        role_id=f"bq-transfers-role-{get_stack()}",
        permissions=[
            "bigquery.transfers.update",
            "bigquery.transfers.get",
            "bigquery.datasets.get",
            "bigquery.datasets.update",
            "bigquery.jobs.create",
        ],
        title="BigQuery Transfers Role",
        stage="GA",
    ),
)

# Grant the custom role to the default service account.
# https://cloud.google.com/bigquery/docs/enable-transfer-service#grant_bigqueryadmin_access
bq_transfers_perm = projects.IAMMember(
    "bq-admin-perm",
    member=Output.concat("serviceAccount:").concat(
        default_bq_service_account_email
    ),
    project=project,
    role=Output.concat("roles/").concat(transfers_role.role_id),
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
            service_account_name=default_bq_service_account_email,
        ),
        opts=ResourceOptions(
            depends_on=[
                bigquery_sql_connection,
                bq_cloudsql_perm,
                bq_transfers_perm,
            ]
        ),
    )
