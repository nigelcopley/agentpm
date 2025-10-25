---
title: Claude Code Comprehensive Integration Plan
work_item: WI-116
task: T-616
version: 1.0.0
date: 2025-10-21
status: Complete
author: Implementation Orchestrator
tags:
  - claude-code
  - integration
  - implementation-plan
  - task-sequencing
---

# Claude Code Comprehensive Integration Plan

## Executive Summary

This plan consolidates extensive research on Claude Code capabilities into a cohesive implementation roadmap for WI-116. Based on comprehensive analysis of Claude Code's official documentation, existing AIPM architecture, and prior integration attempts, this plan defines a phased approach to achieving full Claude Code integration for APM (Agent Project Manager).

**Key Insight**: Claude Code operates through natural language invocation and YAML-defined agents, NOT through programmatic APIs with typed parameters. Our integration must align with this reality while maintaining AIPM's database-first, multi-agent architecture.

**Timeline**: 24 hours (implementation) across 11 tasks
**Complexity**: High (architectural alignment required)
**Dependencies**: WI-114 (Persistent Memory), WI-119 (Integration Consolidation)
**Risk Level**: Medium (well-researched, clear path forward)

---

## 1. Feature Inventory: What Claude Code Provides

### 1.1 Core Capabilities

Based on comprehensive documentation review ([claude-code-integration-comprehensive-analysis.md](../../analysis/agents/claude-code/claude-code-integration-comprehensive-analysis.md)), Claude Code offers:

#### **Plugin System**
- **Structure**: `.claude-plugin/plugin.json` manifest + modular capabilities
- **Components**: Commands (slash commands), Agents (subagents), Skills, Hooks
- **Distribution**: Git-based sharing, team installation support
- **Integration Point**: AIPM can package as distributable plugin

#### **Hooks System** (9 Event Types)
- **SessionStart**: Initialize context from database (CRITICAL for AIPM)
- **SessionEnd**: Persist learnings and decisions
- **PreToolUse/PostToolUse**: Validate operations, enforce rules
- **UserPromptSubmit**: Intent classification, routing decisions
- **Stop/SubagentStop**: Capture outcomes, update state
- **PreCompact**: Preserve critical context before compression
- **Notification**: Handle permission requests

**Status**: Partially implemented (`.claude/hooks/` directory exists with 8 hook scripts)

#### **Subagent Orchestration**
- **Invocation Method**: Natural language descriptions, not programmatic API
- **Parallelism**: Up to 10 concurrent subagent tasks
- **Context Isolation**: Each subagent receives own context window
- **Agent Definition**: YAML frontmatter + markdown body in `.claude/agents/`

**Critical Finding**: No `subagent_type` parameter exists in official API. AIPM's delegation pseudocode is documentation notation, not actual invocation syntax.

#### **Settings System**
- **Locations**: `~/.claude/settings.json` (user), `.claude/settings.json` (project), `.claude/settings.local.json` (local)
- **Configuration**: Hooks registration, output styles, MCP servers
- **Validation**: JSON schema-based, safe defaults
- **Integration Point**: AIPM settings can be injected via SessionStart hook

