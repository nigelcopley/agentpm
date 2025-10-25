"""
Tests for checkpoint models.

Coverage:
- SessionCheckpoint model validation
- CheckpointMetadata model
- Pydantic validation and serialization
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from agentpm.services.claude_integration.checkpoints.models import (
    SessionCheckpoint,
    CheckpointMetadata
)


class TestSessionCheckpoint:
    """Test SessionCheckpoint model."""

    def test_create_minimal_checkpoint(self):
        """Test creating checkpoint with minimal required fields."""
        # Arrange & Act
        checkpoint = SessionCheckpoint(
            session_id=1,
            checkpoint_name="test"
        )

        # Assert
        assert checkpoint.session_id == 1
        assert checkpoint.checkpoint_name == "test"
        assert checkpoint.work_items_snapshot == []
        assert checkpoint.tasks_snapshot == []
        assert checkpoint.context_snapshot == {}
        assert checkpoint.restore_count == 0

    def test_create_full_checkpoint(self, sample_checkpoint):
        """Test creating checkpoint with all fields."""
        # Assert
        assert sample_checkpoint.id is None  # Not assigned yet
        assert sample_checkpoint.session_id == 1
        assert sample_checkpoint.checkpoint_name == "test-checkpoint"
        assert len(sample_checkpoint.work_items_snapshot) == 1
        assert len(sample_checkpoint.tasks_snapshot) == 1
        assert "session_id" in sample_checkpoint.context_snapshot
        assert sample_checkpoint.created_by == "test-user"

    def test_checkpoint_name_validation(self):
        """Test checkpoint name must be non-empty."""
        # Act & Assert
        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=1,
                checkpoint_name=""  # Empty not allowed
            )

    def test_checkpoint_name_max_length(self):
        """Test checkpoint name max length validation."""
        # Arrange
        long_name = "a" * 201  # Exceeds 200 char limit

        # Act & Assert
        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=1,
                checkpoint_name=long_name
            )

    def test_session_id_must_be_positive(self):
        """Test session_id must be > 0."""
        # Act & Assert
        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=0,  # Must be > 0
                checkpoint_name="test"
            )

        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=-1,
                checkpoint_name="test"
            )

    def test_restore_count_must_be_non_negative(self):
        """Test restore_count must be >= 0."""
        # Act & Assert
        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=1,
                checkpoint_name="test",
                restore_count=-1  # Must be >= 0
            )

    def test_size_bytes_must_be_non_negative(self):
        """Test size_bytes must be >= 0."""
        # Act & Assert
        with pytest.raises(ValidationError):
            SessionCheckpoint(
                session_id=1,
                checkpoint_name="test",
                size_bytes=-100  # Must be >= 0
            )

    def test_checkpoint_serialization(self, sample_checkpoint):
        """Test checkpoint can be serialized to dict."""
        # Act
        data = sample_checkpoint.model_dump()

        # Assert
        assert data["session_id"] == 1
        assert data["checkpoint_name"] == "test-checkpoint"
        assert isinstance(data["work_items_snapshot"], list)
        assert isinstance(data["tasks_snapshot"], list)
        assert isinstance(data["context_snapshot"], dict)

    def test_checkpoint_json_serialization(self, sample_checkpoint):
        """Test checkpoint can be serialized to JSON."""
        # Act
        json_str = sample_checkpoint.model_dump_json()

        # Assert
        assert '"session_id":1' in json_str or '"session_id": 1' in json_str
        assert '"checkpoint_name":"test-checkpoint"' in json_str or '"checkpoint_name": "test-checkpoint"' in json_str


class TestCheckpointMetadata:
    """Test CheckpointMetadata model."""

    def test_create_metadata(self):
        """Test creating checkpoint metadata."""
        # Arrange & Act
        metadata = CheckpointMetadata(
            id=1,
            checkpoint_name="test",
            created_at=datetime.now(),
            session_id=1,
            size_bytes=1024,
            restore_count=3,
            notes_preview="Test notes preview"
        )

        # Assert
        assert metadata.id == 1
        assert metadata.checkpoint_name == "test"
        assert metadata.session_id == 1
        assert metadata.size_bytes == 1024
        assert metadata.restore_count == 3

    def test_metadata_notes_preview_truncated(self):
        """Test notes preview respects max length."""
        # Arrange
        long_notes = "a" * 101  # Exceeds 100 char limit

        # Act & Assert
        with pytest.raises(ValidationError):
            CheckpointMetadata(
                id=1,
                checkpoint_name="test",
                created_at=datetime.now(),
                session_id=1,
                size_bytes=100,
                notes_preview=long_notes
            )

    def test_metadata_serialization(self):
        """Test metadata can be serialized."""
        # Arrange
        metadata = CheckpointMetadata(
            id=1,
            checkpoint_name="test",
            created_at=datetime.now(),
            session_id=1,
            size_bytes=1024
        )

        # Act
        data = metadata.model_dump()

        # Assert
        assert data["id"] == 1
        assert data["checkpoint_name"] == "test"
        assert data["size_bytes"] == 1024
