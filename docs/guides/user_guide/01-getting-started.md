# Getting Started with AIPM

**AI Project Manager (AIPM)** is a framework-agnostic, AI-powered project management tool that helps you organize development work with intelligent context awareness, quality gates, and phase-based workflows.

## What You'll Learn

- Install and initialize AIPM in your project
- Create your first work item and tasks
- Understand the phase-based workflow
- Navigate quality gates and task lifecycle
- Use AIPM's intelligent project analysis

**Time Required**: 15 minutes

---

## Prerequisites

- Python 3.10 or higher
- A software project (any stack - Django, React, Node.js, etc.)
- Basic command-line knowledge

---

## 1. Installation

### Install AIPM

```bash
# From the AIPM repository
cd aipm-v2
pip install -e .

# Verify installation
python -m agentpm.cli.main --version
```

### Create an Alias (Recommended)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias apm='python -m agentpm.cli.main'
```

After reloading your shell, you can use `apm` instead of the full command.

---

## 2. Initialize AIPM in Your Project

Navigate to your project directory and run:

```bash
cd /path/to/your/project
apm init "Project Name" -d "Brief project description"
```

### Real Example: Fullstack E-commerce Platform

```bash
cd testing/fullstack-ecommerce
apm init "Fullstack Ecommerce" -d "Full-stack e-commerce platform with Django backend and React frontend"
```

### What Happens During Initialization

**Output** (condensed for clarity):

```
🚀 Initializing AIPM project: Fullstack Ecommerce
📁 Location: /Users/nigelcopley/.project_manager/aipm-v2/testing/fullstack-ecommerce

🚀 Migration 0018: Consolidated Schema Migration (Enum-Driven)
   - Creating complete APM (Agent Project Manager) database schema
✅ Migration 0018: Consolidated Schema Migration Complete

  Creating directory structure... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Database schema up to date      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Creating project record...      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Agent Generation
   Agents are stored in database (via migrations)
   Generate provider-specific files with:
   apm agents generate --all

✅ Project initialized successfully!

           🔍 Detected Technologies
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Technology ┃ Confidence ┃ Plugin           ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Django     │        60% │ framework:django │
│ Python     │        66% │ lang:python      │
│ Typescript │        69% │ lang:typescript  │
│ Javascript │        66% │ lang:javascript  │
│ Pytest     │        60% │ testing:pytest   │
│ React      │        60% │ framework:react  │
└────────────┴────────────┴──────────────────┘

📊 Detected 9 technologies in 27ms

📚 Next steps:
   apm agents generate --all           # Generate agent files
   apm status                          # View project dashboard
   apm work-item create "My Feature"  # Create work item
   apm task create "My Task"          # Create task

💾 Database: .aipm/data/aipm.db
📁 Project ID: 1
```

### Generate Agent Files

After initialization, generate provider-specific agent files:

```bash
apm agents generate --all
```

**Output**:

```
🤖 Generating agent files from database...
   ✓ Generated 50+ agents
      • definition-orch (orchestrator)
      • planning-orch (orchestrator)
      • implementation-orch (orchestrator)
      • context-delivery (sub-agent)
      • code-implementer (sub-agent)
      • ... and 45 more

   📁 Agent SOPs written to: .claude/agents/

✅ Agent generation complete!
```

### What Got Created

```
your-project/
├── .aipm/
│   ├── data/
│   │   └── aipm.db          # SQLite database with project data
│   ├── contexts/            # Plugin-generated context files
│   └── cache/               # Temporary cache
├── .claude/
│   └── agents/              # Agent SOPs (generated from database)
│       ├── orchestrators/   # Phase orchestrators (6 agents)
│       ├── sub-agents/      # Single-purpose agents (25+ agents)
│       └── utilities/       # Support agents (15+ agents)
└── [your existing files]
```

**Key Points**:

✅ **Database-First**: Agents stored in database, files generated on demand
✅ **Intelligent Detection**: AIPM automatically detected 9 technologies in our project
✅ **Provider-Specific**: Generated files work with Claude Code, Claude Desktop, etc.
✅ **Zero Configuration**: No manual setup required - AIPM analyzed and configured itself
✅ **Fast**: Complete initialization in under 5 seconds

---

## 3. Check Project Status

View your project dashboard:

```bash
apm status
```

**Real Output**:

```
╭─────────────────────── 🤖 APM (Agent Project Manager) Project Dashboard ───────────────────────╮
│ Fullstack Ecommerce                                                        │
│ 📁 /Users/nigelcopley/.project_manager/aipm-v2/testing/fullstack-ecommerce │
│ Status: active                                                             │
╰────────────────────────────────────────────────────────────────────────────╯

ℹ️  No work items yet
💡 Create one: apm work-item create "My Feature" --type=feature

ℹ️  No tasks yet
💡 Create one: apm task create "My Task" --work-item-id=<id> --type=implementation --effort=3

