# BaseProvider Implementation Guide

**Quick Reference for Implementing New Provider Generators**

## Prerequisites

```python
# Required imports
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from agentpm.providers.generators.base import (
    BaseProviderGenerator,
    TemplateBasedMixin,
    ProviderConfig,
    GenerationContext,
    GenerationResult,
    FileOutput,
    UniversalContext,
)
from agentpm.providers.generators.models import (
    OutputFormat,
    ProviderFeature,
)
from agentpm.core.database.models import Agent, Rule, Project
```

## Implementation Checklist

### 1. Define Provider Configuration

```python
def create_provider_config() -> ProviderConfig:
    """Create provider configuration"""
    return ProviderConfig(
        # Identity
        name="my-provider",              # Unique identifier
        display_name="My Provider",      # Human-readable name
        version="1.0.0",                 # Config format version

        # Output
        output_format=OutputFormat.DIRECTORY,  # or SINGLE_FILE, MULTI_FILE
        config_directory=Path(".myprovider"),  # Base config directory
        file_extension=".md",                  # File extension

        # Features
        supported_features=[
            ProviderFeature.SLASH_COMMANDS,
            ProviderFeature.HOOKS,
            ProviderFeature.SUBAGENTS,
        ],

        # Templates (if using template-based generation)
        template_engine="jinja2",       # or "mustache", "none"
        template_directory=Path(__file__).parent / "templates",

        # Validation
        enable_validation=True,
        validation_schema=None,         # Optional JSON schema path
    )
```

### 2. Implement Generator Class

#### Option A: Template-Based Generator (Recommended)

```python
class MyProviderGenerator(BaseProviderGenerator, TemplateBasedMixin):
    """Generate configuration for My Provider

    Output structure:
        .myprovider/
        ├── config.yaml
        ├── agents/
        │   ├── orchestrator-1.md
        │   └── specialist-1.md
        └── rules.yaml
    """

    template_name = "agent_file.md.j2"

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize generator

        Args:
            project_path: Project root (defaults to cwd)
        """
        config = create_provider_config()
        super().__init__(config)
        self.project_path = project_path or Path.cwd()

    # =========================================================================
    # REQUIRED METHODS
    # =========================================================================

    def generate_from_agents(
        self,
        context: GenerationContext
    ) -> GenerationResult:
        """Generate provider configuration

        This is the main entry point.
        For template-based generators, use the mixin:
        """
        return self.generate_from_template(
            self.template_name,
            context
        )

    def validate_config(
        self,
        context: GenerationContext
    ) -> tuple[bool, List[str]]:
        """Validate configuration before generation

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Use base class validation
        agents_valid, agent_errors = self.validate_agents(context.agents)
        errors.extend(agent_errors)

        rules_valid, rule_errors = self.validate_rules(context.project_rules)
        errors.extend(rule_errors)

        # Provider-specific validation
        if not context.project_path:
            errors.append("Project path is required")

        # Check for required agent types
        orchestrators = [
            a for a in context.agents
            if 'orch' in a.role.lower()
        ]
        if not orchestrators:
            errors.append("At least one orchestrator required")

        return (len(errors) == 0, errors)

    def format_context(
        self,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """Transform context for templates

        Returns:
            Provider-specific context dictionary
        """
        # Group agents by tier
        agents_by_tier = context.get_agents_by_tier()

        # Group rules by category
        rules_by_category = context.get_rules_by_category()

        # Build template context
        return {
            # Core data
            'project': context.universal_context.project,
            'agents': context.agents,
            'agents_by_tier': agents_by_tier,
            'rules': context.project_rules,
            'rules_by_category': rules_by_category,

            # Technical context
            'tech_stack': context.universal_context.tech_stack,
            'frameworks': context.universal_context.detected_frameworks,
            'exclusions': context.universal_context.common_exclusions,

            # Metadata
            'generation_timestamp': context.generation_timestamp,
            'generator_version': context.generator_version,

            # Provider-specific
            'provider_name': self.config.name,
            'provider_version': self.config.version,
        }

    def get_output_paths(
        self,
        context: GenerationContext
    ) -> List[Path]:
        """Determine where files will be written

        Returns:
            List of output file paths
        """
        base_dir = context.project_path or self.project_path
        config_dir = base_dir / self.config.config_directory
        agents_dir = config_dir / 'agents'

        paths = []

        # Main config file
        paths.append(config_dir / 'config.yaml')

        # Agent files (one per agent)
        for agent in context.agents:
            filename = f"{agent.role}{self.config.file_extension}"
            paths.append(agents_dir / filename)

        # Rules file
        paths.append(config_dir / 'rules.yaml')

        return paths

    # =========================================================================
    # OPTIONAL: Provider-specific validation
    # =========================================================================

    def _validate_agent_for_provider(self, agent: Agent) -> List[str]:
        """Provider-specific agent validation

        Override this to add custom validation logic.
        """
        errors = []

        # Example: Check for required metadata
        if not agent.sop_content:
            errors.append(
                f"Agent {agent.role}: SOP content is required"
            )

        # Example: Check for required capabilities
        if not agent.capabilities:
            errors.append(
                f"Agent {agent.role}: at least one capability required"
            )

        return errors
```