#### **Memory System**
- **CLAUDE.md**: Project-specific instructions (AIPM's master orchestrator file)
- **Agent Files**: Individual agent definitions with role, capabilities, constraints
- **Context Efficiency**: Structured files reduce token consumption vs conversation history
- **Integration Point**: AIPM can generate/sync memory files from database

#### **Slash Commands**
- **Definition**: Markdown files in `.claude/commands/` or plugins
- **Format**: YAML frontmatter + command description
- **Usage**: `/command-name` in Claude session
- **Integration Point**: Custom AIPM commands (`/apm-status`, `/apm-context`)

#### **Checkpointing**
- **Session Snapshots**: Durable state for recovery and analysis
- **Transcript Storage**: JSONL format conversation history
- **Integration Point**: Link checkpoints to AIPM work items/tasks

#### **MCP Integration**
- **Transports**: HTTP (recommended), stdio, SSE (deprecated)
- **Scopes**: Local, project (`.mcp.json`), user
- **Tools**: Natural language queries against MCP servers
- **Integration Point**: AIPM database as MCP server (future enhancement)

### 1.2 What Claude Code Does NOT Provide

Based on analysis:
- **No programmatic subagent API** - Natural language invocation only
- **No typed delegation parameters** - Relies on description matching
- **No explicit input/output contracts** - Free-form natural language
- **No Agent Skills documentation** - Feature exists but docs incomplete (404 error)
- **No guaranteed subagent awareness** - Subagents appear as fresh Claude instances

---

## 2. AIPM Integration Points: Where We Connect

### 2.1 Database-First Architecture Alignment

**AIPM Core Principle**: Database is source of truth, not files

**Integration Strategy**:
```
Database (Source of Truth)
  ↓
SessionStart Hook (Python script)
  ↓
Query Database (rules, work items, tasks, context)
  ↓
Generate Memory Files (.claude/ directory)
  ↓
Claude Code Reads Memory
  ↓
Session Work Performed
  ↓
SessionEnd Hook (Python script)
  ↓
Persist Updates to Database
```

**Key Files**:
- `.claude/hooks/session-start.py` - Load context from database
- `.claude/hooks/session-end.py` - Save learnings to database
- `.claude/CLAUDE.md` - Master orchestrator (generated from database)
- `.claude/agents/**/*.md` - Agent definitions (static, with dynamic context injection)

### 2.2 Three-Tier Agent Architecture Alignment

**AIPM Architecture**:
```
Tier 3: Master Orchestrator (CLAUDE.md)
  ├─ Routes by phase and artifact type
  └─ NEVER implements directly

Tier 2: Phase Orchestrators (6 agents)
  ├─ definition-orch (D1 phase)
  ├─ planning-orch (P1 phase)
  ├─ implementation-orch (I1 phase)
  ├─ review-test-orch (R1 phase)
  ├─ release-ops-orch (O1 phase)
  └─ evolution-orch (E1 phase)

Tier 1: Sub-Agents (~25 single-purpose agents)
  ├─ context-delivery (MANDATORY - session start)
  ├─ intent-triage, ac-writer, test-runner
  └─ quality-gatekeeper, etc.
```

**Claude Code Compatibility**:
- **Tier 3**: CLAUDE.md with natural language routing instructions
- **Tier 2**: `.claude/agents/orchestrators/*.md` with proactive invocation triggers
- **Tier 1**: `.claude/agents/sub-agents/*.md` with focused descriptions

**Required Change**: Update delegation language from pseudo-API syntax to natural language:

**Before** (Pseudo-API):
```
delegate -> intent-triage
input: {request: "raw user request"}
expect: {work_type, domain, complexity, priority}
```

**After** (Natural Language):
```
Use the intent-triage subagent to classify this request.

Provide the subagent with:
- Raw user request: "[request text]"
- Project context: [context summary]

The subagent will analyze and return:
- Work type (FEATURE, ENHANCEMENT, FIX, etc.)
- Domain classification (backend, frontend, database, etc.)
- Complexity assessment (simple, moderate, complex)
- Priority recommendation (P0-P4)
```

### 2.3 Workflow Integration Points

| AIPM Workflow Phase | Claude Code Hook | Action | Database Update |
|---------------------|------------------|--------|-----------------|
| Session Start | SessionStart | Load work item/task context from DB | Read-only |
| User Request | UserPromptSubmit | Route to appropriate orchestrator | Log intent |
| Tool Execution | PreToolUse | Validate against rules (DP-*, TES-*, SEC-*) | Audit log |
| Tool Completion | PostToolUse | Capture artifacts, update quality metrics | Write results |
| Subagent Complete | SubagentStop | Extract compressed findings, update context | Cache results |
| Session End | SessionEnd | Persist decisions, learnings, status updates | Write state |
| Context Overflow | PreCompact | Preserve critical context (AC, risks, decisions) | Checkpoint |

### 2.4 Quality Gate Integration

**AIPM Gates** → **Claude Code Enforcement**:

- **D1 (Definition)**: Validated via `definition.gate-check` agent (invoked at phase completion)
- **P1 (Planning)**: Validated via `planning.gate-check` agent (checks task breakdown, estimates)
- **I1 (Implementation)**: Validated via `implementation.gate-check` agent (tests, docs, migrations)
- **R1 (Review)**: Validated via `quality-gatekeeper` agent (AC verification, test pass rate)
- **O1 (Operations)**: Validated via `operability-gatecheck` agent (deployment health)
- **E1 (Evolution)**: Validated via `evolution.gate-check` agent (telemetry analysis)

**Hook Integration**: PreToolUse hook can block operations that would violate BLOCK-level rules (DP-001 to DP-008, SEC-001 to SEC-006, etc.)

---

## 3. Implementation Phases: Tasks 617-627 Mapped

### Phase 1: Foundation (Tasks 617-618) - 6 hours

**Objective**: Establish core infrastructure for Claude Code integration

#### **Task 617: Create Claude Code Plugin System** (3h)
**Priority**: P0 (CRITICAL - all other tasks depend on this)

**Deliverables**:
- `.claude-plugin/plugin.json` manifest
- Plugin registry service (`agentpm/services/claude/plugin_registry.py`)
- Plugin loader (loads hooks, commands, agents from database metadata)
- Plugin validation (schema checks, dependency resolution)

**Acceptance Criteria**:
- [ ] Plugin manifest validates against Claude Code schema
- [ ] Registry can load/unload plugins dynamically
- [ ] Dependencies tracked and resolved
- [ ] Unit tests: 90%+ coverage

**Integration Points**:
- Database: `plugins` table (plugin metadata, enabled state)
- Hooks: Plugin system loads hook configurations
- Commands: Plugin system registers slash commands

#### **Task 618: Create Claude Code Hooks System** (3h)
**Priority**: P0 (CRITICAL - enables context persistence)

**Deliverables**:
- Hooks engine (`agentpm/services/claude/hooks_engine.py`)
- Normalized event bus (all 9 hook types)
- Hook configuration manager (loads from settings.json + database)
- Error handling with graceful degradation

**Acceptance Criteria**:
- [ ] All 9 hook events supported (SessionStart, SessionEnd, etc.)
- [ ] Hooks can be registered via database or settings files
- [ ] Event payloads validated and sanitized
- [ ] Exit code 0 (success), Exit code 2 (blocking error) handled correctly
- [ ] Integration tests: End-to-end hook lifecycle

**Critical Hooks**:
```python
# SessionStart: Load context from database
def session_start_handler(event):
    work_item = db.get_active_work_item()
    context = ContextAssemblyService.assemble_work_item_context(work_item.id)
    print(json.dumps(context))  # Stdout to Claude
    sys.exit(0)

# SessionEnd: Persist learnings
def session_end_handler(event):
    learnings = extract_learnings_from_transcript(event.transcript_path)
    db.save_session_summary(learnings)
    sys.exit(0)
```

**Dependencies**: Task 617 (plugin system must load hooks)

---

### Phase 2: Core Features (Tasks 619-621) - 7 hours

**Objective**: Enable subagent orchestration, settings management, and slash commands

#### **Task 619: Create Claude Code Subagents System** (3h)
**Priority**: P1 (HIGH - enables multi-agent workflows)

**Deliverables**:
- Subagent orchestrator (`agentpm/services/claude/subagent_orchestrator.py`)
- Strategy-based routing (maps AIPM phases to orchestrator agents)
- Dependency-aware execution (tasks with dependencies execute sequentially)
- Lifecycle management (track subagent state, outcomes)

**Acceptance Criteria**:
- [ ] Can invoke subagents via natural language descriptions
- [ ] Parallel execution up to 10 concurrent tasks
- [ ] Dependency resolution prevents premature execution
- [ ] Subagent outcomes captured and cached
- [ ] Integration tests: Parallel + sequential workflows

**Natural Language Routing Examples**:
```python
routing_strategies = {
    "D1_DISCOVERY": "Use the definition-orch subagent to complete discovery...",
    "P1_PLAN": "Use the planning-orch subagent to create implementation plan...",
    "I1_IMPLEMENTATION": "Use the implementation-orch subagent to implement feature...",
}
```

**Dependencies**: Task 618 (hooks system must trigger orchestrator)

#### **Task 620: Create Claude Code Settings System** (2h)
**Priority**: P2 (MEDIUM - improves configurability)

**Deliverables**:
- Settings manager (`agentpm/services/claude/settings_manager.py`)
- Typed settings with Pydantic validation
- Multi-layer configuration (user → project → local)
- Safe defaults with environment variable expansion

**Acceptance Criteria**:
- [ ] Settings loaded from ~/.claude/, .claude/, .claude/settings.local.json
- [ ] Validation prevents invalid configurations
- [ ] Environment variables expanded (`${API_TOKEN}`)
- [ ] CLI commands: `apm claude-settings show`, `apm claude-settings update`
- [ ] Unit tests: 95%+ coverage

**Settings Schema**:
```python
class ClaudeSettings(BaseModel):
    hooks: Dict[str, List[HookConfig]]
    output_style: str = "default"
    mcp_servers: Dict[str, MCPServerConfig] = {}
    agent_defaults: AgentDefaults
```

**Dependencies**: Task 617 (plugin system uses settings)

#### **Task 621: Create Claude Code Slash Commands** (2h)
**Priority**: P2 (MEDIUM - improves UX)

**Deliverables**:
- Command registry (`agentpm/services/claude/command_registry.py`)
- Declarative command definitions (markdown files in `.claude/commands/`)
- Validation and rich help
- 5 core commands: `/apm-status`, `/apm-context`, `/apm-gates`, `/apm-rules`, `/apm-agents`

**Acceptance Criteria**:
- [ ] Commands defined in `.claude/commands/*.md` format
- [ ] Command validation (arguments, permissions)
- [ ] Help text auto-generated from markdown
- [ ] Integration tests: All 5 commands functional
- [ ] Documentation: Command reference guide

**Example Command**:
```markdown
---
name: apm-status
description: Show current AIPM project status
---

Displays:
- Active work items and their phases
- Current tasks (ready, in-progress, blocked)
- Recent quality gate results
- Pending blockers

Usage: `/apm-status [--verbose]`
```

**Dependencies**: Task 617 (plugin system registers commands)

---

### Phase 3: Advanced Features (Tasks 622-624) - 10 hours

**Objective**: Add checkpointing, memory tools, and comprehensive orchestration

#### **Task 622: Create Claude Code Checkpointing System** (3h)
**Priority**: P2 (MEDIUM - enables recovery and analysis)

**Deliverables**:
- Checkpoint service (`agentpm/services/claude/checkpoint_service.py`)
- Durable snapshots of interaction and context state
- Checkpoint kinds: SESSION, DECISION, IMPLEMENTATION, REVIEW
- Recovery mechanism (restore from checkpoint)

**Acceptance Criteria**:
- [ ] Checkpoints saved with metadata (timestamp, work_item_id, task_id)
- [ ] Diff tracking (what changed since last checkpoint)
- [ ] Recovery: `apm checkpoint restore <id>`
- [ ] Integration with SessionEnd hook (auto-checkpoint on session close)
- [ ] Storage: `.aipm/checkpoints/` + database references
- [ ] Integration tests: Create, restore, diff

**Checkpoint Schema**:
```python
class Checkpoint(BaseModel):
    id: str
    kind: CheckpointKind
    created_at: datetime
    work_item_id: Optional[int]
    task_id: Optional[int]
    metadata: Dict[str, Any]
    diff_refs: List[str]  # Git commit SHAs or file hashes
    transcript_path: str
```

**Dependencies**: Task 618 (hooks trigger checkpoints)

#### **Task 623: Create Claude Code Memory Tool System** (3h)
**Priority**: P1 (HIGH - database-driven persistent memory)

**Deliverables**:
- Memory system (`agentpm/services/claude/memory_system.py`)
- Database-to-file sync (RULES, PRINCIPLES, WORKFLOW, AGENTS, CONTEXT, PROJECT, IDEAS)
- Auto-generation from database state
- Conflict resolution (last-write-wins with diff checkpoints)

**Acceptance Criteria**:
- [ ] Memory files generated from database (not manually edited)
- [ ] 7 memory file types: RULES, PRINCIPLES, WORKFLOW, AGENTS, CONTEXT, PROJECT, IDEAS
- [ ] Sync triggered by SessionStart hook
- [ ] Content hashing prevents unnecessary rewrites
- [ ] CLI: `apm memory sync`, `apm memory show <type>`
- [ ] Integration tests: Sync, conflict resolution

**Memory File Types**:
```python
class MemoryScope(Enum):
    RULES = "rules"              # Project rules from database
    PRINCIPLES = "principles"    # Architectural principles (ADRs)
    WORKFLOW = "workflow"        # Phase gates and workflow
    AGENTS = "agents"            # Agent metadata and capabilities
    CONTEXT = "context"          # Active work item/task context
    PROJECT = "project"          # Business objectives, tech stack
    IDEAS = "ideas"              # Backlog, future enhancements
```

**Storage Locations**:
```
.claude/memory/
  ├── RULES.md           (from database: apm rules list)
  ├── PRINCIPLES.md      (from database: ADRs, design decisions)
  ├── WORKFLOW.md        (from database: phase definitions, gates)
  ├── AGENTS.md          (from database: agent catalog)
  ├── CONTEXT.md         (generated per session: active work)
  ├── PROJECT.md         (from database: project metadata)
  └── IDEAS.md           (from database: backlog items)
```

**Dependencies**: Task 618 (SessionStart hook triggers sync), WI-114 (persistent memory design)

#### **Task 624: Create Claude Code Orchestrator** (4h)
**Priority**: P1 (HIGH - coordinates all integration components)

**Deliverables**:
- Integration service (`agentpm/services/claude/integration_service.py`)
- Orchestrates: plugins, hooks, subagents, memory, checkpoints, commands
- Error handling with agent-first messaging
- Performance monitoring (timing, token usage)

**Acceptance Criteria**:
- [ ] Single service coordinates all Claude Code components
- [ ] Initialization: Load plugins, register hooks, sync memory
- [ ] Event handling: Route hook events to appropriate handlers
- [ ] Subagent execution: Manage lifecycle, dependencies, parallelism
- [ ] Graceful degradation: Continue if non-critical components fail
- [ ] Logging and telemetry: Track usage patterns
- [ ] Integration tests: End-to-end workflows (D1 → P1 → I1 → R1)

**Service Interface**:
```python
class ClaudeIntegrationService:
    def initialize(self, context: ProjectContext) -> IntegrationSession:
        """Load plugins, register hooks, sync memory"""

    def handle_event(self, event: HookEvent) -> EventResult:
        """Route hook events to handlers"""

    def update_memory(self, scope: MemoryScope) -> MemoryUpdateResult:
        """Sync memory files from database"""

    def run_subagent(self, plan: SubagentPlan) -> SubagentResult:
        """Execute subagent with dependency awareness"""

    def checkpoint(self, kind: CheckpointKind, data: dict) -> CheckpointRef:
        """Create durable snapshot"""

    def execute_slash(self, command: SlashCommand, args: dict) -> CommandResult:
        """Execute registered command"""
```

**Dependencies**: All previous tasks (orchestrates everything)

---

### Phase 4: Finalization (Tasks 625-627) - 7 hours

**Objective**: CLI integration, comprehensive testing, and documentation

#### **Task 625: Create CLI Commands for Claude Code Integration** (2h)
**Priority**: P2 (MEDIUM - enables manual control)

**Deliverables**:
- CLI command group (`agentpm/cli/commands/claude.py`)
- 8 commands: `init`, `status`, `sync-memory`, `checkpoint`, `restore`, `settings`, `hooks`, `agents`
- Rich output formatting (tables, colors, progress bars)
- Click validators and auto-completion

**Acceptance Criteria**:
- [ ] All 8 commands functional
- [ ] Help text clear and actionable
- [ ] Output formatted for both humans and scripts (--format=json)
- [ ] Error messages include next actions
- [ ] Integration tests: All commands with sample data

**Commands**:
```bash
apm claude init                    # Initialize Claude Code integration
apm claude status                  # Show integration status
apm claude sync-memory [--scope]   # Sync memory files from database
apm claude checkpoint [--kind]     # Create checkpoint
apm claude restore <id>            # Restore from checkpoint
apm claude settings [show|update]  # Manage settings
apm claude hooks [list|test]       # Manage hooks
apm claude agents [list|validate]  # Manage agents
```

**Dependencies**: Task 624 (CLI calls integration service)

#### **Task 626: Create Comprehensive Test Suite** (3h)
**Priority**: P1 (HIGH - ensures quality)

**Deliverables**:
- Unit tests for all services (plugins, hooks, subagents, memory, checkpoints)
- Integration tests for end-to-end workflows
- Fixtures for sample data (work items, tasks, agents)
- Coverage report: ≥90% for integration components

**Test Structure**:
```
tests/services/claude/
  ├── test_plugin_registry.py       (unit)
  ├── test_hooks_engine.py          (unit + integration)
  ├── test_subagent_orchestrator.py (unit + integration)
  ├── test_settings_manager.py      (unit)
  ├── test_command_registry.py      (unit)
  ├── test_checkpoint_service.py    (unit + integration)
  ├── test_memory_system.py         (unit + integration)
  ├── test_integration_service.py   (integration)
  └── test_end_to_end_workflows.py  (integration)
```

**Coverage Targets**:
- Plugin system: ≥90%
- Hooks engine: ≥95% (critical path)
- Subagent orchestrator: ≥90%
- Memory system: ≥95% (critical path)
- Integration service: ≥85%

**Dependencies**: All implementation tasks (tests validate implementations)

#### **Task 627: Create Comprehensive Documentation** (2h)
**Priority**: P2 (MEDIUM - enables adoption)

**Deliverables**:
- User guide: Claude Code integration setup and usage
- Developer guide: Extending and customizing integration
- API reference: Services, models, hooks
- Troubleshooting guide: Common issues and solutions

**Documentation Structure**:
```
docs/guides/user_guide/
  └── claude-code-integration.md    (setup, usage, examples)

docs/guides/developer_guide/
  └── claude-code-extension.md      (custom hooks, plugins)

docs/reference/api/
  └── claude-code-services.md       (API reference)

docs/operations/troubleshooting/
  └── claude-code-issues.md         (FAQ, solutions)
```

**Content Requirements**:
- Installation instructions (step-by-step)
- Configuration examples (hooks, settings, memory)
- Usage workflows (session lifecycle, subagent delegation)
- Extension patterns (custom hooks, plugins)
- Troubleshooting decision trees

**Dependencies**: All tasks (documents complete system)

---

## 4. Task Sequencing and Dependencies

### Critical Path (Must Execute Sequentially)

```
Task 617 (Plugin System) [3h]
  ↓
Task 618 (Hooks System) [3h]
  ↓
Task 619 (Subagents) [3h] + Task 620 (Settings) [2h] (Parallel)
  ↓
Task 621 (Commands) [2h] + Task 622 (Checkpointing) [3h] (Parallel)
  ↓
Task 623 (Memory System) [3h]
  ↓
Task 624 (Orchestrator) [4h]
  ↓
Task 625 (CLI) [2h] + Task 626 (Tests) [3h] (Parallel)
  ↓
Task 627 (Documentation) [2h]
```

**Total Sequential Time**: 24 hours
**With Parallelization**: ~20 hours

### Dependency Matrix

| Task | Depends On | Can Parallelize With | Blocks |
|------|-----------|---------------------|--------|
| 617 | None | - | 618, 620, 621 |
| 618 | 617 | - | 619, 622, 623 |
| 619 | 618 | 620 | 624 |
| 620 | 617 | 619, 621 | 624 |
| 621 | 617 | 620, 622 | 624 |
| 622 | 618 | 621 | 624 |
| 623 | 618 | - | 624 |
| 624 | 619, 620, 621, 622, 623 | - | 625, 626 |
| 625 | 624 | 626 | 627 |
| 626 | 624 | 625 | 627 |
| 627 | 625, 626 | - | None |

### Recommended Execution Order

**Sprint 1 (Foundation) - 6h**:
1. Task 617: Plugin System (3h)
2. Task 618: Hooks System (3h)

**Sprint 2 (Core) - 7h**:
3. Task 619: Subagents (3h) || Task 620: Settings (2h)
4. Task 621: Commands (2h) || Task 622: Checkpointing (3h) - Start after 619/620

**Sprint 3 (Advanced) - 7h**:
5. Task 623: Memory System (3h)
6. Task 624: Orchestrator (4h)

**Sprint 4 (Finalization) - 5h**:
7. Task 625: CLI (2h) || Task 626: Tests (3h)
8. Task 627: Documentation (2h)

**Total Effort**: 25 hours
**Calendar Time** (with parallelization): 3-4 days

---

## 5. Success Metrics

### Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Test Coverage** | ≥90% | pytest-cov |
| **Hook Execution Time** | <500ms | Performance profiling |
| **Memory Sync Time** | <200ms | Database query + file I/O timing |
| **Subagent Invocation Latency** | <1s | End-to-end timing |
| **Plugin Load Time** | <100ms | Startup profiling |
| **Command Response Time** | <2s | CLI benchmarks |

### Quality Metrics

| Metric | Target | Validation Method |
|--------|--------|------------------|
| **Gate Pass Rate** | 100% (all gates implemented) | `apm work-item validate 116` |
| **Documentation Completeness** | All public APIs documented | Doc coverage tool |
| **Agent Compatibility** | All 31 AIPM agents load successfully | Agent validation tests |
| **Hook Reliability** | 99.9% success rate | Error tracking |
| **Memory Consistency** | Zero data loss on sync | Integrity checks |

### User Experience Metrics

| Metric | Target | Success Indicator |
|--------|--------|------------------|
| **Session Start Time** | <3s (context loaded) | User feedback |
| **Context Relevance** | >90% (useful information) | Qualitative assessment |
| **Learnings Persistence** | 100% (all decisions saved) | Database verification |
| **Command Discoverability** | All commands in `/help` | Help text completeness |
| **Error Actionability** | 100% (clear next steps) | Error message review |

---

## 6. Risk Assessment

### High Risks

#### **Risk 1: Delegation Mismatch**
- **Description**: Orchestrators expect programmatic API, Claude uses natural language
- **Impact**: HIGH - Agents may not be invoked as expected
- **Probability**: MEDIUM (well-researched, but requires careful implementation)
- **Mitigation**:
  - Update all delegation language to natural language style (Task 619)
  - Add PROACTIVE keywords to agent descriptions
  - Test invocation patterns with real Claude sessions
  - Fallback: Explicit "Use the X subagent..." instructions

#### **Risk 2: Memory Sync Conflicts**
- **Description**: Database updates during session could conflict with memory files
- **Impact**: MEDIUM - Context could become stale or inconsistent
- **Probability**: LOW (SessionStart loads once, SessionEnd persists once)
- **Mitigation**:
  - Last-write-wins with diff checkpoints (Task 622)
  - Audit trail for all memory updates
  - Conflict detection with warning notifications
  - Manual merge tools for critical conflicts

### Medium Risks

#### **Risk 3: Hook Performance Degradation**
- **Description**: Complex hooks (SessionStart) could slow down Claude startup
- **Impact**: MEDIUM - Poor user experience if >3s delay
- **Probability**: MEDIUM (database queries + file generation)
- **Mitigation**:
  - Optimize database queries (indexes on work_item_id, task_id)
  - Cache frequently-accessed data
  - Lazy load non-critical context
  - Performance budget: SessionStart <500ms

#### **Risk 4: Agent Description Ambiguity**
- **Description**: Claude might not recognize which agent to invoke
- **Impact**: MEDIUM - Requires manual "Use X subagent" prompts
- **Probability**: MEDIUM (natural language is fuzzy)
- **Mitigation**:
  - Clear, specific agent descriptions with examples
  - Keywords: "MUST BE USED", "PROACTIVELY", "Use when"
  - Test agent invocation with various prompts
  - Fallback: Master orchestrator provides explicit routing

### Low Risks

#### **Risk 5: Settings Validation Complexity**
- **Description**: Multi-layer settings (user/project/local) could conflict
- **Impact**: LOW - Configuration errors are debuggable
- **Probability**: LOW (well-established pattern)
- **Mitigation**:
  - Clear precedence: local > project > user
  - Validation at load time with clear error messages
  - `apm claude-settings validate` command
  - Documentation of all settings with examples

#### **Risk 6: Checkpoint Storage Growth**
- **Description**: Checkpoints accumulate, consuming disk space
- **Impact**: LOW - Storage is cheap, can prune old checkpoints
- **Probability**: HIGH (every session creates checkpoint)
- **Mitigation**:
  - Retention policy: Keep last 30 days, archive older
  - `apm checkpoint prune` command
  - Compression for archived checkpoints
  - Warning when storage exceeds threshold

---

## 7. Alignment with AIPM Principles

### Database-First Architecture

**Compliance**:
- ✅ All configuration loaded from database (rules, work items, tasks)
- ✅ Memory files generated from database, not manually edited
- ✅ Hooks persist learnings back to database
- ✅ Checkpoints reference database entities (work_item_id, task_id)

**Code Evidence**:
```python
# SessionStart: Load from database
context = ContextAssemblyService.assemble_work_item_context(work_item_id)

# SessionEnd: Persist to database
db.work_item_methods.update_status(work_item_id, status)
db.summary_methods.create_summary(summary)
```

### Three-Layer Pattern (Models → Adapters → Methods)

**Compliance**:
- ✅ **Models**: Pydantic (HookEvent, MemoryFile, SubagentPlan, Checkpoint, Settings)
- ✅ **Adapters**: Convert database rows to models, models to files
- ✅ **Methods**: Business logic in services (plugin_registry, hooks_engine, etc.)

**Directory Structure**:
```
agentpm/services/claude/
  ├── models.py          (Pydantic models)
  ├── adapters.py        (Database/file conversion)
  ├── plugin_registry.py (Methods)
  ├── hooks_engine.py    (Methods)
  └── integration_service.py (Orchestration methods)
```

### Quality Gate Enforcement

**Compliance**:
- ✅ **I1 Gate**: All tasks have tests (Task 626)
- ✅ **I1 Gate**: Documentation complete (Task 627)
- ✅ **I1 Gate**: Coverage ≥90% (tracked in test suite)
- ✅ **I1 Gate**: No BLOCK-level rule violations

**Validation**:
```bash
apm work-item validate 116 --gate=I1
# Expected: PASS (all deliverables complete)
```

### Agent-First Error Handling

**Compliance**:
- ✅ Error messages include context and next actions
- ✅ Graceful degradation (non-critical failures don't crash)
- ✅ Audit trail for all errors (logged to database)
- ✅ Agent-readable error formats (JSON with structured fields)

**Example**:
```python
# Good: Agent-first error
raise IntegrationError(
    message="SessionStart hook failed to load context",
    context={"work_item_id": 116, "error": str(e)},
    next_actions=[
        "Check database connection",
        "Verify work item 116 exists",
        "Review hook logs: .aipm/logs/hooks.log"
    ]
)
```

---

## 8. Open Questions and Decisions Needed

### Critical Decisions (Block Implementation)

**Q1**: Should we support Agent Skills (404 documentation)?
- **Options**:
  - A) Wait for official documentation
  - B) Reverse-engineer from community examples
  - C) Skip for V1, add later
