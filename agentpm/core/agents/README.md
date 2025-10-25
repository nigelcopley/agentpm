# Agent Loading System

Extensible system for loading agent definitions from YAML files to database.

## Overview

The agent loader provides a type-safe, validated approach to defining and loading agents into AIPM. It supports:

- **Pydantic validation**: Schema enforcement with clear error messages
- **Dependency checking**: Validates agent dependencies exist
- **Conflict detection**: Prevents duplicate agent roles
- **Dry-run mode**: Validate without database changes
- **Batch loading**: Load multiple agents from directories
- **Force overwrite**: Update existing agents

## Quick Start

### CLI Usage

```bash
# Load all agents from .claude/agents/
apm agents load

# Load specific file
apm agents load --file=my-agent.yaml

# Validate without loading
apm agents load --validate-only

# Force overwrite existing agents
apm agents load --force

# Load from custom directory
apm agents load --directory=./config/agents --pattern="*.yml"
```

### Python API

```python
from agentpm.core.agents.loader import AgentLoader
from pathlib import Path

# Initialize loader
loader = AgentLoader(db_service, project_id=1)

# Load single file
result = loader.load_from_yaml(
    Path("agent.yaml"),
    project_id=1,
    dry_run=False,
    force=False
)

# Load directory
result = loader.load_all(
    Path(".claude/agents/"),
    project_id=1,
    dry_run=False,
    force=False,
    pattern="*.yaml"
)

# Check results
if result.success:
    print(f"Loaded {result.loaded_count} agents")
else:
    print(f"Errors: {result.errors}")
```

## YAML Format

### Single Agent

```yaml
role: intent-triage
display_name: Intent Triage Agent
description: Classifies requests by type, domain, complexity, and priority
tier: 1
category: sub-agent
sop_content: |
  You are the Intent Triage agent.

  ## Responsibilities
  - Analyze raw requests
  - Classify by type, domain, complexity
  - Assign priority

  ## Output Format
  ```yaml
  work_type: FEATURE
  domain: authentication
  complexity: MEDIUM
  priority: P1
  ```
capabilities:
  - request_classification
  - domain_mapping
  - complexity_assessment
  - priority_assignment
tools:
  - Read
  - Grep
  - Glob
  - Write
dependencies:
  - context-assembler
triggers:
  - raw_request_received
  - classification_needed
examples:
  - "Classify 'Add OAuth2 login' as FEATURE, auth domain, MEDIUM, P1"
  - "Triage 'Fix slow query' as BUGFIX, database domain, HIGH, P2"
agent_type: analyzer
metadata:
  version: "1.0.0"
  author: "AIPM Team"
is_active: true
```

### Multiple Agents

```yaml
agents:
  - role: agent-one
    display_name: First Agent
    description: First agent description
    tier: 1
    category: sub-agent
    sop_content: "Agent one SOP"
    capabilities:
      - capability_one

  - role: agent-two
    display_name: Second Agent
    description: Second agent description
    tier: 2
    category: specialist
    sop_content: "Agent two SOP"
    capabilities:
      - capability_two
    dependencies:
      - agent-one
```

## Field Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Unique agent identifier (lowercase-with-hyphens) |
| `display_name` | string | Human-readable agent name |
| `description` | string | Agent purpose and responsibilities |
| `tier` | integer | Agent tier (1=sub-agent, 2=specialist, 3=orchestrator) |
| `category` | string | Agent category (orchestrator, sub-agent, specialist, utility, generic) |
| `sop_content` | string | Standard Operating Procedure (markdown) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capabilities` | list[string] | [] | List of agent capabilities |
| `tools` | list[string] | [] | Required tools (Read, Write, Bash, etc.) |
| `dependencies` | list[string] | [] | Other agents this depends on |
| `triggers` | list[string] | [] | When to invoke (for auto-selection) |
| `examples` | list[string] | [] | Usage examples |
| `agent_type` | string | null | Base template type (e.g., 'implementer', 'tester') |
| `metadata` | dict | {} | Additional agent metadata |
| `is_active` | boolean | true | Whether agent is currently active |

## Validation Rules

### Role Format

- Must contain only alphanumeric characters, hyphens, and underscores
- Automatically converted to lowercase
- Must be unique within project

**Valid**: `intent-triage`, `python-implementer`, `code_reviewer`
**Invalid**: `Intent Triage`, `python implementer`, `code@reviewer`

### Category

Must be one of:
- `orchestrator` - Coordinates other agents (Tier 3)
- `sub-agent` - Research and analysis (Tier 1)
- `specialist` - Implementation (Tier 2)
- `utility` - Helper functions
- `generic` - General purpose

### Tier

Must be 1, 2, or 3:
- **Tier 1**: Sub-agents (research, analysis, discovery)
- **Tier 2**: Specialist agents (implementation, testing)
- **Tier 3**: Orchestrators (coordination, routing)

## Error Handling

### Validation Errors

```yaml
# Missing required field
role: test-agent
display_name: Test Agent
# ERROR: Missing 'description', 'tier', 'category', 'sop_content'
```

**Error Message**:
```
Agent 1: Validation failed:
  description: Field required
  tier: Field required
  category: Field required
  sop_content: Field required
```

### Conflict Detection

```yaml
# Duplicate role
role: intent-triage
display_name: New Intent Triage
# ERROR: Role 'intent-triage' already exists
```

**Error Message**:
```
Conflicts:
  intent-triage:
    • Agent already exists

Tip: Use --force to overwrite existing agents
```

### Dependency Warnings

```yaml
# Missing dependency
role: dependent-agent
dependencies:
  - missing-agent
