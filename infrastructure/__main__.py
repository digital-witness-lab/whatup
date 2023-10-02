import pulumi

from pulumi_gcp import cloudrunv2, config as gcp_config
from pulumi_gcp import artifactregistry
import pulumi_random as random

# Import the program's configuration settings.
config = pulumi.Config()
app_path = config.get("appPath", "./app")
image_name = config.get("imageName", "my-app")
container_port = config.get_int("containerPort", 8080)
cpu = config.get_int("cpu", 1)
memory = config.get("memory", "1Gi")
concurrency = config.get_float("concurrency", 50)

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")
