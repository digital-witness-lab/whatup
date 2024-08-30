from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import (
    cloudrunv2,
    serviceaccount,
    storage,
    bigquery,
)

from artifact_registry import diwi_api_image
from service import Service, ServiceArgs
from storage import media_bucket
from bigquery import bq_dataset_id
from dns import create_subdomain_service
from network import public_services_network, vpc_public

service_name = "api-data"

service_account = serviceaccount.Account(
    "api-data",
    account_id=f"whatup-api-data-{get_stack()}",
    description=f"Service account for {service_name}",
)

bigquery_user_perm = bigquery.DatasetIamMember(
    "api-data-bq-user-perm",
    bigquery.DatasetIamMemberArgs(
        dataset_id=bq_dataset_id,
        role="roles/bigquery.user",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

media_bucket_perm = storage.BucketIAMMember(
    "api-data-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

api_data = Service(
    service_name,
    ServiceArgs(
        args=["data-api"],
        concurrency=50,
        container_port=8080,
        protocol="http1",
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=diwi_api_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_ALL",
        memory="1Gi",
        public_access=True,
        service_account=service_account,
        request_timeout=60,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc_public.id, subnetwork=public_services_network.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="MEDIA_BUCKET",
                value=media_bucket.name,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="BIGQUERY_DATASET_ID",
                value=bq_dataset_id,
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[
            media_bucket_perm,
            bigquery_user_perm,
        ]
    ),
)

create_subdomain_service("data", api_data)
