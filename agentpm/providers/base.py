"""
Base Provider Interface

Defines the interface that all LLM providers must implement.

This module contains two main abstractions:
1. BaseProvider: Legacy interface for agent file generation and context formatting
2. BaseProviderGenerator: New interface for multi-provider configuration generation

Pattern: Abstract Base Class (ABC) with Pydantic models for type safety
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, NamedTuple
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib

from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule
from agentpm.core.database.models.project import Project

# Global registry for formatters
_FORMATTER_REGISTRY = {}


# ============================================================================
# Provider Configuration Generation Models
# ============================================================================


class ProviderConfig(BaseModel):
    """
    Provider configuration metadata.

    Defines the basic characteristics of a provider (Claude Code, Cursor, etc.)
    including its native configuration directory and supported features.

    Attributes:
        name: Provider identifier (e.g., 'claude-code', 'cursor', 'codex')
        display_name: Human-readable provider name
        config_directory: Native config directory (e.g., '.claude', '.codex', empty for Cursor)
        supported_features: List of features this provider supports
        template_engine: Template engine to use (default: 'jinja2')

    Example:
        >>> config = ProviderConfig(
        ...     name="claude-code",
        ...     display_name="Claude Code",
        ...     config_directory=".claude",
        ...     supported_features=["agents", "hooks", "memory", "skills"]
        ... )
    """
    name: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Human-readable provider name")
    config_directory: str = Field(..., description="Native config directory")
    supported_features: List[str] = Field(
        default_factory=list,
        description="List of supported features"
    )
    template_engine: str = Field(
        default="jinja2",
        description="Template engine to use for generation"
    )


class GenerationContext(BaseModel):
    """
    Context passed to configuration generator.

    Contains all the database entities and metadata needed to generate
    provider-native configuration files.

    Attributes:
        agents: Flat list of all agents (no tier hierarchy)
        rules: All active rules from database
        project: Project metadata
        work_item: Optional current work item context
        task: Optional current task context
        tech_stack: Optional list of detected technologies

    Example:
        >>> context = GenerationContext(
        ...     agents=[agent1, agent2],
        ...     rules=[rule1, rule2],
        ...     project=project,
        ...     tech_stack=["python", "sqlite"]
        ... )
    """
    agents: List[Agent] = Field(..., description="Flat list of all agents")
    rules: List[Rule] = Field(..., description="All active rules")
    project: Project = Field(..., description="Project metadata")
    work_item: Optional[Any] = Field(
        default=None,
        description="Current work item context"
    )
    task: Optional[Any] = Field(
        default=None,
        description="Current task context"
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Detected technologies"
    )


class FileOutput(BaseModel):
    """
    Generated file metadata with content verification.

    Tracks each file generated during configuration generation,
    including its path, hash, size, and timestamp for verification.

    Attributes:
        path: Absolute path to generated file
        content_hash: SHA-256 hash of file content
        size_bytes: File size in bytes
        generated_at: Timestamp of generation

    Example:
        >>> output = FileOutput(
        ...     path=Path("/project/.claude/agents/developer.md"),
        ...     content_hash="a1b2c3...",
        ...     size_bytes=1024,
        ...     generated_at=datetime.now()
        ... )
    """
    path: Path = Field(..., description="Absolute path to generated file")
    content_hash: str = Field(..., description="SHA-256 hash of content")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    generated_at: datetime = Field(..., description="Generation timestamp")

    @staticmethod
    def create_from_content(path: Path, content: str) -> "FileOutput":
        """
        Create FileOutput from content string.

        Args:
            path: Path to file
            content: File content

        Returns:
            FileOutput instance with computed hash and size
        """
        return FileOutput(
            path=path,
            content_hash=hashlib.sha256(content.encode('utf-8')).hexdigest(),
            size_bytes=len(content.encode('utf-8')),
            generated_at=datetime.utcnow()
        )


class GenerationResult(BaseModel):
    """
    Result of configuration generation operation.

    Contains the outcome of a generation run, including all files created,
    any errors encountered, and optional statistics.

    Attributes:
        success: Whether generation completed successfully
        files: List of generated file metadata
        errors: List of error messages (empty if successful)
        statistics: Optional generation statistics

    Example:
        >>> result = GenerationResult(
        ...     success=True,
        ...     files=[file1, file2],
        ...     statistics={"agents_generated": 2, "duration_ms": 150}
        ... )
    """
    success: bool = Field(..., description="Whether generation succeeded")
    files: List[FileOutput] = Field(
        default_factory=list,
        description="List of generated files"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="List of error messages"
    )
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional generation statistics"
    )


# ============================================================================
# Template-Based Mixin
# ============================================================================


class TemplateBasedMixin:
    """
    Mixin for Jinja2 template rendering support.

    Provides common template initialization, rendering, and custom filter
    registration for provider generators that use Jinja2 templates.

    Methods:
        _init_templates: Initialize Jinja2 environment with template directory
        _render_template: Render a template with context
        _register_custom_filters: Register provider-specific custom filters

    Usage:
        >>> class MyGenerator(BaseProviderGenerator, TemplateBasedMixin):
        ...     def __init__(self, template_dir: Path):
        ...         self._init_templates(template_dir)
        ...         self._register_custom_filters()
    """

    def _init_templates(self, template_dir: Path) -> None:
        """
        Initialize Jinja2 environment with template directory.

        Sets up the Jinja2 environment with sensible defaults:
        - FileSystemLoader for template directory
        - Autoescape for HTML/XML (safety)
        - Trim blocks and lstrip blocks (clean output)

        Args:
            template_dir: Directory containing Jinja2 templates

        Raises:
            ImportError: If jinja2 is not installed
            FileNotFoundError: If template_dir doesn't exist
        """
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
        except ImportError:
            raise ImportError(
                "jinja2 is required for template-based providers. "
                "Install it with: pip install jinja2"
            )

        if not template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Register default filters
        self.env.filters['kebab_case'] = self._kebab_case
        self.env.filters['snake_case'] = self._snake_case
        self.env.filters['flatten_agents'] = self._flatten_agents

    def _render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Render a Jinja2 template with context.

        Args:
            template_name: Name of template file (relative to template_dir)
            context: Template context dictionary

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateError: If rendering fails
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _register_custom_filters(self) -> None:
        """
        Register provider-specific custom Jinja2 filters.

        Override this method in subclasses to add custom filters beyond
        the default kebab_case, snake_case, and flatten_agents.

        Example:
            >>> def _register_custom_filters(self):
            ...     super()._register_custom_filters()
            ...     self.env.filters['my_filter'] = lambda x: x.upper()
        """
        pass

    @staticmethod
    def _kebab_case(text: str) -> str:
        """Convert text to kebab-case."""
        import re
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Insert hyphens before capitals and convert to lowercase
        text = re.sub(r'([a-z])([A-Z])', r'\1-\2', text)
        return text.lower()

    @staticmethod
    def _snake_case(text: str) -> str:
        """Convert text to snake_case."""
        import re
        # Replace spaces and hyphens with underscores
        text = re.sub(r'[\s-]+', '_', text)
        # Insert underscores before capitals and convert to lowercase
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        return text.lower()

    @staticmethod
    def _flatten_agents(agents: List[Agent]) -> List[Agent]:
        """
        Flatten agent list (identity function for compatibility).

        In the new architecture, agents are already flat (no tiers).
        This filter exists for template compatibility.

        Args:
            agents: List of agents

        Returns:
            Same list (identity function)
        """
        return agents


# ============================================================================
# BaseProviderGenerator Abstract Base Class
# ============================================================================


class BaseProviderGenerator(ABC):
    """
    Abstract base class for provider configuration generators.

    Defines the minimal interface that all providers (Claude Code, Cursor, OpenAI Codex)
    must implement for generating native configuration files from APM database.

    Design Principles:
    - Single Responsibility: Each provider handles only its native format
    - Open/Closed: Extensible for new providers without modifying existing code
    - Liskov Substitution: All providers are interchangeable through this interface
    - Interface Segregation: Minimal interface with only essential methods
    - Dependency Inversion: Depends on abstractions (ABC) not concrete implementations

    Required Methods:
        provider_name: Property returning provider identifier
        config_directory: Property returning native config directory
        generate_from_agents: Generate configuration files from database entities
        validate_config: Validate existing configuration
        format_context: Format APM context for real-time updates

    Example Implementation:
        >>> class ClaudeCodeGenerator(BaseProviderGenerator, TemplateBasedMixin):
        ...     @property
        ...     def provider_name(self) -> str:
        ...         return "claude-code"
        ...
        ...     @property
        ...     def config_directory(self) -> str:
        ...         return ".claude"
        ...
        ...     def generate_from_agents(self, agents, rules, project, output_dir, **kwargs):
        ...         # Implementation here
        ...         pass
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Provider identifier.

        Returns:
            Provider name (e.g., 'claude-code', 'cursor', 'codex')

        Example:
            >>> generator.provider_name
            'claude-code'
        """
        pass

    @property
    @abstractmethod
    def config_directory(self) -> str:
        """
        Native configuration directory for this provider.

        Returns:
            Directory name (e.g., '.claude', '.codex', empty string for Cursor)

        Example:
            >>> generator.config_directory
            '.claude'
        """
        pass

    @abstractmethod
    def generate_from_agents(
        self,
        agents: List[Agent],
        rules: List[Rule],
        project: Project,
        output_dir: Path,
        **kwargs
    ) -> GenerationResult:
        """
        Generate provider-native configuration files from database entities.

        This is the main generation method that creates all necessary configuration
        files in the provider's native format.

        Args:
            agents: Flat list of all agents (no tier hierarchy)
            rules: All active rules from database
            project: Project metadata
            output_dir: Project root directory (config will be in output_dir / config_directory)
            **kwargs: Provider-specific options (e.g., include_hooks=True)

        Returns:
            GenerationResult with success status, generated files, and any errors

        Example:
            >>> result = generator.generate_from_agents(
            ...     agents=[agent1, agent2],
            ...     rules=[rule1, rule2],
            ...     project=project,
            ...     output_dir=Path("/projects/myapp")
            ... )
            >>> print(f"Generated {len(result.files)} files")
        """
        pass

    @abstractmethod
    def validate_config(self, config_dir: Path) -> List[str]:
        """
        Validate existing configuration directory.

        Checks that the configuration is valid according to provider requirements.
        Used for health checks and troubleshooting.

        Args:
            config_dir: Directory containing provider configuration

        Returns:
            List of validation error messages (empty list if valid)

        Example:
            >>> errors = generator.validate_config(Path("/projects/myapp/.claude"))
            >>> if errors:
            ...     print(f"Configuration errors: {errors}")
            ... else:
            ...     print("Configuration is valid")
        """
        pass

    @abstractmethod
    def format_context(
        self,
        project: Project,
        work_item: Optional[Any],
        task: Optional[Any]
    ) -> str:
        """
        Format APM context for real-time updates in provider-native format.

        Creates a formatted context block that can be injected into provider
        sessions for real-time project state awareness.

        Args:
            project: Project metadata
            work_item: Optional current work item
            task: Optional current task

        Returns:
            Formatted context string in provider-native format

        Example:
            >>> context = generator.format_context(project, work_item, task)
            >>> print(context)
            ## Current Context
            - Project: MyApp
            - Work Item: #123 - Implement feature X
            - Task: #456 - Write unit tests
        """
        pass


# ============================================================================
# Legacy BaseProvider Interface (Maintained for Compatibility)
# ============================================================================


def register_formatter(provider_name: str, formatter_class):
    """Register a formatter for a provider."""
    _FORMATTER_REGISTRY[provider_name] = formatter_class


def get_formatter(provider_name: str):
    """Get registered formatter for a provider."""
    return _FORMATTER_REGISTRY.get(provider_name)


class TokenAllocation(NamedTuple):
    """Token allocation for context formatting."""
    total_tokens: int
    context_tokens: int
    response_tokens: int
    safety_buffer: int


class LLMContextFormatter(ABC):
    """Base class for LLM context formatters."""
    
    provider: str
    
    @abstractmethod
    def format_task(self, payload, *, token_allocation=None, **metadata) -> str:
        """Format task context for the LLM."""
        pass
    
    @abstractmethod
    def format_session(self, history: str, *, token_allocation=None, **metadata) -> str:
        """Format session context for the LLM."""
        pass


class LLMContextAdapter(ABC):
    """Base class for LLM context adapters."""
    
    provider: str
    
    @abstractmethod
    def plan_tokens(self, payload) -> TokenAllocation:
        """Plan token allocation for the context payload."""
        pass


class BaseProvider(ABC):
    """
    Base class for all LLM providers.
    
    Each provider handles:
    - Agent file generation for their platform
    - Context formatting for their LLM
    - Hook template generation
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'openai')."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass
    
    @abstractmethod
    def generate_agent_files(
        self, 
        agents: List[Agent], 
        output_dir: Path
    ) -> None:
        """
        Generate provider-specific agent files.
        
        Args:
            agents: List of agents to generate files for
            output_dir: Directory to write files to
        """
        pass
    
    @abstractmethod
    def format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context for this provider's LLM.
        
        Args:
            context: Context data to format
            
        Returns:
            Formatted context string
        """
        pass
    
    @abstractmethod
    def get_hook_templates(self) -> Dict[str, str]:
        """
        Get provider-specific hook templates.
        
        Returns:
            Dictionary mapping hook names to template content
        """
        pass
    
    def validate_agent(self, agent: Agent) -> List[str]:
        """
        Validate an agent for this provider.
        
        Args:
            agent: Agent to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation
        if not agent.role:
            errors.append("Agent role is required")
        
        if not agent.display_name:
            errors.append("Agent display name is required")
        
        if not agent.sop_content:
            errors.append("Agent SOP content is required")
        
        return errors
    
    def get_output_directory(self, project_path: Path) -> Path:
        """
        Get the output directory for this provider.

        Args:
            project_path: Project root path

        Returns:
            Provider-specific output directory
        """
        # Default implementation - override in subclasses
        return project_path / f".{self.name}"


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # New Provider Generation Interface
    "BaseProviderGenerator",
    "ProviderConfig",
    "GenerationContext",
    "FileOutput",
    "GenerationResult",
    "TemplateBasedMixin",

    # Legacy Provider Interface
    "BaseProvider",
    "LLMContextFormatter",
    "LLMContextAdapter",
    "TokenAllocation",

    # Registry Functions
    "register_formatter",
    "get_formatter",
]