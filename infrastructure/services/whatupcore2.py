from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, secretmanager, serviceaccount
from pulumi_gcp.cloudrunv2 import (
    ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from artifact_registry import whatupcore2_image
from config import is_prod_stack
from dwl_secrets import (
    db_url_secrets,
    whatup_anon_key_secret,
    whatup_salt_secret,
)
from network import private_services_network_with_db, vpc
from service import Service, ServiceArgs

service_name = "whatupcore2"

service_account = serviceaccount.Account(
    "whatupcore",
    account_id=f"whatupcore-{get_stack()}",
    description=f"Service account for {service_name}",
)

db_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["whatupcore"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["whatupcore"].name,
        version="latest",
    )
)

salt_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-salt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_salt_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

whatup_salt_secret_source = (
    cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
        secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
            secret=whatup_salt_secret.name,
            version="latest",
        )
    )
)

anon_key_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-anon-key-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_anon_key_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

whatup_anon_key_secret_source = (
    cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
        secret_key_ref=ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
            secret=whatup_anon_key_secret.name,
            version="latest",
        )
    )
)

log_level = "INFO" if is_prod_stack() else "DEBUG"
whatupcore2_service = Service(
    service_name,
    ServiceArgs(
        args=["rpc", f"--log-level={log_level}"],
        concurrency=500,
        container_port=3447,
        cpu="1",
        # Route only egress traffic bound for private IPs
        # via the VPC network. All other traffic will take
        # the default route bound for the internet gateway.
        # Routing all traffic via the VPC for this container
        # will cause the websocket connection to WhatsApp to
        # fail due to dial timeout.
        egress="PRIVATE_RANGES_ONLY",
        image=whatupcore2_image,
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
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="USE_SSL",
                value="false",
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="APP_NAME_SUFFIX",
                value="" if is_prod_stack() else get_stack(),
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="ENC_KEY_SALT",
                value_source=whatup_salt_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="ANON_KEY",
                value_source=whatup_anon_key_secret_source,
            ),
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="RAND_STRING",  # change rand string to force deploy
                value="34943534473298",
            ),
        ],
    ),
    opts=ResourceOptions(
        depends_on=[
            db_secret_manager_perm,
            salt_secret_manager_perm,
        ]
    ),
)
