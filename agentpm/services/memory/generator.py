"""
Memory File Generator

Core service for generating Claude's persistent memory files from APM (Agent Project Manager) database.
Part of WI-114: Claude Persistent Memory System.

This generator creates structured markdown files that provide Claude with
always-current access to:
- Rules: Governance rules system
- Principles: Development principles pyramid
- Workflow: Quality-gated workflow processes
- Agents: Agent system architecture
- Context: Context assembly framework
- Project: Project information and metadata
- Ideas: Ideas analysis pipeline
"""

import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.memory import MemoryFile, MemoryFileType, ValidationStatus
from agentpm.core.database.methods import memory_methods


class MemoryGenerator:
    """Generate and manage Claude's persistent memory files.

    This service coordinates memory file generation by:
    1. Extracting data from APM (Agent Project Manager) database tables
    2. Applying markdown templates
    3. Calculating quality scores
    4. Persisting to database
    5. Writing files to .claude/ directory
    """

    def __init__(self, db: DatabaseService, project_root: Path):
        """Initialize memory generator.

        Args:
            db: DatabaseService instance
            project_root: Path to project root directory
        """
        self.db = db
        self.project_root = project_root
        self.claude_dir = project_root / ".claude"

    def generate_memory_file(
        self,
        project_id: int,
        file_type: MemoryFileType,
        session_id: Optional[int] = None,
        force_regenerate: bool = False
    ) -> MemoryFile:
        """Generate a memory file for Claude.

        Args:
            project_id: Project ID
            file_type: Type of memory file to generate
            session_id: Optional session ID (for tracking)
            force_regenerate: Force regeneration even if current

        Returns:
            MemoryFile model with generated content

        Example:
            >>> generator = MemoryGenerator(db, Path("/project"))
            >>> memory = generator.generate_memory_file(1, MemoryFileType.RULES)
            >>> print(f"Generated {memory.file_path}")
        """
        start_time = time.time()

        # Check if current file exists and is not stale (unless forcing)
        if not force_regenerate:
            existing = memory_methods.get_memory_file_by_type(self.db, project_id, file_type)
            if existing and not existing.is_stale and not existing.is_expired:
                return existing

        # Generate content based on file type
        content, source_tables = self._generate_content_for_type(project_id, file_type)

        # Calculate file hash
        file_hash = self._calculate_hash(content)

        # Calculate quality scores
        confidence_score = self._calculate_confidence(content, source_tables)
        completeness_score = self._calculate_completeness(content, file_type)

        # Determine file path
        file_path = self._get_file_path(file_type)

        # Calculate generation duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Create memory file model
        memory_file = MemoryFile(
            project_id=project_id,
            session_id=session_id,
            file_type=file_type,
            file_path=file_path,
            file_hash=file_hash,
            content=content,
            source_tables=source_tables,
            template_version="1.0.0",
            confidence_score=confidence_score,
            completeness_score=completeness_score,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="memory-generator",
            generation_duration_ms=duration_ms,
            generated_at=datetime.now().isoformat(),
            validated_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=24)).isoformat()
        )

        # Check if file already exists for this project and type
        existing = memory_methods.get_memory_file_by_type(self.db, project_id, file_type)

        if existing:
            # Update existing record
            updates = {
                'session_id': session_id,
                'file_hash': file_hash,
                'content': content,
                'source_tables': source_tables,
                'confidence_score': confidence_score,
                'completeness_score': completeness_score,
                'validation_status': ValidationStatus.VALIDATED,
                'generation_duration_ms': duration_ms,
                'generated_at': memory_file.generated_at,
                'validated_at': memory_file.validated_at,
                'expires_at': memory_file.expires_at
            }
            memory_file = memory_methods.update_memory_file(self.db, existing.id, updates)
        else:
            # Create new record
            memory_file = memory_methods.create_memory_file(self.db, memory_file)

        # Write file to .claude/ directory
        self._write_file(file_path, content)

        return memory_file

    def generate_all_memory_files(
        self,
        project_id: int,
        session_id: Optional[int] = None
    ) -> List[MemoryFile]:
        """Generate all memory files for a project.

        Args:
            project_id: Project ID
            session_id: Optional session ID (for tracking)

        Returns:
            List of generated MemoryFile models

        Example:
            >>> generator = MemoryGenerator(db, Path("/project"))
            >>> memories = generator.generate_all_memory_files(1)
            >>> print(f"Generated {len(memories)} memory files")
        """
        memory_files = []

        for file_type in MemoryFileType:
            try:
                memory_file = self.generate_memory_file(project_id, file_type, session_id)
                memory_files.append(memory_file)
            except Exception as e:
                # Log error but continue with other files
                print(f"Error generating {file_type.value}: {e}")

        return memory_files

    def _generate_content_for_type(
        self,
        project_id: int,
        file_type: MemoryFileType
    ) -> tuple[str, List[str]]:
        """Generate content for a specific memory file type.

        Args:
            project_id: Project ID
            file_type: Type of memory file

        Returns:
            Tuple of (content, source_tables)
        """
        # Placeholder implementation - will be expanded in next tasks
        # Each file type will have its own extraction and template logic

        generators = {
            MemoryFileType.RULES: self._generate_rules_content,
            MemoryFileType.PRINCIPLES: self._generate_principles_content,
            MemoryFileType.WORKFLOW: self._generate_workflow_content,
            MemoryFileType.AGENTS: self._generate_agents_content,
            MemoryFileType.CONTEXT: self._generate_context_content,
            MemoryFileType.PROJECT: self._generate_project_content,
            MemoryFileType.IDEAS: self._generate_ideas_content,
        }

        generator = generators.get(file_type)
        if generator:
            return generator(project_id)

        # Default placeholder
        return (
            f"# {file_type.value.upper()}\n\nContent generation pending...",
            []
        )

    def _generate_rules_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate RULES.md content from rules table.

        Queries the rules table and formats as hierarchical markdown
        organized by category and enforcement level.
        """
        from agentpm.core.database.methods import rules as rules_methods

        # Query all enabled rules for this project
        all_rules = rules_methods.list_rules(self.db, project_id=project_id, enabled_only=True)

        if not all_rules:
            return (
                "# APM (Agent Project Manager) Governance Rules\n\nNo active rules found for this project.",
                ["rules"]
            )

        # Group rules by category
        rules_by_category = {}
        for rule in all_rules:
            category = rule.category or "Uncategorized"
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)

        # Build markdown content
        content = "# APM (Agent Project Manager) Governance Rules\n\n"
        content += f"**Active Rules**: {len(all_rules)}\n"
        content += f"**Categories**: {len(rules_by_category)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## Rule Categories\n\n"

        # Sort categories alphabetically
        for category in sorted(rules_by_category.keys()):
            rules_list = rules_by_category[category]
            content += f"### {category}\n\n"
            content += f"**Rules in category**: {len(rules_list)}\n\n"

            # Group by enforcement level within category
            by_enforcement = {}
            for rule in rules_list:
                level = rule.enforcement_level
                if level not in by_enforcement:
                    by_enforcement[level] = []
                by_enforcement[level].append(rule)

            # Display by enforcement level (BLOCK first, then others)
            enforcement_order = ['BLOCK', 'LIMIT', 'GUIDE', 'ENHANCE']
            for level in enforcement_order:
                if level not in by_enforcement:
                    continue

                level_rules = by_enforcement[level]
                content += f"#### {level} Level ({len(level_rules)} rules)\n\n"

                for rule in sorted(level_rules, key=lambda r: r.rule_id):
                    content += f"**{rule.rule_id}**: {rule.name}\n\n"
                    if rule.description:
                        content += f"{rule.description}\n\n"
                    if rule.error_message:
                        content += f"*Violation Message*: {rule.error_message}\n\n"
                    content += "---\n\n"

        return (content, ["rules"])

    def _generate_principles_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate PRINCIPLES.md content from development principles.

        Extracts principle-related rules (DP-* category) and formats
        as a hierarchical pyramid structure.
        """
        from agentpm.core.database.methods import rules as rules_methods

        # Query development principle rules
        all_rules = rules_methods.list_rules(self.db, project_id=project_id, enabled_only=True)
        principle_rules = [r for r in all_rules if r.category == "Development Principles"]

        content = "# Development Principles Pyramid\n\n"
        content += f"**Total Principles**: {len(principle_rules)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## Core Development Principles\n\n"

        content += "APM (Agent Project Manager) follows a structured approach to software development:\n\n"
        content += "- **Time-Boxing**: All work is time-boxed to maintain focus and prevent scope creep\n"
        content += "- **Quality Gates**: Each phase has defined entry/exit criteria\n"
        content += "- **Database-First**: Schema defines contracts, code follows schema\n"
        content += "- **Type Safety**: Pydantic models provide runtime validation\n\n"

        content += "---\n\n"
        content += "## Active Principles\n\n"

        # Group principles by enforcement level
        by_level = {}
        for rule in principle_rules:
            level = rule.enforcement_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(rule)

        # Display principles tier by tier
        tiers = {
            'BLOCK': 'Tier 1: Non-Negotiable Principles',
            'LIMIT': 'Tier 2: Strong Recommendations',
            'GUIDE': 'Tier 3: Best Practices',
            'ENHANCE': 'Tier 4: Optimizations'
        }

        for level in ['BLOCK', 'LIMIT', 'GUIDE', 'ENHANCE']:
            if level not in by_level:
                continue

            content += f"### {tiers[level]}\n\n"
            for rule in sorted(by_level[level], key=lambda r: r.rule_id):
                content += f"**{rule.rule_id}**: {rule.name}\n\n"
                if rule.description:
                    content += f"{rule.description}\n\n"

        return (content, ["rules"])

    def _generate_workflow_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate WORKFLOW.md content from workflow tables.

        Extracts current workflow state: active work items, tasks,
        phase distribution, and quality gate status.
        """
        from agentpm.core.database.methods import work_items, tasks

        # Query active work items and tasks
        all_work_items = work_items.list_work_items(self.db, project_id=project_id)
        all_tasks = tasks.list_tasks(self.db)

        # Group work items by status and phase
        by_status = {}
        by_phase = {}
        for wi in all_work_items:
            status = wi.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(wi)

            phase = getattr(wi, 'phase', 'unknown')
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(wi)

        # Build content
        content = "# APM (Agent Project Manager) Workflow System\n\n"
        content += f"**Total Work Items**: {len(all_work_items)}\n"
        content += f"**Total Tasks**: {len(all_tasks)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## Quality-Gated Workflow\n\n"
        content += "APM (Agent Project Manager) uses a 6-phase quality-gated workflow:\n\n"
        content += "1. **D1_DISCOVERY**: Define requirements (6W + AC + Risks)\n"
        content += "2. **P1_PLAN**: Create tasks, estimates, dependencies\n"
        content += "3. **I1_IMPLEMENTATION**: Build, test, document\n"
        content += "4. **R1_REVIEW**: Validate AC, quality checks\n"
        content += "5. **O1_OPERATIONS**: Deploy, monitor, health checks\n"
        content += "6. **E1_EVOLUTION**: Analyze, improve, iterate\n\n"

        content += "---\n\n"
        content += "## Work Item Distribution\n\n"

        content += "### By Status\n\n"
        for status in sorted(by_status.keys()):
            count = len(by_status[status])
            content += f"- **{status}**: {count} work items\n"

        content += "\n### By Phase\n\n"
        # Sort phases, handling None values
        phase_keys = sorted(
            [k for k in by_phase.keys() if k is not None],
            key=lambda x: str(x)
        )
        if None in by_phase:
            phase_keys.append(None)

        for phase in phase_keys:
            count = len(by_phase[phase])
            phase_str = str(phase) if phase is not None else "unknown"
            content += f"- **{phase_str}**: {count} work items\n"

        content += "\n---\n\n"
        content += "## Active Work Items\n\n"

        # Show active work items
        active_items = [wi for wi in all_work_items if wi.status in ['active', 'in_progress']]
        if active_items:
            for wi in active_items[:10]:  # Limit to 10
                content += f"### WI-{wi.id}: {wi.name}\n\n"
                content += f"- **Status**: {wi.status}\n"
                content += f"- **Phase**: {getattr(wi, 'phase', 'unknown')}\n"
                content += f"- **Type**: {wi.type}\n"
                if wi.description:
                    content += f"- **Description**: {wi.description[:100]}...\n"
                content += "\n"
        else:
            content += "No active work items.\n\n"

        return (content, ["work_items", "tasks"])

    def _generate_agents_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate AGENTS.md content from agents table.

        Extracts agent directory structure, organizing by functional_category
        (planning, implementation, testing, documentation, utilities).
        """
        from agentpm.core.database.methods import agents as agent_methods
        from agentpm.core.database.enums import AgentFunctionalCategory

        # Query all active agents
        all_agents = agent_methods.list_agents(self.db, project_id=project_id, active_only=True)

        # Group agents by functional_category (preferred) or tier (fallback)
        by_category = {}
        for agent in all_agents:
            category = getattr(agent, 'functional_category', None)
            # Convert enum to string value if it's an enum instance
            if category is not None:
                category_key = category.value if hasattr(category, 'value') else str(category)
            elif agent.tier:
                # Fallback to tier mapping for backwards compatibility
                tier_to_category = {
                    1: 'utilities',      # TIER_1 (sub-agents) → utilities
                    2: 'implementation', # TIER_2 (specialists) → implementation
                    3: 'planning'        # TIER_3 (orchestrators) → planning
                }
                category_key = tier_to_category.get(agent.tier.value, 'uncategorized')
            else:
                category_key = 'uncategorized'

            if category_key not in by_category:
                by_category[category_key] = []
            by_category[category_key].append(agent)

        content = "# APM (Agent Project Manager) Agent System\n\n"
        content += f"**Total Active Agents**: {len(all_agents)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## Agent Directory (Flat - Organized by Function)\n\n"

        # Display agents by functional category
        category_order = ['planning', 'implementation', 'testing', 'documentation', 'utilities']
        category_labels = {
            'planning': 'Planning & Analysis',
            'implementation': 'Implementation',
            'testing': 'Testing & Quality',
            'documentation': 'Documentation',
            'utilities': 'Utilities'
        }

        for category in category_order:
            if category not in by_category:
                continue

            agents_in_category = sorted(by_category[category], key=lambda a: a.role)
            content += f"### {category_labels.get(category, category.title())} ({len(agents_in_category)})\n\n"

            for agent in agents_in_category:
                content += f"- **{agent.role}**: {agent.display_name}"
                if agent.description:
                    # Truncate description to first line or 150 chars
                    desc = agent.description.split('\n')[0][:150]
                    content += f" - {desc}"
                content += "\n"

            content += "\n"

        # Also list uncategorized agents at the end
        if 'uncategorized' in by_category:
            content += f"### Uncategorized ({len(by_category['uncategorized'])})\n\n"
            for agent in sorted(by_category['uncategorized'], key=lambda a: a.role):
                content += f"- **{agent.role}**: {agent.display_name}\n"
            content += "\n"

        return (content, ["agents"])

    def _generate_context_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate CONTEXT.md content from contexts table.

        Extracts 6W context data, confidence scores, and resource files.
        """
        from agentpm.core.database.methods import contexts as context_methods

        # Query all contexts for this project
        with self.db.connect() as conn:
            import sqlite3
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM contexts WHERE project_id = ? LIMIT 50",
                (project_id,)
            )
            context_rows = [dict(row) for row in cursor.fetchall()]

        content = "# APM (Agent Project Manager) Context System\n\n"
        content += f"**Total Contexts**: {len(context_rows)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## 6W Context Framework\n\n"
        content += "APM (Agent Project Manager) uses the 6W framework for comprehensive context capture:\n\n"
        content += "- **WHO**: Stakeholders, users, developers involved\n"
        content += "- **WHAT**: Features, requirements, deliverables\n"
        content += "- **WHEN**: Timelines, milestones, dependencies\n"
        content += "- **WHERE**: Systems, environments, locations\n"
        content += "- **WHY**: Business value, user needs, motivations\n"
        content += "- **HOW**: Technical approach, architecture, patterns\n\n"

        content += "---\n\n"
        content += "## Context Statistics\n\n"

        # Group contexts by type
        by_type = {}
        for ctx in context_rows:
            ctx_type = ctx.get('context_type', 'unknown')
            if ctx_type not in by_type:
                by_type[ctx_type] = []
            by_type[ctx_type].append(ctx)

        for ctx_type in sorted(by_type.keys()):
            count = len(by_type[ctx_type])
            content += f"- **{ctx_type}**: {count} contexts\n"

        # Show high-confidence contexts
        content += "\n---\n\n"
        content += "## High-Confidence Contexts\n\n"

        high_confidence = [
            ctx for ctx in context_rows
            if ctx.get('confidence_score') is not None and ctx.get('confidence_score', 0) >= 0.7
        ]
        if high_confidence:
            for ctx in high_confidence[:10]:
                content += f"### Context #{ctx['id']}\n\n"
                content += f"- **Type**: {ctx.get('context_type', 'unknown')}\n"
                content += f"- **Confidence**: {ctx.get('confidence_score', 0):.2f}\n"
                content += f"- **Band**: {ctx.get('confidence_band', 'unknown')}\n"
                if ctx.get('entity_type') and ctx.get('entity_id'):
                    content += f"- **Entity**: {ctx['entity_type']} #{ctx['entity_id']}\n"
                content += "\n"
        else:
            content += "No high-confidence contexts found.\n\n"

        return (content, ["contexts"])

    def _generate_project_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate PROJECT.md content from projects table.

        Extracts project metadata: tech stack, business domain,
        status, and key metrics.
        """
        from agentpm.core.database.methods import projects

        # Get project details
        project = projects.get_project(self.db, project_id)
        if not project:
            return (
                "# APM (Agent Project Manager) Project Context\n\nProject not found.",
                ["projects"]
            )

        content = f"# {project.name}\n\n"
        content += f"**Project ID**: {project.id}\n"
        content += f"**Status**: {project.status}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if project.description:
            content += "---\n\n"
            content += "## Description\n\n"
            content += f"{project.description}\n\n"

        content += "---\n\n"
        content += "## Technical Stack\n\n"

        # Tech stack
        try:
            import json
            tech_stack = json.loads(project.tech_stack) if isinstance(project.tech_stack, str) else project.tech_stack
            if tech_stack:
                for tech in tech_stack:
                    content += f"- {tech}\n"
            else:
                content += "No tech stack defined.\n"
        except:
            content += "Tech stack data unavailable.\n"

        # Detected frameworks
        content += "\n### Detected Frameworks\n\n"
        try:
            frameworks = json.loads(project.detected_frameworks) if isinstance(project.detected_frameworks, str) else project.detected_frameworks
            if frameworks:
                for fw in frameworks:
                    content += f"- {fw}\n"
            else:
                content += "No frameworks detected.\n"
        except:
            content += "Framework data unavailable.\n"

        # Business context
        if getattr(project, 'business_domain', None):
            content += "\n---\n\n"
            content += "## Business Context\n\n"
            content += f"**Domain**: {project.business_domain}\n"
            if getattr(project, 'business_description', None):
                content += f"\n{project.business_description}\n"

        # Project metadata
        content += "\n---\n\n"
        content += "## Metadata\n\n"
        content += f"- **Path**: {project.path}\n"
        content += f"- **Created**: {getattr(project, 'created_at', 'unknown')}\n"
        content += f"- **Updated**: {getattr(project, 'updated_at', 'unknown')}\n"

        return (content, ["projects"])

    def _generate_ideas_content(self, project_id: int) -> tuple[str, List[str]]:
        """Generate IDEAS.md content from ideas table.

        Extracts ideas backlog organized by status, vote count,
        and conversion tracking.
        """
        from agentpm.core.database.methods import ideas as idea_methods

        # Query all ideas for this project
        all_ideas = idea_methods.list_ideas(self.db, project_id=project_id)

        # Group ideas by status
        by_status = {}
        for idea in all_ideas:
            status = idea.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(idea)

        content = "# APM (Agent Project Manager) Ideas System\n\n"
        content += f"**Total Ideas**: {len(all_ideas)}\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        content += "---\n\n"
        content += "## Ideas Pipeline\n\n"
        content += "APM (Agent Project Manager) uses a lightweight ideas system for capturing brainstorming:\n\n"
        content += "1. **idea**: Initial capture\n"
        content += "2. **research**: Investigation phase\n"
        content += "3. **design**: Technical design\n"
        content += "4. **accepted**: Ready for conversion\n"
        content += "5. **converted**: Converted to work item\n"
        content += "6. **rejected**: Not pursued\n\n"

        content += "---\n\n"
        content += "## Ideas by Status\n\n"

        for status in sorted(by_status.keys()):
            ideas_list = by_status[status]
            content += f"### {status.upper()} ({len(ideas_list)})\n\n"

            # Sort by votes descending
            sorted_ideas = sorted(ideas_list, key=lambda i: getattr(i, 'votes', 0), reverse=True)

            for idea in sorted_ideas[:10]:  # Limit to top 10 per status
                content += f"**Idea #{idea.id}**: {idea.title}\n\n"
                content += f"- **Votes**: {getattr(idea, 'votes', 0)}\n"
                content += f"- **Source**: {getattr(idea, 'source', 'unknown')}\n"
                if idea.description:
                    content += f"- **Description**: {idea.description[:100]}...\n"
                if getattr(idea, 'converted_to_work_item_id', None):
                    content += f"- **Converted to**: WI-{idea.converted_to_work_item_id}\n"
                content += "\n"

        # Show top voted ideas across all statuses
        content += "---\n\n"
        content += "## Top Voted Ideas\n\n"

        all_sorted = sorted(all_ideas, key=lambda i: getattr(i, 'votes', 0), reverse=True)
        for idea in all_sorted[:5]:
            content += f"- **{idea.title}** ({getattr(idea, 'votes', 0)} votes) - {idea.status}\n"

        return (content, ["ideas"])

    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content.

        Args:
            content: Content to hash

        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def _calculate_confidence(self, content: str, source_tables: List[str]) -> float:
        """Calculate confidence score for generated content.

        Args:
            content: Generated content
            source_tables: List of source tables

        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple heuristic: more source tables and longer content = higher confidence
        base_score = 0.7
        source_bonus = min(len(source_tables) * 0.05, 0.2)
        length_bonus = min(len(content) / 10000, 0.1)

        return min(base_score + source_bonus + length_bonus, 1.0)

    def _calculate_completeness(self, content: str, file_type: MemoryFileType) -> float:
        """Calculate completeness score for generated content.

        Args:
            content: Generated content
            file_type: Type of memory file

        Returns:
            Completeness score (0.0-1.0)
        """
        # Simple heuristic: check for key sections
        required_sections = {
            MemoryFileType.RULES: ["# APM (Agent Project Manager)", "Rule Categories", "Active Rules"],
            MemoryFileType.PRINCIPLES: ["# Development", "Tier", "Pyramid"],
            MemoryFileType.WORKFLOW: ["# APM (Agent Project Manager)", "Phase", "Quality Gates"],
            MemoryFileType.AGENTS: ["# APM (Agent Project Manager)", "Agent", "Tier"],
            MemoryFileType.CONTEXT: ["# APM (Agent Project Manager)", "6W", "Context"],
            MemoryFileType.PROJECT: ["# APM (Agent Project Manager)", "Project", "Context"],
            MemoryFileType.IDEAS: ["# APM (Agent Project Manager)", "Ideas", "Analysis"],
        }

        sections = required_sections.get(file_type, [])
        if not sections:
            return 1.0

        found_count = sum(1 for section in sections if section in content)
        return found_count / len(sections)

    def _get_file_path(self, file_type: MemoryFileType) -> str:
        """Get file path for memory file type.

        Args:
            file_type: Type of memory file

        Returns:
            Relative file path in .claude/ directory
        """
        filenames = {
            MemoryFileType.RULES: "RULES.md",
            MemoryFileType.PRINCIPLES: "PRINCIPLES.md",
            MemoryFileType.WORKFLOW: "WORKFLOW.md",
            MemoryFileType.AGENTS: "AGENTS.md",
            MemoryFileType.CONTEXT: "CONTEXT.md",
            MemoryFileType.PROJECT: "PROJECT.md",
            MemoryFileType.IDEAS: "IDEAS.md",
        }

        filename = filenames.get(file_type, f"{file_type.value.upper()}.md")
        return f".claude/{filename}"

    def _write_file(self, file_path: str, content: str) -> None:
        """Write memory file to .claude/ directory.

        Args:
            file_path: Relative file path
            content: File content
        """
        full_path = self.project_root / file_path

        # Ensure .claude directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        full_path.write_text(content, encoding='utf-8')
