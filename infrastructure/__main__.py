# flake8: noqa
import pulumi

# Import this first to register the services first.
import gcp_services

from services import (
    whatupcore2,
    bot_archive,
    bot_db,
    bot_register,
)
from jobs import (
    bot_db_load_archive,
    bot_onboard_bulk,
    db_migrations,
    whatupcore_remove_user,
)

from bigquery import bigquery_sql_connection, create_automated_bq_transfer_jobs

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

create_automated_bq_transfer_jobs(source_tables)

pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
