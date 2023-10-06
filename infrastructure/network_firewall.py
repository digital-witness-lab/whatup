from pulumi_gcp import compute

from .network import (
    private_db_network,
    private_services_network,
    private_services_network_with_db,
)

firewall_policy = compute.NetworkFirewallPolicy(
    "vpcFirewallPolicy",
    description="VPC firewall policy",
)

compute.NetworkFirewallPolicyRule(
    "dbAccessFirewallRule",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private services to connect to the DB",
        direction="EGRESS",
        disabled=False,
        enable_logging=True,
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
            dest_ip_ranges=[private_db_network.ip_cidr_range],
        ),
    ),
)

compute.NetworkFirewallPolicyRule(
    "internetEgressFirewallRule",
    compute.NetworkFirewallPolicyRuleArgs(
        action="allow",
        description="Allow private services to connect to the internet",
        direction="EGRESS",
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
