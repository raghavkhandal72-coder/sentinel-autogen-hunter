"""Tests for Human-in-the-Loop (HITL) Gate and Approval Workflow."""

from agents.hitl_approver import (
    PENDING_APPROVALS,
    approve_action,
    is_high_risk_target,
    reject_action,
    request_containment_approval,
)


def setup_function():
    """Clear approvals cache before each test."""
    PENDING_APPROVALS.clear()


def test_is_high_risk_target():
    # Internal subnets with high/critical risk
    assert is_high_risk_target("10.0.1.20", "high") is True
    assert is_high_risk_target("192.168.1.105", "critical") is True
    assert is_high_risk_target("172.16.0.1", "high") is True

    # Low risk or public IPs should not trigger HITL
    assert is_high_risk_target("10.0.1.20", "low") is False
    assert is_high_risk_target("185.220.101.5", "high") is False
    assert is_high_risk_target("203.0.113.1", "critical") is False


def test_request_containment_autonomous_execution():
    # Public IP: autonomous containment without human gate
    result = request_containment_approval(
        ip_to_block="198.51.100.22",
        proposed_command="iptables -I DOCKER-USER -s 198.51.100.22 -j DROP",
        threat_type="SSH_BRUTE_FORCE",
        risk_level="high",
    )
    assert result["execution_mode"] == "AUTONOMOUS"
    assert result["requires_human_approval"] is False
    assert result["status"] == "EXECUTED"


def test_request_containment_hitl_queue_and_approval():
    # High-risk internal IP: held in HITL queue
    result = request_containment_approval(
        ip_to_block="10.0.4.15",
        proposed_command="iptables -I DOCKER-USER -s 10.0.4.15 -j DROP",
        threat_type="LATERAL_MOVEMENT_KERBEROS",
        risk_level="critical",
    )
    assert result["execution_mode"] == "HUMAN_IN_THE_LOOP"
    assert result["requires_human_approval"] is True
    assert result["status"] == "PENDING_APPROVAL"

    action_id = result["action_id"]
    assert action_id in PENDING_APPROVALS

    # Now approve the action
    approval_resp = approve_action(action_id, approver="soc-lead@enterprise.local")
    assert approval_resp["success"] is True
    assert approval_resp["action"]["status"] == "APPROVED_AND_EXECUTED"
    assert approval_resp["action"]["approver"] == "soc-lead@enterprise.local"


def test_reject_action_workflow():
    result = request_containment_approval(
        ip_to_block="192.168.1.50",
        proposed_command="iptables -I DOCKER-USER -s 192.168.1.50 -j DROP",
        threat_type="PORT_SCAN",
        risk_level="high",
    )
    action_id = result["action_id"]

    reject_resp = reject_action(action_id, reason="Approved vulnerability scanner IP")
    assert reject_resp["success"] is True
    assert reject_resp["action"]["status"] == "REJECTED"
    assert (
        reject_resp["action"]["rejection_reason"] == "Approved vulnerability scanner IP"
    )


def test_approve_nonexistent_action():
    resp = approve_action("hitl-nonexistent99")
    assert resp["success"] is False
    assert "not found" in resp["error"].lower()


def test_orchestrator_hitl_api_endpoints():
    import asyncio

    from agents.orchestrator import (
        approve_containment_endpoint,
        list_pending_approvals,
        reject_containment_endpoint,
    )

    # Enqueue a high-risk action
    req = request_containment_approval(
        ip_to_block="10.0.2.88",
        proposed_command="iptables -I DOCKER-USER -s 10.0.2.88 -j DROP",
        threat_type="CREDENTIAL_DUMPING",
        risk_level="critical",
    )
    action_id = req["action_id"]

    # 1. Query pending list
    pending = asyncio.run(list_pending_approvals())
    assert pending["pending_count"] >= 1
    pending_ids = [a["action_id"] for a in pending["actions"]]
    assert action_id in pending_ids

    # 2. Approve via API endpoint
    post_resp = asyncio.run(
        approve_containment_endpoint(action_id, approver="secops-lead")
    )
    assert post_resp["success"] is True
    assert post_resp["action"]["status"] == "APPROVED_AND_EXECUTED"
    assert post_resp["action"]["approver"] == "secops-lead"

    # 3. Test rejection endpoint on another action
    req2 = request_containment_approval(
        ip_to_block="172.16.0.99",
        proposed_command="iptables -I DOCKER-USER -s 172.16.0.99 -j DROP",
        threat_type="SUSPICIOUS_PROBE",
        risk_level="high",
    )
    action_id_2 = req2["action_id"]
    reject_resp = asyncio.run(
        reject_containment_endpoint(
            action_id_2, reason="Security audit authorized test"
        )
    )
    assert reject_resp["success"] is True
    assert reject_resp["action"]["status"] == "REJECTED"
