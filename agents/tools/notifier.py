"""Enterprise SecOps notification module for Microsoft Teams and Slack."""

import logging
import os

import requests

logger = logging.getLogger("TeamsNotifier")


def send_teams_alert(
    threat_type: str,
    attacker_ip: str,
    recommended_action: str,
    risk_level: str = "High",
    confidence_score: float = 0.95,
) -> bool:
    """Sends a formatted Adaptive Card to a Microsoft Teams channel via Webhook.

    Returns True if successfully sent, or True in mock mode when no webhook is set.
    """
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        logger.info(
            f"[SecOps Alert Simulation] Threat: {threat_type} | Attacker: {attacker_ip} | "
            f"Action: {recommended_action} | Risk: {risk_level} (Confidence: {confidence_score:.2f})"
        )
        return True

    # High / Critical: Red; Medium: Orange; Low: Blue
    color_map = {
        "critical": "D83B01",
        "high": "E81123",
        "medium": "FFAA44",
        "low": "0078D4",
    }
    theme_color = color_map.get(risk_level.lower(), "E81123")

    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": theme_color,
        "summary": f"Sentinel-AutoGen-Hunter: {threat_type} Detected",
        "sections": [
            {
                "activityTitle": "Autonomous Threat Hunter Notification",
                "activitySubtitle": f"Severity: {risk_level.upper()} | Confidence: {confidence_score * 100:.1f}%",
                "facts": [
                    {"name": "Threat Classification:", "value": threat_type},
                    {"name": "Attacker IP:", "value": attacker_ip},
                    {
                        "name": "Autonomous Remediation:",
                        "value": f"`{recommended_action}`",
                    },
                    {"name": "Engine:", "value": "Microsoft AutoGen + Sentinel Hunter"},
                ],
                "markdown": True,
            }
        ],
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(
            f"Dispatched enterprise alert to Microsoft Teams for IP {attacker_ip}"
        )
        return True
    except requests.exceptions.RequestException as exc:
        logger.error(f"Failed to deliver Microsoft Teams alert: {exc}")
        return False
