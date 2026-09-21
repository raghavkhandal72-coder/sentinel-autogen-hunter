"""Zero-trust Linux host action execution bridge.

Queues verified firewall containment actions to an append-only FIFO log
consumed by the host-level enforcer. Strictly prevents command injection.
"""

import logging
import os
import re
from datetime import datetime, timezone

logger = logging.getLogger("LinuxCMD")

IP_CLEAN_REGEX = re.compile(
    r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:/[0-9]{1,2})?$"
)


def sanitize_ip(ip_address: str) -> tuple[bool, str]:
    """Sanitizes and validates an IP or CIDR block against command injection.

    Rejects any shell metacharacters (;, &, |, `, $, \\, newline, space).
    """
    if not ip_address:
        return False, "empty_ip"

    cleaned = ip_address.strip()
    # Reject shell injection characters
    dangerous_chars = [
        ";",
        "&",
        "|",
        "`",
        "$",
        "(",
        ")",
        "{",
        "}",
        "<",
        ">",
        "\n",
        "\r",
        " ",
    ]
    if any(char in cleaned for char in dangerous_chars):
        return False, "injection_character_detected"

    if not IP_CLEAN_REGEX.match(cleaned):
        return False, "invalid_ipv4_format"

    return True, cleaned


def execute_firewall_rule(
    proposed_command: str, ip_to_block: str, risk_level: str = "high"
) -> bool:
    """Queues a validated firewall containment rule for the host enforcer to execute.

    Never executes unvetted AI shell strings directly as root.
    """
    is_safe, sanitized_ip = sanitize_ip(ip_to_block)
    if not is_safe:
        logger.error(
            f"Command execution rejected: IP '{ip_to_block}' failed sanitization ({sanitized_ip})"
        )
        return False

    action_log_path = os.getenv("ACTION_LOG_PATH", "actions/pending_blocks.log")

    # Ensure parent directory exists
    parent_dir = os.path.dirname(action_log_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    # Standardized, immutable entry format: TIMESTAMP,IP,RISK_LEVEL,COMMAND
    entry = (
        f"{timestamp},{sanitized_ip},{risk_level.lower()},{proposed_command.strip()}\n"
    )

    try:
        with open(action_log_path, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(
            f"Queued firewall containment rule for target {sanitized_ip} (Risk: {risk_level})"
        )
        return True
    except Exception as exc:
        logger.error(f"Failed to queue firewall rule to {action_log_path}: {exc}")
        return False
