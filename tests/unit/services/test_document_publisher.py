"""
Tests for Document Publishing Workflow Service

Tests all document lifecycle transitions, file operations, and audit logging.

Pattern: Arrange-Act-Assert (AAA)
Coverage Target: >90%
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from agentpm.core.services.document_publisher import (
    DocumentPublisher,
    PublishResult,
    SyncResult,
    ValidationError,
    PublishError
)
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.document_reference import DocumentReference
from agentpm.core.database.enums import (
    EntityType,
    DocumentType,
    DocumentFormat,
    DocumentLifecycle,
    DocumentVisibility,
    StorageMode,
    SyncStatus
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory structure"""
    # Create .agentpm/docs structure
    private_docs = tmp_path / ".agentpm" / "docs" / "guides" / "user_guide"
    private_docs.mkdir(parents=True, exist_ok=True)

    # Create docs structure
    public_docs = tmp_path / "docs" / "guides" / "user_guide"
    public_docs.mkdir(parents=True, exist_ok=True)

    # Change to temp directory for tests
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Restore original directory
    os.chdir(original_cwd)


@pytest.fixture
def db(tmp_path):
    """Create test database"""
    db_path = tmp_path / "test.db"
    service = DatabaseService(db_path)
    return service


@pytest.fixture
def publisher(db):
    """Create DocumentPublisher instance"""
    return DocumentPublisher(db)


@pytest.fixture
def sample_document(db) -> DocumentReference:
    """Create sample document for testing"""
    from agentpm.core.database.methods import document_references as doc_methods

    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=164,
        category="guides",
        document_type=DocumentType.USER_GUIDE,
        filename="test-guide.md",
        file_path="docs/guides/user_guide/test-guide.md",
        title="Test User Guide",
        description="Test document for publishing workflow",
        format=DocumentFormat.MARKDOWN,
        content="# Test Guide\n\nThis is test content.",
        storage_mode=StorageMode.HYBRID,
        sync_status=SyncStatus.SYNCED,
        created_by="test-user"
    )

    # Add publishing workflow fields
    doc.lifecycle_stage = DocumentLifecycle.DRAFT.value
    doc.visibility = DocumentVisibility.PUBLIC.value
    doc.review_status = None
    doc.reviewer_id = None

    created = doc_methods.create_document_reference(db, doc)
    return created


# =============================================================================
# State Transition Tests
# =============================================================================

def test_submit_review_transitions_correctly(publisher, sample_document):
    """Test submit review changes state from DRAFT to REVIEW"""
    # Arrange
    doc_id = sample_document.id

    # Act
    success = publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

    # Assert
    assert success

    # Verify state changed
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.REVIEW.value
    assert doc.review_status == "pending"
    assert doc.reviewer_id == "reviewer@test.com"
    assert doc.reviewer_assigned_at is not None


def test_submit_review_fails_if_not_draft(publisher, sample_document):
    """Test submit review fails if document not in DRAFT state"""
    # Arrange
    doc_id = sample_document.id
    sample_document.lifecycle_stage = DocumentLifecycle.APPROVED.value

    from agentpm.core.database.methods import document_references as doc_methods
    doc_methods.update_document_reference(publisher.db, sample_document)

    # Act & Assert
    with pytest.raises(ValidationError, match="must be in DRAFT state"):
        publisher.submit_review(doc_id)


def test_approve_transitions_to_approved(publisher, sample_document):
    """Test approve changes state from REVIEW to APPROVED"""
    # Arrange
    doc_id = sample_document.id
    reviewer_id = "reviewer@test.com"

    # First submit for review
    publisher.submit_review(doc_id, reviewer_id=reviewer_id)

    # Act
    success = publisher.approve(doc_id, reviewer_id=reviewer_id, comment="LGTM")

    # Assert
    assert success

    # Verify state changed
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value
    assert doc.review_status == "approved"
    assert doc.review_comment == "LGTM"
    assert doc.review_completed_at is not None


