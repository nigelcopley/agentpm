name: Work Item Workflow Steward
description: Manage AIPM ideas, work items, and tasks using only `apm` CLI workflow commands. Use when you need to inspect status, advance phases, or keep metadata in sync.
allowed-tools: Bash
---

# Work Item Workflow Steward

## Purpose
Operate the AIPM workflow lifecycle (ideas → work items → tasks) exclusively through `apm` commands to ensure a consistent, auditable state transition history.

## Preconditions
- You have the target project name or ID.
- Authentication/CLI context is already configured (`apm auth status` succeeds).
- Any required work item IDs are known or can be discovered via `apm` queries.

## Instructions
1. **Confirm Context**
   - Run `apm context show` to verify the active project.
   - If switching projects, execute `apm context use <project>` before proceeding.
2. **Review Ideas and Work Items**
   - List inflight ideas: `apm idea list --state in_progress --limit 20`.
   - Inspect a specific idea: `apm idea show <idea-id>`.
   - Convert or link ideas as needed: `apm idea promote <idea-id>`.
3. **Manage Work Items**
   - View current board: `apm workitem list --state all --limit 20`.
   - Show detailed metadata: `apm workitem show <workitem-id>`.
   - Advance phase or status: `apm workitem update <workitem-id> --state <state> --phase <phase> --reason "<note>"`.
   - Attach evidence: `apm workitem log <workitem-id> --message "<update>"`.
4. **Coordinate Tasks**
   - List tasks for a work item: `apm task list --workitem <workitem-id>`.
   - Create a task: `apm task create --workitem <workitem-id> --title "<title>" --assignee "<owner>" --timebox "<h>"`.
   - Update status: `apm task update <task-id> --state <state> --note "<context>"`.
   - Record completion evidence: `apm task log <task-id> --message "<result>"`.
5. **Maintain Audit Trail**
   - After each change, log a short summary using `apm workitem log` or `apm task log`.
   - If additional follow-up is required, create new tasks rather than leaving implicit TODOs.
6. **Verify Outcomes**
   - Re-run relevant list commands to ensure states reflect the intended changes.
   - Optionally export a snapshot for reports: `apm workitem list --state active --format table`.

## Output Expectations
- CLI command outputs that confirm state transitions or resource creation.
- Brief textual summaries describing why each change was made.
- Note remaining blockers or tasks that need assignment.

## Examples
```bash
# Switch to the target project and inspect the backlog
apm context use core-platform
apm workitem list --state ready --limit 10

# Advance a work item to active and log the reason
apm workitem update WI-204 --state active --phase implementation --reason "Design sign-off complete"
apm workitem log WI-204 --message "Implementation kickoff with team scheduled for 2025-10-31"

# Create a follow-up task for testing
apm task create --workitem WI-204 --title "Implement API pagination" --assignee "backend-team" --timebox "4h"
apm task list --workitem WI-204

# Complete a task and record evidence
apm task update T-982 --state completed --note "Tests green in CI pipeline run 1284"
apm task log T-982 --message "Validated pagination works for 10k records"
```

```bash
# Promote an idea into a work item and verify assignment
apm idea show IDEA-17
apm idea promote IDEA-17 --title "Self-healing job scheduler" --assignee "sre-lead"
apm workitem list --state proposed --limit 5
```