📚 Quick Commands:
   apm work-item list          # View all work items
   apm task list               # View all tasks
   apm work-item show <id>     # Check quality gates
```

The dashboard shows:
- Project name and location
- Current status
- Work items and tasks count
- Helpful next-step commands

---

## 4. Create Your First Work Item

Work items are the primary unit of work in AIPM. They represent features, bug fixes, research, or other deliverables.

### Command Syntax

```bash
apm work-item create "Name" --type=<type> [options]
```

### Work Item Types

| Type | Purpose | Typical Phase Sequence |
|------|---------|------------------------|
| `feature` | New functionality | D1 → P1 → I1 → R1 → O1 → E1 (full lifecycle) |
| `bugfix` | Bug fixes | I1 → R1 (implementation + review) |
| `research` | Investigation | D1 → P1 (discovery + planning) |
| `enhancement` | Improvements | P1 → I1 → R1 (plan, implement, review) |
| `refactoring` | Code improvement | P1 → I1 → R1 → O1 (plan through ops) |
| `infrastructure` | DevOps work | D1 → P1 → I1 → R1 → O1 (full ops lifecycle) |

### Real Example: Create a Feature Work Item

```bash
apm work-item create "Product Catalog API" \
  --type=feature \
  --priority=1 \
  -d "Build REST API endpoints for product catalog with search, filtering, and pagination" \
  --business-context "Enable customers to browse and discover products efficiently, supporting 1000+ SKUs" \
  --who "E-commerce customers, Product managers, Frontend developers" \
  --what "RESTful API for product catalog operations" \
  --where "backend/api/products/, backend/models.py, backend/serializers.py" \
  --when "Sprint 1, Week 1-2, Foundation for Q1 2025 launch" \
  --why "Core business functionality, Revenue generation, Customer satisfaction" \
  --how "Django REST Framework, PostgreSQL full-text search, Redis caching, Pagination with cursor-based approach"
```

**Real Output**:

```
✅ Work item created: Product Catalog API
   ID: 1
   Type: feature
   Status: draft
   Priority: 1
   Business Context: ✓
   6W Context: ✓ (stored in contexts table)

📋 Phase-based workflow:
   • Progress through phases: D1 → P1 → I1 → R1 → O1 → E1
   • Phase gates validate outcomes (code complete? tests passing?)
   • Create tasks as needed to achieve phase goals

📚 Next step:
   apm work-item next 1  # Start D1 (Discovery) phase
```

### Understanding the 6W Framework

AIPM uses a sophisticated **6W Framework** (UnifiedSixW) for comprehensive context analysis:

- **WHO**: Target users and stakeholders
- **WHAT**: What you're building
- **WHERE**: System boundaries and locations
- **WHEN**: Timeline and deadlines
- **WHY**: Business value and rationale
- **HOW**: Technical approach

The 6W Framework is a 15-field structured analysis system that helps AI agents provide better assistance and ensures everyone understands the work's purpose. For complete details, see [6W Questions Answered](../specifications/6W-QUESTIONS-ANSWERED.md).

---

## 5. Create Tasks

Create tasks as needed to progress through phases. Tasks are flexible - organize work however makes sense for your project.

**Phase-based approach**: Focus on outcomes, not task categories
- P1 gate asks: "Do you have a plan?" (not "Do you have a DESIGN task?")
- I1 gate asks: "Is code complete and tested?" (not "Are IMPL+TEST tasks DONE?")

### Example: Create Design Task

```bash
apm task create "Design Product Catalog API Architecture" \
  --work-item-id=1 \
  --type=design \
  --effort=3 \
  -d "Design REST API endpoints, data models, caching strategy, and search implementation"
```

**Output**:

```
✅ Task created: Design Product Catalog API Architecture
   ID: 1
   Type: design
   Status: draft
   Effort: 3.0h
   Priority: 3

📚 Next steps:
   apm task list --work-item-id=1  # View all tasks
   apm task start 1                # Start working on this task
```

### Create Remaining Tasks

```bash
# Implementation task
apm task create "Implement Product API Endpoints" \
  --work-item-id=1 \
  --type=implementation \
  --effort=4 \
  -d "Implement Django REST Framework views, serializers, and URL patterns"

# Testing task
apm task create "Test Product Catalog API" \
  --work-item-id=1 \
  --type=testing \
  --effort=3 \
  -d "Write comprehensive test suite covering API endpoints and edge cases"

# Documentation task
apm task create "Document Product Catalog API" \
  --work-item-id=1 \
  --type=documentation \
  --effort=2 \
  -d "Create API documentation with OpenAPI spec and usage examples"
```

### View All Tasks

```bash
apm task list
```

**Real Output**:

```
                                  📋 Tasks (4)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━┓
