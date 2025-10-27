# Jinja2 Template Architecture Design
## Multi-Provider Configuration Generation

**Author**: APM (Agent Project Manager) Architecture Team
**Version**: 1.0.0
**Date**: 2025-10-27
**Status**: Design Proposal

---

## 1. Executive Summary

This document defines a robust Jinja2 template architecture for generating provider-specific configurations from AGENTS.md and database sources. The architecture supports 3 primary providers (Claude Code, Cursor, OpenAI Codex) with extensibility for future providers.

**Key Goals**:
- Template reusability through inheritance and macros
- Type-safe context with Pydantic validation
- Secure rendering with injection prevention
- Performance through template caching
- Testability with isolated template testing

---

## 2. Directory Structure

```
agentpm/providers/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── provider.py              # BaseProvider abstract class
│   ├── renderer.py              # TemplateRenderer with caching
│   └── context.py               # TemplateContext models (Pydantic)
│
├── templates/
│   ├── common/
│   │   ├── base.j2              # Base template for all providers
│   │   ├── agents_md.j2         # AGENTS.md master template
│   │   └── macros/
│   │       ├── agents.j2        # Agent block formatting macros
│   │       ├── rules.j2         # Rule formatting macros
│   │       ├── formatting.j2    # Common formatting utilities
│   │       └── safety.j2        # Escaping and sanitization
│   │
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── agent_filters.py     # Agent transformation filters
│   │   ├── rule_filters.py      # Rule transformation filters
│   │   ├── format_filters.py    # Format conversion filters
│   │   └── escape_filters.py    # Security escaping filters
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_macros.py
│       └── test_filters.py
│
├── anthropic/
│   ├── __init__.py
│   ├── provider.py              # ClaudeCodeProvider
│   ├── formatter.py             # Claude-specific formatting
│   └── templates/
│       ├── claude_md.j2         # Main CLAUDE.md template
│       ├── agent.j2             # .claude/agents/*.md template
│       ├── settings.j2          # .claude/settings.json template
│       └── hooks/
│           ├── pre_tool_use.j2
│           └── session_start.j2
│
├── cursor/
│   ├── __init__.py
│   ├── provider.py              # CursorProvider
│   ├── formatter.py             # Cursor-specific formatting
│   └── templates/
│       ├── cursorrules.j2       # .cursorrules template
│       ├── cursorignore.j2      # .cursorignore template
│       ├── modes/
│       │   ├── agent_mode.j2
│       │   └── composer_mode.j2
│       └── rules/
│           ├── python_impl.mdc.j2
│           ├── testing.mdc.j2
│           └── database.mdc.j2
│
└── openai/
    ├── __init__.py
    ├── provider.py              # CodexProvider
    ├── formatter.py             # Codex-specific formatting
    └── templates/
        ├── agents_md.j2         # OpenAI agents format
        └── config.toml.j2       # Configuration file
```

---

## 3. Template Context Models (Pydantic)

### 3.1 Base Context Model

```python
"""
Template context models with Pydantic validation.

Location: agentpm/providers/base/context.py
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator, root_validator


class EnforcementLevel(str, Enum):
    """Rule enforcement levels"""
    BLOCK = "BLOCK"
    WARN = "WARN"
    SUGGEST = "SUGGEST"
    LIMIT = "LIMIT"


class RuleContext(BaseModel):
    """Rule data for template rendering"""
    rule_id: str = Field(..., pattern=r"^[A-Z]+-\d{3}$")
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    category: str
    enforcement_level: EnforcementLevel
    priority: int = Field(..., ge=0, le=100)
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

    class Config:
        frozen = False
        use_enum_values = True


class AgentContext(BaseModel):
    """Agent data for template rendering"""
    id: Optional[int] = None
    role: str = Field(..., pattern=r"^[a-z0-9-]+$")
    display_name: str = Field(..., min_length=1)
    description: str
    tier: int = Field(..., ge=1, le=3)
    agent_type: str
    capabilities: List[str] = Field(default_factory=list)
    is_active: bool = True
    reports_to: Optional[str] = None
    delegates_to: List[str] = Field(default_factory=list)
    activation_triggers: List[str] = Field(default_factory=list)
    mcp_tools: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)
    parallel_capable: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sop_content: Optional[str] = None
    file_path: Optional[str] = None

    @validator('tier')
    def validate_tier(cls, v):
        """Validate tier is 1 (sub-agent), 2 (specialist), or 3 (orchestrator)"""
        if v not in [1, 2, 3]:
            raise ValueError("Tier must be 1 (sub-agent), 2 (specialist), or 3 (orchestrator)")
        return v


class ProjectContext(BaseModel):
    """Project metadata for template rendering"""
    id: int
    name: str = Field(..., min_length=1)
    path: Path
    business_domain: str = "General software"
    app_type: str = "Application"
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    database: Optional[str] = None
    testing_frameworks: List[str] = Field(default_factory=list)
    methodology: str = "Agile"
    tech_stack: List[str] = Field(default_factory=list)

    @validator('path')
    def validate_path(cls, v):
        """Ensure path is absolute"""
        if not v.is_absolute():
            raise ValueError("Project path must be absolute")
        return v


class ProviderConfig(BaseModel):
    """Provider-specific configuration"""
    provider_name: str = Field(..., pattern=r"^[a-z_]+$")
    provider_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    features_enabled: Dict[str, bool] = Field(default_factory=dict)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class TemplateContext(BaseModel):
    """
    Complete context for template rendering.

    This is the main context object passed to all templates.
    Ensures type safety and validation before rendering.
    """
    project: ProjectContext
    agents: List[AgentContext] = Field(default_factory=list)
    rules: List[RuleContext] = Field(default_factory=list)
    provider: ProviderConfig
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @root_validator
    def validate_context(cls, values):
        """Validate cross-field constraints"""
        agents = values.get('agents', [])

        # Validate delegation relationships
        agent_roles = {agent.role for agent in agents}
        for agent in agents:
            if agent.reports_to and agent.reports_to not in agent_roles:
                raise ValueError(
                    f"Agent '{agent.role}' reports to unknown agent '{agent.reports_to}'"
                )
            for delegate in agent.delegates_to:
                if delegate not in agent_roles:
                    raise ValueError(
                        f"Agent '{agent.role}' delegates to unknown agent '{delegate}'"
                    )

        return values

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }


class RenderResult(BaseModel):
    """Result of template rendering"""
    success: bool
    content: Optional[str] = None
    file_path: Optional[Path] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 4. Template Renderer with Caching

### 4.1 Core Renderer Implementation

```python
"""
Template renderer with caching and security.

Location: agentpm/providers/base/renderer.py
"""

