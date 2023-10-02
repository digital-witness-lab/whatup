from os import path
from pulumi_gcp import serviceaccount

from ..service import Service, ServiceArgs

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "serviceAccount",
    description=f"Service account for {service_name}",
)

whatupcore2 = Service(
    "whatupcore2",
    ServiceArgs(
        app_path=path.join("..", "whatupcore2"),
        commands=["rpc", "--log-level=DEBUG"],
        concurrency=50,
        container_port=3447,
        cpu=1,
        envs=[],
        image_name="whatupcore2",
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
    ),
)
