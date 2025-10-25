# Provider Generator System

**Extensible architecture for generating LLM provider-specific agent files from database records**

## Overview

The provider generator system transforms database agent records into provider-specific configuration files (e.g., `.claude/agents/*.md` for Claude Code, `.cursor/agents/*.md` for Cursor).

### Key Benefits

- **Single Source of Truth**: Agent metadata lives in database, files are generated
- **Multi-Provider Support**: Same agent definitions work across different LLM providers
- **Consistency**: All generated files follow provider conventions automatically
- **Extensibility**: Easy to add new providers by implementing interface

## Architecture

### Three-Layer Design

```
Database (Agent Records)
         ↓
Provider Generator (Transformation Logic)
         ↓
Provider Files (.claude/agents/*.md, etc.)
```

### Core Components

1. **ProviderGenerator (Base Interface)**: Abstract base class defining contract
2. **TemplateBasedGenerator**: Jinja2-powered implementation base
3. **ClaudeCodeGenerator**: Claude Code specific implementation
4. **Provider Registry**: Central registration and auto-detection

## Usage

### Basic Usage

```bash
# Auto-detect provider and generate all agents
apm agents generate --all

# Generate specific agent
apm agents generate --role context-generator

# Specify provider explicitly
apm agents generate --all --provider=claude-code

# Dry run (preview without writing)
apm agents generate --all --dry-run
```

### Provider Detection

Detection order (highest priority first):

1. `AIPM_LLM_PROVIDER` environment variable
2. `.claude/` directory → `claude-code`
3. `.cursor/` directory → `cursor`
4. Default to `claude-code`

## Implementing New Provider

### Step 1: Create Generator Class

```python
# agentpm/core/plugins/domains/llms/generators/my_provider/generator.py

from pathlib import Path
from agentpm.core.plugins.domains.llms.generators.base import TemplateBasedGenerator


class MyProviderGenerator(TemplateBasedGenerator):
    """Generator for My Provider LLM"""

    provider_name = "my-provider"
    file_extension = ".yaml"  # or .md, .json, etc.
    template_name = "agent.yaml.j2"

    def get_output_path(
            self,
            agent_role: str,
            project_path: Path = None
    ) -> Path:
        """Define where files are written"""
        if project_path is None:
            project_path = Path.cwd()

        # Example: .myprovider/agents/{role}.yaml
        return project_path / ".myprovider" / "agents" / f"{agent_role}{self.file_extension}"
```

### Step 2: Create Template

```jinja2
{# agentpm/core/plugins/domains/llms/generators/my_provider/templates/agent.yaml.j2 #}

name: {{ agent.role }}
persona: {{ agent.persona }}
description: |
  {{ agent.description }}

rules:
{% for rule in project_rules %}
  - code: {{ rule.code }}
    title: {{ rule.title }}
    enforcement: {{ rule.enforcement_level }}
{% endfor %}
```

### Step 3: Register Provider

```python
# agentpm/core/plugins/domains/llms/generators/registry.py

def _register_builtin_providers():
    """Register built-in provider generators"""

    # ... existing registrations ...

    # Add your provider
    try:
        from agentpm.core.plugins.domains.llms.generators.my_provider.generator import (
            MyProviderGenerator
        )
        register_provider_generator('my-provider', MyProviderGenerator)
    except ImportError:
        pass  # Provider not available
```

### Step 4: Update CLI

```python
# agentpm/cli/commands/agents/generate.py

@click.option(
    '--provider',
    help='LLM provider (auto-detected if not specified)',
    type=click.Choice([
        'claude-code',
        'cursor',
        'my-provider',  # Add here
    ], case_sensitive=False)
)
```

## API Reference

### ProviderGenerator

