# flake8: noqa
import pulumi

# Import this first to register the services first.
import gcp_services

from bigquery import bigquery_sql_connection

from jobs import (
    bot_db_load_archive,
    # bot_onboard_bulk,
    bq_init_schema,
    db_migrations,
    db_delete_groups,
    whatupcore_remove_user,
)
from services import (
    whatupcore2,
    bot_register,
)

# pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
