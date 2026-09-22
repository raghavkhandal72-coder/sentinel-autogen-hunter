"""OpenClaw Multi-Channel Messaging Manager.

Normalizes messages from external channels (WhatsApp, Telegram, Discord, Slack, Companion)
and screens them through Sentinel's zero-trust pre-execution perimeter.
"""

import time
from typing import Any

from .llm_router import llm_router


class OpenClawChannelManager:
    """Manages multi-channel ingress and response generation."""

    SUPPORTED_CHANNELS = ["whatsapp", "telegram", "discord", "slack", "companion", "cli", "webhook"]

    def __init__(self):
        self.message_history: list[dict[str, Any]] = []

    def handle_incoming_message(
        self,
        channel: str,
        sender_id: str,
        content: str,
        sender_ip: str = "127.0.0.1",
    ) -> dict[str, Any]:
        """Ingests a message from a connected channel and executes agent workflow."""
        start_time = time.perf_counter()

        if channel not in self.SUPPORTED_CHANNELS:
            return {"status": "error", "message": f"Unsupported channel: {channel}"}

        # 1. Pre-execution Prompt Inspection via SentinelAgentShield (<1.5ms)
        from agents.agent_shield import agent_shield
        shield_res = agent_shield.scan_prompt_input(
            prompt=content,
            sender_ip=sender_ip,
            session_id=f"{channel}-{sender_id}",
        )

        if not shield_res.get("allowed", True):
            record = {
                "timestamp": int(time.time()),
                "channel": channel,
                "sender_id": sender_id,
                "status": "BLOCKED",
                "reason": shield_res.get("reason"),
                "incident": shield_res.get("incident"),
            }
            self.message_history.append(record)
            return {
                "status": "BLOCKED",
                "channel": channel,
                "response": "[SECURITY ALERT] Security Policy Violation: Prompt injection / jailbreak detected and contained.",
                "incident": shield_res.get("incident"),
            }

        # 2. Generate Agent Response via LLMRouter
        llm_res = llm_router.generate_response(messages=[{"role": "user", "content": content}])
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        record = {
            "timestamp": int(time.time()),
            "channel": channel,
            "sender_id": sender_id,
            "status": "DELIVERED",
            "latency_ms": elapsed_ms,
        }
        self.message_history.append(record)

        return {
            "status": "DELIVERED",
            "channel": channel,
            "sender_id": sender_id,
            "response": llm_res.get("content", ""),
            "latency_ms": elapsed_ms,
            "model": llm_res.get("model"),
        }


channel_manager = OpenClawChannelManager()
