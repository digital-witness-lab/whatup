# flake8: noqa
import pulumi

# Import this first to register the services first.
import gcp_services
from bigquery import sql_connections
from jobs import (
    bot_db_load_archive,
    bot_onboard_bulk,
    bq_init_schema,
    db_delete_groups,
    db_migrations,
    hash_gen,
    whatupcore_remove_user,
)
from services import (
    bot_archive,
    bot_db,
    bot_register,
    bot_user_services,
    whatupcore2,
)
from scheduled_tasks import (
    translate_bigquery,
    cloudsql_bigquery_transfer,
)

# pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
