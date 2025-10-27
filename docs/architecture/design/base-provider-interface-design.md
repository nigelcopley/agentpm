# BaseProvider Interface Design

**Version:** 1.0.0
**Date:** 2025-10-27
**Status:** Draft
**Author:** System Architect

## Executive Summary

This document defines the complete interface for multi-provider configuration generation in AgentPM. The design enables generation of native config files (not API calls) for Claude Code, Cursor, and OpenAI Codex from a universal AGENTS.md source.

**Key Goals:**
- Abstract base class for all provider generators
- Template-based generation using Jinja2
- Support both file-based and directory-based outputs
- Provider-specific feature handling
- SHA-256 validation for integrity
- Clean integration with existing database models

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          BaseProviderGenerator (ABC)                │
│  - generate_from_agents()                           │
│  - validate_config()                                │
│  - format_context()                                 │
│  - get_provider_metadata()                          │
└─────────────────────────────────────────────────────┘
                      ▲
                      │
          ┌───────────┴───────────┐
          │                       │
┌─────────────────────┐  ┌────────────────────┐
│ TemplateBasedGen    │  │ ProgrammaticGen    │
│ (Jinja2)            │  │ (Code-based)       │
└─────────────────────┘  └────────────────────┘
          ▲                       ▲
          │                       │
    ┌─────┴─────┬─────────┬──────┴─────┐
    │           │         │            │
┌─────────┐ ┌──────┐ ┌──────┐  ┌──────────┐
│ Claude  │ │Cursor│ │OpenAI│  │ Custom   │
│  Code   │ │      │ │Codex │  │ Provider │
└─────────┘ └──────┘ └──────┘  └──────────┘
```

## Core Models

### 1. ProviderConfig

```python
"""Provider configuration metadata"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime
from enum import Enum


class OutputFormat(str, Enum):
    """Supported output formats"""
    SINGLE_FILE = "single_file"      # All config in one file (Cursor)
    DIRECTORY = "directory"          # Config split across files (Claude Code)
    MULTI_FILE = "multi_file"        # Multiple independent files (OpenAI)


class ProviderFeature(str, Enum):
    """Provider-specific features"""
    SLASH_COMMANDS = "slash_commands"
    HOOKS = "hooks"
    MEMORY = "memory"
    PLUGINS = "plugins"
    SKILLS = "skills"
    SUBAGENTS = "subagents"
    CUSTOM_TOOLS = "custom_tools"
    CONTEXT_FILES = "context_files"


class ProviderConfig(BaseModel):
    """Provider configuration metadata

    Defines capabilities, output format, and generation settings
    for a specific LLM provider.
    """

    name: str = Field(..., description="Provider identifier (e.g., 'claude-code')")
    display_name: str = Field(..., description="Human-readable name")
    version: str = Field(default="1.0.0", description="Config format version")

    # Output configuration
    output_format: OutputFormat = Field(..., description="How config is structured")
    config_directory: Path = Field(..., description="Base directory for config files")
    file_extension: str = Field(default=".md", description="File extension for agent files")

    # Feature support
    supported_features: List[ProviderFeature] = Field(
        default_factory=list,
        description="Features this provider supports"
    )

    # Template configuration
    template_engine: Literal["jinja2", "mustache", "none"] = Field(
        default="jinja2",
        description="Template engine to use"
    )
    template_directory: Optional[Path] = Field(
        default=None,
        description="Directory containing templates"
    )

    # Validation settings
    enable_validation: bool = Field(default=True, description="Enable config validation")
    validation_schema: Optional[Path] = Field(
        default=None,
        description="JSON schema for validation"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('config_directory', 'template_directory')
    def resolve_paths(cls, v: Optional[Path]) -> Optional[Path]:
        """Resolve and validate paths"""
        if v is None:
            return None
        return Path(v).expanduser().resolve()

    def supports_feature(self, feature: ProviderFeature) -> bool:
        """Check if provider supports a specific feature"""
        return feature in self.supported_features

    def is_template_based(self) -> bool:
        """Check if provider uses template-based generation"""
        return self.template_engine != "none"

    class Config:
        use_enum_values = False
        validate_assignment = True
```

### 2. GenerationContext

```python
"""Context for configuration generation"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from agentpm.core.database.models import Agent, Rule, Project


