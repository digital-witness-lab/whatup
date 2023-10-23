from pulumi import get_stack

from pulumi_gcp import secretmanager

from database import get_sql_instance_url

from config import db_root_password

messages_db_url_secret = secretmanager.Secret(
    "msgs-db-url",
    secretmanager.SecretArgs(
        secret_id=f"msgs-db-url-{get_stack()}",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "msgs-db-url-secret",
    secretmanager.SecretVersionArgs(
        secret=messages_db_url_secret.id,
        secret_data=get_sql_instance_url("messages"),
        enabled=True,
    ),
)

messages_db_root_pass_secret = secretmanager.Secret(
    "msgs-db-root",
    secretmanager.SecretArgs(
        secret_id=f"msgs-db-root-{get_stack()}",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "msgs-db-root-secret",
    secretmanager.SecretVersionArgs(
        secret=messages_db_root_pass_secret.id,
        secret_data=db_root_password,
        enabled=True,
    ),
)
