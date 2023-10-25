from os import path

from pulumi import get_stack, ResourceOptions, Output
from pulumi_gcp import serviceaccount, cloudrunv2, storage

from service import Service, ServiceArgs
from network import vpc, private_services_network
from storage import whatupcore2_bucket

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "whatupcore",
    account_id=f"whatupcore-{get_stack()}",
    description=f"Service account for {service_name}",
)

bucket_perm = storage.BucketIAMMember(
    "wu-core-strg-perm",
    storage.BucketIAMMemberArgs(
        bucket=whatupcore2_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

whatupcore2_service = Service(
    service_name,
    ServiceArgs(
        app_path=path.join("..", "whatupcore2"),
        args=["/gcsfuse_run.sh", "--log-level=INFO"],
        concurrency=50,
        container_port=3447,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image_name=service_name,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        public_access=True,
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="USE_SSL",
                value="false",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_BUCKET",
                value=whatupcore2_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="WHATUPCORE2_BUCKET_MNT_DIR",
                value="/db/",
            ),
        ],
    ),
    opts=ResourceOptions(depends_on=bucket_perm),
)