@dataclass
class UniversalContext:
    """Universal context shared across all providers

    Contains project-wide information that all providers need.
    """
    project: Project
    tech_stack: List[str] = field(default_factory=list)
    detected_frameworks: List[str] = field(default_factory=list)
    common_exclusions: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'project_name': self.project.name,
            'project_path': str(self.project.path),
            'tech_stack': self.tech_stack,
            'frameworks': self.detected_frameworks,
            'exclusions': self.common_exclusions,
            'env_vars': self.environment_vars,
        }


@dataclass
class GenerationContext:
    """Complete context for provider configuration generation

    Combines agent data, rules, project context, and provider settings
    for configuration generation.
    """

    # Core data
    agents: List[Agent]
    project_rules: List[Rule]
    universal_context: UniversalContext

    # Provider configuration
    provider_config: ProviderConfig

    # Optional data
    universal_rules: Optional[List[Rule]] = None
    project_path: Optional[Path] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    generation_timestamp: datetime = field(default_factory=datetime.utcnow)
    generator_version: str = "1.0.0"

    def get_rules_by_category(self) -> Dict[str, List[Rule]]:
        """Group rules by category for organized output"""
        from collections import defaultdict
        categorized = defaultdict(list)

        for rule in self.project_rules:
            category = rule.category or 'general'
            categorized[category].append(rule)

        return dict(categorized)

    def get_agents_by_tier(self) -> Dict[str, List[Agent]]:
        """Group agents by tier (orchestrator, specialist, sub-agent)"""
        from collections import defaultdict
        from agentpm.core.database.enums import AgentTier

        tiered = defaultdict(list)

        for agent in self.agents:
            tier = agent.tier or AgentTier.SPECIALIST
            tiered[tier.value].append(agent)

        return dict(tiered)

    def filter_agents_by_feature(
        self,
        feature: ProviderFeature
    ) -> List[Agent]:
        """Filter agents that require a specific feature"""
        # Implementation depends on agent metadata structure
        filtered = []
        for agent in self.agents:
            if agent.metadata:
                import json
                metadata = json.loads(agent.metadata) if isinstance(agent.metadata, str) else agent.metadata
                required_features = metadata.get('required_features', [])
                if feature.value in required_features:
                    filtered.append(agent)
        return filtered
```

### 3. GenerationResult

```python
"""Result of configuration generation"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib


@dataclass
class FileOutput:
    """Single file generated by provider"""
    path: Path
    content: str
    content_hash: str = field(init=False)
    size_bytes: int = field(init=False)

    def __post_init__(self):
        """Calculate hash and size"""
        self.content_hash = hashlib.sha256(
            self.content.encode('utf-8')
        ).hexdigest()
        self.size_bytes = len(self.content.encode('utf-8'))

    def verify_integrity(self) -> bool:
        """Verify content hasn't been modified"""
        current_hash = hashlib.sha256(
            self.content.encode('utf-8')
        ).hexdigest()
        return current_hash == self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'path': str(self.path),
            'content_hash': self.content_hash,
            'size_bytes': self.size_bytes,
        }


@dataclass
class GenerationResult:
    """Complete result of provider configuration generation

    Includes all generated files, validation results, and metadata.
    """

    # Generation metadata
    provider_name: str
    success: bool
    generation_time: datetime = field(default_factory=datetime.utcnow)

    # Generated files
    files: List[FileOutput] = field(default_factory=list)

    # Validation
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    # Errors
    errors: List[str] = field(default_factory=list)

    # Statistics
    agents_processed: int = 0
    rules_applied: int = 0
    features_enabled: List[str] = field(default_factory=list)

    def add_file(self, path: Path, content: str) -> FileOutput:
        """Add a generated file to results"""
        file_output = FileOutput(path=path, content=content)
        self.files.append(file_output)
        return file_output

    def has_errors(self) -> bool:
        """Check if generation had errors"""
        return bool(self.errors or self.validation_errors)

    def get_file_manifest(self) -> List[Dict[str, Any]]:
        """Get manifest of all generated files"""
        return [f.to_dict() for f in self.files]

    def total_size(self) -> int:
        """Total size of all generated files in bytes"""
        return sum(f.size_bytes for f in self.files)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'provider': self.provider_name,
            'success': self.success,
            'generation_time': self.generation_time.isoformat(),
            'files': self.get_file_manifest(),
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'errors': self.errors,
            'statistics': {
                'agents_processed': self.agents_processed,
                'rules_applied': self.rules_applied,
                'features_enabled': self.features_enabled,
                'total_size_bytes': self.total_size(),
            }
        }
