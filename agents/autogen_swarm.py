"""Microsoft AutoGen multi-agent coordination swarm.

Coordinates an autonomous debate and consensus flow between:
1. Analyzer Agent (Evaluates IOCs, correlates threat intelligence)
2. Remediation Agent (Formulates containment and rollback policies)
3. Sentinel Auditor (Validates SIEM compliance and synthesizes KQL rules)
"""

import logging
from typing import Any

from .network_analyzer import NetworkAnalyzerAgent
from .remediation_agent import RemediationAgent
from .sentinel_auditor import SentinelAuditorAgent

logger = logging.getLogger("AutoGenSwarm")


class AutoGenThreatSwarm:
    """Manages the lifecycle and collaborative reasoning loop of the security agents."""

    def __init__(self, model: str = "gpt-4o"):
        self.analyzer = NetworkAnalyzerAgent(model=model)
        self.remediator = RemediationAgent(model=model)
        self.sentinel_auditor = SentinelAuditorAgent(model=model)

    def execute_hunt_pipeline(self, raw_telemetry: dict[str, Any]) -> dict[str, Any]:
        """Executes the multi-agent consensus workflow on incoming network telemetry.

        Workflow:
        1. Analyzer evaluates raw logs + AbuseIPDB threat intel.
        2. If threat confirmed, Remediation Agent determines containment + rollback.
        3. Sentinel Auditor crafts MITRE mapping, KQL query, and pushes to Azure.
        """
        source_ip = raw_telemetry.get("source_ip", "unknown")
        logger.info(f"Initiating AutoGen Hunt Swarm for target: {source_ip}")

        # Step 1: Anomaly Analysis & Threat Scoring
        analysis_result = self.analyzer.analyze(raw_telemetry)
        is_threat = analysis_result.get("threat_detected", False)
        confidence = analysis_result.get("confidence_score", 0.0)

        pipeline_result = {
            "source_ip": source_ip,
            "threat_detected": is_threat,
            "confidence_score": confidence,
            "analysis": analysis_result,
            "remediation": None,
            "sentinel": None,
            "swarm_status": "COMPLETED",
        }

        if not is_threat:
            logger.info(f"AutoGen Swarm Consensus: Traffic from {source_ip} is benign.")
            return pipeline_result

        # Step 2: Remediation & Host Containment
        remediation_result = self.remediator.analyze(analysis_result)
        pipeline_result["remediation"] = remediation_result

        # Step 3: Microsoft Sentinel Telemetry & KQL Generation
        audit_context = {
            "threat_type": analysis_result.get("threat_type"),
            "attacker_ip": analysis_result.get("attacker_ip") or source_ip,
            "target_asset": analysis_result.get("target_asset"),
            "confidence_score": confidence,
            "proposed_command": remediation_result.get("proposed_command"),
            "rollback_command": remediation_result.get("rollback_command"),
            "risk_level": remediation_result.get("risk_level"),
        }
        sentinel_result = self.sentinel_auditor.analyze(audit_context)
        pipeline_result["sentinel"] = sentinel_result

        logger.info(
            f"AutoGen Swarm Consensus reached for {source_ip}: Threat={analysis_result.get('threat_type')} "
            f"| Command={remediation_result.get('proposed_command')} | KQL Generated."
        )
        return pipeline_result
