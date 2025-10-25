# Sub-Agents Complete Analysis

**Date**: 2025-10-17
**Objective**: Complete understanding of what "sub-agents" means in AIPM context
**Status**: COMPREHENSIVE

---

## Executive Summary

**Sub-agents in APM (Agent Project Manager) exist in TWO DISTINCT contexts:**

1. **Tier 1 Sub-Agents (Phase Execution)** - Database-defined, single-responsibility agents that execute specific tasks within phase workflows
2. **Context Compression Pattern (ADR-002)** - Proposed delegation pattern for compressing large context (200K → 20K tokens)

**Critical Discovery**: These are **DIFFERENT concepts** with the same name.

---

## 1. Tier 1 Sub-Agents (Implemented)

### What They Are

**Definition**: Single-responsibility agents that execute atomic tasks within mini-orchestrator workflows.

**Architecture**: Three-Tier Orchestration
```
Master Orchestrator (CLAUDE.md)
├─ Mini-Orchestrators (6 phase orchestrators)
│  ├─ Definition-Orch
│  ├─ Planning-Orch
│  ├─ Implementation-Orch
│  ├─ Review-Test-Orch
│  ├─ Release-Ops-Orch
│  └─ Evolution-Orch
│
└─ Sub-Agents (~25 single-responsibility agents)
   ├─ intent-triage
   ├─ context-assembler
   ├─ ac-writer
   ├─ code-implementer
   ├─ test-runner
   └─ ... (full list in scripts/define_sub_agents.py)
```

### Implementation Status

**✅ Fully Defined**: All 25+ sub-agents defined in `scripts/define_sub_agents.py`

**Database Schema**:
```sql
-- agents table
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    role TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    tier INTEGER NOT NULL,  -- 1 = Sub-Agent, 2 = Mini-Orch, 3 = Master
    orchestrator_type TEXT,  -- NULL for sub-agents
    execution_mode TEXT,  -- 'sequential' for focused execution
    symbol_mode BOOLEAN,  -- TRUE for token efficiency
    sop TEXT NOT NULL,  -- Standard Operating Procedure
    is_active BOOLEAN DEFAULT 1
);
```

**Example Sub-Agent** (context-assembler):
```yaml
role: context-assembler
display_name: Context Assembly Agent
tier: 1
reports_to: definition-orch
sop: |
  1. Receive context requirements from triage
  2. Query database for related work items/tasks
  3. Search filesystem for relevant artifacts
  4. Fetch external documentation if needed
  5. Calculate context confidence score
  6. Package context bundle with evidence
tools:
  - context7 (for documentation lookup)
```

### Location in Codebase

**Agent Definitions**:
- Database: `agents` table (source of truth)
- Script: `scripts/define_sub_agents.py` (creation script)
- Generated Files: `.claude/agents/sub-agents/*.md` (execution artifacts)

**Generated Example**: `.claude/agents/sub-agents/context-assembler.md`
```markdown
---
name: context-assembler
description: Gather relevant project context from database and codebase
tools: Read, Grep, Glob, Write, Edit, Bash
---

You are the **Context Assembler** sub-agent.

## Responsibilities
Collect and assemble:
- Relevant code files and patterns
- Similar past implementations
- Related work items
- Applicable rules and standards
```

### How They Work

**Delegation Pattern**:
```
1. Master Orchestrator receives request.raw
2. Routes to Definition-Orch (mini-orchestrator)
3. Definition-Orch delegates to sub-agents:
   - intent-triage: Classify request
   - context-assembler: Gather context
   - problem-framer: Frame problem
   - ac-writer: Write acceptance criteria
   - definition-gate-check: Evaluate gate
4. Returns workitem.ready artifact
```

**Agent Execution**:
```bash
# CLI generates agent markdown on-demand
apm agents generate --role context-assembler --llm claude

# Output: .claude/agents/sub-agents/context-assembler.md
# LLM loads this file when agent is activated via Task tool
```

### Problem They Solve

**Before Three-Tier Architecture**:
- Monolithic orchestrator (CLAUDE.md) tried to do everything
- Complex logic in single file
- Hard to maintain, test, and evolve

**After Three-Tier Architecture**:
- Master Orchestrator: Pure routing, no execution
- Mini-Orchestrators: Phase-specific coordination
- Sub-Agents: Single-responsibility execution
- Clear separation of concerns

