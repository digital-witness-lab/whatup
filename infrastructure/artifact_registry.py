from typing import Optional

import pulumi_docker as docker
from pulumi import Output, export, get_stack
from pulumi_gcp import artifactregistry

from config import location, project

repository = artifactregistry.Repository(
    "whatup-repo",
    repository_id=f"whatup-{get_stack()}-repo",
    description="Repository for whatup container image",
    format="DOCKER",
    location=location,
)

repository_url = Output.concat(
    location,
    "-docker.pkg.dev/",
    project,
    "/",
    repository.repository_id,
)


def create_image(
    image_name: str, app_path: str, build_args: Optional[dict] = None
) -> docker.Image:
    image = docker.Image(
        f"{image_name}-{get_stack()}-img",
        image_name=Output.concat(repository_url, "/", image_name),
        build=docker.DockerBuildArgs(
            context=app_path,
            builder_version=docker.BuilderVersion.BUILDER_BUILD_KIT,
            platform="linux/amd64",
            args={
                # There is a cache bug in the Docker provider
                # that causes the provider to reuse an image
                # digest that was built for a different
                # location.
                "ENVIRONMENT": get_stack(),
                **(build_args or {}),
            },
        ),
    )
    docker.Tag(
        image_name,
        target_image=f"whatup/{image_name}",
        source_image=image.base_image_name,
    )
    export(image_name, image.repo_digest)
    return image


configure_vm_secrets_image: docker.Image = create_image(
    "configure-vm-secrets", "../configure-vm-secrets/"
)

configure_vm_build_args = {
    "CONFIGURE_VM_SECRETS_REPO": configure_vm_secrets_image.image_name
}
export("vm_secrets_name", configure_vm_secrets_image.image_name)

whatupy_image: docker.Image = create_image(
    "whatupy", "../whatupy/", build_args=configure_vm_build_args
)
whatupcore2_image: docker.Image = create_image(
    "whatupcore2", "../whatupcore2/", build_args=configure_vm_build_args
)
migrations_image: docker.Image = create_image("migrations", "../migrations/")
bq_init_schema_image: docker.Image = create_image(
    "bq-init-schema", "../bq-init-schema/"
)

hash_gen_image: docker.Image = create_image(
    "hash-gen", "../hash-gen/"
)