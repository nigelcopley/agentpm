# Template Architecture Examples

This directory contains comprehensive examples demonstrating the Jinja2 template architecture for multi-provider configuration generation.

---

## Overview

The template architecture provides:
- **Type-safe contexts** using Pydantic validation
- **Reusable templates** with inheritance and macros
- **Custom filters** for data transformation
- **Security features** with automatic escaping
- **Performance optimization** through caching

---

## Example Files

### 1. `example_context.py`
**Building Template Contexts**

Demonstrates how to:
- Create `TemplateContext` with Pydantic validation
- Build project metadata (`ProjectContext`)
- Define agents (`AgentContext`) with 3-tier architecture
- Specify rules (`RuleContext`) with enforcement levels
- Configure providers (`ProviderConfig`)
- Handle validation errors

**Key Functions**:
```python
build_sample_context()              # Build complete example context
validate_context_example()          # Demonstrate Pydantic validation
cross_field_validation_example()    # Show relationship validation
```

**Run**:
```bash
cd examples/templates
python example_context.py
```

**Output**: Complete validated context with project, agents, and rules

---

### 2. `example_rendering.py`
**Template Rendering**

Demonstrates how to:
- Render templates with `TemplateRenderer`
- Use custom filters (agent, rule, format)
- Apply security escaping
- Use macros for reusability
- Handle conditional rendering
- Detect and report errors
- Leverage template caching

**Key Functions**:
```python
example_basic_rendering()        # Basic template usage
example_filters()                # Custom filter demonstrations
example_format_filters()         # Format conversion (JSON/TOML/YAML)
example_security_filters()       # Security escaping
example_macros()                 # Reusable macro patterns
example_conditional_rendering()  # Context-based conditionals
example_error_handling()         # Error detection and recovery
example_tests()                  # Custom Jinja2 tests
example_performance()            # Caching performance
```

**Run**:
```bash
cd examples/templates
python example_rendering.py
```

**Output**: Multiple rendered examples showing different features

---

### 3. `example_provider.py`
**Complete Provider Implementation**

Demonstrates how to:
- Implement `BaseProvider` interface
- Install/uninstall provider configurations
- Render provider-specific templates
- Verify installation integrity
- Handle database operations
- Recover from rendering errors

**Key Classes**:
```python
ExampleProvider                 # Complete provider implementation
```

**Key Functions**:
```python
example_usage()                 # Full provider lifecycle
example_custom_renderer()       # Direct renderer usage
example_error_recovery()        # Graceful error handling
```

**Run**:
```bash
cd examples/templates
python example_provider.py
```

**Output**: Provider installation/verification simulation

---

## Quick Start

### Step 1: Build Context

```python
from example_context import build_sample_context

# Create validated template context
context = build_sample_context()

print(f"Project: {context.project.name}")
print(f"Agents: {len(context.agents)}")
print(f"Rules: {len(context.rules)}")
```

### Step 2: Render Template

```python
from pathlib import Path
from agentpm.providers.base.renderer import TemplateRenderer

# Create renderer
renderer = TemplateRenderer(
    template_dirs=[Path("templates/")],
)

# Render from string
template = """
# {{ project.name }}

Agents: {{ agents | flatten_agents }}
"""

result = renderer.render_string(template, context)

if result.success:
    print(result.content)
```

### Step 3: Use Filters

```python
# In templates
{{ agents | filter_by_tier(2) }}              # Tier 2 agents
{{ rules | filter_rules(enforcement='BLOCK') }} # Blocking rules
{{ config | to_toml }}                        # TOML format
```

---

## Template Examples

### Basic Template

```jinja2
# {{ project.name }}

**Domain**: {{ project.business_domain }}
**Type**: {{ project.app_type }}

## Tech Stack
{% for tech in project.tech_stack %}
- {{ tech }}
{% endfor %}
```

### Using Filters

```jinja2
# Agent Summary

## All Roles
{{ agents | flatten_agents }}

## Specialists
{% for agent in agents | filter_by_tier(2) %}
- {{ agent.display_name }}: {{ agent.description }}
{% endfor %}

## Blocking Rules
{% for rule in rules | filter_rules(enforcement='BLOCK') %}
- **{{ rule.rule_id }}**: {{ rule.name }}
{% endfor %}
```

### Using Macros

```jinja2
{% macro agent_card(agent) %}
## {{ agent.display_name }}
- Role: `{{ agent.role }}`
- Tier: {{ agent.tier }}
- Type: {{ agent.agent_type }}
{% endmacro %}

# Agent Roster

{% for agent in agents %}
{{ agent_card(agent) }}
{% endfor %}
```

### Conditional Rendering

```jinja2
{% if agents | filter_by_tier(3) %}
## Orchestrators
{% for agent in agents | filter_by_tier(3) %}
- {{ agent.display_name }}
{% endfor %}
{% endif %}

{% if project.database %}
## Database
Using: {{ project.database }}
{% endif %}
```

---

## Custom Filters Reference

### Agent Filters

| Filter | Description | Usage |
|--------|-------------|-------|
| `flatten_agents` | Comma-separated roles | `{{ agents \| flatten_agents }}` |
| `filter_by_tier` | Filter by tier level | `{{ agents \| filter_by_tier(2) }}` |
| `group_by_type` | Group by agent_type | `{% for type, group in agents \| group_by_type %}` |
| `sort_agents` | Sort by field | `{{ agents \| sort_agents('tier') }}` |

### Rule Filters

