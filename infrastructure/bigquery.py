import typing as T

from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import projects, serviceaccount
from pulumi_google_native import bigquery
from pulumi_google_native import bigquerydatatransfer as dts
from pulumi_google_native.bigqueryconnection.v1beta1 import (
    CloudSqlCredentialArgs,
    CloudSqlPropertiesArgs,
    CloudSqlPropertiesType,
    Connection,
    ConnectionArgs,
)

from config import db_configs, is_prod_stack, location, project
from database import primary_cloud_sql_instance
from gcloud import get_project_number

bq_dataset_id = f"messages_{get_stack().replace('-', '_')}"
table_transfers = {
    "messages": {
        "reactions": {"pk": "id"},
        "group_info": {"pk": "id"},
        "group_participants": {"pk": "id"},
        "messages": {"pk": "id"},
        "media": {"pk": "filename"},
        "donor_messages": {"pk": "id"},
        "phash_images": {"pk": "filename"},
    },
    "users": {"user_registration_meta": {"pk": "jid"}},
}


def create_sql_connection(db_config) -> Connection:
    connection_credential = CloudSqlCredentialArgs(
        username=db_config.name, password=db_config.password
    )
    return Connection(
        f"bg-to-sql-{db_config.name_short}",
        args=ConnectionArgs(
            location=location,
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
        location=location,
        friendly_name=f"messages_{get_stack()}",
    ),
)


sql_connections: T.Dict[str, Connection] = {
    "users": create_sql_connection(db_configs["users"]),
    "messages": create_sql_connection(db_configs["messages"]),
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

bq_cloudsql_perm = projects.IAMMember(
    "bq-cloudsql-perm",
    member=Output.concat(
        "serviceAccount:", default_bq_connection_service_account_email
    ),
    project=project,
    role="roles/cloudsql.client",
    opts=ResourceOptions(
        depends_on=list(sql_connections.values()),
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
        depends_on=list(sql_connections.values()),
    ),
)

# Creates data transfer in Big Query (BQ) for
# each table in `source_tables` that need
# to be copied over to BQ. The data
# transfers use scheduled queries.
#
# https://cloud.google.com/bigquery/docs/scheduling-queries

for database, tables_spec in table_transfers.items():
    for table, table_meta in tables_spec.items():
        bq_table = bigquery.v2.Table(
            f"{table}-{get_stack()}_tbl".replace("_", "-"),
            dataset_id=bq_dataset_id,
            project=project,
            table_reference=bigquery.v2.TableReferenceArgs(
                dataset_id=bq_dataset_id, project=project, table_id=table
            ),
            opts=ResourceOptions(depends_on=[messages_dataset]),
        )
        query = Output.all(
            dataset_id=bq_dataset_id,
            table_name=table,
            table_pk=table_meta.get("pk", "id"),
            conn_name=sql_connections[database].name,
        ).apply(
            lambda args: f"""
        MERGE INTO
            {args["dataset_id"]}.{args["table_name"]} AS bq
        USING
            (
                SELECT *
                FROM EXTERNAL_QUERY(
                    "{args['conn_name']}",
                    "SELECT * FROM {args['table_name']};"
                )
            ) AS pg
        ON
            bq.{args["table_pk"]} = pg.{args["table_pk"]} AND bq.record_mtime = pg.record_mtime
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
                schedule="every 6 hours" if is_prod_stack() else None,
                service_account_name=data_transfers_service_account.email,
            ),
            opts=ResourceOptions(
                depends_on=[
                    sql_connections[database],
                    bq_cloudsql_perm,
                    bq_transfers_perm,
                    bq_table,
                ]
            ),
        )