```

## BaseProviderGenerator Interface

```python
"""Abstract base class for provider generators"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging


class BaseProviderGenerator(ABC):
    """Abstract base class for all provider configuration generators

    Implements the core interface that all provider generators must follow.
    Provides common utilities for validation, template loading, and file
    generation.

    Subclasses must implement:
    - generate_from_agents(): Main generation logic
    - validate_config(): Provider-specific validation
    - format_context(): Provider-specific context formatting
    - get_output_paths(): Determine where files should be written

    Example:
        class ClaudeCodeGenerator(BaseProviderGenerator):
            def generate_from_agents(self, context):
                # Generate .claude/agents/*.md files
                ...
    """

    def __init__(self, config: ProviderConfig):
        """Initialize generator with provider configuration

        Args:
            config: Provider configuration metadata
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")

        # Initialize template engine if needed
        if config.is_template_based():
            self._init_template_engine()

    # =====================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =====================================================================

    @abstractmethod
    def generate_from_agents(
        self,
        context: GenerationContext
    ) -> GenerationResult:
        """Generate provider configuration from agents and rules

        This is the main entry point for configuration generation.

        Args:
            context: Complete generation context with agents, rules, and metadata

        Returns:
            GenerationResult with all generated files and validation results

        Example:
            result = generator.generate_from_agents(context)
            if result.success:
                for file in result.files:
                    print(f"Generated: {file.path}")
        """
        pass

    @abstractmethod
    def validate_config(
        self,
        context: GenerationContext
    ) -> tuple[bool, List[str]]:
        """Validate configuration before generation

        Performs provider-specific validation to ensure all required
        data is present and valid.

        Args:
            context: Generation context to validate

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            is_valid, errors = generator.validate_config(context)
            if not is_valid:
                print(f"Validation failed: {errors}")
        """
        pass

    @abstractmethod
    def format_context(
        self,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """Format context for provider-specific templates

        Transforms universal context into provider-specific format.

        Args:
            context: Universal generation context

        Returns:
            Provider-specific context dictionary

        Example:
            template_context = generator.format_context(context)
            # Returns: {'agents': [...], 'rules': {...}, 'project': {...}}
        """
        pass

    @abstractmethod
    def get_output_paths(
        self,
        context: GenerationContext
    ) -> List[Path]:
        """Determine output file paths for generated configuration

        Args:
            context: Generation context

        Returns:
            List of paths where files will be written

        Example:
            paths = generator.get_output_paths(context)
            # Returns: [Path('.claude/agents/dev.md'), ...]
        """
        pass

    # =====================================================================
    # COMMON METHODS - Provided by base class
    # =====================================================================

    def get_provider_metadata(self) -> Dict[str, Any]:
        """Get metadata about this provider generator

        Returns:
            Provider metadata dictionary
        """
        return {
            'name': self.config.name,
            'display_name': self.config.display_name,
            'version': self.config.version,
            'output_format': self.config.output_format.value,
            'supported_features': [f.value for f in self.config.supported_features],
            'template_based': self.config.is_template_based(),
        }

    def validate_agents(
        self,
        agents: List[Agent]
    ) -> tuple[bool, List[str]]:
        """Validate agent records before generation

        Common validation logic for all providers.

        Args:
            agents: List of agents to validate

        Returns:
            Tuple of (all_valid, error_messages)
        """
        errors = []

        for agent in agents:
            # Required fields
            if not agent.role:
                errors.append(f"Agent {agent.id}: role is required")

            if not agent.display_name:
                errors.append(f"Agent {agent.id}: display_name is required")

            if not agent.description:
                errors.append(f"Agent {agent.id}: description is required")

            # Role format (kebab-case)
            if agent.role and not self._is_valid_role(agent.role):
                errors.append(
                    f"Agent {agent.id}: role '{agent.role}' must be kebab-case"
                )

            # Provider-specific validation
            provider_errors = self._validate_agent_for_provider(agent)
            errors.extend(provider_errors)

        return (len(errors) == 0, errors)

    def validate_rules(
        self,
        rules: List[Rule]
    ) -> tuple[bool, List[str]]:
        """Validate rule records before generation

        Args:
            rules: List of rules to validate

        Returns:
            Tuple of (all_valid, error_messages)
        """
        errors = []

        for rule in rules:
            if not rule.rule_id:
                errors.append(f"Rule {rule.id}: rule_id is required")

            if not rule.name:
                errors.append(f"Rule {rule.id}: name is required")

            if not rule.enforcement_level:
                errors.append(f"Rule {rule.id}: enforcement_level is required")

        return (len(errors) == 0, errors)

    def generate_file_hash(self, content: str) -> str:
        """Generate SHA-256 hash of file content

        Args:
            content: File content to hash

        Returns:
            Hexadecimal hash string
        """
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def write_file(
        self,
        path: Path,
        content: str,
        overwrite: bool = False
    ) -> FileOutput:
        """Write generated file to disk

        Args:
            path: Path to write to
            content: File content
            overwrite: Whether to overwrite existing files

        Returns:
            FileOutput with path and hash

        Raises:
            FileExistsError: If file exists and overwrite=False
        """
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"File already exists: {path}. Use overwrite=True to replace."
            )

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(content, encoding='utf-8')

        self.logger.info(f"Generated: {path} ({len(content)} bytes)")

        return FileOutput(path=path, content=content)

    def supports_feature(self, feature: ProviderFeature) -> bool:
        """Check if this provider supports a specific feature

        Args:
            feature: Feature to check

        Returns:
            True if supported
        """
        return feature in self.config.supported_features

    # =====================================================================
    # TEMPLATE METHODS - For template-based generators
    # =====================================================================

    def _init_template_engine(self) -> None:
        """Initialize template engine (Jinja2)"""
        if self.config.template_engine != "jinja2":
            return

        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape

            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.config.template_directory)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Add custom filters
            self._register_template_filters()

        except ImportError:
            raise ImportError(
                "Jinja2 is required for template-based generators. "
                "Install with: pip install jinja2"
            )

    def _register_template_filters(self) -> None:
        """Register custom Jinja2 filters"""
        if not hasattr(self, 'jinja_env'):
            return

        # Common filters
        self.jinja_env.filters['kebab_case'] = self._to_kebab_case
        self.jinja_env.filters['snake_case'] = self._to_snake_case
        self.jinja_env.filters['pascal_case'] = self._to_pascal_case
        self.jinja_env.filters['format_rule'] = self._format_rule
        self.jinja_env.filters['group_by'] = self._group_by

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Render a template with context

        Args:
            template_name: Name of template file
            context: Template context dictionary

        Returns:
            Rendered template content
        """
        if not hasattr(self, 'jinja_env'):
            raise RuntimeError(
                "Template engine not initialized. "
                "Ensure config.template_engine is 'jinja2'."
            )

        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    # =====================================================================
    # UTILITY METHODS - Private helpers
    # =====================================================================

    def _is_valid_role(self, role: str) -> bool:
        """Check if role is valid kebab-case"""
        return (
            role and
            role.replace('-', '').replace('_', '').isalnum() and
            not role.startswith('-') and
            not role.endswith('-') and
            '--' not in role
        )

    def _validate_agent_for_provider(self, agent: Agent) -> List[str]:
        """Provider-specific agent validation (override in subclass)"""
        return []

    # Template filters

    @staticmethod
    def _to_kebab_case(s: str) -> str:
        """Convert string to kebab-case"""
        import re
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', s)
        s = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s)
        return s.replace('_', '-').lower()

    @staticmethod
    def _to_snake_case(s: str) -> str:
        """Convert string to snake_case"""
        import re
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
        s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
        return s.replace('-', '_').lower()

    @staticmethod
    def _to_pascal_case(s: str) -> str:
        """Convert string to PascalCase"""
        return ''.join(word.capitalize() for word in s.replace('_', '-').split('-'))

    @staticmethod
    def _format_rule(rule: Rule) -> str:
        """Format rule for display in templates"""
        return f"{rule.rule_id}: {rule.name} ({rule.enforcement_level.value})"

    @staticmethod
    def _group_by(items: List[Any], key: str) -> Dict[str, List[Any]]:
        """Group items by a key attribute"""
        from collections import defaultdict
        grouped = defaultdict(list)
        for item in items:
            group_key = getattr(item, key, 'unknown')
            grouped[group_key].append(item)
        return dict(grouped)
```

## Template-Based Generator Mixin

```python
"""Mixin for template-based generators"""
from typing import Dict, Any, Optional


class TemplateBasedMixin:
    """Mixin providing template-based generation capabilities

    Use this when your provider uses Jinja2 templates for generation.

    Requirements:
    - Must have self.config (ProviderConfig)
    - Must have self.jinja_env (Jinja2 Environment)

    Example:
        class ClaudeCodeGenerator(BaseProviderGenerator, TemplateBasedMixin):
            template_name = "agent_file.md.j2"

            def generate_from_agents(self, context):
                return self.generate_from_template(
                    self.template_name,
                    context
                )
    """

    template_name: str = "default.j2"

    def generate_from_template(
        self,
        template_name: str,
        context: GenerationContext,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """Generate configuration from template

        Args:
            template_name: Template file name
            context: Generation context
            custom_context: Additional template variables

        Returns:
            GenerationResult with generated files
        """
        result = GenerationResult(
            provider_name=self.config.name,
            success=False
        )

        try:
            # Validate configuration
            is_valid, errors = self.validate_config(context)
            if not is_valid:
                result.validation_errors = errors
                return result

            # Format context for template
            template_context = self.format_context(context)

            # Add custom context
            if custom_context:
                template_context.update(custom_context)

            # Render template
            content = self.render_template(template_name, template_context)

            # Determine output paths
            output_paths = self.get_output_paths(context)

            # Generate files
            for output_path in output_paths:
                file_output = result.add_file(output_path, content)
                self.logger.info(
                    f"Generated {output_path} "
                    f"({file_output.size_bytes} bytes, "
                    f"hash: {file_output.content_hash[:8]}...)"
                )

            # Update statistics
            result.agents_processed = len(context.agents)
            result.rules_applied = len(context.project_rules)
            result.features_enabled = [
                f.value for f in self.config.supported_features
            ]
            result.success = True

        except Exception as e:
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            result.errors.append(str(e))

        return result

    def get_template_variables(self) -> List[str]:
        """Get list of variables used in template

        Returns:
            List of variable names
        """
        if not hasattr(self, 'jinja_env'):
            return []

        try:
            template = self.jinja_env.get_template(self.template_name)
            # Parse template AST to extract variables
            from jinja2 import meta
            ast = self.jinja_env.parse(template.source)
            return list(meta.find_undeclared_variables(ast))
        except:
            return []
```

## Example Implementation: Claude Code Generator

```python
"""Claude Code generator implementation"""
from pathlib import Path
from typing import Dict, Any, List

from .base import (
    BaseProviderGenerator,
    TemplateBasedMixin,
    ProviderConfig,
    GenerationContext,
    GenerationResult,
    ProviderFeature,
    OutputFormat,
)
from agentpm.core.database.models import Agent


class ClaudeCodeGenerator(BaseProviderGenerator, TemplateBasedMixin):
    """Generate Claude Code agent files from database records

    Output structure:
        .claude/
        ├── agents/
        │   ├── orchestrator-definition.md
        │   ├── specialist-python.md
        │   └── utility-context.md
        └── CLAUDE.md (project instructions)

    Features:
    - Directory-based output
    - Markdown agent files
    - Slash commands support
    - Hooks support
    - Memory tool support
    """

    template_name = "agent_file.md.j2"

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize Claude Code generator

        Args:
            project_path: Project root path (defaults to cwd)
        """
        # Create provider configuration
        config = ProviderConfig(
            name="claude-code",
            display_name="Claude Code",
            version="1.0.0",
            output_format=OutputFormat.DIRECTORY,
            config_directory=Path(".claude"),
            file_extension=".md",
            supported_features=[
                ProviderFeature.SLASH_COMMANDS,
                ProviderFeature.HOOKS,
                ProviderFeature.MEMORY,
                ProviderFeature.SUBAGENTS,
                ProviderFeature.CONTEXT_FILES,
            ],
            template_engine="jinja2",
            template_directory=Path(__file__).parent / "templates",
        )

        super().__init__(config)

        self.project_path = project_path or Path.cwd()

    def generate_from_agents(
        self,
        context: GenerationContext
    ) -> GenerationResult:
        """Generate Claude Code agent files

        Args:
            context: Generation context with agents and rules

        Returns:
            GenerationResult with generated files
        """
        return self.generate_from_template(
            self.template_name,
            context
        )

    def validate_config(
        self,
        context: GenerationContext
    ) -> tuple[bool, List[str]]:
        """Validate Claude Code configuration

        Args:
            context: Generation context

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Validate agents
        agents_valid, agent_errors = self.validate_agents(context.agents)
        errors.extend(agent_errors)

        # Validate rules
        rules_valid, rule_errors = self.validate_rules(context.project_rules)
        errors.extend(rule_errors)

        # Claude Code specific validation
        if not context.project_path:
            errors.append("Project path is required for Claude Code")

        # Check for required agent types
        orchestrators = [a for a in context.agents if 'orch' in a.role.lower()]
        if not orchestrators:
            errors.append("At least one orchestrator agent is required")

        return (len(errors) == 0, errors)

    def format_context(
        self,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """Format context for Claude Code templates

        Args:
            context: Universal generation context

        Returns:
            Claude Code specific context
        """
        # Group agents by tier
        agents_by_tier = context.get_agents_by_tier()

        # Group rules by category
        rules_by_category = context.get_rules_by_category()

        # Extract behavioral rules from agent metadata
        behavioral_rules = self._extract_behavioral_rules(context.agents)

        # Build template context
        return {
            'project': context.universal_context.project,
            'agents': context.agents,
            'agents_by_tier': agents_by_tier,
            'project_rules': context.project_rules,
            'rules_by_category': rules_by_category,
            'universal_rules': context.universal_rules or [],
            'behavioral_rules': behavioral_rules,
            'tech_stack': context.universal_context.tech_stack,
            'frameworks': context.universal_context.detected_frameworks,
            'exclusions': context.universal_context.common_exclusions,
            'generation_timestamp': context.generation_timestamp,
            'generator_version': context.generator_version,
        }

    def get_output_paths(
        self,
        context: GenerationContext
    ) -> List[Path]:
        """Determine output paths for Claude Code files

        Args:
            context: Generation context

        Returns:
            List of output file paths
        """
        base_dir = context.project_path or self.project_path
        agents_dir = base_dir / '.claude' / 'agents'

        paths = []

        # Generate path for each agent
        for agent in context.agents:
            filename = f"{agent.role}{self.config.file_extension}"
            paths.append(agents_dir / filename)

        # Add CLAUDE.md if needed
        if context.additional_context.get('generate_claude_md', True):
            paths.append(base_dir / '.claude' / 'CLAUDE.md')

        return paths

    def _validate_agent_for_provider(self, agent: Agent) -> List[str]:
        """Claude Code specific agent validation

        Args:
            agent: Agent to validate

        Returns:
            List of error messages
        """
        errors = []

        # Check SOP content exists (Claude Code requires it)
        if not agent.sop_content or not agent.sop_content.strip():
            errors.append(
                f"Agent {agent.role}: sop_content is required for Claude Code"
            )

        # Check capabilities exist
        if not agent.capabilities:
            errors.append(
                f"Agent {agent.role}: at least one capability is required"
            )

        return errors

    def _extract_behavioral_rules(
        self,
        agents: List[Agent]
    ) -> List[str]:
        """Extract behavioral rules from agent metadata

        Args:
            agents: List of agents

        Returns:
            List of behavioral rules
        """
        import json
        rules = []

        for agent in agents:
            if not agent.metadata:
                continue

            try:
                metadata = (
                    json.loads(agent.metadata)
                    if isinstance(agent.metadata, str)
                    else agent.metadata
                )
                agent_rules = metadata.get('behavioral_rules', [])
                rules.extend(agent_rules)
            except (json.JSONDecodeError, AttributeError):
                continue

        return list(set(rules))  # Remove duplicates
```

## Integration with Database Service

```python
"""Integration with DatabaseService"""
from typing import List, Optional
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models import Agent, Rule, Project


class ProviderGenerationService:
    """Service for generating provider configurations from database

    Bridges DatabaseService and provider generators.

    Example:
        service = ProviderGenerationService(db_service)
        generator = ClaudeCodeGenerator()

        result = service.generate_config(
            project_id=1,
            generator=generator
        )

        if result.success:
            print(f"Generated {len(result.files)} files")
    """

    def __init__(self, db_service: DatabaseService):
        """Initialize generation service

        Args:
            db_service: Database service instance
        """
        self.db = db_service
        self.logger = logging.getLogger(__name__)

    def generate_config(
        self,
        project_id: int,
        generator: BaseProviderGenerator,
        project_path: Optional[Path] = None
    ) -> GenerationResult:
        """Generate provider configuration for a project

        Args:
            project_id: Project ID
            generator: Provider generator instance
            project_path: Optional project path override

        Returns:
            GenerationResult with generated files
        """
        try:
            # Load data from database
            context = self._build_generation_context(
                project_id,
                generator.config,
                project_path
            )

            # Generate configuration
            result = generator.generate_from_agents(context)

            # Write files if successful
            if result.success:
                self._write_generated_files(result)

            return result

        except Exception as e:
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            return GenerationResult(
                provider_name=generator.config.name,
                success=False,
                errors=[str(e)]
            )

    def _build_generation_context(
        self,
        project_id: int,
        provider_config: ProviderConfig,
        project_path: Optional[Path]
    ) -> GenerationContext:
        """Build generation context from database

        Args:
            project_id: Project ID
            provider_config: Provider configuration
            project_path: Optional project path

        Returns:
            GenerationContext
        """
        with self.db.connect() as conn:
            # Load project
            from agentpm.core.database.methods import project_methods
            project = project_methods.get_project(self.db, project_id)

            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Load agents
            from agentpm.core.database.methods import agent_methods
            agents = agent_methods.list_agents(
                self.db,
                project_id=project_id,
                is_active=True
            )

            # Load rules
            from agentpm.core.database.methods import rule_methods
            rules = rule_methods.list_rules(
                self.db,
                project_id=project_id,
                enabled=True
            )

            # Build universal context
            universal_context = UniversalContext(
                project=project,
                tech_stack=project.tech_stack,
                detected_frameworks=project.detected_frameworks,
                common_exclusions=self._get_common_exclusions(),
            )

            # Build generation context
            return GenerationContext(
                agents=agents,
                project_rules=rules,
                universal_context=universal_context,
                provider_config=provider_config,
                project_path=project_path or Path(project.path),
            )

    def _write_generated_files(
        self,
        result: GenerationResult
    ) -> None:
        """Write generated files to disk

        Args:
            result: Generation result with files
        """
        for file_output in result.files:
            try:
                # Create parent directories
                file_output.path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                file_output.path.write_text(
                    file_output.content,
                    encoding='utf-8'
                )

                self.logger.info(f"Wrote: {file_output.path}")

            except Exception as e:
                self.logger.error(
                    f"Failed to write {file_output.path}: {e}",
                    exc_info=True
                )
                result.errors.append(
                    f"Failed to write {file_output.path}: {e}"
                )

    def _get_common_exclusions(self) -> List[str]:
        """Get common file/directory exclusions

        Returns:
            List of exclusion patterns
        """
        return [
            'node_modules/',
            '.git/',
            '.venv/',
            '__pycache__/',
            '*.pyc',
            '.DS_Store',
            '.env',
            '.env.local',
            'dist/',
            'build/',
        ]
```

## Summary

This design provides:

1. **Clean abstraction** - BaseProviderGenerator defines interface
2. **Template support** - Jinja2 integration via mixin
3. **Validation** - SHA-256 hashing, config validation
4. **Flexibility** - Supports file-based and directory-based outputs
5. **Database integration** - ProviderGenerationService bridges DB and generators
6. **Type safety** - Full Python 3.10+ type hints
7. **SOLID compliance** - Single responsibility, open/closed principle
8. **Extensibility** - Easy to add new providers

**Key Files to Create:**
- `agentpm/providers/generators/base_provider.py` - BaseProviderGenerator
- `agentpm/providers/generators/models.py` - Pydantic models
- `agentpm/providers/generators/service.py` - ProviderGenerationService
- `agentpm/providers/generators/anthropic/claude_code.py` - Example implementation

**Next Steps:**
1. Implement BaseProviderGenerator
2. Create Pydantic models
3. Implement ClaudeCodeGenerator
4. Add Cursor and OpenAI generators
5. Create integration tests
6. Add CLI commands for generation
