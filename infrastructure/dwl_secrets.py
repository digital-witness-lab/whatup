from typing import Dict

from pulumi import get_stack, Output
from pulumi_gcp import secretmanager

from config import (
    db_configs,
    db_root_password,
    whatup_anon_key,
    whatup_salt,
    whatup_login_proxy,
)
from database import get_sql_instance_url

db_url_secrets: Dict[str, secretmanager.Secret] = {}
db_pass_secrets: Dict[str, secretmanager.Secret] = {}


def create_secret(name: str, data: str | Output[str]) -> secretmanager.Secret:
    secret = secretmanager.Secret(
        name,
        secretmanager.SecretArgs(
            secret_id=f"{name}-{get_stack()}",
            replication=secretmanager.SecretReplicationArgs(
                auto=secretmanager.SecretReplicationAutoArgs(),
            ),
        ),
    )
    secretmanager.SecretVersion(
        f"{name}-secret",
        secretmanager.SecretVersionArgs(
            secret=secret.id,
            secret_data=data,
            enabled=True,
        ),
    )
    return secret


for db in db_configs.values():
    db_url_secrets[db.name] = create_secret(
        f"{db.name_short}-db-url", get_sql_instance_url(db.name)
    )
    db_pass_secrets[db.name] = create_secret(
        f"{db.name_short}-db-pass", db.password
    )


db_root_pass_secret = create_secret(
    "db-root",
    db_root_password,
)

whatup_salt_secret = create_secret(
    "whatup-salt",
    whatup_salt,
)

whatup_anon_key_secret = create_secret(
    "whatup-anon-key",
    whatup_anon_key,
)

whatup_login_proxy_secret = create_secret(
    "whatup-login-proxy",
    whatup_login_proxy,
)