def test_reject_reverts_to_draft(publisher, sample_document):
    """Test reject changes state to REJECTED then auto-reverts to DRAFT"""
    # Arrange
    doc_id = sample_document.id
    reviewer_id = "reviewer@test.com"
    reason = "Examples need updating"

    # First submit for review
    publisher.submit_review(doc_id, reviewer_id=reviewer_id)

    # Act
    success = publisher.reject(doc_id, reviewer_id=reviewer_id, reason=reason)

    # Assert
    assert success

    # Verify state changed back to DRAFT
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.DRAFT.value  # Auto-reverted
    assert doc.review_status == "rejected"
    assert doc.review_comment == reason


def test_reject_requires_reason(publisher, sample_document):
    """Test reject fails without reason"""
    # Arrange
    doc_id = sample_document.id
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

    # Act & Assert
    with pytest.raises(ValidationError, match="Rejection reason is required"):
        publisher.reject(doc_id, reviewer_id="reviewer@test.com", reason="")


# =============================================================================
# Publish/Unpublish Tests
# =============================================================================

def test_publish_approved_document(publisher, sample_document, temp_project_dir):
    """Test publishing approved document copies file to public location"""
    # Arrange
    doc_id = sample_document.id

    # Transition to approved
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Ensure source file exists
    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    # Act
    result = publisher.publish(doc_id, actor="test-user", trigger="manual")

    # Assert
    assert result.success
    assert result.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
    assert result.destination_path is not None

    # Verify file copied
    dest_path = Path(result.destination_path)
    assert dest_path.exists()
    assert dest_path.read_text() == sample_document.content

    # Verify document updated
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
    assert doc.published_path == result.destination_path
    assert doc.published_date is not None


def test_cannot_publish_draft_document(publisher, sample_document):
    """Test cannot publish document that's not approved"""
    # Arrange
    doc_id = sample_document.id
    # Document is in DRAFT state

    # Act & Assert
    with pytest.raises(ValidationError, match="must be APPROVED to publish"):
        publisher.publish(doc_id)


def test_cannot_publish_private_document(publisher, sample_document):
    """Test cannot publish document with PRIVATE visibility"""
    # Arrange
    doc_id = sample_document.id
    sample_document.visibility = DocumentVisibility.PRIVATE.value

    from agentpm.core.database.methods import document_references as doc_methods
    doc_methods.update_document_reference(publisher.db, sample_document)

    # Transition to approved
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Act & Assert
    with pytest.raises(ValidationError, match="Only PUBLIC documents can be published"):
        publisher.publish(doc_id)


def test_unpublish_removes_public_copy(publisher, sample_document, temp_project_dir):
    """Test unpublish removes file from docs/ but preserves source"""
    # Arrange
    doc_id = sample_document.id

    # Publish document first
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Ensure source exists
    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    result = publisher.publish(doc_id)
    assert result.success

    dest_path = Path(result.destination_path)
    assert dest_path.exists()

    # Act
    success = publisher.unpublish(doc_id, reason="Found error")

    # Assert
    assert success
    assert not dest_path.exists()  # Public file removed
    assert source.exists()  # Source preserved

    # Verify document reverted to approved
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value
    assert doc.unpublished_date is not None


# =============================================================================
# Archive Tests
# =============================================================================

def test_archive_document(publisher, sample_document):
    """Test archiving document"""
    # Arrange
    doc_id = sample_document.id

    # Act
    success = publisher.archive(doc_id, remove_public=False)

    # Assert
    assert success

    # Verify state changed
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.ARCHIVED.value


def test_archive_unpublishes_if_published(publisher, sample_document, temp_project_dir):
    """Test archive removes public copy if document is published"""
    # Arrange
    doc_id = sample_document.id

    # Publish document
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    result = publisher.publish(doc_id)
    dest_path = Path(result.destination_path)
    assert dest_path.exists()

    # Act
    success = publisher.archive(doc_id, remove_public=True)

    # Assert
    assert success
    assert not dest_path.exists()  # Public file removed


# =============================================================================
# Sync Tests
# =============================================================================

def test_sync_detects_missing_destination(publisher, sample_document, temp_project_dir):
    """Test sync detects missing public files and re-publishes"""
    # Arrange
    doc_id = sample_document.id

    # Publish document
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    result = publisher.publish(doc_id)
    dest_path = Path(result.destination_path)

    # Delete public file
    dest_path.unlink()

    # Act
    sync_result = publisher.sync_all(dry_run=False)

    # Assert
    assert len(sync_result.stats["missing_dest"]) == 1
    assert dest_path.exists()  # Re-created