- **Recommendation**: C (skip for V1) - Feature exists but undocumented, too risky
- **Decision Needed By**: Before Task 617 starts

**Q2**: Memory file generation frequency?
- **Options**:
  - A) Only on SessionStart (once per session)
  - B) On SessionStart + every 10 minutes (keep fresh)
  - C) On SessionStart + on database change events
- **Recommendation**: A (once per session) - Simple, predictable, sufficient for V1
- **Decision Needed By**: Before Task 623 starts

### Important Decisions (Affect UX)

**Q3**: Default subagent parallelism?
- **Options**:
  - A) Sequential only (safer, simpler)
  - B) Parallel up to 3 (moderate)
  - C) Parallel up to 10 (max Claude allows)
- **Recommendation**: B (parallel up to 3) - Balance speed and complexity
- **Decision Needed By**: Before Task 619 starts

**Q4**: Checkpoint retention policy?
- **Options**:
  - A) Keep all checkpoints forever
  - B) Keep last 30 days, delete older
  - C) Keep last 10 per work item, delete older
- **Recommendation**: C (last 10 per work item) - Bounded storage, retains relevant history
- **Decision Needed By**: Before Task 622 starts

### Nice-to-Have Decisions (Can Defer)

**Q5**: Custom MCP server for AIPM database?
- **Impact**: Would enable natural language database queries ("Show work items in review")
- **Effort**: ~8 hours (separate work item)
- **Recommendation**: Defer to WI-117 or later (enhancement, not MVP)

