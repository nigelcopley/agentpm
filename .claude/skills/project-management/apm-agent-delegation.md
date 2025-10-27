---
# Skill Metadata (Level 1)
name: apm-agent-delegation
display_name: APM Agent Delegation
description: Multi-agent coordination: phase orchestrators, specialist agents, sub-agents, Task tool patterns
category: project-management
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.598803
updated_at: 2025-10-27T18:34:16.598804
---

# APM Agent Delegation

## Description
Multi-agent coordination: phase orchestrators, specialist agents, sub-agents, Task tool patterns

**Category**: project-management

---

## Instructions (Level 2)

# APM Agent Delegation

## Three-Tier Architecture

### Tier 1: Master Orchestrator
- Routes work by phase
- Never implements directly
- Always delegates via Task tool

### Tier 2: Phase Orchestrators (6)
- definition-orch (D1)
- planning-orch (P1)
- implementation-orch (I1)
- review-test-orch (R1)
- release-ops-orch (O1)
- evolution-orch (E1)

### Tier 3: Specialist Agents (~15)
- aipm-python-cli-developer
- aipm-database-developer
- aipm-testing-specialist
- aipm-documentation-specialist
- aipm-quality-validator

### Tier 4: Sub-Agents (~25)
- context-delivery (MANDATORY at session start)
- intent-triage
- ac-writer
- test-runner
- quality-gatekeeper

## Delegation Pattern

```python
Task(
  subagent_type="aipm-python-cli-developer",
  description="Implement CLI command",
  prompt="""MANDATORY: Follow Agent Operating Protocol

BEFORE STARTING:
  1. Run: apm task start <task-id>

DURING WORK:
  2. Update: apm task update <task-id> --quality-metadata='{...}'

AFTER COMPLETION:
  3. Complete: apm task update <task-id> --quality-metadata='{"completed": true, ...}'
  4. Transition: apm task submit-review <task-id> && apm task approve <task-id>

YOUR TASK:
  Implement [command] following three-layer pattern:
  - Models (Pydantic)
  - Adapters (SQLite conversion)
  - Methods (business logic)

  Task ID: <task-id>
  Requirements: [details]
"""
)
```

## Best Practices
1. **Always start with context-delivery**: Get current state
2. **Route by phase**: Use phase orchestrators
3. **Be specific**: Provide clear task description
4. **Include protocol**: Reference Agent Operating Protocol
5. **Provide context**: Include work item/task IDs

---

## Resources (Level 3)

### Examples
- `Task(subagent_type='definition-orch', ...)`
- `Task(subagent_type='aipm-python-cli-developer', ...)`
- `Task(subagent_type='context-delivery', ...)`

### Templates
- `delegation_template.md`

### Documentation
- [CLAUDE.md sections on delegation](CLAUDE.md sections on delegation)
- [docs/components/agents/architecture/three-tier-orchestration.md](docs/components/agents/architecture/three-tier-orchestration.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Agent Delegation",
  prompt=\"\"\"
  Apply apm-agent-delegation skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Agent Delegation skill.
  \"\"\"
)
```

---

**Skill ID**: 9
**Generated**: 2025-10-27T18:35:40.564969
**Status**: Enabled
