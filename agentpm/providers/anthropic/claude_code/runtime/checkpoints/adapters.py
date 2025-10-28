"""
Checkpoint Adapters

Conversion between Pydantic models and SQLite rows.

Pattern: Three-layer architecture - Adapters layer
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from datetime import datetime

from .models import SessionCheckpoint, CheckpointMetadata


class CheckpointAdapter:
    """
    Convert between SessionCheckpoint models and SQLite rows.

    Handles JSON serialization for snapshot fields.

    Example:
        # To database
        checkpoint = SessionCheckpoint(...)
        db_row = CheckpointAdapter.to_database(checkpoint)

        # From database
        checkpoint = CheckpointAdapter.from_database(db_row)
    """

    @staticmethod
    def to_database(checkpoint: SessionCheckpoint) -> Dict[str, Any]:
        """
        Convert SessionCheckpoint to database row format.

        Args:
            checkpoint: Checkpoint model

        Returns:
            Dictionary for SQLite insertion

        Example:
            checkpoint = SessionCheckpoint(
                session_id=1,
                checkpoint_name="test",
                work_items_snapshot=[{"id": 1}]
            )
            row = CheckpointAdapter.to_database(checkpoint)
            # row["work_items_snapshot"] is JSON string
        """
        return {
            "session_id": checkpoint.session_id,
            "checkpoint_name": checkpoint.checkpoint_name,
            "created_at": checkpoint.created_at.isoformat(),
            "work_items_snapshot": json.dumps(checkpoint.work_items_snapshot),
            "tasks_snapshot": json.dumps(checkpoint.tasks_snapshot),
            "context_snapshot": json.dumps(checkpoint.context_snapshot),
            "session_notes": checkpoint.session_notes,
            "created_by": checkpoint.created_by,
            "restore_count": checkpoint.restore_count,
            "size_bytes": checkpoint.size_bytes,
        }

    @staticmethod
    def from_database(row: Dict[str, Any]) -> SessionCheckpoint:
        """
        Convert database row to SessionCheckpoint model.

        Args:
            row: SQLite row as dictionary

        Returns:
            SessionCheckpoint instance

        Example:
            row = cursor.fetchone()
            checkpoint = CheckpointAdapter.from_database(row)
        """
        return SessionCheckpoint(
            id=row["id"],
            session_id=row["session_id"],
            checkpoint_name=row["checkpoint_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            work_items_snapshot=json.loads(row["work_items_snapshot"]),
            tasks_snapshot=json.loads(row["tasks_snapshot"]),
            context_snapshot=json.loads(row["context_snapshot"]),
            session_notes=row["session_notes"] or "",
            created_by=row["created_by"] or "unknown",
            restore_count=row["restore_count"] or 0,
            size_bytes=row["size_bytes"] or 0,
        )

    @staticmethod
    def to_metadata(row: Dict[str, Any]) -> CheckpointMetadata:
        """
        Convert database row to lightweight metadata.

        Used for listing checkpoints without loading full snapshots.

        Args:
            row: SQLite row as dictionary

        Returns:
            CheckpointMetadata instance

        Example:
            rows = cursor.fetchall()
            metadata_list = [CheckpointAdapter.to_metadata(row) for row in rows]
        """
        notes = row["session_notes"] or ""
        notes_preview = notes[:100] if notes else ""

        return CheckpointMetadata(
            id=row["id"],
            checkpoint_name=row["checkpoint_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            session_id=row["session_id"],
            size_bytes=row["size_bytes"] or 0,
            restore_count=row["restore_count"] or 0,
            notes_preview=notes_preview,
        )
