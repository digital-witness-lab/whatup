# flake8: noqa
import pulumi

# Import this first to register the services first.
import gcp_services
from bigquery import bigquery_sql_connection
from jobs import (bot_db_load_archive, bot_onboard_bulk, bq_init_schema,
                  db_delete_groups, db_migrations, whatupcore_remove_user) #hash_gen
from services import (bot_archive, bot_db, bot_register, bot_user_services,
                      whatupcore2)

# pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
