from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import cloudrunv2, kms, secretmanager, serviceaccount, storage

from artifact_registry import whatupy_image
from job import Job, JobArgs
from kms import sessions_encryption_key, sessions_encryption_key_uri
from network import private_services_network, vpc
from services.whatupcore2 import whatupcore2_service
from storage import sessions_bucket
from whatupcore_network import whatupcore_tls_cert

service_name = "bot-onboard"

service_account = serviceaccount.Account(
    "onboard",
    account_id=f"bot-onboard-{get_stack()}",
    description=f"Service account for {service_name}",
)

sessions_bucket_perm = storage.BucketIAMMember(
    "onboard-sess-perm",
    storage.BucketIAMMemberArgs(
        bucket=sessions_bucket.name,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/storage.objectAdmin",
    ),
)

encryption_key_perm = kms.CryptoKeyIAMMember(
    "onboard-bot-enc-key-perm",
    kms.CryptoKeyIAMMemberArgs(
        crypto_key_id=sessions_encryption_key.id,
        member=Output.concat("serviceAccount:", service_account.email),
        role="roles/cloudkms.cryptoKeyEncrypterDecrypter",
    ),
)

ssl_cert_pem_b64_secret_perm = secretmanager.SecretIamMember(
    "onboard-bot-ssl-cert-secret-perm",
    secretmanager.SecretIamMemberArgs(
        secret_id=whatupcore_tls_cert.cert_b64_secret.id,
        role="roles/secretmanager.secretAccessor",
        member=Output.concat("serviceAccount:", service_account.email),
    ),
)
ssl_cert_pem_b64_source = cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
    secret_key_ref=cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
        secret=whatupcore_tls_cert.cert_b64_secret.name,
        version="latest",
    ),
)

bot_onboard_bulk_job = Job(
    service_name,
    JobArgs(
        args=["/usr/src/whatupy/run.sh", "onboard"],
        cpu="1",
        # Route all egress traffic via the VPC network.
        egress="ALL_TRAFFIC",
        image=whatupy_image,
        # We want this service to only be reachable from within
        # our VPC network.
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",
        memory="1Gi",
        service_account=service_account,
        # Specifying the subnet causes CloudRun to use
        # Direct VPC egress for outbound traffic based
        # on the value of the `egress` property above.
        subnet=cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs(
            network=vpc.id, subnetwork=private_services_network.id
        ),
        envs=[
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="WHATUP_CERT_PEM_B64",
                value_source=ssl_cert_pem_b64_source,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="KEK_URI",
                value=sessions_encryption_key_uri,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="SESSIONS_BUCKET",
                value=sessions_bucket.name,
            ),
            cloudrunv2.JobTemplateTemplateContainerEnvArgs(
                name="WHATUPCORE2_HOST",
                value=whatupcore2_service.get_host(),
            ),
        ],
        timeout="3600s",
    ),
    opts=ResourceOptions(
        depends_on=[sessions_bucket_perm, encryption_key_perm]
    ),
)
