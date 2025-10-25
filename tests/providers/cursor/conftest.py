"""
Fixtures for Cursor provider tests.

Provides isolated test database, mock Cursor projects, sample configurations,
and test data for comprehensive testing.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from agentpm.core.database import DatabaseService
from agentpm.core.database.models import Project, WorkItem
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.enums import WorkItemType, WorkItemStatus
from agentpm.core.database.models.provider import (
    CursorConfig,
    ProviderInstallation,
    CursorMemory,
    ProviderType,
    InstallationStatus,
    Guardrails,
    AllowlistEntry,
    SafetyLevel,
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
    # Database schema is initialized automatically on creation
    service = DatabaseService(str(temp_db_path))
    yield service
    # No explicit cleanup needed - connections auto-close via context managers


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for Cursor installation."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_cursor_project(temp_project_dir):
    """
    Create a mock Cursor project directory structure.

    Creates:
    - .cursor/ directory
    - .cursor/rules/
    - .cursor/memories/
    - .cursor/modes/
    """
    cursor_dir = temp_project_dir / ".cursor"
    cursor_dir.mkdir(parents=True)
    (cursor_dir / "rules").mkdir()
    (cursor_dir / "memories").mkdir()
    (cursor_dir / "modes").mkdir()

    return temp_project_dir


@pytest.fixture
def project(db_service, temp_project_dir):
    """Create a test project in database."""
    proj = Project(
        name="Test Cursor Project",
        description="Test project for Cursor provider testing",
        path=str(temp_project_dir),  # Fixed: use 'path' not 'root_path'
    )
    return project_methods.create_project(db_service, proj)


@pytest.fixture
def work_item(db_service, project):
    """Create a test work item."""
    wi = WorkItem(
        project_id=project.id,
        title="Test Feature",
        description="Test feature for Cursor testing",
        work_item_type=WorkItemType.FEATURE,
        status=WorkItemStatus.PROPOSED,
    )
    return wi_methods.create_work_item(db_service, wi)


@pytest.fixture
def sample_config(temp_project_dir):
    """
    Create a sample CursorConfig for testing.

    Returns complete configuration with all features enabled.
    """
    return CursorConfig(
        project_name="Test Project",
        project_path=str(temp_project_dir),
        tech_stack=["Python", "SQLite", "pytest"],
        rules_enabled=True,
        rules_to_install=[
            "aipm-master",
            "python-implementation",
            "testing-standards",
        ],
        memory_sync_enabled=True,
        memory_sync_interval_hours=1,
        modes_enabled=True,
        modes_to_install=[
            "aipm-discovery",
            "aipm-implementation",
        ],
        guardrails_enabled=True,
        indexing_enabled=True,
        exclude_patterns=[
            ".aipm/",
            "__pycache__/",
            "*.pyc",
        ],
        hooks_enabled=False,
    )


@pytest.fixture
def minimal_config(temp_project_dir):
    """
    Create a minimal CursorConfig for testing.

    Only essential fields, most features disabled.
    """
    return CursorConfig(
        project_name="Minimal Project",
        project_path=str(temp_project_dir),
        tech_stack=[],
        rules_enabled=True,
        memory_sync_enabled=False,
        modes_enabled=False,
        guardrails_enabled=False,
        indexing_enabled=False,
    )


@pytest.fixture
def sample_installation(project, temp_project_dir):
    """Create a sample ProviderInstallation model."""
    return ProviderInstallation(
        project_id=project.id,
        provider_type=ProviderType.CURSOR,
        provider_version="1.0.0",
        install_path=str(temp_project_dir / ".cursor"),
        status=InstallationStatus.INSTALLED,
        config={
            "project_name": "Test Project",
            "rules_enabled": True,
        },
        installed_files=[
            "rules/aipm-master.mdc",
            "rules/python-implementation.mdc",
            ".cursorignore",
        ],
        file_hashes={
            "rules/aipm-master.mdc": "abc123",
            "rules/python-implementation.mdc": "def456",
            ".cursorignore": "ghi789",
        },
        installed_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_memory(project):
    """Create a sample CursorMemory model."""
    return CursorMemory(
        project_id=project.id,
        name="test-learning",
        description="Test learning memory",
        category="testing",
        content="# Test Learning\n\nThis is a test learning.",
        tags=["test", "learning"],
        file_path="test-learning.md",
        file_hash="test123",
        source_learning_id=1,
        last_synced_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_guardrails():
    """Create sample Guardrails configuration."""
    return Guardrails(
        allowlists={
            "apm_commands": [
                AllowlistEntry(
                    pattern="^apm status$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Project dashboard",
                ),
                AllowlistEntry(
                    pattern="^apm work-item list$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="List work items",
                ),
            ],
            "testing": [
                AllowlistEntry(
                    pattern="^pytest tests/.*$",
                    safety=SafetyLevel.SAFE_CONFIRM,
                    auto_run=False,
                    description="Run tests",
                ),
            ],
        },
        require_confirmation_by_default=True,
        allow_destructive_operations=False,
        max_auto_runs_per_session=10,
    )


@pytest.fixture
def sample_rules(temp_project_dir):
    """
    Create sample rule templates for testing.

    Returns dict of rule_id -> rule content.
    """
    rules = {
        "aipm-master": """# AIPM Master Rule

Project: {{ project_name }}
Path: {{ project_path }}

This is the master rule for AIPM project management.
""",
        "python-implementation": """# Python Implementation Standards

Follow Python best practices:
- PEP 8 style guide
- Type hints
- Docstrings
""",
        "testing-standards": """# Testing Standards

All code must have:
- Unit tests (>90% coverage)
- Integration tests
- AAA pattern
""",
    }

    return rules


@pytest.fixture
def aipm_root():
    """Get AIPM root directory for accessing real rule templates."""
    return Path(__file__).parents[3]


@pytest.fixture
def mock_database_with_learnings(db_service, project):
    """
    Create a database with sample learnings for memory sync testing.

    Creates 3 learnings that can be synced to Cursor.
    """
    # Create sample learnings directly in database using transaction context
    with db_service.transaction() as conn:
        for i in range(3):
            conn.execute(
                """
                INSERT INTO learnings (
                    project_id, title, content, type, confidence,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    f"Learning {i+1}",
                    f"# Learning {i+1}\n\nThis is test learning {i+1}.",
                    "technical",
                    0.8,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
        # Auto-commits on context exit

    return db_service