import hashlib
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Any, List, Callable

import jinja2
from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError,
)

from .context import TemplateContext, RenderResult


logger = logging.getLogger(__name__)


class TemplateRenderer:
    """
    Jinja2 template renderer with caching and security.

    Features:
    - Compiled template caching
    - Auto-escaping for security
    - Custom filters and macros
    - Validation before rendering
    - Detailed error reporting
    """

    def __init__(
        self,
        template_dirs: List[Path],
        cache_size: int = 128,
        auto_escape: bool = True,
        strict_undefined: bool = True
    ):
        """
        Initialize template renderer.

        Args:
            template_dirs: Directories to search for templates
            cache_size: Number of compiled templates to cache
            auto_escape: Enable automatic HTML/XML escaping
            strict_undefined: Raise error on undefined variables
        """
        self.template_dirs = [Path(d) for d in template_dirs]
        self.cache_size = cache_size

        # Validate template directories
        for template_dir in self.template_dirs:
            if not template_dir.exists():
                raise ValueError(f"Template directory not found: {template_dir}")

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader([str(d) for d in self.template_dirs]),
            autoescape=select_autoescape(
                enabled_extensions=['j2', 'jinja2', 'html', 'xml'],
                default_for_string=auto_escape,
            ),
            undefined=jinja2.StrictUndefined if strict_undefined else jinja2.Undefined,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        self._register_filters()

        # Register custom tests
        self._register_tests()

        # Cache for compiled templates
        self._template_cache: Dict[str, jinja2.Template] = {}

    def _register_filters(self):
        """Register custom Jinja2 filters"""
        from ..templates.filters import (
            agent_filters,
            rule_filters,
            format_filters,
            escape_filters,
        )

        # Agent filters
        self.env.filters['flatten_agents'] = agent_filters.flatten_agents
        self.env.filters['filter_by_tier'] = agent_filters.filter_by_tier
        self.env.filters['group_by_type'] = agent_filters.group_by_type
        self.env.filters['sort_agents'] = agent_filters.sort_agents

        # Rule filters
        self.env.filters['filter_rules'] = rule_filters.filter_rules
        self.env.filters['group_rules'] = rule_filters.group_rules
        self.env.filters['format_rule'] = rule_filters.format_rule

        # Format filters
        self.env.filters['to_toml'] = format_filters.to_toml
        self.env.filters['to_json'] = format_filters.to_json
        self.env.filters['to_yaml'] = format_filters.to_yaml
        self.env.filters['markdown_table'] = format_filters.markdown_table

        # Security filters
        self.env.filters['escape_shell'] = escape_filters.escape_shell
        self.env.filters['escape_toml'] = escape_filters.escape_toml
        self.env.filters['sanitize_path'] = escape_filters.sanitize_path

    def _register_tests(self):
        """Register custom Jinja2 tests"""
        self.env.tests['orchestrator'] = lambda agent: agent.tier == 3
        self.env.tests['specialist'] = lambda agent: agent.tier == 2
        self.env.tests['subagent'] = lambda agent: agent.tier == 1
        self.env.tests['blocking_rule'] = lambda rule: rule.enforcement_level == 'BLOCK'

    @lru_cache(maxsize=128)
    def _get_template(self, template_name: str) -> jinja2.Template:
        """
        Get compiled template with caching.

        Args:
            template_name: Template filename

        Returns:
            Compiled Jinja2 template

        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateSyntaxError: If template has syntax errors
        """
        try:
            return self.env.get_template(template_name)
        except TemplateNotFound as e:
            logger.error(f"Template not found: {template_name}")
            raise
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {template_name}: {e}")
            raise

    def render(
        self,
        template_name: str,
        context: TemplateContext,
        validate_output: bool = True
    ) -> RenderResult:
        """
        Render template with context.

        Args:
            template_name: Template filename
            context: Validated template context
            validate_output: Validate rendered output

        Returns:
            RenderResult with success status and content
        """
        errors: List[str] = []
        warnings: List[str] = []

        try:
            # Validate context (Pydantic validation)
            if not isinstance(context, TemplateContext):
                return RenderResult(
                    success=False,
                    errors=["Context must be TemplateContext instance"]
                )

            # Get compiled template
            template = self._get_template(template_name)

            # Render template
            content = template.render(context.dict())

            # Validate output
            if validate_output:
                validation_errors = self._validate_output(content, template_name)
                if validation_errors:
                    errors.extend(validation_errors)

            # Check for security issues
            security_warnings = self._check_security(content)
            if security_warnings:
                warnings.extend(security_warnings)

            return RenderResult(
                success=len(errors) == 0,
                content=content if len(errors) == 0 else None,
                errors=errors,
                warnings=warnings,
                metadata={
                    'template': template_name,
                    'size': len(content) if content else 0,
                    'generated_at': context.generated_at.isoformat(),
                }
            )

        except UndefinedError as e:
            logger.error(f"Undefined variable in template {template_name}: {e}")
            return RenderResult(
                success=False,
                errors=[f"Undefined variable: {str(e)}"]
            )
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}", exc_info=True)
            return RenderResult(
                success=False,
                errors=[f"Rendering failed: {str(e)}"]
            )

    def render_string(
        self,
        template_string: str,
        context: TemplateContext
    ) -> RenderResult:
        """
        Render template from string (for testing).

        Args:
            template_string: Template content as string
            context: Validated template context

        Returns:
            RenderResult with success status and content
        """
        try:
            template = self.env.from_string(template_string)
            content = template.render(context.dict())

            return RenderResult(
                success=True,
                content=content,
                metadata={'source': 'string'}
            )
        except Exception as e:
            return RenderResult(
                success=False,
                errors=[f"String rendering failed: {str(e)}"]
            )

    def _validate_output(self, content: str, template_name: str) -> List[str]:
        """
        Validate rendered output.

        Args:
            content: Rendered content
            template_name: Template filename

        Returns:
            List of validation errors
        """
        errors = []

        # Check for empty output
        if not content or content.strip() == "":
            errors.append("Rendered output is empty")

        # Check for unrendered variables
        if "{{" in content or "{%" in content:
            errors.append("Output contains unrendered Jinja2 tags")

        # Check for placeholder text
        if "[INSTRUCTION:" in content:
            errors.append("Output contains unresolved [INSTRUCTION] placeholders")

        return errors

    def _check_security(self, content: str) -> List[str]:
        """
        Check for potential security issues.

        Args:
            content: Rendered content

        Returns:
            List of security warnings
        """
        warnings = []

        # Check for potential shell injection
        dangerous_chars = ['`', '$(', '${']
        for char in dangerous_chars:
            if char in content:
                warnings.append(f"Potential shell injection risk: '{char}' found in output")

        # Check for hardcoded secrets (basic check)
        secret_patterns = ['password=', 'api_key=', 'secret=', 'token=']
        for pattern in secret_patterns:
            if pattern.lower() in content.lower():
                warnings.append(f"Potential secret exposure: '{pattern}' found in output")

        return warnings

    def clear_cache(self):
        """Clear template cache"""
        self._get_template.cache_clear()
        self._template_cache.clear()
