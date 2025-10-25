# APM (Agent Project Manager) Agent System Documentation

**Version**: 2.0
**Status**: Production
**Last Updated**: 2025-10-19

---

## Overview

The APM (Agent Project Manager) agent system is a **database-driven, three-tier orchestration architecture** that generates and manages 84+ specialized AI agents for project development. Agents are organized into orchestrators, specialists, and utilities that collaborate to deliver features through structured workflows.

**Key Features**:
- ✅ Database-first architecture (agents are database records)
- ✅ Intelligent agent selection (context-driven, 5-15 agents per project)
- ✅ Template-based generation (Jinja2 + rule injection)
- ✅ Multi-provider support (Claude Code, Cursor, Gemini)
- ✅ Rule enforcement (project + universal rules embedded)
- ✅ 84 operational agents across 3 tiers

---

## Quick Navigation

### Architecture Documentation
- **[Three-Tier Orchestration](architecture/three-tier-orchestration.md)** - Master, phase, and sub-agent architecture
- **[Agent Selection Algorithm](architecture/agent-selection.md)** - Intelligent context-driven selection
- **[Generation Pipeline](architecture/generation-pipeline.md)** - Template-based agent creation
- **[Provider Generators](architecture/provider-generators.md)** - Multi-LLM provider support

### Implementation Guides
- **[Implementation Guide](guides/implementation-guide.md)** - Step-by-step agent development
- **[Agent Development Guide](guides/agent-development-guide.md)** - Create custom agents
- **[Provider Generator Guide](guides/provider-generator-guide.md)** - Add new LLM providers
- **[Template Customization](guides/template-customization.md)** - Customize agent templates

### Specifications
- **[Agent Format Specification](specifications/agent-format-spec.md)** - Agent file structure
- **[Template Reference](specifications/template-reference.md)** - Base template catalog
- **[Database Schema](specifications/database-schema.md)** - Agent table structure
- **[Rule Injection](specifications/rule-injection.md)** - Project rule embedding

### Examples
- **[Custom Agent Creation](examples/custom-agent-creation.md)** - End-to-end example
- **[Django Agent Setup](examples/django-agent-setup.md)** - Framework-specific agents
- **[Multi-Provider Project](examples/multi-provider-project.md)** - Claude + Cursor setup

---

## System Components

### 1. Agent Database (Source of Truth)

**Location**: `.aipm/data/aipm.db` → `agents` table
**Records**: 84 active agents
**Fields**:
- `role` - Unique identifier (e.g., `context-delivery`, `python-implementer`)
- `display_name` - Human-readable name
- `description` - Agent purpose and capabilities
- `agent_type` - orchestrator, specialist, utility, sub-agent
- `tier` - 1 (master), 2 (phase), 3 (execution)
- `capabilities` - JSON array of skills
- `sop_content` - Standard operating procedures
- `generated_at` - Last generation timestamp
- `file_path` - Path to generated .md file

**CLI Access**:
```bash
apm agents list                    # All agents
apm agents show context-delivery   # Agent details
apm agents validate                # Check agent integrity
```

### 2. Agent Generation System

**Core Components**:
- `agentpm/core/agents/generator.py` - Main generation logic
- `agentpm/core/agents/selection.py` - Intelligent selection
- `agentpm/providers/generators/` - Provider implementations

**Generation Flow**:
```
1. Project Analysis → Tech stack, frameworks, languages
2. Agent Selection → Context-driven (5-15 agents)
3. Template Loading → Base archetypes (implementer, tester, etc.)
4. Rule Injection → Project + universal rules
5. Provider Generation → Jinja2 rendering
6. File Writing → .claude/agents/*.md
7. Database Update → Mark as generated
```

**CLI Usage**:
```bash
# Generate all agents for project
apm agents generate --all

# Generate specific agent
apm agents generate --role context-delivery

# Dry run (preview without writing)
apm agents generate --all --dry-run

# Force regeneration
apm agents generate --all --force
```

### 3. Three-Tier Architecture

**Tier 1: Master Orchestrator**
- **Count**: 1 agent
- **Role**: Route work by phase and artifact type
- **File**: `.claude/agents/master-orchestrator.md`
- **Delegates to**: Phase orchestrators

**Tier 2: Phase Orchestrators**
- **Count**: 6 agents
- **Roles**:
  - `definition-orch` (D1 - Discovery)
  - `planning-orch` (P1 - Planning)
  - `implementation-orch` (I1 - Implementation)
  - `review-test-orch` (R1 - Review)
  - `release-ops-orch` (O1 - Operations)
  - `evolution-orch` (E1 - Evolution)
- **Files**: `.claude/agents/orchestrators/*.md`
- **Delegates to**: Sub-agents and specialists

