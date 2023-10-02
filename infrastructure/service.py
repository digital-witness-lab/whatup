import hashlib
from typing import List, Optional
from attr import dataclass
from pulumi import ComponentResource, Config, ResourceOptions, Output

import pulumi_docker as docker
from pulumi_gcp import cloudrunv2, serviceaccount
from pulumi_gcp import artifactregistry


gcp_config = Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")


@dataclass
class ServiceArgs:
    """
    Args for creating a CloudRun service.

    Possible values for `ingress` are:
        - `INGRESS_TRAFFIC_ALL`
        - `INGRESS_TRAFFIC_INTERNAL_ONLY`
        - `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`
    """

    app_path: str
    commands: List[str]
    concurrency: int
    container_port: int
    cpu: int
    envs: Optional[List[cloudrunv2.ServiceTemplateContainerEnvArgs]]
    image_name: str
    ingress: str
    memory: str
    service_account: serviceaccount.Account


class Service(ComponentResource):
    """
    Creates a CloudRun service accessible only within
    the VPC network.
    """

    def __init__(
        self,
        name: str,
        props: Optional[ServiceArgs] = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__("dwl:cloudrun:Service", name, props, opts)

        child_opts = ResourceOptions(parent=self)

        # Create an Artifact Registry repository
        repository = artifactregistry.Repository(
            props.image_name + "-repo",
            description=f"Repository for {props.image_name} container image",
            format="DOCKER",
            location=location,
            opts=child_opts,
        )

        # Form the repository URL
        repo_url = Output.concat(
            location, "-docker.pkg.dev/", project, "/", repository.repository_id
        )

        # Create a container image for the service.
        # Before running `pulumi up`, configure Docker for Artifact Registry authentication
        # as described here: https://cloud.google.com/artifact-registry/docs/docker/authentication
        image = docker.Image(
            "image",
            image_name=Output.concat(repo_url, "/", props.image_name),
            build=docker.DockerBuildArgs(
                context=props.app_path,
                platform="linux/amd64",
            ),
            opts=child_opts,
        )

        # Create a Cloud Run service definition.
        service = cloudrunv2.Service(
            f"{name}-service",
            cloudrunv2.ServiceArgs(
                location=location,
                ingress=props.ingress,
                template=cloudrunv2.ServiceTemplateArgs(
                    scaling=cloudrunv2.ServiceTemplateScalingArgs(
                        min_instance_count=1, max_instance_count=3
                    ),
                    containers=[
                        cloudrunv2.ServiceTemplateContainerArgs(
                            commands=props.commands,
                            image=image.image_name,
                            resources=cloudrunv2.ServiceTemplateContainerResourcesArgs(
                                limits=dict(
                                    memory=props.memory,
                                    cpu=props.cpu,
                                ),
                            ),
                            ports=[
                                cloudrunv2.ServiceTemplateContainerPortArgs(
                                    # This enables end-to-end HTTP/2 (gRPC)
                                    # as described in:
                                    # https://cloud.google.com/run/docs/configuring/http2
                                    name="h2c",
                                    container_port=props.container_port,
                                ),
                            ],
                            envs=props.envs,
                        ),
                    ],
                    max_instance_request_concurrency=props.concurrency,
                    service_account=props.service_account.email,
                ),
            ),
            opts=child_opts,
        )

        self.add_invoke_permission(service)

        super().register_outputs({})

    def add_invoke_permission(
        self, service: cloudrunv2.Service, service_account_email: str
    ):
        # We just want a random suffix not used for security purposes,
        # so it's ok to use MD5 here.
        md5 = hashlib.md5()
        md5.update(service_account_email.encode("utf-8"))
        # Create an IAM member to make the service publicly accessible.
        invoker = cloudrunv2.ServiceIamMember(
            f"invoker-{md5.hexdigest()[:6]}",
            cloudrunv2.ServiceIamMemberArgs(
                location=location,
                name=service.name,
                role="roles/run.invoker",
                member=f"serviceAccount:{service_account_email}",
            ),
            opts=ResourceOptions(parent=self),
        )
