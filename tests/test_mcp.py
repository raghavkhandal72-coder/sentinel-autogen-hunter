"""Unit tests for the Model Context Protocol (MCP) server."""

from mcp.mcp_server import HunterMCPServer


def test_mcp_tools_manifest():
    """Verify MCP tools manifest matches standard JSON-RPC schema requirements."""
    tools = HunterMCPServer.get_tools_manifest()
    assert isinstance(tools, list)
    assert len(tools) >= 4

    tool_names = [t["name"] for t in tools]
    assert "check_ip_reputation" in tool_names
    assert "queue_firewall_containment" in tool_names
    assert "send_teams_alert" in tool_names
    assert "stream_to_sentinel" in tool_names


def test_mcp_call_check_ip_reputation():
    """Verify MCP invocation of check_ip_reputation tool."""
    result = HunterMCPServer.call_tool(
        "check_ip_reputation", {"ip_address": "203.0.113.19"}
    )
    assert "ip" in result
    assert result["ip"] == "203.0.113.19"
    assert "abuse_score" in result


def test_mcp_call_queue_firewall(tmp_path, monkeypatch):
    """Verify MCP invocation of firewall containment queue tool."""
    log_file = tmp_path / "mcp_actions.log"
    monkeypatch.setenv("ACTION_LOG_PATH", str(log_file))

    result = HunterMCPServer.call_tool(
        "queue_firewall_containment",
        {
            "ip_to_block": "198.51.100.99",
            "proposed_command": "iptables -I DOCKER-USER 1 -s 198.51.100.99 -j DROP",
            "risk_level": "medium",
        },
    )
    assert result["success"] is True
    assert result["ip_blocked"] == "198.51.100.99"


def test_mcp_call_send_teams_alert():
    """Verify MCP invocation of teams alert tool."""
    result = HunterMCPServer.call_tool(
        "send_teams_alert",
        {
            "threat_type": "ssh_brute_force",
            "attacker_ip": "198.51.100.99",
            "recommended_action": "DROP rule applied",
            "risk_level": "High",
        },
    )
    assert result["success"] is True


def test_mcp_call_unknown_tool():
    """Verify MCP handles unknown tool calls gracefully without exceptions."""
    result = HunterMCPServer.call_tool("unregistered_tool", {})
    assert "error" in result
    assert "Unknown MCP tool" in result["error"]
