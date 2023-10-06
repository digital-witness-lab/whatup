from pulumi_gcp import secretmanager

from .database import get_sql_instance_url

db_url_secret = secretmanager.Secret(
    "dbUrlSecret",
    secretmanager.SecretArgs(
        secret_id="db_url_secret",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "dbUrlSecretVersion",
    secretmanager.SecretVersionArgs(
        secret=db_url_secret.id,
        secret_data=get_sql_instance_url("messages"),
        enabled=True,
    ),
)
