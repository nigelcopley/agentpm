# AIPM Agent Definitions

Comprehensive YAML definitions for all default agents in the AIPM system.

## Overview

This directory contains version-controlled YAML files defining all agents across the three-tier orchestration architecture:

- **Tier 3**: Orchestrators (6 agents) - Phase-specific workflow management
- **Tier 2**: Specialists (11 agents) - Domain-specific implementation
- **Tier 1**: Sub-Agents (~40 agents) - Single-purpose task execution
- **Tier 1**: Utilities (4 agents) - Infrastructure services
- **Tier 1**: Generic (9 agents) - Reusable cross-project utilities

**Total**: ~80 agent definitions

## File Structure

```
agentpm/agents/definitions/
├── README.md                    # This file
├── orchestrators.yaml           # 6 mini-orchestrators (Tier 3)
├── sub-agents.yaml              # ~40 single-purpose agents (Tier 1)
├── specialists.yaml             # 11 AIPM-specific specialists (Tier 2)
├── utilities.yaml               # 4 infrastructure agents (Tier 1)
└── generic.yaml                 # 9 generic utility agents (Tier 1)
```

## YAML Structure

Each agent definition follows this structure:

```yaml
agents:
  - role: agent-name                    # Unique identifier (kebab-case)
    display_name: Human Readable Name   # For UI display
    description: >                      # Brief description (1-2 sentences)
      What this agent does and when to use it
    tier: 1|2|3                         # Agent tier (1=sub, 2=specialist, 3=orch)
    category: orchestrator|sub-agent|specialist|utility|generic
    sop_content: |                      # Standard Operating Procedure (markdown)
      # Agent SOP

      ## Universal Rules (MANDATORY)
      All agents MUST follow UNIVERSAL-AGENT-RULES.md

      ## Purpose
      [Agent purpose and responsibilities]

      ## Input
      [Expected input format]

      ## Output
      [Output format and structure]

      ## Prohibited Actions
      - ❌ Never [forbidden action]

    capabilities: [python, database, testing]  # List of capabilities
    tools: [Read, Write, Bash, Grep]          # Tools available to agent
    dependencies: [other-agent-roles]          # Required agents
    triggers:                                  # Auto-activation triggers
      - "Trigger condition 1"
      - "Trigger condition 2"
    examples:                                  # Usage examples
      - "Example usage 1"
      - "Example usage 2"
```

## Agent Categories

### Orchestrators (orchestrators.yaml)
Phase-specific workflow orchestrators that drive quality gates:

1. **definition-orch**: Requirements & scope definition (Gate D1)
2. **planning-orch**: Work breakdown & planning (Gate P1)
3. **implementation-orch**: Code implementation & testing (Gate I1)
4. **review-test-orch**: Quality validation & testing (Gate R1)
5. **release-ops-orch**: Deployment & operations (Gate O1)
6. **evolution-orch**: Continuous improvement (Gate E1)

### Sub-Agents (sub-agents.yaml)
Single-purpose agents invoked by orchestrators:

**Context & Discovery**:
- context-delivery
- intent-triage
- context-assembler

**Requirements**:
- problem-framer
- value-articulator
- ac-writer
- risk-notary

**Gate Checks**:
- definition-gate-check
- planning-gate-check
- implementation-gate-check
- quality-gatekeeper
- operability-gatecheck
- evolution-gate-check

**Planning**:
- decomposer
- estimator
- dependency-mapper
- mitigation-planner
- backlog-curator

**Implementation**:
- pattern-applier
- code-implementer
- test-implementer
- migration-author
- doc-toucher

**Review & Test**:
- static-analyzer
- test-runner
- threat-screener
- ac-verifier

**Release & Ops**:
- versioner
- changelog-curator
- deploy-orchestrator
- health-verifier
- incident-scribe

**Evolution**:
- signal-harvester
- insight-synthesizer
- debt-registrar
- refactor-proposer
- sunset-planner

### Specialists (specialists.yaml)
AIPM-specific domain experts:

1. **aipm-python-cli-developer**: Click CLI development
2. **aipm-database-developer**: SQLite schema & migrations
3. **aipm-testing-specialist**: Pytest & coverage analysis
4. **aipm-quality-validator**: Code review & compliance
5. **aipm-documentation-specialist**: Technical writing
6. **aipm-plugin-developer**: Plugin system development
7. **aipm-frontend-developer**: Flask/HTMX web UI
8. **aipm-devops-specialist**: Deployment & operations
9. **aipm-requirements-specifier**: 6W framework & specs
10. **aipm-team-leader**: Team coordination & workflow
11. **aipm-development-orchestrator**: Work breakdown & sequencing
12. **aipm-owner**: Strategic oversight & compliance

### Utilities (utilities.yaml)
Infrastructure support agents:

1. **workitem-writer**: Database writes with validation
2. **evidence-writer**: Evidence storage & tracking
3. **audit-logger**: Immutable audit trail
4. **rule-validator**: Rule compliance checking

### Generic (generic.yaml)
Reusable cross-project utilities:

