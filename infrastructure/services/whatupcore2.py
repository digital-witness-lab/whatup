from os import path
from pulumi_gcp import serviceaccount, cloudrunv2

from ..service import Service, ServiceArgs
from ..network import vpc, private_services_network

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "serviceAccount",
    description=f"Service account for {service_name}",
)

whatupcore2 = Service(
    "whatupcore2",
    ServiceArgs(
        app_path=path.join("..", "..", "whatupcore2"),
        commands=["rpc", "--log-level=DEBUG"],
        concurrency=50,
        container_port=3447,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image_name="whatupcore2",
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network.id
        ),
        envs=[],
    ),
)
