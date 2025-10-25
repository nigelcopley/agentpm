# WI-44 – Fix Agent Generation Stubs

## Observations
- Generated agent SOPs (e.g., `.claude/agents/planner.md`) still contain placeholders such as `**Action needed**`, indicating the mock Claude integration is not populating templates with project context.
- `MockClaudeIntegration` in `agentpm/core/agents/claude_integration.py` uses simple placeholder replacement and ignores several instruction markers (e.g., quality requirements, compliance sections); real Claude was expected to fill these but mock mode is the default in local dev.
- Agent generator (`agentpm/core/agents/generator.py`) currently writes files even when placeholders remain.
- Work item description references prior issue where mock mode produced 57-byte stubs; current files are larger but still unprofessional.

## Code References
- `agentpm/core/agents/claude_integration.py` (`MockClaudeIntegration.fill_template`)
- `agentpm/core/agents/generator.py` (`generate_agents_with_claude`, `write_agent_sop_file`)
- `.claude/agents/*` generated outputs showing placeholders.

## Proposed Fixes
1. Enhance mock integration to populate key sections (tech stack, rules, patterns, quality gates) using available project context.
2. Add validation step after generation to detect remaining `[INSTRUCTION:` or `**Action needed**` markers—fail generation if present.
3. Improve agent selection logic to ensure sufficient agents (multi-tier orchestrators, specialists) are generated.
4. Provide documentation and tests covering mock generation flow.

