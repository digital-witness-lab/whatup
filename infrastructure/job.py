from typing import List, Optional
from attr import dataclass, field

from pulumi import ComponentResource, ResourceOptions
import pulumi_docker as docker
from pulumi_gcp import cloudrunv2, serviceaccount

from config import location, is_prod_stack
from network_firewall import firewall_policy


@dataclass
class JobArgs:
    """
    Args for creating a CloudRun job.
    """

    # This is passed to the ENTRYPOINT defined in the Dockerfile.
    args: List[str]
    cpu: str
    # Possible values are: `ALL_TRAFFIC`, `PRIVATE_RANGES_ONLY`.
    egress: str
    image: docker.Image
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

    task_count: Optional[int] = field(default=None)
    envs: Optional[
        List[cloudrunv2.JobTemplateTemplateContainerEnvArgs]
    ] = field(default=None)


class Job(ComponentResource):
    def __init__(
        self,
        name: str,
        props: JobArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__("dwl:cloudrun:Job", name, props.__dict__, opts)

        child_opts = ResourceOptions(parent=self)

        resources = cloudrunv2.JobTemplateTemplateContainerResourcesArgs(
            limits=dict(
                memory=props.memory,
                cpu=props.cpu,
            ),
        )

        envs = [
            cloudrunv2.ServiceTemplateContainerEnvArgs(
                name="IS_PROD",
                value="True" if is_prod_stack() else "False",
            ),
            *(props.envs or []),
        ]
        template = cloudrunv2.JobTemplateTemplateArgs(
            service_account=props.service_account.email,
            max_retries=1,
            containers=[
                cloudrunv2.JobTemplateTemplateContainerArgs(
                    args=props.args,
                    image=props.image.repo_digest,
                    resources=resources,
                    envs=envs,
                ),
            ],
            timeout=props.timeout,
            vpc_access=cloudrunv2.JobTemplateTemplateVpcAccessArgs(
                egress=props.egress, network_interfaces=[props.subnet]
            ),
        )
        self._job = cloudrunv2.Job(
            f"{name}-job",
            cloudrunv2.JobArgs(
                # Set the launch stage to BETA since
                # we want to use the Preview feature
                # "Direct VPC Access".
                # https://cloud.google.com/run/docs/configuring/vpc-direct-vpc
                launch_stage="BETA",
                location=location,
                template=cloudrunv2.JobTemplateArgs(
                    template=template,
                    task_count=props.task_count,
                ),
            ),
            opts=ResourceOptions.merge(
                child_opts, ResourceOptions(depends_on=firewall_policy)
            ),
        )

        super().register_outputs({})

    @property
    def job(self):
        return self._job