#### Option B: Programmatic Generator (No Templates)

```python
class MyProviderGenerator(BaseProviderGenerator):
    """Generate configuration programmatically (no templates)"""

    def generate_from_agents(
        self,
        context: GenerationContext
    ) -> GenerationResult:
        """Generate configuration programmatically"""
        result = GenerationResult(
            provider_name=self.config.name,
            success=False
        )

        try:
            # Validate
            is_valid, errors = self.validate_config(context)
            if not is_valid:
                result.validation_errors = errors
                return result

            # Format context
            template_context = self.format_context(context)

            # Generate content programmatically
            content = self._build_config_content(template_context)

            # Get output paths
            output_paths = self.get_output_paths(context)

            # Create files
            for output_path in output_paths:
                result.add_file(output_path, content)

            # Update statistics
            result.agents_processed = len(context.agents)
            result.rules_applied = len(context.project_rules)
            result.success = True

        except Exception as e:
            result.errors.append(str(e))

        return result

    def _build_config_content(
        self,
        context: Dict[str, Any]
    ) -> str:
        """Build configuration content programmatically

        This is where you build the config without templates.
        """
        lines = []

        # Header
        lines.append(f"# {context['project'].name} Configuration")
        lines.append(f"# Generated: {context['generation_timestamp']}")
        lines.append("")

        # Agents
        lines.append("## Agents")
        for agent in context['agents']:
            lines.append(f"### {agent.display_name}")
            lines.append(f"- Role: {agent.role}")
            lines.append(f"- Description: {agent.description}")
            lines.append("")

        # Rules
        lines.append("## Rules")
        for category, rules in context['rules_by_category'].items():
            lines.append(f"### {category}")
            for rule in rules:
                lines.append(
                    f"- {rule.rule_id}: {rule.name} "
                    f"({rule.enforcement_level.value})"
                )
            lines.append("")

        return "\n".join(lines)

    # Still need to implement validate_config, format_context, get_output_paths
    # ... (same as template-based version)
```

### 3. Create Templates (Template-Based Only)

**File:** `agentpm/providers/generators/my_provider/templates/agent_file.md.j2`

```jinja2
# {{ agent.display_name }}

**Role:** {{ agent.role }}
**Tier:** {{ agent.tier.value if agent.tier else 'specialist' }}

## Description
{{ agent.description }}

## Capabilities
{% for capability in agent.capabilities %}
- {{ capability }}
{% endfor %}

## Project Rules

{% for category, rules in rules_by_category.items() %}
### {{ category|title }}
{% for rule in rules %}
- **{{ rule.rule_id }}**: {{ rule.name }}
  - Enforcement: {{ rule.enforcement_level.value }}
  - Description: {{ rule.description }}
{% endfor %}

{% endfor %}

## Standard Operating Procedure

{{ agent.sop_content }}

---

*Generated by {{ provider_name }} v{{ provider_version }}*
*Timestamp: {{ generation_timestamp }}*
```

### 4. Register with CLI

**File:** `agentpm/cli/commands/generate.py`

