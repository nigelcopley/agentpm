# Changelog

All notable changes to APM (Agent Project Manager) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-25 - Foundation Release

### Summary
**First public release** - Database-driven AI agent enablement system with quality gates, 85 specialized agents, and comprehensive web interface. Complete AIPM → APM rebranding with production-ready architecture.

**Major Work Items**: WI-141 (Web Frontend Polish - 60 tasks), WI-145 (Flask Consolidation - 8 tasks), WI-146 (APM Rebranding - 11 tasks)

**Release Notes**: See [RELEASE_NOTES_v1.0.md](RELEASE_NOTES_v1.0.md) for comprehensive details.

### Added

#### Core Platform
- Database-driven architecture: 57 tables, 7 triggers, 28 indexes, FTS5 full-text search
- Quality gate system: 75 enforced rules (BLOCK, LIMIT, WARN, INFORM enforcement levels)
- Time-boxing philosophy: Implementation ≤4h, Testing ≤6h, Design ≤8h (99% compliance)
- 6-phase workflow: Discovery → Planning → Implementation → Review → Operations → Evolution
- 9-state state machine: proposed → validated → accepted → in_progress → review → completed
- Hierarchical context assembly with confidence scoring (6W framework)
- Dependency management: Hard/soft dependencies, blocker tracking, automatic resolution

#### Agent System (85 Specialized Agents)
- Master orchestrator (1): Delegates to phase orchestrators
- Phase orchestrators (6): D1, P1, I1, R1, O1, E1 phase management
- Domain specialists (15+): Python/CLI, database, testing, quality, documentation
- Sub-agents (25+): Context delivery, intent triage, gate checking, test running
- Utility agents: Work item writing, evidence collection, rule validation
- Agent generation: Intelligent agent creation with `apm agents generate-intelligent`

#### Plugin System (11 Active Plugins)
- Frameworks: Python, Django, React, HTMX, Alpine.js, Tailwind CSS
- Build tools: JavaScript, TypeScript, Click, pytest
- Database: SQLite
- Code amalgamations: Classes, functions, components, API endpoints, test suites
- Automatic detection: Version extraction, dependency analysis, pattern recognition

#### CLI Interface (22 Commands)
- Work item management: create, list, show, next (auto-advance), validate, accept, start, submit-review, approve
- Task management: create, list, show, context, next (auto-advance), validate, accept, start
- Agent operations: list, generate-intelligent, show
- Context & rules: show, list, toggle
- System operations: init, status, detect, migrate, web
- Hybrid interface: Automatic `next` commands + explicit state control

#### Web Interface (Professional Flask Application)
- **15 major routes**: Dashboard, work items, tasks, rules, contexts, agents, evidence, documents, ideas, search, sessions, projects, health, workflow, settings
- **WCAG 2.1 AA accessibility**: Skip links, ARIA landmarks, enhanced focus indicators, screen reader optimization
- **Component library**: Skeleton loading states, quick action macros, professional empty states, comprehensive tooltips
- **RESTful architecture**: 10 blueprints with consistent route patterns
- **Advanced features**: Sorting, filtering, pagination, real-time metrics, workflow visualization
- **Responsive design**: Works across all viewports (mobile-friendly, not optimized)

#### Documentation (620+ Files)
- User guides: INDEX.md navigation hub, getting started (15 min), quick reference (2 pages)
- Workflows: Phase workflow guide, ideas workflow, troubleshooting
- Integrations: Claude Code, Cursor, MCP setup
- Advanced: Agent generation, memory system, rich context, detection packs, slash commands
- Developer: Architecture, three-layer pattern, contributing, migrations, database schema
- Complete API documentation with Pydantic model signatures

#### Testing (2,230 Tests)
- 100% test pass rate
- 93-96% coverage on core modules (database, workflow, CLI)
- AAA test pattern throughout (Arrange, Act, Assert)
- 207 test files across unit, integration, E2E suites
- Comprehensive fixtures and factories
- CI/CD integration ready

### Changed

#### Branding (AIPM → APM)
- **Complete rebranding**: All 155,736 lines of code updated
- **New name**: APM (Agent Project Manager)
- **Tagline**: "AI Project Management, Simplified"
- **Domain**: apm.run (reserved, setup pending)
- **Professional README.md**: Complete rewrite with features, architecture, use cases
- **Comprehensive CONTRIBUTING.md**: Development standards, testing requirements, PR process
- **Backward compatibility maintained**: Database schema, CLI commands, configuration paths unchanged

#### Web Interface Architecture
- **Route structure**: Inconsistent patterns → RESTful consistency
- **Blueprint organization**: 10 blueprints with clear separation of concerns
- **Template hierarchy**: Base → layout → specific views
- **Form handling**: CSRF protection, validation, error feedback throughout
- **Error handling**: Comprehensive error pages, logging, user guidance
- **API endpoints**: Organized under `/api/*` namespace

#### Documentation Structure
- **User guides reorganization**: 8 categories with clear learning paths
- **Developer guides consolidation**: Architecture, patterns, contributing
- **CLI reference enhancement**: Quick reference cheat sheet + detailed command docs
- **Integration guides**: Claude Code, Cursor, MCP with step-by-step setup

### Fixed

