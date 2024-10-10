from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, secretmanager, serviceaccount
from pulumi_gcp.cloudrunv2 import (
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from artifact_registry import whatupcore2_image
from dwl_secrets import (
    db_url_secrets,
    whatup_anon_key_secret,
    whatup_salt_secret,
)
from job import Job, JobArgs
from network import private_services_network_with_db, vpc

service_name = "whatupcore-remove-burners"

service_account = serviceaccount.Account(
    "remove-burners",
    account_id=f"whatupcore-rmburners-{get_stack()}",
    description=f"Service account for {service_name}",
)

salt_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-rmburners-salt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_salt_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

whatup_salt_secret_source = cloudrunv2.JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=whatup_salt_secret.name,
        version="latest",
    )
)

db_secret_manager_perm = secretmanager.SecretIamMember(
    "whatupcore-rmburners-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["whatupcore"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = cloudrunv2.JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_url_secrets["whatupcore"].name,
        version="latest",
    ),
)

anon_key_secret_manager_perm = secretmanager.SecretIamMember(
    "wuc-rmburners-anon-key-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatup_anon_key_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

whatup_anon_key_secret_source = cloudrunv2.JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=whatup_anon_key_secret.name,
        version="latest",
    )
)

whatupcore2_rmburners_job = Job(
    service_name,
    JobArgs(
        args=["remove-burners"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="PRIVATE_RANGES_ONLY",
        image=whatupcore2_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        subnet=cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        memory="1Gi",
        service_account=service_account,
        envs=[
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="ENC_KEY_SALT",
                value_source=whatup_salt_secret_source,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="ANON_KEY",
                value_source=whatup_anon_key_secret_source,
            ),
        ],
        timeout="3600s",
    ),
    opts=ResourceOptions(
        depends_on=[
            salt_secret_manager_perm,
            db_secret_manager_perm,
        ],
    ),
)