```python
import click
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.providers.generators.service import ProviderGenerationService
from agentpm.providers.generators.anthropic.claude_code import ClaudeCodeGenerator
from agentpm.providers.generators.cursor.cursor import CursorGenerator
from agentpm.providers.generators.my_provider.generator import MyProviderGenerator


@click.command()
@click.option(
    '--provider',
    type=click.Choice(['claude-code', 'cursor', 'openai', 'my-provider']),
    required=True,
    help='Target provider'
)
@click.option(
    '--project-id',
    type=int,
    required=True,
    help='Project ID to generate config for'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    help='Output directory (default: project path)'
)
def generate_config(provider: str, project_id: int, output: Optional[Path]):
    """Generate provider-specific configuration from database"""

    # Initialize services
    db = DatabaseService("~/.agentpm/agentpm.db")
    service = ProviderGenerationService(db)

    # Select generator
    generators = {
        'claude-code': ClaudeCodeGenerator,
        'cursor': CursorGenerator,
        'my-provider': MyProviderGenerator,
    }

    generator_class = generators.get(provider)
    if not generator_class:
        click.echo(f"Error: Unknown provider: {provider}", err=True)
        return 1

    generator = generator_class(project_path=output)

    # Generate configuration
    click.echo(f"Generating {provider} configuration...")
    result = service.generate_config(
        project_id=project_id,
        generator=generator,
        project_path=output
    )

    # Display results
    if result.success:
        click.echo(f"✓ Generated {len(result.files)} files:")
        for file_output in result.files:
            click.echo(f"  - {file_output.path} ({file_output.size_bytes} bytes)")

        click.echo(f"\nStatistics:")
        click.echo(f"  Agents processed: {result.agents_processed}")
        click.echo(f"  Rules applied: {result.rules_applied}")
        click.echo(f"  Total size: {result.total_size()} bytes")
    else:
        click.echo("✗ Generation failed:", err=True)
        for error in result.errors:
            click.echo(f"  - {error}", err=True)
        for error in result.validation_errors:
            click.echo(f"  - Validation: {error}", err=True)
        return 1

    return 0
```

### 5. Write Tests

**File:** `tests/providers/generators/test_my_provider.py`

```python
import pytest
from pathlib import Path
from datetime import datetime

from agentpm.providers.generators.my_provider.generator import MyProviderGenerator
from agentpm.providers.generators.models import (
    GenerationContext,
    UniversalContext,
    ProviderConfig,
)
from agentpm.core.database.models import Agent, Rule, Project
from agentpm.core.database.enums import AgentTier


@pytest.fixture
def sample_agent():
    """Create sample agent for testing"""
    return Agent(
        id=1,
        project_id=1,
        role="test-agent",
        display_name="Test Agent",
        description="Test agent for unit tests",
        sop_content="# Test SOP\n\nTest procedure",
        capabilities=["testing", "validation"],
        tier=AgentTier.SPECIALIST,
    )


@pytest.fixture
def sample_rule():
    """Create sample rule for testing"""
    return Rule(
        id=1,
        project_id=1,
        rule_id="TEST-001",
        name="test-rule",
        description="Test rule",
        enforcement_level="BLOCK",
        category="testing",
    )


@pytest.fixture
def sample_project():
    """Create sample project for testing"""
    return Project(
        id=1,
        name="Test Project",
        description="Test project",
        path="/tmp/test-project",
        tech_stack=["python", "pytest"],
    )


@pytest.fixture
def generation_context(sample_agent, sample_rule, sample_project):
    """Create generation context for testing"""
    universal_context = UniversalContext(
        project=sample_project,
        tech_stack=["python"],
        detected_frameworks=["pytest"],
    )

    return GenerationContext(
        agents=[sample_agent],
        project_rules=[sample_rule],
        universal_context=universal_context,
        provider_config=MyProviderGenerator().config,
        project_path=Path("/tmp/test-project"),
    )


def test_generator_initialization():
    """Test generator initializes correctly"""
    generator = MyProviderGenerator()

    assert generator.config.name == "my-provider"
    assert generator.config.display_name == "My Provider"
    assert generator.config.is_template_based()


def test_validate_config_success(generation_context):
    """Test validation passes with valid config"""
    generator = MyProviderGenerator()

    is_valid, errors = generator.validate_config(generation_context)

    assert is_valid
    assert len(errors) == 0


def test_validate_config_missing_agent():
    """Test validation fails with no agents"""
    generator = MyProviderGenerator()

    # Create context with no agents
    context = GenerationContext(
        agents=[],
        project_rules=[],
        universal_context=UniversalContext(
            project=Project(id=1, name="Test", path="/tmp/test")
        ),
        provider_config=generator.config,
    )

    is_valid, errors = generator.validate_config(context)

    assert not is_valid
    assert len(errors) > 0


def test_format_context(generation_context):
    """Test context formatting"""
    generator = MyProviderGenerator()

    formatted = generator.format_context(generation_context)

    assert 'project' in formatted
    assert 'agents' in formatted
    assert 'rules' in formatted
    assert 'agents_by_tier' in formatted
    assert 'rules_by_category' in formatted


def test_get_output_paths(generation_context):
    """Test output path generation"""
    generator = MyProviderGenerator()

    paths = generator.get_output_paths(generation_context)

    assert len(paths) > 0
    assert all(isinstance(p, Path) for p in paths)


def test_generate_from_agents_success(generation_context, tmp_path):
    """Test successful generation"""
    generator = MyProviderGenerator(project_path=tmp_path)

    result = generator.generate_from_agents(generation_context)

    assert result.success
    assert len(result.files) > 0
    assert result.agents_processed == 1
    assert result.rules_applied == 1
    assert len(result.errors) == 0


def test_generate_file_hash():
    """Test file hash generation"""
    generator = MyProviderGenerator()

    content = "Test content"
    hash1 = generator.generate_file_hash(content)
    hash2 = generator.generate_file_hash(content)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 produces 64 hex chars


def test_provider_metadata():
    """Test provider metadata"""
    generator = MyProviderGenerator()

    metadata = generator.get_provider_metadata()

    assert metadata['name'] == 'my-provider'
    assert metadata['display_name'] == 'My Provider'
    assert 'supported_features' in metadata
    assert 'template_based' in metadata
```

