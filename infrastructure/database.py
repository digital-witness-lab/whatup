from typing import List
from pulumi import Output, ResourceOptions

from pulumi_gcp import sql

from .config import db_names, db_password, db_root_password
from .network import private_services_network, private_db_network, vpc

sql_instance_settings = sql.DatabaseInstanceSettingsArgs(
    # https://cloud.google.com/sql/pricing#instance-pricing
    tier="db-g1-small",
    deletion_protection_enabled=True,
    ip_configuration=sql.DatabaseInstanceSettingsIpConfigurationArgs(
        allocated_ip_range=private_db_network.name,
        # Allow BigQuery to connect to the DB via the SQL
        # instance's private IP instead.
        enable_private_path_for_google_cloud_services=True,
        # Enable public IP assignment for this SQL instance
        # but it's only so that we can connect to it from
        # the GCP Cloud Shell and do some admin work.
        ipv4_enabled=True,
        authorized_networks=[
            sql.DatabaseInstanceSettingsIpConfigurationAuthorizedNetworkArgs(
                name="private-services-network",
                value=private_services_network.ip_cidr_range,
            )
        ],
        private_network=vpc.id,
    ),
)

primary_cloud_sql_instance = sql.DatabaseInstance(
    "sqlInstance",
    database_version="POSTGRES_15",
    # This is the primary SQL instance.
    instance_type="CLOUD_SQL_INSTANCE",
    settings=sql_instance_settings,
    root_password=db_root_password,
    opts=ResourceOptions(protect=True),
)

databases: List[sql.Database] = []
for db_name in db_names:
    databases.append(
        sql.Database(
            f"{db_name}Db",
            instance=primary_cloud_sql_instance.name,
            name=db_name,
        )
    )

    sql.User(
        f"{db_name}DbUser",
        name=db_name,
        instance=primary_cloud_sql_instance.name,
        password=db_password,
    )


def get_sql_instance_url(db_name: str) -> Output[str]:
    return Output.concat(
        "postgres://",
        db_name,
        ":",
        db_password,
        "@",
        primary_cloud_sql_instance.private_ip_address,
        "5432",
        "/",
        db_name,
    )
