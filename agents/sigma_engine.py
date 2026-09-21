"""Universal Multi-SIEM Sigma Rule Transpiler and Detection Synthesis Engine.

Converts runtime threats and IOCs into industry-standard Sigma rules (YAML)
and automatically transpiles detection logic to:
- Microsoft Sentinel (KQL)
- Splunk (SPL)
- Elasticsearch / Elastic Security (ES|QL & Query DSL)
- AWS CloudWatch Logs Insights / OpenSearch
"""

import json
import logging
from typing import Any
import uuid

from .base_agent import BaseAgent

logger = logging.getLogger("SigmaEngine")

# MITRE ATT&CK technique mapping for common autonomous threat scenarios
MITRE_TACTICS_MAP = {
    "ssh_brute_force": {
        "technique_id": "T1110.001",
        "technique_name": "Brute Force: Password Guessing",
        "tactic": "Credential Access",
        "logsource_category": "authentication",
        "logsource_service": "sshd",
    },
    "port_scan": {
        "technique_id": "T1046",
        "technique_name": "Network Service Discovery",
        "tactic": "Discovery",
        "logsource_category": "firewall",
        "logsource_service": "network",
    },
    "credential_access": {
        "technique_id": "T1552",
        "technique_name": "Unsecured Credentials",
        "tactic": "Credential Access",
        "logsource_category": "file_access",
        "logsource_service": "system",
    },
    "canary_breach": {
        "technique_id": "T1078.004",
        "technique_name": "Valid Accounts: Cloud Accounts",
        "tactic": "Defense Evasion",
        "logsource_category": "cloud_audit",
        "logsource_service": "iam",
    },
    "lateral_movement": {
        "technique_id": "T1021.004",
        "technique_name": "Remote Services: SSH",
        "tactic": "Lateral Movement",
        "logsource_category": "network_connection",
        "logsource_service": "sshd",
    },
}


def generate_sigma_yaml(threat_event: dict[str, Any]) -> str:
    """Synthesizes an official SigmaHQ-compliant YAML detection rule."""
    threat_type = threat_event.get("threat_type", "ssh_brute_force")
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")
    target_asset = threat_event.get("target_asset", "target-server")
    rule_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{threat_type}-{attacker_ip}"))

    mitre_meta = MITRE_TACTICS_MAP.get(
        threat_type,
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "logsource_category": "application",
            "logsource_service": "security",
        },
    )

    sigma_rule = f"""title: Autonomous Hunt: Suspicious {threat_type.replace('_', ' ').title()} Detected
id: {rule_id}
status: test
description: Detects automated {threat_type} patterns against {target_asset} synthesized by Sentinel-AutoGen-Hunter.
references:
    - https://attack.mitre.org/techniques/{mitre_meta['technique_id'].split('.')[0]}/
author: Sentinel-AutoGen-Hunter Swarm
date: 2026/03/21
modified: 2026/03/21
tags:
    - attack.{mitre_meta['tactic'].lower().replace(' ', '_')}
    - attack.{mitre_meta['technique_id'].lower()}
logsource:
    category: {mitre_meta['logsource_category']}
    product: linux
    service: {mitre_meta['logsource_service']}
detection:
    selection_ip:
        src_ip: '{attacker_ip}'
    selection_event:
        event_type: '{threat_type}'
    condition: selection_ip and selection_event
fields:
    - src_ip
    - dst_host
    - user
    - event_type
falsepositives:
    - Authorized internal security audit or penetration test
    - Misconfigured bastion health check probes
level: high
"""
    return sigma_rule.strip()