┃ ID ┃ Name                            ┃ Type           ┃ Status ┃ Effort ┃ WI ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━┩
│ 4  │ Document Product Catalog API    │ documentation  │ draft  │ 2.0h   │ 1  │
│ 3  │ Test Product Catalog API        │ testing        │ draft  │ 3.0h   │ 1  │
│ 2  │ Implement Product API Endpoints │ implementation │ draft  │ 4.0h   │ 1  │
│ 1  │ Design Product Catalog API      │ design         │ draft  │ 3.0h   │ 1  │
│    │ Architecture                    │                │        │        │    │
└────┴─────────────────────────────────┴────────────────┴────────┴────────┴────┘
```

---

## 6. Check Quality Gates

View your work item with quality gate status:

```bash
apm work-item show 1
```

**Real Output**:

```
📋 Work Item #1

Name: Product Catalog API
Type: feature
Status: draft
Priority: 1

Description:
Build REST API endpoints for product catalog with search, filtering, and
pagination capabilities

Tasks (4):
  •  Document Product Catalog API (draft)
  •  Test Product Catalog API (draft)
  •  Implement Product API Endpoints (draft)
  •  Design Product Catalog API Architecture (draft)

Phase Gates:
  Current Phase: D1_DISCOVERY
  Phase gates validate OUTCOMES, not task types:
    ✅ P1 gate: Do you have a plan?
    ✅ I1 gate: Is code complete and tested?
    ✅ R1 gate: Do all tests pass?
```

All quality gates are now satisfied! ✅

---

## 7. Understanding Phases

AIPM uses a **6-phase workflow** (D1 → P1 → I1 → R1 → O1 → E1):

| Phase | Name | Purpose |
|-------|------|---------|
| **D1** | Discovery | Define needs, validate market fit, gather requirements |
| **P1** | Planning | Create detailed plans, estimates, and dependencies |
| **I1** | Implementation | Build the solution |
| **R1** | Review | Test, validate, and ensure quality |
| **O1** | Operations | Deploy and monitor in production |
| **E1** | Evolution | Learn, adapt, and improve |

### Check Phase Status

```bash
apm work-item phase-status 1
```

**Real Output**:

```
Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL (not started)
Current Status: draft
Next Phase: D1_DISCOVERY

Phase Sequence for FEATURE:
  D1_DISCOVERY (future)
  P1_PLAN (future)
  I1_IMPLEMENTATION (future)
  R1_REVIEW (future)
  O1_OPERATIONS (future)
  E1_EVOLUTION (future)

Next Phase (D1_DISCOVERY) Requirements:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Available Actions:
  apm work-item next 1  # Advance to next phase (automatic)
```

### Advance to First Phase

```bash
apm work-item next 1
```

**Real Output**:

```
Advancing Work Item #1: Product Catalog API
Current Phase: NULL
Current Status: draft

Advancing: NULL → D1_DISCOVERY

Validating phase gate requirements...
✅ Phase gate validation PASSED

✅ Phase advanced successfully

Phase: NULL → D1_DISCOVERY
Status: draft → draft

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Required task types:
  • analysis
  • research
  • design

Next Steps:
  apm work-item phase-status 1  # View phase requirements
  apm task list --work-item-id=1  # View tasks
  apm work-item next 1   # Advance when ready
```

---

## 8. Next Steps

### Essential Commands

```bash
# View project dashboard
apm status

# List work items
apm work-item list

# List tasks
apm task list

# View work item details
apm work-item show <id>

# View task details
apm task show <id>

# Check phase status
apm work-item phase-status <id>

# Advance to next phase
apm work-item next <id>
```

### Learn More

- **Quick Reference Card** - Common commands and workflows (docs/user-guides/02-quick-reference.md)
- **CLI Command Reference** - Complete command documentation (docs/user-guides/03-cli-commands.md)
- **Phase Workflow Guide** - Detailed phase progression (docs/user-guides/04-phase-workflow.md)
- **Troubleshooting Guide** - Solutions to common issues (docs/user-guides/05-troubleshooting.md)

---

## Summary

You've learned how to:

✅ Initialize AIPM in your project
✅ Create work items with full business context
✅ Create tasks with quality gates
✅ Understand the phase-based workflow
✅ Navigate the AIPM dashboard and commands

**Key Takeaways**:

1. **Framework Agnostic**: AIPM works with any technology stack
2. **Intelligent Detection**: Auto-detects your project's tech stack
3. **Phase Gates**: Validates outcomes at each phase (code complete? tests passing?)
4. **Phase-Based**: Structured 6-phase workflow (D1→P1→I1→R1→O1→E1)
5. **6W Context**: Sophisticated 15-field analysis for comprehensive project understanding
6. **Flexible Tasks**: Create tasks as needed - gates check completion, not task types

**Next**: Explore the [Quick Reference Card](02-quick-reference.md) for common workflows!

---

**Generated**: 2025-10-17
**AIPM Version**: 2.0
**Real Examples**: All examples from live walkthrough of fullstack-ecommerce project