**Tier 3: Execution Agents**
- **Sub-Agents** (36 agents): Single-purpose research/analysis
  - Examples: `context-delivery`, `ac-writer`, `test-runner`, `quality-gatekeeper`
- **Specialists** (40+ agents): Domain experts
  - Examples: `python-implementer`, `django-tester`, `react-frontend-implementer`
- **Utilities** (3 agents): Service agents
  - Examples: `evidence-writer`, `workflow-updater`, `decision-recorder`

**See**: [Three-Tier Orchestration](architecture/three-tier-orchestration.md) for details

### 4. Intelligent Agent Selection

**Algorithm**: Context-driven selection based on project characteristics

**Selection Criteria**:
1. **Universal Agents** (always included): `specifier`, `reviewer`, `planner`
2. **Language-Specific**: Python, TypeScript, JavaScript, Go, Rust, Java
3. **Framework-Specific**: Django, React, Flask, FastAPI, Vue, Angular, Next.js
4. **Project Type**: Web, API, Mobile, CLI
5. **Infrastructure**: CI/CD, deployment, monitoring

**Example** (Django + React project):
```python
# Input: project_context = {
#   'languages': ['Python', 'TypeScript'],
#   'frameworks': ['Django', 'React'],
#   'app_type': 'Web Application'
# }

# Output: 13 agents selected
- Universal: specifier, reviewer, planner (3)
- Python: python-implementer, python-tester, python-debugger (3)
- TypeScript: typescript-implementer, typescript-tester (2)
- Django: django-backend-implementer, django-api-integrator, django-tester (3)
- React: react-frontend-implementer, react-tester (2)
```

**See**: [Agent Selection Algorithm](architecture/agent-selection.md) for details

### 5. Provider Generator System

**Supported Providers**:
- ✅ **Claude Code** - Production (Anthropic Claude)
- 🚧 **Cursor** - Planned (Cursor IDE)
- 🚧 **Gemini** - Planned (Google Gemini)

**Provider Architecture**:
```
ProviderGenerator (ABC)
├── TemplateBasedGenerator (base class)
│   ├── Jinja2 environment
│   ├── Template rendering
│   └── Rule injection
└── Provider Implementations
    ├── ClaudeCodeGenerator (implemented)
    │   ├── Output: .claude/agents/*.md
    │   ├── Template: agent_file.md.j2
    │   └── Format: Markdown with frontmatter
    ├── CursorGenerator (planned)
    └── GeminiGenerator (planned)
```

**Adding a Provider**:
1. Create `agentpm/providers/generators/{provider}/`
2. Implement `{Provider}Generator(TemplateBasedGenerator)`
3. Create Jinja2 template: `templates/agent_file.md.j2`
4. Register in `agentpm/providers/generators/registry.py`

**See**: [Provider Generator Guide](guides/provider-generator-guide.md) for details

---

## Getting Started

### For Users (Project Setup)

**Step 1**: Initialize AIPM project
```bash
cd /path/to/project
apm init
```

**Step 2**: Generate agents based on project context
```bash
apm agents generate --all
```

**Step 3**: Verify agents generated
```bash
apm agents list
ls .claude/agents/
```

**Step 4**: Start using agents
```bash
# Context assembly (mandatory at session start)
apm context show --task-id=<id>

# Create work item
apm work-item create "Feature Name" --type=feature

# Let orchestrators handle the rest
# Master orchestrator routes to phase orchestrators
# Phase orchestrators delegate to specialists
```

### For Developers (Custom Agents)

**Step 1**: Understand three-tier architecture
- Read: [Three-Tier Orchestration](architecture/three-tier-orchestration.md)
- Read: [Agent Format Specification](specifications/agent-format-spec.md)

**Step 2**: Create agent definition in database

```python
from agentpm.core.database.models import Agent
from agentpm.core.database.methods import agents as agent_methods

agent = Agent(
    role='custom-specialist',
    display_name='Custom Specialist Agent',
    description='Specialized implementation for custom domain',
    agent_type='specialist',
    tier=3,
    capabilities=['custom-framework', 'domain-logic'],
    sop_content='# Custom Agent SOP\n\n...'
)

agent_methods.create_agent(db, agent)
```

**Step 3**: Generate agent file
```bash
apm agents generate --role custom-specialist
```

**Step 4**: Customize generated file
```bash
# Edit .claude/agents/custom-specialist.md
# Add domain-specific instructions
# Add examples and patterns
```

**See**: [Agent Development Guide](guides/agent-development-guide.md) for details

---

## Key Concepts

### Database-First Architecture

**Principle**: Agents are database records, NOT files