def transpile_to_kql(threat_event: dict[str, Any]) -> str:
    """Transpiles threat criteria into Microsoft Sentinel Kusto Query Language (KQL)."""
    threat_type = threat_event.get("threat_type", "ssh_brute_force")
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")

    return f"""// Microsoft Sentinel Analytical Rule (Synthesized by AutoGen Swarm)
AutoGenThreatHunt_CL
| where TimeGenerated >= ago(24h)
| where ThreatType == "{threat_type}" or AttackerIP == "{attacker_ip}"
| summarize EventCount = count(), FirstSeen = min(TimeGenerated), LastSeen = max(TimeGenerated) by AttackerIP, TargetAsset, ThreatType
| where EventCount >= 3
| project FirstSeen, LastSeen, AttackerIP, TargetAsset, ThreatType, EventCount
| extend IPCustomEntity = AttackerIP, HostCustomEntity = TargetAsset"""


def transpile_to_splunk_spl(threat_event: dict[str, Any]) -> str:
    """Transpiles threat criteria into Splunk Search Processing Language (SPL)."""
    threat_type = threat_event.get("threat_type", "ssh_brute_force")
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")

    return f"""index=security sourcetype=linux:auth (src_ip="{attacker_ip}" OR signature="{threat_type}")
| stats count earliest(_time) as first_seen latest(_time) as last_seen by src_ip, dest, user, signature
| where count >= 3
| eval mitre_tactic="Credential Access"
| sort - count"""


def transpile_to_elastic_esql(threat_event: dict[str, Any]) -> str:
    """Transpiles threat criteria into Elastic Security ES|QL query."""
    threat_type = threat_event.get("threat_type", "ssh_brute_force")
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")

    return f"""FROM logs-*
| WHERE @timestamp >= NOW() - 1 day
  AND (source.ip == "{attacker_ip}" OR event.category == "{threat_type}")
| STATS event_count = COUNT(*) BY source.ip, host.name, user.name
| WHERE event_count >= 3
| SORT event_count DESC
| LIMIT 100"""


def transpile_to_aws_opensearch(threat_event: dict[str, Any]) -> str:
    """Transpiles threat criteria into AWS CloudWatch Logs Insights / OpenSearch query."""
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")

    return f"""fields @timestamp, @message, srcAddr, dstAddr, action
| filter srcAddr = '{attacker_ip}' or @message like /FAILED LOGIN/
| stats count(*) as attempts by srcAddr, dstAddr
| filter attempts >= 3
| sort attempts desc"""


def synthesize_universal_matrix(threat_event: dict[str, Any]) -> dict[str, Any]:
    """Builds a complete multi-SIEM detection matrix covering all major platforms."""
    threat_type = threat_event.get("threat_type", "ssh_brute_force")
    attacker_ip = threat_event.get("attacker_ip") or threat_event.get("source_ip", "192.168.1.100")
    mitre_info = MITRE_TACTICS_MAP.get(
        threat_type,
        {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
        },
    )

    sigma_yaml = generate_sigma_yaml(threat_event)
    kql_query = transpile_to_kql(threat_event)
    splunk_spl = transpile_to_splunk_spl(threat_event)
    elastic_esql = transpile_to_elastic_esql(threat_event)
    aws_query = transpile_to_aws_opensearch(threat_event)

    return {
        "status": "success",
        "threat_type": threat_type,
        "attacker_ip": attacker_ip,
        "mitre_attack": mitre_info,
        "detection_rules": {
            "sigma_yaml": sigma_yaml,
            "microsoft_sentinel_kql": kql_query,
            "splunk_spl": splunk_spl,
            "elastic_esql": elastic_esql,
            "aws_cloudwatch": aws_query,
        },
        "platforms_supported": [
            "Sigma Standard (YAML)",
            "Microsoft Sentinel (KQL)",
            "Splunk Enterprise / Cloud (SPL)",
            "Elastic Security (ES|QL)",
            "AWS CloudWatch / OpenSearch",
        ],
    }


class SigmaEngineAgent(BaseAgent):
    """Autonomous Agent synthesizing cross-platform multi-SIEM and Sigma rules."""

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="SigmaEngineAgent", model=model)

    def analyze(self, audit_context: dict[str, Any]) -> dict[str, Any]:
        """Synthesizes the complete detection matrix for any detected security event."""
        return synthesize_universal_matrix(audit_context)
