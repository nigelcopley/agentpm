# Context Assembly Core/Plugins Refactor (WI-66)

**Status:** Proposed design & scaffolding  
**Related work items:** WI-65 (Rich Context System), WI-74 (Session Activity Tracking)

## Current Observations
- Context assembly logic lives in `agentpm/core/context/assembly_service.py` and is consumed directly by `agentpm/hooks/context_integration.py`. Platform-specific formatting is hardcoded in hook adapters.
- `core/plugins/context_assembly/assembly_plugin.py` wraps the service but lacks a structured provider interface; there is no domain separation for LLM adapters or formatters.
- Hooks, CLI commands, and future agents all need the same context payloads, yet they reimplement conversion to Anthropic-friendly markdown.

## Target Architecture
```
core/
  context/
    service.py (existing)
  plugins/
    domains/
      llms/
        base.py             # Shared interfaces + factory helpers
        anthropic/
          __init__.py
          formatter.py       # Markdown assembler for Claude
          adapter.py         # Provider-specific tweaks (rate limits, token budgets)
        openai/
          ...
        google/
          ...
    context_assembly/
      assembly_plugin.py     # Provider-agnostic payload aggregation
```
- `ContextAssemblyPlugin` remains the single orchestration entry. It yields a `ContextPayload` plus structured metadata.
- LLM domain packages provide `LLMContextFormatter` (render payload → string) and `LLMContextAdapter` (provider runtime hints, token budgets).
- Registry exposes `get_llm_formatter(provider_name: str)` so hooks, CLI, or agents choose formatters without direct conditionals.

## Migration Plan
1. **Scaffolding (this change):** Create `core/plugins/domains/llms` namespace, define base Protocols, stub provider packages, and document contracts.
2. **Provider Implementation:** Move existing Anthropic formatting from `hooks/context_integration.py` into `domains/llms/anthropic/formatter.py`. Implement OpenAI and Gemini equivalents or fallbacks.
3. **Hook Refactor:** Replace direct service usage with registry-based formatter selection. Ensure session/task hooks call `ContextAssemblyPlugin` + provider formatter.
4. **Testing:** Add unit coverage for formatters (snapshot style) and integration tests ensuring hooks produce identical output to current behavior.
5. **Documentation & Cleanup:** Update hook README, add plugin development guide, and leave `agentpm/hooks/` as thin adapters.

## Open Questions
- Should token budgeting live in adapters or in `ContextAssemblyService`? Proposal: adapters own provider-specific token splits while service exposes estimated payload size.
- How should we parameterize “provider” in CLI usage (env var, config table, or command flag)? Placeholder: use existing configuration context with default `anthropic`.
