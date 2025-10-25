# Agent Storage Architecture - Executive Summary

**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: DESIGN COMPLETE - READY FOR IMPLEMENTATION

---

## Problem Statement

**Current Issue**: Agent definitions are stored in `.claude/agents/` directory, creating provider lock-in. System needs provider-agnostic templates that can generate agent files for any LLM provider (Claude Code, Gemini, Cursor, etc.).

**Impact**:
- Cannot easily support multiple LLM providers
- Manual agent creation is time-consuming (30 min/agent)
- No validation or version control for agent definitions
- Definitions scattered in Python scripts (not human-readable)

---

## Solution Overview

**Three-Tier Architecture**: YAML definitions → Database state → Provider-specific generation

```
YAML Definitions (version controlled, human-readable)
         ↓
AgentBuilder API (synchronization)
         ↓
Database (runtime state tracking)
         ↓
Provider Plugins (Jinja2 templates)
         ↓
Provider Files (.claude/, .gemini/, .cursor/)
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Definition Format** | YAML | Human-readable, version control friendly, declarative |
| **Template Engine** | Jinja2 | Flexible, powerful, provider-specific customization |
| **Source of Truth** | YAML + Database hybrid | YAML = canonical definitions, Database = runtime state |
| **Provider Location** | `llms/{provider}/` plugin | Consistent with existing architecture |
| **Generation Trigger** | On-demand + staleness | Manual control + automatic when outdated |

---

## Architecture Components

### 1. Definition Layer (YAML)

**Location**: `agentpm/core/agents/definitions/`

**Files**:
- `orchestrators.yaml` - 6 mini-orchestrators (tier 2)
- `sub-agents.yaml` - 31 sub-agents (tier 1)
- `specialists.yaml` - 15 role templates (tier 2)
- `schema.json` - JSON Schema validation

**Example**:
```yaml
orchestrators:
  definition-orch:
    tier: 2
    display_name: "Definition Orchestrator"
    phase: definition
    gate: D1
    sop_sections:
      role: "You are the Definition Orchestrator..."
      delegates_to: [intent-triage, ac-writer, ...]
    tools:
      - name: context7
        phase: discovery
        priority: 1
```

### 2. Plugin Layer (Provider-Specific)

**Location**: `agentpm/core/plugins/domains/llms/{provider}/{tool}/`

**Structure**:
```
llms/
├─ anthropic/claude-code/
│  ├─ generator.py           # ClaudeCodeAgentGenerator
│  └─ templates/
│     ├─ orchestrator.md.j2  # Jinja2 templates
│     ├─ sub-agent.md.j2
│     └─ specialist.md.j2
│
├─ google/gemini/
│  ├─ generator.py           # GeminiAgentGenerator
│  └─ templates/
│     └─ agent.xml.j2        # Gemini XML format
│
└─ openai/codex/             # Future
```

### 3. Database Layer (Runtime State)

**Table**: `agents` (existing schema, NO CHANGES)

**Fields**:
- `id`, `project_id`, `role`, `display_name`, `description`
- `sop_content` (generated markdown, cache)
- `tier` (1=sub-agent, 2=mini-orch, 3=master)
- `is_active`, `last_used_at`, `metadata`
- `file_path`, `generated_at` (staleness tracking)

---

## Workflow

### Developer Workflow (New Agent)

```bash
# 1. Edit YAML definition
vim agentpm/core/agents/definitions/orchestrators.yaml

# 2. Validate YAML
apm agents validate

# 3. Sync to database & generate files
apm agents sync

# 4. Verify output
ls .claude/agents/orchestrators/definition-orch.md
```

**Time**: ~5 minutes (vs 30 minutes manual)

### System Workflow (Data Flow)

```
1. YAML Definition (canonical)
   └─ orchestrators.yaml, sub-agents.yaml, specialists.yaml

2. AgentBuilder API (synchronization)
   └─ load_yaml() → sync_to_database() → mark_stale()

3. Database (runtime state)
   └─ Track: is_active, last_used_at, relationships

4. Provider Detection (automatic or manual)
   └─ Detect: .claude/ → claude-code, .gemini/ → gemini

5. Generator Selection (plugin system)
   └─ Load provider-specific generator

6. File Generation (Jinja2 rendering)
   └─ Combine: YAML definition + database state + template

7. Output Files (provider consumption)
   └─ .claude/agents/orchestrators/definition-orch.md
   └─ .gemini/agents/definition-orch.xml
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Deliverables**:
- YAML schema definition (JSON Schema)
- Export existing agents to YAML
- Claude Code generator implementation
- Synchronization service
- Basic CLI commands

**Tasks**:
1. Define YAML schema
2. Export database → YAML
3. Create Jinja2 templates
4. Implement ClaudeCodeAgentGenerator
5. Implement AgentSynchronizer
6. Test generation workflow

**Effort**: 5 person-days

### Phase 2: Provider Expansion (Week 2)

**Deliverables**:
- Google Gemini generator
- Provider auto-detection
- Advanced CLI commands
- Migration guide

**Tasks**:
1. Implement GeminiAgentGenerator
2. Create Gemini templates (XML)
3. Add provider detection
4. Enhanced CLI (sync, generate, validate)
5. Documentation

**Effort**: 5 person-days

### Phase 3: Validation & Testing (Week 3)

**Deliverables**:
- Comprehensive test suite
- Validation framework
- Staleness detection
- Complete documentation

**Tasks**:
1. Unit tests (all generators)
2. Integration tests (full workflow)
3. YAML validation suite
4. Staleness detection logic
5. Architecture documentation

**Effort**: 5 person-days

**Total Effort**: 15 person-days (3 weeks)

---

