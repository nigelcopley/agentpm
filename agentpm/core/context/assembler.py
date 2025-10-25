"""
Context Assembler - Orchestrate Complete Context Assembly

Assembles hierarchical context with all features:
- Hierarchical entity loading (project + work_item + task)
- 6W merging with override rules
- Plugin facts integration
- Code amalgamation references (lazy loading)
- Confidence scoring
- Staleness detection and warnings

Pattern: Orchestration with graceful degradation
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..database.service import DatabaseService
from ..database.models import Project, WorkItem, Task, Context, UnifiedSixW
from ..database.enums import EntityType, ConfidenceBand
from .merger import SixWMerger
from .scoring import ConfidenceScorer
from .freshness import ContextFreshness


class ContextAssembler:
    """
    Assembles complete hierarchical context with all features.

    Graceful degradation:
    - Missing 6W → partial context with warnings
    - Failed plugins → partial facts with warnings
    - Missing amalgamations → reduced confidence, not failure
    """

    def __init__(self, db: DatabaseService, project_path: Path):
        """
        Initialize context assembler.

        Args:
            db: Database service instance
            project_path: Path to project root (for amalgamations)
        """
        self.db = db
        self.project_path = project_path

    def assemble_task_context(self, task_id: int) -> Dict[str, Any]:
        """
        Assemble complete task context with full hierarchy.

        Returns:
            {
                'project': {...},           # Project entity data
                'work_item': {...},         # Work item entity data
                'task': {...},              # Task entity data
                'merged_6w': {...},         # Merged UnifiedSixW (task > work_item > project)
                'plugin_facts': {...},      # Plugin-extracted facts
                'amalgamations': {...},     # Code file references (lazy - paths only)
                'confidence': {             # Confidence assessment
                    'score': 0.85,
                    'band': 'GREEN',
                    'factors': {...}
                },
                'warnings': [...]           # Staleness/quality warnings
            }
        """
        # Import CRUD methods
        from ..database.methods import tasks, work_items, projects, contexts

        # Load entities (with error handling)
        task = tasks.get_task(self.db, task_id)
        if not task:
            return {'error': f'Task {task_id} not found'}

        work_item = work_items.get_work_item(self.db, task.work_item_id)
        if not work_item:
            return {'error': f'Work item {task.work_item_id} not found'}

        project = projects.get_project(self.db, work_item.project_id)
        if not project:
            return {'error': f'Project {work_item.project_id} not found'}

        # Load contexts (graceful degradation if missing)
        project_ctx = contexts.get_entity_context(self.db, EntityType.PROJECT, project.id)
        wi_ctx = contexts.get_entity_context(self.db, EntityType.WORK_ITEM, work_item.id)
        task_ctx = contexts.get_entity_context(self.db, EntityType.TASK, task_id)

        # Merge 6W hierarchically
        merged_6w = SixWMerger.merge_hierarchical(
            project_ctx.six_w if project_ctx else None,
            wi_ctx.six_w if wi_ctx else None,
            task_ctx.six_w if task_ctx else None
        )

        # Extract plugin facts (from project context or re-extract)
        plugin_facts = self._extract_plugin_facts(project, project_ctx)

        # Get amalgamation references (lazy - paths only)
        amalgamations = self._get_amalgamation_paths(project.tech_stack)

        # Calculate freshness
        freshness = self._calculate_freshness(project_ctx)

        # Calculate confidence score
        confidence = ConfidenceScorer.calculate_confidence(
            merged_6w,
            plugin_facts,
            amalgamations,
            freshness.context_age_days
        )

        # Assemble complete context
        context = {
            'project': self._serialize_project(project),
            'work_item': self._serialize_work_item(work_item),
            'task': self._serialize_task(task),
            'merged_6w': self._serialize_six_w(merged_6w),
            'plugin_facts': plugin_facts,
            'amalgamations': amalgamations,
            'confidence': {
                'score': confidence.total_score,
                'band': confidence.band.value,
                'six_w_completeness': confidence.six_w_completeness,
                'plugin_facts_quality': confidence.plugin_facts_quality,
                'amalgamations_coverage': confidence.amalgamations_coverage,
                'freshness_factor': confidence.freshness_factor,
            },
            'warnings': confidence.warnings + [
                w.message for w in freshness.get_staleness_warnings()
            ]
        }

        return context

    def assemble_work_item_context(self, work_item_id: int) -> Dict[str, Any]:
        """
        Assemble work item context (project + work item).

        Similar to task context but without task-specific details.

        Returns:
            Dictionary with project + work_item + merged 6W + confidence
        """
        from ..database.methods import work_items, projects, contexts

        # Load entities
        work_item = work_items.get_work_item(self.db, work_item_id)
        if not work_item:
            return {'error': f'Work item {work_item_id} not found'}

        project = projects.get_project(self.db, work_item.project_id)
        if not project:
            return {'error': f'Project {work_item.project_id} not found'}

        # Load contexts
        project_ctx = contexts.get_entity_context(self.db, EntityType.PROJECT, project.id)
        wi_ctx = contexts.get_entity_context(self.db, EntityType.WORK_ITEM, work_item_id)

        # Merge 6W (only 2 levels)
        merged_6w = SixWMerger.merge_hierarchical(
            project_ctx.six_w if project_ctx else None,
            wi_ctx.six_w if wi_ctx else None,
            None  # No task level
        )

        # Extract facts and amalgamations
        plugin_facts = self._extract_plugin_facts(project, project_ctx)
        amalgamations = self._get_amalgamation_paths(project.tech_stack)

        # Calculate freshness and confidence
        freshness = self._calculate_freshness(project_ctx)
        confidence = ConfidenceScorer.calculate_confidence(
            merged_6w, plugin_facts, amalgamations, freshness.context_age_days
        )

        return {
            'project': self._serialize_project(project),
            'work_item': self._serialize_work_item(work_item),
            'merged_6w': self._serialize_six_w(merged_6w),
            'plugin_facts': plugin_facts,
            'amalgamations': amalgamations,
            'confidence': {
                'score': confidence.total_score,
                'band': confidence.band.value,
            },
            'warnings': confidence.warnings
        }

    def assemble_project_context(self, project_id: int) -> Dict[str, Any]:
        """
        Assemble project-level context (project only).

        Returns:
            Dictionary with project + facts + amalgamations + confidence
        """
        from ..database.methods import projects, contexts

        project = projects.get_project(self.db, project_id)
        if not project:
            return {'error': f'Project {project_id} not found'}

        project_ctx = contexts.get_entity_context(self.db, EntityType.PROJECT, project_id)

        plugin_facts = self._extract_plugin_facts(project, project_ctx)
        amalgamations = self._get_amalgamation_paths(project.tech_stack)

        freshness = self._calculate_freshness(project_ctx)
        confidence = ConfidenceScorer.calculate_confidence(
            project_ctx.six_w if project_ctx else None,
            plugin_facts,
            amalgamations,
            freshness.context_age_days
        )

        return {
            'project': self._serialize_project(project),
            'six_w': self._serialize_six_w(project_ctx.six_w if project_ctx else None),
            'plugin_facts': plugin_facts,
            'amalgamations': amalgamations,
            'confidence': {
                'score': confidence.total_score,
                'band': confidence.band.value,
            },
            'warnings': confidence.warnings
        }

    # ========== Helper Methods ==========

    def _extract_plugin_facts(
        self,
        project: Project,
        project_ctx: Optional[Context]
    ) -> Dict[str, Any]:
        """
        Extract plugin facts from project context.

        Plugin facts are stored in six_w.how field as:
        six_w.how = "JSON string with plugin_facts key"

        Args:
            project: Project entity
            project_ctx: Project context (may be None)

        Returns:
            Dictionary of plugin facts by framework/language
        """
        if not project_ctx or not project_ctx.six_w:
            return {}

        # Plugin facts stored in HOW dimension
        how_data = project_ctx.six_w.suggested_approach
        if not how_data:
            return {}

        # Parse if it's a JSON-encoded dict (common pattern)
        import json
        try:
            if isinstance(how_data, str) and how_data.startswith('{'):
                parsed = json.loads(how_data)
                return parsed.get('plugin_facts', {})
            elif isinstance(how_data, dict):
                return how_data.get('plugin_facts', {})
        except json.JSONDecodeError:
            pass

        return {}

    def _get_amalgamation_paths(self, tech_stack: Optional[str]) -> Dict[str, str]:
        """
        Get paths to code amalgamation files (lazy loading).

        Returns paths only, NOT file contents. Agents load content as needed.

        Args:
            tech_stack: Comma-separated tech stack (e.g., "Python,Django,pytest")

        Returns:
            Dictionary mapping amalgamation type to file path
        """
        amalg_dir = self.project_path / '.aipm' / 'contexts'
        if not amalg_dir.exists():
            return {}

        amalgamations = {}

        # Scan for amalgamation files
        for file_path in amalg_dir.glob('*.txt'):
            # File naming: lang_python_classes.txt, framework_django_models.txt
            amalg_type = file_path.stem  # e.g., "lang_python_classes"
            amalgamations[amalg_type] = str(file_path)

        return amalgamations

    def _calculate_freshness(self, project_ctx: Optional[Context]) -> ContextFreshness:
        """
        Calculate context freshness.

        Args:
            project_ctx: Project context (may be None)

        Returns:
            ContextFreshness tracker with age and warnings
        """
        if not project_ctx:
            # No context = very stale (treat as 999 days old)
            return ContextFreshness(
                last_context_update=datetime(2000, 1, 1),
                project_path=self.project_path
            )

        return ContextFreshness(
            last_context_update=project_ctx.updated_at,
            project_path=self.project_path
        )

    def _serialize_project(self, project: Project) -> Dict[str, Any]:
        """Serialize project entity for context"""
        return {
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'tech_stack': project.tech_stack,
            'status': project.status.value if project.status else None,
        }

    def _serialize_work_item(self, work_item: WorkItem) -> Dict[str, Any]:
        """Serialize work item entity for context"""
        return {
            'id': work_item.id,
            'name': work_item.name,
            'type': work_item.type.value if work_item.type else None,
            'description': work_item.description,
            'status': work_item.status.value if work_item.status else None,
            'business_context': work_item.business_context,
        }

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Serialize task entity for context"""
        return {
            'id': task.id,
            'name': task.name,
            'type': task.type.value if task.type else None,
            'description': task.description,
            'status': task.status.value if task.status else None,
            'assigned_to': task.assigned_to,
            'effort_hours': task.effort_hours,
            'implementation_steps': task.implementation_steps,
        }

    def _serialize_six_w(self, six_w: Optional[UnifiedSixW]) -> Dict[str, Any]:
        """
        Serialize UnifiedSixW structure for context.

        Converts dataclass to dictionary with all 14 fields.

        Args:
            six_w: UnifiedSixW structure (may be None)

        Returns:
            Dictionary with all 6W dimensions
        """
        if not six_w:
            return {
                'who': {}, 'what': {}, 'where': {},
                'when': {}, 'why': {}, 'how': {}
            }

        return {
            'who': {
                'end_users': six_w.end_users or [],
                'implementers': six_w.implementers or [],
                'reviewers': six_w.reviewers or [],
            },
            'what': {
                'functional_requirements': six_w.functional_requirements or [],
                'technical_constraints': six_w.technical_constraints or [],
                'acceptance_criteria': six_w.acceptance_criteria or [],
            },
            'where': {
                'affected_services': six_w.affected_services or [],
                'repositories': six_w.repositories or [],
                'deployment_targets': six_w.deployment_targets or [],
            },
            'when': {
                'deadline': six_w.deadline.isoformat() if six_w.deadline else None,
                'dependencies_timeline': six_w.dependencies_timeline or [],
            },
            'why': {
                'business_value': six_w.business_value,
                'risk_if_delayed': six_w.risk_if_delayed,
            },
            'how': {
                'suggested_approach': six_w.suggested_approach,
                'existing_patterns': six_w.existing_patterns or [],
            }
        }
