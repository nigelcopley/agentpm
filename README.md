# APM (Agent Project Manager)

**Quality-Gated Coding Agent Enablement System**

A sophisticated project management system that provides AI coding agents with hierarchical context, framework intelligence, and enforced quality gates to ensure professional-quality deliverables.

---

## 🎯 **Mission**

Eliminate AI coding agent failures through:
- **Persistent Memory**: Context survives across sessions (database-driven)
- **Hierarchical Context**: Project → Work Item → Task with appropriate granularity
- **Framework Intelligence**: Plugin-extracted facts and code amalgamations
- **Quality Enforcement**: Strict gates ensure agents follow proper development process
- **Dependency Management**: Structured task dependencies and blocker tracking

---

## ⚡ **Quick Start**

```bash
# Install APM (Agent Project Manager)
pip install -e .

# Initialize project (creates database, detects frameworks)
apm init "My Django App" /path/to/project
# → Detects: Python, Django, pytest
# → Generates: 222KB code amalgamations
# → Extracts: Versions, dependencies, structure

# Generate agent files (database → provider-specific files)
apm agents generate --all
# → Creates: .claude/agents/ directory with 50+ agent SOPs
# → Providers: Claude Code, Claude Desktop, custom

# Create work item (with type-driven validation)
apm work-item create "Add User Authentication" --type feature
# → System requires: DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks

# Create tasks (time-boxed and type-validated)
apm task create "Design auth schema" --type design --effort 3h
apm task create "Implement User model" --type implementation --effort 4h
# → IMPLEMENTATION tasks limited to 4h (enforced)

# Agent gets complete context
apm task context 123
# → Returns: Project facts + Work item scope + Task details + Code examples
```

---

## 🏗️ **Architecture**

### **Phase 1: Foundation** (✅ COMPLETE)

**Database Foundation**:
- 10 tables: 6 entities + 3 relationships (dependencies/blockers) + 1 system
- Pydantic three-layer pattern: Models → Adapters → Methods
- 7 SQLite triggers for workflow automation
- 28 indexes for performance
- **2,230+ tests passing (93-96% coverage)**

**Plugin System**:
- 11 active plugins: Python, JavaScript, TypeScript, Click, Django, React, HTMX, Alpine.js, Tailwind CSS, pytest, SQLite
- Plugin utilities: dependency_parsers, code_extractors, structure_analyzers
- 222KB code amalgamations generated from real project
- **12 tests passing**

**Security Framework**:
- Input validation (prevents injection, path traversal)
- Command security (whitelist, safe execution)
- Output sanitization (sensitive data redaction)
- **4 tests passing**

---

### **Phase 2: Core Systems** (✅ 95% COMPLETE)

**Workflow Management** (✅ 100% COMPLETE):
- Quality-gated transitions (state machine enforced)
- Time-boxing enforcement (IMPLEMENTATION ≤4h STRICT)
- Type-specific validation (FEATURE requires DESIGN+IMPL+TEST+DOC)
- Dependency validation (hard deps block start, blockers prevent completion)
- **93 tests passing, 96% coverage, production ready**

**CLI Interface** (✅ 100% COMPLETE - WI-007):
- 22 commands: agents, claude-code, commands, context, detect, document, idea, init, memory, migrate, provider, rules, search, session, skills, status, summary, task, template, testing, web, work-item
- LazyGroup pattern (<100ms startup)
- Rich formatting (tables, panels, colors)
- Time-boxing enforced at CLI boundary
- Quality gates displayed in real-time
- **107 tests passing, 92% coverage, production ready**

**Task Dependencies** (✅ 100% COMPLETE - WI-008):
- Hard/soft dependency types
- Internal + external blocker tracking
- Workflow integration (blocking enforced)
- 5 CLI commands (add-dependency, add-blocker, list, resolve)
- Auto-resolution SQL trigger
- **6 tests passing, 100% coverage, exceeds Asana capabilities**

**Context System** (Specified):
- Hierarchical context assembly (Project + Work Item + Task)
- Plugin fact integration
- Confidence scoring (RED/YELLOW/GREEN)
- Code amalgamation references

**CLI Interface** (Specified):
- Deferred until Workflow + Context complete

