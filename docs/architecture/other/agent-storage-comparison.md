# Agent Storage Architecture - Current vs. Proposed

**Version**: 1.0.0
**Date**: 2025-10-17

---

## Visual Comparison

### Current Architecture (Provider-Locked)

```
┌─────────────────────────────────────────────────────────────┐
│                    .claude/agents/                          │
│              (Claude Code-Specific Location)                │
│                                                             │
│  ├─ orchestrators/                                         │
│  │  ├─ definition-orch.md        ← Manual files           │
│  │  ├─ planning-orch.md          ← Provider-specific      │
│  │  └─ implementation-orch.md    ← Hard to migrate        │
│  │                                                          │
│  ├─ sub-agents/                                            │
│  │  ├─ intent-triage.md          ← No abstraction         │
│  │  └─ ac-writer.md              ← Tied to Claude Code    │
│  │                                                          │
│  └─ utilities/                                             │
│     └─ workitem-writer.md                                  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ Manual creation
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Database (agents table)                  │
│                                                             │
│  id │ role              │ tier │ sop_content              │
│  ───┼───────────────────┼──────┼──────────────────────────│
│  64 │ definition-orch   │  2   │ "You are the..."         │
│  65 │ planning-orch     │  2   │ "You are the..."         │
│  33 │ intent-triage     │  1   │ "You are the..."         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ Manual SQL inserts
                              │
┌─────────────────────────────────────────────────────────────┐
│              scripts/define_mini_orchestrators.py           │
│                  (Inline definitions in Python)             │
│                                                             │
│  orchestrators = {                                          │
│    "definition-orch": {                                     │
│      "display_name": "Definition Orchestrator",            │
│      "sop": "You are the..."  # Inline markdown           │
│    }                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘

❌ PROBLEMS:
  - Provider lock-in (.claude/ specific)
  - No template abstraction
  - Manual file creation
  - Python scripts contain definitions (not versionable)
  - Hard to support multiple LLM providers
  - No validation
```

---

### Proposed Architecture (Provider-Agnostic)

```
┌─────────────────────────────────────────────────────────────┐
│             YAML DEFINITIONS (Single Source of Truth)       │
│          agentpm/core/agents/definitions/                   │
│                                                             │
│  orchestrators.yaml     │  sub-agents.yaml  │ specialists.yaml│
│  ───────────────────────────────────────────────────────────│
│  orchestrators:         │  sub_agents:      │  specialists:  │
│    definition-orch:     │    intent-triage: │    implementer:│
│      tier: 2            │      tier: 1      │      tier: 2   │
│      phase: definition  │      desc: "..."  │      role: "..." │
│      sop_sections:      │      tools: [...]  │      ...       │
│        role: "..."      │      ...          │                │
│        delegates_to:    │                   │                │
│          - intent-triage│                   │                │
│        tools: [...]     │                   │                │
│        ...              │                   │                │
│                                                             │
│  ✅ Human-readable      ✅ Version controlled               │
│  ✅ Declarative         ✅ JSON Schema validated            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ AgentBuilder API
                              │ (sync_all())
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE (agents table)                    │
│                   (Runtime State Tracking)                  │
│                                                             │
│  id │ role            │ tier │ is_active │ last_used_at    │
│  ───┼─────────────────┼──────┼───────────┼─────────────────│
│  64 │ definition-orch │  2   │ true      │ 2025-10-17     │
│  65 │ planning-orch   │  2   │ true      │ 2025-10-16     │
│  33 │ intent-triage   │  1   │ true      │ 2025-10-17     │
│                                                             │
│  ✅ Runtime state       ✅ Usage tracking                   │
│  ✅ Relationships       ✅ Metadata (JSON)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Provider detection
                              │ (auto or manual)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PROVIDER GENERATORS (Plugins)                  │
│        agentpm/core/plugins/domains/llms/                   │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐ │
│  │ Claude Code      │  │ Google Gemini    │  │ Cursor   │ │
│  │ ──────────────── │  │ ──────────────── │  │ ──────── │ │
│  │ generator.py     │  │ generator.py     │  │ (future) │ │
│  │ templates/       │  │ templates/       │  │          │ │
│  │   orch.md.j2     │  │   agent.xml.j2   │  │          │ │
│  │   sub.md.j2      │  │   ...            │  │          │ │
│  └──────────────────┘  └──────────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                       │                    │
         │ generate()            │ generate()         │ generate()
         ▼                       ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐
│ .claude/agents/  │  │ .gemini/agents/  │  │ .cursor/agents/│
│ ──────────────── │  │ ──────────────── │  │ ────────────── │
│ orchestrators/   │  │ definition-orch  │  │ (future)       │
│   def-orch.md    │  │   .xml           │  │                │
│ sub-agents/      │  │ planning-orch    │  │                │
│   intent.md      │  │   .xml           │  │                │
│                  │  │                  │  │                │
│ ✅ Markdown      │  │ ✅ XML format    │  │ ✅ Provider    │
│ ✅ Auto-gen      │  │ ✅ Auto-gen      │  │    specific    │
│ ✅ Regenerable   │  │ ✅ Regenerable   │  │                │
└──────────────────┘  └──────────────────┘  └────────────────┘

✅ BENEFITS:
  - Provider-agnostic core
  - Template abstraction (Jinja2)
  - Automatic generation
  - YAML = single source (version controlled)
  - Easy to add new providers
  - JSON Schema validation
  - Staleness detection
```