**Benefits**:
- ✅ Single Responsibility Principle (each agent has one job)
- ✅ Testable (each agent can be validated independently)
- ✅ Maintainable (update one agent without affecting others)
- ✅ Composable (mix and match agents for different workflows)

---

## 2. Context Compression Sub-Agents (Proposed in ADR-002)

### What They Are

**Definition**: Specialized agents that analyze large context sources and return compressed summaries.

**Problem Statement** (from ADR-002):
```
AI coding assistants have token limits (200K for Claude)
Complex projects require 200K+ tokens of context:
├─ Project Context:    50,000 tokens
├─ Work Item Context:  80,000 tokens
└─ Task Context:       70,000 tokens
Total: 200,000+ tokens

Problem: Can't fit full context in single session
```

**Solution**: Delegation pattern for context compression

### Architecture

```
┌────────────────────────────────────────────────┐
│   Main Orchestrator (AI Coding Assistant)     │
│   Context Budget: 20,000 tokens               │
│   ├─ Project snapshot:     3,000 tokens       │
│   ├─ Work item snapshot:   5,000 tokens       │
│   ├─ Task snapshot:        8,000 tokens       │
│   └─ Sub-agent reports:    4,000 tokens       │
└──────────┬─────────────────────────────────────┘
           │ Delegates heavy analysis
           │
    ┌──────┴─────┬────────────┬─────────────┐
    │            │            │             │
┌───▼────────┐ ┌▼─────────┐ ┌▼──────────┐ ┌▼────────┐
│ codebase-  │ │ database-│ │ rules-    │ │ test-   │
│ navigator  │ │ schema-  │ │ compliance│ │ pattern-│
│            │ │ explorer │ │ checker   │ │ analyzer│
│ Input: 50K │ │ Input:   │ │ Input:    │ │ Input:  │
│ Output:    │ │ 30K      │ │ 20K       │ │ 25K     │
│ 1.2K       │ │ Output:  │ │ Output:   │ │ Output: │
│            │ │ 1.2K     │ │ 1.0K      │ │ 1.1K    │
│ Compress:  │ │ Compress:│ │ Compress: │ │ Compress│
│ 97.6%      │ │ 96.0%    │ │ 95.0%     │ │ 95.6%   │
└────────────┘ └──────────┘ └───────────┘ └─────────┘
```

### Compression Mechanism

**Structured Report Format**:
```python
@dataclass
class CompressedReport:
    """Standard format for all sub-agent outputs."""

    # One-line summary (≤15 words)
    summary: str

    # 3-5 key findings (≤25 words each)
    key_findings: List[str]

    # Relationships/connections (structured)
    relationships: List[str]

    # Patterns to follow (code examples if needed)
    patterns: List[Pattern]

    # File locations (path:line format)
    files: List[str]

    # Actionable recommendations (3-5 items)
    recommendations: List[str]

    # Confidence in findings (0.0-1.0)
    confidence: float

    # Actual token count (must be ≤2000)
    token_count: int
```

**Example Compression** (50K → 1.2K):

**Input Query**: "Find all tenant-scoped models and relationships"

**Internal Processing** (50,000 tokens):
- Searches 150 Python files
- Analyzes 50 models
- Traces 200 relationships
- Identifies 15 patterns
- Reviews 30 migrations

**Compressed Output** (1,200 tokens):
```yaml
summary: "18 tenant-scoped models found, all inherit TenantMixin"
key_models:
  - "Tenant (models/tenant.py:15-80) - Core tenant model"
  - "Domain (models/domain.py:10-45) - Custom domains per tenant"
  - "TenantUser (models/user.py:20-90) - Tenant-specific users"
relationships:
  - "Tenant → Domain (1:n via tenant_id FK)"
  - "Tenant → TenantUser (1:n via tenant_id FK)"
patterns:
  - "TenantMixin: Base class for tenant-scoped models"
  - "tenant_context(): Context manager for tenant isolation"
recommendations:
  - "New models should inherit TenantMixin"
  - "Use tenant_context() for queries"
confidence: 0.95
token_count: 1200
```

### Proposed Agents (from ADR-002)

