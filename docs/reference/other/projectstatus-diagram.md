# ProjectStatus State Diagram

Auto-generated from `agentpm/core/database/enums/status.py`

```mermaid
stateDiagram-v2
    initiated: Initiated
    active: Active
    on_hold: On Hold
    completed: Completed
    archived: Archived

    initiated --> active: Activate
    active --> on_hold: Pause
    on_hold --> active: Resume
    active --> completed: Complete
    completed --> archived: Archive
```

## States

- **initiated**: INITIATED
- **active**: ACTIVE
- **on_hold**: ON_HOLD
- **completed**: DONE
- **archived**: ARCHIVED

## Metadata

- **Enum Class**: `ProjectStatus`
- **Total States**: 5
- **Terminal States**: Yes
- **Auto-progression**: Yes

---
*This diagram is auto-generated. Do not edit manually.*