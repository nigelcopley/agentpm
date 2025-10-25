"""
Tests for checkpoint adapters.

Coverage:
- SessionCheckpoint to database conversion
- Database to SessionCheckpoint conversion
- CheckpointMetadata conversion
- JSON serialization/deserialization
"""

import pytest
import json
from datetime import datetime

from agentpm.services.claude_integration.checkpoints.models import (
    SessionCheckpoint,
    CheckpointMetadata
)
from agentpm.services.claude_integration.checkpoints.adapters import CheckpointAdapter


class TestCheckpointAdapter:
    """Test CheckpointAdapter conversions."""

    def test_to_database(self, sample_checkpoint):
        """Test converting checkpoint to database format."""
        # Act
        db_row = CheckpointAdapter.to_database(sample_checkpoint)

        # Assert
        assert db_row["session_id"] == 1
        assert db_row["checkpoint_name"] == "test-checkpoint"
        assert isinstance(db_row["work_items_snapshot"], str)  # JSON string
        assert isinstance(db_row["tasks_snapshot"], str)  # JSON string
        assert isinstance(db_row["context_snapshot"], str)  # JSON string
        assert db_row["session_notes"] == "Test checkpoint"
        assert db_row["created_by"] == "test-user"
        assert db_row["restore_count"] == 0

    def test_to_database_json_encoding(self, sample_checkpoint):
        """Test that snapshots are properly JSON encoded."""
        # Act
        db_row = CheckpointAdapter.to_database(sample_checkpoint)

        # Assert - should be valid JSON
        work_items = json.loads(db_row["work_items_snapshot"])
        tasks = json.loads(db_row["tasks_snapshot"])
        context = json.loads(db_row["context_snapshot"])

        assert isinstance(work_items, list)
        assert isinstance(tasks, list)
        assert isinstance(context, dict)
        assert len(work_items) == 1
        assert len(tasks) == 1

    def test_from_database(self):
        """Test converting database row to checkpoint."""
        # Arrange
        db_row = {
            "id": 1,
            "session_id": 42,
            "checkpoint_name": "db-checkpoint",
            "created_at": "2025-10-21T10:30:00",
            "work_items_snapshot": json.dumps([{"id": 1}]),
            "tasks_snapshot": json.dumps([{"id": 2}]),
            "context_snapshot": json.dumps({"test": "data"}),
            "session_notes": "DB notes",
            "created_by": "db-user",
            "restore_count": 5,
            "size_bytes": 2048
        }

        # Act
        checkpoint = CheckpointAdapter.from_database(db_row)

        # Assert
        assert checkpoint.id == 1
        assert checkpoint.session_id == 42
        assert checkpoint.checkpoint_name == "db-checkpoint"
        assert isinstance(checkpoint.created_at, datetime)
        assert checkpoint.work_items_snapshot == [{"id": 1}]
        assert checkpoint.tasks_snapshot == [{"id": 2}]
        assert checkpoint.context_snapshot == {"test": "data"}
        assert checkpoint.session_notes == "DB notes"
        assert checkpoint.created_by == "db-user"
        assert checkpoint.restore_count == 5
        assert checkpoint.size_bytes == 2048

    def test_from_database_with_nulls(self):
        """Test converting database row with NULL values."""
        # Arrange
        db_row = {
            "id": 1,
            "session_id": 1,
            "checkpoint_name": "test",
            "created_at": "2025-10-21T10:30:00",
            "work_items_snapshot": "[]",
            "tasks_snapshot": "[]",
            "context_snapshot": "{}",
            "session_notes": None,  # NULL in database
            "created_by": None,  # NULL in database
            "restore_count": None,  # NULL in database
            "size_bytes": None  # NULL in database
        }

        # Act
        checkpoint = CheckpointAdapter.from_database(db_row)

        # Assert
        assert checkpoint.session_notes == ""  # Converted to empty string
        assert checkpoint.created_by == "unknown"  # Default value
        assert checkpoint.restore_count == 0  # Default value
        assert checkpoint.size_bytes == 0  # Default value

    def test_round_trip_conversion(self, sample_checkpoint):
        """Test converting to database and back preserves data."""
        # Act
        db_row = CheckpointAdapter.to_database(sample_checkpoint)
        # Add ID (would be assigned by database)
        db_row["id"] = 1
        restored = CheckpointAdapter.from_database(db_row)

        # Assert
        assert restored.session_id == sample_checkpoint.session_id
        assert restored.checkpoint_name == sample_checkpoint.checkpoint_name
        assert restored.work_items_snapshot == sample_checkpoint.work_items_snapshot
        assert restored.tasks_snapshot == sample_checkpoint.tasks_snapshot
        assert restored.context_snapshot == sample_checkpoint.context_snapshot
        assert restored.session_notes == sample_checkpoint.session_notes

    def test_to_metadata(self):
        """Test converting database row to metadata."""
        # Arrange
        db_row = {
            "id": 1,
            "checkpoint_name": "test",
            "created_at": "2025-10-21T10:30:00",
            "session_id": 42,
            "size_bytes": 1024,
            "restore_count": 3,
            "session_notes": "This is a long note that should be truncated at 100 characters to create a preview for the metadata display"
        }

        # Act
        metadata = CheckpointAdapter.to_metadata(db_row)

        # Assert
        assert isinstance(metadata, CheckpointMetadata)
        assert metadata.id == 1
        assert metadata.checkpoint_name == "test"
        assert metadata.session_id == 42
        assert metadata.size_bytes == 1024
        assert metadata.restore_count == 3
        assert len(metadata.notes_preview) == 100  # Truncated

    def test_to_metadata_short_notes(self):
        """Test metadata with notes shorter than 100 chars."""
        # Arrange
        db_row = {
            "id": 1,
            "checkpoint_name": "test",
            "created_at": "2025-10-21T10:30:00",
            "session_id": 1,
            "size_bytes": 100,
            "restore_count": 0,
            "session_notes": "Short note"
        }

        # Act
        metadata = CheckpointAdapter.to_metadata(db_row)

        # Assert
        assert metadata.notes_preview == "Short note"  # Not truncated

    def test_to_metadata_null_notes(self):
        """Test metadata with NULL notes."""
        # Arrange
        db_row = {
            "id": 1,
            "checkpoint_name": "test",
            "created_at": "2025-10-21T10:30:00",
            "session_id": 1,
            "size_bytes": 100,
            "restore_count": 0,
            "session_notes": None
        }

        # Act
        metadata = CheckpointAdapter.to_metadata(db_row)

        # Assert
        assert metadata.notes_preview == ""  # Empty string for NULL
