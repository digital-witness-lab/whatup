import urllib.parse

from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)
from pulumi_gcp import (
    cloudrunv2,
    serviceaccount,
    storage,
    secretmanager,
)

from artifact_registry import diwi_dashboard_image
from service import Service, ServiceArgs
from dns import create_subdomain_service
from network import public_services_network, vpc_public
from dwl_secrets import create_secret
from config import dashboard_configs

dashboards = {}
for name, dc in dashboard_configs.items():
    bucket = urllib.parse.urlparse(dc.gs_path, "gs").netloc
    service_name = f"dshbd-{name}-{get_stack()}"

    service_account = serviceaccount.Account(
        f"{service_name}-sa",
        account_id=f"{service_name}",
        description=f"Service account for {service_name}",
    )

    dashboard_bucket_perm = storage.BucketIAMMember(
        f"{service_name}-bucket-perm",
        storage.BucketIAMMemberArgs(
            bucket=bucket,
            member=Output.concat("serviceAccount:", service_account.email),
            role="roles/storage.objectViewer",
        ),
    )

    jwt_secret = create_secret(f"{service_name}-jwt-secret", dc.jwt)
    jwt_perm = secretmanager.SecretIamMember(
        f"{service_name}-jwt-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=jwt_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )
    jwt_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
        secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
            secret=jwt_secret.name,
            version="latest",
        ),
    )

    client_creds_secret = create_secret(
        f"{service_name}-client-creds-secret", dc.client_creds
    )
    client_creds_perm = secretmanager.SecretIamMember(
        f"{service_name}-client-creds-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=client_creds_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )

    client_creds_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
        secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
            secret=client_creds_secret.name,
            version="latest",
        ),
    )

    # Add IAM role 'roles/resourcemanager.viewer' to the service account
    group_list_perm = serviceaccount.IAMMember(
        f"{service_name}-list-groups",
        service_account_id=service_account.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudidentity.groups.readonly",
    )

    dashboard = dashboards[name] = Service(
        service_name,
        ServiceArgs(
            args=[],
            concurrency=50,
            container_port=8080,
            protocol="http1",
            cpu="1",
            # Route all egress traffic via the VPC network.
            egress="ALL_TRAFFIC",
            image=diwi_dashboard_image,
            # We want this service to only be reachable from within
            # our VPC network.
            ingress="INGRESS_TRAFFIC_ALL",
            memory="512M",
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
                    # we _are_ using SSL but cloudrun hides this from aiohttp
                    name="OAUTHLIB_INSECURE_TRANSPORT",
                    value="1",
                ),
                cloudrunv2.ServiceTemplateContainerEnvArgs(
                    name="DASHBOARD_AUTH_GROUP",
                    value=":".join(dc.auth_groups),
                ),
                cloudrunv2.ServiceTemplateContainerEnvArgs(
                    name="DASHBOARD_GS_PATH",
                    value=dc.gs_path,
                ),
                cloudrunv2.ServiceTemplateContainerEnvArgs(
                    name="GOOGLE_AUTH_DATA",
                    value_source=client_creds_secret_source,
                ),
                cloudrunv2.ServiceTemplateContainerEnvArgs(
                    name="JWT_SECRET",
                    value_source=jwt_secret_source,
                ),
            ],
        ),
        opts=ResourceOptions(
            depends_on=[
                jwt_perm,
                client_creds_perm,
                dashboard_bucket_perm,
                group_list_perm,
            ]
        ),
    )

    create_subdomain_service(dc.domain, dashboard)
