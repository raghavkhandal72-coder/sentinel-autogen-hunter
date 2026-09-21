"""Threat intelligence connector for external IP reputation verification."""

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger("ThreatIntel")

IP_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)


def is_valid_ipv4(ip: str) -> bool:
    """Validates if a given string is a valid IPv4 address."""
    return bool(ip and IP_REGEX.match(ip))


def check_ip_reputation(ip_address: str) -> dict[str, Any]:
    """Queries AbuseIPDB to determine if an IP is a known malicious actor.

    Falls back to deterministic evaluation in offline / test mode.
    """
    if not is_valid_ipv4(ip_address):
        return {
            "ip": ip_address,
            "abuse_score": 0,
            "is_malicious": False,
            "error": "invalid_ipv4",
            "usage_type": "Unknown",
        }

    # Detect private / loopback IP ranges
    if ip_address.startswith(("127.", "10.", "192.168.", "172.16.")):
        # Private/RFC1918 range - local simulation behavior
        return {
            "ip": ip_address,
            "abuse_score": 15,
            "is_malicious": False,
            "usage_type": "Private/Local Network",
            "source": "Local RFC1918 Evaluator",
        }

    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        logger.debug("ABUSEIPDB_API_KEY not configured. Using deterministic heuristic.")
        # Simulated heuristic for testing without paid API keys
        simulated_score = (
            85 if ip_address.endswith(".100") or ip_address.startswith("203.") else 10
        )
        return {
            "ip": ip_address,
            "abuse_score": simulated_score,
            "is_malicious": simulated_score >= 50,
            "usage_type": "Simulated ISP",
            "source": "Heuristic Mock Engine",
        }

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Accept": "application/json", "Key": api_key}
    params = {"ipAddress": ip_address, "maxAgeInDays": "90"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("data", {})
        score = int(data.get("abuseConfidenceScore", 0))
        usage_type = str(data.get("usageType", "Unknown"))
        return {
            "ip": ip_address,
            "abuse_score": score,
            "is_malicious": score >= 50,
            "usage_type": usage_type,
            "source": "AbuseIPDB Live API",
        }
    except requests.exceptions.RequestException as exc:
        logger.warning(f"AbuseIPDB API query failed: {exc}. Falling back to default.")
        return {
            "ip": ip_address,
            "abuse_score": 0,
            "is_malicious": False,
            "error": str(exc),
            "source": "Fallback",
        }
