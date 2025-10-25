"""
Fixtures for document content storage tests.

Provides database service, entities, and helper fixtures for testing
document content storage, sync, and search functionality.
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
    service = DatabaseService(str(temp_db_path.parent))
    # Initialize database schema
    service.initialize()
    yield service
    # Cleanup connections
    service.close_all()


@pytest.fixture
def project(db_service):
    """Create a test project."""
    proj = Project(
        name="Test Project",
        description="Test project for document content testing"
    )
    return project_methods.create_project(db_service, proj)


@pytest.fixture
def work_item(db_service, project):
    """Create a test work item."""
    wi = WorkItem(
        project_id=project.id,
        title="Test Work Item",
        description="Test work item for document content testing",
        work_item_type=WorkItemType.FEATURE,
        status=WorkItemStatus.PROPOSED
    )
    return wi_methods.create_work_item(db_service, wi)


@pytest.fixture
def task(db_service, work_item):
    """Create a test task."""
    t = Task(
        work_item_id=work_item.id,
        title="Test Task",
        description="Test task for document content testing",
        status=TaskStatus.PROPOSED
    )
    return task_methods.create_task(db_service, t)


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for file operations."""
    return tmp_path_factory.mktemp("docs")


@pytest.fixture
def cli_runner():
    """Create Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def benchmark():
    """
    Placeholder benchmark fixture for performance tests.

    In production, install pytest-benchmark:
    pip install pytest-benchmark
    """
    class MockBenchmark:
        def __call__(self, func):
            return func()

    return MockBenchmark()
