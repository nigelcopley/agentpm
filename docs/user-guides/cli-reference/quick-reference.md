# Quick Reference

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](getting-started.md) | [Next →](cli-reference/commands.md)

**2-Page Printable Cheat Sheet** | Version 2.0 | Updated 2025-10-17

All examples from real walkthrough of `fullstack-ecommerce` project.

---

## Installation & Setup

```bash
# Install APM
pip install -e /path/to/agentpm

# Create alias (add to ~/.bashrc or ~/.zshrc)
alias apm='python -m agentpm.cli.main'

# Initialize project
cd your-project
apm init "Project Name" -d "Description"

# Check status
apm status
```

---

## Core Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Work Item** | Primary unit of work (feature, bug, research) | "Product Catalog API" |
| **Task** | Specific work within a work item | "Design API Architecture" |
| **Phase** | Workflow stage (D1→P1→I1→R1→O1→E1) | D1_DISCOVERY |
| **Phase Gate** | Validates outcomes at each phase | I1: Code complete? Tests passing? |
| **6W Context** | Sophisticated 15-field analysis system | See [6W Questions](../specifications/6W-QUESTIONS-ANSWERED.md) |

---

## Work Item Commands

### Create Work Item

```bash
# Basic feature
apm work-item create "Product Catalog API" --type=feature --priority=1

# With full context
apm work-item create "Product Catalog API" \
  --type=feature \
  --priority=1 \
  -d "Build REST API with search and filtering" \
  --business-context "Enable 1000+ SKUs discovery" \
  --who "Customers, Product managers" \
  --what "RESTful API for product catalog" \
  --where "backend/api/products/" \
  --when "Sprint 1, Q1 2025" \
  --why "Core business functionality" \
  --how "Django REST Framework, PostgreSQL, Redis"
```

**Real Output**: Work item ID: 1, Status: draft, Priority: 1, Business Context: ✓

### List Work Items

```bash
# All work items
apm work-item list

# Filter by type
apm work-item list --type=feature

# Filter by status
apm work-item list --status=in_progress

# Filter by priority
apm work-item list --priority=1
```

### View Work Item

```bash
apm work-item show 1
```

**Real Output**: Shows name, type, status, description, tasks (4), and quality gates (✅ all satisfied)

### Update Work Item

```bash
# Update name
apm work-item update 1 --name "Updated Name"

# Update priority
apm work-item update 1 --priority=1

# Update description
apm work-item update 1 -d "New description"
```

---

## Task Commands

### Create Tasks

```bash
# Design task
apm task create "Design Product Catalog API" \
  --work-item-id=1 \
  --type=design \
  --effort=3 \
  -d "Design REST API endpoints and data models"

# Implementation task
apm task create "Implement Product API Endpoints" \
  --work-item-id=1 \
  --type=implementation \
  --effort=4 \
  -d "Implement Django REST Framework views"

# Testing task
apm task create "Test Product Catalog API" \
  --work-item-id=1 \
  --type=testing \
  --effort=3 \
  -d "Write comprehensive test suite"

# Documentation task
apm task create "Document Product Catalog API" \
  --work-item-id=1 \
  --type=documentation \
  --effort=2 \
  -d "Create API docs with OpenAPI spec"
```

**Real Output**: Task ID: 1-4, Type: design/implementation/testing/documentation, Status: draft, Effort: 2-4h

### List Tasks

```bash
# All tasks
apm task list

# Tasks for specific work item
apm task list --work-item-id=1

# Filter by type
apm task list --type=implementation

# Filter by status
apm task list --status=in_progress
```

**Real Output** (formatted table):
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━┓
┃ ID ┃ Name                       ┃ Type           ┃ Status ┃ Effort ┃ WI ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━┩
│ 4  │ Document Product Catalog   │ documentation  │ draft  │ 2.0h   │ 1  │
│ 3  │ Test Product Catalog API   │ testing        │ draft  │ 3.0h   │ 1  │
│ 2  │ Implement Product API      │ implementation │ draft  │ 4.0h   │ 1  │
│ 1  │ Design Product Catalog     │ design         │ draft  │ 3.0h   │ 1  │
└────┴────────────────────────────┴────────────────┴────────┴────────┴────┘
```

### View Task

```bash
apm task show 1
```

---

## Phase Workflow

### 6-Phase Lifecycle

```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION
```

| Phase | Purpose | Gate Validates |
|-------|---------|----------------|
| **D1** | Define needs, validate fit | Requirements clear? Risks identified? |
| **P1** | Create plans, estimates | Plan complete? Dependencies mapped? |
| **I1** | Build solution | Code complete? Tests passing? |
| **R1** | Test and validate | All tests pass? Acceptance criteria met? |
| **O1** | Deploy and monitor | Deployed successfully? Monitoring configured? |
| **E1** | Learn and improve | Learnings captured? Next iteration planned? |

### Phase Commands

```bash
# Check current phase status
apm work-item phase-status 1

# Advance to next phase (automatic)
apm work-item next 1
```

**Real Output** (phase-status):
```
Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL (not started)
Next Phase: D1_DISCOVERY

