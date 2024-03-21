from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import projects, serviceaccount
from pulumi_google_native import bigquery
from pulumi_google_native import bigquerydatatransfer as dts

from config import is_prod_stack, project
from bigquery import (
    bq_dataset_id,
    messages_dataset,
    sql_connections,
    default_bq_connection_service_account_email,
    transfers_role,
)
from database import database_descriptions

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


# Creates data transfer in Big Query (BQ) for
# each table in `source_tables` that need
# to be copied over to BQ. The data
# transfers use scheduled queries.
#
# https://cloud.google.com/bigquery/docs/scheduling-queries

for database, tables_spec in database_descriptions.items():
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