```python
class ProviderGenerator(ABC):
    """Abstract base for provider generators"""

    provider_name: str  # Unique identifier
    file_extension: str  # e.g., ".md"

    @abstractmethod
    def generate_agent_file(
        self,
        context: GenerationContext
    ) -> GenerationResult:
        """Generate provider-specific agent file"""
        pass

    @abstractmethod
    def get_output_path(
        self,
        agent_role: str,
        project_path: Path = None
    ) -> Path:
        """Determine output path for agent file"""
        pass

    @abstractmethod
    def validate_agent(
        self,
        agent: Agent
    ) -> tuple[bool, list[str]]:
        """Validate agent before generation"""
        pass
```

### TemplateBasedGenerator

```python
class TemplateBasedGenerator(ProviderGenerator):
    """Jinja2-powered generator base class"""

    template_name: str  # Template filename

    def prepare_template_context(
        self,
        context: GenerationContext
    ) -> dict[str, Any]:
        """Prepare context for template rendering"""
        return {
            "agent": context.agent,
            "project_rules": context.project_rules,
            "universal_rules": context.universal_rules or [],
            "additional_context": context.additional_context or {},
        }
```

### GenerationContext

```python
@dataclass
class GenerationContext:
    """Context for agent file generation"""

    agent: Agent                        # Agent record from database
    project_rules: list[Rule]           # Project-specific rules
    universal_rules: list[Rule] = None  # Universal rules
    project_path: Path = None           # Project root path
    additional_context: dict = None     # Provider-specific data
```

### GenerationResult

```python
@dataclass
class GenerationResult:
    """Result of agent file generation"""

    agent_role: str          # Agent identifier
    output_path: Path        # Where file was/will be written
    content: str             # Generated file content
    success: bool            # True if generation succeeded
    error: str = None        # Error message if failed
    warnings: list[str] = [] # Non-fatal issues
```

## Template Variables

### Available in All Templates

```python
{
    "agent": Agent(
        role="agent-name",
        persona="Agent Persona",
        description="Agent description",
        behavioral_rules=[...],  # JSON list
        success_metrics="...",
    ),
    "project_rules": [
        Rule(
            code="CI-001",
            title="Rule Title",
            description="Rule description",
            category="category",
            enforcement_level="BLOCK|WARN|INFO"
        ),
        ...
    ],
    "universal_rules": [...],  # Same structure as project_rules
    "additional_context": {...},  # Provider-specific data
}
```

### Claude Code Specific

```python
{
    "rules_by_category": {
        "core_principles": [Rule(...), ...],
        "testing": [Rule(...), ...],
        ...
    },
    "behavioral_rules": ["rule1", "rule2", ...],  # Parsed from JSON
    "agent_type": "orchestrator|specialist|utility|sub-agent",
    "has_universal_rules": bool,
}
```

## Testing

### Unit Tests

```python
# Test provider generator implementation
def test_my_provider_generation(tmp_path):
    generator = MyProviderGenerator()

    agent = Agent(
        id=1,
        role="test-agent",
        persona="Test Persona",
        description="Test description"
    )

    context = GenerationContext(
        agent=agent,
        project_rules=[],
        project_path=tmp_path
    )

    result = generator.generate_agent_file(context)

    assert result.success
    assert result.content
    # Verify provider-specific format
```

### Integration Tests

```python
# Test full generation workflow
def test_full_generation_workflow(tmp_path):
    # Register provider
    register_provider_generator('test', MyProviderGenerator)

    # Detect provider
    detected = detect_current_provider(tmp_path)

    # Generate agent file
    generator = get_provider_generator(detected)
    result = generator.generate_agent_file(context)

    # Write file
    result.output_path.write_text(result.content)

    # Verify file exists and is valid
    assert result.output_path.exists()
```

## Best Practices

### 1. Template Organization

```
generators/
  my_provider/
    __init__.py
    generator.py          # Generator implementation
    templates/
      agent.yaml.j2       # Main template
      macros.j2           # Reusable macros
      sections/           # Template partials
        rules.j2
        workflow.j2
```

### 2. Error Handling