**Q6**: Plugin distribution mechanism?
- **Impact**: How teams share custom plugins
- **Options**: Git repos, plugin marketplace, manual copy
- **Recommendation**: Git repos for V1 (simple, proven)

---

## 9. Integration with Existing Work

### WI-114: Persistent Memory System

**Overlap**: Task 623 (Memory Tool System) implements WI-114 deliverables

**Coordination**:
- WI-114 defines memory file types and schemas
- Task 623 implements sync mechanism (database → files)
- Both share `MemoryScope` enum and `MemoryFile` model

**Risk**: If WI-114 changes memory schema, Task 623 must adapt
**Mitigation**: Task 623 depends on WI-114 completion, consumes stable schema

### WI-119: Claude Integration Consolidation

**Overlap**: WI-116 implements architecture defined in WI-119

**Coordination**:
- WI-119 defines Service Coordinator pattern
- Task 624 (Orchestrator) implements `ClaudeIntegrationService`
- Both share interface contracts and plugin architecture

**Risk**: WI-119 design changes during WI-116 implementation
**Mitigation**: WI-119 design phase complete before WI-116 implementation starts

### WI-107: Agent YAML Alignment

**Overlap**: Task 619 (Subagents) depends on agent definitions from WI-107

**Coordination**:
- WI-107 standardizes agent YAML format
- Task 619 loads agents and routes based on descriptions
- Both share agent metadata schema

