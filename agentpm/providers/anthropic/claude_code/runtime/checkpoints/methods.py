"""
Checkpoint Database Methods

CRUD operations for session checkpoints.

Pattern: Three-layer architecture - Methods layer
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional

from .models import SessionCheckpoint, CheckpointMetadata
from .adapters import CheckpointAdapter

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


def create_checkpoint(
    db: DatabaseService,
    checkpoint: SessionCheckpoint
) -> SessionCheckpoint:
    """
    Create a new checkpoint.

    Args:
        db: Database service
        checkpoint: Checkpoint to create (id will be assigned)

    Returns:
        Created checkpoint with assigned ID

    Raises:
        ValueError: If checkpoint data invalid
        sqlite3.IntegrityError: If foreign key constraint fails

    Example:
        checkpoint = SessionCheckpoint(
            session_id=1,
            checkpoint_name="before-refactor",
            work_items_snapshot=[...],
            tasks_snapshot=[...],
            context_snapshot={...}
        )
        created = create_checkpoint(db, checkpoint)
        print(f"Created checkpoint ID: {created.id}")
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        # Convert to database format
        db_row = CheckpointAdapter.to_database(checkpoint)

        # Insert
        cursor.execute("""
            INSERT INTO session_checkpoints (
                session_id,
                checkpoint_name,
                created_at,
                work_items_snapshot,
                tasks_snapshot,
                context_snapshot,
                session_notes,
                created_by,
                restore_count,
                size_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            db_row["session_id"],
            db_row["checkpoint_name"],
            db_row["created_at"],
            db_row["work_items_snapshot"],
            db_row["tasks_snapshot"],
            db_row["context_snapshot"],
            db_row["session_notes"],
            db_row["created_by"],
            db_row["restore_count"],
            db_row["size_bytes"],
        ))

        checkpoint_id = cursor.lastrowid
        conn.commit()

        logger.info(
            f"Created checkpoint: {checkpoint.checkpoint_name} "
            f"(ID: {checkpoint_id}, session: {checkpoint.session_id})"
        )

        # Return with assigned ID
        checkpoint.id = checkpoint_id
        return checkpoint


def get_checkpoint(
    db: DatabaseService,
    checkpoint_id: int
) -> Optional[SessionCheckpoint]:
    """
    Get checkpoint by ID.

    Args:
        db: Database service
        checkpoint_id: Checkpoint ID

    Returns:
        Checkpoint if found, None otherwise

    Example:
        checkpoint = get_checkpoint(db, 1)
        if checkpoint:
            print(f"Found: {checkpoint.checkpoint_name}")
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM session_checkpoints
            WHERE id = ?
        """, (checkpoint_id,))

        row = cursor.fetchone()

        if not row:
            return None

        # Convert to dict for adapter
        row_dict = dict(row)
        return CheckpointAdapter.from_database(row_dict)


def list_checkpoints(
    db: DatabaseService,
    session_id: Optional[int] = None,
    limit: int = 50
) -> List[CheckpointMetadata]:
    """
    List checkpoints.

    Args:
        db: Database service
        session_id: Filter by session ID (optional)
        limit: Maximum number to return

    Returns:
        List of checkpoint metadata (ordered by created_at DESC)

    Example:
        # All checkpoints for session
        checkpoints = list_checkpoints(db, session_id=1)

        # Recent checkpoints (any session)
        recent = list_checkpoints(db, limit=10)
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        if session_id:
            cursor.execute("""
                SELECT id, checkpoint_name, created_at, session_id,
                       size_bytes, restore_count, session_notes
                FROM session_checkpoints
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT id, checkpoint_name, created_at, session_id,
                       size_bytes, restore_count, session_notes
                FROM session_checkpoints
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        return [
            CheckpointAdapter.to_metadata(dict(row))
            for row in rows
        ]


def delete_checkpoint(
    db: DatabaseService,
    checkpoint_id: int
) -> bool:
    """
    Delete checkpoint.

    Args:
        db: Database service
        checkpoint_id: Checkpoint ID to delete

    Returns:
        True if deleted, False if not found

    Example:
        if delete_checkpoint(db, 1):
            print("Checkpoint deleted")
        else:
            print("Checkpoint not found")
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM session_checkpoints
            WHERE id = ?
        """, (checkpoint_id,))

        deleted_count = cursor.rowcount
        conn.commit()

        if deleted_count > 0:
            logger.info(f"Deleted checkpoint ID: {checkpoint_id}")
            return True
        else:
            logger.warning(f"Checkpoint ID {checkpoint_id} not found")
            return False


def increment_restore_count(
    db: DatabaseService,
    checkpoint_id: int
) -> bool:
    """
    Increment restore count for checkpoint.

    Called when checkpoint is restored.

    Args:
        db: Database service
        checkpoint_id: Checkpoint ID

    Returns:
        True if updated, False if not found

    Example:
        if increment_restore_count(db, 1):
            print("Restore count incremented")
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE session_checkpoints
            SET restore_count = restore_count + 1
            WHERE id = ?
        """, (checkpoint_id,))

        updated_count = cursor.rowcount
        conn.commit()

        if updated_count > 0:
            logger.debug(f"Incremented restore count for checkpoint {checkpoint_id}")
            return True
        else:
            logger.warning(f"Checkpoint ID {checkpoint_id} not found")
            return False


def get_latest_checkpoint(
    db: DatabaseService,
    session_id: int
) -> Optional[SessionCheckpoint]:
    """
    Get most recent checkpoint for session.

    Args:
        db: Database service
        session_id: Session ID

    Returns:
        Latest checkpoint if any exist, None otherwise

    Example:
        latest = get_latest_checkpoint(db, session_id=1)
        if latest:
            print(f"Latest: {latest.checkpoint_name}")
    """
    with db.connect() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM session_checkpoints
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (session_id,))

        row = cursor.fetchone()

        if not row:
            return None

        row_dict = dict(row)
        return CheckpointAdapter.from_database(row_dict)