```python
def generate_agent_file(self, context: GenerationContext) -> GenerationResult:
    try:
        # Validate first
        is_valid, errors = self.validate_agent(context.agent)
        if not is_valid:
            return GenerationResult(
                agent_role=context.agent.role,
                output_path=self.get_output_path(context.agent.role),
                content="",
                success=False,
                error="; ".join(errors)
            )

        # Generate content
        content = self._generate_content(context)

        return GenerationResult(
            agent_role=context.agent.role,
            output_path=self.get_output_path(context.agent.role),
            content=content,
            success=True
        )

    except Exception as e:
        return GenerationResult(
            agent_role=context.agent.role,
            output_path=self.get_output_path(context.agent.role),
            content="",
            success=False,
            error=str(e)
        )
```

### 3. Provider-Specific Validation

```python
def validate_agent(self, agent: Agent) -> tuple[bool, list[str]]:
    errors = []

    # Standard validation
    if not agent.role:
        errors.append("Agent role is required")

    # Provider-specific validation
    if self.provider_name == "my-provider":
        if not agent.metadata.get("my_provider_field"):
            errors.append("my_provider_field is required for this provider")

    return (len(errors) == 0, errors)
```

### 4. Template Context Customization

```python
def prepare_template_context(
    self,
    context: GenerationContext
) -> dict[str, Any]:
    # Get base context
    template_context = super().prepare_template_context(context)

    # Add provider-specific data
    template_context.update({
        "provider_version": "1.0",
        "custom_field": self._compute_custom_field(context.agent),
        "formatted_rules": self._format_rules(context.project_rules),
    })

    return template_context
```

## Examples

### Example 1: Generate All Agents

```bash
$ apm agents generate --all

🔍 Using provider: claude-code

🔍 Generating 15 agent(s)...
████████████████████████████████████████ 100%

✅ Generated 15 agent file(s)
📁 Location: .claude/agents/

💡 Agents are ready to use via Task tool delegation
```

### Example 2: Generate Specific Agent

```bash
$ apm agents generate --role context-generator

🔍 Using provider: claude-code

🔍 Generating 1 agent(s)...
████████████████████████████████████████ 100%

✅ Generated 1 agent file(s)
📁 Location: .claude/agents/

💡 Agents are ready to use via Task tool delegation
```

### Example 3: Dry Run

```bash
$ apm agents generate --all --dry-run

🔍 Using provider: claude-code

🔍 Generating 15 agent(s)...
   [DRY RUN - No files will be written]
████████████████████████████████████████ 100%

✅ Generated 15 agent file(s)

💡 Files shown above would be generated
```

## Troubleshooting

### Provider Not Detected

**Problem**: `❌ Could not detect LLM provider`

**Solutions**:
1. Set environment variable: `export AIPM_LLM_PROVIDER=claude-code`
2. Create provider directory: `mkdir .claude`
3. Specify explicitly: `apm agents generate --provider=claude-code`

### Template Not Found

**Problem**: `❌ Error: Template 'agent.j2' not found`

**Solutions**:
1. Verify template exists in `templates/` directory
2. Check `template_name` matches actual filename
3. Ensure Jinja2 loader configuration is correct

### Generation Validation Failed

**Problem**: `❌ Agent 'test-agent': Agent role is required`

**Solutions**:
1. Check agent record in database has all required fields
2. Run database migrations: `apm db migrate`
3. Validate agent: `apm agents validate test-agent`

## Future Enhancements

### Planned Providers

- **Cursor**: `.cursor/agents/*.md`
- **Gemini**: `.gemini/agents/*.yaml`
- **Windsurf**: `.windsurf/agents/*.json`

### Planned Features

- **Multi-file Generation**: Generate supporting files (workflows, configs)
- **Template Inheritance**: Provider templates can extend base templates
- **Validation Hooks**: Custom validation per provider
- **Generation Hooks**: Pre/post-generation callbacks
- **File Watching**: Auto-regenerate on database changes

## See Also

- [Agent Generation Workflow](../user-guides/agent-generation-workflow.md) - User guide for agent generation
- [Agent Architecture](../components/agents/README.md) - Database-first agent system
- [Database Schema](../components/database/schema.md) - Agents table structure
- [CLI Commands Reference](../user-guides/03-cli-commands.md) - All CLI commands