| Filter | Description | Usage |
|--------|-------------|-------|
| `filter_rules` | Filter by criteria | `{{ rules \| filter_rules(enforcement='BLOCK') }}` |
| `group_rules` | Group by category | `{% for cat, group in rules \| group_rules %}` |
| `format_rule` | Format for display | `{{ rule \| format_rule('markdown') }}` |

### Format Filters

| Filter | Description | Usage |
|--------|-------------|-------|
| `to_toml` | Convert to TOML | `{{ config \| to_toml }}` |
| `to_json` | Convert to JSON | `{{ data \| to_json(indent=2) }}` |
| `to_yaml` | Convert to YAML | `{{ data \| to_yaml }}` |
| `markdown_table` | Create table | `{{ agents \| markdown_table(['role', 'tier']) }}` |

### Security Filters

| Filter | Description | Usage |
|--------|-------------|-------|
| `escape_shell` | Shell-safe escaping | `{{ path \| escape_shell }}` |
| `escape_toml` | TOML-safe escaping | `{{ value \| escape_toml }}` |
| `sanitize_path` | Path traversal protection | `{{ file_path \| sanitize_path }}` |
| `escape_markdown` | Markdown escaping | `{{ text \| escape_markdown }}` |

---

## Custom Tests Reference

| Test | Description | Usage |
|------|-------------|-------|
| `orchestrator` | Check if tier 3 | `{% if agent is orchestrator %}` |
| `specialist` | Check if tier 2 | `{% if agent is specialist %}` |
| `subagent` | Check if tier 1 | `{% if agent is subagent %}` |
| `blocking_rule` | Check if BLOCK enforcement | `{% if rule is blocking_rule %}` |

---

## Context Models

### TemplateContext

```python
TemplateContext(
    project: ProjectContext,       # Project metadata
    agents: List[AgentContext],    # Agent definitions
    rules: List[RuleContext],      # Rule specifications
    provider: ProviderConfig,      # Provider config
    metadata: Dict[str, Any],      # Additional metadata
    generated_at: datetime,        # Generation timestamp
)
```

### ProjectContext

```python
ProjectContext(
    id: int,
    name: str,
    path: Path,
    business_domain: str = "General software",
    app_type: str = "Application",
    languages: List[str] = [],
    frameworks: List[str] = [],
    database: Optional[str] = None,
    testing_frameworks: List[str] = [],
    methodology: str = "Agile",
    tech_stack: List[str] = [],
)
```

### AgentContext

```python
AgentContext(
    id: Optional[int] = None,
    role: str,                     # e.g., "orchestrator"
    display_name: str,
    description: str,
    tier: int,                     # 1, 2, or 3
    agent_type: str,               # e.g., "orchestrator"
    capabilities: List[str] = [],
    is_active: bool = True,
    reports_to: Optional[str] = None,
    delegates_to: List[str] = [],
    activation_triggers: List[str] = [],
    mcp_tools: Dict[str, List[Dict]] = {},
    parallel_capable: bool = False,
    metadata: Dict[str, Any] = {},
)
```

### RuleContext

```python
RuleContext(
    rule_id: str,                  # e.g., "DP-001"
    name: str,
    description: str,
    category: str,
    enforcement_level: EnforcementLevel,  # BLOCK/WARN/SUGGEST/LIMIT
    priority: int,                 # 0-100
    config: Dict[str, Any] = {},
    enabled: bool = True,
)
```

---

## Running All Examples

```bash
# Run all examples sequentially
cd examples/templates

echo "=== Example 1: Context Building ==="
python example_context.py

echo "\n=== Example 2: Template Rendering ==="
python example_rendering.py

echo "\n=== Example 3: Provider Implementation ==="
python example_provider.py
```

---

## Testing

### Unit Tests

Test individual filters:

```python
def test_flatten_agents():
    agents = [{'role': 'orch'}, {'role': 'impl'}]
    result = agent_filters.flatten_agents(agents)
    assert result == "orch, impl"
```

### Integration Tests

Test complete rendering:

```python
def test_render_template(renderer, context):
    result = renderer.render("template.j2", context)
    assert result.success
    assert "Expected content" in result.content
```

---

## Troubleshooting

### Issue: Module not found
**Solution**: Run from project root with proper PYTHONPATH

```bash
export PYTHONPATH=/path/to/AgentPM:$PYTHONPATH
python examples/templates/example_context.py
```

### Issue: Template not found
**Solution**: Check template_dirs path is correct

```python
template_dir = Path(__file__).parent / "templates"
renderer = TemplateRenderer(template_dirs=[template_dir])
```

### Issue: Undefined variable error
**Solution**: Validate context has all required fields

```python
context = TemplateContext(
    project=ProjectContext(...),
    agents=[...],  # Don't forget agents
    rules=[...],   # Don't forget rules
    provider=ProviderConfig(...),
)
```

---

## Next Steps

1. **Read the full design**: [jinja2-template-architecture-design.md](../../docs/architecture/jinja2-template-architecture-design.md)

2. **Study existing templates**: Check `agentpm/providers/cursor/templates/` for real examples

3. **Implement a provider**: Use `ExampleProvider` as a starting point

4. **Add custom filters**: Extend `agentpm/providers/templates/filters/`

5. **Create macros**: Add reusable templates to `agentpm/providers/templates/common/macros/`

---

## Resources

- **Full Architecture Design**: `docs/architecture/jinja2-template-architecture-design.md`
- **Quick Reference**: `docs/architecture/jinja2-template-architecture-summary.md`
- **Jinja2 Documentation**: https://jinja.palletsprojects.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Existing Templates**: `agentpm/providers/*/templates/`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-27
