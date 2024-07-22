import pulumi
from pulumi import get_stack
import pulumi_gcp as gcp

from config import root_domain


if root_domain:
    root_domain = root_domain.strip(".")
    # Create and verify the custom domain
    # Create the DNS A record for the custom domain to point to the Cloud Run service
    dns_zone = gcp.dns.ManagedZone(
        f"root-domain-{get_stack()}-zone",
        name=f"root-domain-{get_stack()}-zone",
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

    managed_certificate = gcp.compute.ManagedSslCertificate(
        f"{subdomain}-{get_stack()}-certificate",
        managed=gcp.compute.ManagedSslCertificateManagedArgs(domains=[domain]),
        name=f"{subdomain}-{get_stack()}-certificate",
    )

    dns_record = gcp.dns.RecordSet(
        f"{subdomain}-{get_stack()}-dns-record",
        managed_zone=dns_zone.name,
        name=f"{domain}.",
        type="A",
        ttl=300,
        rrdatas=targets,
    )
    return domain


def create_subdomain_cloudrun(subdomain, cloud_run_service) -> str:
    if dns_zone is None:
        cloud_run_service.statuses.apply(lambda s: s[0].url)

    subdomain = subdomain.strip(".")
    domain = create_subdomain(
        subdomain,
        [cloud_run_service.statuses.apply(lambda statuses: statuses[0].url)],
    )
    # Map the custom domain to the Cloud Run service
    domain_mapping = gcp.cloudrun.DomainMapping(
        f"{subdomain}-{get_stack()}-domain-mapping",
        gcp.cloudrun.DomainMappingArgs(
            name=domain,
            location=cloud_run_service.location,
            service=cloud_run_service.id,
            metadata=None,
            spec=gcp.cloudrun.DomainMappingSpecArgs(
                route_name=cloud_run_service.name,
                certificate_mode="AUTOMATIC",
            ),
        ),
    )

    return pulumi.Output.concat("https://", domain_mapping.name)
