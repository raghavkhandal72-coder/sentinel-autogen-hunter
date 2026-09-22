"""MITRE ATT&CK Enterprise Matrix Navigator & Coverage Mapper.

Maps Sentinel-AutoGen-Hunter's autonomous multi-agent threat swarm, Sigma transpiler,
canary deception engine, and agent shield directly to MITRE ATT&CK v14.1 enterprise tactics.

Supports exporting official MITRE ATT&CK Navigator Layer JSON format (v4.5).
"""

import json
from typing import Any

# Comprehensive MITRE ATT&CK Mapping for Sentinel-AutoGen-Hunter capabilities
MITRE_TECHNIQUES_DATABASE = {
    # 1. Initial Access
    "T1190": {
        "name": "Exploit Public-Facing Application",
        "tactic": "initial-access",
        "component": "NetworkAnalyzerAgent",
        "coverage": "high",
        "detection": "AbuseIPDB Velocity & CVE Payload Heuristics",
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "initial-access",
        "component": "DeceptionAgent",
        "coverage": "high",
        "detection": "Canary Honeytoken Credential Traps",
    },
    "T1566": {
        "name": "Phishing & Prompt Delivery",
        "tactic": "initial-access",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Adversarial Prompt Injection Scanner",
    },
    # 2. Execution
    "T1059.004": {
        "name": "Command and Scripting Interpreter: Unix Shell",
        "tactic": "execution",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Destructive Shell Gatekeeper & Reverse Shell Blocker",
    },
    "T1059.001": {
        "name": "Command and Scripting Interpreter: PowerShell",
        "tactic": "execution",
        "component": "SigmaEngineAgent",
        "coverage": "medium",
        "detection": "Transpiled Multi-SIEM Sigma Detections",
    },
    "T1609": {
        "name": "Container Administration Command",
        "tactic": "execution",
        "component": "IaCScannerAgent",
        "coverage": "high",
        "detection": "Host PID & Privileged Docker Inspection",
    },
    # 3. Persistence
    "T1098": {
        "name": "Account Manipulation",
        "tactic": "persistence",
        "component": "CSPMEngineAgent",
        "coverage": "high",
        "detection": "Cloud IAM Admin Escalation Auditor",
    },
    "T1053": {
        "name": "Scheduled Task/Job: Cron",
        "tactic": "persistence",
        "component": "SentinelAuditorAgent",
        "coverage": "medium",
        "detection": "KQL Cron Modification Correlation Rules",
    },
    # 4. Privilege Escalation
    "T1548": {
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "privilege-escalation",
        "component": "IaCScannerAgent",
        "coverage": "high",
        "detection": "Kubernetes allowPrivilegeEscalation Policy Linter",
    },
    "T1611": {
        "name": "Escape to Host",
        "tactic": "privilege-escalation",
        "component": "IaCScannerAgent",
        "coverage": "high",
        "detection": "Sensitive hostPath Mount Interceptor (/var/run/docker.sock)",
    },
    # 5. Defense Evasion
    "T1070": {
        "name": "Indicator Removal: Clear Command History",
        "tactic": "defense-evasion",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Blacklisted history flushing / iptables -F commands",
    },
    "T1562": {
        "name": "Impair Defenses: Disable Firewall",
        "tactic": "defense-evasion",
        "component": "RemediationAgent",
        "coverage": "high",
        "detection": "Netfilter DOCKER-USER Kernel Chain Protection & Rollback",
    },
    # 6. Credential Access
    "T1110.001": {
        "name": "Brute Force: Password Guessing",
        "tactic": "credential-access",
        "component": "NetworkAnalyzerAgent",
        "coverage": "high",
        "detection": "Continuous SSH honeypot auth log velocity monitor",
    },
    "T1552": {
        "name": "Unsecured Credentials",
        "tactic": "credential-access",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Direct read block on /etc/shadow, .env, and id_rsa",
    },
    "T1552.001": {
        "name": "Credentials in Files",
        "tactic": "credential-access",
        "component": "GitHubScanner",
        "coverage": "high",
        "detection": "Automated regex leak scanner for API keys & tokens",
    },
    # 7. Discovery
    "T1046": {
        "name": "Network Service Discovery",
        "tactic": "discovery",
        "component": "NetworkAnalyzerAgent",
        "coverage": "high",
        "detection": "Port scan & ingress probe telemetry scoring",
    },
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "discovery",
        "component": "SentinelAgentShield",
        "coverage": "medium",
        "detection": "Agent tool invocation reconnaissance analyzer",
    },
    # 8. Lateral Movement
    "T1021.004": {
        "name": "Remote Services: SSH",
        "tactic": "lateral-movement",
        "component": "NetworkAnalyzerAgent",
        "coverage": "high",
        "detection": "AbuseIPDB cross-node IP correlation",
    },
    # 9. Exfiltration
    "T1048": {
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "exfiltration",
        "component": "DeceptionAgent",
        "coverage": "high",
        "detection": "Canary token webhooks & DNS canary tripwires",
    },
    "T1567": {
        "name": "Exfiltration Over Web Service",
        "tactic": "exfiltration",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Curl/Webhook exfiltration pattern blocker",
    },
    # 10. Impact
    "T1485": {
        "name": "Data Destruction",
        "tactic": "impact",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Raw disk overwrite (dd, mkfs) and rm -rf gatekeeper",
    },
    "T1499": {
        "name": "Endpoint Denial of Service: Fork Bomb",
        "tactic": "impact",
        "component": "SentinelAgentShield",
        "coverage": "high",
        "detection": "Fork bomb regex (:(){ :|:& };:) pre-execution drop",
    },
}