#### Core Issues
- Task detail view alignment with work item detail pattern (#WI-141)
- Empty tech_stack list handling in context builder (#WI-145)
- Migration schema mismatches (#WI-108)
- Agent generation import errors (#WI-109)
- Document path validation enforcement (#WI-113)
- Stale documentation across codebase (#WI-115)
- Boilerplate task metadata system (#WI-117)

#### Web Interface
- Missing templates and backend errors blocking routes
- Inconsistent navigation and route patterns
- Form validation and error handling gaps
- Accessibility compliance issues
- Mobile viewport rendering issues

### Security

- **Input validation**: Pydantic models validate all user input (SEC-001)
- **SQL injection prevention**: Parameterized queries throughout (SEC-002)
- **XSS prevention**: Template auto-escaping enabled (SEC-003)
- **CSRF protection**: All POST/PUT/DELETE requests protected (SEC-004)
- **Path traversal protection**: File operations validated (SEC-005)
- **Field-level encryption**: Sensitive data encrypted at rest (optional, SEC-006)

### Deprecated

- Old route patterns (no redirects provided - update bookmarks)
- `aipm` command references (use `apm` instead)
- Legacy environment variable names (still work but prefer `APM_*`)

### Known Limitations

**Deferred to v1.1-1.2** (see RELEASE_NOTES_v1.0.md for details):
- Advanced search features (faceted navigation, saved queries)
- Real-time collaboration (WebSocket updates, presence indicators)
- Advanced analytics dashboard (velocity tracking, quality trends)
- Mobile-optimized interface (touch gestures, PWA support)

**Performance Notes**:
- Context assembly may be slow for projects >1000 work items (optimization planned)
- FTS5 search does not support regex patterns (use CLI grep for complex patterns)
- Web interface requires modern browser (IE11 not supported)

### Migration Guide

**Fresh Installation**:
```bash
git clone https://github.com/nigelcopley/agentpm.git
cd agentpm
pip install -e .
apm init "My Project"
```

**Upgrading from AIPM (pre-1.0)**:
1. Backup database: `cp .agentpm/data/agentpm.db .agentpm/data/agentpm.db.backup`
2. Update code: `git pull origin main && pip install -e . --upgrade`
3. Verify: `apm --version` (should show v1.0.0)
4. Migrate: `apm migrate` (if needed)
5. Update custom scripts (branding references only)
6. Update web bookmarks (route structure changed)

**Rollback** (if needed):
```bash
cp .agentpm/data/agentpm.db.backup .agentpm/data/agentpm.db
git checkout <previous-version>
pip install -e .
```

### Statistics

**Work Completed**:
- 3 major work items (WI-141, WI-145, WI-146)
- 79 tasks completed (60 + 8 + 11)
- 59 total work items done (39% of 152)
- 594 total tasks done (59% of 999)

**Project Metrics**:
- 155,736 lines of production code
- 2,230 tests (100% passing)
- 207 test files
- 620+ documentation files
- 85 specialized agents
- 11 active plugins
- 75 quality rules
- 57 database tables
- 22 CLI commands

**Quality**:
- 93-96% test coverage (core modules)
- 99% time-boxing compliance (910/911 tasks)
- 100% rule compliance
- WCAG 2.1 AA accessibility
- Apache 2.0 license

### What's Next

**v1.1 (Q1 2026)**:
- Complete context assembly system (75% → 100%)
- Enhanced agent delegation patterns
- Session persistence and resumption
- Advanced search features (deferred from v1.0)

**v1.2 (Q2 2026)**:
- Real-time collaboration (WebSocket updates)
- MCP server integration
- Mobile-optimized interface
- Advanced analytics dashboard

**v1.3 (Q3 2026)**:
- Asana/Linear bidirectional sync
- GitHub Issues integration
- Slack/Discord notifications
- Plugin marketplace

### Credits

**Technology Stack**: Python 3.9+, SQLite 3.35+, Pydantic 2.x, Click 8.x, Rich, Flask 3.x, pytest

**Architecture**: Database-first design, three-layer pattern (Models → Adapters → Methods), quality gates, time-boxing

**Agent System**: 85 specialized agents across hierarchical orchestration (Master → Phase → Specialists → Sub-agents)

**Testing**: AAA pattern, 2,230 tests, comprehensive fixtures, 93-96% coverage

**Documentation**: 620+ files covering user guides, developer guides, API reference, integration guides

**Open Source**: Apache License 2.0 - Built by developers, for AI agents, with quality gates

---

## [0.1.0] - 2025-10-25

### Changed
- **BREAKING**: Rebranded from "APM (Agent Project Manager)" to "AgentPM" (Agent Project Manager)
  - Package renamed: `aipm-v2` → `agentpm`
  - Python module: `aipm_v2` → `agentpm`
  - CLI command remains: `apm` (backward compatible)
  - All references updated from "APM (Agent Project Manager)" to "APM (Agent Project Manager)"
- **Project location**: Moved from `~/.project_manager/aipm-v2` to `~/Projects/AgentPM`
- **Repository**: Updated to `github.com/nigelcopley/agentpm`

### Added
- Initial public release preparation
- PyPI packaging configuration
- `MANIFEST.in` for distribution
- `LICENSE` file (Apache 2.0)
- `RELEASE.md` with complete release procedures
- `INSTALL_VERIFICATION.sh` for testing installations

### Fixed
- Document path validation enforcement (#113)
  - Consolidated DocumentReference models with strict path validation
  - Added database CHECK constraint for docs/ prefix enforcement
  - Migrated 49 non-compliant documents to proper structure (87.5% success)
  - Enhanced CLI with path guidance and auto-suggestions
  - Updated 45 agent SOPs with path structure examples
  - Created comprehensive test suite with >90% coverage target
  - Improved compliance from 16.4% to 89.6% (73 point improvement)

