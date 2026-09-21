"""Microsoft Sentinel / Azure Log Analytics ingestion client."""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger("SentinelConnector")


def push_to_sentinel(
    threat_event: Dict[str, Any], log_type: str = "AutoGenThreatHunt_CL"
) -> bool:
    """Streams structured security telemetry directly to Microsoft Sentinel.

    If Azure credentials (SENTINEL_WORKSPACE_ID, SENTINEL_SHARED_KEY) are configured,
    posts via Azure Data Ingestion API. Otherwise, logs formatted Sentinel payload for testing.
    """
    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    shared_key = os.getenv("SENTINEL_SHARED_KEY")

    payload = {
        "TimeGenerated": datetime.now(timezone.utc).isoformat() + "Z",
        "ThreatType": threat_event.get("threat_type", "Unknown"),
        "AttackerIP": threat_event.get("attacker_ip", "0.0.0.0"),
        "TargetAsset": threat_event.get("target_asset", "unknown-host"),
        "ConfidenceScore": float(threat_event.get("confidence_score", 0.0)),
        "ProposedCommand": threat_event.get("proposed_command", ""),
        "RollbackCommand": threat_event.get("rollback_command", ""),
        "RiskLevel": threat_event.get("risk_level", "Medium"),
        "MitreTechnique": threat_event.get("mitre_technique_id", "T1110"),
        "KqlQuery": threat_event.get("kql_query", ""),
        "OrchestratorVersion": "1.0.0-enterprise",
    }

    if not workspace_id or not shared_key:
        logger.debug(
            f"[Sentinel Ingestion Simulation] LogType: {log_type} | Event: {json.dumps(payload)}"
        )
        return True

    # Real Azure Log Analytics HTTP Data Collector API integration
    try:
        import base64
        import hashlib
        import hmac

        import requests

        body = json.dumps([payload])
        content_length = len(body)
        rfc1123date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        string_to_hash = f"POST\n{content_length}\napplication/json\nx-ms-date:{rfc1123date}\n/api/logs"
        hashed = hmac.new(
            base64.b64decode(shared_key), string_to_hash.encode("utf-8"), hashlib.sha256
        ).digest()
        signature = base64.b64encode(hashed).decode("utf-8")
        authorization = f"SharedKey {workspace_id}:{signature}"

        url = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }

        response = requests.post(url, data=body, headers=headers, timeout=5)
        response.raise_for_status()
        logger.info(
            f"Successfully ingested telemetry into Microsoft Sentinel ({log_type})"
        )
        return True
    except Exception as exc:
        logger.warning(f"Failed to post telemetry to Microsoft Sentinel: {exc}")
        return False
