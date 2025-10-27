"""
Example: Template Rendering

This example demonstrates how to render templates using the TemplateRenderer
with custom filters and macros.
"""

from pathlib import Path
from agentpm.providers.base.renderer import TemplateRenderer
from agentpm.providers.base.context import RenderResult

# Import sample context
from example_context import build_sample_context


def example_basic_rendering():
    """
    Example 1: Basic template rendering
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic Template Rendering")
    print("=" * 60)
    print()

    # Create renderer with template directory
    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    # Build context
    context = build_sample_context()

    # Render simple template
    simple_template = """
# {{ project.name }}

**Type**: {{ project.app_type }}
**Domain**: {{ project.business_domain }}

## Tech Stack
{% for tech in project.tech_stack %}
- {{ tech }}
{% endfor %}

## Agent Summary
Total Agents: {{ agents | length }}
    """

    result = renderer.render_string(simple_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_filters():
    """
    Example 2: Using custom filters
    """
    print("=" * 60)
    print("EXAMPLE 2: Custom Filters")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template using filters
    filter_template = """
# Agent Analysis

## All Agent Roles
{{ agents | flatten_agents }}

## Tier 2 Specialists
{% for agent in agents | filter_by_tier(2) %}
- **{{ agent.display_name }}** (`{{ agent.role }}`): {{ agent.description }}
{% endfor %}

## Agents by Type
{% for type, group in agents | group_by_type %}
### {{ type | title }}
{% for agent in group %}
- {{ agent.role }}
{% endfor %}
{% endfor %}

## Blocking Rules
{% for rule in rules | filter_rules(enforcement='BLOCK') %}
- **{{ rule.rule_id }}**: {{ rule.name }} (Priority: {{ rule.priority }})
{% endfor %}

## Rules by Category
{% for category, group in rules | group_rules %}
### {{ category | replace('_', ' ') | title }}
{% for rule in group %}
- {{ rule.name }}: {{ rule.description }}
{% endfor %}
{% endfor %}
    """

    result = renderer.render_string(filter_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_format_filters():
    """
    Example 3: Format conversion filters
    """
    print("=" * 60)
    print("EXAMPLE 3: Format Conversion")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template using format filters
    format_template = """
# Configuration Formats

## JSON Format
```json
{{ metadata | to_json(indent=2) }}
```

## Agent Table (Markdown)
{{ agents | markdown_table(['role', 'tier', 'agent_type']) }}

## Provider Config (TOML)
```toml
{{ provider | to_toml }}
```
    """

    result = renderer.render_string(format_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_security_filters():
    """
    Example 4: Security escaping filters
    """
    print("=" * 60)
    print("EXAMPLE 4: Security Filters")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template using security filters
    security_template = """
# Security Examples

## Shell Command (Safe)
```bash
cd {{ project.path | escape_shell }}
echo {{ project.name | escape_shell }}
```

## TOML Value (Safe)
```toml
project_name = "{{ project.name | escape_toml }}"
description = "{{ project.business_domain | escape_toml }}"
```

## Sanitized Path
Original: {{ project.path }}
Sanitized: {{ project.path | sanitize_path }}
    """

    result = renderer.render_string(security_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_macros():
    """
    Example 5: Using macros (if macro files exist)
    """
    print("=" * 60)
    print("EXAMPLE 5: Macros")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template using macros (inline for demonstration)
    macro_template = """
{% macro agent_summary(agent) %}
## {{ agent.display_name }}
- **Role**: `{{ agent.role }}`
- **Tier**: {{ agent.tier }}
- **Type**: {{ agent.agent_type }}
- **Status**: {% if agent.is_active %}Active{% else %}Inactive{% endif %}
{% if agent.capabilities %}
- **Capabilities**: {{ agent.capabilities | join(', ') }}
{% endif %}
{% endmacro %}

# Agent Details

{% for agent in agents | sort_agents('tier', reverse=True) %}
{{ agent_summary(agent) }}
{% endfor %}
    """

    result = renderer.render_string(macro_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_conditional_rendering():
    """
    Example 6: Conditional rendering based on context
    """
    print("=" * 60)
    print("EXAMPLE 6: Conditional Rendering")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template with conditionals
    conditional_template = """
# {{ project.name }} Configuration

{% if agents | filter_by_tier(3) %}
## Orchestration Layer
{% for agent in agents | filter_by_tier(3) %}
- {{ agent.display_name }}: {{ agent.description }}
{% endfor %}
{% endif %}

