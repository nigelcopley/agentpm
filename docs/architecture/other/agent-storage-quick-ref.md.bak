# Agent Storage Architecture - Quick Reference

**Version**: 1.0.0
**Date**: 2025-10-17

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                      YAML DEFINITIONS                           │
│                   (Single Source of Truth)                      │
├─────────────────────────────────────────────────────────────────┤
│  orchestrators.yaml  │  sub-agents.yaml  │  specialists.yaml   │
│    6 mini-orchs      │    31 sub-agents  │    15 role types   │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT BUILDER API                          │
│                   (Database Synchronization)                    │
├─────────────────────────────────────────────────────────────────┤
│  create_orchestrator()  │  create_sub_agent()  │  sync_all()   │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (agents table)                    │
│                      (Runtime State)                            │
├─────────────────────────────────────────────────────────────────┤
│  id, role, tier, is_active, last_used_at, relationships        │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROVIDER GENERATORS                           │
│                  (Plugin-Based Generation)                      │
├──────────────────────┬──────────────────────────────────────────┤
│  ClaudeCodeGenerator │  GeminiGenerator  │  CursorGenerator    │
│  (Jinja2 templates)  │  (XML templates)  │  (Future)           │
└──────────────┬───────┴──────────┬────────────────┬─────────────┘
               │                  │                │
               ▼                  ▼                ▼
      .claude/agents/    .gemini/agents/    .cursor/agents/
      (Markdown files)   (XML files)        (Future)
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Definition Format** | YAML | Human-readable, version control friendly, declarative |
| **Template Engine** | Jinja2 | Flexible, powerful, widely known |
| **Source of Truth** | YAML + Database hybrid | YAML = definitions, Database = runtime state |
| **Provider Location** | `llms/{provider}/` | Consistent with existing plugin architecture |
| **Generation Trigger** | On-demand + staleness | Manual control + automatic when outdated |

---

## File Locations

### Core Definitions (Version Controlled)
```
agentpm/core/agents/definitions/
├─ orchestrators.yaml       # 6 mini-orchestrators
├─ sub-agents.yaml          # 31 sub-agents
├─ specialists.yaml         # 15 role templates
└─ schema.json             # JSON Schema validation
```

### Provider Plugins (Version Controlled)
```
agentpm/core/plugins/domains/llms/
├─ anthropic/claude-code/
│  ├─ generator.py
│  └─ templates/
│     ├─ orchestrator.md.j2
│     ├─ sub-agent.md.j2
│     └─ specialist.md.j2
│
├─ google/gemini/
│  ├─ generator.py
│  └─ templates/
│     └─ gemini-agent.xml.j2
│
└─ openai/codex/ (future)
```

### Generated Files (Ephemeral)
```
.claude/agents/              # Claude Code specific
├─ orchestrators/
│  └─ definition-orch.md
├─ sub-agents/
│  └─ intent-triage.md
└─ specialists/
   └─ implementer.md

.gemini/agents/              # Gemini specific (if detected)
└─ definition-orch.xml
```

---

## Data Flow

### 1. Initial Setup (One-Time)
```bash
# Export existing database agents to YAML
python scripts/migrate_agents_to_yaml.py

# Result: YAML definitions created from database
```

### 2. Normal Development (Edit → Sync → Generate)
```bash
# 1. Edit YAML definition
vim agentpm/core/agents/definitions/orchestrators.yaml

# 2. Sync to database
apm agents sync

# 3. Generate provider files (automatic, or manual)
apm agents generate
```

### 3. Provider-Specific Generation
```bash
# Auto-detect provider and generate
apm agents generate

# Or specify provider
apm agents generate --provider=gemini
apm agents generate --provider=claude-code
```

---

## CLI Commands

### Agent Synchronization
```bash
# Sync all: YAML → Database → Provider files
apm agents sync

# Force regeneration (even if not stale)
apm agents sync --force

# Dry-run (show what would change)
apm agents sync --dry-run
```

