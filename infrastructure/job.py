from typing import List, Optional
from attr import dataclass

from pulumi import ComponentResource, Output, ResourceOptions
import pulumi_docker as docker
from pulumi_gcp import artifactregistry, cloudrunv2, serviceaccount

from .config import location, project


@dataclass
class JobArgs:
    """
    Args for creating a CloudRun job.
    """

    app_path: str
    # This is passed to the ENTRYPOINT defined in the Dockerfile.
    args: List[str]
    concurrency: int
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
    subnet: cloudrunv2.JobTemplateTemplateVpcAccessNetworkInterfaceArgs
    # A duration in seconds with up to nine fractional digits,
    # ending with 's'. Example: "3.5s".
    timeout: str

    envs: Optional[List[cloudrunv2.JobTemplateTemplateContainerEnvArgs]]


class Job(ComponentResource):
    def __init__(
        self,
        name: str,
        props: JobArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__("dwl:cloudrun:Job", name, props.__dict__, opts)

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

        resources = cloudrunv2.JobTemplateTemplateContainerResourcesArgs(
            limits=dict(
                memory=props.memory,
                cpu=props.cpu,
            ),
        )

        template = cloudrunv2.JobTemplateTemplateArgs(
            service_account=props.service_account.email,
            max_retries=1,
            containers=[
                cloudrunv2.JobTemplateTemplateContainerArgs(
                    args=props.args,
                    image=image.image_name,
                    resources=resources,
                    envs=props.envs,
                ),
            ],
            timeout=props.timeout,
            vpc_access=cloudrunv2.JobTemplateTemplateVpcAccessArgs(
                egress=props.egress, network_interfaces=[props.subnet]
            ),
        )
        self._job = cloudrunv2.Job(
            f"{name}Job",
            cloudrunv2.JobArgs(
                location=location,
                template=cloudrunv2.JobTemplateArgs(template=template),
            ),
            opts=child_opts,
        )

        super().register_outputs({})

    @property
    def job(self):
        return self._job
