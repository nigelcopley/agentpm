"""
Claude Code Generator with Jinja2 Template System

Generates Claude Code configuration files from APM database entities.
Replaces f-string-based subagents.py (7,546 LOC) with template-driven approach (~500 LOC).

Architecture:
- ClaudeCodeGenerator: Main generator class implementing BaseProviderGenerator
- TemplateBasedMixin: Jinja2 template rendering support
- Template files: Reusable Jinja2 templates for all configuration files

Pattern: Template Method Pattern with Strategy Pattern for rendering
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

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
from agentpm.providers.anthropic.claude_code.skill_generator import SkillGenerator
from agentpm.providers.anthropic.claude_code.memory_generator import MemoryGenerator


class ClaudeCodeGenerator(BaseProviderGenerator, TemplateBasedMixin):
    """
    Claude Code configuration generator using Jinja2 templates.

    Generates provider-native configuration from APM database:
    - CLAUDE.md: Master orchestrator documentation
    - .claude/agents/*.md: Individual agent files with YAML frontmatter
    - .claude/hooks/*.py: Python hooks for session start and pre-tool-use
    - .claude/settings.json: Claude Code configuration
    - .claude/memory/**/*.md: Structured memory files (decisions, learnings, patterns, context)

    Design Principles:
    - Template-driven: All formatting in Jinja2 templates
    - Database-first: All data from database, not files
    - Single Responsibility: Each method has one clear purpose
    - Open/Closed: Extensible via templates without code changes

    Example:
        >>> db = DatabaseService("path/to/db")
        >>> generator = ClaudeCodeGenerator(db)
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
        Initialize Claude Code generator.

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

        # Register custom filters
        self._register_custom_filters()

        # Initialize skill generator
        self.skill_generator = SkillGenerator(db_service)

        # Initialize memory generator
        self.memory_generator = MemoryGenerator(db_service)

    @property
    def provider_name(self) -> str:
        """Provider identifier."""
        return "claude-code"

    @property
    def config_directory(self) -> str:
        """Native configuration directory."""
        return ".claude"

    def generate_from_agents(
        self,
        agents: List[Agent],
        rules: List[Rule],
        project: Project,
        output_dir: Path,
        **kwargs
    ) -> GenerationResult:
        """
        Generate Claude Code configuration files from database entities.

        Creates the following structure:
        - output_dir/CLAUDE.md (master documentation)
        - output_dir/.claude/agents/*.md (agent files)
        - output_dir/.claude/hooks/session-start.py
        - output_dir/.claude/hooks/pre-tool-use.py
        - output_dir/.claude/settings.json

        Args:
            agents: Flat list of all agents from database
            rules: All active rules from database
            project: Project metadata
            output_dir: Project root directory
            **kwargs: Optional parameters:
                - include_hooks (bool): Generate hooks (default: True)
                - include_settings (bool): Generate settings.json (default: True)
                - include_memory (bool): Generate memory files (default: True)
                - include_decisions (bool): Include decision files (default: True)
                - include_learnings (bool): Include learning files (default: True)
                - include_patterns (bool): Include pattern files (default: True)
                - include_context (bool): Include context file (default: True)
                - resolve_imports (bool): Resolve @import directives (default: True)

        Returns:
            GenerationResult with success status, files, and statistics

        Example:
            >>> result = generator.generate_from_agents(
            ...     agents=[agent1, agent2],
            ...     rules=[rule1, rule2],
            ...     project=project,
            ...     output_dir=Path("/project"),
            ...     include_hooks=True
            ... )
        """
        errors: List[str] = []
        files: List[FileOutput] = []
        stats: Dict[str, Any] = {
            "agents_generated": 0,
            "skills_generated": 0,
            "rules_included": len(rules),
            "duration_ms": 0,
            "generation_time": datetime.utcnow().isoformat()
        }

        start_time = datetime.utcnow()

        try:
            # Create .claude directory
            claude_dir = output_dir / self.config_directory
            claude_dir.mkdir(parents=True, exist_ok=True)

            # 1. Generate CLAUDE.md
            try:
                claude_md_file = self._generate_claude_md(
                    agents=agents,
                    rules=rules,
                    project=project,
                    output_dir=output_dir
                )
                files.append(claude_md_file)
            except Exception as e:
                errors.append(f"CLAUDE.md generation failed: {e}")

            # 2. Generate agent files
            try:
                agent_files = self._generate_agent_files(
                    agents=agents,
                    rules=rules,
                    output_dir=claude_dir
                )
                files.extend(agent_files)
                stats["agents_generated"] = len(agent_files)
            except Exception as e:
                errors.append(f"Agent files generation failed: {e}")

            # 3. Generate hooks (optional)
            if kwargs.get("include_hooks", True):
                try:
                    hook_files = self._generate_hooks(
                        project=project,
                        output_dir=claude_dir
                    )
                    files.extend(hook_files)
                except Exception as e:
                    errors.append(f"Hooks generation failed: {e}")

            # 4. Generate settings.json (optional)
            if kwargs.get("include_settings", True):
                try:
                    settings_file = self._generate_settings(
                        project=project,
                        output_dir=claude_dir
                    )
                    files.append(settings_file)
                except Exception as e:
                    errors.append(f"Settings generation failed: {e}")

            # 5. Generate skill files (optional)
            if kwargs.get("include_skills", True):
                try:
                    skills_dir = claude_dir / "skills"
                    skill_files = self.skill_generator.generate_skill_files(
                        output_dir=skills_dir
                    )
                    files.extend(skill_files)
                    stats["skills_generated"] = len(skill_files)
                except Exception as e:
                    errors.append(f"Skills generation failed: {e}")

            # 6. Generate memory files (optional)
            if kwargs.get("include_memory", True):
                try:
                    memory_files = self.memory_generator.generate_memory_files(
                        project=project,
                        output_dir=claude_dir,
                        include_decisions=kwargs.get("include_decisions", True),
                        include_learnings=kwargs.get("include_learnings", True),
                        include_patterns=kwargs.get("include_patterns", True),
                        include_context=kwargs.get("include_context", True),
                        resolve_imports=kwargs.get("resolve_imports", True)
                    )
                    files.extend(memory_files)
                    stats["memory_files_generated"] = len(memory_files)
                except Exception as e:
                    errors.append(f"Memory generation failed: {e}")

            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            stats["duration_ms"] = int(duration)

            return GenerationResult(
                success=len(errors) == 0,
                files=files,
                errors=errors,
                statistics=stats
            )

        except Exception as e:
            errors.append(f"Generation failed: {e}")
            return GenerationResult(
                success=False,
                files=files,
                errors=errors,
                statistics=stats
            )

    def validate_config(self, config_dir: Path) -> List[str]:
        """
        Validate existing Claude Code configuration.

        Checks:
        - .claude directory exists
        - CLAUDE.md exists in parent directory
        - Required subdirectories exist (agents, hooks, settings)
        - Agent files have valid YAML frontmatter

        Args:
            config_dir: Path to .claude directory

        Returns:
            List of validation error messages (empty if valid)

        Example:
            >>> errors = generator.validate_config(Path("/project/.claude"))
            >>> if errors:
            ...     print(f"Configuration errors: {errors}")
        """
        errors: List[str] = []

        # Check .claude directory exists
        if not config_dir.exists():
            errors.append(f"Configuration directory not found: {config_dir}")
            return errors

        if not config_dir.is_dir():
            errors.append(f"Configuration path is not a directory: {config_dir}")
            return errors

        # Check CLAUDE.md in parent directory
        claude_md = config_dir.parent / "CLAUDE.md"
        if not claude_md.exists():
            errors.append(f"CLAUDE.md not found at: {claude_md}")

        # Check required subdirectories
        agents_dir = config_dir / "agents"
        if not agents_dir.exists():
            errors.append(f"Agents directory not found: {agents_dir}")
        elif not agents_dir.is_dir():
            errors.append(f"Agents path is not a directory: {agents_dir}")

        hooks_dir = config_dir / "hooks"
        if not hooks_dir.exists():
            # Not an error - hooks are optional
            pass
        elif not hooks_dir.is_dir():
            errors.append(f"Hooks path is not a directory: {hooks_dir}")

        # Check settings.json
        settings_file = config_dir / "settings.local.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid settings.json: {e}")

        # Validate agent files have YAML frontmatter
        if agents_dir.exists() and agents_dir.is_dir():
            agent_files = list(agents_dir.glob("*.md"))
            if not agent_files:
                errors.append(f"No agent files found in: {agents_dir}")
            else:
                for agent_file in agent_files:
                    try:
                        content = agent_file.read_text()
                        if not content.startswith("---\n"):
                            errors.append(
                                f"Agent file missing YAML frontmatter: {agent_file.name}"
                            )
                    except Exception as e:
                        errors.append(f"Error reading agent file {agent_file.name}: {e}")

        return errors

    def format_context(
        self,
        project: Project,
        work_item: Optional[Any],
        task: Optional[Any]
    ) -> str:
        """
        Format APM context for real-time updates in Claude Code format.

        Creates a markdown-formatted context block for injection into
        Claude Code sessions via hooks.

        Args:
            project: Project metadata
            work_item: Optional current work item
            task: Optional current task

        Returns:
            Formatted markdown context string

        Example:
            >>> context = generator.format_context(project, work_item, task)
            >>> print(context)
            ## Current Context
            - Project: MyApp
            - Work Item: #123 - Implement feature X
            - Task: #456 - Write unit tests
        """
        lines = []
        lines.append("## Current Context")
        lines.append("")
        lines.append(f"**Project**: {project.name}")
        lines.append(f"**Status**: {project.status.value}")
        lines.append("")

        if work_item:
            lines.append("**Current Work Item**:")
            lines.append(f"- ID: {work_item.id}")
            lines.append(f"- Name: {work_item.name}")
            lines.append(f"- Type: {work_item.type.value}")
            lines.append(f"- Status: {work_item.status.value}")
            lines.append(f"- Phase: {work_item.phase.value if work_item.phase else 'None'}")
            lines.append("")

        if task:
            lines.append("**Current Task**:")
            lines.append(f"- ID: {task.id}")
            lines.append(f"- Name: {task.name}")
            lines.append(f"- Type: {task.type.value}")
            lines.append(f"- Status: {task.status.value}")
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # Private Generation Methods
    # ========================================================================

    def _generate_claude_md(
        self,
        agents: List[Agent],
        rules: List[Rule],
        project: Project,
        output_dir: Path
    ) -> FileOutput:
        """
        Generate CLAUDE.md master documentation.

        Uses claude_md.j2 template to transform AGENTS.md content:
        - Remove YAML frontmatter
        - Extract [CLAUDE_CODE] conditional blocks
        - Emphasize Task tool delegation
        - Organize agents by functional category

        Args:
            agents: All agents from database
            rules: All active rules
            project: Project metadata
            output_dir: Project root directory

        Returns:
            FileOutput with CLAUDE.md metadata
        """
        # Group agents by functional category
        agents_by_category = self._group_agents_by_category(agents)

        # Render template
        context = {
            "project": project,
            "agents": agents,
            "agents_by_category": agents_by_category,
            "rules": rules,
            "generation_time": datetime.utcnow().isoformat()
        }

        content = self._render_template("claude_md.j2", context)

        # Write file
        output_path = output_dir / "CLAUDE.md"
        output_path.write_text(content)

        return FileOutput.create_from_content(output_path, content)

    def _generate_agent_files(
        self,
        agents: List[Agent],
        rules: List[Rule],
        output_dir: Path
    ) -> List[FileOutput]:
        """
        Generate individual agent files in .claude/agents/.

        Each agent file contains:
        - YAML frontmatter (name, description, tools, skills)
        - Agent description and responsibilities
        - Skills section (if agent has skills)
        - Agent-specific guidance (reduced SOP)
        - Quality standards and workflow integration

        Args:
            agents: All agents from database
            rules: All active rules
            output_dir: .claude directory path

        Returns:
            List of FileOutput for each agent file
        """
        files: List[FileOutput] = []
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        for agent in agents:
            if not agent.is_active:
                continue

            # Query agent skills (metadata only for performance)
            try:
                from agentpm.core.database.methods.skills import get_agent_skills
                agent_skills = get_agent_skills(self.db, agent.id, metadata_only=False)
            except Exception:
                # If skills table doesn't exist yet (Task 1131 not complete), default to empty
                agent_skills = []

            # Render agent template
            context = {
                "agent": agent,
                "agent_skills": agent_skills,
                "rules": rules,
                "generation_time": datetime.utcnow().isoformat()
            }

            content = self._render_template("agent.md.j2", context)

            # Write file
            output_path = agents_dir / f"{agent.role}.md"
            output_path.write_text(content)

            files.append(FileOutput.create_from_content(output_path, content))

        return files

    def _generate_hooks(
        self,
        project: Project,
        output_dir: Path
    ) -> List[FileOutput]:
        """
        Generate Python hooks for Claude Code.

        Creates:
        - session-start.py: Load APM context at session start
        - pre-tool-use.py: Validate operations before tool execution

        Args:
            project: Project metadata
            output_dir: .claude directory path

        Returns:
            List of FileOutput for hook files
        """
        files: List[FileOutput] = []
        hooks_dir = output_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Session start hook
        context = {
            "project": project,
            "generation_time": datetime.utcnow().isoformat()
        }

        session_start_content = self._render_template(
            "hooks/session-start.py.j2",
            context
        )
        session_start_path = hooks_dir / "session-start.py"
        session_start_path.write_text(session_start_content)
        files.append(FileOutput.create_from_content(session_start_path, session_start_content))

        # Pre-tool-use hook
        pre_tool_use_content = self._render_template(
            "hooks/pre-tool-use.py.j2",
            context
        )
        pre_tool_use_path = hooks_dir / "pre-tool-use.py"
        pre_tool_use_path.write_text(pre_tool_use_content)
        files.append(FileOutput.create_from_content(pre_tool_use_path, pre_tool_use_content))

        return files

    def _generate_settings(
        self,
        project: Project,
        output_dir: Path
    ) -> FileOutput:
        """
        Generate settings.local.json for Claude Code.

        Contains:
        - Hook configuration
        - Model settings
        - Permissions
        - Telemetry settings

        Args:
            project: Project metadata
            output_dir: .claude directory path

        Returns:
            FileOutput for settings.local.json
        """
        context = {
            "project": project,
            "generation_time": datetime.utcnow().isoformat()
        }

        content = self._render_template("settings.json.j2", context)

        # Write file
        output_path = output_dir / "settings.local.json"
        output_path.write_text(content)

        return FileOutput.create_from_content(output_path, content)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _group_agents_by_category(
        self,
        agents: List[Agent]
    ) -> Dict[str, List[Agent]]:
        """
        Group agents by functional category.

        Args:
            agents: All agents from database

        Returns:
            Dictionary mapping category names to agent lists

        Example:
            >>> groups = self._group_agents_by_category(agents)
            >>> print(groups.keys())
            dict_keys(['planning', 'implementation', 'testing', 'documentation', 'utilities'])
        """
        groups: Dict[str, List[Agent]] = {}

        for agent in agents:
            if not agent.is_active:
                continue

            # Use functional_category if available, fallback to "utilities"
            category = (
                agent.functional_category.value
                if agent.functional_category
                else "utilities"
            )

            if category not in groups:
                groups[category] = []

            groups[category].append(agent)

        # Sort agents within each category by role
        for category in groups:
            groups[category].sort(key=lambda a: a.role)

        return groups

    def _register_custom_filters(self) -> None:
        """
        Register Claude Code-specific Jinja2 filters.

        Custom filters:
        - format_frontmatter: Format YAML frontmatter
        - format_rules: Format rules for agent files
        - format_capabilities: Format agent capabilities
        """
        super()._register_custom_filters()

        # Register custom filters
        self.env.filters['format_frontmatter'] = self._format_frontmatter
        self.env.filters['format_rules'] = self._format_rules
        self.env.filters['format_capabilities'] = self._format_capabilities

    @staticmethod
    def _format_frontmatter(agent: Agent) -> str:
        """
        Format YAML frontmatter for agent file.

        Args:
            agent: Agent model

        Returns:
            YAML frontmatter string
        """
        lines = ["---"]
        lines.append(f"name: {agent.role}")
        lines.append(f"description: {agent.description or agent.display_name}")

        # Tools
        if agent.capabilities:
            # Map capabilities to tools
            tools = ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
            lines.append(f"tools: {', '.join(tools)}")

        lines.append("---")
        return "\n".join(lines)

    @staticmethod
    def _format_rules(rules: List[Rule]) -> str:
        """
        Format rules for agent file.

        Args:
            rules: List of rules

        Returns:
            Formatted rules markdown
        """
        if not rules:
            return "No rules configured."

        lines = []
        for rule in rules[:10]:  # Limit to top 10
            lines.append(f"- **{rule.rule_id}**: {rule.name}")

        return "\n".join(lines)

    @staticmethod
    def _format_capabilities(capabilities: List[str]) -> str:
        """
        Format agent capabilities.

        Args:
            capabilities: List of capability strings

        Returns:
            Formatted capabilities markdown
        """
        if not capabilities:
            return "No capabilities defined."

        return "\n".join(f"- {cap}" for cap in capabilities)