### Agent Generation
```bash
# Generate for detected provider
apm agents generate

# Generate for specific provider
apm agents generate --provider=claude-code
apm agents generate --provider=gemini

# Regenerate specific agent
apm agents generate --role=definition-orch
```

### Agent Validation
```bash
# Validate YAML definitions
apm agents validate

# List stale agents (need regeneration)
apm agents list --stale

# Show agent details
apm agents show definition-orch
```

### Agent Export/Import
```bash
# Export database to YAML
apm agents export --output=definitions/

# Import YAML to database
apm agents import --source=definitions/
```

---

## YAML Structure

### Orchestrator Example
```yaml
orchestrators:
  definition-orch:
    tier: 2
    orchestrator_type: mini
    display_name: "Definition Orchestrator"
    description: "Requirements & Scope Definition"
    phase: definition
    gate: D1

    sop_sections:
      role: "You are the Definition Orchestrator..."
      responsibilities: [list]
      delegates_to: [list of sub-agents]
      gate_requirements: {dict}
      output_artifact: "workitem.ready"

    tools:
      - name: context7
        phase: discovery
        priority: 1
        purpose: "Documentation research"

    metadata:
      execution_mode: parallel
      symbol_mode: enabled
      version: "1.0.0"
```

### Sub-Agent Example
```yaml
sub_agents:
  intent-triage:
    tier: 1
    display_name: "Intent Triage Agent"
    description: "Classify request type and scope"
    orchestrated_by: [definition-orch]

    sop_sections:
      role: "You are the Intent Triage sub-agent..."
      responsibilities: [list]
      inputs: "Raw user request"
      outputs: "Request classification"

    tools:
      - name: sequential-thinking
        phase: reasoning
        priority: 1

    metadata:
      version: "1.0.0"
```

---

## Provider Generator Interface

### Base Interface
```python
from abc import ABC, abstractmethod
from pathlib import Path

class AgentGenerator(ABC):
    """Base interface for provider-specific agent generators."""

    @abstractmethod
    def generate(self, definition: dict, db_agent: Agent) -> Path:
        """
        Generate provider-specific agent file.

        Args:
            definition: YAML definition (dict)
            db_agent: Database agent record

        Returns:
            Path to generated file
        """
        pass

    @abstractmethod
    def supports_tier(self, tier: int) -> bool:
        """Check if provider supports agent tier."""
        pass
```

### Claude Code Implementation
```python
class ClaudeCodeAgentGenerator(AgentGenerator):
    def generate(self, definition: dict, db_agent: Agent) -> Path:
        # Select template by tier
        template = self.get_template(db_agent.tier)

        # Render with Jinja2
        content = template.render(
            **definition,
            agent_id=db_agent.id,
            is_active=db_agent.is_active
        )

        # Write to .claude/agents/
        output_path = Path(".claude/agents") / f"{db_agent.tier_name}s" / f"{db_agent.role}.md"
        output_path.write_text(content)

        return output_path
```

---

## Validation

### YAML Schema Validation
```python
import jsonschema

# Validate orchestrators.yaml
with open("orchestrators.yaml") as f:
    data = yaml.safe_load(f)

schema = json.load(open("schema.json"))
jsonschema.validate(data, schema)
```

### Database Sync Validation
```python
# Check if database matches YAML
sync = AgentSynchronizer(db)
differences = sync.compare_yaml_to_database()

if differences:
    print(f"Found {len(differences)} differences")
    for diff in differences:
        print(f"  {diff.role}: {diff.change_type}")
```

---

## Migration Path

### Phase 1: Export Existing (Week 1)
```bash
# 1. Export database to YAML
python scripts/migrate_agents_to_yaml.py

# 2. Validate YAML
apm agents validate

# 3. Test sync (dry-run)
apm agents sync --dry-run

# 4. Sync to database
apm agents sync

# 5. Generate files
apm agents generate
```

