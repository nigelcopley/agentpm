---
# Skill Metadata (Level 1)
name: apm-task-workflow
display_name: APM Task Workflow
description: Task lifecycle: draft→validated→accepted→in_progress→review→completed, quality metadata updates
category: project-management
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:
  - Bash

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.598603
updated_at: 2025-10-27T18:34:16.598603
---

# APM Task Workflow

## Description
Task lifecycle: draft→validated→accepted→in_progress→review→completed, quality metadata updates

**Category**: project-management

---

## Instructions (Level 2)

# APM Task Workflow

## Task States
```
draft → validated → accepted → in_progress → review → completed
```

## Agent Operating Protocol

### STEP 1 - START
```bash
apm task start <task-id>  # Transition to ACTIVE
```

### STEP 2 - WORK
```bash
apm task update <task-id> --quality-metadata='{
  "progress": "Implementing feature X",
  "tests_passing": true,
  "coverage_percent": 85
}'
```

### STEP 3 - COMPLETE
```bash
apm task update <task-id> --quality-metadata='{
  "completed": true,
  "deliverables": ["file1.py", "file2.py"],
  "tests_passing": true,
  "coverage_percent": 90
}'
apm task submit-review <task-id>  # Transition to REVIEW
apm task approve <task-id>  # Transition to DONE
```

## Hybrid Command Interface

**Automatic Progression** (Recommended):
```bash
apm task next <id>  # Auto-advances to next logical state
```

**Explicit Control** (When needed):
```bash
apm task validate <id>
apm task accept <id> --agent <role>
apm task start <id>
apm task submit-review <id>
apm task approve <id>
apm task request-changes <id> --reason "..."
```

---

## Resources (Level 3)

### Examples
- `apm task start <id>`
- `apm task update <id> --quality-metadata='{...}'`
- `apm task submit-review <id>`
- `apm task approve <id>`

### Templates
- `task_workflow.md`

### Documentation
- [docs/components/workflow/task-lifecycle.md](docs/components/workflow/task-lifecycle.md)
- [.agentpm/docs/governance/quality_gates_spec/agent-operating-protocol-mandatory-workflow-compliance.md](.agentpm/docs/governance/quality_gates_spec/agent-operating-protocol-mandatory-workflow-compliance.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Task Workflow",
  prompt=\"\"\"
  Apply apm-task-workflow skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Task Workflow skill.
  \"\"\"
)
```

---

**Skill ID**: 8
**Generated**: 2025-10-27T18:35:40.565070
**Status**: Enabled
