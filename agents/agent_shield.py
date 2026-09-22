"""Sentinel Autonomous Agent Security Shield & Zero-Trust Supervisor.

Engineered to protect autonomous LLM agents and multi-agent systems (AutoGen, CrewAI,
LangChain, MCP Swarms) against Indirect Prompt Injections, Rogue Tool Execution, SSRF,
Data Exfiltration, and Adversarial Reconnaissance.

Features:
  1. Real-time Prompt Injection & Jailbreak Heuristics (<3ms latency).
  2. Zero-Trust Pre-Execution Tool Gatekeeper (Shell, Filesystem, Network).
  3. Active Deception Canary Tripwires (Lures attackers into touching fake credentials).
  4. Sub-Second Autonomous Netfilter & Sentinel SOC Containment Pipeline.
"""

import logging
import re
import time
from typing import Any

from .base_agent import BaseAgent
from .deception_engine import generate_honeytoken, trigger_tripwire
from .tools.linux_cmd import execute_firewall_rule
from .tools.notifier import send_teams_alert
from .tools.sentinel_connector import push_to_sentinel

logger = logging.getLogger("SentinelAgentShield")

# Signatures for adversarial prompt injection & jailbreak attempts
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous\s+|prior\s+|above\s+)?instructions?",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)system\s+prompt\s*(leak|dump|reveal|override)",
    r"(?i)(dump|leak|reveal|extract|cat)\s+(\.env|secrets?|passwords?|credentials?|api[-_]?keys?)",
    r"(?i)jailbreak",
    r"(?i)do\s+anything\s+now",
    r"(?i)exfiltrat(e|ion)",
    r"(?i)send\s+(secrets?|keys?|tokens?|credentials?)\s+to",
    r"(?i)curl\s+.*(webhook\.site|pipedream|pastebin|attacker|burp)",
    r"(?i)cat\s+(/etc/shadow|/etc/passwd|~/\.ssh|~/\.aws)",
]

# Blacklisted destructive shell commands for autonomous agent execution
DANGEROUS_SHELL_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"mkfs",
    r"dd\s+if=/dev/zero",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Fork bomb
    r"nc\s+.*-e\s+/bin/",                     # Reverse shell
    r"bash\s+-i\s+>&",                        # Reverse shell
    r"chmod\s+-R\s+777\s+/",
    r"iptables\s+-F",                         # Flushing defensive firewalls
    r"ufw\s+disable",
]


