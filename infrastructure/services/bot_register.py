from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import kms, secretmanager, serviceaccount, storage
from pulumi_google_native import compute

from artifact_registry import whatupy_image
from dwl_secrets import db_url_secrets
from jobs.db_migrations import migrations_job_complete
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network_with_db
from storage import sessions_bucket
from config import primary_bot_name, control_groups
from container_vm import (
    ContainerOnVm,
    ContainerOnVmArgs,
    Container,
    ContainerEnv,
    SharedCoreMachineType,
    ContainerSecurityContext,
)

from .whatupcore2 import whatupcore2_service, ssl_cert_pem_secret

service_name = "bot-register"

service_account = serviceaccount.Account(
    "bot-register",
    account_id=f"whatup-bot-reg-{get_stack()}",
    description=f"Service account for {service_name}",
)

# registerbot needs to be able to write new session files
sessions_bucket_perm = storage.BucketIAMMember(
    "bot-reg-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
        # Condition removed because it wasn't allowing listdir to happen:
        # google.api_core.exceptions.Forbidden: 403 GET
        # https://storage.googleapis.com/storage/v1/b/dwl-sess-706f295/o?maxResults=1&projection=noAcl&prefix=users%2F&prettyPrint=false:
        # whatup-bot-userserv-test@whatup-deploy.iam.gserviceaccount.com does
        # not have storage.objects.list access to the Google Cloud Storage
        # bucket. Permission 'storage.objects.list' denied on resource (or it
        # may not exist).
        # condition=storage.BucketIAMMemberConditionArgs(
        #     title="UsersSubdir",
        #     description="Grants permission to modify objects within the user subdir",
        #     expression=sessions_bucket.name.apply(
        #         lambda name: (
        #             "resource.type == 'storage.googleapis.com/Object' && ("
        #             f"resource.name.startsWith('projects/_/buckets/{name}/objects/users') || "
        #             f"resource.name == 'projects/_/buckets/{name}/objects/{primary_bot_name}.json'"
        #             ")"
        #         )
        #     ),
        # ),
    ),
)

secret_manager_perm = secretmanager.SecretIamMember(
    "bot-reg-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=db_url_secrets["users"].id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)

encryption_key_perm = kms.CryptoKeyIAMMember(
    "bot-reg-enc-key-perm",
    kms.CryptoKeyIAMMemberArgs(
        crypto_key_id=sessions_encryption_key.id,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudkms.cryptoKeyEncrypterDecrypter",
    ),
)

ssl_cert_pem_perm = secretmanager.SecretIamMember(
    "bot-reg-ssl-cert-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=ssl_cert_pem_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)


bot_register = ContainerOnVm(
    service_name,
    ContainerOnVmArgs(
        automatic_static_private_ip=True,
        container_spec=Container(
            command=None,
            args=["/usr/src/whatupy/run.sh", "registerbot"],
            image=whatupy_image.repo_digest,
            tty=False,
            securityContext=ContainerSecurityContext(privileged=False),
            env=[
                ContainerEnv(
                    name="KEK_URI",
                    value=sessions_encryption_key_uri,
                ),
                ContainerEnv(
                    name="SESSIONS_BUCKET",
                    value=sessions_bucket.name,
                ),
                ContainerEnv(
                    name="WHATUPY_CONTROL_GROUPS",
                    value=" ".join(control_groups),
                ),
                ContainerEnv(
                    name="WHATUPCORE2_HOST",
                    value=whatupcore2_service.get_host_output(),
                ),
                ContainerEnv(
                    name="PRIMARY_BOT_NAME",
                    value=primary_bot_name,
                ),
                # Create an implicit dependency on the migrations
                # job completing successfully.
                ContainerEnv(
                    name="MIGRATIONS_JOB_COMPLETE",
                    value=migrations_job_complete.apply(lambda b: f"{b}"),
                ),
            ],
        ),
        machine_type=SharedCoreMachineType.E2Micro,
        restart_policy="Always",
        secret_env=[
            compute.v1.MetadataItemsItemArgs(
                key="DATABASE_URL",
                value=Output.concat(
                    db_url_secrets["users"].id, "/versions/latest"
                ),
            ),
            compute.v1.MetadataItemsItemArgs(
                key="SSL_CERT_PEM",
                value=Output.concat(
                    ssl_cert_pem_secret.id, "/versions/latest"
                ),
            ),
        ],
        subnet=private_services_network_with_db.self_link,
        service_account_email=service_account.email,
    ),
    opts=ResourceOptions(
        depends_on=[
            sessions_bucket_perm,
            encryption_key_perm,
            ssl_cert_pem_perm,
        ]
    ),
)
