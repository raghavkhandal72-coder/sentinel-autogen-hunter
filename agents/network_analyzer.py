"""Specialized Network Analyzer Agent for anomaly classification and threat scoring."""

import json
from typing import Any

from .base_agent import BaseAgent
from .prompts.analyzer_system import ANALYZER_PROMPT
from .tools.threat_intel import check_ip_reputation


class NetworkAnalyzerAgent(BaseAgent):
    """Analyzes raw telemetry payloads, gathers external threat intelligence,

    and outputs deterministic Indicators of Compromise (IOCs).
    """

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="NetworkAnalyzerAgent", model=model)

    def analyze(self, telemetry_data: dict[str, Any]) -> dict[str, Any]:
        """Ingests a telemetry dictionary and evaluates malicious intent."""
        self.logger.info(
            f"Evaluating telemetry event for host: {telemetry_data.get('source_ip', 'unknown')}"
        )

        source_ip = telemetry_data.get("source_ip", "")
        # Gather external threat reputation before reasoning
        intel_report = check_ip_reputation(source_ip) if source_ip else {}
        telemetry_with_context = dict(telemetry_data)
        telemetry_with_context["threat_intel_score"] = intel_report.get(
            "abuse_score", 0
        )
        telemetry_with_context["threat_intel_source"] = intel_report.get(
            "source", "none"
        )

        user_content = json.dumps(telemetry_with_context)
        analysis_result = self._call_llm(ANALYZER_PROMPT, user_content)

        # Merge intel metrics into final report for transparency
        analysis_result["threat_intel"] = intel_report
        return analysis_result
