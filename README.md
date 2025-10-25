# APM (Agent Project Manager)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests: 2,230](https://img.shields.io/badge/tests-2,230-green.svg)](https://github.com/nigelcopley/agentpm)
[![Coverage: 93%+](https://img.shields.io/badge/coverage-93%25+-brightgreen.svg)](https://github.com/nigelcopley/agentpm)

**Database-Driven AI Agent Enablement System with Quality Gates**

APM transforms how AI coding agents work by providing persistent memory, hierarchical context, and enforced quality gates. No more context loss between sessions, no more agents skipping critical steps, no more guessing what the codebase uses.

---

## Why APM?

**The Problem**: AI agents lose context between sessions, skip quality steps, and lack framework-specific knowledge.

**The Solution**: APM provides:

- **Persistent Memory**: Context survives across sessions (database-driven, not file-based)
- **Quality Enforcement**: 75 rules with strict gates agents cannot bypass
- **Framework Intelligence**: 11 plugins extract project facts and provide code examples
- **Time-Boxing**: Forces decomposition (implementation tasks limited to 4 hours)
- **Hierarchical Context**: Project → Work Item → Task with appropriate granularity

---

## Quick Demo

```bash
# Initialize APM in your project
apm init "My Django App" /path/to/project
# → Detects: Python 3.11, Django 5.0, pytest 8.0
# → Extracts: 186KB class definitions, 31KB function signatures
# → Generates: Framework-specific code amalgamations

# Create a feature with quality requirements
apm work-item create "Add User Authentication" --type feature
# → System automatically requires: DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks
# → Enforces: Time-boxing, quality gates, acceptance criteria

# Create time-boxed tasks
apm task create "Design auth schema" --type design --effort 3h
apm task create "Implement User model" --type implementation --effort 3.5h
# → IMPLEMENTATION tasks strictly limited to 4 hours (forces decomposition)

# Agent gets complete hierarchical context
apm task context 123
# Returns:
# - Project facts (Django 5.0, Python 3.11, installed packages)
# - Work item scope (feature goals, acceptance criteria)
# - Task details (objective, time-box, dependencies)
# - Code examples (relevant Django patterns from your codebase)
```

**Result**: Agents work with full context, follow quality processes, and deliver professional results.

---

## Features

### Database-Driven Architecture

- **Persistent Context**: Survives restarts, switches between projects, works across AI providers
- **57 Database Tables**: Projects, work items, tasks, dependencies, contexts, rules, plugins
- **Relationship Tracking**: Hard/soft dependencies, blockers, hierarchical task structures
- **Automated Triggers**: 7 SQLite triggers enforce workflow rules and auto-resolve blockers

### Quality Gate System

- **75 Enforced Rules**: Development principles, testing standards, security requirements, workflow governance
- **Block-Level Enforcement**: Agents cannot bypass critical gates (e.g., tests must pass before review)
- **Time-Boxing**: Implementation ≤4h, Testing ≤6h, Design ≤8h (STRICT enforcement)
- **Type-Specific Validation**: FEATURE requires DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION tasks

### Framework Intelligence

- **11 Active Plugins**: Python, JavaScript, TypeScript, Click, Django, React, HTMX, Alpine.js, Tailwind CSS, pytest, SQLite
- **Automatic Detection**: Scans project for frameworks, extracts versions, dependencies, structure
- **Code Amalgamations**: Generates searchable code groupings (classes, functions, components)
- **Project Facts**: Not recommendations - actual versions, dependencies, patterns from YOUR codebase

### Multi-Agent Orchestration

- **85 Specialized Agents**: Phase orchestrators, domain specialists, single-purpose sub-agents
- **Hierarchical Delegation**: Master orchestrator → Phase orchestrator → Specialist → Sub-agent
- **Context Assembly**: Automatic hierarchical context delivery with confidence scoring
- **Provider Agnostic**: Works with Claude Code, Cursor, Claude Desktop, custom integrations

### Professional Workflow

- **6-Phase Lifecycle**: Discovery → Planning → Implementation → Review → Operations → Evolution
- **State Machine**: 9 states with quality-gated transitions (proposed → validated → accepted → in_progress → review → completed)
- **Dependency Management**: Task and work item dependencies with blocking enforcement
- **Audit Trail**: Complete history of state changes, assignments, quality gate passes

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Git (for version control integration)
- SQLite 3.35+ (usually included with Python)

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/nigelcopley/agentpm.git
cd agentpm

# Install in development mode
pip install -e .

# Verify installation
apm --version
```

### Install from PyPI (Coming Soon)

```bash
pip install agentpm
```

---

## Quick Start

### 1. Initialize Your Project

```bash
# Initialize in current directory
apm init "My Project"

# Or specify path
apm init "My Django App" /path/to/project
```

This creates:
- `.agentpm/data/agentpm.db` - SQLite database with all project data
- `.agentpm/contexts/` - Code amalgamations and extracted facts
- `.agentpm/cache/` - Temporary cache files
- Detects frameworks and extracts project intelligence

### 2. Create Your First Work Item

```bash
# Create a feature
apm work-item create "User Registration System" --type feature

# View quality requirements
apm work-item show 1
# Shows: Required task types, quality gates, acceptance criteria template
```

### 3. Break Down Into Tasks

```bash
# Design phase (max 8 hours)
apm task create "Design user schema" --type design --effort 3h --work-item 1

# Implementation (max 4 hours - STRICT)
apm task create "Implement User model" --type implementation --effort 3.5h --work-item 1
apm task create "Create registration view" --type implementation --effort 3h --work-item 1

# Testing (max 6 hours)
apm task create "Test user registration flow" --type testing --effort 4h --work-item 1

# Documentation (max 4 hours)
apm task create "Document registration API" --type documentation --effort 2h --work-item 1
```

### 4. Work Through Tasks

```bash
# Start a task
apm task start 2

# Get full context for your agent
apm task context 2
# Returns: Project facts + Work item scope + Task details + Code examples

# Complete the task
apm task complete 2
```

### 5. Advance Through Phases

```bash
# Automatic progression (recommended)
apm work-item next 1
# Automatically advances to next logical phase when gates pass

# Explicit control (advanced)
apm work-item validate 1      # Check quality gates
apm work-item start 1         # Begin implementation
apm work-item submit-review 1 # Submit for review
```

---

## Core Concepts

### Quality Gates

Gates ensure agents follow professional development processes:

- **proposed → validated**: All required task types present, no time-box violations
- **validated → accepted**: Ambiguities resolved, agent assigned, design approved
- **accepted → in_progress**: Dependencies met, resources allocated
- **in_progress → review**: All acceptance criteria met, tests passing, code committed
- **review → completed**: Quality review passed, documentation complete

**Agents cannot bypass gates** - the database enforces quality.

### Time-Boxing Philosophy

Time-boxing forces proper decomposition:

- **Implementation ≤4h**: If it takes longer, break it down further
- **Testing ≤6h**: Focused test suites, not marathon sessions
- **Design ≤8h**: High-level design, not over-engineering
- **Documentation ≤4h**: Clear, concise documentation

**Benefits**: Better estimates, smaller commits, easier reviews, faster feedback.

### Three-Layer Architecture

All database operations follow a consistent pattern:

1. **Models** (Pydantic): Type-safe business objects with validation
2. **Adapters**: Convert between Models and SQLite rows
3. **Methods**: Business logic and database operations

**Result**: Maintainable, testable, type-safe codebase with 155,000+ lines of code.

### Plugin System

Plugins extract facts from your project:

- **Automatic Detection**: Scans for frameworks, analyzes structure
- **Version Extraction**: Actual versions from requirements.txt, package.json, etc.
- **Code Analysis**: Extracts classes, functions, components, patterns
- **Amalgamation Generation**: Creates searchable code groupings

**Plugins provide facts, not recommendations** - they tell agents what YOUR project uses.

### Agent Orchestration

85 specialized agents organized hierarchically:

- **Master Orchestrator**: Routes work to phase orchestrators
- **Phase Orchestrators** (6): Discovery, Planning, Implementation, Review, Operations, Evolution
- **Domain Specialists** (15+): Python development, database design, testing, documentation
- **Sub-Agents** (25+): Single-purpose agents for specific tasks (context delivery, gate checking, etc.)
- **Utility Agents**: Work item writing, evidence collection, rule validation

**Agents work together** through structured delegation, not ad-hoc coordination.

---

## Documentation

### Getting Started

- [**User Guide Index**](docs/user-guides/INDEX.md) - Complete navigation with learning paths
- [**Getting Started Guide**](docs/user-guides/getting-started.md) - Detailed installation and first project (15 minutes)
- [**Quick Reference**](docs/user-guides/cli-reference/quick-reference.md) - 2-page command cheat sheet

### Workflows

- [**Phase Workflow**](docs/user-guides/workflows/phase-workflow.md) - Understanding the 6-phase system
- [**Ideas Workflow**](docs/user-guides/workflows/ideas-workflow.md) - Lightweight brainstorming and idea management
- [**Troubleshooting**](docs/user-guides/workflows/troubleshooting.md) - Common issues and solutions

### Integration

- [**Claude Code Integration**](docs/user-guides/integrations/claude-code/overview.md) - Use APM with Claude
- [**Cursor Integration**](docs/user-guides/integrations/cursor/overview.md) - Use APM with Cursor
- [**MCP Setup**](docs/user-guides/integrations/mcp-setup.md) - Model Context Protocol configuration

### Advanced

- [**Agent Generation**](docs/user-guides/advanced/agent-generation.md) - Intelligent agent creation and customization
- [**Memory System**](docs/user-guides/advanced/memory-system.md) - How APM maintains persistent context
- [**Rich Context**](docs/user-guides/advanced/rich-context.md) - Hierarchical context delivery and scoring
- [**Detection Packs**](docs/user-guides/advanced/detection-packs.md) - Framework detection and SBOM generation
- [**Slash Commands**](docs/user-guides/advanced/slash-commands.md) - Custom command creation

### Development

- [**Architecture Guide**](docs/user-guides/developer/architecture.md) - System design and principles
- [**Three-Layer Pattern**](docs/user-guides/developer/three-layer-pattern.md) - Code organization standard
- [**Contributing Guide**](docs/user-guides/developer/contributing.md) - How to contribute to APM
- [**Migrations Guide**](docs/user-guides/developer/migrations.md) - Database migration patterns
- [**Database Schema Reference**](docs/developer-guide/database-schema.md) - Complete schema documentation

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    APM Agent Project Manager                 │
├─────────────────────────────────────────────────────────────┤
│  CLI Layer (22 Commands)                                     │
│  ├─ work-item: Create, list, show, update, advance phases   │
│  ├─ task: Create, start, complete, context, dependencies    │
│  ├─ agents: List, generate SOPs, assign to work             │
│  ├─ context: Show, update, confidence scoring               │
│  ├─ rules: List, validate, enforce quality gates            │
│  └─ init, status, detect, migrate, testing, web, etc.       │
├─────────────────────────────────────────────────────────────┤
│  Core Services                                               │
│  ├─ Workflow: State machine, quality gates, phase lifecycle │
│  ├─ Context: Hierarchical assembly, confidence scoring      │
│  ├─ Plugins: Framework detection, fact extraction           │
│  ├─ Rules: 75 rules with block/warn/inform enforcement      │
│  ├─ Memory: Session persistence, context retrieval          │
│  └─ Search: Full-text search across work items and tasks    │
├─────────────────────────────────────────────────────────────┤
│  Three-Layer Database Pattern                                │
│  ├─ Models: Pydantic type-safe business objects             │
│  ├─ Adapters: SQLite ↔ Model conversion                     │
│  └─ Methods: Business logic, transactions, validation       │
├─────────────────────────────────────────────────────────────┤
│  Database (57 Tables, 7 Triggers, 28 Indexes)                │
│  ├─ Core: projects, work_items, tasks, agents               │
│  ├─ Relationships: dependencies, blockers, hierarchies      │
│  ├─ Context: contexts, rules, evidence, sessions            │
│  └─ Plugins: plugins, facts, code_amalgamations             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Database-First**: All state in SQLite, not files (enables persistence and queries)
- **Quality-Gated**: State machine prevents agents from skipping steps
- **Time-Boxed**: Forces decomposition and realistic estimates
- **Plugin-Driven**: Framework intelligence comes from detection, not assumptions
- **Agent-Orchestrated**: 85 specialized agents, not one generic assistant
- **Type-Safe**: Pydantic everywhere, no Dict[str, Any] in public APIs

---

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=agentpm --cov-report=html

# Run specific test suite
python -m pytest tests/core/database/ -v
python -m pytest tests/core/workflow/ -v

# Quick validation (core schema tests)
python -m pytest tests/core/database/test_schema.py -v
```

**Test Suite**: 2,230 tests, 93%+ coverage on core modules, 100% passing.

### Code Standards

- **Three-Layer Pattern**: Models → Adapters → Methods (MANDATORY)
- **Type Safety**: Pydantic models, type hints everywhere
- **Test Coverage**: ≥90% required (enforced by CI-004 rule)
- **Time-Boxing**: Implementation tasks ≤4h (enforced by DP-001 rule)
- **Conventional Commits**: `type(scope): message` format with work item references

### Contributing

1. Read [CLAUDE.md](CLAUDE.md) - Master orchestrator guide and system overview
2. Review [Contributing Guide](docs/user-guides/developer/contributing.md) - Development standards
3. Check [Architecture Guide](docs/user-guides/developer/architecture.md) - System design
4. Run tests before committing: `python -m pytest tests/ --cov=agentpm`

**Pull Requests**:
- Must pass all 2,230 tests
- Must maintain ≥90% coverage
- Must follow three-layer pattern
- Must include documentation updates

---

## Project Stats

| Metric | Count | Notes |
|--------|-------|-------|
| **Tests** | 2,230 | 100% passing, 93%+ coverage |
| **Code** | 155,000+ lines | Python 3.9+ |
| **CLI Commands** | 22 | Full-featured interface |
| **Plugins** | 11 | Python, JS, TS, Django, React, etc. |
| **Agents** | 85 | Hierarchical orchestration |
| **Database Tables** | 57 | 33 entities + 24 FTS5 indexes |
| **Rules** | 75 | Quality gates and enforcement |
| **Documentation** | 620 files | Comprehensive guides and references |
| **Coverage** | 93-96% | Core modules (database, workflow, CLI) |

---

## Roadmap

### Current Status: Phase 2 (95% Complete)

**Phase 1: Foundation** ✅ Complete
- Database architecture with quality gates
- Plugin system with 11 active plugins
- Security framework and input validation
- Three-layer pattern implementation

**Phase 2: Core Systems** 🔄 95% Complete
- Workflow management with state machine ✅
- CLI interface with 22 commands ✅
- Task dependency system ✅
- Context assembly system 🔄 (75% complete)

### Next: Phase 3 (Q1 2026)

**Agent System Enhancement**
- Complete context assembly system
- Enhance agent delegation patterns
- Improve confidence scoring
- Add session persistence

**Documentation Expansion**
- Video tutorials
- Interactive examples
- Use case deep-dives
- Plugin development guides

### Future: Phase 4 (Q2-Q3 2026)

**Integrations**
- MCP server for Claude integration
- Asana/Linear bidirectional sync
- GitHub Issues integration
- Slack/Discord notifications

**Advanced Features**
- Web-based dashboard
- Real-time collaboration
- Advanced analytics and reporting
- Plugin marketplace

---

## What Makes APM Different

### vs. Traditional Project Management Tools

**Traditional Tools** (Jira, Asana, Linear):
- Static task tracking
- No framework intelligence
- No quality enforcement
- No agent coordination
- Manual context switching

**APM**:
- Database-driven persistent memory
- Framework-specific intelligence (11 plugins)
- Strict quality gates (75 rules)
- 85-agent orchestration
- Automatic hierarchical context assembly

### vs. AI Coding Tools

**Traditional AI Tools** (GitHub Copilot, Cursor standalone):
- Lose context between sessions
- No quality enforcement
- Generic suggestions
- No task breakdown
- No dependency tracking

**APM**:
- Persistent context across sessions
- Enforced quality gates and time-boxing
- Project-specific facts and patterns
- Forced task decomposition (≤4h implementation)
- Structured dependency management with blocking

### Built for AI Agents

APM is designed specifically for AI coding agents:

- **Strict Enforcement**: Agents cannot skip quality steps
- **Complete Context**: Hierarchical delivery from project to task
- **Quality Metadata**: Acceptance criteria, test status, review approval
- **Template-Driven**: Different requirements per work item type
- **Time-Boxed**: Forces agents to decompose complex work

**Result**: Professional-quality deliverables, not quick hacks.

---

## Use Cases

### Solo Developer

- Track personal projects with quality standards
- Maintain context across coding sessions
- Enforce best practices automatically
- Build portfolio-quality work

### Consultant/Freelancer

- Manage multiple client projects
- Demonstrate professional process
- Provide detailed progress reports
- Ensure consistent quality

### Small Team

- Coordinate work across team members
- Track dependencies and blockers
- Enforce team coding standards
- Maintain institutional knowledge

### Open Source

- Organize contributor work
- Track feature development
- Enforce quality gates
- Build sustainable projects

---

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

Copyright 2024-2025 APM Development Team

---

## Support

- **Documentation**: [docs/user-guides/INDEX.md](docs/user-guides/INDEX.md)
- **Issues**: [GitHub Issues](https://github.com/nigelcopley/agentpm/issues)
- **Repository**: [https://github.com/nigelcopley/agentpm](https://github.com/nigelcopley/agentpm)
- **Discussions**: [GitHub Discussions](https://github.com/nigelcopley/agentpm/discussions)

---

## Acknowledgments

APM stands on the shoulders of giants:

- **Pydantic**: Type-safe data validation
- **Click**: Powerful CLI framework
- **Rich**: Beautiful terminal formatting
- **SQLite**: Reliable embedded database
- **pytest**: Comprehensive testing framework

Special thanks to the AI coding community for inspiration and feedback.

---

**APM: Database-driven project management designed for AI coding agents**

Stop losing context. Start delivering quality.