## Common Patterns

### Pattern 1: File per Agent

```python
def get_output_paths(self, context: GenerationContext) -> List[Path]:
    """Generate one file per agent"""
    base_dir = context.project_path / self.config.config_directory
    agents_dir = base_dir / 'agents'

    return [
        agents_dir / f"{agent.role}{self.config.file_extension}"
        for agent in context.agents
    ]
```

### Pattern 2: Single Monolithic File

```python
def get_output_paths(self, context: GenerationContext) -> List[Path]:
    """Generate single file with all config"""
    base_dir = context.project_path
    return [base_dir / '.cursorrules']
```

### Pattern 3: Hierarchical Directory Structure

```python
def get_output_paths(self, context: GenerationContext) -> List[Path]:
    """Generate hierarchical structure"""
    base_dir = context.project_path / self.config.config_directory

    paths = []

    # Group by tier
    for tier, agents in context.get_agents_by_tier().items():
        tier_dir = base_dir / 'agents' / tier
        for agent in agents:
            paths.append(tier_dir / f"{agent.role}.md")

    return paths
```

### Pattern 4: Conditional Feature Files

```python
def get_output_paths(self, context: GenerationContext) -> List[Path]:
    """Include optional feature files based on config"""
    base_dir = context.project_path / self.config.config_directory
    paths = []

    # Always include main config
    paths.append(base_dir / 'config.yaml')

    # Conditional: slash commands
    if self.supports_feature(ProviderFeature.SLASH_COMMANDS):
        paths.append(base_dir / 'commands.yaml')

    # Conditional: hooks
    if self.supports_feature(ProviderFeature.HOOKS):
        paths.append(base_dir / 'hooks.py')

    return paths
```

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agentpm.providers.generators')
logger.setLevel(logging.DEBUG)
```

### Inspect Generated Context

```python
def format_context(self, context: GenerationContext) -> Dict[str, Any]:
    formatted = super().format_context(context)

    # Debug: Print context
    import json
    print(json.dumps(formatted, indent=2, default=str))

    return formatted
```

### Validate Output Files

```python
result = generator.generate_from_agents(context)

for file_output in result.files:
    # Verify hash
    assert file_output.verify_integrity()

    # Check file exists
    assert file_output.path.exists()

    # Verify content
    actual = file_output.path.read_text()
    assert actual == file_output.content
```

## Quick Reference Commands

```bash
# Generate configuration
apm generate config --provider my-provider --project-id 1

# Generate to custom location
apm generate config --provider my-provider --project-id 1 --output /tmp/test

# Validate without writing
apm generate config --provider my-provider --project-id 1 --dry-run

# Show provider info
apm generate list-providers
```

## Summary

**Minimum Required:**
1. Extend `BaseProviderGenerator`
2. Implement 4 abstract methods:
   - `generate_from_agents()`
   - `validate_config()`
   - `format_context()`
   - `get_output_paths()`
3. Create templates (if using `TemplateBasedMixin`)
4. Register with CLI
5. Write tests

**Optional Enhancements:**
- Override `_validate_agent_for_provider()` for custom validation
- Add custom Jinja2 filters via `_register_template_filters()`
- Implement custom hash verification
- Add provider-specific metadata

This guide provides everything needed to implement a new provider generator in ~200 lines of code.
