"""Unit tests for Sentinel-AutoGen-Hunter agents."""

from agents.autogen_swarm import AutoGenThreatSwarm
from agents.network_analyzer import NetworkAnalyzerAgent
from agents.remediation_agent import RemediationAgent
from agents.sentinel_auditor import SentinelAuditorAgent


def test_network_analyzer_malicious_detection():
    """Verify NetworkAnalyzer correctly classifies brute force anomalies."""
    analyzer = NetworkAnalyzerAgent()
    telemetry = {
        "service": "sshd",
        "event_type": "authentication_failed",
        "target_user": "root",
        "source_ip": "203.0.113.100",
        "source_port": "45123",
        "raw_log": "Failed password for root from 203.0.113.100 port 45123 ssh2",
    }

    result = analyzer.analyze(telemetry)
    assert result["threat_detected"] is True
    assert result["confidence_score"] >= 0.7
    assert result["attacker_ip"] == "203.0.113.100"
    assert "threat_intel" in result


def test_network_analyzer_benign_traffic():
    """Verify NetworkAnalyzer does not trigger false positives on benign events."""
    analyzer = NetworkAnalyzerAgent()
    telemetry = {
        "service": "sshd",
        "event_type": "authentication_success",
        "target_user": "dev_alice",
        "source_ip": "10.0.0.12",
        "source_port": "52110",
        "raw_log": "Accepted password for dev_alice from 10.0.0.12 port 52110 ssh2",
    }

    result = analyzer.analyze(telemetry)
    assert result["threat_detected"] is False
    assert result["confidence_score"] < 0.5
    assert result["threat_type"] == "benign_traffic"


def test_remediation_agent_command_generation():
    """Verify RemediationAgent outputs idempotent DOCKER-USER containment and rollback commands."""
    remediator = RemediationAgent()
    analysis_input = {
        "threat_detected": True,
        "threat_type": "ssh_brute_force",
        "attacker_ip": "198.51.100.55",
        "confidence_score": 0.95,
    }

    plan = remediator.analyze(analysis_input)
    assert plan["action_required"] is True
    assert "DOCKER-USER" in plan["proposed_command"]
    assert "198.51.100.55" in plan["proposed_command"]
    assert "rollback_command" in plan
    assert "DOCKER-USER" in plan["rollback_command"]


def test_sentinel_auditor_kql_synthesis():
    """Verify SentinelAuditor formats Microsoft Sentinel event and generates valid KQL."""
    auditor = SentinelAuditorAgent()
    context = {
        "threat_type": "ssh_brute_force",
        "attacker_ip": "198.51.100.55",
        "target_asset": "honeypot-ssh",
        "confidence_score": 0.92,
        "proposed_command": "iptables -I DOCKER-USER 1 -s 198.51.100.55 -j DROP",
    }

    record = auditor.analyze(context)
    assert "kql_query" in record
    assert "AutoGenThreatHunt_CL" in record["kql_query"]
    assert "198.51.100.55" in record["kql_query"]
    assert "mitre_technique_id" in record
    assert record.get("sentinel_ingested") is True


def test_autogen_swarm_full_hunt_pipeline():
    """Verify full AutoGen consensus hunt pipeline executes end-to-end."""
    swarm = AutoGenThreatSwarm()
    telemetry = {
        "service": "sshd",
        "event_type": "authentication_failed",
        "target_user": "admin",
        "source_ip": "203.0.113.88",
        "source_port": "41234",
        "raw_log": "Failed password for invalid user admin from 203.0.113.88 port 41234 ssh2",
    }

    pipeline_result = swarm.execute_hunt_pipeline(telemetry)
    assert pipeline_result["threat_detected"] is True
    assert pipeline_result["swarm_status"] == "COMPLETED"
    assert pipeline_result["remediation"] is not None
    assert pipeline_result["sentinel"] is not None
    assert "kql_query" in pipeline_result["sentinel"]