---

## Side-by-Side Comparison

| Aspect | Current (Provider-Locked) | Proposed (Provider-Agnostic) |
|--------|---------------------------|------------------------------|
| **Definition Storage** | Python scripts (inline) | YAML files (version controlled) |
| **Provider Support** | Claude Code only | Multiple (Claude, Gemini, Cursor, ...) |
| **Template System** | None (manual files) | Jinja2 (flexible, provider-specific) |
| **Database Role** | Storage only | Runtime state tracking |
| **File Generation** | Manual creation | Automatic (on-demand + staleness) |
| **Validation** | None | JSON Schema + CLI validation |
| **Extensibility** | Hard (modify Python) | Easy (add YAML + plugin) |
| **Migration** | N/A | Smooth (export → YAML → import) |
| **Versioning** | None | Semantic versioning in YAML |
| **Human-Readable** | No (Python code) | Yes (YAML) |
| **LLM-Friendly** | No | Yes (documentation-like) |

---

## Feature Comparison

### Current Limitations

```
❌ Provider Lock-In
   └─ Can only use Claude Code
   └─ Switching LLMs requires complete rewrite

❌ No Template Abstraction
   └─ Each agent file manually created
   └─ No reusable patterns

❌ Hard to Maintain
   └─ Definitions scattered in Python scripts
   └─ No central source of truth

❌ No Validation
   └─ Typos and errors discovered at runtime
   └─ No pre-deployment checks

❌ Manual Synchronization
   └─ Database → Files must be synced manually
   └─ Easy to get out of sync

❌ Poor Documentation
   └─ Definitions buried in code
   └─ Hard for non-developers to understand
```

### Proposed Capabilities

```
✅ Provider-Agnostic
   ├─ Support Claude Code (Markdown)
   ├─ Support Google Gemini (XML)
   ├─ Support Cursor (future)
   └─ Easy to add new providers

✅ Template System
   ├─ Jinja2 templates (flexible)
   ├─ Provider-specific customization
   └─ Shared core structure

✅ Easy to Maintain
   ├─ YAML = single source of truth
   ├─ Version controlled definitions
   └─ Clear structure

✅ Validation
   ├─ JSON Schema validation
   ├─ CLI validation commands
   └─ Pre-deployment checks

✅ Automatic Sync
   ├─ YAML → Database → Files
   ├─ One command workflow
   └─ Staleness detection

✅ Excellent Documentation
   ├─ Self-documenting YAML
   ├─ Human-readable format
   └─ LLM-friendly structure
```

---

## Workflow Comparison

### Current Workflow (Manual)

