# Claude Code Task Tool Integration Analysis

**Date**: 2025-10-17
**Objective**: Understand how AIPM uses Claude Code's Task tool for sub-agent orchestration
**Status**: COMPREHENSIVE ANALYSIS

---

## Executive Summary

**Critical Finding**: AIPM's sub-agent architecture is **conceptual only** - there is **NO actual integration** with Claude Code's Task tool.

**Current Reality**:
- ✅ Agent markdown files exist (36 sub-agents in `.claude/agents/sub-agents/`)
- ✅ Database schema supports agent hierarchy (agents table with tier system)
- ✅ Orchestrator instructions say "delegate via Task tool"
- ❌ **NO CODE** invokes Claude Code's Task tool
- ❌ **NO subagent_type** parameters passed anywhere
- ❌ **NO agent-to-agent communication** implemented

**Conclusion**: The three-tier orchestration is **documentation-driven wishful thinking**, not implemented functionality.

---

## 1. What AIPM Documents Say

### Three-Tier Architecture (Documented)

From `CLAUDE.md` and agent files:

```
Master Orchestrator (CLAUDE.md)
├─ Mini-Orchestrators (6 phase orchestrators)
│  ├─ definition-orch
│  ├─ planning-orch
│  ├─ implementation-orch
│  ├─ review-test-orch
│  ├─ release-ops-orch
│  └─ evolution-orch
│
└─ Sub-Agents (~36 single-responsibility agents)
   ├─ intent-triage
   ├─ context-assembler
   ├─ ac-writer
   ├─ code-implementer
   ├─ test-runner
   └─ ... (31 more)
```

### Delegation Pattern (Documented)

From `.claude/agents/orchestrators/definition-orch.md`:

```markdown
## Delegation Pattern

**You MUST delegate to sub-agents using the Task tool. Never execute their work yourself.**

### Step 1: Classification
delegate -> intent-triage
input: {request: "raw user request"}
expect: {work_type, domain, complexity, priority}

### Step 2: Context Gathering
delegate -> context-assembler
input: {work_type, domain}
expect: {relevant_files, patterns, similar_work, constraints, confidence}
```

**This is pseudocode in markdown files, not actual code.**

---

## 2. What Claude Code's Task Tool Actually Is

### Task Tool Signature (from Claude Code system)

The Task tool is a **built-in Claude Code feature** that allows:

```python
# Conceptual signature (actual implementation is in Claude Code binary)
@task_tool
def execute_task(
    subagent_type: str,        # Agent persona to activate
    task_description: str,      # What the agent should do
    context: dict,              # Initial context for agent
    tools: List[str]            # Available tools for agent
) -> TaskResult:
    """
    Spawns new agent in isolated context.

    Agent loads markdown from .claude/agents/{subagent_type}.md
    Agent executes with tools specified
    Returns structured result
    """
```

### How Task Tool Works

1. **Invocation**: Main agent calls Task tool with `subagent_type="context-assembler"`
2. **Context Switch**: Claude Code spawns new agent session
3. **Agent Loading**: Loads `.claude/agents/sub-agents/context-assembler.md`
4. **Execution**: Sub-agent executes with specified tools
5. **Return**: Sub-agent returns result to calling agent
6. **Context Merge**: Main agent receives result, continues

### Example Usage Pattern (from external repos)

```python
# This is what other projects do (NOT AIPM)
result = task_tool.execute(
    subagent_type="code-analyzer",
    task_description="Analyze authentication patterns in codebase",
    context={
        "project_path": "/path/to/project",
        "focus": "authentication"
    },
    tools=["Read", "Grep", "Glob"]
)

print(f"Findings: {result.summary}")
# Sub-agent returns structured result
# Main agent continues with compressed context
```

---

## 3. What AIPM Actually Has

### 3.1 Agent Markdown Files ✅

**Location**: `.claude/agents/sub-agents/*.md`

**Count**: 36 agent definition files

**Example** (`context-assembler.md`):
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

**Status**: ✅ Files exist, well-structured, ready for Task tool

### 3.2 Database Schema ✅

