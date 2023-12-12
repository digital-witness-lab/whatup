import pulumi_docker as docker
from pulumi import get_stack, Output
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


def create_image(image_name, app_path) -> docker.Image:
    return docker.Image(
        image_name + "-img",
        image_name=Output.concat(repository_url, "/", image_name),
        build=docker.DockerBuildArgs(
            context=app_path,
            platform="linux/amd64",
            args={
                # There is a cache bug in the Docker provider
                # that causes the provider to reuse an image
                # digest that was built for a different
                # location.
                "LOCATION": location
            },
        ),
        # opts=child_opts, // IS THIS NEEDED??
    )


whatupy_image: docker.Image = create_image("whatupy", "../whatupy/")
whatupcore2_image: docker.Image = create_image(
    "whatupcore2", "../whatupcore2/"
)
migrations_image: docker.Image = create_image("migrations", "../migrations/")
bq_init_schema_image: docker.Image = create_image(
    "bq-init-schema", "../bq-init-schema/"
)
