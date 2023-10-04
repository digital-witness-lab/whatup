from pulumi import Output, ResourceOptions

from pulumi_gcp import sql

from .config import db_name, db_password, db_user
from .network import private_services_network, private_db_network, vpc

sql_instance_settings = sql.DatabaseInstanceSettingsArgs(
    tier="db-f1-micro",
    deletion_protection_enabled=True,
    ip_configuration=sql.DatabaseInstanceSettingsIpConfigurationArgs(
        allocated_ip_range=private_db_network.name,
        enable_private_path_for_google_cloud_services=True,
        ipv4_enabled=False,
        authorized_networks=[
            sql.DatabaseInstanceSettingsIpConfigurationAuthorizedNetworkArgs(
                name="private-services-network",
                value=private_services_network.ip_cidr_range,
            )
        ],
        private_network=vpc.id,
    ),
)

cloud_sql_instance = sql.DatabaseInstance(
    "sqlInstance",
    database_version="POSTGRES_15",
    settings=sql_instance_settings,
    opts=ResourceOptions(protect=True),
)

database = sql.Database(
    "database",
    instance=cloud_sql_instance.name,
    name=db_name,
)

sql.User(
    "dbUser",
    name=db_user,
    instance=cloud_sql_instance.name,
    password=db_password,
)

sql_instance_url = Output.concat(
    "postgres://",
    db_user,
    ":",
    db_password,
    "@/",
    db_name,
    "?host=/cloudsql/",
    cloud_sql_instance.connection_name,
)