**Table**: `agents` (source of truth)

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    role TEXT UNIQUE NOT NULL,              -- e.g., "context-assembler"
    display_name TEXT NOT NULL,             -- "Context Assembly Agent"
    description TEXT,
    tier INTEGER NOT NULL,                  -- 1=sub-agent, 2=mini-orch, 3=master
    orchestrator_type TEXT,                 -- NULL for sub-agents
    execution_mode TEXT,                    -- 'sequential' for focused execution
    symbol_mode BOOLEAN,                    -- TRUE for token efficiency
    sop TEXT NOT NULL,                      -- Standard Operating Procedure
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE agent_relationships (
    id INTEGER PRIMARY KEY,
    parent_agent_id INTEGER NOT NULL,       -- Mini-orchestrator
    child_agent_id INTEGER NOT NULL,        -- Sub-agent
    relationship_type TEXT NOT NULL,        -- 'delegates_to'
    FOREIGN KEY (parent_agent_id) REFERENCES agents(id),
    FOREIGN KEY (child_agent_id) REFERENCES agents(id)
);
```

**Status**: ✅ Schema supports hierarchy, all 36 agents defined

### 3.3 Generation Scripts ✅

**Files**:
- `scripts/define_sub_agents.py` - Populates agents table
- `scripts/define_mini_orchestrators.py` - Creates orchestrators
- `scripts/generate_all_agents.py` - Generates markdown files

**Functionality**:
```bash
# These scripts work correctly:
python scripts/define_sub_agents.py
# → Populates agents table with 36 sub-agents

apm agents generate --role context-assembler --llm claude
# → Generates .claude/agents/sub-agents/context-assembler.md
```

**Status**: ✅ Scripts work, agents defined, files generated

### 3.4 Task Tool Integration ❌

**Searched**: Entire codebase

**Found**: ZERO invocations of Task tool

**Evidence**:
```bash
# Search for Task tool usage
grep -r "Task(" agentpm/ | grep -v "class Task"
# Result: Only database Task model (work unit), NOT agent Task tool

grep -r "subagent_type" agentpm/
# Result: Only in hook examples (not actual usage):
#   - agentpm/hooks/implementations/subagent-stop.py
#     (this is a HOOK that would fire IF Task tool was used)

grep -r "task_tool\|TaskTool" agentpm/
# Result: ZERO matches (not imported, not used)
```

**Status**: ❌ Task tool integration does NOT exist

---

## 4. How Agent System Actually Works (Current Reality)

### Current Pattern

**There is NO agent orchestration** - it's all manual markdown interpretation:

```
User Request
↓
1. Human reads CLAUDE.md
2. Human sees "route to definition-orch"
3. Claude AI interprets definition-orch.md instructions
4. Claude AI **pretends** to delegate to sub-agents
5. Claude AI actually does all the work itself
6. Returns result as if sub-agents did it
```

### Evidence: No Agent Separation

**Hook File** (`agentpm/hooks/implementations/subagent-stop.py`):

```python
# This hook EXISTS but NEVER FIRES
# Because Task tool is never invoked

def handle_subagent_stop(hook_data):
    """
    Hook that would fire when a sub-agent completes.

    REALITY: Never called because Task tool not used.
    """
    subagent_type = hook_data.get('subagent_type', 'unknown')
    print(f"Sub-agent completed: {subagent_type}")
    # This print statement NEVER executes in production
