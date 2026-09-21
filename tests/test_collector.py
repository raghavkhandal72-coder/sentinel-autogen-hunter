"""Unit tests for the Linux telemetry collector and log parser."""

from collectors.collector import parse_ssh_log


def test_parse_ssh_failed_login():
    """Verify regex extraction from failed SSH password attempt."""
    log_line = "Sep 21 12:00:01 honeypot sshd[1234]: Failed password for invalid user admin from 198.51.100.44 port 54321 ssh2"
    result = parse_ssh_log(log_line)

    assert result is not None
    assert result["service"] == "sshd"
    assert result["event_type"] == "authentication_failed"
    assert result["target_user"] == "admin"
    assert result["source_ip"] == "198.51.100.44"
    assert result["source_port"] == "54321"


def test_parse_ssh_invalid_user():
    """Verify regex extraction from invalid user reconnaissance attempt."""
    log_line = "Sep 21 12:00:02 honeypot sshd[1235]: Invalid user oracle from 203.0.113.12 port 49820"
    result = parse_ssh_log(log_line)

    assert result is not None
    assert result["event_type"] == "invalid_user_attempt"
    assert result["target_user"] == "oracle"
    assert result["source_ip"] == "203.0.113.12"
    assert result["source_port"] == "49820"


def test_parse_ssh_accepted_password():
    """Verify extraction of legitimate login events."""
    log_line = "Sep 21 12:00:03 honeypot sshd[1236]: Accepted password for bob from 10.0.0.50 port 51111 ssh2"
    result = parse_ssh_log(log_line)

    assert result is not None
    assert result["event_type"] == "authentication_success"
    assert result["target_user"] == "bob"
    assert result["source_ip"] == "10.0.0.50"


def test_parse_ssh_preauth_disconnect():
    """Verify scanner / port knocking identification."""
    log_line = "Sep 21 12:00:04 honeypot sshd[1237]: Connection closed by 192.0.2.77 port 39100 [preauth]"
    result = parse_ssh_log(log_line)

    assert result is not None
    assert result["event_type"] == "preauth_disconnect_scan"
    assert result["source_ip"] == "192.0.2.77"


def test_parse_ssh_unrelated_line():
    """Verify non-security noise lines are safely ignored."""
    noise = "Sep 21 12:00:05 honeypot systemd[1]: Started Daily apt upgrade and clean activities."
    result = parse_ssh_log(noise)
    assert result is None
