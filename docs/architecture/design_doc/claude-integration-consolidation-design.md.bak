# Claude Integration Consolidation – Architecture Design

## Purpose
Unify all Claude-related work into a coherent, maintainable integration aligned with APM (Agent Project Manager) principles. This design consolidates plugins, hooks, subagents, memory, settings, checkpointing, and slash commands under the Service Coordinator pattern with clear interfaces and phase gates.

## Audience
- AI coding agents and maintainers implementing/operating Claude integration in APM (Agent Project Manager)
- Reviewers validating architecture and quality gates compliance

## Scope
- In scope: Claude Code plugin system, hooks lifecycle, subagent orchestration, database-driven persistent memory, settings management, checkpointing, and slash commands.
- Out of scope: Third-party provider feature parity beyond immediate needs, UI polish for ancillary tools, and non-Claude agent backports.

## Architecture Overview
The integration follows the database service pattern and three-layer architecture:
1) Models: Pydantic models for events, memory payloads, settings, and orchestration plans.
2) Adapters: Converters between models and database rows, and between database and memory files.
3) Methods: Business logic for hooks handling, memory generation/sync, subagent routing, checkpointing, and command handling.

### Key Components
- Service Coordinator: `ClaudeIntegrationService` responsible for orchestration and error handling.
- Plugins: Modular capability units (hooks, slash commands, memory tools, checkpointing) loaded via a registry.
- Hooks Engine: Normalised event bus for events such as SessionStart, SessionEnd, PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact, Notification.
- Subagent Orchestrator: Strategy-based routing and lifecycle management for Claude subagents with dependency-aware execution.
- Persistent Memory System: Database-driven memory files in `.claude/` kept in sync with project state (RULES, PRINCIPLES, WORKFLOW, AGENTS, CONTEXT, PROJECT, IDEAS).
- Settings Manager: Typed settings with validation and safe defaults; CLI and file-based configuration.
- Checkpointing: Durable snapshots of key interaction and context state for recovery and analysis.
- Slash Commands: Declarative command registry with validation and rich help.

## Interfaces
```text
ClaudeIntegrationService
  ├── initialise(context) -> IntegrationSession
  ├── handle_event(event: HookEvent) -> EventResult
  ├── update_memory(scope: MemoryScope) -> MemoryUpdateResult
  ├── run_subagent(plan: SubagentPlan) -> SubagentResult
  ├── checkpoint(kind: CheckpointKind, data: dict) -> CheckpointRef
  └── execute_slash(command: SlashCommand, args: dict) -> CommandResult

Plugin
  ├── name: str
  ├── supports(event|command|capability) -> bool
  └── handle(input) -> Output
```

## Sequencing and Dependencies
1) Complete WI-114 (Persistent Memory) foundational templates and generators.
2) Complete WI-116 (Comprehensive Integration) component stubs aligned with this architecture.
3) Align agent interactions (WI-107) to new interfaces.
4) Integrate hooks and subagents using the orchestrator; wire slash commands.
5) Enable checkpointing and end-to-end tests.

## Data & Models
- HookEvent: type, payload, correlation_id, session_id, timestamp.
- MemoryFile: name, path, content_hash, source_version.
- SubagentPlan: objectives, constraints, tools, handoff_policy.
- Checkpoint: id, kind, created_at, metadata, diff_refs.
- Settings: validated options for capabilities and limits.

## Error Handling (Agent-First)
- Actionable errors with guidance and next actions.
- Guard rails: validate inputs at boundaries; refuse incomplete payloads.

## Security & Compliance
- Input validation on CLI and file boundaries (Click validators).
- Output sanitisation; redact tokens/secrets.
- Whitelisted command execution; timeouts for external calls.

## Testing Strategy
- Unit tests for plugins, adapters, and service methods.
- Integration tests for end-to-end flows (hooks → orchestrator → memory → checkpoint).
- Coverage target ≥ 90% for integration components.

## Acceptance Criteria Mapping
- Approved consolidated integration architecture documented (this file).
- End-to-end flow operational with database-driven memory sync and checkpointing.
- Hooks and slash commands verified in integration tests.
- ≥ 90% coverage for integration components; consolidated docs published.

## Risks & Mitigations
- Dependency timelines (WI-114/116/107): track via work item dependencies and phase gates.
- Event payload ambiguity: define canonical schemas and contract tests.
- Memory sync conflicts: adopt last-write-wins with diff checkpoints and audit trail.

## Next Steps
- Finalise interface signatures and generate stubs for plugins and orchestrator.
- Align WI-116 tasks to this service contract.
- Prepare test scaffolding and coverage thresholds.

## Quick Validation
```bash
apm work-item show 119                 # Check artifacts and status
apm task show 643                      # Verify design deliverables linked
apm work-item validate 119             # Validate gates for current phase
```

## Canonical References
- Service pattern (gold standard): [service.py](mdc:agentpm/core/database/service.py)
- Context system: [docs/components/context/README.md](mdc:docs/components/context/README.md)
- Workflow gates: [workflow validators](mdc:agentpm/core/workflow/validators.py)
- CLI patterns: [agentpm/cli/](mdc:agentpm/cli/)



