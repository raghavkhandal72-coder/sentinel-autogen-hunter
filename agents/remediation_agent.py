"""Specialized Remediation Agent for autonomous containment policy generation."""

import json
from typing import Any

from .base_agent import BaseAgent
from .prompts.remediation_system import REMEDIATION_PROMPT
from .tools.linux_cmd import execute_firewall_rule
from .tools.notifier import send_teams_alert


class RemediationAgent(BaseAgent):
    """Generates idempotent network containment rules, logs rollback steps,

    and dispatches enterprise alerts to Microsoft Teams.
    """

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="RemediationAgent", model=model)

    def analyze(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        """Ingests threat analysis results and formulates a containment plan."""
        attacker_ip = analysis_result.get("attacker_ip")
        threat_type = analysis_result.get("threat_type", "unknown_threat")
        confidence = float(analysis_result.get("confidence_score", 0.9))

        user_content = json.dumps(analysis_result)
        action_plan = self._call_llm(REMEDIATION_PROMPT, user_content)

        if action_plan.get("action_required") and attacker_ip:
            proposed_cmd = action_plan.get(
                "proposed_command",
                f"iptables -I DOCKER-USER 1 -s {attacker_ip} -j DROP",
            )
            risk = action_plan.get("risk_level", "high")

            # 1. Safely queue host firewall command
            queued = execute_firewall_rule(proposed_cmd, attacker_ip, risk)
            action_plan["enforcement_queued"] = queued

            # 2. Dispatch Microsoft Teams Adaptive Card alert
            alert_sent = send_teams_alert(
                threat_type=threat_type,
                attacker_ip=attacker_ip,
                recommended_action=proposed_cmd,
                risk_level=risk,
                confidence_score=confidence,
            )
            action_plan["alert_dispatched"] = alert_sent

        return action_plan
