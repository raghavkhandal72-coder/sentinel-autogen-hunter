"""Infrastructure as Code (IaC) static security analyzer.

Scans Kubernetes manifests and Terraform configurations against CIS benchmarks,
identifying security misconfigurations before deployment (Shift-Left DevSecOps).
"""

import re
from typing import Any

# CIS Benchmark Rules for Kubernetes
K8S_RULES = [
    {
        "id": "K8S-001",
        "title": "Container May Run As Root",
        "severity": "HIGH",
        "pattern": r"(?:runAsNonRoot\s*:\s*false|runAsUser\s*:\s*0)",
        "description": "Containers must not run with root privileges to mitigate container breakout.",
        "remediation": "Set securityContext.runAsNonRoot: true and securityContext.runAsUser: 10001",
    },
    {
        "id": "K8S-002",
        "title": "Privileged Container Execution",
        "severity": "CRITICAL",
        "pattern": r"privileged\s*:\s*true",
        "description": "Privileged containers share the host kernel namespace and can take over the host VM.",
        "remediation": "Set securityContext.privileged: false",
    },
    {
        "id": "K8S-003",
        "title": "Privilege Escalation Allowed",
        "severity": "HIGH",
        "pattern": r"allowPrivilegeEscalation\s*:\s*true",
        "description": "Processes should not be allowed to gain more privileges than their parent process.",
        "remediation": "Set securityContext.allowPrivilegeEscalation: false",
    },
    {
        "id": "K8S-004",
        "title": "Host Network / Namespace Sharing",
        "severity": "CRITICAL",
        "pattern": r"(?:hostNetwork\s*:\s*true|hostPID\s*:\s*true|hostIPC\s*:\s*true)",
        "description": "Pods must not attach to host networking or host PID namespaces.",
        "remediation": "Remove hostNetwork/hostPID/hostIPC or set them to false",
    },
    {
        "id": "K8S-005",
        "title": "Missing Resource Limits",
        "severity": "MEDIUM",
        "pattern": r"resources\s*:\s*\{\s*\}|limits\s*:\s*\{\s*\}",
        "description": "Missing CPU/Memory resource limits exposes cluster nodes to Denial of Service.",
        "remediation": "Specify resources.limits.cpu and resources.limits.memory",
    },
]

# CIS Benchmark Rules for Terraform / Cloud Infrastructure
TERRAFORM_RULES = [
    {
        "id": "TF-001",
        "title": "Open Ingress to 0.0.0.0/0 on Sensitive Ports",
        "severity": "CRITICAL",
        "pattern": r"(?:0\.0\.0\.0/0.*?(?:22|3389|5432|3306|27017)|(?:22|3389|5432|3306|27017).*?0\.0\.0\.0/0)",
        "description": "Administrative management ports (SSH/RDP/Databases) must never be open to the internet.",
        "remediation": "Restrict cidr_blocks to specific corporate VPN or bastion IP CIDRs.",
    },
    {
        "id": "TF-002",
        "title": "Public Storage Access Enabled",
        "severity": "HIGH",
        "pattern": r'(?:public_network_access_enabled\s*=\s*true|acl\s*=\s*"public-read")',
        "description": "Storage accounts or S3 buckets must not allow unauthenticated public read access.",
        "remediation": "Set public_network_access_enabled = false and enable private endpoints.",
    },
    {
        "id": "TF-003",
        "title": "Storage Volume Encryption Disabled",
        "severity": "HIGH",
        "pattern": r"(?:encrypted\s*=\s*false|enable_encryption\s*=\s*false)",
        "description": "Data at rest must be encrypted using customer-managed or cloud-provider keys.",
        "remediation": "Set encrypted = true on storage resources.",
    },
]


def analyze_iac_content(
    content: str, filename: str = "manifest.yaml"
) -> dict[str, Any]:
    """Scans IaC manifest content for security violations."""
    findings: list[dict[str, Any]] = []
    is_terraform = filename.endswith((".tf", ".hcl"))
    rules_to_evaluate = TERRAFORM_RULES if is_terraform else K8S_RULES

    for rule in rules_to_evaluate:
        matches = list(re.finditer(rule["pattern"], content, re.IGNORECASE | re.DOTALL))
        if matches:
            findings.append(
                {
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "remediation": rule["remediation"],
                    "occurrence_count": len(matches),
                }
            )

    # Additional contextual checks for Kubernetes
    if not is_terraform and "kind:" in content:
        if "readOnlyRootFilesystem: true" not in content and "containers:" in content:
            findings.append(
                {
                    "rule_id": "K8S-006",
                    "title": "Root Filesystem Not Read-Only",
                    "severity": "LOW",
                    "description": "Container root filesystem should be mounted as read-only to prevent persistent malware.",
                    "remediation": "Set securityContext.readOnlyRootFilesystem: true",
                    "occurrence_count": 1,
                }
            )

    critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low_count = sum(1 for f in findings if f["severity"] == "LOW")

    passed = critical_count == 0 and high_count == 0

    # Compute a 0-100 compliance security posture score
    penalty = (
        (critical_count * 30) + (high_count * 15) + (medium_count * 5) + (low_count * 2)
    )
    compliance_score = max(0, 100 - penalty)

    return {
        "filename": filename,
        "iac_type": "Terraform" if is_terraform else "Kubernetes",
        "passed": passed,
        "compliance_score": compliance_score,
        "summary": {
            "total_findings": len(findings),
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
        },
        "findings": findings,
    }
