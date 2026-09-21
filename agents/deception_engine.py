"""Active Defense & Canary Honeytoken Deception Engine.

Deploys deceptive digital assets (decoy AWS keys, GitHub PATs, Azure secrets,
and database connection strings) to detect unauthorized reconnaissance,
credential harvesting, and lateral movement. Triggers instant Zero-Trust containment.
"""

import hashlib
import hmac
import logging
import secrets
import time
from typing import Any

from .base_agent import BaseAgent
from .tools.linux_cmd import execute_firewall_rule
from .tools.notifier import send_teams_alert
from .tools.sentinel_connector import push_to_sentinel

logger = logging.getLogger("DeceptionEngine")

# In-memory registry of deployed canary tokens
HONEYTOKEN_REGISTRY: dict[str, dict[str, Any]] = {}
BREACH_INCIDENTS: list[dict[str, Any]] = []

SECRET_SALT = "sentinel-canary-secret-salt-2026"


def generate_honeytoken(
    token_type: str = "aws_key",
    asset_name: str = "production-app",
    deployment_path: str = "config/.env",
) -> dict[str, Any]:
    """Generates a high-fidelity deceptive credential with embedded verification signature."""
    timestamp = int(time.time())
    raw_entropy = secrets.token_hex(8)

    # Cryptographic signature to verify genuineness offline
    sig = hmac.new(
        SECRET_SALT.encode(), f"{token_type}:{timestamp}:{raw_entropy}".encode(), hashlib.sha256
    ).hexdigest()[:8]

    token_value = ""
    token_id = f"canary-{raw_entropy[:6]}"

    if token_type == "aws_key":
        token_value = f"AKIA{secrets.token_hex(8).upper()}{sig.upper()}"
    elif token_type == "github_token":
        token_value = f"ghp_{secrets.token_urlsafe(16)}_{sig}"
    elif token_type == "azure_secret":
        token_value = f"az_{secrets.token_hex(12)}_{sig}"
    elif token_type == "db_connection":
        token_value = f"postgresql://canary_admin:{sig}@decoy-db.internal:5432/{asset_name}"
    else:
        token_value = f"canary_token_{raw_entropy}_{sig}"

    honeytoken_record = {
        "token_id": token_id,
        "token_type": token_type,
        "token_value": token_value,
        "asset_name": asset_name,
        "deployment_path": deployment_path,
        "created_at": timestamp,
        "status": "ARMED",
        "tripped_count": 0,
        "mitre_technique": "T1078.004 - Valid Accounts: Cloud Accounts",
    }

    HONEYTOKEN_REGISTRY[token_value] = honeytoken_record
    logger.info(f"Deployed Honeytoken [{token_id}] ({token_type}) for asset '{asset_name}'")
    return honeytoken_record


def verify_honeytoken(token_value: str) -> dict[str, Any] | None:
    """Verifies whether a token is an active armed canary tripwire."""
    return HONEYTOKEN_REGISTRY.get(token_value)


def trigger_tripwire(
    token_value: str,
    source_ip: str,
    action: str = "unauthorized_credential_usage",
    user_agent: str = "curl/8.4.0",
) -> dict[str, Any]:
    """Activates canary tripwire upon attacker interaction and enqueues immediate zero-trust isolation."""
    record = verify_honeytoken(token_value)
    now = int(time.time())

    if not record:
        # Check if matches pattern even if not in current memory table
        is_pattern_match = token_value.startswith("AKIA") or token_value.startswith("ghp_") or "canary" in token_value
        if is_pattern_match:
            record = {
                "token_id": "canary-synthetic",
                "token_type": "decoy_credential",
                "token_value": token_value,
                "asset_name": "unknown_asset",
                "deployment_path": "/unknown",
                "created_at": now,
                "status": "ARMED",
                "tripped_count": 0,
                "mitre_technique": "T1552 - Unsecured Credentials",
            }
        else:
            return {
                "tripwire_triggered": False,
                "message": "Token not recognized as an active honeytoken tripwire.",
            }

    record["status"] = "TRIPPED"
    record["tripped_count"] += 1
    record["last_tripped_at"] = now
    record["last_tripped_ip"] = source_ip

    incident_id = f"tripwire-{secrets.token_hex(4)}"
    containment_cmd = f"iptables -I DOCKER-USER 1 -s {source_ip} -j DROP"

    # 1. Execute instant firewall isolation
    firewall_success = execute_firewall_rule(
        containment_cmd, source_ip, risk_level="critical"
    )

    # 2. Dispatch high-urgency Teams Alert
    send_teams_alert(
        threat_type=f"HONEYTOKEN BREACH: {record['token_type'].upper()}",
        attacker_ip=source_ip,
        recommended_action=f"Host isolated immediately via DOCKER-USER. Decoy asset '{record['asset_name']}' compromised.",
        risk_level="Critical",
    )

    # 3. Stream breach event into Microsoft Sentinel
    sentinel_event = {
        "IncidentId": incident_id,
        "ThreatType": "canary_honeytoken_breached",
        "AttackerIP": source_ip,
        "TargetAsset": record["asset_name"],
        "MitreTechnique": record["mitre_technique"],
        "HoneytokenType": record["token_type"],
        "UserAgent": user_agent,
        "Severity": "Critical",
        "AutonomousAction": "Host Isolated via iptables",
    }
    push_to_sentinel(sentinel_event)

    incident_summary = {
        "incident_id": incident_id,
        "tripwire_triggered": True,
        "token_id": record["token_id"],
        "token_type": record["token_type"],
        "asset_compromised": record["asset_name"],
        "attacker_ip": source_ip,
        "firewall_isolated": firewall_success,
        "mitre_technique": record["mitre_technique"],
        "timestamp": now,
        "urgency": "CRITICAL",
    }

    BREACH_INCIDENTS.append(incident_summary)
    logger.warning(f"🚨 CANARY BREACH DETECTED from IP {source_ip}! Asset '{record['asset_name']}' triggered tripwire.")
    return incident_summary


def list_honeytokens() -> list[dict[str, Any]]:
    """Returns all currently deployed canary honeytokens."""
    return list(HONEYTOKEN_REGISTRY.values())


def list_breaches() -> list[dict[str, Any]]:
    """Returns history of canary tripwire incidents."""
    return BREACH_INCIDENTS


class DeceptionAgent(BaseAgent):
    """Autonomous Agent managing active deception and honeytoken tripwires."""

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="DeceptionAgent", model=model)

    def analyze(self, audit_context: dict[str, Any]) -> dict[str, Any]:
        """Processes deception commands or evaluates potential tripwire triggers."""
        action = audit_context.get("action", "deploy")
        if action == "deploy":
            token_type = audit_context.get("token_type", "aws_key")
            asset = audit_context.get("asset_name", "prod-cluster")
            path = audit_context.get("deployment_path", ".env")
            return generate_honeytoken(token_type, asset, path)
        elif action == "tripwire":
            token_val = audit_context.get("token_value", "")
            source_ip = audit_context.get("source_ip", "198.51.100.42")
            return trigger_tripwire(token_val, source_ip)
        return {"status": "ok", "honeytokens": list_honeytokens()}
