"""
Pytest fixtures for checkpoint tests.
"""

import pytest
from datetime import datetime
from agentpm.providers.anthropic.claude_code.runtime.checkpoints.models import SessionCheckpoint


@pytest.fixture
def sample_checkpoint():
    """Sample checkpoint for testing."""
    return SessionCheckpoint(
        session_id=1,
        checkpoint_name="test-checkpoint",
        created_at=datetime.now(),
        work_items_snapshot=[
            {
                "id": 116,
                "name": "Claude Integration",
                "type": "feature",
                "status": "active",
                "phase": "I1_implementation"
            }
        ],
        tasks_snapshot=[
            {
                "id": 622,
                "objective": "Create checkpointing",
                "type": "implementation",
                "status": "active"
            }
        ],
        context_snapshot={
            "session_id": 1,
            "tool_name": "claude-code",
            "captured_at": datetime.now().isoformat()
        },
        session_notes="Test checkpoint",
        created_by="test-user",
        restore_count=0,
        size_bytes=1024
    )


@pytest.fixture
def checkpoint_data():
    """Sample checkpoint data for database operations."""
    return {
        "session_id": 1,
        "checkpoint_name": "test-checkpoint",
        "work_items_snapshot": [{"id": 116, "name": "Test"}],
        "tasks_snapshot": [{"id": 622, "objective": "Test"}],
        "context_snapshot": {"test": "data"},
        "session_notes": "Test notes",
        "created_by": "test-user",
        "restore_count": 0,
        "size_bytes": 100
    }
