from pulumi import Output, get_stack, ResourceOptions

from pulumi_gcp import projects, serviceaccount

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

from config import (
    location,
    project,
    is_prod_stack,
    db_configs,
)
from database import primary_cloud_sql_instance
from gcloud import get_project_number

bq_dataset_id = f"messages_{get_stack().replace('-', '_')}"
messages_tables = [
    "reactions",
    "group_info",
    "group_participants",
    "messages_seen",
    "messages",
    "media",
]


messages_dataset = bigquery.v2.Dataset(
    "messages",
    bigquery.v2.DatasetArgs(
        dataset_reference=bigquery.v2.DatasetReferenceArgs(
            dataset_id=bq_dataset_id,
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
default_bq_connection_service_account_email = get_project_number(
    project
).apply(
    lambda proj_number: f"service-{proj_number}@gcp-sa-bigqueryconnection.iam.gserviceaccount.com"
)

bq_cloudsql_perm = projects.IAMMember(
    "bq-cloudsql-perm",
    member=Output.concat(
        "serviceAccount:", default_bq_connection_service_account_email
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

data_transfers_service_account = serviceaccount.Account(
    "bq-datatransfers-sa",
    serviceaccount.AccountArgs(
        account_id=f"bq-datatransfers-sa-{get_stack()}",
        description="Service account used by Big Query Data Transfers",
    ),
)

# Grant the custom role to the custom service account.
# https://cloud.google.com/bigquery/docs/enable-transfer-service#grant_bigqueryadmin_access
bq_transfers_perm = projects.IAMMember(
    "bq-transfers-perm",
    member=Output.concat(
        "serviceAccount:", data_transfers_service_account.email
    ),
    project=project,
    role=Output.concat("roles/").concat(transfers_role.name),
    opts=ResourceOptions(
        depends_on=[bigquery_sql_connection],
    ),
)

# Creates data transfer in Big Query (BQ) for
# each table in `source_tables` that need
# to be copied over to BQ. The data
# transfers use scheduled queries.
#
# https://cloud.google.com/bigquery/docs/scheduling-queries

for table in messages_tables:
    messages_dataset_table = bigquery.v2.Table(
        f"{table}-{get_stack()}_tbl".replace("_", "-"),
        dataset_id=bq_dataset_id,
        project=project,
        table_reference=bigquery.v2.TableReferenceArgs(
            dataset_id=bq_dataset_id, project=project, table_id=table
        ),
    )
    query = Output.all(
        dataset_id=bq_dataset_id,
        table_name=table,
        conn_name=bigquery_sql_connection.name,
    ).apply(
        lambda args: f"""
    MERGE INTO
        {args["dataset_id"]}.{args["table_name"]} AS bq
    USING
        (SELECT *
        FROM
            EXTERNAL_QUERY(
                "{args['conn_name']}",
                "SELECT * FROM {args['table_name']};"
            ) pg)
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
            destination_dataset_id=bq_dataset_id,
            display_name=f"Copy messages.{table} data",
            data_source_id="scheduled_query",
            params={
                "query": query,
            },
            schedule="every 24 hours" if is_prod_stack() else None,
            service_account_name=data_transfers_service_account.email,
        ),
        opts=ResourceOptions(
            depends_on=[
                bigquery_sql_connection,
                bq_cloudsql_perm,
                bq_transfers_perm,
                messages_dataset_table,
            ]
        ),
    )