**Risk**: Agent format changes mid-implementation
**Mitigation**: WI-107 must reach stable format before Task 619 starts

---

## 10. Validation and Testing Strategy

### Unit Testing (Per Task)

**Scope**: Individual components in isolation

**Framework**: pytest with fixtures

**Coverage Target**: ≥90% per component

**Example** (Task 617 - Plugin System):
```python
def test_plugin_registry_loads_valid_plugin():
    registry = PluginRegistry(db)
    plugin = registry.load_plugin("aipm-core")
    assert plugin.name == "aipm-core"
    assert plugin.version == "1.0.0"
    assert "SessionStart" in plugin.hooks

def test_plugin_registry_rejects_invalid_manifest():
    with pytest.raises(PluginValidationError):
        registry.load_plugin("invalid-plugin")
```

### Integration Testing (Cross-Component)

**Scope**: Multiple components working together

**Focus Areas**:
- SessionStart hook → Memory sync → Context delivery
- SubagentStop hook → Checkpoint creation → Database persist
- CLI command → Integration service → Database update

**Example** (End-to-End Session):
```python
def test_full_session_lifecycle():
    # SessionStart
    session_id = integration_service.initialize(project_context)
    assert session_id is not None

    # Memory loaded
    context_file = Path(".claude/memory/CONTEXT.md")
    assert context_file.exists()

    # Work performed (simulated)
    integration_service.handle_event(UserPromptSubmit(prompt="implement feature"))

    # SessionEnd
    integration_service.handle_event(SessionEnd(session_id=session_id))

    # Checkpoint created
    checkpoints = db.checkpoint_methods.list_checkpoints(session_id=session_id)
    assert len(checkpoints) == 1
```

