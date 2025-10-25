"""Stub adapter for Anthropic Claude provider."""

from __future__ import annotations

from typing import Optional

from ..base import LLMContextAdapter, TokenAllocation
from agentpm.core.context.assembly_service import ContextPayload


class AnthropicAdapter(LLMContextAdapter):
    """Expose default token budgeting and system prompt for Claude."""

    provider = "anthropic"
    DEFAULT_TOTAL_TOKENS = 200_000

    def plan_tokens(self, payload: ContextPayload) -> TokenAllocation:
        # Adopt provisional 60/20/20 split until token estimator is implemented.
        total = self.DEFAULT_TOTAL_TOKENS
        prompt = int(total * 0.6)
        completion = int(total * 0.2)
        reserve = total - prompt - completion
        return TokenAllocation(total=total, prompt=prompt, completion=completion, reserve=reserve)

    def system_prompt(self) -> Optional[str]:
        return (
            "You are Claude operating as part of the AIPM agent network. "
            "Follow provided context precisely and avoid speculative edits."
        )
