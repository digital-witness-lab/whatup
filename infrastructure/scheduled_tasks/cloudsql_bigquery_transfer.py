from pulumi import Output, ResourceOptions, get_stack
from pulumi_google_native import bigquery
from pulumi_google_native import bigquerydatatransfer as dts

from config import is_prod_stack, project, bq_dataset_region
from bigquery import (
    bq_dataset_id,
    messages_dataset,
    sql_connections,
    data_transfers_service_account,
)
from database import database_descriptions


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
                location=bq_dataset_region,
                display_name=f"Copy messages.{table} data",
                data_source_id="scheduled_query",
                params={
                    "query": query,
                },
                # run every 3 hours, starting at midnight
                schedule="every 3 hours syncronized"
                if is_prod_stack()
                else None,
                service_account_name=data_transfers_service_account.email,
            ),
            opts=ResourceOptions(
                depends_on=[
                    sql_connections[database],
                    bq_table,
                ]
            ),
        )
