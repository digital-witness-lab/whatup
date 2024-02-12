from enum import Enum
from typing import List
from attr import dataclass

import yaml

import pulumi
from pulumi.resource import ResourceOptions
import pulumi_google_native as gcp

from config import project
from gcloud import get_project_number


class SharedCoreMachineType(Enum):
    E2Micro = "e2-micro"
    E2Small = "e2-small"
    E2Medium = "e2-medium"


@dataclass
class ContainerEnv(yaml.YAMLObject):
    name: str
    value: pulumi.Input[str]


@dataclass
class ContainerSecurityContext(yaml.YAMLObject):
    privileged: bool


@dataclass
class ContainerSpec(yaml.YAMLObject):
    """
    The container spec that will be serialized as yaml
    and added as the value for the instance metdata
    property `gce-container-declaration`.
    """

    args: List[str]
    command: List[str]
    env: List[ContainerEnv]
    image: pulumi.Input[str]
    securityContext: ContainerSecurityContext
    tty: bool
    restartPolicy: str


@dataclass
class ContainerOnVmArgs:
    container_spec: ContainerSpec
    machine_type: SharedCoreMachineType
    subnet: pulumi.Output[str]
    secret_env: List[gcp.compute.v1.MetadataItemsItemArgs]
    service_account_email: pulumi.Output[str]


project_number = get_project_number(project)


class ContainerOnVm(pulumi.ComponentResource):
    def __init__(
        self, name: str, args: ContainerOnVmArgs, opts: ResourceOptions
    ):
        super().__init__("dwl:gce:ContainerOnVm", name, None, opts)

        container_declaration = self.__get_container_declaration(
            args.container_spec
        )

        instance_template_args = gcp.compute.v1.InstanceTemplateArgs(
            properties=gcp.compute.v1.InstancePropertiesArgs(
                can_ip_forward=False,
                confidential_instance_config=gcp.compute.v1.ConfidentialInstanceConfigArgs(
                    enable_confidential_compute=False,
                ),
                network_interfaces=[
                    gcp.compute.v1.NetworkInterfaceArgs(
                        subnetwork=args.subnet,
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
                            # Only certain image support running containers
                            # automatically via the gce-container-declaration
                            # instance metadata.
                            source_image="projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts"
                            # Use Google's Container-Optimized OS (cos),
                            # which comes with Docker pre-installed.
                            # We are using latest production-ready
                            # stable version of cos.
                            #
                            # The version number scheme is defined at:
                            # https://cloud.google.com/container-optimized-os/docs/concepts/versioning
                            # source_image="projects/cos-cloud/global/images/family/cos-stable"
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
                            value=container_declaration,
                        ),
                        # gcp.compute.v1.MetadataItemsItemArgs(
                        #     key="startup-script", value=""
                        # ),
                    ]
                ),
                scheduling=gcp.compute.v1.SchedulingArgs(
                    provisioning_model=gcp.compute.v1.SchedulingProvisioningModel.STANDARD,
                ),
                service_accounts=[
                    # gcp.compute.v1.ServiceAccountArgs(
                    #     email=project_number.apply(
                    #         lambda p: f"{p}-compute@developer.gserviceaccount.com"
                    #     ),
                    #     scopes=[
                    #         # TODO: Grant access to pull container image from
                    #         # Artifact Registry.
                    #         "https://www.googleapis.com/auth/devstorage.read_only",
                    #         "https://www.googleapis.com/auth/logging.write",
                    #         "https://www.googleapis.com/auth/monitoring.write",
                    #         "https://www.googleapis.com/auth/servicecontrol",
                    #         "https://www.googleapis.com/auth/service.management.readonly",
                    #         "https://www.googleapis.com/auth/trace.append",
                    #     ],
                    # ),
                    gcp.compute.v1.ServiceAccountArgs(
                        email=args.service_account_email,
                        scopes=[
                            "https://www.googleapis.com/auth/cloud-platform",
                        ],
                    ),
                ],
            )
        )

        instance_template_args.properties.metadata.items.extend(
            args.secret_env
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

        container_declaration.apply(
            lambda cd: pulumi.log.info(cd, self.instance_template)
        )

        self.instance_group = gcp.compute.v1.InstanceGroupManager(
            f"{name}-instance-group",
            base_instance_name=name,
            instance_template=self.instance_template.self_link,
            target_size=1,
            # update_policy=gcp.compute.v1.InstanceGroupManagerUpdatePolicyArgs(
            #     type=gcp.compute.v1.InstanceGroupManagerUpdatePolicyType.PROACTIVE,
            #     most_disruptive_allowed_action=gcp.compute.v1.InstanceGroupManagerUpdatePolicyMostDisruptiveAllowedAction.REPLACE,
            # ),
        )

    def __lift_container_spec_env_vars(
        self, spec: ContainerSpec, values: List[str]
    ) -> ContainerSpec:
        i = 0
        for env_var in spec.env:
            env_var.value = values[i]
            i += 1

        return spec

    def __lift_container_spec_image(
        self, spec: ContainerSpec, image: str
    ) -> ContainerSpec:
        spec.image = image
        return spec

    def __get_container_declaration(self, spec: ContainerSpec):
        yaml.emitter.Emitter.process_tag = lambda self, *args, **kw: None

        # HACK! In order to "lift" the output values in the spec,
        # we need to "apply" each of them, overwrite the corresponding
        # property in the spec. Each method that overwrites the property
        # with the lifted plain value, it must return the spec so that
        # we can continue the chain.
        return (
            pulumi.Output.all(*(env_var.value for env_var in spec.env))
            .apply(lambda v: self.__lift_container_spec_env_vars(spec, v))
            .apply(lambda _: spec.image)
            .apply(lambda i: self.__lift_container_spec_image(spec, i))
            # The end goal is to serialize the spec as a yaml string.
            .apply(lambda s: yaml.dump(s))
        )
