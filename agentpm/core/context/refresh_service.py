"""
Context Refresh Service - Staleness Detection & Context Refresh

Implements context refresh and staleness detection:
- Detect stale contexts based on age and code changes
- Trigger context refresh when needed
- Invalidate cache on updates
- Auto-refresh for high-priority stale contexts

Pattern: Service pattern with dependency on ContextAssemblyService
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import subprocess

from ..database.service import DatabaseService
from ..database.enums import EntityType
from .assembly_service import ContextAssemblyService
from .freshness import ContextFreshness
from .models import ContextPayload
from .triggers import RefreshTriggers


@dataclass
class StaleContext:
    """
    Represents a stale context that needs refresh.

    Attributes:
        context_id: ID of the stale context
        entity_type: 'project', 'work_item', or 'task'
        entity_id: ID of the entity
        days_old: Age of context in days
        priority: 'high', 'medium', or 'low'
        reasons: List of reasons for staleness
    """
    context_id: int
    entity_type: str
    entity_id: int
    days_old: int
    priority: str
    reasons: List[str]


@dataclass
class RefreshReport:
    """
    Report of refresh operations.

    Attributes:
        stale: List of stale contexts detected
        refreshed: List of contexts that were refreshed
        failed: List of contexts that failed to refresh
        duration_ms: Total refresh operation duration
    """
    stale: List[StaleContext]
    refreshed: List[int]  # Context IDs
    failed: List[Dict[str, Any]]  # {context_id, error}
    duration_ms: float


class RefreshService:
    """
    Context refresh and staleness detection service.

    Monitors context freshness and triggers refresh operations when:
    - Context is >7 days old (warning)
    - Context is >30 days old (critical)
    - Code changes detected since last context assembly (git commits)
    - Plugin versions changed

    Integration with ContextFreshness (WI-0005) for age-based detection.
    """

    # Staleness thresholds (days)
    WARNING_THRESHOLD = 7
    CRITICAL_THRESHOLD = 30

    def __init__(
        self,
        db: DatabaseService,
        assembler: ContextAssemblyService,
        project_path: Path
    ):
        """
        Initialize refresh service.

        Args:
            db: Database service for context queries
            assembler: Context assembly service for refresh operations
            project_path: Project root directory (for git checks)
        """
        self.db = db
        self.assembler = assembler
        self.project_path = project_path

    def detect_stale_contexts(
        self,
        project_id: int,
        threshold_days: int = 7,
        check_git: bool = True
    ) -> List[StaleContext]:
        """
        Detect contexts that need refresh.

        Staleness criteria:
        1. Age-based: Context updated >threshold_days ago
        2. Code changes: Git commits since last context assembly
        3. Plugin changes: Plugin versions changed (Phase 2)

        Args:
            project_id: Project ID to check
            threshold_days: Age threshold in days (default: 7)
            check_git: Check git log for code changes (default: True)

        Returns:
            List of StaleContext objects, prioritized by severity

        Performance: <100ms for typical project
        """
        from ..database.methods import contexts, projects

        stale_contexts = []

        # Get project for path validation
        project = projects.get_project(self.db, project_id)
        if not project:
            return []

        # Load all contexts for this project (tasks, work items, project)
        # Start with task contexts (most specific)
        task_contexts = self._get_task_contexts_for_project(project_id)

        for ctx in task_contexts:
            if not ctx.updated_at:
                continue

            # Calculate age
            age = (datetime.now() - ctx.updated_at).days

            # Check if stale based on age
            if age < threshold_days:
                continue

            reasons = []
            priority = 'low'

            # Age-based staleness with clear priority bands
            if age >= self.CRITICAL_THRESHOLD:  # 30+ days
                reasons.append(f"Context is {age} days old (critically outdated)")
                priority = 'high'
            elif age >= threshold_days:  # 7-29 days
                reasons.append(f"Context is {age} days old")
                priority = 'medium'

            # Code change detection (if enabled)
            if check_git and self._has_code_changes_since(ctx.updated_at):
                commits_count = self._count_commits_since(ctx.updated_at)
                reasons.append(f"Code changed ({commits_count} commits since last update)")
                # Upgrade priority if code changed
                if priority == 'low':
                    priority = 'medium'
                elif priority == 'medium':
                    priority = 'high'

            # Add to stale list
            stale_contexts.append(StaleContext(
                context_id=ctx.id,
                entity_type='task',
                entity_id=ctx.entity_id,
                days_old=age,
                priority=priority,
                reasons=reasons
            ))

        # Sort by priority (high -> medium -> low) then by age (oldest first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        stale_contexts.sort(
            key=lambda x: (priority_order[x.priority], -x.days_old)
        )

        return stale_contexts

    def trigger_refresh(
        self,
        context_id: int,
        reason: str
    ) -> ContextPayload:
        """
        Trigger context refresh for a specific context.

        Steps:
        1. Load context to get entity info
        2. Invalidate cache for this context (if caching enabled)
        3. Re-run ContextAssemblyService.assemble_task_context()
        4. Update context.updated_at timestamp
        5. Log refresh event

        Args:
            context_id: Context ID to refresh
            reason: Reason for refresh (for logging)

        Returns:
            Fresh ContextPayload

        Raises:
            ContextAssemblyError: If refresh fails

        Performance: <200ms (delegates to ContextAssemblyService)
        """
        from ..database.methods import contexts

        # Load context to get entity info
        ctx = contexts.get_context(self.db, context_id)
        if not ctx:
            from .assembly_service import ContextAssemblyError
            raise ContextAssemblyError(f"Context {context_id} not found")

        # Invalidate cache (if assembler has cache)
        self._invalidate_cache(ctx.entity_type, ctx.entity_id)

        # Re-assemble context
        if ctx.entity_type == EntityType.TASK:
            payload = self.assembler.assemble_task_context(
                task_id=ctx.entity_id
            )
        else:
            # Work item and project contexts not implemented in MVP
            # Phase 2: Add work_item and project context assembly
            from .assembly_service import ContextAssemblyError
            raise ContextAssemblyError(
                f"Refresh not implemented for {ctx.entity_type} contexts (MVP limitation)"
            )

        # Update context.updated_at timestamp
        contexts.update_context(
            self.db,
            context_id=context_id,
            six_w=payload.merged_6w,
            confidence_score=payload.confidence_score
        )

        # Log refresh event (simple implementation)
        # Phase 2: Add structured event logging
        print(f"[RefreshService] Refreshed context {context_id} - Reason: {reason}")

        return payload

    def auto_refresh_check(
        self,
        project_id: int,
        auto_refresh_high_priority: bool = True,
        use_smart_triggers: bool = True
    ) -> RefreshReport:
        """
        Check all contexts and auto-refresh if needed.

        Background task pattern - runs periodically (e.g., via cron or hook).
        Only auto-refreshes high-priority stale contexts by default.

        Args:
            project_id: Project ID to check
            auto_refresh_high_priority: Auto-refresh high-priority contexts (default: True)
            use_smart_triggers: Use RefreshTriggers for intelligent detection (default: True)

        Returns:
            RefreshReport with detection and refresh results

        Performance: Variable (depends on number of stale contexts)
        """
        import time
        start_time = time.perf_counter()

        # Detect stale contexts
        stale = self.detect_stale_contexts(project_id, threshold_days=7)

        refreshed = []
        failed = []

        # Auto-refresh high-priority contexts
        if auto_refresh_high_priority:
            high_priority = [ctx for ctx in stale if ctx.priority == 'high']

            for ctx in high_priority:
                # Use smart triggers if enabled
                if use_smart_triggers:
                    # Load context to get timestamp
                    from ..database.methods import contexts
                    context_obj = contexts.get_context(self.db, ctx.context_id)
                    if not context_obj:
                        continue

                    # Check if refresh needed via triggers
                    should_refresh, trigger_reasons = RefreshTriggers.should_auto_refresh(
                        db=self.db,
                        project_path=self.project_path,
                        context_id=ctx.context_id,
                        entity_type=EntityType.TASK if ctx.entity_type == 'task' else EntityType.WORK_ITEM,
                        entity_id=ctx.entity_id,
                        context_updated_at=context_obj.updated_at
                    )

                    if not should_refresh:
                        continue  # Skip this context

                # Trigger refresh
                try:
                    self.trigger_refresh(
                        context_id=ctx.context_id,
                        reason=f"Auto-refresh: {', '.join(ctx.reasons)}"
                    )
                    refreshed.append(ctx.context_id)
                except Exception as e:
                    failed.append({
                        'context_id': ctx.context_id,
                        'entity_type': ctx.entity_type,
                        'entity_id': ctx.entity_id,
                        'error': str(e)
                    })

        duration_ms = (time.perf_counter() - start_time) * 1000

        return RefreshReport(
            stale=stale,
            refreshed=refreshed,
            failed=failed,
            duration_ms=duration_ms
        )

    # ─────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────────────────

    def _get_task_contexts_for_project(self, project_id: int):
        """
        Get all task contexts for a project.

        Args:
            project_id: Project ID

        Returns:
            List of Context objects
        """
        from ..database.methods import contexts, tasks, work_items

        # Get all work items for project
        wis = work_items.list_work_items(self.db, project_id=project_id)

        # Get all tasks for these work items
        task_contexts = []
        for wi in wis:
            wi_tasks = tasks.list_tasks(self.db, work_item_id=wi.id)
            for task in wi_tasks:
                # Try to get context for this task
                try:
                    ctx = contexts.get_entity_context(
                        self.db,
                        entity_type=EntityType.TASK,
                        entity_id=task.id
                    )
                    if ctx:
                        task_contexts.append(ctx)
                except Exception:
                    # No context exists - skip
                    continue

        return task_contexts

    def _has_code_changes_since(self, since: datetime) -> bool:
        """
        Check if code changed since timestamp (using git).

        Args:
            since: Timestamp to check from

        Returns:
            True if commits exist after timestamp
        """
        try:
            # Check if commits exist since timestamp
            result = subprocess.run(
                ['git', 'log', '--since', since.isoformat(), '--oneline'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Non-empty output = commits exist
                return bool(result.stdout.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            # Git not available, not a repo, or timeout - assume no changes
            pass

        return False

    def _count_commits_since(self, since: datetime) -> int:
        """
        Count commits since timestamp.

        Args:
            since: Timestamp to count from

        Returns:
            Number of commits (0 if git unavailable)
        """
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', '--since', since.isoformat(), 'HEAD'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return int(result.stdout.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, subprocess.CalledProcessError):
            pass

        return 0

    def _invalidate_cache(self, entity_type: EntityType, entity_id: int):
        """
        Invalidate cache for entity (if caching enabled).

        Args:
            entity_type: Entity type (PROJECT, WORK_ITEM, TASK)
            entity_id: Entity ID
        """
        # Delegate to ContextAssemblyService cache invalidation
        entity_type_str = entity_type.value if hasattr(entity_type, 'value') else str(entity_type).lower()
        self.assembler.invalidate_cache(
            entity_type=entity_type_str,
            entity_id=entity_id
        )
