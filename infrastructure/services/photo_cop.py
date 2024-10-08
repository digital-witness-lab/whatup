from pulumi import Output, ResourceOptions, get_stack
from pulumi_gcp import secretmanager, serviceaccount
from pulumi_google_native import compute

from artifact_registry import photo_cop_image
from container_vm import (
    Container,
    ContainerEnv,
    ContainerOnVm,
    ContainerOnVmArgs,
)
from dwl_secrets import photo_dna_api_key_secret
from network import private_services_network_with_db
from whatupcore_network import (
    photocop_tls_cert,
    photocop_static_private_ip,
)

service_name = "photo-cop"
photo_cop_service = None

if photo_dna_api_key_secret is not None:
    service_account = serviceaccount.Account(
        "photo-cop",
        account_id=f"photo-cop-vm-{get_stack()}",
        description=f"Service account for {service_name}",
    )

    tls_private_key_pem_perm = secretmanager.SecretIamMember(
        "photocop-tls-pk-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=photocop_tls_cert.key_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )

    tls_cert_pem_perm = secretmanager.SecretIamMember(
        "photocop-tls-cert-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=photocop_tls_cert.cert_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )

    photodna_api_key_perm = secretmanager.SecretIamMember(
        "photo-cop-photodna-api-key-perm",
        secretmanager.SecretIamMemberArgs(
            secret_id=photo_dna_api_key_secret.id,
            role="roles/secretmanager.secretAccessor",
            member=Output.concat("serviceAccount:", service_account.email),
        ),
    )

    photo_cop_service = ContainerOnVm(
        service_name,
        ContainerOnVmArgs(
            automatic_static_private_ip=False,
            private_address=photocop_static_private_ip,
            tcp_healthcheck_port=3447,
            container_spec=Container(
                command=None,
                args=[],
                image=photo_cop_image.repo_digest,
                env=[
                    ContainerEnv(
                        name="PHOTOCOP_TLS_CERT",
                        value="/run/secrets/PHOTOCOP_CERT_PEM",
                    ),
                    ContainerEnv(
                        name="PHOTOCOP_TLS_KEY",
                        value="/run/secrets/PHOTOCOP_KEY_PEM",
                    ),
                ],
            ),
            secret_env=[
                compute.v1.MetadataItemsItemArgs(
                    key="PHOTODNA_API_KEY",
                    value=Output.concat(
                        photo_dna_api_key_secret.id, "/versions/latest"
                    ),
                ),
                compute.v1.MetadataItemsItemArgs(
                    key="PHOTOCOP_KEY_PEM",
                    value=Output.concat(
                        photocop_tls_cert.key_secret.id, "/versions/latest"
                    ),
                ),
                compute.v1.MetadataItemsItemArgs(
                    key="PHOTOCOP_CERT_PEM",
                    value=Output.concat(
                        photocop_tls_cert.cert_secret.id, "/versions/latest"
                    ),
                ),
            ],
            service_account_email=service_account.email,
            subnet=private_services_network_with_db.self_link,
        ),
        opts=ResourceOptions(),
    )
