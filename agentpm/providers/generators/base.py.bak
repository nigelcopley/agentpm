"""
Base Provider Generator Interface

Defines the abstract interface for generating LLM provider-specific agent files
from database agent records.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from agentpm.core.database.models import Agent, Rule


@dataclass
class GenerationContext:
    """Context for agent file generation"""

    agent: Agent
    project_rules: List[Rule]
    universal_rules: Optional[List[Rule]] = None
    project_path: Optional[Path] = None
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """Result of agent file generation"""

    agent_role: str
    output_path: Path
    content: str
    success: bool
    error: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ProviderGenerator(ABC):
    """
    Abstract base class for provider-specific agent file generators.

    Implementations must:
    1. Generate provider-specific agent files from database records
    2. Handle provider-specific formatting and conventions
    3. Inject project rules and universal rules
    4. Determine appropriate output paths
    """

    provider_name: str = "base"
    file_extension: str = ".md"

    @abstractmethod
    def generate_agent_file(self, context: GenerationContext) -> GenerationResult:
        """
        Generate provider-specific agent file from database agent.

        Args:
            context: Generation context with agent, rules, and metadata

        Returns:
            GenerationResult with file content and metadata
        """
        pass

    @abstractmethod
    def get_output_path(
        self,
        agent_role: str,
        project_path: Optional[Path] = None
    ) -> Path:
        """
        Determine where to write generated agent file.

        Args:
            agent_role: Agent role identifier
            project_path: Optional project root path

        Returns:
            Path where agent file should be written
        """
        pass

    @abstractmethod
    def validate_agent(self, agent: Agent) -> tuple[bool, List[str]]:
        """
        Validate agent record before generation.

        Args:
            agent: Agent to validate

        Returns:
            (is_valid, error_messages)
        """
        pass

    def get_template_path(self) -> Optional[Path]:
        """
        Get path to template file (if template-based).

        Returns:
            Path to template or None if not template-based
        """
        return None

    def supports_agent_type(self, agent_type: str) -> bool:
        """
        Check if provider supports this agent type.

        Args:
            agent_type: Type of agent (orchestrator, specialist, utility, etc.)

        Returns:
            True if supported
        """
        return True  # Default: support all types

    def get_provider_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this provider generator.

        Returns:
            Metadata dictionary
        """
        return {
            "provider_name": self.provider_name,
            "file_extension": self.file_extension,
            "template_based": self.get_template_path() is not None,
        }


class TemplateBasedGenerator(ProviderGenerator):
    """
    Base class for template-based generators using Jinja2.

    Subclasses only need to:
    1. Define template_name
    2. Implement get_output_path()
    3. Optionally override prepare_template_context()
    """

    template_name: str = "agent_file.md.j2"

    def __init__(self):
        """Initialize Jinja2 environment"""
        try:
            from jinja2 import Environment, PackageLoader, select_autoescape

            self.jinja_env = Environment(
                loader=PackageLoader(
                    self.__class__.__module__.rsplit('.', 1)[0],
                    'templates'
                ),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        except ImportError:
            raise ImportError(
                "Jinja2 is required for template-based generators. "
                "Install with: pip install jinja2"
            )

    def generate_agent_file(self, context: GenerationContext) -> GenerationResult:
        """Generate agent file using Jinja2 template"""
        try:
            # Validate agent
            is_valid, errors = self.validate_agent(context.agent)
            if not is_valid:
                return GenerationResult(
                    agent_role=context.agent.role,
                    output_path=self.get_output_path(context.agent.role, context.project_path),
                    content="",
                    success=False,
                    error="; ".join(errors)
                )

            # Prepare template context
            template_context = self.prepare_template_context(context)

            # Render template
            template = self.jinja_env.get_template(self.template_name)
            content = template.render(**template_context)

            # Get output path
            output_path = self.get_output_path(
                context.agent.role,
                context.project_path
            )

            return GenerationResult(
                agent_role=context.agent.role,
                output_path=output_path,
                content=content,
                success=True
            )

        except Exception as e:
            return GenerationResult(
                agent_role=context.agent.role,
                output_path=self.get_output_path(context.agent.role, context.project_path),
                content="",
                success=False,
                error=str(e)
            )

    def prepare_template_context(
        self,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Prepare context dictionary for template rendering.

        Override to customize template variables.

        Args:
            context: Generation context

        Returns:
            Dictionary for template rendering
        """
        return {
            "agent": context.agent,
            "project_rules": context.project_rules,
            "universal_rules": context.universal_rules or [],
            "additional_context": context.additional_context or {},
        }

    def validate_agent(self, agent: Agent) -> tuple[bool, List[str]]:
        """Default validation for template-based generators"""
        errors = []

        if not agent.role:
            errors.append("Agent role is required")

        if not agent.display_name:
            errors.append("Agent display_name is required")

        if not agent.description:
            errors.append("Agent description is required")

        return (len(errors) == 0, errors)

    def get_template_path(self) -> Optional[Path]:
        """Get path to template file"""
        try:
            template = self.jinja_env.get_template(self.template_name)
            return Path(template.filename) if hasattr(template, 'filename') else None
        except:
            return None