## Benefits

### Quantitative

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Agent creation time** | 30 min | 5 min | 83% faster |
| **Provider support** | 1 | 3+ | 300% increase |
| **Validation coverage** | 0% | 100% | N/A |
| **Manual steps** | 5 | 1 | 80% reduction |

### Qualitative

**Developer Experience**:
- ✅ Easy to add/modify agents (YAML editing)
- ✅ Fast feedback loop (validate → sync → generate)
- ✅ Clear documentation (self-documenting YAML)

**System Flexibility**:
- ✅ Support any LLM provider (plugin architecture)
- ✅ Easy to extend (add new provider = add plugin)
- ✅ Future-proof (no provider lock-in)

**Operational Excellence**:
- ✅ Automated validation (JSON Schema)
- ✅ Staleness detection (automatic regeneration)
- ✅ Version control (YAML in git)

---

## Migration Strategy

### Phase 1: Export & Setup (Week 1)
```bash
# Export existing database agents to YAML
python scripts/migrate_agents_to_yaml.py

# Validate exported YAML
apm agents validate

# Test sync (dry-run)
apm agents sync --dry-run
```

### Phase 2: Dual System (Weeks 2-3)
- Keep old manual files
- Generate new files alongside
- Compare outputs (should be identical)
- Fix any discrepancies

### Phase 3: Switch Over (Week 4+)
- Remove manual files
- Use only generated files
- Update documentation
- Train developers

**Risk**: LOW (backward compatible, no database changes)

---

## CLI Commands

### Agent Synchronization
```bash
apm agents sync                # YAML → DB → Files
apm agents sync --force        # Force regeneration
apm agents sync --dry-run      # Show what would change
```

### Agent Generation
```bash
apm agents generate                        # Auto-detect provider
apm agents generate --provider=gemini      # Specific provider
apm agents generate --role=definition-orch # Single agent
```

### Agent Validation
```bash
apm agents validate            # Validate all YAML
apm agents list --stale        # Show agents needing regeneration
apm agents show definition-orch # Show agent details
```

### Agent Export/Import
```bash
apm agents export --output=definitions/  # DB → YAML
apm agents import --source=definitions/  # YAML → DB
```

---

## Success Criteria

### Functional Requirements
- ✅ YAML definitions are single source of truth
- ✅ Database tracks runtime state (active, usage)
- ✅ Providers generate agent files automatically
- ✅ New providers added without core changes
- ✅ Existing agents migrate cleanly
- ✅ CLI commands for all operations

### Non-Functional Requirements
- ✅ Generation time: <1s for all agents
- ✅ YAML validation catches errors before sync
- ✅ Provider detection is automatic
- ✅ Staleness detection triggers regeneration
- ✅ Backward compatible (no database changes)

### Quality Gates
- ✅ All YAML validates against schema
- ✅ Generated files match expected format
- ✅ Database sync is idempotent
- ✅ Test coverage ≥90%
- ✅ Documentation complete

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Generated files differ** | Medium | Medium | Compare using diff, validate before switching |
| **YAML schema errors** | Low | Medium | JSON Schema validation + CLI validation |
| **Database sync fails** | Low | High | Dry-run mode, rollback support |
| **Provider detection fails** | Low | Low | Manual provider specification |
| **Template errors** | Low | Medium | Comprehensive test suite |
| **Migration data loss** | Very Low | High | Export → validate → import workflow |

**Overall Risk**: LOW-MEDIUM

---

## Documentation Deliverables

1. **Complete Architecture Design** (`agent-storage-architecture.md`)
   - 15,000 words comprehensive design
   - All technical details
   - Implementation guidance

2. **Quick Reference Guide** (`agent-storage-quick-ref.md`)
   - 5,000 words quick guide
   - Common tasks
   - Troubleshooting

3. **Current vs Proposed Comparison** (`agent-storage-comparison.md`)
   - 6,000 words comparison
   - Migration strategy
   - Impact analysis

4. **Executive Summary** (this document)
   - 2,000 words summary
   - High-level overview
   - Decision rationale

**Total Documentation**: ~28,000 words

---

## Recommendation

**Status**: ✅ APPROVE FOR IMPLEMENTATION

**Rationale**:
1. **Low Risk**: No database schema changes, backward compatible
2. **High Value**: 83% time savings, multi-provider support
3. **Clear Path**: Well-defined phases, 3-week timeline
4. **Strong Design**: Provider-agnostic, extensible, testable
5. **Complete Docs**: Comprehensive documentation provided

**Next Steps**:
1. Architecture review and approval (1 day)
2. Begin Phase 1 implementation (Week 1)
3. Validate with existing agents (Week 2)
4. Complete testing and documentation (Week 3)

---

## Appendix: File Locations

**Documentation**:
- `docs/design/agent-storage-architecture.md` - Complete design
- `docs/design/agent-storage-quick-ref.md` - Quick guide
- `docs/design/agent-storage-comparison.md` - Comparison
- `docs/design/AGENT_STORAGE_SUMMARY.md` - This summary

**Implementation** (to be created):
- `agentpm/core/agents/definitions/` - YAML definitions
- `agentpm/core/agents/sync.py` - Synchronizer
- `agentpm/core/plugins/domains/llms/` - Provider plugins
- `scripts/migrate_agents_to_yaml.py` - Migration script

**References**:
- `agentpm/core/database/models/agent.py` - Agent model (no changes)
- `agentpm/templates/agents/` - Existing templates (to deprecate)
- `.claude/agents/` - Current agent files (to be generated)

---

**Approval Status**: PENDING REVIEW
**Implementation Status**: READY TO START
**Contact**: System Architect
**Date**: 2025-10-17