**Core Analysis Sub-Agents**:
1. `CodebaseNavigatorAgent` (50K → 1.2K) - Find patterns, implementations, dependencies
2. `DatabaseSchemaExplorerAgent` (30K → 1.2K) - Map schema, relationships, migrations
3. `RulesComplianceCheckerAgent` (20K → 1.0K) - Validate against standards

**Specialized Sub-Agents**:
4. `WorkflowAnalyzerAgent` (15K → 900) - Task overlap, state transitions
5. `PluginSystemAnalyzerAgent` (50K → 1.5K) - Plugin patterns, coverage gaps
6. `TestPatternAnalyzerAgent` (25K → 1.1K) - Coverage analysis, test patterns
7. `DocumentationAnalyzerAgent` (30K → 1.3K) - Doc gaps, quality assessment

### Implementation Status

**❌ NOT IMPLEMENTED** (ADR-002 status: "Proposed")

**What Exists**:
- ADR-002 specification (complete)
- ADR-003 specification (sub-agent communication protocol)
- Compression targets defined
- Structured report format designed

**What Doesn't Exist**:
- No `CompressedReport` dataclass in codebase
- No compression sub-agents implemented
- No `ContextAssemblyService.assemble_comprehensive_context()` with sub-agent calls
- No caching infrastructure for compressed reports

**Current ContextService**:
```python
# agentpm/core/context/service.py
class ContextService:
    """Context service WITHOUT compression sub-agents."""

    def get_project_context(self, project_id: int) -> Dict[str, Any]:
        """Returns full context from database (no compression)."""
        # Loads project, contexts, amalgamations
        # Does NOT call compression sub-agents
        # Returns complete data structure
```

### Problem It Solves

**Context Explosion Problem**:
```
Session 1 (Main Orchestrator):
├─ Loads full project context (50K tokens)
├─ Loads full work item context (80K tokens)
├─ Loads full task context (70K tokens)
└─ Total: 200K tokens → EXCEEDS BUDGET ❌

Session 1 (With Compression Sub-Agents):
├─ Delegates to codebase-navigator → 1.2K tokens
├─ Delegates to database-explorer → 1.2K tokens
├─ Delegates to rules-checker → 1.0K tokens
├─ Loads compressed project context (3K tokens)
├─ Loads compressed work item context (5K tokens)
├─ Loads compressed task context (8K tokens)
└─ Total: 19.4K tokens → FITS IN BUDGET ✅
```

**10x Context Capacity**: Support 200K+ tokens of context in 20K tokens

---

## 3. Relationship Between Two Concepts

### Similarities (Why the Confusion)

1. **Both Called "Sub-Agents"**: Same terminology, different meaning
2. **Both Use Delegation**: Master delegates to sub-agents
3. **Both Use Task Tool**: Execute as separate agent personas
4. **Both Return Structured Reports**: Defined output formats

### Differences (Critical)

| Aspect | Tier 1 Sub-Agents | Compression Sub-Agents |
|--------|------------------|------------------------|
| **Status** | ✅ Implemented | ❌ Proposed (ADR-002) |
| **Purpose** | Execute phase tasks | Compress large context |
| **Tier** | Tier 1 (lowest) | Tier 0 (utility) |
| **Reports To** | Mini-Orchestrators | Main Orchestrator directly |
| **Input** | Phase artifacts | Large context sources |
| **Output** | Phase-specific artifacts | CompressedReport (1-2K tokens) |
| **Compression** | No compression | 95%+ compression |
| **Database** | Defined in `agents` table | Not in database |
| **Example** | `ac-writer`, `code-implementer` | `codebase-navigator`, `database-explorer` |

### Name Collision Problem

**The aipm-v2 CLAUDE.md mentions**:
```
"Sub-agents launch with Task tool"
"Sub-agents start with zero context"
```

**This refers to**: Tier 1 Sub-Agents (implemented)

**The ADRs mention**:
```
"Sub-agent delegation for compression"
"Sub-agents compress 50K → 1.2K"
```

**This refers to**: Compression Sub-Agents (proposed)

**Recommendation**: Rename compression sub-agents to **"Context Compression Agents"** or **"Analyzer Agents"** to avoid confusion.

---

## 4. What Needs to Be Built

### For Tier 1 Sub-Agents (Already Built)

**✅ Complete**:
- Agent definitions in database
- SOP content for all 25+ agents
- Generation script (`define_sub_agents.py`)
- Markdown generation via CLI
- Three-tier architecture documented