### Manual Testing (Real Claude Sessions)

**Scope**: Validate with actual Claude Code usage

**Test Cases**:
1. **Context Persistence**: Start session, check context loads automatically
2. **Subagent Invocation**: Request work, verify orchestrator routes correctly
3. **Memory Consistency**: Make changes, restart session, verify updates persist
4. **Command Execution**: Run slash commands, verify results
5. **Hook Reliability**: Trigger all 9 hooks, verify no crashes

**Test Environment**:
- Separate test project (not production AIPM data)
- Sample work items with known states
- Instrumented hooks (log all events for analysis)

### Performance Testing

**Metrics**:
- SessionStart latency (<500ms target)
- Memory sync time (<200ms target)
- Checkpoint creation (<1s target)
- CLI command response (<2s target)

**Tools**:
- Python profiler (cProfile)
- Database query analysis (EXPLAIN)
- File I/O monitoring (time.perf_counter)

**Benchmarks**:
```python
def test_session_start_performance():
    start = time.perf_counter()
    integration_service.handle_event(SessionStart(session_id="test"))
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"SessionStart took {elapsed}s (target: <0.5s)"
```

---

## 11. Documentation Deliverables

### User Documentation

**Location**: `docs/guides/user_guide/claude-code-integration.md`

**Contents**:
1. **Setup Guide**
   - Prerequisites (Claude Code installed, AIPM initialized)
   - Installation steps (`apm claude init`)
   - Configuration (hooks, settings, memory)

