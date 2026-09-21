"""IaC Security Scanner Agent for shift-left pre-deployment infrastructure audits."""

import json
from typing import Any

from .base_agent import BaseAgent
from .tools.iac_analyzer import analyze_iac_content

IAC_SYSTEM_PROMPT = """You are a Principal Cloud DevSecOps Architect specializing in Infrastructure as Code (IaC) security hardening.
You review static analysis findings on Kubernetes and Terraform manifests and formulate automated, production-ready remediation diffs.

INSTRUCTIONS:
1. Review the list of security violations detected in the manifest.
2. Provide a concise technical justification.
3. Formulate a clean, production-ready YAML or HCL configuration snippet that resolves all findings.
4. You must respond ONLY with a valid JSON object matching the schema below.

REQUIRED JSON SCHEMA:
{
  "audit_passed": boolean,
  "compliance_grade": string ("A", "B", "C", "D", "F"),
  "critical_risk_summary": string,
  "suggested_patch": string,
  "developer_action_items": [string]
}
"""


class IaCScannerAgent(BaseAgent):
    """Audits Kubernetes manifests and Terraform configurations prior to deployment."""

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="IaCScannerAgent", model=model)

    def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """Scans IaC manifest content and generates security recommendations."""
        content = data.get("content", "")
        filename = data.get("filename", "manifest.yaml")

        # 1. Run deterministic static analysis
        static_report = analyze_iac_content(content, filename)

        # 2. Enrich with LLM / heuristic recommendations
        user_content = json.dumps(static_report)
        llm_output = self._call_llm(IAC_SYSTEM_PROMPT, user_content)

        # Fallback simulation mapping if LLM returns default
        if "compliance_grade" not in llm_output:
            score = static_report["compliance_score"]
            if score >= 90:
                grade = "A"
            elif score >= 75:
                grade = "B"
            elif score >= 60:
                grade = "C"
            elif score >= 40:
                grade = "D"
            else:
                grade = "F"

            action_items = [f["remediation"] for f in static_report["findings"]]
            llm_output = {
                "audit_passed": static_report["passed"],
                "compliance_grade": grade,
                "critical_risk_summary": (
                    f"Found {static_report['summary']['critical']} critical and "
                    f"{static_report['summary']['high']} high severity violations."
                ),
                "suggested_patch": (
                    "# Hardened SecurityContext Recommendation:\n"
                    "securityContext:\n"
                    "  runAsNonRoot: true\n"
                    "  runAsUser: 10001\n"
                    "  allowPrivilegeEscalation: false\n"
                    "  readOnlyRootFilesystem: true\n"
                    "  capabilities:\n"
                    "    drop:\n"
                    "      - ALL"
                ),
                "developer_action_items": action_items,
            }

        return {
            "static_analysis": static_report,
            "agent_remediation": llm_output,
            "status": "APPROVED" if static_report["passed"] else "BLOCKED_BY_POLICY",
        }
