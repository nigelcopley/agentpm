"""
Context Assembly Service - Hierarchical Context Orchestration

Coordinates <200ms context assembly for AI agents:
- 10-step assembly pipeline (load → merge → score → inject)
- Hierarchical 6W merging (Task > WorkItem > Project)
- Plugin intelligence integration
- Agent SOP injection
- Temporal context loading
- Graceful degradation on component failures

Pattern: Service orchestrator with sub-component delegation
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from .models import ContextPayload, AgentValidationError
from .merger import SixWMerger
from .scoring import ConfidenceScorer
from .freshness import ContextFreshness
from .sop_injector import AgentSOPInjector
from .temporal_loader import TemporalContextLoader
from .role_filter import RoleBasedFilter
from ..database.models.context import UnifiedSixW
from ..database.enums import EntityType, ContextType
from ..plugins.orchestrator import PluginOrchestrator


class ContextAssemblyService:
    """
    Orchestrate hierarchical context assembly for AI agents.

    Primary entry point for Context Delivery Agent (WI-31).
    Coordinates all sub-components to deliver complete, scored, hierarchical context.

    Performance Target: <200ms (p95) for complete assembly
    Reliability Target: 95% graceful degradation on component failures

    Example usage:
        service = ContextAssemblyService(db, project_path)
        context = service.assemble_task_context(task_id=45, agent_role='python-developer')
        # Returns ContextPayload with merged 6W, plugin facts, SOP, session history
    """

    def __init__(
        self,
        db,
        project_path: Path,
        enable_cache: bool = False  # Cache disabled for MVP
    ):
        """
        Initialize context assembly service.

        Args:
            db: DatabaseService instance for entity/context queries
            project_path: Project root directory (for plugins, SOPs, amalgamations)
            enable_cache: Enable two-tier caching (default: False, MVP scope)
        """
        self.db = db
        self.project_path = project_path

        # Sub-components (pure logic, no state)
        self.merger = SixWMerger()
        self.scorer = ConfidenceScorer()

        # Plugin orchestrator (for facts/amalgamations)
        self.plugin_orchestrator = PluginOrchestrator(min_confidence=0.5)

        # NEW components (Task #144)
        self.sop_injector = AgentSOPInjector(project_path)
        self.temporal_loader = TemporalContextLoader(db)

        # NEW component (Task #146)
        self.role_filter = RoleBasedFilter(db)

        # Cache disabled for MVP (Phase 2: Task #145)
        self.cache_enabled = enable_cache
        self.cache: Dict[str, Any] = {}  # Simple in-memory cache (MVP)

    # ─────────────────────────────────────────────────────────────────
    # PUBLIC API - Task-level context (MVP scope)
    # ─────────────────────────────────────────────────────────────────

    def assemble_task_context(
        self,
        task_id: int,
        agent_role: Optional[str] = None
    ) -> ContextPayload:
        """
        Assemble complete hierarchical context for a task.

        Hierarchy: Project → Work Item → Task (merged with task precedence)

        Args:
            task_id: Task ID to assemble context for
            agent_role: Optional agent role override (uses task.assigned_to if None)

        Returns:
            ContextPayload with complete hierarchical context

        Raises:
            ContextAssemblyError: If critical components fail
            AgentValidationError: If agent assignment is invalid

        Performance: <200ms (p95) target

        Example:
            >>> service.assemble_task_context(task_id=45)
            ContextPayload(
                project={...},
                work_item={...},
                task={...},
                merged_6w=UnifiedSixW(...),
                plugin_facts={'python': {...}},
                amalgamations={'classes': '.aipm/contexts/classes.txt'},
                agent_sop='# Python Developer SOP...',
                assigned_agent='python-developer',
                temporal_context=[...],
                confidence_score=0.85,
                confidence_band=ConfidenceBand.GREEN,
                warnings=[],
                assembled_at=datetime.now(),
                assembly_duration_ms=120.5,
                cache_hit=False
            )
        """
        start_time = time.perf_counter()

        # Cache disabled for MVP - go straight to assembly
        payload = self._assemble_task_context_uncached(task_id, agent_role)

        # Record assembly duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        payload.assembly_duration_ms = duration_ms

        return payload

    # ─────────────────────────────────────────────────────────────────
    # PRIVATE - 10-step assembly pipeline (MVP implementation)
    # ─────────────────────────────────────────────────────────────────

    def _assemble_task_context_uncached(
        self,
        task_id: int,
        agent_role: Optional[str] = None
    ) -> ContextPayload:
        """
        Uncached task context assembly (11-step pipeline).

        Steps:
        1. Load entities (task, work item, project) - CRITICAL
        2. Load 6W contexts (all three levels) - IMPORTANT
        3. Merge 6W hierarchically (task > work_item > project) - 5ms
        4. Load plugin facts (from project context or fresh detection) - 20ms cached / 100ms fresh
        5. Get amalgamation paths (code files) - 10ms
        6. Calculate freshness (staleness warnings) - 5ms
        7. Calculate confidence (formula-based scoring) - 10ms
        8. Inject agent SOP (if agent assigned) - 10-20ms
        9. Load temporal context (session summaries) - 10ms
        10. Filter by agent role (capability-based filtering) - 5-10ms
        11. Load applicable rules (enabled rules for task type) - 5ms (NEW)
        12. Return payload

        Returns:
            Complete ContextPayload

        Raises:
            ContextAssemblyError: If critical steps fail
            AgentValidationError: If agent assignment invalid
        """
        warnings = []

        # ─── STEP 1: Load Entities (CRITICAL) ───
        # Hard failure if entities don't exist
        task = self._load_task(task_id)
        work_item = self._load_work_item(task.work_item_id)
        project = self._load_project(work_item.project_id)

        # ─── STEP 2: Load 6W Contexts (IMPORTANT) ───
        # Graceful degradation - continue with empty 6W if missing
        project_ctx = self._load_6w_context(EntityType.PROJECT, project.id)
        wi_ctx = self._load_6w_context(EntityType.WORK_ITEM, work_item.id)
        task_ctx = self._load_6w_context(EntityType.TASK, task_id)

        if not any([project_ctx, wi_ctx, task_ctx]):
            warnings.append("No 6W context found at any level")

        # ─── STEP 3: Merge 6W Hierarchically (5ms) ───
        merged_6w = self.merger.merge_hierarchical(
            project_6w=project_ctx.six_w if project_ctx else None,
            work_item_6w=wi_ctx.six_w if wi_ctx else None,
            task_6w=task_ctx.six_w if task_ctx else None
        )

        # ─── STEP 4: Load Plugin Facts (20ms cached / 100ms fresh) ───
        # Graceful degradation - continue without facts if plugin fails
        plugin_facts = self._load_plugin_facts(project, project_ctx)
        if not plugin_facts:
            warnings.append("No plugin facts available (plugin detection may have failed)")

        # ─── STEP 5: Get Amalgamation Paths (10ms) ───
        # Lazy loading - return paths, not content
        amalgamations = self._get_amalgamation_paths()

        # ─── STEP 6: Calculate Freshness (5ms) ───
        freshness_days = self._calculate_freshness_days(task_ctx)
        if freshness_days > 30:
            warnings.append(f"Context is {freshness_days} days old (consider refresh)")

        # ─── STEP 7: Calculate Confidence (10ms) ───
        confidence = self.scorer.calculate_confidence(
            six_w=merged_6w,
            plugin_facts=plugin_facts,
            amalgamations=amalgamations,
            freshness_days=freshness_days
        )

        # Add confidence warnings
        warnings.extend(confidence.warnings)

        # ─── STEP 8: Inject Agent SOP (10-20ms) ───
        # Determine agent role (explicit override > task.assigned_to > None)
        effective_agent_role = agent_role or task.assigned_to
        agent_sop = None

        if effective_agent_role:
            try:
                agent_sop = self.sop_injector.load_sop(
                    project_id=project.id,
                    agent_role=effective_agent_role,
                    db=self.db
                )
            except AgentValidationError as e:
                # Agent assignment invalid - this is a CRITICAL error
                raise ContextAssemblyError(f"Invalid agent assignment: {e}") from e
            except Exception as e:
                # SOP file missing - warn but continue (graceful degradation)
                warnings.append(f"Agent SOP not found for '{effective_agent_role}'")

        # ─── STEP 9: Load Temporal Context (10ms) ───
        # Graceful degradation - continue without summaries if missing
        temporal_context = self.temporal_loader.load_recent_summaries(
            work_item_id=work_item.id,
            limit=3
        )

        # ─── STEP 10: Filter by Agent Role (5-10ms) ───
        # Only filter if agent assigned - scope context to relevant information
        filtered_amalgamations = amalgamations
        filtered_plugin_facts = plugin_facts
        filtering_stats = {}

        if effective_agent_role:
            try:
                # Track original counts for effectiveness measurement
                original_amalg_count = len(amalgamations)
                original_facts_count = len(plugin_facts)

                # Filter amalgamations by agent capabilities
                filtered_amalgamations = self.role_filter.filter_amalgamations(
                    project_id=project.id,
                    agent_role=effective_agent_role,
                    amalgamations=amalgamations
                )

                # Filter plugin facts by agent capabilities
                filtered_plugin_facts = self.role_filter.filter_plugin_facts(
                    project_id=project.id,
                    agent_role=effective_agent_role,
                    plugin_facts=plugin_facts
                )

                # Calculate filtering effectiveness
                amalg_reduction = self.role_filter.calculate_filter_effectiveness(
                    original_amalg_count,
                    len(filtered_amalgamations)
                )
                facts_reduction = self.role_filter.calculate_filter_effectiveness(
                    original_facts_count,
                    len(filtered_plugin_facts)
                )

                filtering_stats = {
                    'amalgamations_filtered': original_amalg_count - len(filtered_amalgamations),
                    'amalgamations_reduction': amalg_reduction,
                    'plugin_facts_filtered': original_facts_count - len(filtered_plugin_facts),
                    'plugin_facts_reduction': facts_reduction,
                    'total_reduction': (amalg_reduction + facts_reduction) / 2
                }

                # Add informational message if significant filtering occurred
                if filtering_stats['total_reduction'] > 0.3:  # >30% reduction
                    warnings.append(
                        f"Context scoped to '{effective_agent_role}' capabilities "
                        f"({filtering_stats['total_reduction']:.0%} reduction)"
                    )

            except Exception as e:
                # Graceful degradation - filtering failure doesn't stop assembly
                warnings.append(f"Role-based filtering failed: {e}")
                # Continue with unfiltered context
                filtered_amalgamations = amalgamations
                filtered_plugin_facts = plugin_facts

        # ─── STEP 11: Load Applicable Rules (5ms) ───
        # Graceful degradation - continue without rules if loading fails
        applicable_rules = []
        blocking_rules = []
        rule_summary = ""

        try:
            applicable_rules = self._load_applicable_rules(project.id, task)
            blocking_rules = [r for r in applicable_rules if r.enforcement_level.value == 'BLOCK']
            rule_summary = self._format_rule_summary(applicable_rules)

            if applicable_rules:
                warnings.append(f"Loaded {len(applicable_rules)} rules ({len(blocking_rules)} BLOCK)")
        except Exception as e:
            # Graceful degradation - missing rules don't stop assembly
            warnings.append(f"Rule loading failed: {e}")

        # ─── STEP 12: Return Payload ───

        payload = ContextPayload(
            project=self._serialize_entity(project),
            work_item=self._serialize_entity(work_item),
            task=self._serialize_entity(task),
            merged_6w=merged_6w,
            plugin_facts=filtered_plugin_facts,  # Filtered by role
            amalgamations=filtered_amalgamations,  # Filtered by role
            agent_sop=agent_sop,
            assigned_agent=effective_agent_role,
            temporal_context=temporal_context,
            applicable_rules=applicable_rules,  # NEW: All enabled rules
            blocking_rules=blocking_rules,  # NEW: BLOCK-level rules only
            rule_summary=rule_summary,  # NEW: Compressed summary
            confidence_score=confidence.total_score,
            confidence_band=confidence.band,
            confidence_breakdown={
                'six_w_completeness': confidence.six_w_completeness,
                'plugin_facts_quality': confidence.plugin_facts_quality,
                'amalgamations_coverage': confidence.amalgamations_coverage,
                'freshness_factor': confidence.freshness_factor
            },
            warnings=warnings,
            assembled_at=datetime.now(),
            assembly_duration_ms=0.0,  # Set by caller
            cache_hit=False
        )

        # Add filtering stats to payload (if available)
        if filtering_stats:
            payload.confidence_breakdown['filtering_stats'] = filtering_stats

        return payload

    # ─────────────────────────────────────────────────────────────────
    # HELPER METHODS - Component integration
    # ─────────────────────────────────────────────────────────────────

    def _load_task(self, task_id: int):
        """Load task from database (CRITICAL - hard failure)."""
        from ..database.methods import tasks
        task = tasks.get_task(self.db, task_id)
        if not task:
            raise ContextAssemblyError(f"Task {task_id} not found")
        return task

    def _load_work_item(self, work_item_id: int):
        """Load work item from database (CRITICAL - hard failure)."""
        from ..database.methods import work_items
        wi = work_items.get_work_item(self.db, work_item_id)
        if not wi:
            raise ContextAssemblyError(f"Work item {work_item_id} not found")
        return wi

    def _load_project(self, project_id: int):
        """Load project from database (CRITICAL - hard failure)."""
        from ..database.methods import projects
        proj = projects.get_project(self.db, project_id)
        if not proj:
            raise ContextAssemblyError(f"Project {project_id} not found")
        return proj

    def _load_6w_context(self, entity_type: EntityType, entity_id: int):
        """
        Load 6W context from database (IMPORTANT - graceful degradation).

        Returns None if context doesn't exist (not an error).
        """
        from ..database.methods import contexts
        try:
            return contexts.get_entity_context(self.db, entity_type, entity_id)
        except Exception:
            # Graceful degradation - missing context is not fatal
            return None

    def _load_plugin_facts(self, project, project_ctx) -> Dict[str, Any]:
        """
        Load plugin facts (OPTIONAL - graceful degradation).

        Strategy:
        1. Try to extract from project context (fast, cached)
        2. Fallback to fresh plugin detection (slow, rare)
        3. Return empty dict if all fails (not an error)
        """
        # Try cached facts from project context
        if project_ctx and project_ctx.confidence_factors:
            cached_facts = project_ctx.confidence_factors.get('plugin_facts')
            if cached_facts:
                return cached_facts

        # Fallback: Fresh plugin detection (MVP scope - simple implementation)
        # Full plugin orchestration deferred to Phase 2
        try:
            # Simple detection without full orchestration
            return {}  # MVP: Return empty dict, Phase 2 will add full detection

        except Exception:
            # Graceful degradation - no facts available
            return {}

    def _get_amalgamation_paths(self) -> Dict[str, str]:
        """
        Get code amalgamation file paths (OPTIONAL - graceful degradation).

        Returns:
            {type: file_path} mapping (e.g., {'classes': '.aipm/contexts/classes.txt'})

        Performance: <10ms (filesystem scan)
        """
        amalg_dir = self.project_path / '.aipm' / 'contexts'

        if not amalg_dir.exists():
            return {}

        # Scan for *.txt files (generated by plugins)
        amalgamations = {}
        for f in amalg_dir.glob('*.txt'):
            if f.is_file():
                # Extract type from filename (e.g., 'lang_python_classes.txt' -> 'classes')
                filename = f.stem
                # Try to extract meaningful type (remove plugin prefix)
                parts = filename.split('_')
                if len(parts) > 2:
                    amalg_type = '_'.join(parts[2:])  # After 'lang_python_'
                else:
                    amalg_type = filename

                amalgamations[amalg_type] = str(f)

        return amalgamations

    def _calculate_freshness_days(self, task_ctx) -> int:
        """
        Calculate context age in days.

        Args:
            task_ctx: Task context (may be None)

        Returns:
            Days since last context update (999 if no context)
        """
        if not task_ctx or not task_ctx.updated_at:
            return 999  # Very stale (no context)

        delta = datetime.now() - task_ctx.updated_at
        return delta.days

    def _serialize_entity(self, entity: Any) -> Dict[str, Any]:
        """
        Serialize Pydantic model to dict.

        Args:
            entity: Pydantic model (Task, WorkItem, Project)

        Returns:
            Dictionary representation
        """
        if entity is None:
            return {}

        if hasattr(entity, 'model_dump'):
            return entity.model_dump()
        elif hasattr(entity, 'dict'):
            return entity.dict()
        else:
            return {}

    def _load_applicable_rules(self, project_id: int, task) -> List:
        """
        Load rules applicable to this task.

        Filters rules by:
        1. Project ID (project-specific rules)
        2. Enabled status (only active rules)
        3. Task type (if rule has task_type config)

        Args:
            project_id: Project ID
            task: Task entity (used for type filtering)

        Returns:
            List of applicable Rule models

        Performance: <5ms (database query)
        """
        from ..database.methods import rules as rule_methods

        # Load all enabled rules for this project
        all_rules = rule_methods.list_rules(self.db, project_id, enabled_only=True)

        # Filter by task type if rule specifies it
        task_rules = []
        for rule in all_rules:
            # If rule has no task_type config, it applies to all tasks
            if not rule.config or 'task_type' not in rule.config:
                task_rules.append(rule)
                continue

            # If rule specifies task_type, check if it matches
            rule_task_types = rule.config.get('task_type', [])
            if isinstance(rule_task_types, str):
                rule_task_types = [rule_task_types]

            # Check if task type matches any of the rule's target types
            if task.type.value in rule_task_types:
                task_rules.append(rule)

        return task_rules

    def _format_rule_summary(self, rules: List) -> str:
        """
        Create compressed rule summary for agent context.

        Format prioritizes BLOCK rules (must comply) over GUIDE rules (recommendations).
        Limits output to top rules to keep context lean.

        Args:
            rules: List of Rule models

        Returns:
            Markdown-formatted rule summary

        Performance: <1ms (string formatting)
        """
        if not rules:
            return "No rules applicable to this task."

        # Separate by enforcement level
        blocking = [r for r in rules if r.enforcement_level.value == 'BLOCK']
        limiting = [r for r in rules if r.enforcement_level.value == 'LIMIT']
        guiding = [r for r in rules if r.enforcement_level.value == 'GUIDE']
        enhancing = [r for r in rules if r.enforcement_level.value == 'ENHANCE']

        summary_parts = []

        # Header with counts
        summary_parts.append(
            f"## Applicable Rules ({len(blocking)} BLOCK, {len(limiting)} LIMIT, "
            f"{len(guiding)} GUIDE, {len(enhancing)} ENHANCE)\n"
        )

        # BLOCK rules (must comply) - show all
        if blocking:
            summary_parts.append("### BLOCK Rules (must comply):")
            for rule in blocking[:15]:  # Max 15 blocking rules
                desc = rule.description[:80] + "..." if rule.description and len(rule.description) > 80 else rule.description or ""
                summary_parts.append(f"- **{rule.rule_id}** ({rule.name}): {desc}")
            if len(blocking) > 15:
                summary_parts.append(f"  ... and {len(blocking) - 15} more BLOCK rules")
            summary_parts.append("")

        # LIMIT rules (soft constraints) - show top 10
        if limiting:
            summary_parts.append("### LIMIT Rules (warnings):")
            for rule in limiting[:10]:
                desc = rule.description[:80] + "..." if rule.description and len(rule.description) > 80 else rule.description or ""
                summary_parts.append(f"- **{rule.rule_id}** ({rule.name}): {desc}")
            if len(limiting) > 10:
                summary_parts.append(f"  ... and {len(limiting) - 10} more LIMIT rules")
            summary_parts.append("")

        # GUIDE rules (recommendations) - show top 5
        if guiding:
            summary_parts.append("### GUIDE Rules (recommendations):")
            for rule in guiding[:5]:
                desc = rule.description[:80] + "..." if rule.description and len(rule.description) > 80 else rule.description or ""
                summary_parts.append(f"- **{rule.rule_id}** ({rule.name}): {desc}")
            if len(guiding) > 5:
                summary_parts.append(f"  ... and {len(guiding) - 5} more GUIDE rules")
            summary_parts.append("")

        # ENHANCE rules (context enrichment) - show count only
        if enhancing:
            summary_parts.append(f"**{len(enhancing)} ENHANCE rules** (context enrichment only)\n")

        return "\n".join(summary_parts)

    # ─────────────────────────────────────────────────────────────────
    # CACHE MANAGEMENT (Task #145)
    # ─────────────────────────────────────────────────────────────────

    def invalidate_cache(
        self,
        context_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None
    ):
        """
        Invalidate cached contexts.

        Three invalidation strategies:
        1. Specific context: invalidate_cache(context_id=123)
        2. Entity type: invalidate_cache(entity_type='task')
        3. Specific entity: invalidate_cache(entity_type='task', entity_id=45)

        Args:
            context_id: Specific context to invalidate (optional)
            entity_type: Invalidate all contexts of type (optional)
            entity_id: Specific entity ID (requires entity_type)

        Example:
            # Invalidate specific task context
            service.invalidate_cache(entity_type='task', entity_id=45)

            # Invalidate all task contexts
            service.invalidate_cache(entity_type='task')

            # Clear entire cache
            service.invalidate_cache()

        Performance: <5ms (in-memory dict operation)
        """
        if not self.cache_enabled or not self.cache:
            return

        # Strategy 1: Clear all (no args)
        if context_id is None and entity_type is None:
            self.cache.clear()
            return

        # Strategy 2: Specific context ID
        if context_id is not None:
            cache_key = f"context:{context_id}"
            self.cache.pop(cache_key, None)
            return

        # Strategy 3: Entity type or specific entity
        if entity_type:
            # Build pattern to match
            if entity_id is not None:
                pattern = f"{entity_type}:{entity_id}"
            else:
                pattern = f"{entity_type}:"

            # Remove matching keys
            keys_to_remove = [k for k in self.cache if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (size, enabled status)

        Example:
            >>> service.get_cache_stats()
            {'enabled': True, 'size': 15, 'keys': ['task:45', 'task:46', ...]}
        """
        return {
            'enabled': self.cache_enabled,
            'size': len(self.cache) if self.cache else 0,
            'keys': list(self.cache.keys()) if self.cache else []
        }

    # ─────────────────────────────────────────────────────────────────
    # NEW: Rich Context Assembly Methods
    # ─────────────────────────────────────────────────────────────────

    def assemble_rich_context(
        self,
        entity_type: EntityType,
        entity_id: int,
        context_types: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Assemble rich context for any entity (Idea, Work Item, Task).

        Args:
            entity_type: Type of entity (IDEA, WORK_ITEM, TASK)
            entity_id: ID of the entity
            context_types: Optional list of specific context types to load

        Returns:
            Dictionary with rich context data organized by context type
        """
        from ..database.enums import ContextType

        rich_context = {}

        # Default context types if none specified
        if context_types is None:
            if entity_type == EntityType.PROJECT:
                context_types = [
                    ContextType.PROJECT_CONTEXT,
                    ContextType.BUSINESS_PILLARS_CONTEXT,
                    ContextType.MARKET_RESEARCH_CONTEXT,
                    ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
                    ContextType.STAKEHOLDER_CONTEXT
                ]
            elif entity_type == EntityType.IDEA:
                context_types = [
                    ContextType.IDEA_CONTEXT,
                    ContextType.BUSINESS_PILLARS_CONTEXT,
                    ContextType.MARKET_RESEARCH_CONTEXT,
                    ContextType.COMPETITIVE_ANALYSIS_CONTEXT
                ]
            elif entity_type == EntityType.WORK_ITEM:
                context_types = [
                    ContextType.WORK_ITEM_CONTEXT,
                    ContextType.BUSINESS_PILLARS_CONTEXT,
                    ContextType.MARKET_RESEARCH_CONTEXT,
                    ContextType.QUALITY_GATES_CONTEXT,
                    ContextType.STAKEHOLDER_CONTEXT
                ]
            elif entity_type == EntityType.TASK:
                context_types = [
                    ContextType.TASK_CONTEXT,
                    ContextType.TECHNICAL_CONTEXT,
                    ContextType.IMPLEMENTATION_CONTEXT,
                    ContextType.QUALITY_GATES_CONTEXT
                ]

        # Load each context type
        for context_type in context_types:
            context_data = self._load_rich_context(entity_type, entity_id, context_type)
            if context_data:
                rich_context[context_type.value] = context_data

        return rich_context

    def assemble_hierarchical_rich_context(
        self,
        task_id: int,
        include_idea_context: bool = False
    ) -> Dict[str, Any]:
        """
        Assemble hierarchical rich context from Idea → Work Item → Task.

        Args:
            task_id: Task ID to assemble context for
            include_idea_context: Whether to include idea context if available

        Returns:
            Dictionary with hierarchical rich context
        """
        # Load entities
        task = self._load_task(task_id)
        work_item = self._load_work_item(task.work_item_id)
        project = self._load_project(work_item.project_id)

        hierarchical_context = {
            'project': {
                'id': project.id,
                'name': project.name,
                'context': self.assemble_rich_context(EntityType.PROJECT, project.id)
            },
            'work_item': {
                'id': work_item.id,
                'name': work_item.name,
                'context': self.assemble_rich_context(EntityType.WORK_ITEM, work_item.id)
            },
            'task': {
                'id': task.id,
                'name': task.name,
                'context': self.assemble_rich_context(EntityType.TASK, task.id)
            }
        }

        # Include idea context if requested and available
        if include_idea_context:
            idea_context = self._load_idea_context_for_work_item(work_item.id)
            if idea_context:
                hierarchical_context['idea'] = idea_context

        return hierarchical_context

    def assemble_document_driven_context(
        self,
        entity_type: EntityType,
        entity_id: int
    ) -> Dict[str, Any]:
        """
        Assemble context from associated documents.

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity

        Returns:
            Dictionary with document-driven context
        """
        from ..database.methods import document_references as doc_methods

        # Load document references for this entity
        doc_refs = doc_methods.get_documents_by_entity(
            self.db, entity_type, entity_id
        )

        document_context = {}
        for doc_ref in doc_refs:
            doc_type = doc_ref.document_type.value if doc_ref.document_type else 'unknown'
            document_context[doc_type] = {
                'file_path': doc_ref.file_path,
                'title': doc_ref.title,
                'description': doc_ref.description,
                'format': doc_ref.format.value if doc_ref.format else None,
                'created_at': doc_ref.created_at,
                'updated_at': doc_ref.updated_at
            }

        return document_context

    def create_rich_context_payload(
        self,
        entity_type: EntityType,
        entity_id: int,
        context_data: Dict[str, Any],
        confidence_score: float = 0.8
    ) -> Dict[str, Any]:
        """
        Create a rich context payload structure.

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            context_data: The rich context data
            confidence_score: Confidence score for this context

        Returns:
            Structured rich context payload
        """
        from ..database.enums import ConfidenceBand

        return {
            'entity_type': entity_type.value,
            'entity_id': entity_id,
            'context_data': context_data,
            'confidence_score': confidence_score,
            'confidence_band': ConfidenceBand.from_score(confidence_score).value,
            'assembled_at': datetime.now().isoformat(),
            'context_types': list(context_data.keys()),
            'context_count': len(context_data)
        }

    # ─────────────────────────────────────────────────────────────────
    # PRIVATE: Rich Context Helper Methods
    # ─────────────────────────────────────────────────────────────────

    def _load_rich_context(
        self,
        entity_type: EntityType,
        entity_id: int,
        context_type: 'ContextType'
    ) -> Optional[Dict[str, Any]]:
        """
        Load rich context data for a specific entity and context type.

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            context_type: Type of context to load

        Returns:
            Rich context data or None if not found
        """
        from ..database.methods import contexts as context_methods

        # Load context from database
        context = context_methods.get_context_by_entity_and_type(
            self.db, entity_type, entity_id, context_type
        )

        if context and context.context_data:
            return context.context_data

        return None

    def _load_idea_context_for_work_item(self, work_item_id: int) -> Optional[Dict[str, Any]]:
        """
        Load idea context for a work item (if it was converted from an idea).

        Args:
            work_item_id: Work Item ID

        Returns:
            Idea context data or None if not found
        """
        from ..database.methods import contexts as context_methods
        from ..database.enums import ContextType

        # Look for idea-to-work-item mapping context
        mapping_context = context_methods.get_context_by_entity_and_type(
            self.db, EntityType.WORK_ITEM, work_item_id, ContextType.IDEA_TO_WORK_ITEM_MAPPING
        )

        if mapping_context and mapping_context.context_data:
            idea_id = mapping_context.context_data.get('original_idea_id')
            if idea_id:
                # Load the original idea context
                return self.assemble_rich_context(EntityType.IDEA, idea_id)

        return None

    def _load_applicable_rules(self, project_id: int, task: 'Task') -> List['Rule']:
        """
        Load applicable rules for task (with optional role-based filtering).

        Strategy:
        1. Load all enabled rules for project
        2. Filter by agent role if task is assigned (Phase 2 implementation)
        3. Return filtered list

        Args:
            project_id: Project ID
            task: Task model (for agent assignment lookup)

        Returns:
            List of applicable rules (filtered by role if assigned)

        Performance: <5ms (database query + filtering)
        """
        from ..database.methods import rules as rule_methods

        # Load all enabled rules for project
        all_rules = rule_methods.list_rules(
            self.db,
            project_id=project_id,
            enabled_only=True
        )

        # If task has agent assignment, filter by role
        if task.assigned_to:
            try:
                # Filter rules by agent capabilities
                filtered_rules = self.role_filter.filter_rules(
                    project_id=project_id,
                    agent_role=task.assigned_to,
                    rules=all_rules
                )
                return filtered_rules
            except Exception:
                # Graceful degradation - return unfiltered if filtering fails
                return all_rules

        # No agent assigned - return all enabled rules
        return all_rules

    def _format_rule_summary(self, rules: List['Rule']) -> str:
        """
        Format rule summary for compact representation.

        Creates a compressed summary of rules grouped by enforcement level:
        - BLOCK rules (critical - must pass)
        - LIMIT rules (important - warn if violated)
        - GUIDE rules (suggestions)
        - ENHANCE rules (context enrichment)

        Args:
            rules: List of Rule models

        Returns:
            Formatted summary string

        Example:
            >>> rules = [
            ...     Rule(enforcement_level='BLOCK', category='Testing Standards', ...),
            ...     Rule(enforcement_level='LIMIT', category='Code Quality', ...),
            ... ]
            >>> summary = service._format_rule_summary(rules)
            >>> print(summary)
            🚨 BLOCK (1): Testing Standards
            ⚠️ LIMIT (1): Code Quality

        Performance: <1ms (string formatting)
        """
        if not rules:
            return ""

        # Group by enforcement level
        by_level = {}
        for rule in rules:
            level = rule.enforcement_level.value
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(rule)

        # Format summary
        lines = []

        # BLOCK rules (critical)
        if 'BLOCK' in by_level:
            block_rules = by_level['BLOCK']
            categories = {r.category or 'General' for r in block_rules}
            lines.append(f"🚨 BLOCK ({len(block_rules)}): {', '.join(sorted(categories))}")

        # LIMIT rules (important)
        if 'LIMIT' in by_level:
            limit_rules = by_level['LIMIT']
            categories = {r.category or 'General' for r in limit_rules}
            lines.append(f"⚠️ LIMIT ({len(limit_rules)}): {', '.join(sorted(categories))}")

        # GUIDE rules (suggestions)
        if 'GUIDE' in by_level:
            guide_rules = by_level['GUIDE']
            categories = {r.category or 'General' for r in guide_rules}
            lines.append(f"💡 GUIDE ({len(guide_rules)}): {', '.join(sorted(categories))}")

        # ENHANCE rules (context)
        if 'ENHANCE' in by_level:
            enhance_rules = by_level['ENHANCE']
            categories = {r.category or 'General' for r in enhance_rules}
            lines.append(f"✨ ENHANCE ({len(enhance_rules)}): {', '.join(sorted(categories))}")

        return '\n'.join(lines)


class ContextAssemblyError(Exception):
    """Raised when critical context assembly step fails."""
    pass
