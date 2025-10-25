"""Stub adapter for Google Gemini models."""

from __future__ import annotations

from typing import Optional

from ..base import LLMContextAdapter, TokenAllocation
from agentpm.core.context.assembly_service import ContextPayload


class GoogleAdapter(LLMContextAdapter):
    provider = "google"
    DEFAULT_TOTAL_TOKENS = 32_000

    def plan_tokens(self, payload: ContextPayload) -> TokenAllocation:
        total = self.DEFAULT_TOTAL_TOKENS
        prompt = int(total * 0.55)
        completion = int(total * 0.35)
        reserve = total - prompt - completion
        return TokenAllocation(total=total, prompt=prompt, completion=completion, reserve=reserve)

    def system_prompt(self) -> Optional[str]:
        return (
            "You are Gemini assisting the AIPM workflow. Use the supplied context to "
            "craft precise, implementation-ready guidance."
        )