### Phase 2: Dual System (Weeks 2-3)
- Keep old `.claude/agents/` files
- Generate new files alongside
- Compare outputs
- Fix any discrepancies

### Phase 3: Switch Over (Week 4+)
- Remove manual `.claude/agents/` files
- Use only generated files
- Update documentation

---

## Troubleshooting

### Issue: Generated file differs from manual file
**Solution**: Compare using diff, update YAML definition to match desired output

```bash
diff .claude/agents/orchestrators/definition-orch.md \
     .claude/agents/orchestrators/definition-orch.md.old
```

### Issue: YAML validation fails
**Solution**: Check against JSON Schema, fix YAML syntax

```bash
apm agents validate
# Error: orchestrators.definition-orch.tier must be integer (1, 2, or 3)
```

### Issue: Database out of sync with YAML
**Solution**: Run sync command

```bash
apm agents sync --force
```

### Issue: Provider not detected
**Solution**: Manually specify provider

```bash
apm agents generate --provider=claude-code
```

---

## Testing

### Unit Tests
```python
# tests/core/agents/test_sync.py
def test_yaml_to_database_sync():
    sync = AgentSynchronizer(db)
    sync.sync_all()
    assert db.agents.count() == 38

# tests/core/plugins/llms/test_claude_code_generator.py
def test_generate_orchestrator():
    generator = ClaudeCodeAgentGenerator()
    definition = load_yaml("definition-orch")
    db_agent = db.agents.get_by_role("definition-orch")
    output = generator.generate(definition, db_agent)
    assert output.exists()
```

### Integration Tests
```python
# tests/integration/test_agent_workflow.py
def test_full_workflow():
    # 1. Load YAML
    definitions = load_yaml_definitions()

    # 2. Sync to database
    sync.sync_all()

    # 3. Generate files
    generator.generate_all()

    # 4. Validate outputs
    assert all_agents_generated()
```

---

## Performance

### Expected Performance
- **YAML Load**: <100ms for all definitions
- **Database Sync**: <500ms for all agents
- **Generation**: <1s for all provider files
- **Validation**: <200ms for all YAML files

### Optimization Tips
- Cache parsed YAML definitions
- Batch database inserts
- Parallel file generation
- Use compiled Jinja2 templates

---

## Best Practices

### YAML Definitions
1. ✅ Use YAML anchors for repeated content
2. ✅ Keep descriptions concise (≤200 chars)
3. ✅ Use consistent naming (kebab-case for roles)
4. ✅ Document all custom fields in metadata
5. ✅ Version definitions (semantic versioning)

### Template Development
1. ✅ Keep templates provider-agnostic where possible
2. ✅ Use Jinja2 filters for formatting
3. ✅ Handle missing fields gracefully
4. ✅ Test with various definition structures
5. ✅ Document custom template variables

### Database Sync
1. ✅ Always validate YAML before sync
2. ✅ Use dry-run first for major changes
3. ✅ Back up database before sync
4. ✅ Monitor sync performance
5. ✅ Handle conflicts explicitly

---

## References

**Main Documentation**:
- [Complete Architecture Design](agent-storage-architecture.md)
- [Agent Builder API](../components/agents/agent-builder-api.md)
- [Plugin Development Guide](../components/plugins/developer-guide.md)

**Related Systems**:
- Database Schema: `agentpm/core/database/models/agent.py`
- Plugin Interface: `agentpm/core/plugins/base/plugin_interface.py`
- Existing Templates: `agentpm/templates/agents/`

**External Resources**:
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/templates/)
- [YAML 1.2 Specification](https://yaml.org/spec/1.2.2/)
- [JSON Schema Validation](https://json-schema.org/understanding-json-schema/)

---

**Last Updated**: 2025-10-17
**Version**: 1.0.0
**Status**: READY FOR USE
