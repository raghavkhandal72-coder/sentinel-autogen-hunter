"""Unit tests for Sentinel-AutoGen-Hunter security tools."""

from agents.tools.linux_cmd import execute_firewall_rule, sanitize_ip
from agents.tools.notifier import send_teams_alert
from agents.tools.sentinel_connector import push_to_sentinel
from agents.tools.threat_intel import check_ip_reputation, is_valid_ipv4


def test_is_valid_ipv4():
    """Verify IPv4 validation handles edge cases."""
    assert is_valid_ipv4("192.168.1.1") is True
    assert is_valid_ipv4("203.0.113.50") is True
    assert is_valid_ipv4("999.999.999.999") is False
    assert is_valid_ipv4("192.168.1.1; rm -rf /") is False
    assert is_valid_ipv4("") is False


def test_sanitize_ip_injection_rejection():
    """Verify command injection attempts are cleanly detected and blocked."""
    dangerous_inputs = [
        "192.168.1.1; rm -rf /",
        "10.0.0.1 && cat /etc/passwd",
        "172.16.0.1 | bash",
        "192.168.1.1`id`",
        "192.168.1.1\nreboot",
        "attacker.com",
        "10.0.0.1$(whoami)",
    ]

    for evil_input in dangerous_inputs:
        is_safe, reason = sanitize_ip(evil_input)
        assert is_safe is False
        assert reason in ["injection_character_detected", "invalid_ipv4_format"]


def test_sanitize_ip_valid():
    """Verify legitimate IPs pass sanitization."""
    is_safe, clean_ip = sanitize_ip("203.0.113.19")
    assert is_safe is True
    assert clean_ip == "203.0.113.19"


def test_execute_firewall_rule(tmp_path, monkeypatch):
    """Verify safe queueing of firewall commands into pending_blocks log."""
    log_file = tmp_path / "test_pending_blocks.log"
    monkeypatch.setenv("ACTION_LOG_PATH", str(log_file))

    success = execute_firewall_rule(
        proposed_command="iptables -I DOCKER-USER 1 -s 203.0.113.19 -j DROP",
        ip_to_block="203.0.113.19",
        risk_level="high",
    )
    assert success is True
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")
    assert "203.0.113.19" in content
    assert "high" in content
    assert "DOCKER-USER" in content


def test_threat_intel_evaluation():
    """Verify reputation score extraction for RFC1918 and public IPs."""
    rfc1918_result = check_ip_reputation("192.168.1.45")
    assert rfc1918_result["is_malicious"] is False
    assert "Private/Local Network" in rfc1918_result["usage_type"]

    public_result = check_ip_reputation("203.0.113.100")
    assert "abuse_score" in public_result
    assert isinstance(public_result["abuse_score"], int)


def test_notifier_simulation():
    """Verify alert simulation succeeds without throwing errors."""
    alert_result = send_teams_alert(
        threat_type="ssh_brute_force",
        attacker_ip="203.0.113.100",
        recommended_action="iptables -I DOCKER-USER 1 -s 203.0.113.100 -j DROP",
        risk_level="high",
        confidence_score=0.98,
    )
    assert alert_result is True


def test_sentinel_push_simulation():
    """Verify Microsoft Sentinel payload generation and mock ingestion."""
    event = {
        "threat_type": "ssh_brute_force",
        "attacker_ip": "203.0.113.100",
        "target_asset": "auth-honeypot",
        "confidence_score": 0.95,
        "kql_query": "AutoGenThreatHunt_CL | where AttackerIP == '203.0.113.100'",
    }
    ingest_result = push_to_sentinel(event)
    assert ingest_result is True
