"""Stub adapter for OpenAI GPT models."""

from __future__ import annotations

from typing import Optional

from ..base import LLMContextAdapter, TokenAllocation
from agentpm.core.context.assembly_service import ContextPayload


class OpenAIAdapter(LLMContextAdapter):
    provider = "openai"
    DEFAULT_TOTAL_TOKENS = 128_000

    def plan_tokens(self, payload: ContextPayload) -> TokenAllocation:
        total = self.DEFAULT_TOTAL_TOKENS
        prompt = int(total * 0.5)
        completion = int(total * 0.4)
        reserve = total - prompt - completion
        return TokenAllocation(total=total, prompt=prompt, completion=completion, reserve=reserve)

    def system_prompt(self) -> Optional[str]:
        return (
            "You are part of the AIPM engineering workflow. Follow context directives "
            "and provide actionable, concise responses."
        )
