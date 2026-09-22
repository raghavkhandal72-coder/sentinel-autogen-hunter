"""OpenClaw Engine Package for Sentinel-AutoGen-Hunter.

Integrates the full OpenClaw autonomous multi-channel agent gateway with
Cloud Sentinel's zero-trust threat defense and active canary deception.
"""

from .channels import OpenClawChannelManager, channel_manager
from .gateway import gateway_router
from .llm_router import OpenClawLLMRouter, llm_router
from .pairing import OpenClawPairingManager, pairing_manager
from .sandbox import OpenClawSandbox, openclaw_sandbox
from .wizard import run_onboarding_wizard

__all__ = [
    "OpenClawChannelManager",
    "OpenClawLLMRouter",
    "OpenClawPairingManager",
    "OpenClawSandbox",
    "channel_manager",
    "gateway_router",
    "llm_router",
    "openclaw_sandbox",
    "pairing_manager",
    "run_onboarding_wizard",
]
