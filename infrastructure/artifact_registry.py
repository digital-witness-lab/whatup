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


def create_image(image_name, app_path) -> docker.Image:
    return docker.Image(
        f"{image_name}-{get_stack()}-img",
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
