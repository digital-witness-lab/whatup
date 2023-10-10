from os import path

from pulumi import Output, ResourceOptions

from pulumi_gcp import serviceaccount, cloudrunv2, secretmanager
from pulumi_gcp.cloudrunv2 import (
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from job import JobArgs, Job
from network import vpc, private_services_network_with_db
from dwl_secrets import messages_db_root_url_secret

job_name = "db-migrations"
app_path = path.join("..", "migrations")

service_account = serviceaccount.Account(
    "dbMigrations",
    account_id="db-migrations",
    description=f"Service account for {job_name}",
)

secret_manager_perm = secretmanager.SecretIamMember(
    "dbMigrationsSecretsAccess",
    secretmanager.SecretIamMemberArgs(
        secret_id=messages_db_root_url_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_url_secret_source = JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=messages_db_root_url_secret.name,
        version="latest",
    )
)

db_migrations_job = Job(
    job_name,
    JobArgs(
        app_path=app_path,
        args=["/migrations/run_migrations.sh"],
        concurrency=1,
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image_name=job_name,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network_with_db.id
        ),
        envs=[
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE_URL",
                value_source=db_url_secret_source,
            ),
        ],
        timeout="60s",
    ),
    opts=ResourceOptions(depends_on=secret_manager_perm),
)
