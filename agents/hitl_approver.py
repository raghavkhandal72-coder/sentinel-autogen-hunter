"""Human-in-the-Loop (HITL) Approver module for high-risk containment actions.

Ensures critical infrastructure or internal subnet targets are never blocked
without explicit SecOps authorization, preventing false-positive network partitions.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from .tools.linux_cmd import execute_firewall_rule
from .tools.notifier import send_teams_alert

logger = logging.getLogger("HITLApprover")

# In-memory registry for pending approval requests
PENDING_APPROVALS: dict[str, dict[str, Any]] = {}

# Sensitive subnets requiring mandatory Human-in-the-Loop confirmation
SENSITIVE_PREFIXES = ("10.0.", "192.168.1.", "172.16.0.")


def is_high_risk_target(ip_address: str, risk_level: str) -> bool:
    """Evaluates if an IP address belongs to sensitive internal enterprise infrastructure."""
    return risk_level.lower() in ("critical", "high") and ip_address.startswith(
        SENSITIVE_PREFIXES
    )


def request_containment_approval(
    ip_to_block: str,
    proposed_command: str,
    threat_type: str,
    risk_level: str = "high",
    confidence_score: float = 0.95,
) -> dict[str, Any]:
    """Evaluates whether to execute autonomously or hold in Human-in-the-Loop queue."""
    if not is_high_risk_target(ip_to_block, risk_level):
        # Safe to execute autonomously on public or external adversaries
        success = execute_firewall_rule(proposed_command, ip_to_block, risk_level)
        return {
            "execution_mode": "AUTONOMOUS",
            "status": "EXECUTED" if success else "FAILED",
            "ip_blocked": ip_to_block,
            "requires_human_approval": False,
        }

    # High-Risk / Internal Asset: Hold in HITL queue
    action_id = f"hitl-{uuid.uuid4().hex[:8]}"
    approval_record = {
        "action_id": action_id,
        "ip_to_block": ip_to_block,
        "proposed_command": proposed_command,
        "threat_type": threat_type,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "status": "PENDING_APPROVAL",
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    PENDING_APPROVALS[action_id] = approval_record

    logger.warning(
        f"[HITL GATE TRIGGERED] Action {action_id} for target {ip_to_block} held for SecOps human approval."
    )

    # Dispatch SecOps alert with approval directive
    send_teams_alert(
        threat_type=f"[HITL APPROVAL REQUIRED] {threat_type}",
        attacker_ip=ip_to_block,
        recommended_action=f"Approve action via POST /remediation/approve/{action_id}",
        risk_level="Critical",
        confidence_score=confidence_score,
    )

    return {
        "execution_mode": "HUMAN_IN_THE_LOOP",
        "status": "PENDING_APPROVAL",
        "action_id": action_id,
        "ip_blocked": ip_to_block,
        "requires_human_approval": True,
        "approval_endpoint": f"/remediation/approve/{action_id}",
    }


def approve_action(action_id: str, approver: str = "secops-admin") -> dict[str, Any]:
    """Authorizes and executes a pending containment action."""
    record = PENDING_APPROVALS.get(action_id)
    if not record:
        return {"success": False, "error": f"Action ID '{action_id}' not found."}

    if record["status"] != "PENDING_APPROVAL":
        return {
            "success": False,
            "error": f"Action '{action_id}' is already {record['status']}.",
        }

    # Execute the verified firewall containment
    success = execute_firewall_rule(
        record["proposed_command"], record["ip_to_block"], record["risk_level"]
    )
    record["status"] = "APPROVED_AND_EXECUTED" if success else "EXECUTION_FAILED"
    record["approver"] = approver
    record["approved_at"] = datetime.now(timezone.utc).isoformat()

    logger.info(f"Action {action_id} approved by {approver}. Enforcement: {success}")
    return {"success": success, "action": record}


def reject_action(
    action_id: str, reason: str = "False positive confirmed"
) -> dict[str, Any]:
    """Rejects and dismisses a pending containment action."""
    record = PENDING_APPROVALS.get(action_id)
    if not record:
        return {"success": False, "error": f"Action ID '{action_id}' not found."}

    record["status"] = "REJECTED"
    record["rejection_reason"] = reason
    record["rejected_at"] = datetime.now(timezone.utc).isoformat()

    logger.info(f"Action {action_id} rejected by SecOps: {reason}")
    return {"success": True, "action": record}
