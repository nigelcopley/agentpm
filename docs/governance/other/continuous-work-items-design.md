# Continuous Work Item System (WI-79)

## Objective

Introduce first-class support for long-running “continuous” work items that stay open indefinitely to aggregate recurring operational work (bugs, maintenance, monitoring, documentation, security). Provide an auto-aggregated “Fix Bugs/Issues” work item that collects new bug tasks as they are discovered.

## Scope

### New Work Item Types

- `maintenance` – Ongoing support/operations backlog
- `monitoring` – Observability/SLA tracking backlog
- `documentation` – Living documentation backlog
- `security` – Security/DevSecOps backlog
- `fix_bugs_issues` – Auto-aggregated backlog for all incoming bugs/issues

All five are “continuous” work items: they should never complete, but they maintain state for reporting, summaries, and SLA compliance.

### Work Item Model Changes

- Add `is_continuous: bool = False` flag to `WorkItem`.
- Extend enum validations/migrations so the new types and flag persist in SQLite.
- Restrict destructive transitions (`approve`, `complete`, `archive`) when `is_continuous` is true.

### Workflow / Validation Adjustments

- Continuous items skip completion gates (CI-002, CI-006, CI-010) that require 100% task closure or “submit review” before completion.
- Continuous items must honor:
  - No unresolved blockers for > X days (configurable)
  - SLA metrics (MTTR, backlog size) surfaced in dashboard
- Task requirement changes:
  - `maintenance`, `monitoring`, `documentation`, `security` types require at least one recurring task type on creation (enforced by validator).
  - `fix_bugs_issues` auto-creates tasks; human-created tasks optional.

### Automatic Bug Aggregation

- Extend bug ingestion/event pipeline (`agentpm/core/events` and `workflow`) to:
  - Detect new bug/issue records (from context ingestion or CLI)
  - Create/attach tasks to the “Fix Bugs/Issues” work item (creating it if missing)
- Maintain summary metadata (`metadata.continuous.metrics`) with:
  - `open_bug_count`
  - `mttr_days`
  - `last_incident_at`

### CLI & UI

- `apm work-item create`:
  - Show continuous types and mark them as such.
  - Accept `--continuous` flag (defaults true for new types).
- Disable `submit-review` / `approve` commands for continuous items.
- Add `apm work-item status --continuous` filter.
- Web dashboard:
  - New section summarising continuous backlog health.
  - Work item detail view: show continuous metrics panel instead of completion progress ring.

### Database Migration

1. Add `is_continuous BOOLEAN NOT NULL DEFAULT 0` to `work_items`.
2. Update enum CHECK constraint for `work_items.type`.
3. Backfill existing maintenance-like work items (if any) with `is_continuous = 1` (based on metadata tag).
4. Seed single "Fix Bugs/Issues" work item per project if absent (optional migration helper).

### Docs & Tests

- Update developer guide (continuous backlogs playbook).
- Expand CLI help (continuous types, auto-bug aggregator usage).
- Tests:
  - Enum/migration test for new types.
  - Workflow validator test for continuous items skipping completion.
  - Bug ingestion integration test ensures tasks attach to `fix_bugs_issues`.
  - CLI tests for create/list restrictions.

## Out of Scope (Future Work)

- Automated metrics ingestion from external bug trackers.
- SLA breach alerting (notifications to agents/humans).
- Cross-project continuous backlog analytics.

## Rollout Plan

1. Ship schema migration + enum updates.
2. Add continuous flag to WorkItem model + service methods.
3. Implement workflow validation adjustments.
4. Integrate bug auto-aggregation pipeline.
5. Update CLI/UI surfaces.
6. Document usage and add tests.
7. Migrate/seed existing projects (utility command).

## Risks & Mitigations

- **Enum drift** – ensure migrations update CHECK constraints, add regression test.
- **Infinite loops** – bug auto-aggregation must dedupe tasks by external ID.
- **User confusion** – documentation and CLI messaging must clarify that continuous items don’t close and how to interpret their health metrics.

