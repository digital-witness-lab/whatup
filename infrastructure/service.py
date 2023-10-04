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
    """

    app_path: str
    commands: List[str]
    concurrency: int
    container_port: int
    cpu: str
    # Possible values are: `ALL_TRAFFIC`, `PRIVATE_RANGES_ONLY`.
    egress: str
    image_name: str
    # Possible values for `ingress` are:
    # - `INGRESS_TRAFFIC_ALL`
    # - `INGRESS_TRAFFIC_INTERNAL_ONLY`
    # - `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`
    ingress: str
    memory: str
    service_account: serviceaccount.Account
    # Specify the subnet to use Direct VPC egress instead of
    # serverless VPC connectors for outbound traffic from
    # this service.
    subnet: cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs

    envs: Optional[List[cloudrunv2.ServiceTemplateContainerEnvArgs]]


class Service(ComponentResource):
    """
    Creates a CloudRun service accessible only within
    the VPC network.
    """

    def __init__(
        self,
        name: str,
        props: ServiceArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__("dwl:cloudrun:Service", name, props.__dict__, opts)

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
            location,
            "-docker.pkg.dev/",
            project,
            "/",
            repository.repository_id,
        )

        # Create a container image for the service.
        # Before running `pulumi up`, configure Docker for
        # Artifact Registry authentication.
        # as described here:
        # https://cloud.google.com/artifact-registry/docs/docker/authentication
        image = docker.Image(
            "image",
            image_name=Output.concat(repo_url, "/", props.image_name),
            build=docker.DockerBuildArgs(
                context=props.app_path,
                platform="linux/amd64",
            ),
            opts=child_opts,
        )

        resources = cloudrunv2.ServiceTemplateContainerResourcesArgs(
            limits=dict(
                memory=props.memory,
                cpu=props.cpu,
            ),
        )

        # Create a Cloud Run service definition.
        self._service = cloudrunv2.Service(
            f"{name}-service",
            cloudrunv2.ServiceArgs(
                location=location,
                ingress=props.ingress,
                template=cloudrunv2.ServiceTemplateArgs(
                    scaling=cloudrunv2.ServiceTemplateScalingArgs(
                        min_instance_count=1, max_instance_count=3
                    ),
                    vpc_access=cloudrunv2.ServiceTemplateVpcAccessArgs(
                        egress=props.egress, network_interfaces=[props.subnet]
                    ),
                    containers=[
                        cloudrunv2.ServiceTemplateContainerArgs(
                            commands=props.commands,
                            image=image.image_name,
                            resources=resources,
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

        super().register_outputs({})

    @property
    def service(self):
        return self._service

    def add_invoke_permission(
        self, service: cloudrunv2.Service, service_account_email: str
    ):
        # We just want a random suffix not used for security purposes,
        # so it's ok to use MD5 here. The random suffix is needed here
        # since this method will create many resources and each of them
        # needs to have a unique Pulumi resource name.
        md5 = hashlib.md5()
        md5.update(service_account_email.encode("utf-8"))
        # Create an IAM member to make the service publicly accessible.
        cloudrunv2.ServiceIamMember(
            f"invoker-{md5.hexdigest()[:6]}",
            cloudrunv2.ServiceIamMemberArgs(
                location=location,
                name=service.name,
                role="roles/run.invoker",
                member=f"serviceAccount:{service_account_email}",
            ),
            opts=ResourceOptions(parent=self),
        )
