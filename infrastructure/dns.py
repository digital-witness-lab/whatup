import pulumi
from pulumi import get_stack, Output
import pulumi_gcp as gcp

from config import root_domain, project
from service import Service


if root_domain:
    root_domain = root_domain.strip(".")
    # Create and verify the custom domain
    # Create the DNS A record for the custom domain to point to the Cloud Run service
    zone_name = f"root-domain-{get_stack()}-zone"
    zone_id = f"projects/{project}/managedZones/{zone_name}"
    dns_zone = gcp.dns.ManagedZone.get(zone_name, zone_id)
    if dns_zone is None:
        dns_zone = gcp.dns.ManagedZone(
            f"root-domain-{get_stack()}-zone",
            name=zone_name,
            dns_name=f"{root_domain}.",
            cloud_logging_config=gcp.dns.ManagedZoneCloudLoggingConfigArgs(
                enable_logging=True
            ),
        )
    pulumi.export(f"Name servers for: {root_domain}", dns_zone.name_servers)
else:
    dns_zone = None


def create_subdomain(subdomain, targets):
    if dns_zone is None:
        return
    subdomain = subdomain.strip(".")
    domain = f"{subdomain}.{root_domain}"

    gcp.dns.RecordSet(
        f"{subdomain}-{get_stack()}-dns-record",
        managed_zone=dns_zone.name,
        name=f"{domain}.",
        type="CNAME",
        ttl=300,
        rrdatas=targets,
    )
    return domain


def create_subdomain_service(
    subdomain, service: Service
) -> Output[str | None]:
    cr_service = service.service
    url = service.get_url()
    if dns_zone is None:
        return url

    subdomain = subdomain.strip(".")
    domain = create_subdomain(
        subdomain,
        ["ghs.googlehosted.com."],
    )
    # Map the custom domain to the Cloud Run service
    domain_mapping = gcp.cloudrun.DomainMapping(
        f"{subdomain}-{get_stack()}-domain-mapping",
        gcp.cloudrun.DomainMappingArgs(
            name=domain,
            location=cr_service.location,
            metadata=gcp.cloudrun.DomainMappingMetadataArgs(
                namespace=project,
            ),
            spec=gcp.cloudrun.DomainMappingSpecArgs(
                route_name=cr_service.name,
                certificate_mode="AUTOMATIC",
            ),
        ),
    )

    return pulumi.Output.concat("https://", domain_mapping.name)
