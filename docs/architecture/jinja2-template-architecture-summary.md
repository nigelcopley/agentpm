# Jinja2 Template Architecture - Quick Reference

**Full Design**: [jinja2-template-architecture-design.md](./jinja2-template-architecture-design.md)

---

## Architecture Overview

```
Template Architecture (3-Layer)
├── Context Layer (Pydantic Models)
│   ├── TemplateContext (main)
│   ├── ProjectContext
│   ├── AgentContext
│   ├── RuleContext
│   └── ProviderConfig
│
├── Rendering Layer (Jinja2)
│   ├── TemplateRenderer (cached)
│   ├── Custom Filters
│   ├── Common Macros
│   └── Template Inheritance
│
└── Provider Layer (Output)
    ├── Claude Code (.claude/*)
    ├── Cursor (.cursor/*)
    └── OpenAI Codex (config.toml)
```

---

## Key Components

### 1. Template Context (Type-Safe)

```python
from agentpm.providers.base.context import TemplateContext

context = TemplateContext(
    project=ProjectContext(...),     # Project metadata
    agents=[AgentContext(...)],      # Agent definitions
    rules=[RuleContext(...)],        # Rule specifications
    provider=ProviderConfig(...),    # Provider config
)
```

**Benefits**:
- Pydantic validation before rendering
- Type hints throughout
- Clear contract between database and templates

### 2. Template Renderer (Cached)

```python
from agentpm.providers.base.renderer import TemplateRenderer

renderer = TemplateRenderer(
    template_dirs=[Path("templates/")],
    cache_size=128,                  # LRU cache
    auto_escape=True,                # Security
    strict_undefined=True            # Catch errors
)

result = renderer.render("template.j2", context)
```

**Benefits**:
- Compiled template caching (performance)
- Automatic escaping (security)
- Strict undefined variable checking (correctness)

### 3. Custom Filters

```python
# Usage in templates
{{ agents | flatten_agents }}                    # "orch, impl, tester"
{{ agents | filter_by_tier(2) }}                 # Tier 2 agents only
{{ rules | filter_rules(enforcement='BLOCK') }}  # Blocking rules
{{ config | to_toml }}                           # TOML format
{{ user_input | escape_shell }}                  # Shell-safe
```

**Categories**:
- **Agent Filters**: `flatten_agents`, `filter_by_tier`, `group_by_type`
- **Rule Filters**: `filter_rules`, `group_rules`, `format_rule`
- **Format Filters**: `to_toml`, `to_json`, `to_yaml`, `markdown_table`
- **Security Filters**: `escape_shell`, `escape_toml`, `sanitize_path`

### 4. Reusable Macros

```jinja2
{% import "common/macros/agents.j2" as agent_macros %}

{# Render full agent block #}
{{ agent_macros.agent_block(agent, include_sop=True) }}

{# Render just header #}
{{ agent_macros.agent_header(agent) }}
```

**Macro Libraries**:
- `agents.j2`: Agent formatting (header, delegation, capabilities)
- `rules.j2`: Rule formatting (block, table, grouped)
- `formatting.j2`: Common utilities (metadata, code blocks)

---

## Directory Structure

```
agentpm/providers/
├── base/                          # Shared infrastructure
│   ├── provider.py                # BaseProvider ABC
│   ├── renderer.py                # TemplateRenderer
│   └── context.py                 # Pydantic models
│
├── templates/
│   ├── common/                    # Shared templates
│   │   ├── base.j2                # Base template
│   │   └── macros/                # Reusable macros
│   │       ├── agents.j2
│   │       ├── rules.j2
│   │       └── formatting.j2
│   │
│   └── filters/                   # Custom filters
│       ├── agent_filters.py
│       ├── rule_filters.py
│       ├── format_filters.py
│       └── escape_filters.py
│
├── anthropic/                     # Claude Code provider
│   └── templates/
│       ├── claude_md.j2           # CLAUDE.md
│       ├── agent.j2               # Agent files
│       └── hooks/                 # Hook templates
│
├── cursor/                        # Cursor provider
│   └── templates/
│       ├── cursorrules.j2         # .cursorrules
│       ├── cursorignore.j2        # .cursorignore
│       └── rules/                 # Rule templates
│
└── openai/                        # OpenAI Codex provider
    └── templates/
        ├── agents_md.j2           # Agents format
        └── config.toml.j2         # Config file
```

---

## Quick Start

### Step 1: Create Template

```jinja2
{# templates/my_provider/config.j2 #}

{% extends "common/base.j2" %}
{% import "common/macros/agents.j2" as agent_macros %}

{% block content %}
# {{ project.name }}

## Agents
{% for agent in agents | filter_by_tier(2) %}
{{ agent_macros.agent_header(agent) }}
{% endfor %}

## Rules
{% for rule in rules | filter_rules(enforcement='BLOCK') %}
- {{ rule.rule_id }}: {{ rule.name }}
{% endfor %}
{% endblock %}
```

### Step 2: Create Context