def test_sync_dry_run_does_not_modify(publisher, sample_document, temp_project_dir):
    """Test sync dry run reports issues without making changes"""
    # Arrange
    doc_id = sample_document.id

    # Publish document
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    result = publisher.publish(doc_id)
    dest_path = Path(result.destination_path)

    # Delete public file
    dest_path.unlink()

    # Act
    sync_result = publisher.sync_all(dry_run=True)

    # Assert
    assert len(sync_result.stats["missing_dest"]) == 1
    assert not dest_path.exists()  # NOT re-created
    assert sync_result.dry_run is True


# =============================================================================
# Auto-Publish Tests
# =============================================================================

def test_user_guide_auto_publishes_on_approval(publisher, sample_document, temp_project_dir):
    """Test user guides auto-publish when approved"""
    # Arrange
    doc_id = sample_document.id
    # sample_document is already a user_guide with PUBLIC visibility

    # Ensure source exists
    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    # Submit and approve
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

    # Act
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Assert - should auto-publish
    from agentpm.core.database.methods import document_references as doc_methods
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
    assert doc.published_path is not None


def test_private_documents_never_auto_publish(publisher, sample_document):
    """Test private documents never auto-publish"""
    # Arrange
    doc_id = sample_document.id
    sample_document.visibility = DocumentVisibility.PRIVATE.value

    from agentpm.core.database.methods import document_references as doc_methods
    doc_methods.update_document_reference(publisher.db, sample_document)

    # Submit and approve
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

    # Act
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Assert - should NOT auto-publish
    doc = doc_methods.get_document_reference(publisher.db, doc_id)
    assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value  # Not published
    assert doc.published_path is None


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

def test_publish_creates_destination_directory(publisher, sample_document, temp_project_dir):
    """Test publish creates destination directory if it doesn't exist"""
    # Arrange
    doc_id = sample_document.id

    # Transition to approved
    publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
    publisher.approve(doc_id, reviewer_id="reviewer@test.com")

    # Ensure source exists
    source = Path(sample_document.computed_path)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(sample_document.content)

    # Remove destination directory
    dest_dir = Path("docs/guides/user_guide")
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Act
    result = publisher.publish(doc_id)

    # Assert
    assert result.success
    assert Path(result.destination_path).exists()


def test_document_not_found_raises_error(publisher):
    """Test operations on non-existent document raise ValidationError"""
    # Act & Assert
    with pytest.raises(ValidationError, match="Document .* not found"):
        publisher.submit_review(99999)


def test_approve_validates_reviewer_authorization(publisher, sample_document):
    """Test approve validates reviewer matches assigned reviewer"""
    # Arrange
    doc_id = sample_document.id
    publisher.submit_review(doc_id, reviewer_id="reviewer1@test.com")

    # Act & Assert
    with pytest.raises(ValidationError, match="not authorized"):
        publisher.approve(doc_id, reviewer_id="reviewer2@test.com")


# =============================================================================
# Helper Method Tests
# =============================================================================

def test_calculate_file_hash(publisher, temp_project_dir):
    """Test file hash calculation"""
    # Arrange
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("Hello World")

    # Act
    hash1 = publisher._calculate_file_hash(test_file)
    hash2 = publisher._calculate_file_hash(test_file)

    # Assert
    assert hash1 == hash2  # Same content = same hash
    assert len(hash1) == 64  # SHA256 hex digest length


def test_should_auto_publish_logic(publisher, sample_document):
    """Test auto-publish rule evaluation"""
    # Arrange - user_guide with PUBLIC visibility
    doc = sample_document
    doc.document_type = DocumentType.USER_GUIDE
    doc.visibility = DocumentVisibility.PUBLIC.value

    # Act
    should_publish = publisher._should_auto_publish(doc)

    # Assert
    assert should_publish is True


def test_should_not_auto_publish_internal_doc(publisher, sample_document):
    """Test internal documents don't auto-publish"""
    # Arrange
    doc = sample_document
    doc.document_type = DocumentType.DESIGN_DOC
    doc.visibility = DocumentVisibility.INTERNAL.value

    # Act
    should_publish = publisher._should_auto_publish(doc)

    # Assert
    assert should_publish is False
