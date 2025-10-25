"""
Integration tests for checkpoint system.

Tests the complete workflow:
- Creating checkpoints
- Listing checkpoints
- Restoring checkpoints
- Manager + methods + adapters integration
"""

import pytest
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.services.claude_integration.checkpoints import CheckpointManager
from agentpm.services.claude_integration.checkpoints.models import SessionCheckpoint
from agentpm.services.claude_integration.checkpoints import methods


class TestCheckpointIntegration:
    """Integration tests for checkpoint system."""

    def test_create_and_retrieve_checkpoint(self, db_service):
        """Test creating checkpoint and retrieving it."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create a session first
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-001",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        # Act - Create checkpoint
        checkpoint = manager.create_checkpoint(
            session_id=created_session.id,
            name="integration-test",
            notes="Integration test checkpoint"
        )

        # Assert - Checkpoint created
        assert checkpoint.id is not None
        assert checkpoint.checkpoint_name == "integration-test"

        # Act - Retrieve checkpoint
        retrieved = manager.get_checkpoint(checkpoint.id)

        # Assert - Retrieved matches created
        assert retrieved is not None
        assert retrieved.id == checkpoint.id
        assert retrieved.checkpoint_name == checkpoint.checkpoint_name
        assert retrieved.session_id == created_session.id

    def test_list_checkpoints_for_session(self, db_service):
        """Test listing checkpoints for a specific session."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-002",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        # Create multiple checkpoints
        cp1 = manager.create_checkpoint(
            session_id=created_session.id,
            name="checkpoint-1"
        )
        cp2 = manager.create_checkpoint(
            session_id=created_session.id,
            name="checkpoint-2"
        )
        cp3 = manager.create_checkpoint(
            session_id=created_session.id,
            name="checkpoint-3"
        )

        # Act
        checkpoints = manager.list_checkpoints(session_id=created_session.id)

        # Assert
        assert len(checkpoints) == 3
        # Should be ordered by created_at DESC (newest first)
        names = [cp.checkpoint_name for cp in checkpoints]
        assert "checkpoint-3" in names
        assert "checkpoint-2" in names
        assert "checkpoint-1" in names

    def test_delete_checkpoint(self, db_service):
        """Test deleting a checkpoint."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session and checkpoint
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-003",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        checkpoint = manager.create_checkpoint(
            session_id=created_session.id,
            name="to-delete"
        )

        # Act
        deleted = manager.delete_checkpoint(checkpoint.id)

        # Assert
        assert deleted is True

        # Verify it's gone
        retrieved = manager.get_checkpoint(checkpoint.id)
        assert retrieved is None

    def test_get_latest_checkpoint(self, db_service):
        """Test getting the most recent checkpoint."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-004",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        # Create checkpoints with small delay to ensure ordering
        import time
        cp1 = manager.create_checkpoint(
            session_id=created_session.id,
            name="old-checkpoint"
        )
        time.sleep(0.01)
        cp2 = manager.create_checkpoint(
            session_id=created_session.id,
            name="latest-checkpoint"
        )

        # Act
        latest = manager.get_latest_checkpoint(created_session.id)

        # Assert
        assert latest is not None
        assert latest.checkpoint_name == "latest-checkpoint"
        assert latest.id == cp2.id

    def test_checkpoint_captures_work_items(self, db_service):
        """Test that checkpoint captures active work items."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session and work item
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.methods import work_items as wi_methods
        from agentpm.core.database.models.session import Session
        from agentpm.core.database.models.work_item import WorkItem

        session = Session(
            session_id="test-session-005",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        work_item = WorkItem(
            project_id=1,
            name="Test Work Item",
            type="feature",
            phase="I1_implementation",
            status="active"
        )
        wi_methods.create_work_item(db_service, work_item)

        # Act
        checkpoint = manager.create_checkpoint(
            session_id=created_session.id,
            name="with-work-items"
        )

        # Assert
        assert len(checkpoint.work_items_snapshot) > 0
        # Check that work item was captured
        captured = checkpoint.work_items_snapshot[0]
        assert captured["name"] == "Test Work Item"
        assert captured["type"] == "feature"

    def test_checkpoint_size_calculation(self, db_service):
        """Test that checkpoint size is calculated."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-006",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        # Act
        checkpoint = manager.create_checkpoint(
            session_id=created_session.id,
            name="size-test"
        )

        # Assert
        assert checkpoint.size_bytes > 0  # Should have calculated size

    def test_restore_checkpoint_increments_count(self, db_service):
        """Test that restoring checkpoint increments restore count."""
        # Arrange
        manager = CheckpointManager(db_service)

        # Create session
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.models.session import Session

        session = Session(
            session_id="test-session-007",
            project_id=1,
            tool_name="claude_code",
            started_at=datetime.now().isoformat()
        )
        created_session = session_methods.create_session(db_service, session)

        checkpoint = manager.create_checkpoint(
            session_id=created_session.id,
            name="restore-test"
        )

        assert checkpoint.restore_count == 0

        # Act - Restore (note: actual restoration logic is TODO)
        manager.restore_checkpoint(checkpoint.id)

        # Assert - Count incremented
        restored = manager.get_checkpoint(checkpoint.id)
        assert restored.restore_count == 1


@pytest.fixture
def db_service(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test.db"
    db = DatabaseService(str(db_path))

    # Run migrations
    from agentpm.core.database.migrations import MigrationManager
    migration_manager = MigrationManager(db)
    migration_manager.run_all_pending()

    yield db

    # No cleanup needed - DatabaseService doesn't have close()
