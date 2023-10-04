from pulumi_gcp import compute

vpc = compute.Network("vpc", auto_create_subnetworks=False)

private_services_network = compute.Subnetwork(
    "privateServicesNetwork",
    name="private-services",
    network=vpc.id,
    ip_cidr_range="10.1.0.0/16",
    private_ip_google_access=True,
)

private_db_network = compute.Subnetwork(
    "dbNetwork",
    name="db",
    network=vpc.id,
    ip_cidr_range="10.2.0.0/28",
    private_ip_google_access=True,
)
