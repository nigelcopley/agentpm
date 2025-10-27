"""
AGENTS.md Generator - Universal Agent Directory Format

Generates the universal AGENTS.md instruction format from database.
This is the critical linchpin file that all provider-specific generators transform.

Architecture:
- Database-first: Queries agents, rules, work items, tasks from database
- Universal format: Provider-agnostic AGENTS.md structure
- Flat agent model: Single-level subagent directory organized by function
- YAML frontmatter: Metadata for provider transformation
- Conditional blocks: Provider-specific instructions

Pattern: Generator class with database service dependency
Output: AGENTS.md with YAML frontmatter + markdown sections

Reference:
- Document #218: AGENTS.md Flat Architecture Specification
- agentpm/providers/common/patterns.py: UniversalContext
- agentpm/core/database/enums/types.py: AgentFunctionalCategory

Usage:
    generator = AGENTSMDGenerator(db_service)
    content = generator.generate(project_id=1, provider="claude-code")

    # Optionally write to file
    generator.generate(
        project_id=1,
        output_path=Path(".claude/AGENTS.md"),
        provider="claude-code"
    )
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import agents as agent_methods
from agentpm.core.database.methods import rules as rule_methods
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import work_items as work_item_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.models import Agent, Rule, Project, WorkItem, Task
from agentpm.core.database.enums import AgentFunctionalCategory
from agentpm.providers.common.patterns import (
    UniversalContext,
    ProjectContext,
    WorkItemContext,
    TaskContext,
    CommonRuleCategories,
)


logger = logging.getLogger(__name__)


class AGENTSMDGenerator:
    """
    Generates universal AGENTS.md format from database.

    This generator produces the canonical agent directory format that all
    provider-specific generators transform into their native formats:
    - Claude Code: AGENTS.md → CLAUDE.md
    - Cursor: AGENTS.md → .cursorrules
    - OpenAI Codex: AGENTS.md (native)
    - Google Gemini: AGENTS.md → project_instructions.md

    The output includes:
    - YAML frontmatter (metadata)
    - Flat agent directory (organized by functional_category)
    - Development standards (rules from database)
    - Current work context (active work item + task)
    - Provider-specific conditional blocks

    Attributes:
        db: DatabaseService instance for database queries
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize generator with database service.

        Args:
            db_service: DatabaseService instance for database access
        """
        self.db = db_service
        self.logger = logging.getLogger(__name__)

    def generate(
        self,
        project_id: int,
        output_path: Optional[Path] = None,
        provider: str = "claude-code",
    ) -> str:
        """
        Generate AGENTS.md content from database.

        Queries database for:
        - Active agents (with functional_category)
        - Active rules (organized by category)
        - Project metadata (name, description, tech_stack)
        - Current work item (if status='active')
        - Current task (if status='in_progress')

        Args:
            project_id: Project ID to generate for
            output_path: Optional path to write generated content
            provider: Provider name for conditional blocks (default: 'claude-code')

        Returns:
            Generated AGENTS.md content as string

        Raises:
            ValueError: If project_id not found

        Example:
            >>> generator = AGENTSMDGenerator(db_service)
            >>> content = generator.generate(project_id=1)
            >>> print(content[:100])
            ---
            version: "1.0"
            architecture: flat
            ...
        """
        self.logger.info(f"Generating AGENTS.md for project_id={project_id}, provider={provider}")

        # Build universal context from database
        context = self._build_universal_context(project_id, provider)

        # Generate AGENTS.md sections
        content = self._generate_frontmatter(context)
        content += self._generate_header(context)
        content += self._generate_agent_directory(context)
        content += self._generate_development_standards(context)
        content += self._generate_work_context(context)
        content += self._generate_provider_instructions(context, provider)

        # Optionally write to file
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Wrote AGENTS.md to {output_path}")

        return content

    def _build_universal_context(self, project_id: int, provider: str) -> UniversalContext:
        """
        Build UniversalContext from database queries.

        Queries all necessary entities to populate the universal context:
        - Project (metadata, tech_stack, frameworks)
        - Agents (active only, with functional_category)
        - Rules (enabled only, organized by category)
        - Work item (current active, if any)
        - Task (current in_progress, if any)

        Args:
            project_id: Project ID to query
            provider: Provider name for context

        Returns:
            UniversalContext with all database entities

        Raises:
            ValueError: If project not found
        """
        # Query project
        project = project_methods.get_project(self.db, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Query agents (active only)
        agents = agent_methods.list_agents(self.db, project_id=project_id, active_only=True)
        self.logger.info(f"Loaded {len(agents)} active agents")

        # Query rules (enabled only)
        rules = rule_methods.list_rules(self.db, project_id=project_id, enabled_only=True)
        self.logger.info(f"Loaded {len(rules)} enabled rules")

        # Query current work item (active status)
        work_items = work_item_methods.list_work_items(
            self.db,
            project_id=project_id,
            status=None  # Get all, filter active in Python to avoid enum issues
        )
        work_items = [wi for wi in work_items if wi.status == 'active'] if work_items else []
        current_work_item = work_items[0] if work_items else None

        # Query current task (active status)
        # list_tasks doesn't accept project_id, only work_item_id
        # Get active task from current work item if available
        current_task = None
        if current_work_item:
            tasks = task_methods.list_tasks(
                self.db,
                work_item_id=current_work_item.id,
                status=None
            )
            active_tasks = [t for t in tasks if t.status == 'active'] if tasks else []
            current_task = active_tasks[0] if active_tasks else None

        # Build project context
        project_context = ProjectContext(
            id=project.id,
            name=project.name,
            description=project.description,
            tech_stack=project.tech_stack or [],
            frameworks=project.detected_frameworks or [],
            root_path=str(project.path) if project.path else None,
        )

        # Build work item context (if exists)
        work_item_context = None
        if current_work_item:
            work_item_context = WorkItemContext(
                id=current_work_item.id,
                name=current_work_item.name,
                type=current_work_item.type.value,
                status=current_work_item.status.value,
                phase=current_work_item.phase.value if current_work_item.phase else None,
                business_context=current_work_item.business_context,
                effort_estimate_hours=current_work_item.effort_estimate_hours,
                priority=current_work_item.priority,
            )

        # Build task context (if exists)
        task_context = None
        if current_task:
            task_context = TaskContext(
                id=current_task.id,
                name=current_task.name,
                type=current_task.type.value,
                status=current_task.status.value,
                description=current_task.description,
                effort_hours=current_task.effort_hours,
                priority=current_task.priority,
                assigned_to=current_task.assigned_to,
                quality_metadata=current_task.quality_metadata,
            )

        # Build universal context
        return UniversalContext(
            version="1.0",
            project=project_context,
            generated=datetime.utcnow(),
            providers=[provider],
            work_item=work_item_context,
            task=task_context,
            rules=rules,
            agents=agents,
            tech_stack=project.tech_stack or [],
            detected_frameworks=project.detected_frameworks or [],
        )

    def _generate_frontmatter(self, context: UniversalContext) -> str:
        """
        Generate YAML frontmatter with metadata.

        Frontmatter includes:
        - version: Format version (1.0)
        - architecture: Agent model (flat)
        - generated: ISO timestamp
        - project: id, name, tech_stack

        Args:
            context: UniversalContext with project data

        Returns:
            YAML frontmatter as string
        """
        tech_stack_yaml = ', '.join(f'"{tech}"' for tech in context.tech_stack)

        frontmatter = f"""---