{% if agents | filter_by_tier(2) %}
## Specialist Layer
{% for agent in agents | filter_by_tier(2) %}
- {{ agent.display_name }}: {{ agent.description }}
{% endfor %}
{% endif %}

{% if agents | filter_by_tier(1) %}
## Sub-Agent Layer
{% for agent in agents | filter_by_tier(1) %}
- {{ agent.display_name }}: {{ agent.description }}
{% endfor %}
{% endif %}

{% if rules | filter_rules(enforcement='BLOCK') %}
## Critical Rules (MUST FOLLOW)
{% for rule in rules | filter_rules(enforcement='BLOCK') %}
- **{{ rule.rule_id }}**: {{ rule.name }}
  {{ rule.description }}
{% endfor %}
{% endif %}

{% if project.database %}
## Database Configuration
Database: {{ project.database }}
{% if 'PostgreSQL' in project.frameworks %}
Using PostgreSQL with Django ORM
{% endif %}
{% endif %}
    """

    result = renderer.render_string(conditional_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_error_handling():
    """
    Example 7: Error handling and validation
    """
    print("=" * 60)
    print("EXAMPLE 7: Error Handling")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
        strict_undefined=True,  # Raise error on undefined variables
    )

    context = build_sample_context()

    # Template with undefined variable (will error)
    error_template = """
# {{ project.name }}

This will fail: {{ undefined_variable }}
    """

    result = renderer.render_string(error_template, context)

    if result.success:
        print(result.content)
    else:
        print("Expected error occurred:")
        for error in result.errors:
            print(f"  - {error}")

    print()

    # Template with unrendered tags (validation error)
    validation_template = """
# {{ project.name }}

This has unrendered tags: {{ project.name
    """

    result = renderer.render_string(validation_template, context)

    if not result.success:
        print("Validation error occurred:")
        for error in result.errors:
            print(f"  - {error}")

    print()


def example_tests():
    """
    Example 8: Custom Jinja2 tests
    """
    print("=" * 60)
    print("EXAMPLE 8: Custom Tests")
    print("=" * 60)
    print()

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
    )

    context = build_sample_context()

    # Template using custom tests
    test_template = """
# Agent Analysis

## Orchestrators
{% for agent in agents %}
{% if agent is orchestrator %}
- {{ agent.display_name }} (manages {{ agent.delegates_to | length }} agents)
{% endif %}
{% endfor %}

## Specialists
{% for agent in agents %}
{% if agent is specialist %}
- {{ agent.display_name }} ({{ agent.capabilities | length }} capabilities)
{% endif %}
{% endfor %}

## Sub-Agents
{% for agent in agents %}
{% if agent is subagent %}
- {{ agent.display_name }}
{% endif %}
{% endfor %}

## Blocking Rules
{% for rule in rules %}
{% if rule is blocking_rule %}
- {{ rule.rule_id }}: {{ rule.name }} (Priority {{ rule.priority }})
{% endif %}
{% endfor %}
    """

    result = renderer.render_string(test_template, context)

    if result.success:
        print(result.content)
    else:
        print(f"Errors: {result.errors}")

    print()


def example_performance():
    """
    Example 9: Performance with caching
    """
    print("=" * 60)
    print("EXAMPLE 9: Template Caching Performance")
    print("=" * 60)
    print()

    import time

    renderer = TemplateRenderer(
        template_dirs=[Path(__file__).parent / "templates"],
        cache_size=128,  # Enable caching
    )

    context = build_sample_context()

    template_content = """
# {{ project.name }}

## Agents ({{ agents | length }})
{% for agent in agents %}
- {{ agent.role }}: {{ agent.display_name }}
{% endfor %}
    """

    # First render (compilation + rendering)
    start = time.time()
    result1 = renderer.render_string(template_content, context)
    time1 = time.time() - start

    # Second render (cached compilation, just rendering)
    start = time.time()
    result2 = renderer.render_string(template_content, context)
    time2 = time.time() - start

    print(f"First render (with compilation): {time1*1000:.2f}ms")
    print(f"Second render (cached): {time2*1000:.2f}ms")
    print(f"Speedup: {time1/time2:.1f}x faster")
    print()

    if result1.success:
        print("Rendered output:")
        print(result1.content)

    print()


def run_all_examples():
    """Run all examples"""
    example_basic_rendering()
    example_filters()
    example_format_filters()
    example_security_filters()
    example_macros()
    example_conditional_rendering()
    example_error_handling()
    example_tests()
    example_performance()


if __name__ == "__main__":
    run_all_examples()