```

---

## 5. Custom Filters

### 5.1 Agent Filters

```python
"""
Agent transformation filters.

Location: agentpm/providers/templates/filters/agent_filters.py
"""

from typing import List, Dict, Any


def flatten_agents(agents: List[Dict[str, Any]]) -> str:
    """
    Flatten agent list to comma-separated roles.

    Usage in template:
        {{ agents | flatten_agents }}

    Output:
        "orchestrator, implementer, tester"
    """
    return ", ".join(agent.get('role', '') for agent in agents)


def filter_by_tier(agents: List[Dict[str, Any]], tier: int) -> List[Dict[str, Any]]:
    """
    Filter agents by tier level.

    Usage in template:
        {% for agent in agents | filter_by_tier(1) %}

    Args:
        agents: List of agent dictionaries
        tier: Tier level (1=sub-agent, 2=specialist, 3=orchestrator)
    """
    return [agent for agent in agents if agent.get('tier') == tier]


def group_by_type(agents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group agents by agent_type.

    Usage in template:
        {% for type, group in agents | group_by_type %}

    Returns:
        Dictionary mapping agent_type to list of agents
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for agent in agents:
        agent_type = agent.get('agent_type', 'unknown')
        if agent_type not in groups:
            groups[agent_type] = []
        groups[agent_type].append(agent)
    return groups


def sort_agents(
    agents: List[Dict[str, Any]],
    key: str = 'role',
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort agents by specified key.

    Usage in template:
        {% for agent in agents | sort_agents('tier', reverse=True) %}
    """
    return sorted(agents, key=lambda a: a.get(key, ''), reverse=reverse)
```

### 5.2 Rule Filters

```python
"""
Rule transformation filters.

Location: agentpm/providers/templates/filters/rule_filters.py
"""

from typing import List, Dict, Any


def filter_rules(
    rules: List[Dict[str, Any]],
    category: str = None,
    enforcement: str = None
) -> List[Dict[str, Any]]:
    """
    Filter rules by category and/or enforcement level.

    Usage in template:
        {% for rule in rules | filter_rules(enforcement='BLOCK') %}
    """
    filtered = rules

    if category:
        filtered = [r for r in filtered if r.get('category') == category]

    if enforcement:
        filtered = [r for r in filtered if r.get('enforcement_level') == enforcement]

    return filtered


def group_rules(rules: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group rules by category.

    Usage in template:
        {% for category, group in rules | group_rules %}
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for rule in rules:
        category = rule.get('category', 'uncategorized')
        if category not in groups:
            groups[category] = []
        groups[category].append(rule)
    return groups


def format_rule(rule: Dict[str, Any], format: str = 'markdown') -> str:
    """
    Format rule for display.

    Usage in template:
        {{ rule | format_rule('markdown') }}

    Formats:
        - markdown: Markdown formatting
        - toml: TOML config format
        - json: JSON format
    """
    rule_id = rule.get('rule_id', 'UNKNOWN')
    name = rule.get('name', '')
    description = rule.get('description', '')
    enforcement = rule.get('enforcement_level', 'SUGGEST')

    if format == 'markdown':
        return f"**{rule_id}: {name}** ({enforcement})\n{description}"
    elif format == 'toml':
        return f'[rules.{rule_id}]\nname = "{name}"\nenforcement = "{enforcement}"\n'
    elif format == 'json':
        import json
        return json.dumps(rule, indent=2)
    else:
        return str(rule)
```

### 5.3 Format Filters

```python
"""
Format conversion filters.

Location: agentpm/providers/templates/filters/format_filters.py
"""

import json
from typing import Any, Dict, List


def to_toml(data: Dict[str, Any]) -> str:
    """
    Convert dictionary to TOML format.

    Usage in template:
        {{ config | to_toml }}
    """
    try:
        import toml
        return toml.dumps(data)
    except ImportError:
        # Fallback to simple key=value format
        lines = []
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            else:
                lines.append(f'{key} = {value}')
        return '\n'.join(lines)


def to_json(data: Any, indent: int = 2) -> str:
    """
    Convert data to JSON format.

    Usage in template:
        {{ metadata | to_json(indent=4) }}
    """
    return json.dumps(data, indent=indent, default=str)


def to_yaml(data: Any) -> str:
    """
    Convert data to YAML format.

    Usage in template:
        {{ config | to_yaml }}
    """
    try:
        import yaml
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    except ImportError:
        # Fallback to JSON
        return to_json(data)


def markdown_table(data: List[Dict[str, Any]], columns: List[str] = None) -> str:
    """
    Format list of dicts as markdown table.

    Usage in template:
        {{ agents | markdown_table(['role', 'tier', 'status']) }}
    """
    if not data:
        return ""

    if columns is None:
        columns = list(data[0].keys())

    # Header
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join([" --- " for _ in columns]) + "|"

    # Rows
    rows = []
    for item in data:
        row_values = [str(item.get(col, '')) for col in columns]
        rows.append("| " + " | ".join(row_values) + " |")

    return "\n".join([header, separator] + rows)
```

### 5.4 Security Filters

```python
"""
Security escaping filters.

Location: agentpm/providers/templates/filters/escape_filters.py
"""

import re
import shlex
from pathlib import Path
from typing import Any


def escape_shell(value: Any) -> str:
    """
    Escape value for safe shell usage.

    Usage in template:
        {{ user_input | escape_shell }}
    """
    return shlex.quote(str(value))


def escape_toml(value: str) -> str:
    """
    Escape string for TOML format.

    Usage in template:
        config_value = "{{ value | escape_toml }}"
    """
    # Escape backslashes and quotes
    return value.replace('\\', '\\\\').replace('"', '\\"')


def sanitize_path(value: str) -> str:
    """
    Sanitize path to prevent directory traversal.

    Usage in template:
        {{ file_path | sanitize_path }}
    """
    # Remove dangerous path components
    path = Path(value)
    parts = [p for p in path.parts if p not in ['.', '..', '~']]

    # Reconstruct safe path
    safe_path = Path(*parts) if parts else Path('.')

    # Ensure no absolute paths unless intended
    if path.is_absolute():
        return str(safe_path)
    else:
        return str(safe_path.relative_to(Path('.')))


def escape_markdown(value: str) -> str:
    """
    Escape markdown special characters.

    Usage in template:
        {{ description | escape_markdown }}
    """
    special_chars = ['*', '_', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    result = value
    for char in special_chars:
        result = result.replace(char, '\\' + char)
    return result
```

---

## 6. Common Macros

### 6.1 Agent Macros

```jinja2
{# agentpm/providers/templates/common/macros/agents.j2 #}

{# Render agent header section #}
{% macro agent_header(agent) %}
# {{ agent.display_name }}

**Role**: `{{ agent.role }}`
**Tier**: {{ agent.tier }} ({% if agent.tier == 1 %}Sub-Agent{% elif agent.tier == 2 %}Specialist{% else %}Orchestrator{% endif %})
**Status**: {% if agent.is_active %}✅ Active{% else %}⏸️ Inactive{% endif %}
**Type**: {{ agent.agent_type }}

---
{% endmacro %}


{# Render delegation section #}
{% macro agent_delegation(agent) %}
## Delegation

{% if agent.reports_to %}
**Reports To**: `{{ agent.reports_to }}`
{% endif %}

{% if agent.delegates_to %}
**Delegates To**:
{% for delegate in agent.delegates_to %}
- `{{ delegate }}`
{% endfor %}
{% else %}
**Delegates To**: None (terminal execution)
{% endif %}
{% endmacro %}


{# Render capabilities list #}
{% macro agent_capabilities(agent) %}
## Capabilities

{% if agent.capabilities %}
{% for capability in agent.capabilities %}
- {{ capability }}
{% endfor %}
{% else %}
No specific capabilities listed.
{% endif %}
{% endmacro %}


{# Render activation triggers #}
{% macro agent_triggers(agent) %}
## Activation Triggers

{% if agent.activation_triggers %}
{% for trigger in agent.activation_triggers %}
- {{ trigger }}
{% endfor %}
{% else %}
- Explicit delegation via Task tool
{% endif %}
{% endmacro %}


{# Render full agent block #}
{% macro agent_block(agent, include_sop=False) %}
{{ agent_header(agent) }}

{{ agent_triggers(agent) }}

{{ agent_delegation(agent) }}

{{ agent_capabilities(agent) }}

{% if include_sop and agent.sop_content %}
## Standard Operating Procedure

{{ agent.sop_content }}
{% endif %}
{% endmacro %}
```

### 6.2 Rule Macros

```jinja2
{# agentpm/providers/templates/common/macros/rules.j2 #}

{# Render single rule #}
{% macro rule_block(rule) %}
### {{ rule.rule_id }}: {{ rule.name }}

**Enforcement**: {{ rule.enforcement_level }}
**Category**: {{ rule.category }}
**Priority**: {{ rule.priority }}

{{ rule.description }}

{% if rule.config %}
**Configuration**:
```json
{{ rule.config | to_json }}
```
{% endif %}
{% endmacro %}


{# Render rules grouped by category #}
{% macro rules_by_category(rules) %}
{% for category, group in rules | group_rules %}
## {{ category | title }}

{% for rule in group %}
{{ rule_block(rule) }}
{% endfor %}
{% endfor %}
{% endmacro %}


{# Render blocking rules only #}
{% macro blocking_rules(rules) %}
## Blocking Rules (MUST FOLLOW)

{% for rule in rules | filter_rules(enforcement='BLOCK') %}
{{ rule_block(rule) }}
{% endfor %}
{% endmacro %}


{# Render rules table #}
{% macro rules_table(rules, columns=['rule_id', 'name', 'enforcement_level']) %}
{{ rules | markdown_table(columns) }}
{% endmacro %}
```

### 6.3 Formatting Macros

```jinja2
{# agentpm/providers/templates/common/macros/formatting.j2 #}

{# Render metadata section #}
{% macro metadata_section(metadata, title='Metadata') %}
## {{ title }}

{% for key, value in metadata.items() %}
- **{{ key | replace('_', ' ') | title }}**: {{ value }}
{% endfor %}
{% endmacro %}


{# Render code block with language #}
{% macro code_block(content, language='') %}
```{{ language }}
{{ content }}
```
{% endmacro %}


{# Render collapsible section #}
{% macro collapsible(title, content, open=False) %}
<details{% if open %} open{% endif %}>
<summary>{{ title }}</summary>

{{ content }}

</details>
{% endmacro %}


{# Render timestamp #}
{% macro timestamp(dt, format='iso') %}
{% if format == 'iso' %}
{{ dt.isoformat() }}
{% elif format == 'human' %}
{{ dt.strftime('%Y-%m-%d %H:%M:%S') }}
{% else %}
{{ dt }}
{% endif %}
{% endmacro %}
```

---

## 7. Provider Templates

### 7.1 Claude Code Templates

#### Main CLAUDE.md Template

```jinja2
{# agentpm/providers/anthropic/templates/claude_md.j2 #}

{% extends "common/base.j2" %}
{% import "common/macros/agents.j2" as agent_macros %}
{% import "common/macros/rules.j2" as rule_macros %}

{% block header %}
# CLAUDE.md - {{ project.name }}

> **Generated by APM (Agent Project Manager)**
> **Date**: {{ generated_at | timestamp('human') }}
> **Version**: {{ provider.provider_version }}
{% endblock %}

{% block content %}
## Project Overview

**Domain**: {{ project.business_domain }}
**Type**: {{ project.app_type }}
**Tech Stack**: {{ project.tech_stack | join(', ') }}

---

## Agents

### Orchestrators (Tier 3)
{% for agent in agents | filter_by_tier(3) %}
{{ agent_macros.agent_block(agent) }}
{% endfor %}

### Specialists (Tier 2)
{% for agent in agents | filter_by_tier(2) %}
{{ agent_macros.agent_block(agent) }}
{% endfor %}

### Sub-Agents (Tier 1)
{% for agent in agents | filter_by_tier(1) %}
{{ agent_macros.agent_block(agent) }}
{% endfor %}

---

## Rules

{{ rule_macros.blocking_rules(rules) }}

{{ rule_macros.rules_by_category(rules | filter_rules(enforcement='WARN')) }}

---

## Quick Commands

```bash
# Work item management
apm work-item create "Feature name"
apm work-item list
apm work-item show <id>

# Task management
apm task create <work-item-id> "Task name"
apm task next <id>

# Agent operations
apm agents list
apm context show
```

{% endblock %}
```

#### Individual Agent Template

```jinja2
{# agentpm/providers/anthropic/templates/agent.j2 #}

{% import "common/macros/agents.j2" as agent_macros %}
{% import "common/macros/rules.j2" as rule_macros %}

---
name: {{ agent.role }}
description: {{ agent.description }}
tools: Read, Grep, Glob, Write, Edit, Bash
---

{{ agent_macros.agent_block(agent, include_sop=True) }}

---

## Project Rules

{{ rule_macros.blocking_rules(rules) }}

---

**Generated**: {{ generated_at | timestamp('iso') }}
**File Path**: `{{ agent.file_path }}`
```

### 7.2 Cursor Templates

#### Main .cursorrules Template

```jinja2
{# agentpm/providers/cursor/templates/cursorrules.j2 #}

# Cursor Rules for {{ project.name }}

Generated by APM (Agent Project Manager) on {{ generated_at | timestamp('human') }}

---

## Project Context

- **Domain**: {{ project.business_domain }}
- **Languages**: {{ project.languages | join(', ') }}
- **Frameworks**: {{ project.frameworks | join(', ') }}
- **Database**: {{ project.database or 'N/A' }}

---

## Blocking Rules (MUST FOLLOW)

{% for rule in rules | filter_rules(enforcement='BLOCK') %}
### {{ rule.rule_id }}: {{ rule.name }}

{{ rule.description }}

{% if rule.config %}
Configuration:
{{ rule.config | to_json }}
{% endif %}

---
{% endfor %}

## Recommended Practices

{% for rule in rules | filter_rules(enforcement='SUGGEST') %}
- **{{ rule.name }}**: {{ rule.description }}
{% endfor %}

---

## Agent Roster

{% for agent in agents | sort_agents('tier', reverse=True) %}
- `{{ agent.role }}` (Tier {{ agent.tier }}): {{ agent.description }}
{% endfor %}
```

### 7.3 OpenAI Codex Templates

#### Configuration TOML Template

```jinja2
{# agentpm/providers/openai/templates/config.toml.j2 #}

# OpenAI Codex Configuration
# Generated: {{ generated_at | timestamp('iso') }}

[project]
name = "{{ project.name | escape_toml }}"
type = "{{ project.app_type | escape_toml }}"
domain = "{{ project.business_domain | escape_toml }}"

[project.tech_stack]
languages = [{{ project.languages | map('escape_toml') | map('quote') | join(', ') }}]
frameworks = [{{ project.frameworks | map('escape_toml') | map('quote') | join(', ') }}]
database = "{{ project.database or 'none' | escape_toml }}"

{% for agent in agents %}
[[agents]]
role = "{{ agent.role | escape_toml }}"
name = "{{ agent.display_name | escape_toml }}"
tier = {{ agent.tier }}
type = "{{ agent.agent_type | escape_toml }}"
active = {{ agent.is_active | lower }}
capabilities = [{{ agent.capabilities | map('escape_toml') | map('quote') | join(', ') }}]
{% endfor %}

{% for category, group in rules | group_rules %}
[rules.{{ category }}]
{% for rule in group %}
[rules.{{ category }}.{{ rule.rule_id }}]
name = "{{ rule.name | escape_toml }}"
description = "{{ rule.description | escape_toml }}"
enforcement = "{{ rule.enforcement_level | escape_toml }}"
priority = {{ rule.priority }}
{% endfor %}
{% endfor %}
```

---

## 8. Testing Strategy

### 8.1 Unit Tests for Filters

```python
"""
Unit tests for custom Jinja2 filters.

Location: agentpm/providers/templates/tests/test_filters.py
"""

import pytest
from agentpm.providers.templates.filters import agent_filters, rule_filters


class TestAgentFilters:
    """Test agent transformation filters"""

    def test_flatten_agents(self):
        """Test flattening agent list to roles"""
        agents = [
            {'role': 'orchestrator'},
            {'role': 'implementer'},
            {'role': 'tester'},
        ]

        result = agent_filters.flatten_agents(agents)

        assert result == "orchestrator, implementer, tester"

    def test_filter_by_tier(self):
        """Test filtering agents by tier"""
        agents = [
            {'role': 'orchestrator', 'tier': 3},
            {'role': 'implementer', 'tier': 2},
            {'role': 'analyzer', 'tier': 1},
        ]

        tier_2_agents = agent_filters.filter_by_tier(agents, 2)

        assert len(tier_2_agents) == 1
        assert tier_2_agents[0]['role'] == 'implementer'

    def test_group_by_type(self):
        """Test grouping agents by type"""
        agents = [
            {'role': 'impl-1', 'agent_type': 'implementer'},
            {'role': 'impl-2', 'agent_type': 'implementer'},
            {'role': 'test-1', 'agent_type': 'tester'},
        ]

        groups = agent_filters.group_by_type(agents)

        assert 'implementer' in groups
        assert 'tester' in groups
        assert len(groups['implementer']) == 2
        assert len(groups['tester']) == 1


class TestRuleFilters:
    """Test rule transformation filters"""

    def test_filter_rules_by_enforcement(self):
        """Test filtering rules by enforcement level"""
        rules = [
            {'rule_id': 'R1', 'enforcement_level': 'BLOCK'},
            {'rule_id': 'R2', 'enforcement_level': 'WARN'},
            {'rule_id': 'R3', 'enforcement_level': 'BLOCK'},
        ]

        blocking = rule_filters.filter_rules(rules, enforcement='BLOCK')

        assert len(blocking) == 2
        assert all(r['enforcement_level'] == 'BLOCK' for r in blocking)

    def test_format_rule_markdown(self):
        """Test formatting rule as markdown"""
        rule = {
            'rule_id': 'DP-001',
            'name': 'time-boxing',
            'description': 'Limit implementation tasks to 4 hours',
            'enforcement_level': 'BLOCK'
        }

        result = rule_filters.format_rule(rule, 'markdown')

        assert '**DP-001: time-boxing**' in result
        assert '(BLOCK)' in result
        assert 'Limit implementation tasks' in result
```

### 8.2 Integration Tests for Templates

```python
"""
Integration tests for template rendering.

Location: agentpm/providers/templates/tests/test_templates.py
"""

import pytest
from pathlib import Path
from datetime import datetime

from agentpm.providers.base.renderer import TemplateRenderer
from agentpm.providers.base.context import (
    TemplateContext,
    ProjectContext,
    AgentContext,
    RuleContext,
    ProviderConfig,
    EnforcementLevel,
)


@pytest.fixture
def template_dirs(tmp_path):
    """Create temporary template directories"""
    common_dir = tmp_path / "common"
    common_dir.mkdir()

    macros_dir = common_dir / "macros"
    macros_dir.mkdir()

    return [tmp_path]


@pytest.fixture
def sample_context():
    """Create sample template context"""
    return TemplateContext(
        project=ProjectContext(
            id=1,
            name="Test Project",
            path=Path("/tmp/test"),
            languages=["Python"],
            frameworks=["Django"],
        ),
        agents=[
            AgentContext(
                role="orchestrator",
                display_name="Master Orchestrator",
                description="Main coordinator",
                tier=3,
                agent_type="orchestrator",
                is_active=True,
            ),
        ],
        rules=[
            RuleContext(
                rule_id="DP-001",
                name="time-boxing",
                description="Limit tasks to 4 hours",
                category="development",
                enforcement_level=EnforcementLevel.BLOCK,
                priority=100,
            ),
        ],
        provider=ProviderConfig(
            provider_name="anthropic",
            provider_version="1.0.0",
        ),
    )


class TestTemplateRenderer:
    """Test template renderer"""

    def test_render_simple_template(self, template_dirs, sample_context):
        """Test rendering simple template"""
        # Create simple template
        template_file = template_dirs[0] / "simple.j2"
        template_file.write_text("# {{ project.name }}\n")

        renderer = TemplateRenderer(template_dirs)
        result = renderer.render("simple.j2", sample_context)

        assert result.success
        assert "# Test Project" in result.content

    def test_render_with_filters(self, template_dirs, sample_context):
        """Test rendering with custom filters"""
        template_file = template_dirs[0] / "filters.j2"
        template_file.write_text("Agents: {{ agents | flatten_agents }}\n")

        renderer = TemplateRenderer(template_dirs)
        result = renderer.render("filters.j2", sample_context)

        assert result.success
        assert "orchestrator" in result.content

    def test_render_with_macros(self, template_dirs, sample_context):
        """Test rendering with macros"""
        # Create macro file
        macros_dir = template_dirs[0] / "macros"
        macros_dir.mkdir()

        macro_file = macros_dir / "test.j2"
        macro_file.write_text("""
{% macro header(title) %}
# {{ title }}
---
{% endmacro %}
        """)

        # Create template using macro
        template_file = template_dirs[0] / "with_macro.j2"
        template_file.write_text("""
{% import "macros/test.j2" as test_macros %}
{{ test_macros.header(project.name) }}
        """)

        renderer = TemplateRenderer(template_dirs)
        result = renderer.render("with_macro.j2", sample_context)

        assert result.success
        assert "# Test Project" in result.content

    def test_render_undefined_variable(self, template_dirs, sample_context):
        """Test error handling for undefined variables"""
        template_file = template_dirs[0] / "undefined.j2"
        template_file.write_text("{{ undefined_var }}\n")

        renderer = TemplateRenderer(template_dirs)
        result = renderer.render("undefined.j2", sample_context)

        assert not result.success
        assert "Undefined variable" in result.errors[0]

    def test_security_warnings(self, template_dirs, sample_context):
        """Test security warning detection"""
        template_file = template_dirs[0] / "security.j2"
        template_file.write_text("password=secret123\n")

        renderer = TemplateRenderer(template_dirs)
        result = renderer.render("security.j2", sample_context)

        assert result.success  # Renders but warns
        assert len(result.warnings) > 0
        assert "secret" in result.warnings[0].lower()
```

---

## 9. Base Provider Class

```python
"""
Base provider abstract class.

Location: agentpm/providers/base/provider.py
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any

from agentpm.core.database.service import DatabaseService
from .renderer import TemplateRenderer
from .context import TemplateContext, RenderResult


class BaseProvider(ABC):
    """
    Abstract base class for providers.

    All providers must implement:
    - install() - Install provider files
    - uninstall() - Remove provider files
    - update() - Update provider files
    - verify() - Verify installation
    - render_configs() - Render provider-specific configs
    """

    def __init__(self, db: DatabaseService, template_dir: Path):
        """
        Initialize provider.

        Args:
            db: Database service
            template_dir: Provider template directory
        """
        self.db = db
        self.template_dir = template_dir

        # Initialize renderer with provider templates
        common_dir = template_dir.parent / "templates" / "common"
        self.renderer = TemplateRenderer(
            template_dirs=[template_dir, common_dir],
            cache_size=128,
        )

    @abstractmethod
    def install(
        self,
        project_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Install provider for project.

        Args:
            project_path: Project root directory
            config: Optional provider configuration

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def uninstall(self, project_path: Path) -> bool:
        """
        Uninstall provider.

        Args:
            project_path: Project root directory

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def update(self, project_path: Path) -> bool:
        """
        Update provider installation.

        Args:
            project_path: Project root directory

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def verify(self, project_path: Path) -> bool:
        """
        Verify provider installation.

        Args:
            project_path: Project root directory

        Returns:
            True if valid
        """
        pass

    @abstractmethod
    def render_configs(
        self,
        context: TemplateContext
    ) -> Dict[str, RenderResult]:
        """
        Render all provider-specific configuration files.

        Args:
            context: Template context with project data

        Returns:
            Dictionary mapping filename to RenderResult
        """
        pass

    def _load_project_context(self, project_path: Path) -> TemplateContext:
        """
        Load project context from database.

        Args:
            project_path: Project root directory

        Returns:
            Validated template context
        """
        from .context import (
            ProjectContext,
            AgentContext,
            RuleContext,
            ProviderConfig,
        )

        # Query database for project
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT * FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

            if not project_row:
                raise ValueError(f"Project not found: {project_path}")

            project_id = project_row['id']

            # Load agents
            agent_rows = conn.execute(
                "SELECT * FROM agents WHERE project_id = ? AND is_active = 1",
                (project_id,)
            ).fetchall()

            # Load rules
            rule_rows = conn.execute(
                "SELECT * FROM rules WHERE project_id = ? AND enabled = 1",
                (project_id,)
            ).fetchall()

        # Build context
        project_ctx = ProjectContext(
            id=project_row['id'],
            name=project_row['name'],
            path=Path(project_row['path']),
            business_domain=project_row.get('business_domain', 'General'),
        )

        agents_ctx = [
            AgentContext(
                id=row['id'],
                role=row['role'],
                display_name=row['display_name'],
                description=row['description'],
                tier=row['tier'],
                agent_type=row['agent_type'],
                is_active=bool(row['is_active']),
            )
            for row in agent_rows
        ]

        rules_ctx = [
            RuleContext(
                rule_id=row['rule_id'],
                name=row['name'],
                description=row['description'],
                category=row['category'],
                enforcement_level=row['enforcement_level'],
                priority=row['priority'],
            )
            for row in rule_rows
        ]

        provider_cfg = ProviderConfig(
            provider_name=self.__class__.__name__.lower().replace('provider', ''),
            provider_version="1.0.0",
        )

        return TemplateContext(
            project=project_ctx,
            agents=agents_ctx,
            rules=rules_ctx,
            provider=provider_cfg,
        )
```

---

## 10. Performance Considerations

### 10.1 Template Caching

- **Compiled Templates**: Use `@lru_cache` to cache compiled Jinja2 templates
- **Cache Size**: Default 128 templates, configurable per provider
- **Cache Invalidation**: Clear cache on template file modification

### 10.2 Context Building

- **Lazy Loading**: Load only required data from database
- **Batch Queries**: Use joins to minimize database round-trips
- **Pydantic Validation**: Validate once at context creation, not at render time

### 10.3 Rendering Optimization

- **Parallel Rendering**: Render independent templates in parallel
- **Incremental Updates**: Re-render only changed templates
- **Output Caching**: Cache rendered output with content hash

---

## 11. Security Considerations

### 11.1 Input Validation

- **Pydantic Models**: All template context validated before rendering
- **SQL Injection**: Use parameterized queries for database access
- **Path Traversal**: Sanitize file paths with `sanitize_path` filter

### 11.2 Output Escaping

- **Auto-Escaping**: Enabled for HTML/XML templates
- **Custom Filters**: `escape_shell`, `escape_toml`, `escape_markdown`
- **Manual Escaping**: Mark safe content explicitly with `| safe`

### 11.3 Template Injection Prevention

- **Strict Undefined**: Raise error on undefined variables
- **No Dynamic Template Loading**: All templates from known directories
- **No eval()**: Never use Python eval() in templates

---

## 12. Migration Path

### Phase 1: Core Infrastructure
1. Implement `TemplateContext` models
2. Implement `TemplateRenderer` class
3. Create common macros
4. Implement custom filters

### Phase 2: Provider Templates
1. Claude Code templates
2. Cursor templates
3. OpenAI Codex templates

### Phase 3: Integration
1. Update `CursorProvider` to use renderer
2. Create `ClaudeCodeProvider` with renderer
3. Create `CodexProvider` with renderer

### Phase 4: Testing
1. Unit tests for filters
2. Integration tests for templates
3. End-to-end provider tests

---

## 13. Example Usage

### 13.1 Rendering Claude Code Config

```python
from pathlib import Path
from agentpm.providers.anthropic.provider import ClaudeCodeProvider
from agentpm.core.database.service import DatabaseService

# Initialize provider
db = DatabaseService(Path("/path/to/project/.agentpm/database.db"))
provider = ClaudeCodeProvider(db)

# Install (renders all configs)
success = provider.install(
    project_path=Path("/path/to/project"),
    config={
        "agents_enabled": True,
        "rules_enabled": True,
    }
)

# Verify installation
is_valid = provider.verify(Path("/path/to/project"))

# Update configs
updated = provider.update(Path("/path/to/project"))
```

### 13.2 Rendering Custom Template

```python
from agentpm.providers.base.renderer import TemplateRenderer
from agentpm.providers.base.context import TemplateContext, ProjectContext

# Create renderer
renderer = TemplateRenderer(
    template_dirs=[Path("templates/custom")],
)

# Build context
context = TemplateContext(
    project=ProjectContext(
        id=1,
        name="My Project",
        path=Path("/path/to/project"),
        languages=["Python", "TypeScript"],
    ),
    agents=[],  # Load from database
    rules=[],   # Load from database
    provider=ProviderConfig(
        provider_name="custom",
        provider_version="1.0.0",
    ),
)

# Render template
result = renderer.render("my_template.j2", context)

if result.success:
    print(result.content)
else:
    print(f"Errors: {result.errors}")
```

---

## 14. Appendix: Template Inheritance Example

### Base Template

```jinja2
{# templates/common/base.j2 #}

{# Base template for all provider configs #}
{% block header %}
# Generated Configuration
{% endblock %}

{% block content %}
{# Content goes here #}
{% endblock %}

{% block footer %}
---
Generated by APM (Agent Project Manager)
Date: {{ generated_at | timestamp('iso') }}
{% endblock %}
```

### Child Template

```jinja2
{# templates/anthropic/claude_md.j2 #}

{% extends "common/base.j2" %}

{% block header %}
# CLAUDE.md - {{ project.name }}
{% endblock %}

{% block content %}
## Project: {{ project.name }}

Agents: {{ agents | length }}
Rules: {{ rules | length }}
{% endblock %}
```

---

**End of Document**
