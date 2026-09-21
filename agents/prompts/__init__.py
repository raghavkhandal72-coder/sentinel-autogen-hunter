"""System prompts package for multi-agent autonomous threat hunting."""

from .analyzer_system import ANALYZER_PROMPT
from .remediation_system import REMEDIATION_PROMPT
from .sentinel_system import SENTINEL_AUDITOR_PROMPT

__all__ = ["ANALYZER_PROMPT", "REMEDIATION_PROMPT", "SENTINEL_AUDITOR_PROMPT"]