**Enhancement Opportunities**:
1. **Validation**: Test each sub-agent independently
2. **Metrics**: Track sub-agent execution time, success rate
3. **Improvement**: Refine SOPs based on usage patterns

### For Context Compression Sub-Agents (To Be Built)

**Phase 1: Core Framework** (Week 1-2)
```yaml
Tasks:
  - Define CompressedReport dataclass
  - Create SubAgent base class with compression validation
  - Implement caching infrastructure
  - Add token counting and validation

Files to Create:
  - agentpm/core/context/compression.py
  - agentpm/core/context/compressed_report.py
  - agentpm/core/context/cache.py
```

**Phase 2: Implement Compression Agents** (Week 3-6)
```yaml
Core Agents:
  - CodebaseNavigatorAgent (highest priority)
  - DatabaseSchemaExplorerAgent
  - RulesComplianceCheckerAgent

Integration:
  - Update ContextAssemblyService to use compression agents
  - Add assemble_comprehensive_context() method
  - Implement parallel agent execution
```

**Phase 3: Cache & Optimization** (Week 7-8)
```yaml
Tasks:
  - Implement ContextCache with 1-hour TTL
  - Add cache invalidation on code changes
  - Optimize database queries for sub-agents
  - Add cache warming for active work items
```

**Phase 4: Validation & Testing** (Week 9-10)
```yaml
Tasks:
  - Compression quality tests (>90% accuracy)
  - A/B testing (compressed vs full context)
  - Performance benchmarks (<5s per sub-agent)
  - Integration tests with all providers
```

---

## 5. Current System Reality

### What Actually Exists Today

**ContextService** (agentpm/core/context/service.py):
```python
class ContextService:
    """
    NO COMPRESSION - Returns full context from database.
    """

    def get_project_context(self, project_id: int) -> Dict[str, Any]:
        """Returns FULL project context (no compression)."""
        # Loads project entity
        # Loads UnifiedSixW from contexts table
        # Returns complete data structure
        # No sub-agent delegation
        # No compression

    def get_work_item_context(self, work_item_id: int) -> Dict[str, Any]:
        """Returns FULL work item + project context."""
        # Inherits full project context
        # Adds full work item data
        # No compression

    def get_task_context(self, task_id: int) -> Dict[str, Any]:
        """Returns FULL task + work item + project context."""
        # Inherits full work item context (which includes project)
        # Adds full task data
        # No compression
```

**Current Context Assembly**:
```python
# On session start
context = ContextService(db, project_path)
task_context = context.get_task_context(task_id)

# Result: Full hierarchical context (could be 200K+ tokens)
# No compression sub-agents called
# No CompressedReport format
# No token budget management
```

### What the ADRs Promise

**ADR-002 Vision**:
```python
# Proposed (not implemented)
class ContextAssemblyService:
    """WITH compression sub-agents."""

    def assemble_comprehensive_context(self, task_id: int) -> ComprehensiveContext:
        """
        Assemble with sub-agent compression (~20K tokens).
        """
        # Load standard context (15K tokens)
        standard = self.assemble_standard_context(task_id)

        # Delegate to compression sub-agents (5K tokens total)
        codebase_report = await delegate_to("codebase-navigator")  # 1.2K
        schema_report = await delegate_to("database-explorer")     # 1.2K
        rules_report = await delegate_to("rules-checker")          # 1.0K
        test_report = await delegate_to("test-analyzer")           # 1.1K

        return ComprehensiveContext(
            standard_context=standard,
            codebase_analysis=codebase_report,
            schema_analysis=schema_report,
            rules_compliance=rules_report,
            test_patterns=test_report,
            total_tokens=19400  # Fits in 20K budget!
        )
```

---

## 6. Implementation Roadmap

### Option 1: Implement ADR-002 Compression (High Value)

**Why**:
- Enables complex project support (currently impossible)
- 10x context capacity increase
- Solves real token limit problems

**Effort**: 8-10 weeks (as per ADR-002 timeline)

**Priority**: HIGH if working on complex projects

### Option 2: Enhance Tier 1 Sub-Agents (Medium Value)

**Why**:
- Improve existing architecture
- Add monitoring and metrics
- Refine SOPs based on usage

