"""Tests for Active Defense and Canary Honeytoken Deception Engine."""

import pytest

from agents.deception_engine import (
    DeceptionAgent,
    generate_honeytoken,
    list_honeytokens,
    trigger_tripwire,
    verify_honeytoken,
)
from agents.orchestrator import app
from mcp.mcp_server import HunterMCPServer


def test_generate_honeytoken_types():
    aws_token = generate_honeytoken(token_type="aws_key", asset_name="prod-s3")
    assert aws_token["token_value"].startswith("AKIA")
    assert aws_token["status"] == "ARMED"
    assert aws_token["token_type"] == "aws_key"

    gh_token = generate_honeytoken(token_type="github_token", asset_name="repo-backend")
    assert gh_token["token_value"].startswith("ghp_")
    assert gh_token["status"] == "ARMED"

    db_token = generate_honeytoken(token_type="db_connection", asset_name="users-db")
    assert "postgresql://" in db_token["token_value"]


def test_verify_honeytoken_lookup():
    token = generate_honeytoken(token_type="azure_secret", asset_name="azure-app")
    record = verify_honeytoken(token["token_value"])
    assert record is not None
    assert record["asset_name"] == "azure-app"


def test_trigger_tripwire_quarantine():
    token = generate_honeytoken(token_type="aws_key", asset_name="prod-billing-db")
    attacker_ip = "203.0.113.77"

    result = trigger_tripwire(token["token_value"], source_ip=attacker_ip)
    assert result["tripwire_triggered"] is True
    assert result["asset_compromised"] == "prod-billing-db"
    assert result["attacker_ip"] == attacker_ip
    assert result["urgency"] == "CRITICAL"
    assert result["firewall_isolated"] is True

    # Verify status changed in registry
    updated_record = verify_honeytoken(token["token_value"])
    assert updated_record["status"] == "TRIPPED"
    assert updated_record["tripped_count"] == 1


def test_deception_agent_workflow():
    agent = DeceptionAgent()
    # Test deploy action
    deploy_res = agent.analyze({"action": "deploy", "token_type": "aws_key", "asset_name": "agent-cluster"})
    assert deploy_res["status"] == "ARMED"

    # Test tripwire action
    trip_res = agent.analyze({"action": "tripwire", "token_value": deploy_res["token_value"], "source_ip": "198.51.100.88"})
    assert trip_res["tripwire_triggered"] is True


def test_orchestrator_deception_api_endpoints():
    import asyncio
    from agents.orchestrator import (
        HoneytokenDeployRequest,
        HoneytokenTripwireRequest,
        deploy_honeytoken_endpoint,
        list_honeytokens_endpoint,
        trigger_tripwire_endpoint,
    )

    # 1. Deploy honeytoken
    deploy_req = HoneytokenDeployRequest(
        token_type="github_token", asset_name="prod-gateway", deployment_path=".github/secrets"
    )
    token_data = asyncio.run(deploy_honeytoken_endpoint(deploy_req))
    assert "token_value" in token_data

    # 2. List honeytokens
    list_data = asyncio.run(list_honeytokens_endpoint())
    assert list_data["total_armed"] > 0

    # 3. Trigger tripwire
    trip_req = HoneytokenTripwireRequest(
        token_value=token_data["token_value"], source_ip="198.51.100.99"
    )
    trip_data = asyncio.run(trigger_tripwire_endpoint(trip_req))
    assert trip_data["tripwire_triggered"] is True


def test_mcp_deception_tools():
    # Deploy tool
    deploy_res = HunterMCPServer.call_tool(
        "deploy_honeytoken",
        {"token_type": "aws_key", "asset_name": "mcp-test-asset", "deployment_path": "config.yaml"},
    )
    assert "token_value" in deploy_res

    # Tripwire tool
    trip_res = HunterMCPServer.call_tool(
        "trigger_honeytoken_tripwire",
        {"token_value": deploy_res["token_value"], "source_ip": "192.0.2.55"},
    )
    assert trip_res["tripwire_triggered"] is True
