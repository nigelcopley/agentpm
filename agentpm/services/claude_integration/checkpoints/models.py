"""
Checkpoint Models

Pydantic models for session state checkpointing.

Pattern: Three-layer architecture - Models layer
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SessionCheckpoint(BaseModel):
    """
    Session state checkpoint.

    Captures complete session state including work items, tasks, and context
    for later restoration.

    Attributes:
        id: Checkpoint database ID
        session_id: Session database ID
        checkpoint_name: Human-readable checkpoint name
        created_at: Timestamp when checkpoint was created
        work_items_snapshot: Serialized work items state
        tasks_snapshot: Serialized tasks state
        context_snapshot: Serialized context data
        session_notes: User notes about this checkpoint
        created_by: User who created checkpoint
        restore_count: Number of times this checkpoint was restored
        size_bytes: Total size of checkpoint data in bytes

    Example:
        checkpoint = SessionCheckpoint(
            id=1,
            session_id=42,
            checkpoint_name="before-refactor",
            created_at=datetime.now(),
            work_items_snapshot=[
                {"id": 116, "name": "Claude Integration", "status": "active"}
            ],
            tasks_snapshot=[
                {"id": 622, "objective": "Create checkpointing", "status": "active"}
            ],
            context_snapshot={"current_phase": "I1_implementation"},
            session_notes="Checkpoint before major refactoring",
            created_by="developer@example.com",
            restore_count=0,
            size_bytes=2048
        )
    """

    id: Optional[int] = Field(
        default=None,
        description="Checkpoint database ID (auto-assigned)"
    )

    session_id: int = Field(
        ...,
        description="Session database ID",
        gt=0
    )

    checkpoint_name: str = Field(
        ...,
        description="Human-readable checkpoint name",
        min_length=1,
        max_length=200
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when checkpoint was created"
    )

    # State snapshots (JSON-serializable)
    work_items_snapshot: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Serialized work items state at checkpoint time"
    )

    tasks_snapshot: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Serialized tasks state at checkpoint time"
    )

    context_snapshot: Dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized context data (active entities, settings, etc.)"
    )

    # Metadata
    session_notes: str = Field(
        default="",
        description="User notes about this checkpoint",
        max_length=1000
    )

    created_by: str = Field(
        default="unknown",
        description="User who created checkpoint (email or identifier)",
        max_length=200
    )

    restore_count: int = Field(
        default=0,
        description="Number of times this checkpoint was restored",
        ge=0
    )

    size_bytes: int = Field(
        default=0,
        description="Total size of checkpoint data in bytes",
        ge=0
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": 42,
                "checkpoint_name": "before-refactor",
                "created_at": "2025-10-21T10:30:00",
                "work_items_snapshot": [
                    {
                        "id": 116,
                        "name": "Claude Code Comprehensive Integration",
                        "type": "feature",
                        "phase": "I1_implementation",
                        "status": "active"
                    }
                ],
                "tasks_snapshot": [
                    {
                        "id": 622,
                        "objective": "Create Claude Code Checkpointing System",
                        "type": "implementation",
                        "status": "active",
                        "effort_hours": 3.0
                    }
                ],
                "context_snapshot": {
                    "active_work_items": [116],
                    "active_tasks": [622],
                    "current_phase": "I1_implementation",
                    "settings": {
                        "plugin_enabled": True,
                        "verbose_logging": False
                    }
                },
                "session_notes": "Checkpoint before major refactoring of checkpoint system",
                "created_by": "developer@example.com",
                "restore_count": 0,
                "size_bytes": 2048
            }
        }


class CheckpointMetadata(BaseModel):
    """
    Lightweight checkpoint metadata.

    Used for listing checkpoints without loading full state.

    Attributes:
        id: Checkpoint ID
        checkpoint_name: Checkpoint name
        created_at: Creation timestamp
        session_id: Associated session ID
        size_bytes: Data size
        restore_count: Restore count
        notes_preview: First 100 chars of notes

    Example:
        metadata = CheckpointMetadata(
            id=1,
            checkpoint_name="before-refactor",
            created_at=datetime.now(),
            session_id=42,
            size_bytes=2048,
            restore_count=0,
            notes_preview="Checkpoint before major..."
        )
    """

    id: int = Field(..., description="Checkpoint ID")
    checkpoint_name: str = Field(..., description="Checkpoint name")
    created_at: datetime = Field(..., description="Creation timestamp")
    session_id: int = Field(..., description="Associated session ID")
    size_bytes: int = Field(..., description="Data size in bytes")
    restore_count: int = Field(default=0, description="Restore count")
    notes_preview: str = Field(
        default="",
        description="First 100 chars of notes",
        max_length=100
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "checkpoint_name": "before-refactor",
                "created_at": "2025-10-21T10:30:00",
                "session_id": 42,
                "size_bytes": 2048,
                "restore_count": 0,
                "notes_preview": "Checkpoint before major refactoring..."
            }
        }
