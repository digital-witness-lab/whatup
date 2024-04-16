from enum import Enum
from typing import List, Optional

import pulumi
import yaml
from attr import dataclass, field
from google.cloud.compute_v1 import (
    InstanceGroupManagersClient,
    ListManagedInstancesInstanceGroupManagersRequest,
)
from pulumi.resource import ResourceOptions
from pulumi_gcp import compute as classic_gcp_compute
from pulumi_gcp import projects
from pulumi_google_native.compute import v1 as native_compute_v1

from config import project, zone
from gcloud import get_project_number
from network_firewall import firewall_association

startup_script = """
#! /bin/bash
echo "Setting docker log size"
cat <<EOF > /etc/docker/daemon.json
{
    "live-restore": true,
    "log-opts": {
        "tag": "{{.Name}}",
        "max-size": "100m"
    },
    "storage-driver": "overlay2",
    "mtu": 1460
}
EOF
systemctl restart docker
""".strip()


class SharedCoreMachineType(Enum):
    E2Micro = "e2-micro"
    E2Small = "e2-small"
    E2Medium = "e2-medium"
    E2HighMem8 = "e2-highmem-8"


@dataclass
class ContainerEnv(yaml.YAMLObject):
    name: str
    value: pulumi.Input[str]


@dataclass
class ContainerSecurityContext(yaml.YAMLObject):
    privileged: bool


@dataclass
class Container(yaml.YAMLObject):
    """
    The container spec that will be serialized as yaml
    and added as the value for the instance metdata
    property `gce-container-declaration`.
    """

    args: List[str]
    env: List[ContainerEnv]
    image: pulumi.Input[str]
    tty: bool = field(default=False)
    securityContext: ContainerSecurityContext = field(
        default=ContainerSecurityContext(privileged=False)
    )
    command: Optional[List[str]] = field(default=None)


@dataclass
class ContainerSpec(yaml.YAMLObject):
    containers: List[Container]
    restartPolicy: str


@dataclass
class Spec(yaml.YAMLObject):
    spec: ContainerSpec


@dataclass
class ContainerOnVmArgs:
    # The static private IP to assign to the managed instance
    # in the group.
    #
    # Note: Conflicts with `automatic_static_private_ip`.
    container_spec: Container
    machine_type: SharedCoreMachineType
    secret_env: List[native_compute_v1.MetadataItemsItemArgs]
    service_account_email: pulumi.Output[str]
    subnet: pulumi.Output[str]

    is_spot: bool = field(default=False)
    n_instances: int = field(default=1)
    # Flag indicating if you want the instance group to automatically
    # promote any private IP to be a static one.
    #
    # Note: Conflicts with `private_address`.
    automatic_static_private_ip: bool = field(default=False)

    # restart_policy can be one of "Always", "Never", "OnFailure"
    # https://github.com/GoogleCloudPlatform/konlet/blob/a0e73/gce-containers-startup/types/api.go#L23-L27
    restart_policy: str = field(default="Always")
    tcp_healthcheck_port: Optional[int] = field(default=None)
    private_address: Optional[native_compute_v1.Address] = field(default=None)


project_number = get_project_number(project)