**Implications**:
- ✅ Agent metadata stored in database (`agents` table)
- ✅ Agent files generated on demand from database
- ✅ Database is source of truth (files are artifacts)
- ✅ Regeneration is safe (files are reproducible)
- ✅ Multi-provider support (same DB, different file formats)

**Workflow**:
```
Database → Provider Generator → Agent File
(source)   (renderer)           (artifact)
```

### Rule Injection

**Principle**: Project rules embedded into every agent file

**Rule Types**:
1. **Project Rules** - Project-specific governance
   - Queried from `rules` table WHERE `project_id = <id>` AND `enabled = 1`
   - Grouped by category: development_principles, testing, security, workflow
2. **Universal Rules** - Cross-project standards
   - Queried from `rules` table WHERE `project_id IS NULL` AND `enabled = 1`
   - Examples: CI-001 to CI-006

**Template Injection**:
```jinja2
## Project Rules

{% for category, rules in rules_by_category.items() %}
### {{ category|title }}

{% for rule in rules %}
**{{ rule.code }}**: {{ rule.title }}
- **Enforcement**: {{ rule.enforcement_level }}
- **Description**: {{ rule.description }}
{% endfor %}
{% endfor %}
```

**See**: [Rule Injection](specifications/rule-injection.md) for details

### Intelligent Selection

**Principle**: Generate only relevant agents for project context

**Benefits**:
- ✅ Faster onboarding (5-15 agents vs 84)
- ✅ Reduced complexity (fewer agents to understand)
- ✅ Better specialization (agents tailored to project)
- ✅ Lower token usage (less context per session)

**Selection Logic**:
```python
def select_agents(project_context):
    selected = []

    # 1. Universal (always)
    selected += ['specifier', 'reviewer', 'planner']

    # 2. Language-specific
    if 'Python' in languages:
        selected += ['python-implementer', 'python-tester', 'python-debugger']

    # 3. Framework-specific
    if 'Django' in frameworks:
        selected += ['django-backend-implementer', 'django-api-integrator', 'django-tester']

    # 4. Project-type specific
    if app_type == 'Web':
        selected += ['api-documenter']

    # 5. Infrastructure
    if has_cicd:
        selected += ['cicd-automator', 'deployment-specialist']

    return selected
```

**See**: [Agent Selection Algorithm](architecture/agent-selection.md) for details

---

## File Structure

### Project Layout
```
project/
├── .aipm/
│   └── data/
│       └── aipm.db              # Agent database (source of truth)
├── .claude/
│   └── agents/                  # Generated agent files
│       ├── master-orchestrator.md
│       ├── orchestrators/
│       │   ├── definition-orch.md
│       │   ├── planning-orch.md
│       │   ├── implementation-orch.md
│       │   ├── review-test-orch.md
│       │   ├── release-ops-orch.md
│       │   └── evolution-orch.md
│       ├── sub-agents/
│       │   ├── context-delivery.md
│       │   ├── ac-writer.md
│       │   ├── test-runner.md
│       │   └── ... (36 agents)
│       └── utilities/
│           ├── evidence-writer.md
│           ├── workflow-updater.md
│           └── decision-recorder.md
└── docs/
    └── components/
        └── agents/              # This documentation
```

### APM (Agent Project Manager) Codebase Structure
```
agentpm/
├── core/
│   └── agents/
│       ├── generator.py         # Main generation logic
│       ├── selection.py         # Intelligent selection
│       ├── loader.py            # Agent loading from database
│       └── templates/           # Base agent archetypes
│           ├── implementer.md
│           ├── tester.md
│           ├── planner.md
│           └── ... (18 templates)
├── providers/
│   └── generators/
│       ├── base.py              # Provider interface
│       ├── registry.py          # Provider registry
│       └── anthropic/
│           ├── claude_code_generator.py
│           └── templates/
│               └── agent_file.md.j2
├── cli/
│   └── commands/
│       └── agents/
│           ├── generate.py      # `apm agents generate`
│           ├── list.py          # `apm agents list`
│           ├── show.py          # `apm agents show`
│           └── validate.py      # `apm agents validate`
└── core/
    └── database/
        ├── models/
        │   └── agent.py         # Agent model
        └── methods/
            └── agents.py        # Agent CRUD operations
```

---

## Common Workflows

### Generate Agents for New Project

```bash
# 1. Initialize project
cd /path/to/new-project
apm init

# 2. Answer questionnaire (tech stack, frameworks, etc.)
# AIPM detects: Python, Django, React, PostgreSQL

# 3. Generate agents
apm agents generate --all

# Output:
# ✅ Generated 13 agents:
#   - Universal: specifier, reviewer, planner
#   - Python: python-implementer, python-tester, python-debugger
#   - Django: django-backend-implementer, django-api-integrator, django-tester
#   - React: react-frontend-implementer, react-tester
#   - API: api-documenter

# 4. Verify
apm agents list
ls .claude/agents/
```

