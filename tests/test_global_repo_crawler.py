"""Unit tests for Global Repository Ingestor and Ecosystem Auditing."""

import asyncio

from agents.autogen_swarm import AutoGenThreatSwarm
from agents.orchestrator import scan_entire_ecosystem_endpoint
from agents.tools.global_repo_crawler import (
    audit_entire_github_ecosystem,
    get_all_repositories,
)
from mcp.mcp_server import HunterMCPServer


def test_get_all_repositories_deterministic_fallback(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    repos = get_all_repositories()
    assert isinstance(repos, list)
    assert len(repos) >= 3

    # Validate structure
    for r in repos:
        assert "id" in r
        assert "name" in r
        assert "full_name" in r
        assert "private" in r
        assert "critical_files" in r
        assert isinstance(r["critical_files"], list)

    # Validate coverage of both public and private repos
    has_public = any(not r["private"] for r in repos)
    has_private = any(r["private"] for r in repos)
    assert has_public is True
    assert has_private is True


def test_audit_entire_github_ecosystem():
    res = audit_entire_github_ecosystem()
    assert res["status"] == "success"
    assert res["total_repositories_found"] >= 3
    assert res["public_repositories"] >= 1
    assert res["private_repositories"] >= 1
    assert res["total_critical_files_indexed"] > 0
    assert len(res["repositories"]) == res["total_repositories_found"]


def test_mcp_audit_entire_github_ecosystem():
    server = HunterMCPServer()
    manifest = server.get_tools_manifest()
    tool_names = [t["name"] for t in manifest]
    assert "audit_entire_github_ecosystem" in tool_names

    res = server.call_tool("audit_entire_github_ecosystem", {})
    assert res["status"] == "success"
    assert res["total_repositories_found"] >= 3


def test_autogen_swarm_ecosystem_audit():
    swarm = AutoGenThreatSwarm()
    result = swarm.audit_github_ecosystem()
    assert result["swarm_status"] == "COMPLETED"
    assert "ecosystem" in result
    assert "analysis" in result
    assert result["ecosystem"]["status"] == "success"


def test_orchestrator_ecosystem_endpoint():
    res = asyncio.run(scan_entire_ecosystem_endpoint())
    assert res["status"] == "success"
    assert res["total_repositories_found"] >= 3
    assert res["total_critical_files_indexed"] >= 1