class ContainerOnVm(pulumi.ComponentResource):
    __args: ContainerOnVmArgs
    __name: str

    def __init__(
        self, name: str, args: ContainerOnVmArgs, opts: ResourceOptions
    ):
        super().__init__("dwl:gce:ContainerOnVm", name, None, opts)

        if args.automatic_static_private_ip and args.private_address:
            raise Exception(
                "Cannot configure both automatic static private IP AND pass in a static private IP."
            )

        self.__args = args
        self.__name = name

        # Grant access to pull container image from Artifact Registry.
        self.__artifact_registry_perm = projects.IAMMember(
            f"{name}-artifact-reg-perm",
            args=projects.IAMMemberArgs(
                member=pulumi.Output.concat(
                    "serviceAccount:", args.service_account_email
                ),
                role="roles/artifactregistry.reader",
                project=project,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.__logging_perm = projects.IAMMember(
            f"{name}-logging-perm",
            args=projects.IAMMemberArgs(
                member=pulumi.Output.concat(
                    "serviceAccount:", args.service_account_email
                ),
                role="roles/logging.logWriter",
                project=project,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.__monitoring_perm = projects.IAMMember(
            f"{name}-monitoring-perm",
            args=projects.IAMMemberArgs(
                member=pulumi.Output.concat(
                    "serviceAccount:", args.service_account_email
                ),
                role="roles/monitoring.metricWriter",
                project=project,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.__create_instance_template()

        self.__autohealing = None
        if args.tcp_healthcheck_port is not None:
            self.__autohealing = classic_gcp_compute.HealthCheck(
                "autohealing",
                check_interval_sec=5,
                timeout_sec=5,
                healthy_threshold=2,
                unhealthy_threshold=10,
                tcp_health_check=classic_gcp_compute.HealthCheckTcpHealthCheckArgs(
                    port=args.tcp_healthcheck_port,
                ),
                opts=pulumi.ResourceOptions(parent=self),
            )

        self.__create_zonal_instance_group()

        super().register_outputs({})

    def __create_instance_template(self):
        args = self.__args
        name = self.__name

        container_declaration = self.__get_container_declaration(
            args.container_spec, args.restart_policy
        )

        provisioning_model = (
            native_compute_v1.SchedulingProvisioningModel.SPOT
            if args.is_spot
            else native_compute_v1.SchedulingProvisioningModel.STANDARD
        )
        instance_template_args = native_compute_v1.InstanceTemplateArgs(
            properties=native_compute_v1.InstancePropertiesArgs(
                can_ip_forward=False,
                confidential_instance_config=native_compute_v1.ConfidentialInstanceConfigArgs(
                    enable_confidential_compute=False,
                ),
                network_interfaces=[
                    native_compute_v1.NetworkInterfaceArgs(
                        subnetwork=args.subnet,
                        # Use the default NAT that will assign an ephemeral public IP.
                        access_configs=[
                            native_compute_v1.AccessConfigArgs(
                                type=native_compute_v1.AccessConfigType.ONE_TO_ONE_NAT
                            )
                        ],
                        # Use the private address if it was provided.
                        # This means any instance created with this template
                        # will only have this private IP. It also limits the
                        # number of instances to 1. If we are going to set
                        # the number of instances to be > 1, we need an LB
                        # and wouldn't be assigning static private IPs
                        # directly to VMs anyway.
                        network_ip=(
                            args.private_address.address
                            if args.private_address
                            else None
                        ),
                    )
                ],
                disks=[
                    native_compute_v1.AttachedDiskArgs(
                        auto_delete=True,
                        boot=True,
                        disk_size_gb="32",
                        initialize_params=native_compute_v1.AttachedDiskInitializeParamsArgs(
                            # Use Google's Container-Optimized OS (cos),
                            # which comes with Docker pre-installed.
                            # We are using latest production-ready
                            # stable version of cos.
                            #
                            # The version number scheme is defined at:
                            # https://cloud.google.com/container-optimized-os/docs/concepts/versioning
                            source_image="projects/cos-cloud/global/images/family/cos-stable"
                        ),
                    ),
                ],
                machine_type=args.machine_type.value,
                metadata=native_compute_v1.MetadataArgs(
                    items=[
                        native_compute_v1.MetadataItemsItemArgs(
                            key="enable-oslogin",
                            value="true",
                        ),
                        native_compute_v1.MetadataItemsItemArgs(
                            key="enable-oslogin-2fa", value="true"
                        ),
                        native_compute_v1.MetadataItemsItemArgs(
                            key="google-monitoring-enabled", value="true"
                        ),
                        native_compute_v1.MetadataItemsItemArgs(
                            key="google-logging-enabled", value="true"
                        ),
                        native_compute_v1.MetadataItemsItemArgs(
                            key="gce-container-declaration",
                            value=container_declaration,
                        ),
                        native_compute_v1.MetadataItemsItemArgs(
                            key="startup-script",
                            value=startup_script,
                        ),
                    ]
                ),
                scheduling=native_compute_v1.SchedulingArgs(
                    provisioning_model=provisioning_model,
                ),
                service_accounts=[
                    native_compute_v1.ServiceAccountArgs(
                        email=args.service_account_email,
                        scopes=[
                            "https://www.googleapis.com/auth/cloud-platform",
                        ],
                    ),
                ],
            )
        )

        # Add all the secret env vars as custom instance metadata items.
        instance_template_args.properties.metadata.items.extend(
            args.secret_env
        )

        self.instance_template = native_compute_v1.InstanceTemplate(
            f"{name}-instance-template",
            args=instance_template_args,
            opts=pulumi.ResourceOptions(
                parent=self,
                # Instance templates are immutable so we need to Pulumi
                # to replace the template anytime any property is
                # changed.
                replace_on_changes=["*"],
            ),
        )

        container_declaration.apply(
            lambda cd: pulumi.log.debug(cd, self.instance_template)
        )

    def __create_zonal_instance_group(self):
        args = self.__args
        name = self.__name

        # Due to an issue with the Pulumi Google Native provider,
        # we have to use the classic GCP provider to create the
        # managed instance group.
        #
        # https://github.com/pulumi/pulumi-google-native/issues/401
        #
        # Note: A PR was opened to fix the issue in the provider
        # but there is no timeline on when it would be merged.
        assert args.n_instances in (
            0,
            1,
        ), "More than 1 instance is not currently supported"
        self.zonal_instance_group = classic_gcp_compute.InstanceGroupManager(
            f"{name}-instance-group",
            base_instance_name=name,
            versions=[
                classic_gcp_compute.InstanceGroupManagerVersionArgs(
                    instance_template=self.instance_template.self_link
                )
            ],
            zone=zone,
            target_size=args.n_instances,
            auto_healing_policies=(
                classic_gcp_compute.InstanceGroupManagerAutoHealingPoliciesArgs(
                    initial_delay_sec=30,
                    health_check=self.__autohealing.id,
                )
                if self.__autohealing is not None
                else None
            ),
            update_policy=classic_gcp_compute.InstanceGroupManagerUpdatePolicyArgs(
                type="PROACTIVE",
                minimal_action="REPLACE",
                # most_disruptive_allowed_action="REPLACE",
                max_unavailable_fixed=3,
                replacement_method="RECREATE",
            ),
            stateful_internal_ips=(
                [
                    classic_gcp_compute.InstanceGroupManagerStatefulInternalIpArgs(
                        delete_rule="ON_PERMANENT_INSTANCE_DELETION",
                        interface_name="nic0",
                    )
                ]
                if args.automatic_static_private_ip
                else None
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[
                    firewall_association,
                    self.__artifact_registry_perm,
                    self.__logging_perm,
                    self.__monitoring_perm,
                ],
            ),
        )

    def __get_internal_ip(self, instance_group_manager_name: str):
        """
        Returns the internal IP address for a valid managed instance
        created by the (MIG) managed instance group.
        """
        # We use the Google Cloud SDK to do this because neither versions
        # of the Google providers in Pulumi offer a way to list managed
        # instances of a group. At least at the of this writing they
        # didn't.
        client = InstanceGroupManagersClient()
        request = ListManagedInstancesInstanceGroupManagersRequest(
            instance_group_manager=instance_group_manager_name,
            project=project,
            zone=zone,
        )
        page_result = client.list_managed_instances(request)
        internal_ip_addr = ""
        for instance in page_result:
            if (
                instance.instance_status == "STOPPED"
                or instance.current_action
                not in ["NONE", "CREATING", "REFRESHING", "VERIFYING"]
            ):
                pulumi.log.info(
                    f"Skipping managed instance with status: {instance.instance_status} and current action: {instance.current_action}"
                )
                continue

            internal_ip_addr = (
                instance.preserved_state_from_policy.internal_i_ps[
                    "nic0"
                ].ip_address.literal
            )
            break

        if internal_ip_addr == "":
            raise Exception(
                "Did not find a reserved IP address or any running instances in the managed instance group"
            )

        return internal_ip_addr

    def get_host(self) -> pulumi.Output[str]:
        if self.__args.private_address:
            return self.__args.private_address.address
            # return pulumi.Output.concat(
            #    "https://", self.__args.private_address.address
            # )

        # The self_link is only available once the instance group manager
        # resource is created, so creating a dependency on that will
        # ensure that the lambda will not run until after the
        # resource has been created. If we apply()'d on the
        # `name` property, the enclosed lambda will always
        # run and there is no way to know if the resource
        # was actually created.
        return (
            pulumi.Output.all(
                self.zonal_instance_group.name,
                self.zonal_instance_group.self_link,
            ).apply(lambda args: self.__get_internal_ip(args[0]))
            # .apply(lambda ip: f"https://{ip}")
        )

    def __lift_container_spec_env_vars(
        self, spec: Container, values: List[str]
    ) -> Container:
        i = 0
        for env_var in spec.env:
            env_var.value = values[i]
            i += 1

        return spec

    def __lift_container_spec_image(
        self, spec: Container, image: str
    ) -> Container:
        spec.image = image
        return spec

    def __get_container_declaration(
        self, container: Container, restart_policy: str
    ):
        yaml.emitter.Emitter.process_tag = lambda self, *args, **kw: None

        # HACK! In order to "lift" the output values in the spec,
        # we need to "apply" each of them, overwrite the corresponding
        # property in the spec. Each method that overwrites the property
        # with the lifted plain value must return the spec so that
        # we can continue the chain.
        return (
            pulumi.Output.all(*(env_var.value for env_var in container.env))
            .apply(lambda v: self.__lift_container_spec_env_vars(container, v))
            .apply(lambda _: container.image)
            .apply(lambda i: self.__lift_container_spec_image(container, i))
            .apply(
                lambda c: Spec(
                    spec=ContainerSpec(
                        containers=[c], restartPolicy=restart_policy
                    )
                )
            )
            # The end goal is to serialize the spec as a yaml string.
            .apply(lambda s: yaml.dump(s))
        )