---

## 📊 **Type System**

### **Work Item Types** (7 strategic deliverables):
- **FEATURE**: New capability/system
- **ENHANCEMENT**: Improve existing
- **BUGFIX**: Fix substantial defect
- **RESEARCH**: Investigation/spike
- **PLANNING**: Architecture/design/roadmap
- **REFACTORING**: Code improvement
- **INFRASTRUCTURE**: DevOps/platform work

### **Task Types** (10 tactical activities):
- **DESIGN**: Design/planning (max 8h)
- **IMPLEMENTATION**: Write code (max 4h - STRICT)
- **TESTING**: Write tests (max 6h)
- **BUGFIX**: Fix bugs (max 4h)
- **REFACTORING**: Improve code (max 4h)
- **DOCUMENTATION**: Write docs (max 6h)
- **DEPLOYMENT**: Deploy/release (max 4h)
- **REVIEW**: Code review (max 2h)
- **ANALYSIS**: Research (max 8h)
- **SIMPLE**: Quick tasks (max 1h)

---

## 🚪 **Quality Gates**

### **State Transitions Require Quality**:

**proposed → validated**:
- ✅ All required task types present (FEATURE needs DESIGN+IMPLEMENTATION+TESTING+DOCUMENTATION)
- ✅ quality_metadata initialized
- ✅ No time-box violations

**validated → accepted**:
- ✅ All ambiguities resolved
- ✅ Agent assigned
- ✅ Design approved

**in_progress → review**:
- ✅ All acceptance criteria met
- ✅ Tests written and passing
- ✅ Code committed

**review → completed**:
- ✅ Quality review passed
- ✅ All feedback addressed
- ✅ Documentation complete

**Agents cannot skip gates** - system enforces quality.

---

## 🔌 **Plugin System**

### **Available Plugins**:

**Phase 1** (Self-Hosting):
- **Python**: Versions, dependencies, structure, standards → 186KB classes, 31KB functions
- **pytest**: Test framework, fixtures, patterns
- **Click**: CLI commands, structure
- **SQLite**: Schema, tables, indexes

**Phase 2A** (Planned - Priority 1, 14h):
- **JavaScript/Node.js**: Language foundation (enables 8+ plugins)
- **TypeScript**: Modern full-stack (80%+ adoption)

**Phase 2B** (Planned - Priority 2, 22h):
- **Django**: Models, views, URLs, admin
- **React**: Components, hooks, state management
- **Docker**: Containerization, docker-compose

**Phase 2C** (Planned - Priority 3, 16h):
- **Jest**: JavaScript testing
- **PostgreSQL**: Production database
- **Git**: VCS intelligence

**Total**: 52 hours → 95% real-world coverage

See: `docs/components/plugins/ROADMAP.md` (plugin development roadmap)

### **What Plugins Provide**:
1. **Project Facts**: Versions, dependencies, structure, code standards
2. **Code Amalgamations**: Searchable code groupings in `.agentpm/contexts/`
3. **Not Recommendations**: Plugins extract facts, don't advise

---

## 🗄️ **Database Schema**

### **Core Entities**:
- **projects**: Container with tech stack
- **work_items**: Features, bugs, research (strategic)
- **tasks**: Design, implementation, testing (tactical)
- **agents**: AI assistants with SOPs
- **contexts**: UnifiedSixW structure + confidence scoring
- **rules**: Quality gates, enforcement levels

### **Relationships**:
- **task_dependencies**: Task→Task prerequisites
- **task_blockers**: Impediment tracking with auto-resolution
- **work_item_dependencies**: Work Item→Work Item prerequisites

### **Features**:
- Unified 9-state workflow (proposed → completed)
- Hierarchical status (ProjectStatus, WorkItemStatus, TaskStatus)
- Quality metadata (JSON field for gate tracking)
- 7 triggers for automation

---

## 🧪 **Testing**

```bash
# Run all tests-BAK
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/core/database/ -v
python -m pytest tests/core/plugins/ -v

# With coverage
python -m pytest tests/ --cov=agentpm --cov-report=html

# Quick validation
python -m pytest tests/core/database/test_schema.py -v  # 15 tests, should all pass
```

