from pulumi import (
    runtime,
    ResourceTransformationResult,
    ResourceOptions,
    ResourceTransformationArgs,
)

from pulumi_gcp import projects

enabled_services = []

# The following APIs need to be enabled for the resources
# we create in this project.
for service in [
    "artifactregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    # run.googleapis.com allows us to use the
    # CloudRun Admin API to execute jobs.
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
]:
    enabled_services.append(
        projects.Service(service, disable_on_destroy=False, service=service)
    )


# Dynamically attach dependency on the GCP APIs
# that need to be enabled, so that Pulumi doesn't
# try to create resources before the APIs are
# enabled in the project.
def gcp_service_api_stack_transformation(
    args: ResourceTransformationArgs,
):
    return ResourceTransformationResult(
        props=args.props,
        opts=ResourceOptions.merge(
            args.opts, ResourceOptions(depends_on=enabled_services)
        ),
    )


runtime.register_stack_transformation(gcp_service_api_stack_transformation)
