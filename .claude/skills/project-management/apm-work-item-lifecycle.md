---
# Skill Metadata (Level 1)
name: apm-work-item-lifecycle
display_name: APM Work Item Lifecycle
description: Work item workflow: D1→P1→I1→R1→O1→E1 phases, quality gates, status transitions
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
created_at: 2025-10-27T18:34:16.598139
updated_at: 2025-10-27T18:34:16.598139
---

# APM Work Item Lifecycle

## Description
Work item workflow: D1→P1→I1→R1→O1→E1 phases, quality gates, status transitions

**Category**: project-management

---

## Instructions (Level 2)

# APM Work Item Lifecycle

## Phase Progression
```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION
```

## Phase Gates

### D1_DISCOVERY (Define Requirements)
**Gate Requirements**:
- business_context ≥50 chars
- acceptance_criteria ≥3
- risks ≥1
- 6W confidence ≥0.70

**Commands**:
```bash
apm work-item create "Feature Name" --type=feature
apm work-item next <id>  # Advance to P1
```

### P1_PLAN (Create Implementation Plan)
**Gate Requirements**:
- Tasks created (≥1 per AC)
- Effort estimates (≤4 hours each)
- Dependencies mapped
- Risk mitigations planned

**Commands**:
```bash
apm work-item next <id>  # Advance to I1
```

### I1_IMPLEMENTATION (Build & Test)
**Gate Requirements**:
- Tests updated
- Code complete
- Docs updated
- Migrations applied

### R1_REVIEW (Quality Validation)
**Gate Requirements**:
- AC verified
- Tests pass (100%)
- Quality checks passed
- Code review approved

### O1_OPERATIONS (Deploy & Monitor)
**Gate Requirements**:
- Version bumped
- Deployed
- Health checks passing
- Monitoring active

### E1_EVOLUTION (Continuous Improvement)
**Gate Requirements**:
- Telemetry analyzed
- Improvements identified
- Feedback captured

---

## Resources (Level 3)

### Examples
- `apm work-item create`
- `apm work-item next <id>`
- `apm work-item show <id>`

### Templates
- `work_item_workflow.md`

### Documentation
- [docs/components/workflow/work-item-lifecycle.md](docs/components/workflow/work-item-lifecycle.md)
- [CLAUDE.md sections on phase routing](CLAUDE.md sections on phase routing)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Work Item Lifecycle",
  prompt=\"\"\"
  Apply apm-work-item-lifecycle skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Work Item Lifecycle skill.
  \"\"\"
)
```

---

**Skill ID**: 7
**Generated**: 2025-10-27T18:35:40.565168
**Status**: Enabled