1. **context-generator**: Project context generation
2. **agent-builder**: Agent definition creation
3. **database-query-agent**: Safe database queries
4. **file-operations-agent**: Safe file operations
5. **workflow-coordinator**: Multi-step workflow coordination
6. **documentation-writer**: Documentation generation
7. **documentation-reader**: Documentation parsing
8. **web-research-agent**: Web research & extraction
9. **code-analyzer**: Code analysis & metrics

## Loading Agents into Database

### Python API

```python
from agentpm.agents.loader import load_agents_from_yaml

# Load all agents
agents = load_agents_from_yaml()

# Load specific category
orchestrators = load_agents_from_yaml(category='orchestrator')
specialists = load_agents_from_yaml(category='specialist')

# Register in database
from agentpm.core.database.methods.agents import create_agent

for agent_data in agents:
    create_agent(
        project_id=1,
        role=agent_data['role'],
        display_name=agent_data['display_name'],
        description=agent_data['description'],
        sop_content=agent_data['sop_content'],
        capabilities=agent_data['capabilities'],
        tier=agent_data['tier']
    )
```

### CLI Command (Future)

```bash
# Load all agents
apm agents load --all

# Load specific category
apm agents load --category orchestrator
apm agents load --category specialist

# Load specific file
apm agents load --file orchestrators.yaml

# Verify loaded agents
apm agents list
apm agents list --tier 3  # Orchestrators only
apm agents list --category specialist
```

## Agent Tier System

### Tier 3: Orchestrators
- **Purpose**: Phase-specific workflow management
- **Delegation**: Coordinate multiple sub-agents
- **Gates**: Enforce quality gates (D1, P1, I1, R1, O1, E1)
- **Count**: 6 agents
- **Examples**: definition-orch, planning-orch, implementation-orch

### Tier 2: Specialists
- **Purpose**: Domain-specific implementation
- **Expertise**: Deep knowledge in specific domain
- **Scope**: Complete feature implementation
- **Count**: ~15 agents
- **Examples**: aipm-python-cli-developer, aipm-database-developer

### Tier 1: Sub-Agents & Utilities
- **Purpose**: Single-responsibility task execution
- **Focus**: One specific operation
- **Invocation**: Called by orchestrators or specialists
- **Count**: ~50 agents
- **Examples**: ac-writer, test-runner, code-implementer

## Universal Agent Rules

**ALL agents MUST**:
1. Follow UNIVERSAL-AGENT-RULES.md
2. Include Universal Rules section in SOP
3. Define clear input/output formats
4. List prohibited actions
5. Specify capabilities and tools
6. Provide usage examples

## Quality Standards

### SOP Content
- **Markdown formatted**: Clear hierarchy with headers
- **Sections required**: Purpose, Responsibilities, Input, Output, Prohibited Actions
- **Examples included**: At least 1-2 usage examples
- **Validation**: Input/output formats clearly specified

### Capabilities
- **Accurate**: List only capabilities agent actually has
- **Specific**: Use concrete terms (not vague like "general programming")
- **Technology-specific**: Include relevant tech (python, pytest, flask)

### Dependencies
- **Explicit**: List all required agents
- **Minimal**: Only include truly required dependencies
- **Valid**: All dependencies must exist in agent definitions

## Validation

To validate agent definitions:

```python
from agentpm.agents.validator import validate_agent_definitions

# Validate all files
results = validate_agent_definitions()

for file, status in results.items():
    if status['valid']:
        print(f"✅ {file}: {status['agent_count']} agents validated")
    else:
        print(f"❌ {file}: Errors found")
        for error in status['errors']:
            print(f"   - {error}")
```

## Contributing

### Adding New Agents

1. **Choose correct file**:
   - Orchestrator → orchestrators.yaml
   - AIPM specialist → specialists.yaml
   - Single-purpose → sub-agents.yaml
   - Infrastructure → utilities.yaml
   - Generic utility → generic.yaml

2. **Follow YAML structure**: Use template above

3. **Include Universal Rules**: All SOPs must reference UNIVERSAL-AGENT-RULES.md

4. **Validate**: Run validator before committing

5. **Test**: Create test agent in database to verify

### Modifying Existing Agents

1. **Update YAML**: Edit agent definition in appropriate file

2. **Update version**: Change "Last Updated" date in file header

3. **Validate**: Ensure changes don't break structure

4. **Reload**: Update database agents if needed

## Version History

- **2025-10-18**: Initial comprehensive agent definitions
  - 6 orchestrators
  - ~40 sub-agents
  - 11 specialists
  - 4 utilities
  - 9 generic agents
  - Total: ~80 agent definitions

## See Also

- **Agent Database Schema**: `agentpm/core/database/models/agent.py`
- **Agent Methods**: `agentpm/core/database/methods/agents.py`
- **Universal Agent Rules**: `.claude/agents/UNIVERSAL-AGENT-RULES.md`
- **Three-Tier Architecture**: `docs/components/agents/architecture/`
- **Agent Selection Logic**: Database rules (`apm rules list -c agent_selection`) or `docs/agents/`

## License

Part of the APM (Agent Project Manager) project.
