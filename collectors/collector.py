"""Lightweight streaming Linux telemetry collector daemon.

Tails target system and authentication logs, extracts security IOCs using compiled regex,
and streams normalized JSON payloads to the AI Threat Orchestrator.
"""

import logging
import os
import re
import time
from collections.abc import Generator
from typing import Any

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [Collector] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TelemetryCollector")

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/var/log/target/auth.log")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://ai-orchestrator:8000/analyze")

# Compiled regex patterns for Linux / sshd authentication events
FAILED_PASSWORD_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)"
)
INVALID_USER_PATTERN = re.compile(
    r"Invalid user (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)"
)
ACCEPTED_PASSWORD_PATTERN = re.compile(
    r"Accepted password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)"
)
CONNECTION_CLOSED_PATTERN = re.compile(
    r"Connection closed by (?:authenticating user (?P<user>\S+) )?(?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+) \[preauth\]"
)


def parse_ssh_log(log_line: str) -> dict[str, Any] | None:
    """Extracts security metadata from Linux sshd / auth.log entries."""
    if not log_line or not isinstance(log_line, str):
        return None

    line = log_line.strip()

    # 1. Check failed password
    match = FAILED_PASSWORD_PATTERN.search(line)
    if match:
        return {
            "service": "sshd",
            "event_type": "authentication_failed",
            "target_user": match.group("user"),
            "source_ip": match.group("ip"),
            "source_port": match.group("port"),
            "raw_log": line,
        }

    # 2. Check invalid user attempt
    match = INVALID_USER_PATTERN.search(line)
    if match:
        return {
            "service": "sshd",
            "event_type": "invalid_user_attempt",
            "target_user": match.group("user"),
            "source_ip": match.group("ip"),
            "source_port": match.group("port"),
            "raw_log": line,
        }

    # 3. Check accepted password (useful for tracking compromised accounts)
    match = ACCEPTED_PASSWORD_PATTERN.search(line)
    if match:
        return {
            "service": "sshd",
            "event_type": "authentication_success",
            "target_user": match.group("user"),
            "source_ip": match.group("ip"),
            "source_port": match.group("port"),
            "raw_log": line,
        }

    # 4. Check pre-auth disconnect (common indicator of scanner / banner grab)
    match = CONNECTION_CLOSED_PATTERN.search(line)
    if match:
        return {
            "service": "sshd",
            "event_type": "preauth_disconnect_scan",
            "target_user": match.group("user") or "unknown",
            "source_ip": match.group("ip"),
            "source_port": match.group("port"),
            "raw_log": line,
        }

    return None


def follow_log(
    file_path: str, poll_interval: float = 0.5
) -> Generator[str, None, None]:
    """Generator mimicking 'tail -f' with resilient wait for file creation."""
    while not os.path.exists(file_path):
        logger.info(
            f"Target log {file_path} not found. Awaiting honeypot initialization..."
        )
        time.sleep(2)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(poll_interval)
                continue
            yield line


def forward_payload(
    payload: dict[str, Any], url: str = ORCHESTRATOR_URL, timeout: int = 5
) -> bool:
    """Dispatches extracted telemetry payload to the AI Orchestrator."""
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        if response.status_code in (200, 202):
            logger.info(
                f"Successfully routed event ({payload['event_type']}) from {payload['source_ip']} to AI"
            )
            return True
        logger.warning(
            f"Orchestrator returned unexpected status {response.status_code}"
        )
        return False
    except requests.exceptions.RequestException as exc:
        logger.error(f"Failed to communicate with AI Orchestrator at {url}: {exc}")
        return False


def main():
    """Main daemon loop."""
    logger.info(f"Starting Telemetry Collector daemon. Target: {LOG_FILE_PATH}")
    for line in follow_log(LOG_FILE_PATH):
        event = parse_ssh_log(line)
        if event:
            forward_payload(event)


if __name__ == "__main__":
    main()
