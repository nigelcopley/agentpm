---
name: APM (Agent Project Manager) Project Manager
description: Comprehensive Agent Project Manager for managing work items, tasks, and context. Use when working on projects that need structured project management, work item tracking, or quality gate enforcement.
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# APM (Agent Project Manager) Project Manager

## Instructions
# APM (Agent Project Manager) Project Manager

## Instructions

1. **Check Project Status**: `apm status`
2. **List Work Items**: `apm work-item list`
3. **Get Context**: `apm context show --work-item-id=all`
4. **Create Work Items**: `apm work-item create "APM (Agent Project Manager) Project Manager" --type `
5. **Manage Tasks**: `apm task create "" --type  --effort `

## Quality Gates

- **FEATURE** requires: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT** requires: DESIGN + IMPLEMENTATION + TESTING  
- **BUGFIX** requires: ANALYSIS + BUGFIX + TESTING
- **IMPLEMENTATION** tasks max 4 hours (enforced)

## Context-First Approach

Always start with context before making changes:
1. Get hierarchical context: `apm context show --task-id=<id>`
2. Review quality indicators (RED/YELLOW/GREEN)
3. Check dependencies: `apm work-item list-dependencies <id>`
4. Follow established patterns
5. Record decisions: `apm learnings record --type=decision --content="..."`

## Work Item Management

```bash
# Create work item
apm work-item create "Feature Name" --type feature

# Add dependency
apm work-item add-dependency <id> --depends-on <id>

# Validate work item
apm work-item validate <id>
```

## Task Management

```bash
# Create task
apm task create "Task Name" --type implementation --effort 4

# Start task
apm task start <task_id>

# Complete task
apm task complete <task_id> --evidence="Implementation details"
```

## Evidence-Based Development

Always record decisions with evidence:
```bash
apm learnings record --type=decision --content="Decision" --evidence="Supporting evidence"
apm learnings record --type=pattern --content="Pattern description" --when-to-use="Usage guidance"
```

## Examples
## Examples

### Starting a New Feature
```bash
# 1. Get project context
apm status
apm context show --work-item-id=all

# 2. Create feature work item
apm work-item create "User Authentication" --type feature

# 3. Add required tasks
apm task create "Design Authentication" --type design --effort 6
apm task create "Implement Authentication" --type implementation --effort 4
apm task create "Test Authentication" --type testing --effort 4
apm task create "Document Authentication" --type documentation --effort 3

# 4. Start with design
apm task start <design_task_id>
```

### Fixing a Bug
```bash
# 1. Create bugfix work item
apm work-item create "Fix Login Issue" --type bugfix

# 2. Add required tasks
apm task create "Analyze Login Issue" --type analysis --effort 4
apm task create "Fix Login Issue" --type bugfix --effort 4
apm task create "Test Login Fix" --type testing --effort 3

# 3. Start analysis
apm task start <analysis_task_id>
```

### Getting Context for Work
```bash
# Get comprehensive context
apm context show --task-id=<task_id>

# Check work item dependencies
apm work-item list-dependencies <work_item_id>

# Review recent decisions
apm learnings list --recent
```

## Requirements
## Requirements

- APM (Agent Project Manager) CLI installed and configured
- Project initialised with `apm init`
- Database accessible
- Git repository for version control

## Installation

```bash
# Install APM (Agent Project Manager)
pip install aipm-v2

# Initialise project
apm init "Project Name" /path/to/project
```