2. **Usage Guide**
   - Starting a session (automatic context loading)
   - Working with subagents (natural language delegation)
   - Using slash commands (`/apm-status`, etc.)
   - Ending a session (automatic persistence)

3. **Examples**
   - Complete workflow: D1 → P1 → I1 → R1
   - Multi-session work (context carries over)
   - Handoff between agents (Claude → human review)

### Developer Documentation

**Location**: `docs/guides/developer_guide/claude-code-extension.md`

**Contents**:
1. **Architecture Overview**
   - Plugin system structure
   - Hook event flow
   - Subagent orchestration pattern

2. **Extension Points**
   - Custom hooks (add new event handlers)
   - Custom plugins (bundle capabilities)
   - Custom slash commands (add CLI functionality)

3. **API Reference**
   - `ClaudeIntegrationService` methods
   - Hook event schemas
   - Memory file formats

### Troubleshooting Guide

**Location**: `docs/operations/troubleshooting/claude-code-issues.md`

**Contents**:
1. **Common Issues**
   - "Context not loading" → Check SessionStart hook logs
   - "Subagent not invoked" → Verify agent description clarity
   - "Memory out of sync" → Run `apm memory sync --force`

2. **Diagnostic Commands**
   - `apm claude status` - Overall health check
   - `apm claude hooks test` - Validate hook execution
   - `apm claude agents validate` - Check agent definitions

3. **Debug Mode**
   - Enable verbose logging
   - Capture hook outputs
   - Analyze session transcripts

---

## 12. Next Steps and Recommendations

### Immediate Actions (Before Implementation Starts)

