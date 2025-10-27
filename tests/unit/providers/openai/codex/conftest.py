"""
Fixtures for Codex generator tests.

Provides isolated test database, temporary directories, and sample data
for CodexGenerator testing.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from agentpm.core.database import DatabaseService


@pytest.fixture
def temp_db_path():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    yield db_path
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def db_service(temp_db_path):
    """Create a DatabaseService instance with test database."""
    # Database schema is initialized automatically on creation
    service = DatabaseService(str(temp_db_path))
    yield service
    # No explicit cleanup needed - connections auto-close via context managers
