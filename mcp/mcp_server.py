"""Model Context Protocol (MCP) Server for Sentinel-AutoGen-Hunter.

Exposes security tools to Microsoft Security Copilot, AutoGen, and external LLMs:
- check_ip_reputation: Real-time AbuseIPDB threat intelligence
- queue_firewall_containment: Zero-trust DOCKER-USER firewall enforcement
- send_teams_alert: Microsoft Teams Adaptive Card dispatch
- stream_to_sentinel: Azure Log Analytics / Sentinel ingestion
"""

import json
import logging
import sys
from typing import Any

from agents.tools.linux_cmd import execute_firewall_rule
from agents.tools.notifier import send_teams_alert
from agents.tools.sentinel_connector import push_to_sentinel
from agents.tools.threat_intel import check_ip_reputation

logger = logging.getLogger("HunterMCPServer")


class HunterMCPServer:
    """Production MCP server implementing tool discovery and invocation."""

    @staticmethod
    def get_tools_manifest() -> list[dict[str, Any]]:
        """Returns the MCP tool definitions conforming to the Model Context Protocol."""
        return [
            {
                "name": "check_ip_reputation",
                "description": "Queries global threat intelligence (AbuseIPDB) to score an IP address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ip_address": {
                            "type": "string",
                            "description": "The IPv4 address to inspect",
                        }
                    },
                    "required": ["ip_address"],
                },
            },
            {
                "name": "queue_firewall_containment",
                "description": "Safely enqueues an iptables DOCKER-USER containment rule for host enforcement.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ip_to_block": {
                            "type": "string",
                            "description": "The attacker IPv4 address to isolate",
                        },
                        "proposed_command": {
                            "type": "string",
                            "description": "The specific iptables rule command",
                        },
                        "risk_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": "high",
                        },
                    },
                    "required": ["ip_to_block", "proposed_command"],
                },
            },
            {
                "name": "send_teams_alert",
                "description": "Dispatches an enterprise Adaptive Card security incident alert to Microsoft Teams.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "threat_type": {"type": "string"},
                        "attacker_ip": {"type": "string"},
                        "recommended_action": {"type": "string"},
                        "risk_level": {"type": "string", "default": "High"},
                    },
                    "required": ["threat_type", "attacker_ip", "recommended_action"],
                },
            },
            {
                "name": "stream_to_sentinel",
                "description": "Streams autonomous threat detection and KQL telemetry into Microsoft Sentinel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "threat_event": {
                            "type": "object",
                            "description": "Structured telemetry payload including MITRE tactics and KQL",
                        }
                    },
                    "required": ["threat_event"],
                },
            },
            {
                "name": "scan_iac_manifest",
                "description": "Shift-left pre-deployment static analysis of Kubernetes manifests or Terraform files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The YAML or HCL configuration text to analyze",
                        },
                        "filename": {
                            "type": "string",
                            "description": "File name e.g. deployment.yaml or main.tf",
                            "default": "manifest.yaml",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "query_cloud_posture_sql",
                "description": "Executes an ANSI SQL query across multi-cloud infrastructure assets to audit security posture.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "Read-only SELECT query against the cloud_assets table",
                        }
                    },
                    "required": ["sql_query"],
                },
            },
            {
                "name": "ingest_all_repos",
                "description": "Autonomously audits commit streams across all repositories owned by the user for hardcoded secrets and backdoor patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "audit_entire_github_ecosystem",
                "description": "Globally indexes all public and private repositories, organizations, and critical configuration files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "github_token": {
                            "type": "string",
                            "description": "Optional PAT token. Defaults to environment variable.",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "synthesize_universal_detection_rule",
                "description": "Converts threat IOCs into Sigma YAML, Sentinel KQL, Splunk SPL, and Elastic ES|QL queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "threat_type": {"type": "string", "description": "Type of threat e.g. ssh_brute_force, port_scan"},
                        "attacker_ip": {"type": "string", "description": "Attacker IPv4 address"},
                        "target_asset": {"type": "string", "description": "Target server or workload name"},
                    },
                    "required": ["threat_type"],
                },
            },
            {
                "name": "deploy_honeytoken",
                "description": "Deploys an active cryptographic canary honeytoken tripwire (AWS key, GitHub PAT, Azure secret, DB URI).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token_type": {"type": "string", "enum": ["aws_key", "github_token", "azure_secret", "db_connection"], "default": "aws_key"},
                        "asset_name": {"type": "string", "default": "prod-api"},
                        "deployment_path": {"type": "string", "default": "config/.env"},
                    },
                    "required": ["token_type"],
                },
            },
            {
                "name": "trigger_honeytoken_tripwire",
                "description": "Activates canary tripwire upon attacker credential usage and executes immediate DOCKER-USER firewall containment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token_value": {"type": "string", "description": "Compromised honeytoken string"},
                        "source_ip": {"type": "string", "description": "Attacker IP"},
                    },
                    "required": ["token_value", "source_ip"],
                },
            },
        ]

    @staticmethod
    def call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatches an MCP tool invocation to the corresponding tool handler."""
        try:
            if tool_name == "check_ip_reputation":
                ip = arguments.get("ip_address", "")
                return check_ip_reputation(ip)

            elif tool_name == "queue_firewall_containment":
                ip = arguments.get("ip_to_block", "")
                cmd = arguments.get("proposed_command", "")
                risk = arguments.get("risk_level", "high")
                success = execute_firewall_rule(cmd, ip, risk)
                return {"success": success, "ip_blocked": ip, "risk_level": risk}

            elif tool_name == "send_teams_alert":
                success = send_teams_alert(
                    threat_type=arguments.get("threat_type", "Unknown"),
                    attacker_ip=arguments.get("attacker_ip", "0.0.0.0"),
                    recommended_action=arguments.get("recommended_action", ""),
                    risk_level=arguments.get("risk_level", "High"),
                )
                return {"success": success}

            elif tool_name == "stream_to_sentinel":
                event = arguments.get("threat_event", {})
                success = push_to_sentinel(event)
                return {"success": success}

            elif tool_name == "scan_iac_manifest":
                from agents.tools.iac_analyzer import analyze_iac_content

                content = arguments.get("content", "")
                filename = arguments.get("filename", "manifest.yaml")
                return analyze_iac_content(content, filename)

            elif tool_name == "query_cloud_posture_sql":
                from agents.tools.cspm_sql import get_cspm_db

                sql = arguments.get("sql_query", "SELECT * FROM cloud_assets")
                db = get_cspm_db()
                results = db.execute_query(sql)
                return {"success": True, "count": len(results), "assets": results}

            elif tool_name == "ingest_all_repos":
                from agents.tools.github_scanner import ingest_all_repos

                return ingest_all_repos()

            elif tool_name == "audit_entire_github_ecosystem":
                from agents.tools.global_repo_crawler import (
                    audit_entire_github_ecosystem,
                )

                token = arguments.get("github_token")
                return audit_entire_github_ecosystem(token)

            elif tool_name == "synthesize_universal_detection_rule":
                from agents.sigma_engine import synthesize_universal_matrix

                return synthesize_universal_matrix(arguments)

            elif tool_name == "deploy_honeytoken":
                from agents.deception_engine import generate_honeytoken

                token_type = arguments.get("token_type", "aws_key")
                asset = arguments.get("asset_name", "prod-api")
                path = arguments.get("deployment_path", "config/.env")
                return generate_honeytoken(token_type, asset, path)

            elif tool_name == "trigger_honeytoken_tripwire":
                from agents.deception_engine import trigger_tripwire

                token_val = arguments.get("token_value", "")
                ip = arguments.get("source_ip", "198.51.100.42")
                return trigger_tripwire(token_val, ip)

            else:
                return {"error": f"Unknown MCP tool: {tool_name}"}

        except Exception as exc:
            logger.error(f"Error invoking MCP tool {tool_name}: {exc}")
            return {"error": str(exc), "success": False}


def run_stdio_server():
    """Starts the standard IO JSON-RPC loop for MCP integration."""
    server = HunterMCPServer()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            req_type = request.get("method")
            req_id = request.get("id")

            if req_type == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": server.get_tools_manifest()},
                }
            elif req_type == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                tool_result = server.call_tool(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(tool_result)}]
                    },
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": "Method not found"},
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(exc)},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
