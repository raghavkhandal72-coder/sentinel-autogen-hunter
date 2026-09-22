"""Sentinel Agent Guard Execution Entrypoint.

Provides zero-trust pre-execution lifecycle hooks for autonomous agents:
  1. on_user_message: Intercepts prompt injections before LLM reasoning loops.
  2. on_before_tool_execute: Gatekeeps shell execution, reverse shells, and credential exfiltration.
"""

from typing import Any
from agents.agent_shield import agent_shield


def on_user_message(message: str, sender_id: str = "agent_user", channel: str = "default") -> dict[str, Any]:
    """Hook executed before passing user message or external instruction to the LLM agent."""
    result = agent_shield.scan_prompt_input(message, sender_ip=sender_id, session_id=f"session-{channel}")
    return result


def on_before_tool_execute(tool_name: str, tool_args: dict[str, Any] | str, caller_id: str = "autonomous_agent") -> dict[str, Any]:
    """Hook executed before executing any system or shell tool on the host environment."""
    result = agent_shield.validate_tool_execution(tool_name, tool_args, source_ip=caller_id)
    return result


if __name__ == "__main__":
    print("[+] Sentinel-Agent-Guard Extension loaded successfully.")