1. **Resolve Critical Decisions** (Q1, Q2 from Section 8)
   - Agent Skills support: Skip for V1
   - Memory generation frequency: SessionStart only
   - **Owner**: Implementation Orchestrator
   - **Deadline**: Before Task 617 starts

2. **Validate Dependencies**
   - Confirm WI-114 (Persistent Memory) schema stable
   - Confirm WI-119 (Integration Consolidation) design complete
   - Confirm WI-107 (Agent Alignment) format stable
   - **Owner**: Planning Orchestrator
   - **Deadline**: Before sprint kickoff

3. **Prepare Test Environment**
   - Create test project with sample data
   - Set up isolated database (not production)
   - Install Claude Code in test environment
   - **Owner**: Testing Specialist
   - **Deadline**: Before Task 626 starts

### Implementation Kickoff

1. **Task Assignment**
   - Assign tasks to developers (or single developer for full stack)
   - Establish communication channel (Slack, Discord)
   - Schedule daily standups (15 minutes)

2. **Sprint Planning**
   - Sprint 1 (Foundation): Tasks 617-618
   - Sprint 2 (Core): Tasks 619-622
   - Sprint 3 (Advanced): Tasks 623-624
   - Sprint 4 (Finalization): Tasks 625-627

3. **Quality Gates**
   - Each task must pass unit tests before PR merge
   - Each sprint must pass integration tests before next sprint
   - Final sprint must pass I1 gate before WI-116 completion

### Post-Implementation

1. **Validation with Real Usage**
   - Dogfooding: Product owner uses for 1 week
   - Beta testing: 3-5 developers test with their projects
   - Feedback collection: What works, what doesn't

2. **Iteration Based on Feedback**
   - Performance tuning (if hooks too slow)
   - UX improvements (if commands unclear)
   - Bug fixes (issues found in production use)

3. **Future Enhancements** (Defer to Later WIs)
   - Agent Skills support (when docs available)
   - MCP server for AIPM database (WI-117?)
   - Plugin marketplace (WI-118?)
   - Multi-device sync (WI-119?)

---

## 13. Conclusion

This integration plan provides a clear, phased roadmap for achieving comprehensive Claude Code integration in APM (Agent Project Manager). The plan is grounded in extensive research, aligns with AIPM's database-first architecture, and sequences tasks to minimize risk while maximizing value delivery.

**Key Takeaways**:

1. **Well-Researched Foundation**: Comprehensive analysis of Claude Code capabilities ensures we build on solid understanding
2. **Phased Approach**: 4 phases (Foundation → Core → Advanced → Finalization) allow for validation at each stage
3. **Clear Dependencies**: Task sequencing prevents blockers and enables parallel work where possible
4. **Quality Focus**: 90%+ test coverage, comprehensive documentation, and I1 gate compliance
5. **Risk Mitigation**: Identified risks with clear mitigation strategies
6. **AIPM Alignment**: Database-first, three-layer pattern, agent-first errors

**Success Criteria Met**:

- ✅ Comprehensive feature analysis complete
- ✅ Integration plan documented (this file)
- ✅ Task sequencing defined (Section 4)
- ✅ Dependencies mapped (Section 4.2)
- ✅ Risks identified with mitigations (Section 6)

**Ready for Implementation**: Yes, pending resolution of critical decisions (Q1, Q2)

---

## Appendix A: Reference Documents

### Analysis Documents
- [Claude Code Integration Comprehensive Analysis](../../analysis/agents/claude-code/claude-code-integration-comprehensive-analysis.md) - 18,000 words, complete feature analysis
- [Claude Plan](../../analysis/agents/claude-code/claude-plan.md) - Strategic planning session, Micro-MVP recommendation
- [Cursor Provider Architecture](../design/cursor-provider-architecture.md) - Existing provider integration patterns

### Architecture Documents
- [Claude Integration Consolidation Design](../../architecture/design/claude-integration-consolidation-design.md) - WI-119 architecture
- [Three-Tier Orchestration](../../components/agents/architecture/three-tier-orchestration.md) - AIPM agent architecture

### Database Schema
- [Database Service](../../../agentpm/core/database/service.py) - Gold standard service pattern
- [Workflow Validators](../../../agentpm/core/workflow/validators.py) - Quality gate enforcement

### Existing Implementations
- Hooks: `.claude/hooks/*.py` (8 hook scripts, partially implemented)
- Agents: `.claude/agents/` (31 agents, format needs alignment)
- Settings: `.claude/settings.local.json` (hook registration)

---

## Appendix B: Task Checklist

**Phase 1: Foundation**
- [ ] Task 617: Create Claude Code Plugin System (3h)
- [ ] Task 618: Create Claude Code Hooks System (3h)

**Phase 2: Core Features**
- [ ] Task 619: Create Claude Code Subagents System (3h)
- [ ] Task 620: Create Claude Code Settings System (2h)
- [ ] Task 621: Create Claude Code Slash Commands (2h)
- [ ] Task 622: Create Claude Code Checkpointing System (3h)

**Phase 3: Advanced Features**
- [ ] Task 623: Create Claude Code Memory Tool System (3h)
- [ ] Task 624: Create Claude Code Orchestrator (4h)

**Phase 4: Finalization**
- [ ] Task 625: Create CLI Commands for Claude Code Integration (2h)
- [ ] Task 626: Create Comprehensive Test Suite (3h)
- [ ] Task 627: Create Comprehensive Documentation (2h)

**Total**: 11 tasks, 25 hours estimated effort

---

**Document Status**: Complete, ready for implementation
**Last Updated**: 2025-10-21
**Next Review**: After Task 617 completion (validate assumptions)
**Maintained By**: Implementation Orchestrator
