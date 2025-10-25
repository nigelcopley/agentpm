"""
Fixtures for document_references methods unit tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from agentpm.core.database import DatabaseService
from agentpm.core.database.models import WorkItem, Task, Project
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.enums import WorkItemType, WorkItemStatus, TaskStatus


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
    # DatabaseService auto-initializes schema in __init__
    service = DatabaseService(str(temp_db_path))
    yield service
    # No explicit cleanup needed - connections are context-managed


@pytest.fixture
def project(db_service, temp_db_path):
    """Create a test project."""
    proj = Project(
        name="Test Project",
        description="Test project for document testing",
        path=str(temp_db_path.parent)  # Use temp directory as project path
    )
    return project_methods.create_project(db_service, proj)


@pytest.fixture
def work_item(db_service, project):
    """Create a test work item."""
    wi = WorkItem(
        project_id=project.id,
        name="Test Work Item",
        description="Test work item for document testing",
        work_item_type=WorkItemType.FEATURE,
        status=WorkItemStatus.DRAFT  # Updated to 6-state system
    )
    return wi_methods.create_work_item(db_service, wi)


@pytest.fixture
def task(db_service, work_item):
    """Create a test task."""
    t = Task(
        work_item_id=work_item.id,
        title="Test Task",
        description="Test task for document testing",
        status=TaskStatus.DRAFT  # Updated to 6-state system
    )
    return task_methods.create_task(db_service, t)