ALL_TACTICS = [
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
]


def get_mitre_coverage_matrix() -> dict[str, Any]:
    """Computes overall tactical and technique coverage percentages."""
    tactics_summary: dict[str, dict[str, Any]] = {tactic: {"count": 0, "techniques": []} for tactic in ALL_TACTICS}

    for tech_id, details in MITRE_TECHNIQUES_DATABASE.items():
        tactic = details["tactic"]
        if tactic in tactics_summary:
            tactics_summary[tactic]["count"] += 1
            tactics_summary[tactic]["techniques"].append({
                "technique_id": tech_id,
                "name": details["name"],
                "component": details["component"],
                "coverage": details["coverage"],
                "detection": details["detection"],
            })

    covered_tactics = sum(1 for t in tactics_summary.values() if t["count"] > 0)
    total_tactics = len(ALL_TACTICS)
    coverage_score = round((covered_tactics / total_tactics) * 100, 1)

    return {
        "total_techniques_mapped": len(MITRE_TECHNIQUES_DATABASE),
        "covered_tactics_count": covered_tactics,
        "total_tactics_count": total_tactics,
        "tactical_coverage_score": coverage_score,
        "tactics": tactics_summary,
    }


def export_mitre_navigator_layer() -> dict[str, Any]:
    """Generates standard MITRE ATT&CK Navigator Layer v4.5 JSON."""
    techniques_list = []
    for tech_id, details in MITRE_TECHNIQUES_DATABASE.items():
        score = 100 if details["coverage"] == "high" else 60
        techniques_list.append({
            "techniqueID": tech_id,
            "tactic": details["tactic"],
            "score": score,
            "color": "#00ff88" if details["coverage"] == "high" else "#ffaa00",
            "comment": f"Enforced by Sentinel-AutoGen-Hunter [{details['component']}]: {details['detection']}",
            "enabled": True,
        })

    return {
        "name": "Sentinel-AutoGen-Hunter Coverage Layer",
        "versions": {
            "attack": "14",
            "navigator": "4.5",
            "layer": "4.5",
        },
        "domain": "enterprise-attack",
        "description": "Autonomous Multi-Agent Threat Swarm & Zero-Trust Defense Matrix",
        "techniques": techniques_list,
        "gradient": {
            "colors": ["#ff0055", "#ffaa00", "#00ff88"],
            "minValue": 0,
            "maxValue": 100,
        },
        "legendItems": [
            {"label": "Autonomous Line-Rate Enforcement (High)", "color": "#00ff88"},
            {"label": "Transpiled Multi-SIEM Rule (Medium)", "color": "#ffaa00"},
        ],
    }


def render_ascii_matrix() -> str:
    """Renders a readable terminal ASCII view of tactical defense readiness."""
    cov = get_mitre_coverage_matrix()
    lines = [
        "=" * 70,
        "   [+] SENTINEL-AUTOGEN-HUNTER : MITRE ATT&CK MATRIX COVERAGE",
        "=" * 70,
        f"Tactical Readiness Score : {cov['tactical_coverage_score']}% ({cov['covered_tactics_count']}/{cov['total_tactics_count']} Tactics)",
        f"Active Techniques Mapped : {cov['total_techniques_mapped']}",
        "-" * 70,
    ]

    for tactic, data in cov["tactics"].items():
        status = "[COVERED]" if data["count"] > 0 else "[PENDING]"
        lines.append(f"{tactic.upper():<24} {status:<10} ({data['count']} techniques)")
        for tech in data["techniques"]:
            lines.append(f"  * {tech['technique_id']:<10} {tech['name'][:30]:<32} [{tech['component']}]")

    lines.append("=" * 70)
    return "\n".join(lines)