Phase Sequence for FEATURE:
  D1_DISCOVERY (future)
  P1_PLAN (future)
  I1_IMPLEMENTATION (future)
  R1_REVIEW (future)
  O1_OPERATIONS (future)
  E1_EVOLUTION (future)
```

**Real Output** (next):
```
Advancing Work Item #1: Product Catalog API
Current Phase: NULL → D1_DISCOVERY

✅ Phase advanced successfully

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements
```

---

## Task Lifecycle

### State Transitions

```
draft → validated → accepted → in_progress → review → completed
```

### Lifecycle Commands

**Recommended: Automatic Progression**
```bash
# Auto-advance to next logical state (most common)
apm task next 1
apm work-item next 1
```

**Advanced: Explicit State Control** (when you need precision)
```bash
# Validate task (draft → validated)
apm task validate 1

# Accept task (validated → accepted) - REQUIRES --agent flag
apm task accept 1 --agent python-implementer

# Start task (accepted → in_progress)
apm task start 1

# Submit for review (in_progress → review)
apm task submit-review 1

# Approve task (review → completed)
apm task approve 1

# Request changes (review → in_progress) - REQUIRES --reason
apm task request-changes 1 --reason "Missing edge cases"
```

---

## Work Item Types & Phase Sequences

| Type | Typical Phase Sequence | Approach |
|------|------------------------|----------|
| `feature` | D1 → P1 → I1 → R1 → O1 → E1 | Full lifecycle |
| `bugfix` | I1 → R1 | Quick fix + validate |
| `research` | D1 → P1 | Discovery + planning |
| `enhancement` | P1 → I1 → R1 | Plan, implement, review |
| `refactoring` | P1 → I1 → R1 → O1 | Plan through ops |
| `infrastructure` | D1 → P1 → I1 → R1 → O1 | Full ops lifecycle |

**Phase-based approach**: Gates validate outcomes, not task types

---

## Common Workflows

### 1. Start New Feature

```bash
# 1. Create feature work item
apm work-item create "My Feature" --type=feature --priority=1

# 2. Start phase workflow
apm work-item next <id>  # Advance to D1

# 3. Create tasks as needed for current phase
apm task create "Design My Feature" --work-item-id=<id> --type=design --effort=3
apm task create "Analyze Requirements" --work-item-id=<id> --type=analysis --effort=2

# 4. Check phase status
apm work-item phase-status <id>

# 5. Advance when phase goals met
apm work-item next <id>  # D1 → P1 → I1 → R1 → O1 → E1
```

### 2. Work on Task

**Recommended: Simple workflow**
```bash
# Auto-advance through states
apm task next <task-id>  # Repeat to progress: draft → validated → accepted → in_progress → review → completed
```

**Advanced: Explicit workflow**
```bash
# 1. Accept task (assign to agent) - REQUIRES --agent
apm task accept <task-id> --agent <agent-name>

# 2. Start work
apm task next <task-id>  # or: apm task start <task-id>

# 3. Submit for review when done
apm task next <task-id>  # or: apm task submit-review <task-id>

# 4. Approve (by reviewer)
apm task approve <task-id>
```

### 3. Advance Through Phases

```bash
# Check current phase
apm work-item phase-status <id>

# Advance to next phase (automatic)
apm work-item next <id>

# Repeat for each phase: D1 → P1 → I1 → R1 → O1 → E1
```

---

## Quick Filters & Queries

```bash
# Show only high-priority work items
apm work-item list --priority=1

# Show only in-progress work items
apm work-item list --status=in_progress

# Show only implementation tasks
apm task list --type=implementation

# Show tasks for specific work item
apm task list --work-item-id=1

# Show all features
apm work-item list --type=feature

# Show project dashboard
apm status
```

---

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Task validation fails | Check work item is `ready` status: `apm work-item next <id>` |
| Phase advance blocked | Check phase requirements: `apm work-item phase-status <id>` |
| Phase gate not passing | Review outcomes and use: `apm work-item next <id>` to advance |
| Can't start task | Use automatic progression: `apm task next <id>` |

---

## Help Commands

```bash
# General help
apm --help

# Command group help
apm work-item --help
apm task --help

# Specific command help
apm work-item create -h
apm task create -h
apm work-item next -h
apm task next -h
```

---

## Real Project Data (fullstack-ecommerce)

```
Project: Fullstack Ecommerce
Location: testing/fullstack-ecommerce
Technologies: Django, Python, React, TypeScript, PostgreSQL, Pytest
Work Items: 1 (Product Catalog API)
Tasks: 4 (Design, Implementation, Testing, Documentation)
Phase: D1_DISCOVERY
Quality Gates: ✅ All satisfied
```

---

**Print this card and keep it handy!** 📄

For detailed documentation, see:
- [Getting Started Guide](01-getting-started.md)
- [CLI Command Reference](03-cli-commands.md)
- [Phase Workflow Guide](04-phase-workflow.md)
- [Troubleshooting Guide](05-troubleshooting.md)

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Quick Reference](getting-started.md)
- [➡️ Next: CLI Commands](cli-reference/commands.md)

---
