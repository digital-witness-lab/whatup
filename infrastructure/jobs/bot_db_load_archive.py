from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import secretmanager, serviceaccount, storage
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
    SharedCoreMachineType,
)
from pulumi_google_native import compute

from artifact_registry import whatupy_image
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from network import private_services_network_with_db
from storage import media_bucket, message_archive_bucket
from config import is_prod_stack, load_archive_job

service_name = "bot-db-load-archive"

service_account = serviceaccount.Account(
    "db-load-archive",
    account_id=f"bot-db-load-archive-{get_stack()}",
    description=f"Service account for {service_name}",
)

message_archive_bucket_perm = storage.BucketIAMMember(
    "db-ld-archive-arch-perm",
    storage.BucketIAMMemberArgs(
        bucket=message_archive_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectViewer",
    ),
)

media_bucket_perm = storage.BucketIAMMember(
    "db-ld-media-perm",
    storage.BucketIAMMemberArgs(
        bucket=media_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "db-ld-archive-scrt-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["messages"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

machine_type = SharedCoreMachineType.E2Small
num_tasks = 4
if is_prod_stack():
    machine_type = SharedCoreMachineType.E2HighMem8
    num_tasks = 36
n_instances = 1 if load_archive_job else 0

db_migrations_vm = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=False,
        machine_type=machine_type,
        is_spot=True,
        n_instances=n_instances,
        restart_policy="Never",
        container_spec=Container(
            args=["/usr/src/whatupy/run.sh", "load-archive"],
            image=whatupy_image.repo_digest,
            env=[
                ContainerEnv(name="ARCHIVE_FILTER", value="."),
                ContainerEnv(name="NUM_TASKS", value=str(num_tasks)),
                ContainerEnv(
                    name="MESSAGE_ARCHIVE_BUCKET",
                    value=message_archive_bucket.name,
                ),
                ContainerEnv(
                    name="MEDIA_BUCKET",
                    value=media_bucket.name,
                ),
                ContainerEnv(
                    name="WHATUPY_RUN_NAME",
                    value="post-device-group-info",
                ),
                # Create an implicit dependency on the migrations
                # job completing successfully.
                ContainerEnv(
                    name="MIGRATIONS_JOB_COMPLETE",
                    value=migrations_job_complete.apply(lambda b: f"{b}"),
                ),
            ],
        ),
        secret_env=[
            compute.v1.MetadataItemsItemArgs(
                key="DATABASE_URL",
                value=Output.concat(
                    db_url_secrets["messages"].id, "/versions/latest"
                ),
            ),
        ],
        service_account_email=service_account.email,
        subnet=private_services_network_with_db.self_link,
    ),
    opts=ResourceOptions(
        depends_on=[
            message_archive_bucket_perm,
            media_bucket_perm,
        ]
    ),
)
