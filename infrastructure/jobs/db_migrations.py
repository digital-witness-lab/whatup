from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, secretmanager, serviceaccount
from pulumi_gcp.cloudrunv2 import (  # noqa: E501
    JobTemplateTemplateContainerEnvValueSourceArgs,
    JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs,
)

from artifact_registry import migrations_image
from database import db_configs, primary_cloud_sql_instance
from dwl_secrets import db_root_pass_secret
from job import Job, JobArgs
from network import private_services_network_with_db, vpc

from .execute_job import run_job_sync

job_name = "db-migrations"

service_account = serviceaccount.Account(
    "db-migrations",
    account_id=f"db-migrations-{get_stack()}",
    description=f"Service account for {job_name}",
)

secret_manager_perm = secretmanager.SecretIamMember(
    "db-mig-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_root_pass_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

db_root_pass_secret_source = JobTemplateTemplateContainerEnvValueSourceArgs(
    secret_key_ref=JobTemplateTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=db_root_pass_secret.name,
        version="latest",
    )
)

db_migrations_job = Job(
    job_name,
    JobArgs(
        args=["/run_migrations.sh"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=migrations_image,
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
                value="postgres",
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
                name="DATABASES",
                value=",".join(db_configs.keys()),
            ),
        ],
        timeout="60s",
    ),
    opts=ResourceOptions(depends_on=secret_manager_perm),
)

migrations_job_complete = Output.apply(
    db_migrations_job.job.name,
    lambda job_name: run_job_sync(job_name, 120),
)
