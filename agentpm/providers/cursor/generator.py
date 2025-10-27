"""
Cursor Generator with Jinja2 Template System

Generates Cursor configuration files from APM database entities.
Cursor is the simplest provider - just two files (.cursorrules + .cursorignore).

Architecture:
- CursorGenerator: Main generator class implementing BaseProviderGenerator
- TemplateBasedMixin: Jinja2 template rendering support
- Template files: Simple Jinja2 templates for plain text rules

Pattern: Template Method Pattern (like Claude Code but simpler)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule
from agentpm.core.database.models.project import Project
from agentpm.core.database.enums import AgentFunctionalCategory
from agentpm.providers.base import (
    BaseProviderGenerator,
    TemplateBasedMixin,
    GenerationResult,
    FileOutput
)
from agentpm.providers.common.patterns import CommonExclusions


class CursorGenerator(BaseProviderGenerator, TemplateBasedMixin):
    """
    Cursor configuration generator using Jinja2 templates.

    Generates provider-native configuration from APM database:
    - .cursorrules: Plain text AI instructions (transform AGENTS.md)
    - .cursorignore: Gitignore-style exclusions

    Cursor is the simplest provider:
    - No agent files (Cursor doesn't support agent concepts)
    - No directory structure (files at project root)
    - Plain text format (no YAML frontmatter)

    Design Principles:
    - Template-driven: All formatting in Jinja2 templates
    - Database-first: All data from database, not files
    - Flattened agents: Convert agents to "expert mode" instructions
    - Single Responsibility: Each method has one clear purpose

    Example:
        >>> db = DatabaseService("path/to/db")
        >>> generator = CursorGenerator(db)
        >>> result = generator.generate_from_agents(
        ...     agents=db.list_agents(),
        ...     rules=db.list_rules(),
        ...     project=db.get_project(),
        ...     output_dir=Path("/project")
        ... )
        >>> print(f"Generated {len(result.files)} files")
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize Cursor generator.

        Args:
            db_service: Database service for accessing APM data

        Raises:
            FileNotFoundError: If template directory doesn't exist
            ImportError: If jinja2 is not installed
        """
        self.db = db_service

        # Initialize Jinja2 templates
        template_dir = Path(__file__).parent / "templates"
        self._init_templates(template_dir)

        # Register custom filters (none needed for Cursor, but call for consistency)
        self._register_custom_filters()

    @property
    def provider_name(self) -> str:
        """Provider identifier."""
        return "cursor"

    @property
    def config_directory(self) -> str:
        """Native configuration directory (empty for Cursor - files at root)."""
        return ""

    def generate_from_agents(
        self,
        agents: List[Agent],
        rules: List[Rule],
        project: Project,
        output_dir: Path,
        **kwargs
    ) -> GenerationResult:
        """
        Generate Cursor configuration files from database entities.

        Creates the following structure:
        - output_dir/.cursorrules (plain text instructions)
        - output_dir/.cursorignore (exclusion patterns)

        Args:
            agents: Flat list of all agents from database
            rules: All active rules from database
            project: Project metadata
            output_dir: Project root directory
            **kwargs: Optional parameters (none used for Cursor)

        Returns:
            GenerationResult with success status, files, and statistics

        Example:
            >>> result = generator.generate_from_agents(
            ...     agents=[agent1, agent2],
            ...     rules=[rule1, rule2],
            ...     project=project,
            ...     output_dir=Path("/project")
            ... )
        """
        errors: List[str] = []
        files: List[FileOutput] = []
        stats: Dict[str, Any] = {
            "agents_generated": len(agents),
            "rules_included": len(rules),
            "duration_ms": 0,
            "generation_time": datetime.utcnow().isoformat()
        }

        start_time = datetime.utcnow()

        try:
            # 1. Generate .cursorrules
            try:
                cursorrules_file = self._generate_cursorrules(
                    agents=agents,
                    rules=rules,
                    project=project,
                    output_dir=output_dir
                )
                files.append(cursorrules_file)
            except Exception as e:
                errors.append(f"Failed to generate .cursorrules: {e}")

            # 2. Generate .cursorignore
            try:
                cursorignore_file = self._generate_cursorignore(
                    output_dir=output_dir
                )
                files.append(cursorignore_file)
            except Exception as e:
                errors.append(f"Failed to generate .cursorignore: {e}")

            # Calculate duration
            end_time = datetime.utcnow()
            stats["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

            return GenerationResult(
                success=len(errors) == 0,
                files=files,
                errors=errors,
                statistics=stats
            )

        except Exception as e:
            errors.append(f"Unexpected error during generation: {e}")
            return GenerationResult(
                success=False,
                files=files,
                errors=errors,
                statistics=stats
            )

    def _generate_cursorrules(
        self,
        agents: List[Agent],
        rules: List[Rule],
        project: Project,
        output_dir: Path
    ) -> FileOutput:
        """
        Generate .cursorrules file from AGENTS.md transformation.

        Cursor doesn't support agents, so we convert them to plain text
        "expert mode" instructions grouped by functional category.

        Args:
            agents: All agents from database
            rules: All active rules from database
            project: Project metadata
            output_dir: Project root directory

        Returns:
            FileOutput for .cursorrules file
        """
        # Group agents by functional category for better organization
        agents_by_category = self._group_agents_by_category(agents)

        # Prepare template context
        context = {
            "project": {
                "name": project.name,
                "description": project.description,
                "tech_stack": project.tech_stack or [],
            },
            "rules": rules,
            "agents_by_category": agents_by_category,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Render template
        content = self._render_template("cursorrules.j2", context)

        # Write file
        file_path = output_dir / ".cursorrules"
        file_path.write_text(content, encoding="utf-8")

        # Return file output
        return FileOutput.create_from_content(file_path, content)

    def _generate_cursorignore(self, output_dir: Path) -> FileOutput:
        """
        Generate .cursorignore file from CommonExclusions.

        Args:
            output_dir: Project root directory

        Returns:
            FileOutput for .cursorignore file
        """
        # Get Cursor-specific exclusions
        exclusions = CommonExclusions.CURSOR

        # Prepare template context
        context = {
            "exclusions": exclusions,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Render template
        content = self._render_template("cursorignore.j2", context)

        # Write file
        file_path = output_dir / ".cursorignore"
        file_path.write_text(content, encoding="utf-8")

        # Return file output
        return FileOutput.create_from_content(file_path, content)

    def _group_agents_by_category(
        self, agents: List[Agent]
    ) -> Dict[str, List[Agent]]:
        """
        Group agents by functional category for template rendering.

        Args:
            agents: All agents from database

        Returns:
            Dictionary mapping category name to list of agents
        """
        grouped: Dict[str, List[Agent]] = {
            "planning": [],
            "implementation": [],
            "testing": [],
            "documentation": [],
            "utilities": [],
        }

        for agent in agents:
            if not agent.is_active:
                continue

            category = agent.functional_category
            if category is None:
                # Default to utilities if no category
                grouped["utilities"].append(agent)
            else:
                category_name = category.value if hasattr(category, 'value') else str(category)
                if category_name in grouped:
                    grouped[category_name].append(agent)
                else:
                    # Fallback for unknown categories
                    grouped["utilities"].append(agent)

        return grouped

    def validate_config(self, config_dir: Path) -> List[str]:
        """
        Validate existing Cursor configuration.

        Checks that:
        - .cursorrules file exists
        - .cursorrules is valid UTF-8 plain text
        - .cursorignore exists (optional)

        Args:
            config_dir: Project root directory (not a subdirectory for Cursor)

        Returns:
            List of validation error messages (empty list if valid)

        Example:
            >>> errors = generator.validate_config(Path("/project"))
            >>> if errors:
            ...     print(f"Configuration errors: {errors}")
        """
        errors: List[str] = []

        # Check .cursorrules exists
        cursorrules_path = config_dir / ".cursorrules"
        if not cursorrules_path.exists():
            errors.append(".cursorrules file not found")
        else:
            # Validate UTF-8 encoding
            try:
                cursorrules_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(".cursorrules is not valid UTF-8")
            except Exception as e:
                errors.append(f".cursorrules read error: {e}")

        # .cursorignore is optional, but validate if present
        cursorignore_path = config_dir / ".cursorignore"
        if cursorignore_path.exists():
            try:
                cursorignore_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(".cursorignore is not valid UTF-8")
            except Exception as e:
                errors.append(f".cursorignore read error: {e}")

        return errors

    def format_context(
        self,
        project: Project,
        work_item: Optional[Any],
        task: Optional[Any]
    ) -> str:
        """
        Format APM context for real-time updates in Cursor format.

        Creates a plain text context block that can be appended to .cursorrules
        for session-specific context.

        Args:
            project: Project metadata
            work_item: Optional current work item
            task: Optional current task

        Returns:
            Formatted context string in plain text format

        Example:
            >>> context = generator.format_context(project, work_item, task)
            >>> print(context)
            === CURRENT CONTEXT ===
            Project: MyApp
            Work Item: #123 - Implement feature X
            Task: #456 - Write unit tests
        """
        lines = ["", "=== CURRENT CONTEXT ==="]

        # Project info
        lines.append(f"Project: {project.name}")
        if project.description:
            lines.append(f"Description: {project.description}")

        # Work item info (if present)
        if work_item:
            lines.append("")
            lines.append(f"Work Item: #{work_item.id} - {work_item.name}")
            if hasattr(work_item, 'phase') and work_item.phase:
                lines.append(f"Phase: {work_item.phase}")
            if hasattr(work_item, 'status') and work_item.status:
                lines.append(f"Status: {work_item.status}")

        # Task info (if present)
        if task:
            lines.append("")
            lines.append(f"Task: #{task.id} - {task.name}")
            if hasattr(task, 'type') and task.type:
                lines.append(f"Type: {task.type}")
            if hasattr(task, 'status') and task.status:
                lines.append(f"Status: {task.status}")

        lines.append("=" * 40)
        lines.append("")

        return "\n".join(lines)
