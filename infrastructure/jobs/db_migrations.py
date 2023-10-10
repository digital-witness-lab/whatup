from os import path

from pulumi import Output, ResourceOptions

from pulumi_gcp import serviceaccount, cloudrunv2, secretmanager
from pulumi_gcp.cloudrunv2 import (
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)  # noqa: E501

from job import JobArgs, Job
from network import vpc, private_services_network_with_db
from dwl_secrets import messages_db_root_pass_secret
from database import primary_cloud_sql_instance

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
        secret_id=messages_db_root_pass_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_root_pass_secret_source = JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=messages_db_root_pass_secret.name,
        version="latest",
    )
)

db_migrations_job = Job(
    job_name,
    JobArgs(
        app_path=app_path,
        args=["/run_migrations.sh"],
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
                name="DATABASE_USER",
                value="root",
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE_ROOT_PASSWORD",
                value_source=db_root_pass_secret_source,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE_HOST",
                value=primary_cloud_sql_instance.private_ip_address,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="DATABASE",
                value="messages",
            ),
        ],
        timeout="60s",
    ),
    opts=ResourceOptions(depends_on=secret_manager_perm),
)
