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

from bigquery import bigquery_sql_connection

pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
