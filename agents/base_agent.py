"""Abstract Base Agent supporting multi-provider LLM dispatch and deterministic mock fallback."""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("BaseAgent")


class BaseAgent(ABC):
    """Abstract base class establishing the contract for all autonomous security agents."""

    def __init__(self, name: str, model: str = "gpt-4o"):
        self.name = name
        self.model = os.getenv("LLM_MODEL", model)
        self.logger = logging.getLogger(self.name)
        self.mode = os.getenv("HUNTER_MODE", "mock").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")

        # Check if live client should be initialized
        self.client = None
        if (
            self.mode != "mock"
            and self.api_key
            and self.api_key != "mock_key_for_testing"
        ):
            try:
                from openai import AzureOpenAI, OpenAI

                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                if azure_endpoint:
                    self.client = AzureOpenAI(
                        azure_endpoint=azure_endpoint,
                        api_key=self.api_key,
                        api_version=os.getenv(
                            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
                        ),
                    )
                    self.logger.info(
                        f"Initialized Azure OpenAI client for agent {self.name}"
                    )
                else:
                    self.client = OpenAI(api_key=self.api_key)
                    self.logger.info(f"Initialized OpenAI client for agent {self.name}")
            except ImportError:
                self.logger.warning(
                    "openai package not installed. Running in deterministic mock mode."
                )
            except Exception as exc:
                self.logger.warning(
                    f"Could not initialize LLM client: {exc}. Running in mock mode."
                )

    @abstractmethod
    def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """Core analysis method every agent must implement."""

    def _call_llm(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Wrapper for LLM invocation with strict JSON output parsing and fallback."""
        if self.client is not None:
            try:
                self.logger.info(f"{self.name} querying live model {self.model}...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                raw_output = response.choices[0].message.content or "{}"
                return json.loads(raw_output)
            except Exception as exc:
                self.logger.error(
                    f"Live LLM call failed: {exc}. Falling back to deterministic simulation."
                )

        # Deterministic simulation for zero-cost testing, CI, and offline execution
        return self._simulate_agent_reasoning(system_prompt, user_content)

    def _simulate_agent_reasoning(
        self, system_prompt: str, user_content: str
    ) -> dict[str, Any]:
        """Generates schema-compliant deterministic responses based on prompt and payload context."""
        try:
            payload = json.loads(user_content) if user_content.startswith("{") else {}
        except Exception:
            payload = {}

        # 1. Analyzer Agent logic simulation
        if "Cloud Security Analyst AI" in system_prompt:
            event_type = payload.get("event_type", "unknown")
            ip = payload.get("source_ip", "0.0.0.0")
            intel_score = payload.get("threat_intel_score", 0)

            is_malicious = (
                event_type in ["ssh_failed_login", "authentication_failed", "port_scan"]
                or intel_score >= 50
            )
            confidence = 0.94 if is_malicious else 0.12
            threat_type = (
                "ssh_brute_force"
                if "ssh" in event_type or "auth" in event_type
                else "port_scan"
            )
            if not is_malicious:
                threat_type = "benign_traffic"

            return {
                "threat_detected": is_malicious,
                "confidence_score": confidence,
                "threat_type": threat_type,
                "target_asset": payload.get("service", "target-server"),
                "attacker_ip": ip if is_malicious else None,
                "evidence": f"Detected {event_type} event from {ip} with threat score {intel_score}",
                "recommended_urgency": "critical"
                if intel_score > 75
                else ("high" if is_malicious else "low"),
            }

        # 2. Remediation Agent logic simulation
        elif "Senior DevOps Security Automation Engineer" in system_prompt:
            ip = payload.get("attacker_ip") or payload.get("source_ip", "192.168.1.100")
            threat_type = payload.get("threat_type", "ssh_brute_force")
            action_required = payload.get("threat_detected", True)

            return {
                "action_required": action_required,
                "mitigation_strategy": f"Isolate attacking host {ip} on DOCKER-USER bridge chain to protect container ingress",
                "proposed_command": f"iptables -I DOCKER-USER 1 -s {ip} -j DROP",
                "rollback_command": f"iptables -D DOCKER-USER -s {ip} -j DROP",
                "risk_level": "low",
                "auto_executable": True,
            }

        # 3. Sentinel Auditor logic simulation
        elif "Microsoft Sentinel" in system_prompt or "KQL" in system_prompt:
            ip = payload.get("attacker_ip", "192.168.1.100")
            threat_type = payload.get("threat_type", "ssh_brute_force")
            kql_snippet = (
                f"AutoGenThreatHunt_CL\n"
                f"| where TimeGenerated >= ago(1h)\n"
                f"| where AttackerIP == '{ip}' or ThreatType == '{threat_type}'\n"
                f"| summarize AttackAttempts = count() by AttackerIP, TargetAsset\n"
                f"| where AttackAttempts >= 3"
            )
            return {
                "sentinel_event_title": f"Autonomous Threat Mitigation: {threat_type} from {ip}",
                "mitre_technique_id": "T1110.001 - Brute Force: Password Guessing",
                "severity": "High",
                "kql_query": kql_snippet,
                "soc_recommendation": f"Monitor firewall drop counters on DOCKER-USER chain for {ip} and verify lateral movement indicators.",
            }

        return {"status": "ok", "message": "Simulated default response"}