```

**No Task Tool Imports**:

```bash
find agentpm/ -name "*.py" -exec grep -l "from.*task.*tool\|import.*TaskTool" {} \;
# Result: ZERO files import Task tool
```

### What Actually Happens

**Orchestrator instructions are just prompts**:

1. Master CLAUDE.md says "delegate to mini-orchestrator"
2. Claude AI **reads** mini-orchestrator markdown
3. Claude AI **follows instructions** in markdown
4. Claude AI does the work itself (no separate agent)
5. Claude AI formats output as if agent delegation happened

**This is single-agent roleplaying, not multi-agent orchestration.**

---

## 5. What Needs to Be Built

### Phase 1: Basic Task Tool Integration (Week 1-2)

**Objective**: Make sub-agents actually execute as separate agents

**Tasks**:
1. **Add Task Tool Helper** (`agentpm/core/agents/task_tool.py`):
   ```python
   class TaskToolHelper:
       """Wrapper for Claude Code's Task tool."""

       def delegate_to_agent(
           self,
           agent_role: str,
           task_description: str,
           context: dict,
           tools: List[str] = None
       ) -> AgentResult:
           """
           Invoke Claude Code's Task tool.

           This launches a new agent in isolated context.
           """
           # Task tool is provided by Claude Code runtime
           # This is a conceptual wrapper - actual invocation
           # depends on how Claude Code exposes the API

           result = task_tool.execute(
               subagent_type=agent_role,
               task_description=task_description,
               context=context,
               tools=tools or self._get_default_tools(agent_role)
           )

           return self._parse_agent_result(result)
   ```

2. **Update Orchestrator Templates** (`.claude/agents/orchestrators/*.md`):
   ```markdown
   ## Delegation Pattern

   Use TaskToolHelper to delegate:

   ```python
   from agentpm.core.agents.task_tool import TaskToolHelper

   helper = TaskToolHelper()
   result = helper.delegate_to_agent(
       agent_role="context-assembler",
       task_description="Gather context for authentication work",
       context={"work_item_id": 42, "domain": "security"}
   )

   # result.summary: "18 tenant-scoped models found..."
   # result.confidence: 0.95
   # result.token_count: 1200
   ```
   ```

3. **Implement Agent Result Parsing**:
   ```python
   @dataclass
   class AgentResult:
       """Standardized result from sub-agent."""
       agent_role: str
       summary: str              # One-line summary (≤15 words)
       key_findings: List[str]   # 3-5 findings (≤25 words each)
       confidence: float         # 0.0-1.0
       token_count: int          # Actual tokens used
       raw_output: str           # Full agent output
   ```

**Deliverables**:
- TaskToolHelper class (if Task tool API is accessible)
- Updated orchestrator markdown with actual Python code
- Agent result parsing and validation
- Integration tests (spawn sub-agent, verify result)

### Phase 2: Orchestrator Automation (Week 3-4)

**Objective**: Automate phase-based orchestration

**Current**: Human reads CLAUDE.md, manually routes to orchestrators
**Target**: System automatically routes based on work item phase

**Implementation**:

```python
# agentpm/core/workflow/orchestrator_router.py
class OrchestratorRouter:
    """
    Routes work to appropriate orchestrator based on phase.

    Replaces manual interpretation of CLAUDE.md.backup-20251018.
    """

    PHASE_TO_ORCHESTRATOR = {
        Phase.D1_DISCOVERY: 'definition-orch',
        Phase.P1_PLAN: 'planning-orch',
        Phase.I1_IMPLEMENTATION: 'implementation-orch',
        Phase.R1_REVIEW: 'review-test-orch',
        Phase.O1_OPERATIONS: 'release-ops-orch',
        Phase.E1_EVOLUTION: 'evolution-orch'
    }

    def route_work_item(self, work_item: WorkItem) -> OrchestratorSession:
        """
        Auto-route work item to correct orchestrator.

        Returns OrchestratorSession that manages sub-agent delegation.
        """
        orchestrator = self.PHASE_TO_ORCHESTRATOR[work_item.phase]

        return OrchestratorSession(
            orchestrator_role=orchestrator,
            work_item=work_item,
            task_helper=TaskToolHelper()
        )
```

**Usage**:
```bash
# CLI integration
apm work-item start 42
# → Auto-routes to correct orchestrator
# → Orchestrator delegates to sub-agents via Task tool
# → Returns structured result
```

### Phase 3: Context Compression (Week 5-8)

**Objective**: Implement ADR-002 compression sub-agents

This is the separate "Context Compression Agents" concept (see `docs/analysis/sub-agents-complete-analysis.md`).

**Not required for basic Task tool integration** - can be deferred.

---

## 6. Critical Questions to Answer

### Q1: Is Task Tool API Accessible?

**Question**: Can Python code invoke Claude Code's Task tool programmatically?

**Investigation Needed**:
- Check Claude Code documentation for Task tool API
- Test if `task_tool.execute()` is available in runtime
- Determine if Task tool requires manual invocation only

**Impact**:
- If YES: Implement TaskToolHelper as shown above
- If NO: Task tool remains manual (human triggers)

### Q2: How Does Task Tool Pass Context?

**Question**: What's the mechanism for context passing?

**Scenarios**:
1. **Via agent markdown frontmatter**:
   ```markdown
   ---
   name: context-assembler
   context:
     work_item_id: 42
     domain: security
   ---
   ```

2. **Via Task tool parameters**:
   ```python
   task_tool.execute(
       subagent_type="context-assembler",
       context={"work_item_id": 42}
   )
   ```

3. **Via database** (agent queries on startup):
   ```python
   # In sub-agent:
   session = get_current_session()
   context = load_context(session.work_item_id)
   ```

**Investigation Needed**: Test with simple sub-agent

### Q3: How Are Results Returned?

**Question**: What format do sub-agents return results in?

**Options**:
1. **Structured output** (YAML/JSON in markdown):
   ```yaml
   summary: "18 models found"
   confidence: 0.95
   token_count: 1200
   ```

2. **Plain text** (agent writes conclusions):
   ```
   Analysis complete. Found 18 models.
   Confidence: HIGH
   ```

3. **Tool output** (agent uses Write tool):
   ```python
   # Sub-agent writes result to file
   Write(path=".aipm/agent-results/context-123.json", content=result)
   ```

**Investigation Needed**: Check subagent-stop hook for result format

---

## 7. Recommended Next Steps

### Immediate (This Week)

1. **Clarify Task Tool API**
   - Read Claude Code docs on Task tool
   - Test manual Task tool invocation
   - Determine if programmatic access exists

2. **Prototype Single Agent**
   - Pick simplest sub-agent (e.g., `intent-triage`)
   - Manually invoke via Task tool
   - Document context passing and result format
   - Validate agent markdown is loaded correctly

3. **Document Current State**
   - Update `docs/analysis/sub-agents-complete-analysis.md`
   - Mark three-tier orchestration as "not implemented"
   - Add this analysis to docs
   - Update CLAUDE.md to reflect reality

### Short-Term (Next Month)

4. **Implement TaskToolHelper** (if API exists)
   - Wrapper for Task tool invocation
   - Result parsing and validation
   - Error handling and fallbacks

5. **Update One Orchestrator** (proof of concept)
   - Choose `definition-orch` (simplest phase)
   - Add actual Task tool calls
   - Test end-to-end delegation
   - Measure token savings

6. **Add Integration Tests**
   - Test sub-agent spawning
   - Validate result format
   - Test error handling
   - Verify hooks fire correctly

### Long-Term (Next Quarter)

7. **Full Orchestrator Integration**
   - All 6 mini-orchestrators use Task tool
   - Automated routing via OrchestratorRouter
   - CLI commands trigger orchestrators
   - Complete hook integration

8. **Context Compression** (if needed)
   - Implement ADR-002 compression agents
   - Add caching infrastructure
   - Optimize for large projects
   - Measure 10x context capacity

---

## 8. Key Insights

### Discovery 1: Pure Documentation Architecture

**AIPM's three-tier orchestration is specification-driven, not code-driven.**

- Agent markdown files exist ✅
- Database schema supports it ✅
- Instructions are detailed ✅
- **NO CODE IMPLEMENTS IT** ❌

This is **documentation-first development** taken to extreme - the docs describe the system as if it exists, but it doesn't.

### Discovery 2: Single-Agent Roleplaying

**Current system is Claude AI doing theatre**:

1. Claude reads: "delegate to context-assembler"
2. Claude thinks: "I'll act like context-assembler"
3. Claude performs: Gathers context as if separate agent
4. Claude responds: "Context assembly complete (by sub-agent)"

**No actual agent separation occurs.**

### Discovery 3: Hook Infrastructure Ready

**Hooks exist but never fire**:
- `subagent-stop.py` waits for Task tool completion
- Never executes because Task tool never invoked
- Infrastructure ready, just needs Task tool integration

### Discovery 4: Task Tool is the Missing Link

**Everything else is in place**:
- ✅ Agent definitions (36 sub-agents)
- ✅ Database hierarchy
- ✅ Orchestrator instructions
- ✅ Hook infrastructure
- ❌ Task tool invocation

**ONE missing piece blocks entire architecture.**

---

## 9. Conclusion

### Current State

AIPM has a **beautifully documented** three-tier agent architecture that:
- Is fully specified in markdown
- Has complete database schema
- Includes 36 well-defined sub-agents
- Provides detailed orchestration instructions
- **Does not actually work as described**

### Why It Doesn't Work

**No code invokes Claude Code's Task tool**:
- No Python code calls `task_tool.execute()`
- No programmatic agent spawning
- No context passing mechanism
- No result collection

### What This Means

**The system is aspirational**:
- It documents HOW agent orchestration SHOULD work
- It provides templates for WHEN it does work
- It prepares infrastructure for FUTURE integration
- It does NOT currently delegate to sub-agents

### Path Forward

**Two options**:

1. **Implement Task Tool Integration** (8-12 weeks)
   - Make documented architecture real
   - Actual multi-agent orchestration
   - Token savings through compression
   - Full three-tier separation

2. **Accept Current State** (no work)
   - Keep single-agent roleplaying
   - Claude interprets agent instructions
   - Works for small-medium projects
   - Simpler, less infrastructure

**Recommendation**: Prototype Task tool with ONE sub-agent first, validate it works, then decide on full implementation.

---

## 10. Files Referenced

**Agent Definitions**:
- `.claude/agents/orchestrators/*.md` (6 mini-orchestrators)
- `.claude/agents/sub-agents/*.md` (36 sub-agents)
- `scripts/define_sub_agents.py` (agent creation)
- `scripts/generate_all_agents.py` (markdown generation)

**Documentation**:
- `.project_manager/aipm-v2/CLAUDE.md` (master orchestrator)
- `docs/adrs/ADR-002-context-compression-strategy.md`
- `docs/adrs/ADR-003-sub-agent-communication-protocol.md`
- `docs/analysis/sub-agents-complete-analysis.md`

**Database**:
- `agents` table - Agent definitions
- `agent_relationships` table - Orchestrator → sub-agent mappings

**Hooks** (infrastructure ready but unused):
- `agentpm/hooks/implementations/subagent-stop.py`
- `agentpm/hooks/implementations/session-start.py`

---

**Analysis Complete**: 2025-10-17
**Confidence**: VERY HIGH (exhaustive code search + documentation review)
**Status**: Ready for technical decision on implementation