**Effort**: 2-3 weeks

**Priority**: MEDIUM (nice-to-have improvements)

### Option 3: Clarify Terminology (Low Effort, High Clarity)

**Why**:
- Avoid confusion between two concepts
- Clear documentation

**Actions**:
1. Rename compression sub-agents to "Context Compression Agents"
2. Update ADR-002 terminology
3. Update CLAUDE.md to distinguish between:
   - "Tier 1 Sub-Agents" (phase execution)
   - "Context Compression Agents" (context compression)

**Effort**: 1 day

**Priority**: HIGH (prevents future confusion)

---

## 7. Key Insights

### Discovery 1: Two Separate Concepts

**Sub-agents** means TWO different things in AIPM:
1. **Phase execution agents** (implemented, working)
2. **Context compression agents** (proposed, not implemented)

### Discovery 2: Compression Is Not Implemented

**Current Reality**:
- ContextService returns FULL context from database
- No compression mechanism exists
- No CompressedReport dataclass
- No sub-agent delegation for compression

**ADR-002 Promise**:
- 95%+ compression (200K → 20K tokens)
- Sub-agent delegation pattern
- Structured compression reports

**Gap**: ADR-002 is aspirational specification, not current system

### Discovery 3: Three-Tier Architecture Works

**Tier 1 Sub-Agents** (implemented) are working well:
- Clean separation of concerns
- Single-responsibility agents
- Database-driven, not file-based
- Generated on-demand via CLI

### Discovery 4: Compression Would Be Valuable

**If implemented**, context compression would:
- Enable complex project development (currently blocked by token limits)
- Provide 10x context capacity
- Maintain context quality through structured summaries

---

## 8. Recommendations

### Immediate (This Week)

1. **Clarify Terminology**
   - Rename compression sub-agents to "Context Compression Agents"
   - Update documentation to distinguish two concepts
   - Add clarity to CLAUDE.md and ADRs

2. **Document Current State**
   - Update ADR-002 status to clearly indicate "Not Implemented"
   - Add implementation status to docs
   - Create this analysis document

### Short-Term (Next Month)

3. **Prototype Compression Agent**
   - Build CodebaseNavigatorAgent as proof-of-concept
   - Measure compression ratio and quality
   - Validate token count assumptions

4. **Design Decisions**
   - Decide if compression is needed NOW (based on project complexity)
   - Prioritize against other features
   - Create implementation plan if proceeding

### Long-Term (Next Quarter)

5. **Full Compression Implementation** (if prioritized)
   - Follow ADR-002 timeline (10 weeks)
   - Implement all 7 compression agents
   - Add caching and optimization
   - Validate with real projects

---

## 9. Files Referenced

**Documentation**:
- `docs/adrs/ADR-002-context-compression-strategy.md` - Compression spec
- `docs/adrs/ADR-003-sub-agent-communication-protocol.md` - Communication protocol
- `docs/components/agents/README.md` - Agent system overview
- `.project_manager/aipm-v2/CLAUDE.md` - Master orchestrator instructions

**Code**:
- `scripts/define_sub_agents.py` - Tier 1 sub-agent definitions (25+ agents)
- `agentpm/core/context/service.py` - Current context service (no compression)
- `.claude/agents/sub-agents/*.md` - Generated agent files (execution artifacts)

**Database**:
- `agents` table - Agent definitions (source of truth)
- `agent_relationships` table - Orchestrator → sub-agent mappings

---

## 10. Conclusion

**Sub-agents in APM (Agent Project Manager) exist in two forms**:

1. **Tier 1 Sub-Agents** ✅
   - Implemented and working
   - 25+ single-responsibility agents
   - Part of three-tier architecture
   - Database-defined, CLI-generated

2. **Context Compression Agents** ❌
   - Proposed in ADR-002
   - Not implemented
   - Would provide 10x context capacity
   - 95%+ compression (200K → 20K tokens)

**Recommendation**: Prioritize terminology clarification NOW, decide on compression implementation based on project needs.

**Next Steps**:
1. Review this analysis with team
2. Decide terminology changes
3. Prioritize compression implementation (or defer)
4. Update documentation to reflect current state

---

**Analysis Complete**: 2025-10-17
**Confidence**: HIGH (comprehensive search and code analysis)
**Status**: Ready for review and decision