**Current Status**: 2,230 tests passing (100% success rate, 92-100% coverage)

---

## 📚 **Documentation Structure**

```
docs/
├── user-guides/                          # 📖 USER DOCUMENTATION (START HERE!)
│   ├── INDEX.md                          # Complete navigation & learning paths
│   ├── getting-started.md                # Installation & first project (15 min)
│   ├── cli-reference/                    # Command reference & quick guide
│   ├── workflows/                        # Phase workflow & troubleshooting
│   ├── advanced/                         # Agents, memory, context, detection
│   ├── integrations/                     # Claude Code, Cursor, MCP setup
│   ├── use-cases/                        # Solo, consultant, enterprise, OSS
│   └── developer/                        # Architecture, patterns, contributing
├── components/                           # Component documentation
│   ├── workflow/                         # Workflow system (6-state + phases)
│   ├── plugins/                          # Plugin system
│   ├── cli/                              # CLI commands
│   ├── database/                         # Database architecture
│   ├── context/                          # Context assembly system
│   └── web-admin/                        # Web interface
├── adrs/                                 # Architecture Decision Records
├── specifications/                       # System specifications
└── developer-guide/                      # Developer documentation
```

### 🚀 **Quick Links**

**New Users**:
- 📖 [**User Guide Index**](docs/user-guides/INDEX.md) - Complete navigation with learning paths
- 🏁 [**Getting Started**](docs/user-guides/getting-started.md) - Install and create your first project (15 min)
- 📋 [**Quick Reference**](docs/user-guides/cli-reference/quick-reference.md) - 2-page command cheat sheet
- 🔄 [**Phase Workflow**](docs/user-guides/workflows/phase-workflow.md) - Understanding the 6-phase system

**Integration**:
- 🤖 [**Claude Code Integration**](docs/user-guides/integrations/claude-code/overview.md) - Use APM with Claude
- 🎯 [**Cursor Integration**](docs/user-guides/integrations/cursor/overview.md) - Use APM with Cursor
- 🔌 [**MCP Setup**](docs/user-guides/integrations/mcp-setup.md) - Model Context Protocol

**Developers**:
- 🏗️ [**Architecture Guide**](docs/user-guides/developer/architecture.md) - System design and principles
- 🔧 [**Three-Layer Pattern**](docs/user-guides/developer/three-layer-pattern.md) - Code standards
- 🤝 [**Contributing Guide**](docs/user-guides/developer/contributing.md) - How to contribute

---

## 🎯 **Current Status**

### **✅ Phase 1: Foundation - COMPLETE** (41 hours)
- Database with quality gates ✅
- Plugin system (4 plugins) ✅
- Security framework ✅

### **✅ Phase 2: Core Systems - 95% COMPLETE** (44 hours)
- Workflow Management (WI-005) ✅ 100%
- CLI Interface (WI-007) ✅ 100%
- Task Dependencies (WI-008) ✅ 100%
- Context System (WI-006) 🔄 75%

### **📋 Phase 3: Planning Complete** (8 hours today)
- Plugin Development Roadmap ✅
- Agent System Specification (WI-010) ✅
- README.md Implementation Standards ✅
- Test Environment Structure ✅ 30%

### **🎯 Next Priorities**
- Option A: Complete Testing Environment (2h) - Validate foundation
- Option B: Start WI-010 Agent System (26h) - Unblock production
- Option C: Start Plugin Phase 2A (14h) - Unlock frontend ecosystem

### **📈 Total Progress**
- **Phase 1**: 41 hours ✅ COMPLETE
- **Phase 2**: 44 hours ✅ 95% COMPLETE (WI-006 wiring remaining)
- **Planning**: 8 hours ✅ Roadmaps + specifications
- **Total**: 93 hours invested, production-ready core

---

## 📋 **Development Standards**

**CRITICAL**: Read `README.md` before any development work!

**Key Rules**:
- Three-layer database pattern (Models → Adapters → Methods) - MANDATORY
- Time-boxing (IMPLEMENTATION ≤4h STRICT)
- Testing >90% coverage (CI-004)
- FEATURE work items need DESIGN + IMPL + TEST + DOC
- CLI uses Rich formatting only
- Conventional commits with WI-XXX references

