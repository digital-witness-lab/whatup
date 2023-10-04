import pulumi

config = pulumi.Config()
db_name = config.require("dbName")
db_password = config.require_secret("dbPassword")
db_user = config.require("dbUser")


# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
