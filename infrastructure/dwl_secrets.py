from typing import Dict

from pulumi import get_stack
from pulumi_gcp import secretmanager

from database import get_sql_instance_url
from config import db_root_password, db_configs


db_url_secrets: Dict[str, secretmanager.Secret] = {}
for db in db_configs.values():
    db_url_secrets[db.name] = secret = secretmanager.Secret(
        f"{db.name_short}-db-url",
        secretmanager.SecretArgs(
            secret_id=f"{db.name_short}-db-url-{get_stack()}",
            replication=secretmanager.SecretReplicationArgs(
                auto=secretmanager.SecretReplicationAutoArgs(),
            ),
        ),
    )
    secretmanager.SecretVersion(
        f"{db.name_short}-db-url-secret",
        secretmanager.SecretVersionArgs(
            secret=secret.id,
            secret_data=get_sql_instance_url(db.name),
            enabled=True,
        ),
    )


db_root_pass_secret = secretmanager.Secret(
    "db-root",
    secretmanager.SecretArgs(
        secret_id=f"db-root-{get_stack()}",
        replication=secretmanager.SecretReplicationArgs(
            auto=secretmanager.SecretReplicationAutoArgs(),
        ),
    ),
)

secretmanager.SecretVersion(
    "db-root-secret",
    secretmanager.SecretVersionArgs(
        secret=db_root_pass_secret.id,
        secret_data=db_root_password,
        enabled=True,
    ),
)
