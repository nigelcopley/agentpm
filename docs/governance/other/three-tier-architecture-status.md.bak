# WI-46 – Three-Tier Agent Architecture Status

## Goal
- Consolidate scattered agent documentation into a single, authoritative specification.
- Formalize the three-tier agent hierarchy (Master Orchestrator → Phase Orchestrators → Specialists) and introduce a WI Reviewer governance layer.

## Current Assets
- `.claude/agents/` contains master orchestrator, planner, reviewer, specialists, but content is inconsistent (many placeholders remain – see WI-44).
- `scripts/generate_all_agents.py` orchestrates generation of mini-orchestrators and sub-agents (authored under WI-46) but lacks integrated documentation references.
- Existing docs: `docs/components/agents/AGENT_FORMAT_SPECIFICATION.md`, `AGENT_GENERATION_SUMMARY.md`, `agent-builder-api.md`, etc., partially describe roles but not the full architecture.

## Gaps Identified
1. No unified specification describing roles/responsibilities across tiers.
2. Lack of WI Reviewer governance docs and integration steps.
3. Missing automated validation ensuring required agents exist and are up-to-date.
4. Outdated snippets still describing legacy approach (`schema.py` initialization, old migration references).

## Proposed Steps
- Design consolidated architecture document covering tiers, responsibilities, governance flows.
- Update generator scripts and templates to reference the architecture and ensure WI Reviewer agent is created.
- Implement validation tooling to confirm orchestrators/specialists exist and contain fresh SOP content.
- Document process for maintaining agents and reviewer flows.

