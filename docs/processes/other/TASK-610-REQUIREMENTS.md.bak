# Task 610: Documentation Fixes Report

**Task**: Fix all stale documentation references using testing infrastructure
**Date**: 2025-10-20
**Status**: In Progress

## Test Results Summary

### State Machine Issues

**Problem**: Documentation references obsolete status values that no longer exist in enums.

**Valid States** (from `agentpm/core/database/enums/status.py`):
- `draft`, `ready`, `active`, `review`, `done`, `blocked`, `cancelled`, `archived`

**Invalid States** (found in documentation):
- `completed` (should be `done`)
- `initiated` (should be `draft` or `active`)
- `on_hold` (removed from system)

### TaskStatus Documentation Drift

Files referencing invalid TaskStatus states:

1. `docs/specifications/6W-QUESTIONS-ANSWERED.md` - References: `completed`
2. `docs/analysis/event-driven-architecture-analysis.md` - References: `completed`
3. `docs/external-research/AIPM-V2-COMPLETE-SYSTEM-BREAKDOWN.md` - References: `initiated`, `on_hold`, `completed`
4. `docs/adrs/ADR-010-dependency-management-and-scheduling.md` - References: `completed`
5. `docs/adrs/ADR-009-event-system-and-integrations.md` - References: `completed`
6. `docs/developer-guide/01-architecture-overview.md` - References: `completed`
7. `docs/reports/MIGRATION-0018-REFACTOR-SUMMARY.md` - References: `initiated`, `on_hold`, `completed`
8. `agents/generic/mini-orchestrator-delegation-audit.md` - References: `completed`
9. `architecture/specification/wi-perpetual-reviewer.md` - References: `completed`
10. `communication/status_report/wi-115-implementation-complete.md` - References: `initiated`, `completed`

### WorkItemStatus Documentation Drift

Files referencing invalid WorkItemStatus states:

1. `docs/design/testing-strategy.md` - References: `completed`
2. `docs/analysis/work-item-lifecycle-tracking-analysis.md` - References: `completed`
3. `docs/external-research/AIPM-V2-COMPLETE-SYSTEM-BREAKDOWN.md` - References: `initiated`, `on_hold`, `completed`
4. `docs/developer-guide/01-architecture-overview.md` - References: `completed`
5. `docs/developer-guide/02-three-layer-pattern.md` - References: `completed`
6. `docs/developer-guide/03-contributing.md` - References: `completed`
7. `docs/reports/MIGRATION-0018-REFACTOR-SUMMARY.md` - References: `initiated`, `on_hold`, `completed`
8. `docs/reports/WORKFLOW-ANALYSIS.md` - References: `completed`
9. `docs/reports/phase-status-coupling-analysis.md` - References: `completed`
10. `analysis/system-review/WEEK-1-IMPLEMENTATION-PLAN.md` - References: `completed`
11. `architecture/specification/TASK-263-265-354-COMPLETION-REPORT.md` - References: `completed`
12. `architecture/specification/wi-perpetual-reviewer.md` - References: `completed`
13. `communication/status_report/wi-115-implementation-complete.md` - References: `initiated`, `completed`
14. `work-items/wi-77/task-context-delivery-design.md` - References: `completed`

### State Diagram Issues

The state diagrams have parsing issues - they contain literal string `{', ".join(cls.choices())'}` instead of actual state names. This indicates the diagrams need to be regenerated from scratch.

**Files needing regeneration**:
1. `docs/reference/state-diagrams/taskstatus-diagram.md`
2. `docs/reference/state-diagrams/workitemstatus-diagram.md`
3. `docs/reference/state-diagrams/projectstatus-diagram.md`

### Python Code Examples Issues

**Python syntax errors**: 202 instances across 63 files

**Categories**:
1. **Pseudo-code marked as Python** - Files contain workflow diagrams, ASCII art, or examples that aren't valid Python
2. **Missing imports** - Code references modules that don't exist (e.g., `agentpm.agents.base`)
3. **Incomplete snippets** - Code fragments without proper context
4. **Unicode in code blocks** - Symbols like →, ✅, ≥ in Python code blocks

### Bash Command Issues

**Invalid APM commands**: 428 invalid command references across 86 files

**Common issues**:
1. Commands reference removed subcommands (e.g., `apm work-item phase-advance`)
2. Wrong flag syntax (e.g., `--phase` instead of phase being derived from status)
3. Obsolete command patterns

## Fix Strategy

### Phase 1: High-Priority State Machine Fixes (CRITICAL)

Fix all references to invalid status values in critical documentation:

**Replacement map**:
- `completed` → `done`
- `initiated` → `draft` (if creating) or `active` (if working)
- `on_hold` → `blocked` (with blocker) or `ready` (paused)

**Priority files** (user-facing docs):
1. `docs/developer-guide/01-architecture-overview.md`
2. `docs/developer-guide/02-three-layer-pattern.md`
3. `docs/developer-guide/03-contributing.md`
4. `CLAUDE.md` (if any issues found)

### Phase 2: Regenerate State Diagrams

Use `scripts/poc_state_diagrams.py` to generate accurate diagrams from enums.

### Phase 3: Fix Python Code Examples

**Two approaches**:

1. **Convert to pseudo-code** - Change code fence from ```python to ```text or ```pseudocode
2. **Fix the code** - Add missing imports, fix syntax

**Decision criteria**:
- If code is meant to be runnable → Fix it
- If code is illustrative/conceptual → Convert to pseudo-code

### Phase 4: Fix Bash Command Examples

**Systematic replacement** of obsolete commands with current syntax.

## Execution Plan

**Time estimate**: 4 hours

1. **Hour 1**: Fix state machine references (Phase 1) - ~24 files
2. **Hour 2**: Regenerate state diagrams (Phase 2) + verify
3. **Hour 3**: Triage Python code examples (Phase 3) - Mark pseudo-code files
4. **Hour 4**: Fix critical bash commands + final test verification

## Success Criteria

- [ ] All TaskStatus/WorkItemStatus references use valid states
- [ ] State diagrams match enums exactly
- [ ] Python code examples either execute or marked as pseudo-code
- [ ] Critical bash commands use current syntax
- [ ] All pytest tests pass: `pytest tests/docs/ -v`

## Notes

- Many errors are in analysis/design documents (lower priority)
- Focus on user-facing documentation first
- Use automated find/replace where safe
- Manual review for command syntax (context-dependent)
