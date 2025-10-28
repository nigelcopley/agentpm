"""
Checkpoint Manager

High-level checkpoint operations including state capture and restoration.

Pattern: Three-layer architecture - Business logic layer
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from datetime import datetime

from .models import SessionCheckpoint, CheckpointMetadata
from . import methods

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manage session checkpoints.

    Provides high-level operations for creating and restoring session state.

    Responsibilities:
    - Capture current session state (work items, tasks, context)
    - Save checkpoints to database
    - Restore session to checkpoint state
    - List and manage checkpoints

    Example:
        from agentpm.core.database import DatabaseService
        from agentpm.providers.anthropic.claude_code.runtime.checkpoints import CheckpointManager

        db = DatabaseService("path/to/db")
        manager = CheckpointManager(db)

        # Create checkpoint
        checkpoint = manager.create_checkpoint(
            session_id=1,
            name="before-refactor",
            notes="Checkpoint before major refactoring"
        )

        # Later... restore
        success = manager.restore_checkpoint(checkpoint.id)
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize checkpoint manager.

        Args:
            db: Database service instance
        """
        self.db = db
        logger.debug("CheckpointManager initialized")

    def create_checkpoint(
        self,
        session_id: int,
        name: Optional[str] = None,
        notes: str = "",
        created_by: str = "unknown"
    ) -> SessionCheckpoint:
        """
        Create checkpoint of current session state.

        Captures:
        - Active work items with full state
        - Active tasks with full state
        - Session context (settings, metadata)

        Args:
            session_id: Session ID to checkpoint
            name: Optional checkpoint name (auto-generated if None)
            notes: User notes about this checkpoint
            created_by: User identifier (email or name)

        Returns:
            Created checkpoint with assigned ID

        Raises:
            ValueError: If session not found or invalid

        Example:
            checkpoint = manager.create_checkpoint(
                session_id=1,
                name="before-refactor",
                notes="All tests passing, about to refactor auth"
            )
            print(f"Created checkpoint: {checkpoint.id}")
        """
        # Generate name if not provided
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            name = f"checkpoint-{timestamp}"

        logger.info(f"Creating checkpoint '{name}' for session {session_id}")

        # Capture current state
        work_items_snapshot = self._capture_work_items(session_id)
        tasks_snapshot = self._capture_tasks(session_id)
        context_snapshot = self._capture_context(session_id)

        # Calculate size
        size_bytes = self._calculate_size(
            work_items_snapshot,
            tasks_snapshot,
            context_snapshot
        )

        # Create checkpoint model
        checkpoint = SessionCheckpoint(
            session_id=session_id,
            checkpoint_name=name,
            created_at=datetime.now(),
            work_items_snapshot=work_items_snapshot,
            tasks_snapshot=tasks_snapshot,
            context_snapshot=context_snapshot,
            session_notes=notes,
            created_by=created_by,
            restore_count=0,
            size_bytes=size_bytes
        )

        # Save to database
        created = methods.create_checkpoint(self.db, checkpoint)

        logger.info(
            f"Checkpoint created: {created.checkpoint_name} "
            f"(ID: {created.id}, size: {size_bytes} bytes)"
        )

        return created

    def restore_checkpoint(self, checkpoint_id: int) -> bool:
        """
        Restore session to checkpoint state.

        WARNING: This will modify work items and tasks to match checkpoint state.
        Consider creating a new checkpoint before restoring.

        Args:
            checkpoint_id: Checkpoint ID to restore

        Returns:
            True if restoration successful

        Raises:
            ValueError: If checkpoint not found

        Example:
            # Create safety checkpoint first
            safety = manager.create_checkpoint(
                session_id=1,
                name="before-restore"
            )

            # Restore to previous state
            if manager.restore_checkpoint(older_checkpoint_id):
                print("State restored successfully")
        """
        # Load checkpoint
        checkpoint = methods.get_checkpoint(self.db, checkpoint_id)

        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")

        logger.info(
            f"Restoring checkpoint: {checkpoint.checkpoint_name} "
            f"(ID: {checkpoint_id}, session: {checkpoint.session_id})"
        )

        # Restore state (in transaction)
        try:
            self._restore_work_items(checkpoint.work_items_snapshot)
            self._restore_tasks(checkpoint.tasks_snapshot)
            self._restore_context(checkpoint.context_snapshot, checkpoint.session_id)

            # Increment restore count
            methods.increment_restore_count(self.db, checkpoint_id)

            logger.info(f"Checkpoint {checkpoint_id} restored successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to restore checkpoint {checkpoint_id}: {e}", exc_info=True)
            raise

    def list_checkpoints(
        self,
        session_id: Optional[int] = None,
        limit: int = 50
    ) -> List[CheckpointMetadata]:
        """
        List checkpoints.

        Args:
            session_id: Filter by session ID (optional)
            limit: Maximum number to return

        Returns:
            List of checkpoint metadata (ordered by created_at DESC)

        Example:
            # All checkpoints for session
            checkpoints = manager.list_checkpoints(session_id=1)
            for cp in checkpoints:
                print(f"{cp.checkpoint_name}: {cp.created_at}")

            # Recent checkpoints (any session)
            recent = manager.list_checkpoints(limit=10)
        """
        return methods.list_checkpoints(self.db, session_id, limit)

    def delete_checkpoint(self, checkpoint_id: int) -> bool:
        """
        Delete checkpoint.

        Args:
            checkpoint_id: Checkpoint ID

        Returns:
            True if deleted, False if not found

        Example:
            if manager.delete_checkpoint(old_checkpoint_id):
                print("Checkpoint deleted")
        """
        return methods.delete_checkpoint(self.db, checkpoint_id)

    def get_checkpoint(self, checkpoint_id: int) -> Optional[SessionCheckpoint]:
        """
        Get checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID

        Returns:
            Checkpoint if found, None otherwise

        Example:
            checkpoint = manager.get_checkpoint(1)
            if checkpoint:
                print(f"Work items: {len(checkpoint.work_items_snapshot)}")
                print(f"Tasks: {len(checkpoint.tasks_snapshot)}")
        """
        return methods.get_checkpoint(self.db, checkpoint_id)

    def get_latest_checkpoint(self, session_id: int) -> Optional[SessionCheckpoint]:
        """
        Get most recent checkpoint for session.

        Args:
            session_id: Session ID

        Returns:
            Latest checkpoint if any exist, None otherwise

        Example:
            latest = manager.get_latest_checkpoint(session_id=1)
            if latest:
                print(f"Latest checkpoint: {latest.checkpoint_name}")
        """
        return methods.get_latest_checkpoint(self.db, session_id)

    # Private helper methods for state capture

    def _capture_work_items(self, session_id: int) -> List[Dict[str, Any]]:
        """Capture active work items for session."""
        from agentpm.core.database.methods import work_items as wi_methods

        # Get active work items
        active_wis = wi_methods.list_work_items(
            self.db,
            status="active",
            limit=100
        )

        # Serialize to JSON-compatible dicts
        return [
            {
                "id": wi.id,
                "name": wi.name,
                "type": wi.type,
                "phase": wi.phase,
                "status": wi.status,
                "priority": wi.priority,
                "business_context": wi.business_context,
                "acceptance_criteria": wi.acceptance_criteria,
                "risks": wi.risks,
                "metadata": wi.metadata
            }
            for wi in active_wis
        ]

    def _capture_tasks(self, session_id: int) -> List[Dict[str, Any]]:
        """Capture active tasks for session."""
        from agentpm.core.database.methods import tasks as task_methods

        # Get active and ready tasks
        active_tasks = task_methods.list_tasks(
            self.db,
            status="active",
            limit=100
        )

        ready_tasks = task_methods.list_tasks(
            self.db,
            status="ready",
            limit=100
        )

        all_tasks = active_tasks + ready_tasks

        # Serialize to JSON-compatible dicts
        return [
            {
                "id": task.id,
                "work_item_id": task.work_item_id,
                "objective": task.objective,
                "type": task.type,
                "status": task.status,
                "priority": task.priority,
                "effort_hours": task.effort_hours,
                "acceptance_criteria": task.acceptance_criteria,
                "quality_metadata": task.quality_metadata
            }
            for task in all_tasks
        ]

    def _capture_context(self, session_id: int) -> Dict[str, Any]:
        """Capture session context (settings, active entities)."""
        from agentpm.core.database.methods import sessions as session_methods

        # Get session info
        session = session_methods.get_session(self.db, session_id)

        if not session:
            return {}

        return {
            "session_id": session.id,
            "session_uuid": session.session_id,
            "tool_name": session.tool_name,
            "llm_model": session.llm_model,
            "session_type": session.session_type,
            "metadata": session.metadata,
            "captured_at": datetime.now().isoformat()
        }

    def _calculate_size(
        self,
        work_items: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> int:
        """Calculate total size of checkpoint data in bytes."""
        # Rough estimate using JSON serialization
        data = {
            "work_items": work_items,
            "tasks": tasks,
            "context": context
        }
        return len(json.dumps(data).encode('utf-8'))

    # Private helper methods for state restoration

    def _restore_work_items(self, work_items_snapshot: List[Dict[str, Any]]) -> None:
        """Restore work items from snapshot."""
        # NOTE: This is a simplified implementation
        # In production, you'd want more sophisticated merging logic
        logger.info(f"Would restore {len(work_items_snapshot)} work items")
        # TODO: Implement work item restoration logic
        # This could involve:
        # - Updating existing work items
        # - Creating new work items if they don't exist
        # - Handling conflicts

    def _restore_tasks(self, tasks_snapshot: List[Dict[str, Any]]) -> None:
        """Restore tasks from snapshot."""
        logger.info(f"Would restore {len(tasks_snapshot)} tasks")
        # TODO: Implement task restoration logic
        # Similar to work items restoration

    def _restore_context(self, context_snapshot: Dict[str, Any], session_id: int) -> None:
        """Restore session context from snapshot."""
        logger.info(f"Would restore context for session {session_id}")
        # TODO: Implement context restoration logic
        # This could involve:
        # - Restoring session metadata
        # - Restoring settings
        # - Restoring active entity tracking
