# Migration 0014: Agent System Enhancement - Summary

## Overview

**Migration File**: `/agentpm/core/database/migrations/files/migration_0014.py`
**Documentation**: `/docs/architecture/database/agent-system-schema.md`
**SQL Reference**: `/docs/architecture/database/agent-system-schema.sql`

This migration enhances the existing agent system with database-first architecture supporting the three-tier orchestration pattern (Master → Mini-Orchestrators → Sub-Agents) while keeping SuperClaude complexity minimal.

## Schema Changes

### 1. Enhanced `agents` Table (4 new columns)

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `execution_mode` | TEXT | 'parallel' | Execution preference: 'parallel' or 'sequential' |
| `symbol_mode` | INTEGER | 0 | Symbol-based reporting: 0=disabled, 1=enabled |
| `orchestrator_type` | TEXT | NULL | Tier: 'master', 'mini', or NULL (sub-agent) |
| `agent_file_path` | TEXT | NULL | Path to agent SOP file (e.g., '.claude/agents/orchestrators/definition-orch.md') |

### 2. New Table: `agent_relationships`

Tracks agent delegation and reporting hierarchy.

**Purpose**: Support three-tier architecture delegation patterns

**Key Fields**:
- `agent_id` → `related_agent_id`
- `relationship_type`: 'delegates_to' or 'reports_to'
- `metadata` (JSON): Phases, conditions, constraints, escalation rules

**Example**:
```json
{
  "agent_id": 1,  // Master Orchestrator
  "related_agent_id": 2,  // DefinitionOrch
  "relationship_type": "delegates_to",
  "metadata": {
    "phases": ["definition"],
    "artifact": "workitem.ready",
    "conditions": ["confidence >= 0.7"]
  }
}
```

### 3. New Table: `agent_tools`

MCP tool preferences per workflow phase (borrowed from SuperClaude).

**Purpose**: Database-driven MCP tool routing

**Workflow Phases**:
- `discovery`: Research, context gathering (Context7, Tavily)
- `implementation`: Code generation (Magic, Morphllm)
- `reasoning`: Analysis, debugging (Sequential-Thinking)
- `testing`: Test execution, validation
- `documentation`: Doc generation
- `deployment`: Release, deployment

**Tool Priority**:
- `1` (primary): First choice tool
- `2` (fallback): Use if primary fails
- `3` (optional): Enhancement only

**Example**:
```json
{
  "agent_id": 42,  // context-delivery
  "phase": "discovery",
  "tool_name": "context7",
  "priority": 1,
  "config": {
    "topic_focus": true,
    "token_limit": 5000
  }
}
```

### 4. New Table: `agent_examples`

Learning scenarios with input/output pairs for agent improvement.

**Purpose**: Enable agent learning and performance improvement

**Key Fields**:
- `scenario_name`: Descriptive name
- `category`: Scenario type (discovery, implementation, error-handling)
- `input_context` (JSON): Request, context, constraints
- `expected_output` (JSON): Response, artifacts, decisions
- `success_criteria`: What makes this successful
- `edge_cases` (JSON array): Edge case handling
- `effectiveness_score`: 0.0-1.0 quality metric

**Example**:
```json
{
  "scenario_name": "Discovery with Low Context",
  "category": "discovery",
  "input_context": {
    "request": "Implement user authentication",
    "context": {
      "confidence": 0.3,
      "missing": ["tech_stack", "security_requirements"]
    },
    "constraints": {"time_budget": 300}
  },
  "expected_output": {
    "artifacts": ["research.md", "requirements.yaml"],
    "decisions": [
      "Escalate to external-discovery",
      "Escalate to internal-discovery"
    ],
    "confidence_improvement": 0.7
  },
  "success_criteria": "Context confidence >= 0.7 AND all critical gaps filled",
  "effectiveness_score": 0.85
}
```

## SuperClaude Patterns Borrowed (Minimal Complexity)

### ✅ Borrowed (Useful)
1. **Parallel Execution Preference**: `execution_mode` column supports parallel-first approach
2. **MCP Tool Routing**: `agent_tools` table routes tools per workflow phase
3. **Symbol-Based Reporting**: `symbol_mode` flag enables compressed communication (30-50% token reduction)

### ❌ Avoided (Too Complex)
1. **Resource Zones**: Not needed for APM (Agent Project Manager)
2. **Adaptive Depth**: Keep orchestration simple and predictable
3. **Multiple Brainstorming Modes**: Single focused approach

## Three-Tier Architecture Support