```
1. Define Agent in Python
   └─ Edit scripts/define_mini_orchestrators.py
   └─ Add orchestrator definition (inline markdown)

2. Run Script to Create Database Entry
   └─ python scripts/define_mini_orchestrators.py
   └─ Creates database record

3. Manually Create Agent File
   └─ vim .claude/agents/orchestrators/definition-orch.md
   └─ Copy-paste SOP from Python script
   └─ Format as markdown

4. Update Database with File Path
   └─ UPDATE agents SET file_path = '.claude/...' WHERE role = '...';

5. Verify Synchronization
   └─ Check database matches file
   └─ Manual comparison

⏱️ Time: ~30 minutes per agent
🔴 Error-Prone: Manual steps, copy-paste errors
🔴 Provider-Locked: Only works for Claude Code
```

### Proposed Workflow (Automated)

```
1. Define Agent in YAML
   └─ Edit agentpm/core/agents/definitions/orchestrators.yaml
   └─ Add orchestrator definition (declarative)

2. Validate YAML
   └─ apm agents validate
   └─ JSON Schema checks structure

3. Sync to Database & Generate Files
   └─ apm agents sync
   └─ YAML → Database → Provider files (all automatic)

4. Verify Output
   └─ ls .claude/agents/orchestrators/
   └─ Agent file generated automatically

⏱️ Time: ~5 minutes per agent
🟢 Reliable: Automated, validated
🟢 Provider-Agnostic: Works for all supported LLMs
```

**Time Savings**: 80% reduction (30 min → 5 min)

---

## Migration Path Visualization

### Current State → Transition → Future State

```
CURRENT STATE (Provider-Locked)
┌────────────────────────────────────┐
│  Python Scripts                    │
│  └─ Inline definitions             │
│                                    │
│  Database                          │
│  └─ Agent records                  │
│                                    │
│  .claude/agents/                   │
│  └─ Manual files                   │
└────────────────────────────────────┘

            │
            │ PHASE 1: Export & Define (Week 1)
            │ python scripts/migrate_agents_to_yaml.py
            ▼

TRANSITION STATE (Dual System)
┌────────────────────────────────────┐
│  YAML Definitions     ✅ NEW       │
│  └─ Exported from database         │
│                                    │
│  Database             ✅ Same      │
│  └─ Unchanged                      │
│                                    │
│  .claude/agents/      ⚠️ Both      │
│  ├─ Manual files (old)             │
│  └─ Generated files (new)          │
│                                    │
│  Provider Plugins     ✅ NEW       │
│  └─ Claude Code generator          │
└────────────────────────────────────┘

            │
            │ PHASE 2: Validate & Test (Weeks 2-3)
            │ Compare old vs new, fix discrepancies
            ▼

FUTURE STATE (Provider-Agnostic)
┌────────────────────────────────────┐
│  YAML Definitions     ✅ Source    │
│  └─ Single source of truth         │
│                                    │
│  Database             ✅ Runtime   │
│  └─ State tracking only            │
│                                    │
│  .claude/agents/      ✅ Generated │
│  .gemini/agents/      ✅ Generated │
│  .cursor/agents/      ✅ Future    │
│  └─ All auto-generated             │
│                                    │
│  Provider Plugins     ✅ Multi     │
│  └─ Support all LLMs               │
└────────────────────────────────────┘
```

---

## Impact Analysis

### Code Changes Required

| Component | Changes | Effort | Risk |
|-----------|---------|--------|------|
| **New Components** | | | |
| YAML definitions | Create 3 files | 1 day | Low |
| Provider plugins | Create plugin structure | 2 days | Low |
| Jinja2 templates | Create templates | 1 day | Low |
| Sync service | Create synchronizer | 2 days | Medium |
| CLI commands | Add agent commands | 1 day | Low |
| **Existing Components** | | | |
| Database schema | NO CHANGE | 0 days | None |
| Agent model | NO CHANGE | 0 days | None |
| AgentBuilder API | Minor additions | 0.5 days | Low |
| **Testing** | | | |
| Unit tests | New test suite | 2 days | Low |
| Integration tests | End-to-end tests | 1 day | Medium |
| **Documentation** | | | |
| Architecture docs | Update docs | 1 day | Low |
| User guide | Create guide | 1 day | Low |
| **TOTAL** | | **12 days** | **Low-Medium** |

