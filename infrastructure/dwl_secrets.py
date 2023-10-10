from pulumi_gcp import secretmanager

from database import get_sql_instance_url, get_sql_instance_root_url

messages_db_url_secret = secretmanager.Secret(
    "messagesDbUrlSecret",
    secretmanager.SecretArgs(
        secret_id="db_url_secret",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "messagesDbUrlSecretVer",
    secretmanager.SecretVersionArgs(
        secret=messages_db_url_secret.id,
        secret_data=get_sql_instance_url("messages"),
        enabled=True,
    ),
)

messages_db_root_url_secret = secretmanager.Secret(
    "messagesDbRootUrlSecret",
    secretmanager.SecretArgs(
        secret_id="db_root_url_secret",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "messagesDbRootUrlSecretVer",
    secretmanager.SecretVersionArgs(
        secret=messages_db_root_url_secret.id,
        secret_data=get_sql_instance_root_url("messages"),
        enabled=True,
    ),
)