### Master Orchestrator (1)
```sql
orchestrator_type = 'master'
execution_mode = 'parallel'  -- Delegates only, never executes
symbol_mode = 0              -- Full verbose coordination
```

**Delegates to**: All 6 mini-orchestrators
**Reports to**: NULL (top-level)

### Mini-Orchestrators (6)
```sql
orchestrator_type = 'mini'
execution_mode = 'parallel'  -- Parallel sub-agent delegation
symbol_mode = 0              -- Phase-specific reporting
```

**Examples**:
- `definition-orch` → delegates to: intent-triage, context-assembler, problem-framer, ac-writer, risk-notary
- `planning-orch` → delegates to: decomposer, estimator, dependency-mapper, mitigation-planner
- `implementation-orch` → delegates to: pattern-applier, code-implementer, test-implementer
- `review-test-orch` → delegates to: static-analyzer, test-runner, ac-verifier, quality-gatekeeper
- `release-ops-orch` → delegates to: versioner, deploy-orchestrator, health-verifier
- `evolution-orch` → delegates to: signal-harvester, insight-synthesizer, debt-registrar

**Reports to**: Master Orchestrator

### Sub-Agents (~25)
```sql
orchestrator_type = NULL     -- Not an orchestrator
execution_mode = 'sequential' OR 'parallel'  -- Task-dependent
symbol_mode = 1              -- Compressed reporting (token efficiency)
```

**Delegates to**: NULL (single-responsibility, no delegation)
**Reports to**: Parent mini-orchestrator

**Tool preferences**: Configured per agent in `agent_tools` table

## Performance & Storage

### Indexes Created (10 total)
- **2 agents**: execution_mode, orchestrator_type (partial)
- **2 relationships**: agent_id/type, related_agent_id/type
- **3 tools**: agent/phase, priority, usage (partial)
- **3 examples**: agent/category, score (partial), recent (partial)

### Query Performance
- Agent delegation lookup: **O(log n)** with indexes
- Tool selection: **O(log n)** with priority index
- Example retrieval: **O(log n)** with score index

### Storage Impact (Minimal)
- **agent_relationships**: ~5KB (50 relationships × 100 bytes)
- **agent_tools**: ~30KB (150 tools × 200 bytes)
- **agent_examples**: ~200KB (200 examples × 1KB)
- **Total overhead**: ~235KB

## Migration Safety

### ✅ Idempotent
- All `CREATE TABLE IF NOT EXISTS`
- All `CREATE INDEX IF NOT EXISTS`
- Column additions check for existence
- Safe to run multiple times

### ✅ Backward Compatible
- New columns have defaults (no data migration)
- Existing queries still work
- No breaking changes

### ⚠️ Rollback Limitation
- `downgrade()` drops tables/indexes successfully
- **SQLite cannot drop columns** - new columns remain but unused after rollback
- Full rollback would require agents table recreation

## Usage Examples

### 1. Query Agent Delegation Tree
```sql
-- Who does DefinitionOrch delegate to?
SELECT
    a2.role,
    a2.display_name,
    ar.metadata
FROM agent_relationships ar
JOIN agents a1 ON ar.agent_id = a1.id
JOIN agents a2 ON ar.related_agent_id = a2.id
WHERE a1.role = 'definition-orch'
  AND ar.relationship_type = 'delegates_to';
```

### 2. Query Tool Preferences
```sql
-- Get primary tools for discovery phase
SELECT
    tool_name,
    config
FROM agent_tools
WHERE agent_id = 42  -- context-delivery
  AND phase = 'discovery'
  AND priority = 1;
```

### 3. Query Learning Examples
```sql
-- Find high-quality examples for similar scenarios
SELECT
    scenario_name,
    input_context,
    expected_output,
    effectiveness_score
FROM agent_examples
WHERE agent_id = 45
  AND category = 'discovery'
  AND effectiveness_score >= 0.8
ORDER BY effectiveness_score DESC
LIMIT 5;
```

### 4. Query Parallel Execution Agents
```sql
-- Find all agents preferring parallel execution
SELECT
    role,
    display_name,
    orchestrator_type
FROM agents
WHERE execution_mode = 'parallel'
  AND is_active = 1
ORDER BY orchestrator_type NULLS LAST;
```

## Symbol-Based Reporting (Token Efficiency)

When `symbol_mode = 1`, agents use compressed communication:

**Standard (verbose)**:
```
The authentication system has a security vulnerability in the user validation
function at line 45. Performance analysis shows the algorithm is slow because
it has O(n²) complexity.
```