See `README.md` for complete implementation standards.

---

## 🔑 **Key Features**

### **Quality-Driven Development**:
- ✅ Time-boxing (IMPLEMENTATION max 4h)
- ✅ Required tasks per work item type
- ✅ Quality gates at each state transition
- ✅ No shortcuts allowed for agents

### **Intelligent Context**:
- ✅ Plugin-extracted facts (versions, dependencies, structure)
- ✅ Code amalgamations (222KB searchable code)
- ✅ Hierarchical assembly (task inherits work item + project)
- ✅ Confidence scoring (RED/YELLOW/GREEN)

### **Dependency Management**:
- ✅ Structured dependencies (task→task, work_item→work_item)
- ✅ Blocker tracking with auto-resolution
- ✅ Circular dependency detection
- ✅ SQLite triggers for automation

---

## 🤝 **Contributing**

### **Before Starting**:
1. Read `CLAUDE.md` (master orchestrator guide)
2. Review `docs/components/` (component documentation)
3. Check `docs/developer-guide/` (development standards)

### **Development Rules**:
- ✅ Pydantic three-layer pattern (Models → Adapters → Methods)
- ✅ Type-safe everywhere (no Dict[str, Any] in public APIs)
- ✅ ≥90% test coverage required
- ✅ Follow quality gate specifications (no shortcuts)

### **Testing**:
```bash
# Before committing
python -m pytest tests-BAK/ --cov=agentpm --cov-report=term-missing
# Must have ≥90% coverage
```

---

## 🚀 **Roadmap**

### **Q4 2025**: Phase 1 Foundation ✅
- Database, Plugins, Security

### **Q1 2026**: Phase 2 Core Systems
- Workflow, Context, CLI

### **Q2 2026**: Phase 3 Extended Plugins
- Django, HTML, JavaScript, Next.js

### **Q3 2026**: Phase 4 Integrations
- MCP server
- Asana/Linear sync
- Advanced features

---

## 📖 **Learn More**

- **Architecture**: `docs/specifications/AIPM-V2-COMPLETE-SPECIFICATION.md`
- **Plugin Development**: `docs/components/plugins/developer-guide.md`
- **Workflow System**: `docs/components/workflow/6-state-workflow-system.md`
- **Context System**: `docs/components/context/README.md` (coming soon)

---

## 📊 **Statistics**

- **Code**: 8,000+ lines
- **Tests**: 2,230+ passing (93-96% coverage on core modules)
- **Database**: 10 tables, 28 indexes, 7 triggers
- **Plugins**: 11 active (Python, JavaScript, TypeScript, Click, Django, React, HTMX, Alpine.js, Tailwind CSS, pytest, SQLite)
- **Documentation**: 50+ specification documents
- **Specifications**: Complete through Phase 2

---

## 💡 **What Makes APM (Agent Project Manager) Different**

**Not Just Task Tracking**:
- Quality-gated workflow (agents must follow process)
- Time-boxed tasks (IMPLEMENTATION max 4h - forces decomposition)
- Type-specific validation (FEATURE requires DESIGN+IMPLEMENTATION+TESTING+DOCUMENTATION)
- Framework intelligence (plugins provide context, not generic advice)

**Built for AI Agents**:
- Strict enforcement (no shortcuts)
- Complete context delivery (hierarchical)
- Quality metadata tracking (acceptance criteria, test status, review approval)
- Template-driven validation (different requirements per task type)

---

## 🎯 **Next Steps**

**For Developers**:
1. Read `CLAUDE.md` (master orchestrator)
2. Review `docs/developer-guide/` (development standards)
3. Check `docs/components/` (component architecture)
4. Run tests: `python -m pytest tests/ -v`

**For Users**:
1. Install: `pip install -e .`
2. Initialize: `apm init "My Project"`
3. Create work items and tasks
4. Use phase workflow: `apm work-item next <id>`

---

**APM (Agent Project Manager): Quality-driven development for AI coding agents**

**Status**: Foundation complete, core systems in progress
**License**: Apache 2.0
**Documentation**: Complete specifications in `docs/project-plan/`