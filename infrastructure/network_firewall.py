from pulumi_gcp import compute

from network import (
    private_services_connect_ip_prefix,
    private_services_connect_ip_range,
    private_services_network,
    private_services_network_with_db,
    vpc,
)

firewall_policy = compute.NetworkFirewallPolicy(
    "vpc-fw-policy",
    description="VPC firewall policy",
)

firewall_association = compute.NetworkFirewallPolicyAssociation(
    "vpc-firewall-assoc",
    firewall_policy=firewall_policy.name,
    attachment_target=vpc.id,
)

private_services_network_block = (
    f"{private_services_connect_ip_prefix}/{private_services_connect_ip_range}"
)

compute.NetworkFirewallPolicyRule(
    "deny-to-db",
    compute.NetworkFirewallPolicyRuleArgs(
        action="deny",
        description="Deny private-services subnet from connecting to the DB",
        direction="EGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=999,
        rule_name="deny-db-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=[private_services_network.ip_cidr_range],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=[private_services_network_block],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "allow-to-db",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private-services-with-db subnet to connect to the DB",  # noqa: E501
        direction="EGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=1000,
        rule_name="allow-db-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=[private_services_network_with_db.ip_cidr_range],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=[private_services_network_block],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "allow-to-internet",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private services to connect to the internet",
        direction="EGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=1001,
        rule_name="allow-internet-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=[
                private_services_network.ip_cidr_range,
                private_services_network_with_db.ip_cidr_range,
            ],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=["0.0.0.0/0"],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "deny-all-to-db",
    compute.NetworkFirewallPolicyRuleArgs(
        action="deny",
        description="Deny other networks from connecting to the DB",
        direction="EGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=9000,
        rule_name="deny-all-db-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=["0.0.0.0/0"],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=[private_services_network_block],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "deny-to-internet",
    compute.NetworkFirewallPolicyRuleArgs(
        action="deny",
        description="Deny connecting to the internet from any other subnet",
        direction="EGRESS",
        disabled=False,
        enable_logging=False,
        firewall_policy=firewall_policy.name,
        priority=9001,
        rule_name="deny-internet-connectivity-rule",
        match=compute.NetworkFirewallPolicyRuleMatchArgs(
            src_ip_ranges=["0.0.0.0/0"],
            layer4_configs=[
                compute.NetworkFirewallPolicyRuleMatchLayer4ConfigArgs(
                    ip_protocol="all",
                )
            ],
            dest_ip_ranges=["0.0.0.0/0"],
        ),
    ),
)
