from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Self, List

import pulumi


class SharedCoreMachineType(Enum):
    E2Micro = "e2-micro"
    E2Small = "e2-small"
    E2Medium = "e2-medium"
    E2HighMem2 = "e2-highmem-2"
    E2HighMem8 = "e2-highmem-8"


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


@dataclass
class DashboardConfig:
    domain: str
    gs_path: str
    auth_groups: List[str]

    jwt: pulumi.Output[str]
    client_creds: pulumi.Output[str]

    @classmethod
    def from_config(cls, config: pulumi.Config, obj: Dict) -> Self:
        jwt = config.require_secret(obj["jwtKey"])
        client_creds = config.require_secret(obj["clientCredsKey"])
        return cls(
            domain=obj["domain"],
            gs_path=obj["gsPath"],
            auth_groups=obj["authGroups"],
            jwt=jwt,
            client_creds=client_creds,
        )


config = pulumi.Config()
db_configs: Dict[str, DatabaseConfig] = {
    data["name"]: DatabaseConfig.from_config(config, data)
    for data in config.require_object("databases")
}
machine_types: Dict[str | None, SharedCoreMachineType] = {
    data["serviceName"]: SharedCoreMachineType[data["type"]]
    for data in config.require_object("machineTypes")
}
if None in machine_types:
    default_type = machine_types.pop(None)
    machine_types = defaultdict(lambda: default_type, **machine_types)

root_domain = config.get("rootDomain", None)
bq_dataset_region = config.require("bqDatasetRegion")
db_root_password = config.require_secret("dbRootPassword")
whatup_salt = config.require_secret("whatupSalt")
whatup_anon_key = config.require_secret("whatupAnonKey")
whatup_login_proxy = config.get_secret("whatupLoginProxy") or ""

primary_bot_name = str(config.require("primary_bot_name"))
temp_bucket_ttl_days = config.require_int("temp_bucket_ttl_days")
control_groups = config.require_object("control_groups")

is_prod = config.get_bool("isProd", False) or False
load_archive_job = config.get_bool("loadArchiveJob", False)
translation_enabled = config.get_bool("translationEnabled", False)

enabledServices = config.require_object("enabledServices")

dashboard_configs: Dict[str, DashboardConfig] = {
    data["domain"]: DashboardConfig.from_config(config, data)
    for data in config.get_object("dashboards", [])
}

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
zone = gcp_config.require("zone")


def is_prod_stack() -> bool:
    return is_prod
