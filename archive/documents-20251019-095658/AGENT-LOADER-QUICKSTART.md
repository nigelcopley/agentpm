# Agent Loader Quick Start

Fast reference for loading agents into APM (Agent Project Manager).

## Basic Usage

```bash
# Load all agents from .claude/agents/
apm agents load

# Load specific file
apm agents load --file=my-agent.yaml

# Validate without loading (dry-run)
apm agents load --validate-only

# Force overwrite existing agents
apm agents load --force
```

## Minimal YAML Template

```yaml
role: my-agent
display_name: My Agent Name
description: What this agent does
tier: 1                    # 1=sub-agent, 2=specialist, 3=orchestrator
category: sub-agent        # sub-agent, specialist, orchestrator, utility, generic
sop_content: |
  You are the My Agent.

  ## Responsibilities
  - Do things
  - Return results

  ## Output Format
  ```yaml
  status: success
  result: "Task completed"
  ```
```

## Complete YAML Template

```yaml
role: complete-agent
display_name: Complete Agent
description: Demonstrates all fields
tier: 2
category: specialist
sop_content: |
  Complete SOP with responsibilities, tasks, and output format

capabilities:
  - capability_one
  - capability_two

tools:
  - Read
  - Write
  - Bash

dependencies:
  - other-agent

triggers:
  - when_to_invoke

examples:
  - "Example usage"

agent_type: implementer
is_active: true

metadata:
  version: "1.0.0"
  author: "Team"
```

## Multi-Agent File

```yaml
agents:
  - role: agent-one
    display_name: First Agent
    tier: 1
    # ... fields ...

  - role: agent-two
    display_name: Second Agent
    tier: 2
    # ... fields ...
```

## Required Fields

- `role` - Unique identifier (lowercase-with-hyphens)
- `display_name` - Human-readable name
- `description` - Agent purpose
- `tier` - 1, 2, or 3
- `category` - orchestrator, sub-agent, specialist, utility, generic
- `sop_content` - Standard Operating Procedure (markdown)

## Validation Rules

### Role
- Lowercase alphanumeric with hyphens/underscores
- Automatically converted to lowercase
- Must be unique

### Tier
- 1 = Sub-agent (research/analysis)
- 2 = Specialist (implementation)
- 3 = Orchestrator (coordination)

### Category
- `orchestrator` - Tier 3
- `sub-agent` - Tier 1
- `specialist` - Tier 2
- `utility` - Helper
- `generic` - General

## Common Errors

**Missing required fields**:
```
description: Field required
tier: Field required
```
→ Add missing fields to YAML

**Invalid tier**:
```
tier: Tier must be one of {1, 2, 3}, got: 5
```
→ Use 1, 2, or 3

**Agent already exists**:
```
Conflicts:
  my-agent:
    • Agent already exists
```
→ Use `--force` to overwrite

**Missing dependency**:
```
Warnings:
  • my-agent: Missing dependencies: other-agent
```
→ Add dependency or load it first

## Workflow

```bash
# 1. Create YAML file
cat > my-agent.yaml << 'EOF'
role: my-agent
display_name: My Agent
description: Does things
tier: 1
category: sub-agent
sop_content: "You are My Agent. Do things."
EOF

# 2. Validate
apm agents load --file=my-agent.yaml --validate-only

# 3. Load if valid
apm agents load --file=my-agent.yaml

# 4. Verify loaded
apm agents show my-agent
```

## Directory Structure

```
.claude/agents/
├── orchestrators/       # Tier 3 agents
│   └── my-orch.yaml
├── specialists/         # Tier 2 agents
│   └── my-specialist.yaml
└── sub-agents/          # Tier 1 agents
    └── my-subagent.yaml
```

## Python API

```python
from agentpm.core.agents.loader import AgentLoader
from pathlib import Path

# Initialize
loader = AgentLoader(db_service, project_id=1)

# Load
result = loader.load_from_yaml(
    Path("agent.yaml"),
    dry_run=False,
    force=False
)

# Check
if result.success:
    print(f"Loaded {result.loaded_count} agents")
else:
    for error in result.errors:
        print(error)
```

## Quick Tips

1. **Always validate first**: `--validate-only`
2. **Group related agents**: Use multi-agent YAML files
3. **Document dependencies**: List all required agents
4. **Provide examples**: Clear usage examples
5. **Version your agents**: Track changes in metadata

## See Also

- Full Guide: `docs/components/agents/agent-loader-guide.md`
- Examples: `examples/agents/`
- Tests: `agentpm/core/agents/test_loader.py`
- README: `agentpm/core/agents/README.md`
