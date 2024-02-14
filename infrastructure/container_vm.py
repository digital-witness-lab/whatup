from enum import Enum
from typing import List, Optional
from attr import dataclass

import yaml

from google.cloud.compute_v1 import (
    RegionInstanceGroupManagersClient,
    ListManagedInstancesRegionInstanceGroupManagersRequest,
)

import pulumi
from pulumi.resource import ResourceOptions
from pulumi_google_native.compute import v1 as native_compute_v1
from pulumi_gcp import projects, compute as classic_gcp_compute

from config import project, location
from gcloud import get_project_number
from network_firewall import firewall_association


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
class Container(yaml.YAMLObject):
    """
    The container spec that will be serialized as yaml
    and added as the value for the instance metdata
    property `gce-container-declaration`.
    """

    args: List[str]
    command: Optional[List[str]]
    env: List[ContainerEnv]
    image: pulumi.Input[str]
    securityContext: ContainerSecurityContext
    tty: bool


@dataclass
class ContainerSpec(yaml.YAMLObject):
    containers: List[Container]
    restartPolicy: str


@dataclass
class Spec(yaml.YAMLObject):
    spec: ContainerSpec


@dataclass
class ContainerOnVmArgs:
    container_spec: Container
    machine_type: SharedCoreMachineType
    subnet: pulumi.Output[str]
    secret_env: List[native_compute_v1.MetadataItemsItemArgs]
    service_account_email: pulumi.Output[str]
    restart_policy: str


project_number = get_project_number(project)


class ContainerOnVm(pulumi.ComponentResource):
    def __init__(
        self, name: str, args: ContainerOnVmArgs, opts: ResourceOptions
    ):
        super().__init__("dwl:gce:ContainerOnVm", name, None, opts)

        container_declaration = self.__get_container_declaration(
            args.container_spec, args.restart_policy
        )

        # Grant access to pull container image from Artifact Registry.
        artifact_registry_perm = projects.IAMBinding(
            f"{name}-artifact-reg-perm",
            projects.IAMBindingArgs(
                members=[
                    pulumi.Output.concat(
                        "serviceAccount:", args.service_account_email
                    )
                ],
                role="roles/artifactregistry.reader",
                project=project,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        logging_perm = projects.IAMBinding(
            f"{name}-logging-perm",
            projects.IAMBindingArgs(
                members=[
                    pulumi.Output.concat(
                        "serviceAccount:", args.service_account_email
                    )
                ],
                role="roles/logging.logWriter",
                project=project,
            ),
            opts=pulumi.ResourceOptions(parent=self),
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
                    )
                ],
                disks=[
                    native_compute_v1.AttachedDiskArgs(
                        auto_delete=True,
                        boot=True,
                        disk_size_gb="10",
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
                        # native_compute_v1.MetadataItemsItemArgs(
                        #     key="startup-script", value=""
                        # ),
                    ]
                ),
                scheduling=native_compute_v1.SchedulingArgs(
                    provisioning_model=native_compute_v1.SchedulingProvisioningModel.STANDARD,
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

        # Due to an issue with the Pulumi Google Native provider,
        # we have to use the classic GCP provider to create the
        # managed instance group.
        #
        # https://github.com/pulumi/pulumi-google-native/issues/401
        #
        # Note: A PR was opened to fix the issue in the provider
        # but there is no timeline on when it would be merged.
        self.region_instance_group = classic_gcp_compute.RegionInstanceGroupManager(
            f"{name}-region-instance-group",
            base_instance_name=name,
            versions=[
                classic_gcp_compute.RegionInstanceGroupManagerVersionArgs(
                    instance_template=self.instance_template.self_link
                )
            ],
            region=location,
            target_size=1,
            update_policy=classic_gcp_compute.RegionInstanceGroupManagerUpdatePolicyArgs(
                type="PROACTIVE",
                minimal_action="REFRESH",
                most_disruptive_allowed_action="REPLACE",
            ),
            stateful_internal_ips=[
                classic_gcp_compute.RegionInstanceGroupManagerStatefulInternalIpArgs(
                    delete_rule="ON_PERMANENT_INSTANCE_DELETION",
                    interface_name="nic0",
                )
            ],
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[
                    firewall_association,
                    artifact_registry_perm,
                    logging_perm,
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
        client = RegionInstanceGroupManagersClient()
        request = ListManagedInstancesRegionInstanceGroupManagersRequest(
            instance_group_manager=instance_group_manager_name,
            project=project,
            region=location,
        )
        page_result = client.list_managed_instances(request)
        internal_ip_addr = ""
        for instance in page_result:
            if (
                instance.instance_status == "STOPPED"
                or instance.current_action
                not in ["NONE", "CREATING", "REFRESHING", "VERIFYING"]
            ):
                continue

            internal_ip_addr = (
                instance.preserved_state_from_config.internal_i_ps[
                    "nic0"
                ].ip_address.literal
            )
            break

        if internal_ip_addr == "":
            raise Exception(
                "Did not find a reserved IP address or any running instances in the managed instance group"
            )

        return f"https://{internal_ip_addr}"

    def get_host_output(self) -> pulumi.Output[str]:
        # The self_link is only available once the instance group manager
        # resource is created, so creating a dependency on that will
        # ensure that the lambda will not run until after the
        # resource has been created. If we apply()'d on the
        # `name` property, the enclosed lambda will always
        # run and there is no way to know if the resource
        # was actually created.
        return pulumi.Output.all(
            self.region_instance_group.name,
            self.region_instance_group.self_link,
        ).apply(lambda args: self.__get_internal_ip(args[0]))

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
