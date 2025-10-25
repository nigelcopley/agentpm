"""
Fixtures for Claude integration tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from agentpm.core.database import DatabaseService
from agentpm.core.database.models import WorkItem, Task, Project
try:
    from agentpm.core.database.models.session import Session, SessionTool, SessionType
except ImportError:
    # Fallback if session models not available
    Session = None
    SessionTool = None
    SessionType = None
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import sessions as session_methods
from agentpm.core.database.enums import (
    WorkItemType,
    WorkItemStatus,
    Phase,
    TaskStatus,
    TaskType,
)


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
        description="Test project for Claude integration testing",
        business_domain="Software Development",
    )
    return project_methods.create_project(db_service, proj)


@pytest.fixture
def work_item(db_service, project):
    """Create a test work item."""
    wi = WorkItem(
        name="Test Feature",
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.ACTIVE,
        phase=Phase.I1_IMPLEMENTATION,
        project_id=project.id,
        business_context="Test business context for feature",
        acceptance_criteria=["AC1: Feature works", "AC2: Tests pass", "AC3: Docs updated"],
        estimated_hours=8.0,
    )
    return wi_methods.create_work_item(db_service, wi)


@pytest.fixture
def task(db_service, work_item):
    """Create a test task."""
    t = Task(
        work_item_id=work_item.id,
        objective="Implement test feature",
        type=TaskType.IMPLEMENTATION,
        status=TaskStatus.ACTIVE,
        acceptance_criteria=["Implementation complete", "Tests added"],
        effort_estimate=4.0,
    )
    return task_methods.create_task(db_service, t)


@pytest.fixture
def session(db_service, project):
    """Create a test session."""
    if Session is None:
        pytest.skip("Session model not available")

    sess = Session(
        session_id="test-session-123",
        project_id=project.id,
        tool=SessionTool.CLAUDE_CODE,
        tool_version="1.5.0",
        session_type=SessionType.DEVELOPMENT,
        started_at=datetime.now().isoformat(),
    )
    created = session_methods.create_session(db_service, sess)
    session_methods.set_current_session(db_service, created.session_id)
    return created
