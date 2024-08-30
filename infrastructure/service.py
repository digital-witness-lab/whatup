import hashlib
import warnings
from typing import List, Optional, Literal

import pulumi_docker as docker
from attr import dataclass, field
from pulumi import ComponentResource, Output, ResourceOptions
from pulumi_gcp import cloudrunv2, serviceaccount

from config import is_prod_stack, location
from network_firewall import firewall_policy


@dataclass
class ServiceArgs:
    """
    Args for creating a CloudRun service.
    """

    # This is passed to the ENTRYPOINT defined in the Dockerfile.
    args: List[str]
    concurrency: int
    container_port: Optional[int]
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
    public_access: bool
    service_account: serviceaccount.Account
    # Specify the subnet to use Direct VPC egress instead of
    # serverless VPC connectors for outbound traffic from
    # this service.
    subnet: Optional[
        cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs
    ] = field(default=None)

    request_timeout: int = field(default=60 * 60)
    protocol: Literal["h2c", "http1"] = field(default="h2c")

    envs: Optional[List[cloudrunv2.ServiceTemplateContainerEnvArgs]] = field(
        default=None
    )


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

        # Disallow services with open public access accepting ingress from
        # the internet. We do not expect to have such services deployed
        # via this component resource at this time.
        if props.ingress == "INGRESS_TRAFFIC_ALL" and props.public_access:
            warnings.warn(
                f"Public access with direct ingress traffic from the internet is dangerous: {name}",
            )

        child_opts = ResourceOptions(parent=self)

        containers = self.get_containers(props)

        # Create a Cloud Run service definition.
        self._service = cloudrunv2.Service(
            f"{name}-svc",
            cloudrunv2.ServiceArgs(
                location=location,
                # Set the launch stage to BETA since
                # we want to use the Preview feature
                # "Direct VPC Access".
                # https://cloud.google.com/run/docs/configuring/vpc-direct-vpc
                launch_stage="BETA",
                ingress=props.ingress,
                annotations={"namespace": f"{name}-svc"},
                template=cloudrunv2.ServiceTemplateArgs(
                    scaling=cloudrunv2.ServiceTemplateScalingArgs(
                        min_instance_count=1, max_instance_count=1
                    ),
                    timeout=f"{props.request_timeout}s",  # 1hr is the max time allowed by cloudrun
                    vpc_access=cloudrunv2.ServiceTemplateVpcAccessArgs(
                        egress=props.egress,
                        network_interfaces=(
                            [props.subnet] if props.subnet else None
                        ),
                    ),
                    # https://cloud.google.com/run/docs/configuring/execution-environments#yaml
                    # Read about the differences between gen1 and gen2
                    # and choose the most appropriate value.
                    # https://cloud.google.com/run/docs/about-execution-environments#choose
                    execution_environment="EXECUTION_ENVIRONMENT_GEN1",
                    containers=containers,
                    max_instance_request_concurrency=props.concurrency,
                    service_account=props.service_account.email,
                ),
                traffics=[
                    cloudrunv2.ServiceTrafficArgs(
                        type="TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST",
                        percent=100,
                    )
                ],
            ),
            opts=ResourceOptions.merge(
                child_opts, ResourceOptions(depends_on=firewall_policy)
            ),
        )

        # Grant public, unauthenticated access to this service.
        # Since the services are marked with an ingress of
        # internal-only traffic, these are not allowed to be
        # called from the internet anyway. Moreover, the
        # services themselves require authentication, so
        # they are not exactly "anonymous". But marking
        # them as anonymous in GCP makes some things
        # easier to use our own auth.
        cloudrunv2.ServiceIamMember(
            f"{name}-public-access",
            cloudrunv2.ServiceIamMemberArgs(
                location=location,
                name=self._service.name,
                role="roles/run.invoker",
                member="allUsers",
            ),
            opts=child_opts,
        )

        super().register_outputs({})

    @property
    def service(self):
        return self._service

    def get_url(self) -> Output[str]:
        return self._service.uri

    def get_host(self) -> Output[str]:
        return Output.apply(
            self._service.uri,
            lambda u: u.replace("https://", ""),
        )

    def get_containers(self, props: ServiceArgs):
        containers: List[cloudrunv2.ServiceTemplateContainerArgs] = []

        # If a container port was not provided, we assume
        # that the main container image we want to run
        # does not run an HTTP server.
        #
        # Run a simple container that can serve HTTP traffic
        # to make the startup probes of CloudRun happy.
        if props.container_port is None:
            nginx_resources = cloudrunv2.ServiceTemplateContainerResourcesArgs(
                limits=dict(
                    memory="512Mi",
                    cpu="0.5",
                ),
            )
            simple_hello_container = cloudrunv2.ServiceTemplateContainerArgs(
                image="nginxdemos/nginx-hello:0.2",
                resources=nginx_resources,
                ports=[
                    cloudrunv2.ServiceTemplateContainerPortArgs(
                        name="http1",
                        container_port=8080,
                    ),
                ],
            )
            containers.append(simple_hello_container)

        resources = cloudrunv2.ServiceTemplateContainerResourcesArgs(
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
        containers.append(
            cloudrunv2.ServiceTemplateContainerArgs(
                args=props.args,
                image=props.image.repo_digest,
                resources=resources,
                startup_probe=(
                    cloudrunv2.ServiceTemplateContainerStartupProbeArgs(  # noqa: E501
                        failure_threshold=1,
                        initial_delay_seconds=60,
                        timeout_seconds=20,
                        tcp_socket=cloudrunv2.ServiceTemplateContainerStartupProbeTcpSocketArgs(),  # noqa: E501
                    )
                    if props.container_port is not None
                    else None
                ),
                ports=(
                    [
                        cloudrunv2.ServiceTemplateContainerPortArgs(
                            # This enables end-to-end HTTP/2 (gRPC)
                            # as described in:
                            # https://cloud.google.com/run/docs/configuring/http2
                            name=props.protocol,
                            container_port=props.container_port,
                        ),
                    ]
                    if props.container_port is not None
                    else None
                ),
                envs=envs,
            ),
        )
        return containers

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
                member=Output.concat("serviceAccount:", service_account_email),
            ),
            opts=ResourceOptions(parent=self),
        )
