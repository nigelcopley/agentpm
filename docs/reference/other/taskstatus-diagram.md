# TaskStatus State Diagram

Auto-generated from `agentpm/core/database/enums/status.py`

```mermaid
stateDiagram-v2
    draft: Draft
    ready: Ready
    active: Active
    review: Review
    done: Done
    archived: Archived
    blocked: Blocked
    cancelled: Cancelled

    draft --> ready: Validated
    ready --> active: Started
    active --> review: Submit for Review
    review --> done: Approved
    review --> active: Request Changes
    done --> archived: Archive
    active --> blocked: Blocked
    blocked --> active: Unblocked
    draft --> cancelled: Cancelled
```

## States

- **draft**: DRAFT
- **ready**: READY
- **active**: ACTIVE
- **review**: REVIEW
- **done**: DONE
- **archived**: ARCHIVED
- **blocked**: BLOCKED
- **cancelled**: CANCELLED

## Metadata

- **Enum Class**: `TaskStatus`
- **Total States**: 8
- **Terminal States**: Yes
- **Auto-progression**: Yes

---
*This diagram is auto-generated. Do not edit manually.*