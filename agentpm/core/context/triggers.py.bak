"""
Context Refresh Triggers - Event Detection for Auto-Refresh

Monitors for events that should trigger context refresh:
- Code changes (git commits)
- 6W context updates
- Staleness thresholds exceeded

Pattern: Static utility methods for trigger detection
MVP Scope: Simplified detection without full event system
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import subprocess

from ..database.service import DatabaseService
from ..database.enums import EntityType


class RefreshTriggers:
    """
    Detect events that should trigger context refresh.

    MVP Scope:
    - Git-based code change detection
    - Simple 6W update checks
    - Age-based staleness detection

    Phase 2:
    - Event-driven architecture
    - File system watchers
    - Plugin version change detection
    """

    @staticmethod
    def detect_code_changes(
        project_path: Path,
        since: Optional[datetime] = None
    ) -> bool:
        """
        Check if code changed since timestamp (using git).

        Args:
            project_path: Project root directory
            since: Timestamp to check from (None = last 24 hours)

        Returns:
            True if commits exist after timestamp

        Performance: <50ms (subprocess call to git)

        Example:
            >>> RefreshTriggers.detect_code_changes(Path('/project'), since=datetime.now() - timedelta(days=7))
            True  # Commits in last 7 days
        """
        if not (project_path / '.git').exists():
            return False

        # Default: Check last 24 hours
        if since is None:
            from datetime import timedelta
            since = datetime.now() - timedelta(days=1)

        try:
            # Check if commits exist since timestamp
            result = subprocess.run(
                ['git', 'log', '--since', since.isoformat(), '--oneline'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Non-empty output = commits exist
                return bool(result.stdout.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Git not available or timeout - assume no changes
            pass

        return False

    @staticmethod
    def detect_six_w_updates(
        db: DatabaseService,
        context_id: int,
        entity_type: EntityType,
        entity_id: int
    ) -> bool:
        """
        Check if 6W content updated after context assembly.

        Compares context.updated_at with entity.updated_at to detect
        changes that haven't been reflected in assembled context.

        Args:
            db: Database service
            context_id: Context ID to check
            entity_type: Entity type (PROJECT, WORK_ITEM, TASK)
            entity_id: Entity ID

        Returns:
            True if entity updated after context

        Performance: <10ms (2 database queries)

        Example:
            >>> RefreshTriggers.detect_six_w_updates(db, context_id=5, entity_type=EntityType.TASK, entity_id=45)
            True  # Task updated after context
        """
        from ..database.methods import contexts, tasks, work_items, projects

        try:
            # Get context timestamp
            ctx = contexts.get_context(db, context_id)
            if not ctx or not ctx.updated_at:
                return True  # No context or no timestamp = needs refresh

            # Get entity timestamp
            entity = None
            if entity_type == EntityType.TASK:
                entity = tasks.get_task(db, entity_id)
            elif entity_type == EntityType.WORK_ITEM:
                entity = work_items.get_work_item(db, entity_id)
            elif entity_type == EntityType.PROJECT:
                entity = projects.get_project(db, entity_id)

            if not entity or not hasattr(entity, 'updated_at') or not entity.updated_at:
                return False  # No entity or no timestamp = can't detect

            # Compare timestamps
            return entity.updated_at > ctx.updated_at

        except Exception:
            # Error accessing database - assume no update
            return False

    @staticmethod
    def check_staleness_threshold(
        context_updated_at: datetime,
        warning_days: int = 7,
        critical_days: int = 30
    ) -> Optional[str]:
        """
        Check if context exceeded staleness threshold.

        Args:
            context_updated_at: When context was last updated
            warning_days: Warning threshold (default: 7)
            critical_days: Critical threshold (default: 30)

        Returns:
            'critical', 'warning', or None

        Example:
            >>> RefreshTriggers.check_staleness_threshold(datetime.now() - timedelta(days=10))
            'warning'  # 10 days old
        """
        age_days = (datetime.now() - context_updated_at).days

        if age_days >= critical_days:
            return 'critical'
        elif age_days >= warning_days:
            return 'warning'
        else:
            return None

    @staticmethod
    def should_auto_refresh(
        db: DatabaseService,
        project_path: Path,
        context_id: int,
        entity_type: EntityType,
        entity_id: int,
        context_updated_at: datetime
    ) -> tuple[bool, list[str]]:
        """
        Determine if context should be auto-refreshed.

        Checks all trigger conditions and returns decision + reasons.

        Args:
            db: Database service
            project_path: Project root directory
            context_id: Context ID
            entity_type: Entity type
            entity_id: Entity ID
            context_updated_at: When context was last updated

        Returns:
            (should_refresh, reasons) tuple

        Example:
            >>> RefreshTriggers.should_auto_refresh(db, Path('/project'), 5, EntityType.TASK, 45, datetime.now() - timedelta(days=10))
            (True, ['Context is 10 days old (warning)', 'Code changed (3 commits)'])
        """
        reasons = []
        should_refresh = False

        # Check staleness threshold
        staleness = RefreshTriggers.check_staleness_threshold(context_updated_at)
        if staleness == 'critical':
            reasons.append(f"Context critically stale (>{30} days old)")
            should_refresh = True
        elif staleness == 'warning':
            reasons.append(f"Context stale (>{7} days old)")
            # Warning alone doesn't trigger auto-refresh (user discretion)

        # Check code changes
        if RefreshTriggers.detect_code_changes(project_path, since=context_updated_at):
            reasons.append("Code changed since last context update")
            should_refresh = True

        # Check 6W updates
        if RefreshTriggers.detect_six_w_updates(db, context_id, entity_type, entity_id):
            reasons.append("6W content updated")
            should_refresh = True

        return should_refresh, reasons
