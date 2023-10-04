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

firewall_policy = compute.NetworkFirewallPolicy(
    "vpcFirewallPolicy",
    description="VPC firewall policy",
)

compute.NetworkFirewallPolicyRule(
    "dbFirewallRule",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private services to connect to the DB",
        direction="INGRESS",
        disabled=False,
        enable_logging=True,
        firewall_policy=firewall_policy.name,
        priority=1000,
        rule_name="allow-db-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=[private_services_network.ip_cidr_range],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=[private_db_network.ip_cidr_range],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "internetEgressFirewallRule",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private services to connect to the internet",
        direction="INGRESS",
        disabled=False,
        enable_logging=True,
        firewall_policy=firewall_policy.name,
        priority=1001,
        rule_name="allow-db-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=[private_services_network.ip_cidr_range],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=["0.0.0.0/0"],
        ),
    ),
)
