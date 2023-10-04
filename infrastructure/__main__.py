import pulumi

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