### Backward Compatibility

```
✅ Database Schema: NO CHANGES (100% compatible)
✅ Existing Agents: Continue to work during migration
✅ AgentBuilder API: Additive only (no breaking changes)
✅ CLI Commands: New commands (existing unchanged)
⚠️ Manual Files: Deprecated but supported during transition
```

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Generated files differ from manual** | Compare using diff, validate before switching |
| **YAML schema errors** | JSON Schema validation + CLI validation |
| **Database sync fails** | Dry-run mode, rollback support |
| **Provider detection fails** | Manual provider specification |
| **Template errors** | Comprehensive test suite |
| **Migration data loss** | Export → validate → import workflow |

---

## Success Metrics

### Quantitative

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Agent creation time** | 30 min | 5 min | 83% faster |
| **Provider support** | 1 (Claude) | 3+ (Claude, Gemini, Cursor) | 300% increase |
| **Validation coverage** | 0% | 100% | N/A |
| **Definition readability** | Python code | YAML | Human-friendly |
| **Sync automation** | Manual | Automatic | 100% automated |
| **Migration time** | N/A | 12 days | Smooth transition |

### Qualitative

```
✅ Developer Experience
   └─ Easy to add/modify agents
   └─ Clear structure and documentation
   └─ Fast feedback loop

✅ System Flexibility
   └─ Support any LLM provider
   └─ Easy to extend
   └─ Future-proof architecture

✅ Operational Excellence
   └─ Automated validation
   └─ Staleness detection
   └─ Regeneration on-demand

✅ Code Quality
   └─ Version controlled definitions
   └─ Clear separation of concerns
   └─ Testable components
```

---

## Decision Summary

### Core Decisions

1. **YAML for Definitions** (over Python dataclasses)
   - Rationale: Human-readable, version control friendly
   - Trade-off: Runtime parsing cost (minimal)

2. **Jinja2 for Templates** (over programmatic generation)
   - Rationale: Flexible, provider-specific customization
   - Trade-off: Learning curve (minimal for Jinja2)

3. **Hybrid Source of Truth** (YAML + Database)
   - Rationale: YAML = definitions, Database = runtime state
   - Trade-off: Two-step sync (acceptable)

4. **Plugin Architecture** (LLM providers as plugins)
   - Rationale: Consistent with existing plugin system
   - Trade-off: More structure (worth it for extensibility)

### Key Principles

```
1. Provider-Agnostic Core
   └─ No LLM-specific logic in core system

2. Declarative Definitions
   └─ YAML describes "what", not "how"

3. Automatic Generation
   └─ Minimize manual steps

4. Validation First
   └─ Catch errors before deployment

5. Backward Compatible
   └─ No breaking changes to existing system
```

---

## Next Steps

### Immediate Actions

1. **Review & Approve** (1 day)
   - Architecture review
   - Stakeholder approval
   - Finalize design

2. **Phase 1 Implementation** (1 week)
   - Create YAML definitions
   - Implement Claude Code generator
   - Export existing agents to YAML

3. **Phase 2 Implementation** (1 week)
   - Add Gemini support
   - Implement auto-detection
   - Create CLI commands

4. **Phase 3 Validation** (1 week)
   - Comprehensive testing
   - Documentation
   - Migration guide

### Long-Term Roadmap

- **Q1 2026**: Support for Cursor LLM
- **Q2 2026**: Support for OpenAI Codex
- **Q3 2026**: Custom provider plugin API
- **Q4 2026**: Agent marketplace (share YAML definitions)

---

## References

**Main Documents**:
- [Complete Architecture Design](agent-storage-architecture.md)
- [Quick Reference Guide](agent-storage-quick-ref.md)

**Related Systems**:
- [Agent Builder API](../components/agents/agent-builder-api.md)
- [Plugin Development Guide](../components/plugins/developer-guide.md)
- [Database Schema](../components/database/README.md)

---

**Last Updated**: 2025-10-17
**Version**: 1.0.0
**Status**: DESIGN COMPLETE - READY FOR IMPLEMENTATION
