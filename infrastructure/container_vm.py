from attr import dataclass

import pulumi
from pulumi.resource import ResourceOptions
import pulumi_google_native as gcp

from gcloud import get_project_number


@dataclass
class ContainerOnVmArgs:
    network: gcp.compute.v1.Network


project_number = get_project_number()


class ContainerOnVm(pulumi.ComponentResource):
    def __init__(
        self, name: str, args: ContainerOnVmArgs, opts: ResourceOptions
    ):
        super().__init__("dwl:containeronvm", name, args.__dict__, opts)

        instance_template_args = gcp.compute.v1.InstanceTemplateArgs(
            properties=gcp.compute.v1.InstancePropertiesArgs(
                can_ip_forward=True,
                confidential_instance_config=gcp.compute.v1.ConfidentialInstanceConfigArgs(
                    # TODO: Would enabling this have pricing implications?
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
                            source_image="projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20220810"
                        ),
                    ),
                ],
                machine_type="e2-micro",
                metadata=gcp.compute.v1.MetadataArgs(
                    items=[
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="enable-oslogin",
                            value="true",
                        ),
                        gcp.compute.v1.MetadataItemsItemArgs(
                            key="enable-oslogin-2fa", value="true"
                        ),
                    ]
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
                    )
                ],
            )
        )

        self.instance_template = gcp.compute.v1.InstanceTemplate(
            "instance",
            args=instance_template_args,
            opts=pulumi.ResourceOptions(
                # Instance templates are immutable so we need to Pulumi
                # to replace the template anytime any property is
                # changed.
                replace_on_changes=["*"]
            ),
        )

        # const instanceGroup = new gcp.compute.v1.InstanceGroupManager("instance-group-manager", {
        #     targetSize: 1,
        #     baseInstanceName: pulumi.getStack(),
        #     instanceTemplate: instanceTemplate.selfLink,
        #     zone: gcp.config.zone,
        #     updatePolicy: {
        #         type: "PROACTIVE",
        #         mostDisruptiveAllowedAction: "REPLACE",
        #     },
        # });
