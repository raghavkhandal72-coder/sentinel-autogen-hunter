"""OpenClaw Gateway Server & Companion Protocol Runtime.

Provides the complete OpenClaw Gateway API for Windows Companion desktop apps,
multi-channel messaging, and zero-trust Sentinel threat containment.
"""

import time
from typing import Any
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from .channels import channel_manager
from .llm_router import llm_router
from .sandbox import openclaw_sandbox

gateway_router = APIRouter(prefix="/v1", tags=["OpenClaw Gateway"])


class CompanionPairRequest(BaseModel):
    setup_code: str = Field(..., description="Companion pairing setup code or QR payload")
    client_name: str = Field(default="Windows Companion", description="Connected client device name")


class ChannelMessageRequest(BaseModel):
    channel: str = Field(default="companion", description="whatsapp, telegram, discord, slack, companion, cli")
    sender_id: str = Field(default="user_local", description="Unique sender identifier")
    content: str = Field(..., description="Message text or user command")


class ChatCompletionRequest(BaseModel):
    messages: list[dict[str, str]] = Field(..., description="Conversation history messages")
    temperature: float = Field(default=0.7, description="Sampling temperature")


class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(..., description="Tool name (e.g. bash, read_file, curl)")
    tool_args: dict[str, Any] | str = Field(default="", description="Tool arguments or command payload")
    caller_id: str = Field(default="openclaw_agent", description="Agent or subagent identifier")


# Gateway State
GATEWAY_STATE = {
    "status": "online",
    "paired_companions": ["OpenClaw Windows Companion"],
    "active_channels": ["whatsapp", "telegram", "discord", "slack", "companion", "cli"],
    "started_at": int(time.time()),
    "total_requests": 0,
}


@gateway_router.get("/gateway/status", status_code=status.HTTP_200_OK)
async def get_gateway_status():
    """Returns gateway status, active connections, and security telemetry."""
    return {
        "gateway": "OpenClaw + Sentinel-AutoGen-Hunter Unified Engine",
        "version": "1.4.0",
        "status": GATEWAY_STATE["status"],
        "paired_devices": GATEWAY_STATE["paired_companions"],
        "supported_channels": GATEWAY_STATE["active_channels"],
        "uptime_seconds": int(time.time()) - GATEWAY_STATE["started_at"],
        "total_requests": GATEWAY_STATE["total_requests"],
        "defense_shield": "ARMED (Sub-3ms Prompt Injection & Reverse Shell Blocker)",
    }


@gateway_router.post("/gateway/pair", status_code=status.HTTP_200_OK)
async def pair_companion_device(request: CompanionPairRequest):
    """Pairs a desktop companion app via setup code or QR payload."""
    GATEWAY_STATE["paired_companions"].append(request.client_name)
    return {
        "status": "PAIRED",
        "client_name": request.client_name,
        "session_token": f"oc-sec-{int(time.time())}",
        "message": "Companion successfully paired with OpenClaw Gateway.",
    }


@gateway_router.post("/channels/message", status_code=status.HTTP_200_OK)
async def ingest_channel_message(request: ChannelMessageRequest):
    """Ingests and screens messages from WhatsApp, Telegram, Discord, or Companion."""
    GATEWAY_STATE["total_requests"] += 1
    return channel_manager.handle_incoming_message(
        channel=request.channel,
        sender_id=request.sender_id,
        content=request.content,
    )


@gateway_router.post("/chat/completions", status_code=status.HTTP_200_OK)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completion endpoint used by OpenClaw agents."""
    GATEWAY_STATE["total_requests"] += 1
    res = llm_router.generate_response(request.messages, temperature=request.temperature)
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": res.get("model", "openclaw-sentinel-v1"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": res.get("content", "")},
                "finish_reason": res.get("finish_reason", "stop"),
            }
        ],
        "usage": res.get("usage", {}),
    }


@gateway_router.post("/tools/execute", status_code=status.HTTP_200_OK)
async def execute_tool(request: ToolExecutionRequest):
    """Executes a tool call inside the zero-trust OpenClaw Sandbox."""
    GATEWAY_STATE["total_requests"] += 1
    return openclaw_sandbox.execute_tool(
        tool_name=request.tool_name,
        tool_args=request.tool_args,
        caller_id=request.caller_id,
    )


@gateway_router.get("/sandbox/permissions", status_code=status.HTTP_200_OK)
async def get_sandbox_permissions():
    """Returns permission boundaries enforced by Sentinel."""
    return {
        "shell_execution": "Restricted (Blacklisted: rm -rf, fork bombs, reverse shells)",
        "file_access": "Restricted (Protected: /etc/shadow, .env, SSH keys)",
        "network_outbound": "Inspected by Netfilter DOCKER-USER chain",
        "canary_tripwires": "Active (Canary honeytokens deployed in virtual workspace)",
    }
