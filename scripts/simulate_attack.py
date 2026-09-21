"""Interactive and automated attack simulator for Sentinel-AutoGen-Hunter.

Enables instant local verification of the multi-agent detection and remediation pipeline
without requiring Kali Linux or external penetration testing suites.
"""

import argparse
import logging
import sys
import time

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [Simulator] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AttackSimulator")

DEFAULT_ORCHESTRATOR = "http://localhost:8000/analyze"

SIMULATED_ATTACKS = {
    "ssh_brute_force": {
        "service": "sshd",
        "event_type": "authentication_failed",
        "target_user": "admin",
        "source_ip": "203.0.113.42",
        "source_port": "49152",
        "raw_log": "Failed password for invalid user admin from 203.0.113.42 port 49152 ssh2",
    },
    "port_scan": {
        "service": "sshd",
        "event_type": "preauth_disconnect_scan",
        "target_user": "unknown",
        "source_ip": "198.51.100.23",
        "source_port": "58301",
        "raw_log": "Connection closed by 198.51.100.23 port 58301 [preauth]",
    },
    "root_takeover": {
        "service": "sshd",
        "event_type": "invalid_user_attempt",
        "target_user": "root",
        "source_ip": "192.0.2.88",
        "source_port": "34120",
        "raw_log": "Invalid user root from 192.0.2.88 port 34120",
    },
    "benign_traffic": {
        "service": "sshd",
        "event_type": "authentication_success",
        "target_user": "authorized_dev",
        "source_ip": "10.0.0.15",
        "source_port": "51234",
        "raw_log": "Accepted password for authorized_dev from 10.0.0.15 port 51234 ssh2",
    },
}


def launch_simulation(
    attack_type: str, target_url: str, count: int = 3, interval: float = 1.0
):
    """Executes a simulated attack burst against the orchestrator endpoint."""
    payload_template = SIMULATED_ATTACKS.get(attack_type)
    if not payload_template:
        logger.error(
            f"Unknown attack scenario: {attack_type}. Available: {list(SIMULATED_ATTACKS.keys())}"
        )
        sys.exit(1)

    logger.info(
        f"==> Launching simulation: '{attack_type}' ({count} events) against {target_url}"
    )

    for i in range(1, count + 1):
        payload = dict(payload_template)
        # Add slight jitter to port for realism
        payload["source_port"] = str(int(payload["source_port"]) + i)

        try:
            resp = requests.post(target_url, json=payload, timeout=5)
            if resp.status_code in (200, 202):
                logger.info(
                    f"[{i}/{count}] Dispatched telemetry packet: {payload['event_type']} from {payload['source_ip']}"
                )
            else:
                logger.warning(
                    f"[{i}/{count}] Orchestrator responded with HTTP {resp.status_code}: {resp.text}"
                )
        except requests.exceptions.RequestException as exc:
            logger.error(f"[{i}/{count}] Connection failed to {target_url}: {exc}")
            logger.info(
                "Make sure the AI Orchestrator is running (e.g. uvicorn agents.orchestrator:app or docker-compose up)"
            )
            break

        if i < count:
            time.sleep(interval)

    logger.info(
        "Simulation burst complete. Inspect orchestrator logs and Prometheus /metrics to observe AI reaction."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel-AutoGen-Hunter Attack Simulator"
    )
    parser.add_argument(
        "--scenario",
        choices=list(SIMULATED_ATTACKS.keys()),
        default="ssh_brute_force",
        help="Attack vector to simulate",
    )
    parser.add_argument(
        "--url", default=DEFAULT_ORCHESTRATOR, help="Target orchestrator URL"
    )
    parser.add_argument(
        "--count", type=int, default=3, help="Number of telemetry events to generate"
    )
    parser.add_argument(
        "--interval", type=float, default=0.8, help="Interval in seconds between events"
    )

    args = parser.parse_args()
    launch_simulation(args.scenario, args.url, args.count, args.interval)


if __name__ == "__main__":
    main()
