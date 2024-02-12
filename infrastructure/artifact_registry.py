from typing import Optional
from pulumi import export
import pulumi_docker as docker
from pulumi import Output, get_stack
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
    image_name: str, app_path: str, dockerfile_path: Optional[str] = None
) -> docker.Image:
    image = docker.Image(
        f"{image_name}-{get_stack()}-img",
        image_name=Output.concat(repository_url, "/", image_name),
        build=docker.DockerBuildArgs(
            context=app_path,
            dockerfile=dockerfile_path,
            platform="linux/amd64",
            args={
                # There is a cache bug in the Docker provider
                # that causes the provider to reuse an image
                # digest that was built for a different
                # location.
                "ENVIRONMENT": get_stack()
            },
        ),
    )
    export(image_name, image.repo_digest)
    return image


whatupy_image: docker.Image = create_image(
    "whatupy", "../", "../whatupy/Dockerfile"
)
whatupcore2_image: docker.Image = create_image(
    "whatupcore2", "../", "../whatupcore2/Dockerfile"
)
migrations_image: docker.Image = create_image("migrations", "../migrations/")
bq_init_schema_image: docker.Image = create_image(
    "bq-init-schema", "../bq-init-schema/"
)
