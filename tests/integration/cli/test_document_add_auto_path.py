"""
Integration tests for document add command with auto-path generation.

Tests the new auto-path generation features added in WI-164 Task #1082:
- Auto-generated paths when --file-path omitted
- Path correction and file moves
- Visibility policy integration
- Database-first workflow with content
- File-first workflow with placeholders
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from agentpm.cli.commands.document.add import add
from agentpm.core.database.service import DatabaseService


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_db(tmp_path):
    """Create test database with migrations applied."""
    db_path = tmp_path / ".agentpm" / "data" / "test.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # DatabaseService automatically initializes schema in __init__
    db = DatabaseService(str(db_path))

    # Run migrations to ensure visibility system is available
    from agentpm.core.database.migrations.manager import MigrationManager
    migration_manager = MigrationManager(db)
    migration_manager.run_all_pending()

    yield db

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_project(test_db, tmp_path):
    """Create test project."""
    from agentpm.core.database.adapters.project_adapter import ProjectAdapter
    from agentpm.core.database.models.project import Project

    project = Project(
        name="Test Project",
        path=str(tmp_path),
        description="Test project for integration tests"
    )
    created = ProjectAdapter.create(test_db, project)
    return created


@pytest.fixture
def test_work_item(test_db, test_project):
    """Create test work item."""
    from agentpm.core.database.adapters.work_item_adapter import WorkItemAdapter
    from agentpm.core.database.models.work_item import WorkItem
    from agentpm.core.database.enums import WorkItemType, WorkItemStatus

    work_item = WorkItem(
        name="Test Work Item",
        project_id=test_project.id,
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.READY  # Changed from ACCEPTED to READY (6-state model)
    )
    created = WorkItemAdapter.create(test_db, work_item)
    return created


def test_document_add_without_file_path(runner, test_db, test_work_item, tmp_path):
    """Test auto-path generation when --file-path omitted."""
    # Change to temp directory for test
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        # Create context object
        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'Getting Started',
            '--content', '# Getting Started\n\nWelcome!',
            '--no-validate-entity'
        ], obj=ctx_obj)

        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check output contains expected path
        assert "guides/user_guide/getting-started.md" in result.output

        # Check file was created
        expected_path = td_path / ".agentpm/docs/guides/user_guide/getting-started.md"
        assert expected_path.exists(), f"File not created at {expected_path}"

        # Check file content
        content = expected_path.read_text()
        assert "# Getting Started" in content
        assert "Welcome!" in content


def test_document_add_corrects_wrong_path(runner, test_db, test_work_item, tmp_path):
    """Test automatic path correction and file move."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        # Create file at wrong location
        wrong_path = td_path / "docs/wrong.md"
        wrong_path.parent.mkdir(parents=True, exist_ok=True)
        wrong_path.write_text("# Content")

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--file-path', 'docs/wrong.md',
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'My Guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check output mentions path correction or file move
        assert "Path auto-generated" in result.output or "Moving file" in result.output

        # Check old file is gone
        assert not wrong_path.exists(), "Old file should be moved"

        # Check new file exists
        expected_path = td_path / ".agentpm/docs/guides/user_guide/my-guide.md"
        assert expected_path.exists(), f"File not at expected location: {expected_path}"


def test_document_add_private_to_agentpm_docs(runner, test_db, test_work_item, tmp_path):
    """Test private documents go to .agentpm/docs/."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'planning',
            '--type', 'idea',
            '--title', 'New Feature Idea',
            '--content', '# Idea\n\nDetails...',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check output contains .agentpm/docs path
        assert ".agentpm/docs/planning/idea/" in result.output

        # Check file exists in private location
        expected_path = td_path / ".agentpm/docs/planning/idea/new-feature-idea.md"
        assert expected_path.exists(), f"File not created at {expected_path}"


def test_document_add_public_to_docs(runner, test_db, test_work_item, tmp_path):
    """Test public documents go to docs/ when published."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        # User guides are public and auto-publish
        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'Installation Guide',
            '--content', '# Installation\n\nSteps...',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check visibility metadata in output
        assert "Visibility: public" in result.output or "Visibility: private" in result.output

        # Note: Document starts as draft, so goes to .agentpm/docs
        # Will move to docs/ when published
        draft_path = td_path / ".agentpm/docs/guides/user_guide/installation-guide.md"
        assert draft_path.exists(), f"Draft file not created at {draft_path}"


def test_document_add_with_content_creates_file(runner, test_db, test_work_item, tmp_path):
    """Test database-first workflow creates file from content."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        content = "# Architecture Overview\n\n## Components\n\n- Component A\n- Component B"

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'architecture',
            '--type', 'design_doc',
            '--title', 'System Architecture',
            '--content', content,
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check file was created
        expected_path = td_path / ".agentpm/docs/architecture/design_doc/system-architecture.md"
        assert expected_path.exists(), f"File not created at {expected_path}"

        # Check content matches
        file_content = expected_path.read_text()
        assert "# Architecture Overview" in file_content
        assert "Component A" in file_content


def test_document_add_without_content_creates_placeholder(runner, test_db, test_work_item, tmp_path):
    """Test file-first workflow creates placeholder when no file exists."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'planning',
            '--type', 'requirements',
            '--title', 'API Requirements',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check placeholder file was created
        expected_path = td_path / ".agentpm/docs/planning/requirements/api-requirements.md"
        assert expected_path.exists(), f"Placeholder file not created at {expected_path}"

        # Check placeholder content
        content = expected_path.read_text()
        assert "# API Requirements" in content
        assert "<!-- Add content here -->" in content


