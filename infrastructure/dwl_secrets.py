from pulumi_gcp import secretmanager

from database import get_sql_instance_url

from config import db_root_password

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

messages_db_root_pass_secret = secretmanager.Secret(
    "messagesDbRootPassSecret",
    secretmanager.SecretArgs(
        secret_id="db_root_pass_secret",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "messagesDbRootPassSecretVer",
    secretmanager.SecretVersionArgs(
        secret=messages_db_root_pass_secret.id,
        secret_data=db_root_password,
        enabled=True,
    ),
)
