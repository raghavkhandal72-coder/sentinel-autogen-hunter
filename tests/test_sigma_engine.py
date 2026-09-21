"""Tests for Multi-SIEM Universal Sigma Transpiler and Detection Synthesis."""

import pytest

from agents.orchestrator import app
from agents.sigma_engine import (
    SigmaEngineAgent,
    generate_sigma_yaml,
    synthesize_universal_matrix,
    transpile_to_elastic_esql,
    transpile_to_kql,
    transpile_to_splunk_spl,
)
from mcp.mcp_server import HunterMCPServer


@pytest.fixture
def sample_threat():
    return {
        "threat_type": "ssh_brute_force",
        "attacker_ip": "198.51.100.42",
        "target_asset": "prod-k8s-ingress",
    }


def test_generate_sigma_yaml_format(sample_threat):
    yaml_output = generate_sigma_yaml(sample_threat)
    assert "title: Autonomous Hunt:" in yaml_output
    assert "status: test" in yaml_output
    assert "logsource:" in yaml_output
    assert "198.51.100.42" in yaml_output
    assert "attack.credential_access" in yaml_output
    assert "attack.t1110.001" in yaml_output
    assert "level: high" in yaml_output


def test_transpile_to_kql(sample_threat):
    kql = transpile_to_kql(sample_threat)
    assert "AutoGenThreatHunt_CL" in kql
    assert "TimeGenerated >= ago(24h)" in kql
    assert 'AttackerIP == "198.51.100.42"' in kql
    assert "summarize EventCount" in kql


def test_transpile_to_splunk_spl(sample_threat):
    spl = transpile_to_splunk_spl(sample_threat)
    assert "index=security" in spl
    assert 'src_ip="198.51.100.42"' in spl
    assert "stats count" in spl


def test_transpile_to_elastic_esql(sample_threat):
    esql = transpile_to_elastic_esql(sample_threat)
    assert "FROM logs-*" in esql
    assert 'source.ip == "198.51.100.42"' in esql
    assert "STATS event_count = COUNT(*)" in esql


def test_synthesize_universal_matrix(sample_threat):
    matrix = synthesize_universal_matrix(sample_threat)
    assert matrix["status"] == "success"
    assert "sigma_yaml" in matrix["detection_rules"]
    assert "microsoft_sentinel_kql" in matrix["detection_rules"]
    assert "splunk_spl" in matrix["detection_rules"]
    assert "elastic_esql" in matrix["detection_rules"]
    assert "aws_cloudwatch" in matrix["detection_rules"]
    assert len(matrix["platforms_supported"]) == 5


def test_sigma_engine_agent_execution(sample_threat):
    agent = SigmaEngineAgent()
    res = agent.analyze(sample_threat)
    assert res["status"] == "success"
    assert "detection_rules" in res


def test_orchestrator_sigma_api_endpoint(sample_threat):
    import asyncio
    from agents.orchestrator import SigmaSynthesizeRequest, synthesize_sigma_endpoint

    req = SigmaSynthesizeRequest(
        threat_type=sample_threat["threat_type"],
        source_ip=sample_threat["attacker_ip"],
        target_asset=sample_threat["target_asset"],
    )
    data = asyncio.run(synthesize_sigma_endpoint(req))
    assert data["status"] == "success"
    assert "detection_rules" in data


def test_mcp_synthesize_universal_rule(sample_threat):
    res = HunterMCPServer.call_tool("synthesize_universal_detection_rule", sample_threat)
    assert res["status"] == "success"
    assert "sigma_yaml" in res["detection_rules"]
