from pulumi import Output, ResourceOptions, get_stack, log
from pulumi_gcp import secretmanager, serviceaccount
from pulumi_google_native import compute

from artifact_registry import photo_cop_image
from config import is_prod_stack
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
)
from dwl_secrets import photodna_api_key_secret
from network import private_services_network_with_db
from whatupcore_network import (
    ssl_cert_pem_secret,
    ssl_private_key_pem_secret,
    whatupcore2_static_private_ip,
)

service_name = "photo-cop"
port = 50051
photo_cop_addr = Output("")

if photodna_api_key_secret is not None:
    service_account = serviceaccount.Account(
        "photo-cop",
        account_id=f"photo-cop-vm-{get_stack()}",
        description=f"Service account for {service_name}",
    )

    photodna_api_key_perm = secretmanager.SecretIamMember(
        "photo-cop-photodna-api-key-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=photodna_api_key_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )

    photo_cop_service = ContainerOnVm(
        service_name,
        ContainerOnVmArgs(
            automatic_static_private_ip=False,
            private_address=whatupcore2_static_private_ip,
            tcp_healthcheck_port=3447,
            container_spec=Container(
                command=None,
                args=[],
                image=photo_cop_image.repo_digest,
                env=[
                    ContainerEnv(
                        name="PHOTO_COP_PORT",
                        value=str(port),
                    ),
                ],
            ),
            secret_env=[
                compute.v1.MetadataItemsItemArgs(
                    key="PHOTODNA_API_KEY",
                    value=Output.concat(
                        photodna_api_key_secret.id, "/versions/latest"
                    ),
                ),
            ],
            service_account_email=service_account.email,
            subnet=private_services_network_with_db.self_link,
        ),
        opts=ResourceOptions(),
    )

    photo_cop_addr = photo_cop_service.get_host().apply(
        lambda host: f"{host}:{port}"
    )
