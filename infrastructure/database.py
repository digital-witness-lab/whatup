from typing import List

from pulumi import Output, ResourceOptions
from pulumi_gcp import sql

from config import db_configs, db_root_password, is_prod_stack, location
from network import private_ip_address_range, private_vpc_connection, vpc

database_descriptions = {
    "messages": {
        "reactions": {"pk": "id"},
        "group_info": {"pk": "id"},
        "device_group_info": {"pk": "id"},
        "group_participants": {"pk": "id"},
        "messages": {"pk": "id"},
        "media": {"pk": "filename"},
        "donor_messages": {"pk": "id"},
    },
    "users": {"user_registration_meta": {"pk": "jid"}},
}

retention_settings = (
    sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
        retention_unit="COUNT",
        retained_backups=7,
    )
)  # noqa: E501

backup_config = sql.DatabaseInstanceSettingsBackupConfigurationArgs(
    enabled=True,
    location=location,
    backup_retention_settings=retention_settings,
)

sql_instance_settings = sql.DatabaseInstanceSettingsArgs(
    # https://cloud.google.com/sql/pricing#instance-pricing
    tier="db-g1-small",
    backup_configuration=backup_config,
    database_flags=[
        sql.DatabaseInstanceSettingsDatabaseFlagArgs(
            name="max_connections", value="500"
        )
    ],
    # Only disable disable protection if you are intentional
    # about wanting to delete the instance.
    deletion_protection_enabled=is_prod_stack(),
    insights_config=sql.DatabaseInstanceSettingsInsightsConfigArgs(
        query_insights_enabled=True,
    ),
    ip_configuration=sql.DatabaseInstanceSettingsIpConfigurationArgs(
        allocated_ip_range=private_ip_address_range.name,
        # Allow BigQuery to connect to the DB via the SQL
        # instance's private IP instead.
        enable_private_path_for_google_cloud_services=True,
        # CAUTION! Enabling the public IP causes this DB to be
        # accessible via the internet.
        # Only enable this if you know what you are doing.
        ipv4_enabled=False,
        private_network=vpc.id,
    ),
)

primary_cloud_sql_instance = sql.DatabaseInstance(
    "whatup",
    database_version="POSTGRES_15",
    # This is the primary SQL instance.
    instance_type="CLOUD_SQL_INSTANCE",
    settings=sql_instance_settings,
    # We don't need this enabled since we are enabling
    # deletion protection on GCP's side with
    # `deletion_protection_enabled` in the
    # instance settings.
    deletion_protection=False,
    root_password=db_root_password,
    opts=ResourceOptions(
        depends_on=private_vpc_connection, protect=is_prod_stack()
    ),
)

databases: List[sql.Database] = []
for db in db_configs.values():
    databases.append(
        sql.Database(
            f"{db.name}",
            instance=primary_cloud_sql_instance.name,
            name=db.name,
        )
    )

    sql.User(
        f"{db.name}",
        name=db.name,
        instance=primary_cloud_sql_instance.name,
        password=db.password,
    )


def get_sql_instance_url(db_name: str) -> Output[str]:
    c = db_configs[db_name]
    return Output.concat(
        "postgresql://",
        db_name,
        ":",
        c.password,
        "@",
        primary_cloud_sql_instance.private_ip_address,
        ":5432/",
        db_name,
    )