```python
from agentpm.providers.base.context import (
    TemplateContext,
    ProjectContext,
    AgentContext,
    RuleContext,
    ProviderConfig,
)

context = TemplateContext(
    project=ProjectContext(
        id=1,
        name="My Project",
        path=Path("/path/to/project"),
        languages=["Python"],
    ),
    agents=[
        AgentContext(
            role="implementer",
            display_name="Implementation Specialist",
            description="Implements features",
            tier=2,
            agent_type="specialist",
        ),
    ],
    rules=[
        RuleContext(
            rule_id="DP-001",
            name="time-boxing",
            description="Limit tasks to 4 hours",
            category="development",
            enforcement_level="BLOCK",
            priority=100,
        ),
    ],
    provider=ProviderConfig(
        provider_name="my_provider",
        provider_version="1.0.0",
    ),
)
```

### Step 3: Render Template

```python
from agentpm.providers.base.renderer import TemplateRenderer

renderer = TemplateRenderer(
    template_dirs=[Path("templates/my_provider")],
)

result = renderer.render("config.j2", context)

if result.success:
    print(result.content)
    # Write to file
    output_path = Path("/path/to/project/.my_provider/config.md")
    output_path.write_text(result.content)
else:
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
```

---

## Testing Strategy

### Unit Tests (Filters)

```python
def test_flatten_agents():
    agents = [{'role': 'orch'}, {'role': 'impl'}]
    result = agent_filters.flatten_agents(agents)
    assert result == "orch, impl"
```

### Integration Tests (Templates)

```python
def test_render_template(renderer, sample_context):
    result = renderer.render("config.j2", sample_context)
    assert result.success
    assert "# My Project" in result.content
```

### End-to-End Tests (Providers)

```python
def test_provider_install(provider, project_path):
    success = provider.install(project_path)
    assert success
    assert (project_path / ".provider/config.md").exists()
```

---

## Security Features

### Input Validation
- Pydantic models validate all context data
- SQL injection prevention via parameterized queries
- Path traversal protection via `sanitize_path` filter

### Output Escaping
- Auto-escaping for HTML/XML templates
- Custom escape filters: `escape_shell`, `escape_toml`
- Security warnings for potential issues

### Template Safety
- Strict undefined variable checking
- No dynamic template loading
- No eval() or exec() in templates

---

## Performance Optimizations

### Caching
- **Compiled Templates**: `@lru_cache` with configurable size
- **Template Objects**: Cached after first compilation
- **Clear Cache**: `renderer.clear_cache()` for updates

### Lazy Loading
- Load only required data from database
- Use batch queries with joins
- Validate once at context creation

### Parallel Rendering
- Render independent templates in parallel
- Use `concurrent.futures` for multi-template rendering

---

## Migration Checklist

### Phase 1: Core Infrastructure
- [ ] Implement `TemplateContext` models (context.py)
- [ ] Implement `TemplateRenderer` class (renderer.py)
- [ ] Create common macros (templates/common/macros/)
- [ ] Implement custom filters (templates/filters/)

### Phase 2: Provider Templates
- [ ] Claude Code templates (anthropic/templates/)
- [ ] Cursor templates (cursor/templates/)
- [ ] OpenAI Codex templates (openai/templates/)

### Phase 3: Provider Integration
- [ ] Update `CursorProvider` to use renderer
- [ ] Create `ClaudeCodeProvider` with renderer
- [ ] Create `CodexProvider` with renderer

### Phase 4: Testing
- [ ] Unit tests for filters
- [ ] Integration tests for templates
- [ ] End-to-end provider tests

---

## Example: Complete Provider Implementation

```python
from pathlib import Path
from agentpm.providers.base.provider import BaseProvider
from agentpm.providers.base.context import TemplateContext, RenderResult

class MyProvider(BaseProvider):
    """Custom provider implementation"""

    def install(self, project_path: Path, config=None) -> bool:
        # Load context from database
        context = self._load_project_context(project_path)

        # Render all configs
        results = self.render_configs(context)

        # Write files
        for filename, result in results.items():
            if result.success:
                output_path = project_path / ".myprovider" / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(result.content)

        return all(r.success for r in results.values())

    def render_configs(self, context: TemplateContext) -> Dict[str, RenderResult]:
        return {
            "config.md": self.renderer.render("config.j2", context),
            "rules.md": self.renderer.render("rules.j2", context),
        }
```

---

## Common Patterns

### Pattern 1: Grouped Output

```jinja2
{% for category, group in rules | group_rules %}
## {{ category | title }}

{% for rule in group %}
- {{ rule.name }}: {{ rule.description }}
{% endfor %}
{% endfor %}
```

### Pattern 2: Conditional Rendering

```jinja2
{% if agents | filter_by_tier(3) %}
## Orchestrators
{% for agent in agents | filter_by_tier(3) %}
- {{ agent.display_name }}
{% endfor %}
{% endif %}
```

### Pattern 3: Table Generation

```jinja2
{{ agents | markdown_table(['role', 'tier', 'status']) }}
```

---

## Troubleshooting

### Issue: Template Not Found
**Solution**: Check `template_dirs` includes correct path

### Issue: Undefined Variable
**Solution**: Validate context has all required fields

### Issue: Security Warning
**Solution**: Use appropriate escape filter for output format

### Issue: Slow Rendering
**Solution**: Enable template caching, reduce context size

---

## Resources

- **Full Design**: [jinja2-template-architecture-design.md](./jinja2-template-architecture-design.md)
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Example Templates**: `agentpm/providers/*/templates/`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-27