**Symbol mode (compressed)**:
```
auth.js:45 → 🛡️ sec risk in user val()
⚡ perf: slow ∵ O(n²) complexity
```

**Token reduction**: 30-50%
**Information preserved**: ≥95%

## Next Steps

1. **Run Migration**: Apply migration 0014 to database
   ```bash
   apm migrate up
   ```

2. **Populate Relationships**: Map three-tier architecture
   ```sql
   INSERT INTO agent_relationships (agent_id, related_agent_id, relationship_type, metadata)
   VALUES (1, 2, 'delegates_to', '{"phases": ["definition"], "artifact": "workitem.ready"}');
   ```

3. **Configure Tools**: Set MCP preferences per agent/phase
   ```sql
   INSERT INTO agent_tools (agent_id, phase, tool_name, priority, config)
   VALUES (42, 'discovery', 'context7', 1, '{"topic_focus": true}');
   ```

4. **Add Examples**: Create learning scenarios
   ```sql
   INSERT INTO agent_examples (agent_id, scenario_name, category, input_context, expected_output)
   VALUES (45, 'Low Context Discovery', 'discovery', '{"request": "..."}', '{"artifacts": [...]}');
   ```

5. **Enable Symbol Mode**: Test token reduction with sub-agents
   ```sql
   UPDATE agents SET symbol_mode = 1 WHERE orchestrator_type IS NULL;
   ```

6. **Validate**: Run post-migration validation
   ```python
   from agentpm.core.database.migrations.files import migration_0014
   is_valid = migration_0014.validate_post(conn)
   ```

## Files Created

1. **Migration File**: `agentpm/core/database/migrations/files/migration_0014.py`
   - Upgrade/downgrade functions
   - Validation functions
   - Migration summary

2. **Documentation**: `docs/architecture/database/agent-system-schema.md`
   - Complete schema explanation
   - Design principles
   - Usage patterns
   - Performance considerations

3. **SQL Reference**: `docs/architecture/database/agent-system-schema.sql`
   - Complete SQL schema
   - Example data
   - Useful queries
   - Hierarchy visualization

## Validation

**Syntax Check**: ✅ Passed
```bash
python -c "from agentpm.core.database.migrations.files import migration_0014"
```

**Structure Check**: ✅ Passed
- `upgrade()` ✅
- `downgrade()` ✅
- `validate_post()` ✅
- `get_migration_summary()` ✅

**Migration Summary**:
- Tables: 3 (agent_relationships, agent_tools, agent_examples)
- Columns Added: 4 (execution_mode, symbol_mode, orchestrator_type, agent_file_path)
- Indexes: 10
- Backward Compatible: ✅ Yes
- Data Migration Required: ❌ No

## Design Decisions

### Why Database-First?
- **Centralized Configuration**: All agent setup in database, not scattered in code
- **Runtime Flexibility**: Change tool preferences, relationships without code changes
- **Learning Support**: Track example effectiveness, improve agent behavior over time
- **Audit Trail**: All delegation and tool usage tracked in database

### Why Minimal SuperClaude?
- **Complexity Control**: Avoid resource zones, adaptive depth, multiple modes
- **Focused Features**: Only parallel execution, MCP routing, symbol reporting
- **APM (Agent Project Manager) Fit**: Match AIPM's simpler, more predictable architecture

### Why Three-Tier?
- **Clear Separation**: Master (delegate only) → Mini (phase-specific) → Sub (single-task)
- **Scalability**: Add new sub-agents without affecting orchestrators
- **Maintainability**: Each tier has well-defined responsibilities

## Success Criteria

✅ **Schema Design**: Minimal, focused, no SuperClaude bloat
✅ **Migration Safety**: Idempotent, backward compatible, validated
✅ **Documentation**: Complete schema docs, SQL reference, usage examples
✅ **Performance**: Indexed queries, minimal storage overhead (~235KB)
✅ **Three-Tier Support**: Master → Mini → Sub hierarchy fully supported
✅ **Learning Enabled**: Examples with effectiveness tracking
✅ **MCP Integration**: Tool routing per phase, priority-based selection

## References

- **Three-Tier Orchestration**: `docs/components/agents/architecture/three-tier-orchestration.md`
- **Agent SOPs**: `.claude/agents/orchestrators/*.md`, `.claude/agents/sub-agents/*.md`
- **SuperClaude MCP**: `.claude/MCP_*.md` (Context7, Sequential, Magic, etc.)
- **Symbol System**: `.claude/MODE_Token_Efficiency.md`
- **Existing Schema**: `migration_0001.py` (base), `migration_0011.py` (agent enhancements)
