# flake8: noqa
import pulumi

# Import this first to register the services first.
import gcp_services
from bigquery import sql_connections
from config import enabledServices
from jobs import bq_init_schema, db_migrations, db_delete_groups
import storage

enabledServicesPackages = [es.replace("-", "_") for es in enabledServices]
services = __import__(
    "services",
    globals(),
    locals(),
    enabledServicesPackages,
)
for service in enabledServicesPackages:
    locals()[service] = getattr(services, service)

if enabledServicesPackages:
    from jobs import (
        bot_db_load_archive,
        bot_onboard_bulk,
        hash_gen,
        whatupcore_remove_user,
        whatupcore_remove_burners,
    )
    from services import whatupcore2


from scheduled_tasks import (
    translate_bigquery,
    cloudsql_bigquery_transfer,
)

# pulumi.export("bigquery_connection_id", bigquery_sql_connection.connection_id)