def test_document_add_shows_visibility_info(runner, test_db, test_work_item, tmp_path):
    """Test output shows visibility and lifecycle information."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'User Guide',
            '--content', '# Guide\n\nContent...',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check visibility information in output
        assert "Visibility:" in result.output
        assert "Lifecycle: draft" in result.output

        # Check auto-publish info
        assert "Auto-publish:" in result.output

        # Check review requirement info
        assert "Review required:" in result.output or "review" in result.output.lower()


def test_document_add_requires_category_and_type(runner, test_db, test_work_item, tmp_path):
    """Test command requires category and type for auto-path generation."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        # Missing category
        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--type', 'user_guide',
            '--title', 'Test',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code != 0
        assert "--category is required" in result.output

        # Missing type
        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--title', 'Test',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code != 0
        assert "--type is required" in result.output


def test_document_add_requires_title(runner, test_db, test_work_item, tmp_path):
    """Test command requires title for auto-path generation."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code != 0
        assert "--title is required" in result.output


def test_document_add_slugifies_title(runner, test_db, test_work_item, tmp_path):
    """Test title is properly slugified in path."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'OAuth 2.0: Implementation Guide (v2)',
            '--content', '# Guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check slugified path
        expected_path = td_path / ".agentpm/docs/guides/user_guide/oauth-2-0-implementation-guide-v2.md"
        assert expected_path.exists(), f"File not created with slugified name: {expected_path}"


def test_document_add_stores_visibility_metadata(runner, test_db, test_work_item, tmp_path):
    """Test visibility metadata is stored in database."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'planning',
            '--type', 'requirements',
            '--title', 'Test Requirements',
            '--content', '# Requirements',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Query database to verify metadata
        from agentpm.core.database.adapters.document_reference_adapter import DocumentReferenceAdapter

        # Get all documents for this work item
        docs = DocumentReferenceAdapter.list_by_entity(
            test_db,
            entity_type='work_item',
            entity_id=test_work_item.id
        )

        assert len(docs) > 0, "Document not found in database"

        doc = docs[0]
        assert doc.visibility is not None, "Visibility not set"
        assert doc.lifecycle_stage == 'draft', f"Lifecycle should be draft, got {doc.lifecycle_stage}"
        assert doc.auto_publish is not None, "Auto-publish flag not set"


def test_document_add_handles_conflict_resolution(runner, test_db, test_work_item, tmp_path):
    """Test conflict resolution adds numeric suffix."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        # Create first document
        result1 = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'Guide',
            '--content', '# First Guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result1.exit_code == 0, f"First command failed: {result1.output}"

        # Create second document with same title (different work item)
        # First create another work item
        from agentpm.core.database.adapters.work_item_adapter import WorkItemAdapter
        from agentpm.core.database.models.work_item import WorkItem
        from agentpm.core.database.enums import WorkItemType, WorkItemStatus
        from agentpm.core.database.adapters.project_adapter import ProjectAdapter
        from agentpm.core.database.models.project import Project

        # Get the project for this work item
        project = ProjectAdapter.list(test_db)[0]  # Use first project

        work_item2 = WorkItem(
            name="Test Work Item 2",
            project_id=project.id,
            type=WorkItemType.FEATURE,
            status=WorkItemStatus.READY
        )
        created2 = WorkItemAdapter.create(test_db, work_item2)

        result2 = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(created2.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'Guide',  # Same title
            '--content', '# Second Guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result2.exit_code == 0, f"Second command failed: {result2.output}"

        # Check both files exist with different names
        path1 = td_path / ".agentpm/docs/guides/user_guide/guide.md"
        path2 = td_path / ".agentpm/docs/guides/user_guide/guide-2.md"

        assert path1.exists(), "First file should exist"
        assert path2.exists(), "Second file should have -2 suffix"

        # Verify content is different
        content1 = path1.read_text()
        content2 = path2.read_text()
        assert "First Guide" in content1
        assert "Second Guide" in content2


def test_document_add_next_steps_shown(runner, test_db, test_work_item, tmp_path):
    """Test command shows appropriate next steps."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        td_path = Path(td)

        ctx_obj = {
            'console': None,
            'project_root': td_path,
            'db_service': test_db
        }

        result = runner.invoke(add, [
            '--entity-type', 'work-item',
            '--entity-id', str(test_work_item.id),
            '--category', 'guides',
            '--type', 'user_guide',
            '--title', 'Test Guide',
            '--content', '# Guide',
            '--no-validate-entity'
        ], obj=ctx_obj)

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check next steps section
        assert "Next steps:" in result.output or "next steps" in result.output.lower()
        assert "apm document show" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