version: "{context.version}"
architecture: flat
generated: {context.generated.isoformat()}Z
project:
  id: {context.project.id}
  name: "{context.project.name}"
  tech_stack: [{tech_stack_yaml}]
---

"""
        return frontmatter

    def _generate_header(self, context: UniversalContext) -> str:
        """
        Generate header section with summary statistics.

        Args:
            context: UniversalContext with agent/rule counts

        Returns:
            Header markdown
        """
        header = f"""# APM Agent System

**Project**: {context.project.name}
**Total Active Agents**: {len(context.agents)}
**Active Rules**: {len(context.rules)}
**Generated**: {context.generated.strftime('%Y-%m-%d %H:%M:%S')} UTC

---

"""
        return header

    def _generate_agent_directory(self, context: UniversalContext) -> str:
        """
        Generate flat agent directory organized by functional category.

        Groups agents by AgentFunctionalCategory enum:
        - planning: Orchestrators, planners, framers
        - implementation: Developers, implementers, builders
        - testing: Test specialists, verifiers, quality analyzers
        - documentation: Documentation writers, curators
        - utilities: Support agents, helpers

        Args:
            context: UniversalContext with agent list

        Returns:
            Agent directory markdown
        """
        content = "## Subagent Directory (Flat - Organized by Function)\n\n"

        # Group agents by functional_category
        by_category: Dict[str, List[Agent]] = {}
        uncategorized: List[Agent] = []

        for agent in context.agents:
            category = agent.functional_category
            if category:
                # Convert enum to string value
                category_key = category.value if hasattr(category, 'value') else str(category)
                if category_key not in by_category:
                    by_category[category_key] = []
                by_category[category_key].append(agent)
            else:
                uncategorized.append(agent)

        # Category order and display names
        category_order = [
            AgentFunctionalCategory.PLANNING.value,
            AgentFunctionalCategory.IMPLEMENTATION.value,
            AgentFunctionalCategory.TESTING.value,
            AgentFunctionalCategory.DOCUMENTATION.value,
            AgentFunctionalCategory.UTILITIES.value,
        ]

        category_labels = {
            AgentFunctionalCategory.PLANNING.value: "Planning & Analysis",
            AgentFunctionalCategory.IMPLEMENTATION.value: "Implementation",
            AgentFunctionalCategory.TESTING.value: "Testing & Quality",
            AgentFunctionalCategory.DOCUMENTATION.value: "Documentation",
            AgentFunctionalCategory.UTILITIES.value: "Utilities",
        }

        # Generate sections by category
        for category in category_order:
            if category not in by_category:
                continue

            agents_in_category = sorted(by_category[category], key=lambda a: a.role)
            label = category_labels.get(category, category.title())

            content += f"### {label} ({len(agents_in_category)})\n\n"

            for agent in agents_in_category:
                # Format: - **role**: Display Name - Description (first line, max 150 chars)
                desc = ""
                if agent.description:
                    desc = agent.description.split('\n')[0][:150]
                    if len(agent.description.split('\n')[0]) > 150:
                        desc += "..."

                content += f"- **{agent.role}**: {agent.display_name}"
                if desc:
                    content += f" - {desc}"
                content += "\n"

            content += "\n"

        # Uncategorized agents (if any)
        if uncategorized:
            content += f"### Uncategorized ({len(uncategorized)})\n\n"
            for agent in sorted(uncategorized, key=lambda a: a.role):
                desc = ""
                if agent.description:
                    desc = agent.description.split('\n')[0][:150]
                content += f"- **{agent.role}**: {agent.display_name}"
                if desc:
                    content += f" - {desc}"
                content += "\n"
            content += "\n"

        return content

    def _generate_development_standards(self, context: UniversalContext) -> str:
        """
        Generate Development Standards section with rules organized by category.

        Groups rules by category (from CommonRuleCategories):
        - development_principles (Architecture Rules)
        - testing_standards (Testing Rules)
        - security_requirements (Security Rules)
        - documentation_standards (Documentation Rules)
        - workflow_governance (Workflow Rules)
        - code_quality (Code Quality)
        - performance_requirements (Performance)
        - continuous_integration (CI/CD)

        Args:
            context: UniversalContext with rules list

        Returns:
            Development standards markdown
        """
        if not context.rules:
            return ""

        content = "## Development Standards\n\n"

        # Group rules by category
        by_category: Dict[str, List[Rule]] = {}
        for rule in context.rules:
            category = rule.category or "uncategorized"
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rule)

        # Category order (prioritize common categories)
        category_order = [
            CommonRuleCategories.ARCHITECTURE,
            CommonRuleCategories.TESTING,
            CommonRuleCategories.SECURITY,
            CommonRuleCategories.DOCUMENTATION,
            CommonRuleCategories.WORKFLOW,
            CommonRuleCategories.CODE_QUALITY,
            CommonRuleCategories.PERFORMANCE,
            CommonRuleCategories.CI_CD,
        ]

        # Add any other categories not in standard list
        for category in sorted(by_category.keys()):
            if category not in category_order and category != "uncategorized":
                category_order.append(category)

        # Generate sections by category
        for category in category_order:
            if category not in by_category:
                continue

            rules_in_category = sorted(by_category[category], key=lambda r: r.rule_id)
            display_name = CommonRuleCategories.get_display_name(category)

            content += f"### {display_name}\n\n"

            for rule in rules_in_category:
                # Format: - **RULE-ID** (LEVEL): Description
                content += f"- **{rule.rule_id}** ({rule.enforcement_level.value}): "
                content += f"{rule.description}\n"

            content += "\n"

        # Uncategorized rules (if any)
        if "uncategorized" in by_category:
            content += "### Other Rules\n\n"
            for rule in sorted(by_category["uncategorized"], key=lambda r: r.rule_id):
                content += f"- **{rule.rule_id}** ({rule.enforcement_level.value}): "
                content += f"{rule.description}\n"
            content += "\n"

        return content

    def _generate_work_context(self, context: UniversalContext) -> str:
        """
        Generate Current Work Context section.

        Includes:
        - Current work item (if active)
        - Current task (if in_progress)
        - Business context and acceptance criteria

        Args:
            context: UniversalContext with work_item and task

        Returns:
            Work context markdown (empty if no active work)
        """
        if not context.work_item and not context.task:
            return ""

        content = "## Current Work Context\n\n"

        if context.work_item:
            wi = context.work_item
            content += f"### Active Work Item: #{wi.id}\n\n"
            content += f"**Name**: {wi.name}  \n"
            content += f"**Type**: {wi.type}  \n"
            content += f"**Status**: {wi.status}  \n"
            if wi.phase:
                content += f"**Phase**: {wi.phase}  \n"
            content += f"**Priority**: {wi.priority}  \n"
            if wi.effort_estimate_hours:
                content += f"**Effort Estimate**: {wi.effort_estimate_hours} hours  \n"

            if wi.business_context:
                content += f"\n**Business Context**:\n{wi.business_context}\n"

            content += "\n"

        if context.task:
            task = context.task
            content += f"### Current Task: #{task.id}\n\n"
            content += f"**Name**: {task.name}  \n"
            content += f"**Type**: {task.type}  \n"
            content += f"**Status**: {task.status}  \n"
            content += f"**Priority**: {task.priority}  \n"
            if task.effort_hours:
                content += f"**Effort**: {task.effort_hours} hours  \n"
            if task.assigned_to:
                content += f"**Assigned To**: {task.assigned_to}  \n"

            if task.description:
                content += f"\n**Description**:\n{task.description}\n"

            if task.quality_metadata:
                content += f"\n**Quality Metadata**:\n```json\n{task.quality_metadata}\n```\n"

            content += "\n"

        return content

    def _generate_provider_instructions(self, context: UniversalContext, provider: str) -> str:
        """
        Generate provider-specific instruction blocks.

        Uses HTML comments for conditional blocks:
        - <!-- [CLAUDE_CODE] --> ... <!-- [/CLAUDE_CODE] -->
        - <!-- [CURSOR] --> ... <!-- [/CURSOR] -->
        - <!-- [CODEX] --> ... <!-- [/CODEX] -->
        - <!-- [GEMINI] --> ... <!-- [/GEMINI] -->

        Args:
            context: UniversalContext (for agent counts)
            provider: Provider name

        Returns:
            Provider-specific instructions markdown
        """
        content = "## Provider-Specific Instructions\n\n"

        # Claude Code instructions
        content += "<!-- [CLAUDE_CODE] -->\n"
        content += "### Claude Code\n\n"
        content += "Use the Task tool for all subagent delegation:\n\n"
        content += "```python\n"
        content += "Task(\n"
        content += '  subagent_type="agent-role",  # From directory above\n'
        content += '  description="Brief task summary",\n'
        content += '  prompt="Detailed instructions for the agent"\n'
        content += ")\n"
        content += "```\n\n"
        content += "**Example**:\n"
        content += "```python\n"
        content += "Task(\n"
        content += '  subagent_type="aipm-python-cli-developer",\n'
        content += '  description="Implement CLI command",\n'
        content += '  prompt="Create `apm context show` command that displays current work context"\n'
        content += ")\n"
        content += "```\n"
        content += "<!-- [/CLAUDE_CODE] -->\n\n"

        # Cursor instructions
        content += "<!-- [CURSOR] -->\n"
        content += "### Cursor\n\n"
        content += "Cursor does not support subagent delegation. Use the agent directory as a "
        content += "reference for expert personas and capabilities. When implementing tasks, "
        content += "adopt the role and follow the SOP of the most relevant agent.\n"
        content += "<!-- [/CURSOR] -->\n\n"

        # OpenAI Codex instructions
        content += "<!-- [CODEX] -->\n"
        content += "### OpenAI Codex\n\n"
        content += "Use the `codex` CLI for subagent orchestration:\n\n"
        content += "```bash\n"
        content += 'codex --yolo exec "Invoke agent: agent-role\n'
        content += 'Task: [description]\n'
        content += 'Instructions: [detailed prompt]"\n'
        content += "```\n\n"
        content += "**Example**:\n"
        content += "```bash\n"
        content += 'codex --yolo exec "Invoke agent: aipm-testing-specialist\n'
        content += 'Task: Create test suite\n'
        content += 'Instructions: Generate comprehensive unit tests for WorkItem model"\n'
        content += "```\n"
        content += "<!-- [/CODEX] -->\n\n"

        # Google Gemini instructions
        content += "<!-- [GEMINI] -->\n"
        content += "### Google Gemini\n\n"
        content += "Use natural language delegation with explicit agent reference:\n\n"
        content += "```\n"
        content += "Delegate to [agent-role]:\n"
        content += "[Detailed instructions]\n"
        content += "```\n\n"
        content += "The system will route your request to the appropriate agent based on "
        content += "the role reference and task description.\n"
        content += "<!-- [/GEMINI] -->\n\n"

        return content
