"""Microsoft Sentinel Auditor Agent for KQL query generation and SIEM telemetry streaming."""

import json
from typing import Any

from .base_agent import BaseAgent
from .prompts.sentinel_system import SENTINEL_AUDITOR_PROMPT
from .tools.sentinel_connector import push_to_sentinel


class SentinelAuditorAgent(BaseAgent):
    """Translates runtime threat telemetry into Microsoft Sentinel analytical rules

    and streams structured security events to Azure Log Analytics.
    """

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="SentinelAuditorAgent", model=model)

    def analyze(self, audit_context: dict[str, Any]) -> dict[str, Any]:
        """Generates production-grade KQL query and pushes telemetry to Sentinel."""
        user_content = json.dumps(audit_context)
        sentinel_record = self._call_llm(SENTINEL_AUDITOR_PROMPT, user_content)

        # Merge context data into the Sentinel stream
        combined_payload = {**audit_context, **sentinel_record}

        # Stream directly to Microsoft Sentinel
        ingested = push_to_sentinel(combined_payload)
        sentinel_record["sentinel_ingested"] = ingested
        return sentinel_record
