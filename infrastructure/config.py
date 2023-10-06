from typing import List
import pulumi

config = pulumi.Config()
db_names: List[str] = config.require_object("dbNames")
db_password = config.require_secret("dbPassword")
db_root_password = config.require_secret("dbRootPassword")

create_load_archive_job = config.get_bool("createLoadArchiveJob")
create_onboard_bulk_job = config.get_bool("createOnboardBulkJob")


# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
