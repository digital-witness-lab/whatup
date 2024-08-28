from pulumi_gcp import compute, servicenetworking

vpc_public = compute.Network("vpc-public", auto_create_subnetworks=False)
public_services_network = compute.Subnetwork(
    "subnet-public",
    network=vpc_public.id,
    ip_cidr_range="10.1.0.0/16",
    private_ip_google_access=False,
)


vpc = compute.Network("vpc", auto_create_subnetworks=False)

private_services_network = compute.Subnetwork(
    "private",
    network=vpc.id,
    ip_cidr_range="10.1.0.0/16",
    private_ip_google_access=True,
)

private_services_network_with_db = compute.Subnetwork(
    "private-with-db",
    network=vpc.id,
    ip_cidr_range="10.2.0.0/16",
    private_ip_google_access=True,
)

private_services_connect_ip_prefix = "10.240.0.0"
private_services_connect_ip_range = 16

private_ip_address_range = compute.GlobalAddress(
    "reserved-private",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    address=private_services_connect_ip_prefix,
    prefix_length=private_services_connect_ip_range,
    network=vpc.id,
)

private_vpc_connection = servicenetworking.Connection(
    "vpc-connection",
    network=vpc.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_address_range.name],
)