### Regenerate Agents After Rule Changes

```bash
# 1. Update rules
apm rules update DP-001 --description "New time-boxing limit: 3 hours"

# 2. Regenerate all agents (embeds new rules)
apm agents generate --all --force

# 3. Verify rules embedded
cat .claude/agents/python-implementer.md | grep -A 5 "DP-001"
```

### Add Custom Agent

```bash
# 1. Create agent in database
apm agents create \
  --role custom-specialist \
  --name "Custom Specialist" \
  --description "Domain-specific implementation" \
  --type specialist \
  --tier 3

# 2. Generate agent file
apm agents generate --role custom-specialist

# 3. Customize
vim .claude/agents/custom-specialist.md

# 4. Validate
apm agents validate custom-specialist
```

### Debug Agent Generation

```bash
# Dry run (show what would be generated)
apm agents generate --all --dry-run

# Generate with verbose output
apm agents generate --all --verbose

# Check provider detection
apm agents generate --all --show-provider

# Validate database integrity
apm agents validate --all
```

---

## Testing

### Manual Verification

```bash
# 1. Check agent count
apm agents list | wc -l  # Should be 84+ (database) or 5-15 (project)

# 2. Verify generation
apm agents generate --role context-delivery
ls .claude/agents/sub-agents/context-delivery.md

# 3. Check rule injection
cat .claude/agents/python-implementer.md | grep "DP-001"

# 4. Validate structure
apm agents validate --all
```

### Automated Tests

```bash
# Run agent generation tests
pytest tests/cli/commands/test_agents_commands.py -v

# Run agent workflow tests
pytest tests/integration/test_agent_workflow.py -v

# Run full test suite
pytest tests/ -k agent
```

---

## Troubleshooting

### Agent Generation Fails

**Error**: "Could not detect LLM provider"
```bash
# Solution: Create .claude/agents/ directory
mkdir -p .claude/agents

# Or specify provider explicitly
apm agents generate --all --provider=claude-code
```

**Error**: "Agent database empty"
```bash
# Solution: Populate agents from definitions
apm init  # Re-run initialization

# Or manually load agents
apm agents load --from=agentpm/core/agents/definitions/
```

### Rules Not Embedded

**Symptom**: Agent files missing project rules
```bash
# Solution: Verify rules enabled
apm rules list

# Enable rules
apm rules enable DP-001 DP-002 CI-001

# Regenerate agents
apm agents generate --all --force
```

### Wrong Agents Generated

**Symptom**: Too many/too few agents
```bash
# Solution: Check project context
apm context show

# Update project metadata
apm project update --frameworks Django,React --languages Python,TypeScript

# Regenerate
apm agents generate --all --force
```

---

## Performance

### Generation Speed

**Mock Mode** (default): Instant (no API calls)
- Generates 5-15 agents in < 1 second
- Uses intelligent selection + template filling
- Recommended for development

**Real Claude Mode**: Slow (API calls)
- Generates 5-15 agents in ~30-60 seconds
- Uses Claude API for intelligent generation
- Recommended for production (higher quality)

**Usage**:
```bash
# Mock mode (fast)
apm agents generate --all

# Real Claude mode (slow, high quality)
apm agents generate --all --use-real-claude
```

### Token Usage

**Per Agent**: ~2-4KB (with rules embedded)
**Total Project** (13 agents): ~30-50KB
**With Universal Rules**: +10KB

**Optimization**:
- Use intelligent selection (5-15 agents vs 84)
- Enable only relevant rules
- Use mock mode for development

---

## Related Documentation

### Core Concepts
- [Three-Tier Orchestration](architecture/three-tier-orchestration.md)
- [Database-First Architecture](/docs/analysis/system-review/02-database-driven-architecture.md)
- [Workflow System](/docs/features/workflow/README.md)

### Developer Guides
- [Implementation Guide](guides/implementation-guide.md)
- [Agent Development Guide](guides/agent-development-guide.md)
- [Contributing to Agents](/docs/developer-guide/03-contributing.md)

### API Reference
- [Agent Generator API](specifications/agent-format-spec.md)
- [Provider Generator API](architecture/provider-generators.md)
- [Database Schema](specifications/database-schema.md)

---

**Version History**:
- v2.0 (2025-10-19): Database-first architecture, intelligent selection, multi-provider support
- v1.0 (2025-09-15): Initial three-tier architecture, template-based generation

**Maintainers**: AIPM Core Team
**License**: Proprietary