# WARNING: Dependency 'missing-agent' not found
```

**Warning Message**:
```
Warnings:
  • dependent-agent: Missing dependencies: missing-agent
```

## Architecture

### Component Diagram

```
┌─────────────────┐
│   CLI Command   │
│  apm agents load│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AgentLoader    │
│  - load_from_yaml
│  - load_all     │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌─────────────┐  ┌────────────┐  ┌──────────┐
│AgentDefinition│ │LoadResult │  │ Database │
│ (Pydantic)  │  │(dataclass)│  │ Service  │
└─────────────┘  └────────────┘  └──────────┘
```

### Data Flow

1. **Read YAML**: Parse file(s) with PyYAML
2. **Validate**: Pydantic validates schema
3. **Convert**: Transform to Agent models
4. **Check Dependencies**: Validate all deps exist
5. **Detect Conflicts**: Check for duplicate roles
6. **Insert/Update**: Write to database (or dry-run)
7. **Return Result**: Statistics, errors, warnings

## Extension Points

### Custom Categories

Add new categories by updating validation:

```python
@field_validator('category')
@classmethod
def validate_category(cls, v: str) -> str:
    valid = {
        'orchestrator', 'sub-agent', 'specialist',
        'utility', 'generic',
        'custom-category'  # Add custom category
    }
    if v not in valid:
        raise ValueError(f"Category must be one of {valid}")
    return v
```

### Custom Metadata Fields

Add structured metadata in YAML:

```yaml
metadata:
  version: "1.0.0"
  author: "Team Name"
  tags:
    - python
    - testing
  experimental: true
  performance_budget:
    max_tokens: 100000
    timeout_seconds: 300
```

Access in code:

```python
metadata = json.loads(agent.metadata)
if metadata.get('experimental'):
    # Handle experimental agent
    pass
```

### Custom Validation

Add custom validators:

```python
@field_validator('sop_content')
@classmethod
def validate_sop_length(cls, v: str) -> str:
    if len(v) < 100:
        raise ValueError("SOP must be at least 100 characters")
    if len(v) > 50000:
        raise ValueError("SOP must be less than 50K characters")
    return v
```

## Best Practices

### 1. Organize by Directory

```
.claude/agents/
├── orchestrators/
│   ├── implementation-orch.yaml
│   └── planning-orch.yaml
├── sub-agents/
│   ├── intent-triage.yaml
│   └── context-assembler.yaml
└── specialists/
    ├── python-implementer.yaml
    └── test-writer.yaml
```

### 2. Use Multi-Agent Files for Related Agents

Group related agents in one file:

```yaml
# orchestrators.yaml
agents:
  - role: definition-orch
    # ...
  - role: planning-orch
    # ...
  - role: implementation-orch
    # ...
```

### 3. Document Dependencies

Always list dependencies explicitly:

```yaml
dependencies:
  - context-assembler  # Provides project context
  - pattern-applier    # Identifies code patterns
```

### 4. Provide Examples

Include clear usage examples:

```yaml
examples:
  - "Classify 'Add OAuth2' as FEATURE, authentication, MEDIUM, P1"
  - "Triage 'Fix memory leak' as BUGFIX, performance, HIGH, P0"
```

### 5. Version Your Agents

Track versions in metadata:

```yaml
metadata:
  version: "1.2.3"
  changelog:
    - "1.2.3: Added complexity assessment"
    - "1.2.0: Added priority assignment"
    - "1.0.0: Initial release"
```

## Testing

Run the test suite:

```bash
# Run all loader tests
pytest agentpm/core/agents/test_loader.py -v

# Run specific test
pytest agentpm/core/agents/test_loader.py::TestAgentLoader::test_load_single_agent -v

# Run with coverage
pytest agentpm/core/agents/test_loader.py --cov=agentpm.core.agents.loader
```

## Troubleshooting

### Problem: "No project_id provided"

**Solution**: Initialize project first:
```bash
apm init "My Project"
```

### Problem: "Agent already exists"

**Solution**: Use `--force` to overwrite:
```bash
apm agents load --force
```

### Problem: "Invalid YAML format"

**Solution**: Validate YAML syntax:
```bash
# Check YAML is valid
python -c "import yaml; yaml.safe_load(open('agent.yaml'))"
```

### Problem: "Missing dependencies"

**Solution**: Either:
1. Add missing agent definition
2. Remove dependency from YAML
3. Load dependencies first

### Problem: "Validation failed"

**Solution**: Check error message for specific field issues:
```
Agent 1: Validation failed:
  tier: Tier must be one of {1, 2, 3}, got: 5
```

Fix the YAML field and retry.

## Performance

### Benchmarks

| Operation | Count | Time | Notes |
|-----------|-------|------|-------|
| Load single agent | 1 | ~50ms | Includes validation |
| Load directory | 10 | ~200ms | Parallel validation |
| Load directory | 50 | ~800ms | All agents validated first |
| Validate only | 50 | ~400ms | No database writes |

### Optimization Tips

1. **Batch Loading**: Load entire directories at once
2. **Validate First**: Use `--validate-only` to catch errors early
3. **Use Force Wisely**: Force mode updates all agents (slower)
4. **Pattern Matching**: Use specific patterns to reduce file scanning

## See Also

- [Agent Architecture](../../../docs/components/agents/architecture/three-tier-orchestration.md)
- [Agent Selection](./selection.py)
- [Agent Generation](../../cli/commands/agents/generate.py)
- [Agent Templates](../../templates/agents/)
