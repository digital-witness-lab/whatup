from dataclasses import dataclass
from typing import Dict, Self

import pulumi


@dataclass
class DatabaseConfig:
    name: str
    name_short: str
    password: pulumi.Output[str]

    @classmethod
    def from_config(cls, config: pulumi.Config, obj: Dict) -> Self:
        password_key = obj["passwordKey"]
        return cls(
            name=obj["name"],
            name_short=obj["nameShort"],
            password=config.require_secret(password_key),
        )


config = pulumi.Config()
db_configs: Dict[str, DatabaseConfig] = {
    data["name"]: DatabaseConfig.from_config(config, data)
    for data in config.require_object("databases")
}

db_root_password = config.require_secret("dbRootPassword")
whatup_salt = config.require_secret("whatupSalt")
whatup_anon_key = config.require_secret("whatupAnonKey")

primary_bot_name = str(config.require("primary_bot_name"))
temp_bucket_ttl_days = config.require_int("temp_bucket_ttl_days")
control_groups = config.require_object("control_groups")

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
zone = gcp_config.require("zone")


def is_prod_stack() -> bool:
    return pulumi.get_stack() == "prod"
