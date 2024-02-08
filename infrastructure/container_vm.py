from enum import Enum
from typing import Sequence
from attr import dataclass

import yaml

import pulumi
from pulumi.resource import ResourceOptions
import pulumi_google_native as gcp

from gcloud import get_project_number


class SharedCoreMachineType(Enum):
    E2Micro = "e2-micro"
    E2Small = "e2-small"
    E2Medium = "e2-medium"


@dataclass
class ContainerEnv:
    name: str
    value: str


@dataclass
class ContainerSecurityContext:
    privileged: bool


@dataclass
class ContainerSpec:
    args: Sequence[str]
    command: Sequence[str]
    env: Sequence[ContainerEnv]
    image: pulumi.Output[str]
    securityContext: ContainerSecurityContext
    tty: bool
    restartPolicy: str


@dataclass
class ContainerOnVmArgs:
    container_spec: ContainerSpec
    machine_type: SharedCoreMachineType
    network: gcp.compute.v1.Network
    secret_env: Sequence[gcp.compute.v1.MetadataItemsItemArgs]
    service_account_email: pulumi.Output[str]


project_number = get_project_number()


class ContainerOnVm(pulumi.ComponentResource):
    def __init__(
        self, name: str, args: ContainerOnVmArgs, opts: ResourceOptions
    ):
        super().__init__("dwl:gce:ContainerOnVm", name, args.__dict__, opts)

        instance_template_args = gcp.compute.v1.InstanceTemplateArgs(
            properties=gcp.compute.v1.InstancePropertiesArgs(
                can_ip_forward=True,
                confidential_instance_config=gcp.compute.v1.ConfidentialInstanceConfigArgs(
                    enable_confidential_compute=False,
                ),
                network_interfaces=[
                    gcp.compute.v1.NetworkInterfaceArgs(
                        network=args.network.self_link,
                        # Use the default NAT that will assign an ephemeral public IP.
                        access_configs=[
                            gcp.compute.v1.AccessConfigArgs(
                                type=gcp.compute.v1.AccessConfigType.ONE_TO_ONE_NAT
                            )
                        ],
                    )
                ],
                disks=[
                    gcp.compute.v1.AttachedDiskArgs(
                        auto_delete=True,
                        boot=True,
                        disk_size_gb="10",
                        initialize_params=gcp.compute.v1.AttachedDiskInitializeParamsArgs(
                            # Use Google's Container-Optimized OS (cos),
                            # which comes with Docker pre-installed.
                            # We are using latest production-ready
                            # stable version of cos.
                            #
                            # The version number scheme is defined at:
                            # https://cloud.google.com/container-optimized-os/docs/concepts/versioning
                            source_image="projects/cos-cloud/global/images/cos-stable"
                        ),
                    ),
                ],
                machine_type=args.machine_type.value,
                metadata=gcp.compute.v1.MetadataArgs(
                    items=[
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="enable-oslogin",
                            value="true",
                        ),
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="enable-oslogin-2fa", value="true"
                        ),
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="google-monitoring-enabled", value="true"
                        ),
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="gce-container-declaration",
                            value=args.container_spec.image.apply(
                                lambda i: self.__get_container_declaration(
                                    args.container_spec, i
                                )
                            ),
                        ),
                    ].extend(args.secret_env)
                ),
                scheduling=gcp.compute.v1.SchedulingArgs(
                    provisioning_model=gcp.compute.v1.SchedulingProvisioningModel.STANDARD,
                    # Cannot set this to DELETE action since the managed instance group (MIG) prohibits
                    # that action for Spot provisioning model.
                    instance_termination_action=gcp.compute.v1.SchedulingInstanceTerminationAction.STOP,
                ),
                service_accounts=[
                    gcp.compute.v1.ServiceAccountArgs(
                        email=project_number.apply(
                            lambda p: f"{p}-compute@developer.gserviceaccount.com"
                        ),
                        scopes=[
                            "https://www.googleapis.com/auth/devstorage.read_only",
                            "https://www.googleapis.com/auth/logging.write",
                            "https://www.googleapis.com/auth/monitoring.write",
                            "https://www.googleapis.com/auth/servicecontrol",
                            "https://www.googleapis.com/auth/service.management.readonly",
                            "https://www.googleapis.com/auth/trace.append",
                        ],
                    ),
                    gcp.compute.v1.ServiceAccountArgs(
                        email=args.service_account_email,
                        scopes=[
                            "https://www.googleapis.com/auth/cloud-platform",
                        ],
                    ),
                ],
            )
        )

        self.instance_template = gcp.compute.v1.InstanceTemplate(
            f"{name}-instance-template",
            args=instance_template_args,
            opts=pulumi.ResourceOptions(
                # Instance templates are immutable so we need to Pulumi
                # to replace the template anytime any property is
                # changed.
                replace_on_changes=["*"]
            ),
        )

        self.instance_group = gcp.compute.v1.InstanceGroupManager(
            f"{name}-instance-group",
            base_instance_name=name,
            instance_template=self.instance_template.self_link,
            target_size=1,
            update_policy=gcp.compute.v1.InstanceGroupManagerUpdatePolicyArgs(
                type=gcp.compute.v1.InstanceGroupManagerUpdatePolicyType.PROACTIVE,
                most_disruptive_allowed_action=gcp.compute.v1.InstanceGroupManagerUpdatePolicyMostDisruptiveAllowedAction.REFRESH,
            ),
        )

    def __get_container_declaration(self, spec: ContainerSpec, image: str):
        obj = spec.__dict__
        obj["image"] = image
        return yaml.dump(obj)
