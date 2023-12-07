from dataclasses import dataclass
from typing import List, Self, Dict
import pulumi


@dataclass
class DatabaseConfig:
    name: str
    name_short: str
    password: str

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
create_load_archive_job = config.get_bool("createLoadArchiveJob")
create_onboard_bulk_job = config.get_bool("createOnboardBulkJob")


# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")


def is_prod_stack() -> bool:
    return pulumi.get_stack() == "prod"