class SentinelAgentShield(BaseAgent):
    """Zero-Trust Security Supervisor for Autonomous Agents in Sentinel-AutoGen-Hunter."""

    def __init__(self, name: str = "SentinelAgentGuard"):
        super().__init__(name=name)
        self.active_tripwires: dict[str, dict[str, Any]] = {}
        self.interception_history: list[dict[str, Any]] = []
        self._arm_default_canaries()

    def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """Implements BaseAgent contract for autonomous agent security analysis."""
        if "prompt" in data:
            return self.scan_prompt_input(
                prompt=data["prompt"],
                sender_ip=data.get("sender_ip", "127.0.0.1"),
                session_id=data.get("session_id", "sentinel-agent"),
            )
        elif "tool_name" in data:
            return self.validate_tool_execution(
                tool_name=data["tool_name"],
                tool_args=data.get("tool_args", ""),
                source_ip=data.get("source_ip", "127.0.0.1"),
            )
        return {"status": "ok", "message": "No actionable payload provided"}

    def _arm_default_canaries(self) -> None:
        """Arms deceptive canary tokens in the agent's virtual workspace."""
        canary = generate_honeytoken(
            token_type="aws_key",
            asset_name="sentinel-agent-env",
            deployment_path="/agent/workspace/.env",
        )
        self.active_tripwires[canary["token_value"]] = canary

    def scan_prompt_input(self, prompt: str, sender_ip: str = "127.0.0.1", session_id: str = "local") -> dict[str, Any]:
        """Scans an incoming user prompt or agent input for injection & jailbreak attacks."""
        detected_threats = []

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, prompt):
                detected_threats.append(pattern)

        # Check if the prompt attempts to touch or extract armed canary honeytokens
        for token_value, canary in self.active_tripwires.items():
            if token_value in prompt:
                trigger_tripwire(token_value, source_ip=sender_ip, action="prompt_canary_exfiltration")
                detected_threats.append(f"Canary Honeytoken Access: {canary['token_id']}")

        if detected_threats:
            incident = self._trigger_containment(
                threat_type="Adversarial Prompt Injection",
                source_ip=sender_ip,
                details={"patterns": detected_threats, "prompt_snippet": prompt[:120]},
                session_id=session_id,
            )
            return {
                "allowed": False,
                "status": "BLOCKED",
                "reason": "Prompt Injection / Security Policy Violation",
                "incident": incident,
            }

        return {
            "allowed": True,
            "status": "CLEAN",
            "reason": "Input passed zero-trust heuristics",
        }

    def validate_tool_execution(
        self,
        tool_name: str,
        tool_args: dict[str, Any] | str,
        source_ip: str = "127.0.0.1",
    ) -> dict[str, Any]:
        """Intercepts and validates tool calls before the agent executes them on the host system."""
        args_str = str(tool_args)

        # 1. Check for dangerous shell commands
        if tool_name in ["shell", "bash", "terminal", "run_command", "exec"]:
            for pattern in DANGEROUS_SHELL_PATTERNS:
                if re.search(pattern, args_str):
                    incident = self._trigger_containment(
                        threat_type="Destructive Rogue Shell Execution",
                        source_ip=source_ip,
                        details={"tool": tool_name, "pattern_triggered": pattern, "command": args_str},
                    )
                    return {
                        "allowed": False,
                        "status": "INTERCEPTED",
                        "reason": f"Destructive command pattern detected: {pattern}",
                        "incident": incident,
                    }

        # 2. Check for unauthorized sensitive credential/file access across any tool
        sensitive_targets = ["/etc/shadow", "/etc/passwd", ".ssh", ".env", "id_rsa", "id_ed25519", ".aws/credentials", ".aws/config"]
        for target in sensitive_targets:
            if target in args_str:
                incident = self._trigger_containment(
                    threat_type="Credential Harvesting File Access",
                    source_ip=source_ip,
                    details={"tool": tool_name, "target_file": target, "command": args_str},
                )
                return {
                    "allowed": False,
                    "status": "INTERCEPTED",
                    "reason": f"Access to sensitive credential target blocked: {target}",
                    "incident": incident,
                }

        return {
            "allowed": True,
            "status": "AUTHORIZED",
            "tool": tool_name,
        }

    def _trigger_containment(
        self,
        threat_type: str,
        source_ip: str,
        details: dict[str, Any],
        session_id: str = "agent-session",
    ) -> dict[str, Any]:
        """Autonomous sub-second containment and SOC streaming."""
        start_time = time.perf_counter()

        # 1. Apply kernel Netfilter DROP rule if IP is non-local
        if source_ip and source_ip not in ["127.0.0.1", "localhost", "::1"]:
            cmd = f"iptables -I DOCKER-USER 1 -s {source_ip} -j DROP"
            execute_firewall_rule(cmd, source_ip, risk_level="critical")

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        incident_record = {
            "incident_id": f"INC-SHIELD-{int(time.time())}-{len(self.interception_history)+1}",
            "threat_type": threat_type,
            "source_ip": source_ip,
            "session_id": session_id,
            "containment_latency_ms": elapsed_ms,
            "timestamp": int(time.time()),
            "details": details,
            "mitre_tactic": "TA0001 (Initial Access) / TA0002 (Execution)",
        }

        self.interception_history.append(incident_record)

        # 2. Log to Azure Sentinel
        try:
            push_to_sentinel("SentinelAgentDefense_CL", incident_record)
        except Exception:
            pass

        # 3. Stream alert to notification channel
        try:
            send_teams_alert(
                f"🚨 [Sentinel Shield] {threat_type} Intercepted!",
                f"Threat from {source_ip} blocked in {elapsed_ms}ms.\nDetails: {details}",
            )
        except Exception:
            pass

        logger.warning(f"[SHIELD] Intercepted {threat_type} from {source_ip} in {elapsed_ms}ms")
        return incident_record


# Aliases & singleton instances for ergonomic imports
AgentShield = SentinelAgentShield
agent_shield = SentinelAgentShield()
