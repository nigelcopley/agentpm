"""
Comprehensive Integration Tests for Document Publisher Service (Task #1087)

Tests verify end-to-end publishing workflow with real database and file system operations.
Validates full lifecycle: draft → review → approved → published → archived.

Coverage target: ≥90% (document_publisher.py currently at 18.15%)

Test Organization:
- Suite 1: End-to-End Publish Workflow
- Suite 2: End-to-End Unpublish Workflow
- Suite 3: List Unpublished Documents Query
- Suite 4: File System Operations
- Suite 5: Database Updates
- Suite 6: Error Handling & Edge Cases
- Suite 7: Audit Trail Verification
- Suite 8: Transaction Rollback on Errors
- Suite 9: Sync Operations
- Suite 10: Auto-Publish Rules

All tests follow AAA pattern (Arrange-Act-Assert).

Work Item: #164 - Auto-Generate Document File Paths
Task: #1087 - Integration Tests for Publishing Workflow
"""

import pytest
import sqlite3
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from agentpm.core.database.service import DatabaseService
from agentpm.core.services.document_publisher import (
    DocumentPublisher,
    PublishResult,
    SyncResult,
    ValidationError,
    PublishError
)
from agentpm.core.database.models.document_reference import DocumentReference
from agentpm.core.database.models.document_audit_log import DocumentAuditLog
from agentpm.core.database.enums import (
    EntityType,
    DocumentType,
    DocumentFormat,
    DocumentLifecycle,
    DocumentVisibility,
    StorageMode,
    SyncStatus
)
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.adapters.document_audit_adapter import DocumentAuditAdapter


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_workspace(tmp_path):
    """
    Create temporary workspace with project structure.

    Creates:
    - .agentpm/docs/  (private documents)
    - docs/           (public documents)

    Returns tmp_path as current directory.
    """
    import os

    # Create directory structure
    private_docs = tmp_path / ".agentpm" / "docs"
    private_docs.mkdir(parents=True, exist_ok=True)

    public_docs = tmp_path / "docs"
    public_docs.mkdir(parents=True, exist_ok=True)

    # Change to workspace
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Restore
    os.chdir(original_cwd)


@pytest.fixture
def db(tmp_path):
    """Create test database with schema and missing review timestamp columns"""
    db_path = tmp_path / "test.db"
    service = DatabaseService(db_path)

    # Add missing columns needed by document_publisher service
    # These should be added via a proper migration, but for testing we add them directly
    with service.transaction() as conn:
        try:
            conn.execute("ALTER TABLE document_references ADD COLUMN reviewer_assigned_at TIMESTAMP")
        except Exception:
            pass  # Column may already exist
        try:
            conn.execute("ALTER TABLE document_references ADD COLUMN review_completed_at TIMESTAMP")
        except Exception:
            pass  # Column may already exist

    return service


@pytest.fixture
def publisher(db):
    """Create DocumentPublisher instance"""
    return DocumentPublisher(db)


@pytest.fixture
def sample_doc(db, temp_workspace) -> DocumentReference:
    """
    Create sample document in DRAFT state.

    Returns document with:
    - lifecycle_stage = DRAFT
    - visibility = PUBLIC
    - content = sample markdown
    """
    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=164,
        category="guides",
        document_type=DocumentType.USER_GUIDE,
        filename="integration-test-guide.md",
        file_path="docs/guides/user_guide/integration-test-guide.md",
        title="Integration Test User Guide",
        description="Sample document for integration testing",
        format=DocumentFormat.MARKDOWN,
        content="# Integration Test Guide\n\nThis is test content for integration tests.\n\n## Features\n\n- Feature 1\n- Feature 2\n\n## Usage\n\n```python\nprint('hello world')\n```\n",
        storage_mode=StorageMode.HYBRID,
        sync_status=SyncStatus.SYNCED,
        created_by="test-user"
    )

    # Set lifecycle fields
    doc.lifecycle_stage = DocumentLifecycle.DRAFT.value
    doc.visibility = DocumentVisibility.PUBLIC.value
    doc.review_status = None
    doc.reviewer_id = None

    created = doc_methods.create_document_reference(db, doc)
    return created


# ============================================================================
# Suite 1: End-to-End Publish Workflow
# ============================================================================

class TestEndToEndPublishWorkflow:
    """Test complete publish workflow from draft to published"""

    def test_full_workflow_draft_to_published(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Document in DRAFT state with PUBLIC visibility
        WHEN: Submit review → approve → publish
        THEN: Document transitions through all states and file is published
        """
        # Arrange
        doc_id = sample_doc.id
        reviewer = "reviewer@test.com"

        # Ensure source file exists in private location (.agentpm/docs/)
        # The publisher works with documents in .agentpm/docs/ and publishes them to docs/
        source_path = Path(".agentpm") / "docs" / sample_doc.category / sample_doc.document_type.value / sample_doc.filename
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        # Act - Submit for review
        success = publisher.submit_review(doc_id, reviewer_id=reviewer)
        assert success

        # Verify REVIEW state
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.REVIEW.value
        assert doc.review_status == "pending"
        assert doc.reviewer_id == reviewer
        assert doc.reviewer_assigned_at is not None

        # Act - Approve
        success = publisher.approve(doc_id, reviewer_id=reviewer, comment="Looks good!")
        assert success

        # Verify APPROVED state
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value
        assert doc.review_status == "approved"
        assert doc.review_comment == "Looks good!"
        assert doc.review_completed_at is not None

        # Act - Publish
        result = publisher.publish(doc_id, actor="test-user", trigger="manual")

        # Assert
        assert result.success
        assert result.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
        assert result.destination_path is not None

        # Verify published file exists
        dest_path = Path(result.destination_path)
        assert dest_path.exists()
        assert dest_path.read_text(encoding='utf-8') == sample_doc.content

        # Verify database updated
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
        assert doc.published_path == str(dest_path)
        assert doc.published_date is not None

    def test_workflow_with_rejection_and_rework(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Document in REVIEW state
        WHEN: Reject → reverts to DRAFT → resubmit → approve → publish
        THEN: Document completes workflow after rejection rework
        """
        # Arrange
        doc_id = sample_doc.id
        reviewer = "reviewer@test.com"

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        # Submit for review
        publisher.submit_review(doc_id, reviewer_id=reviewer)

        # Act - Reject
        success = publisher.reject(doc_id, reviewer_id=reviewer, reason="Examples need improvement")
        assert success

        # Verify reverted to DRAFT
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.DRAFT.value
        assert doc.review_status == "rejected"
        assert doc.review_comment == "Examples need improvement"

        # Act - Resubmit after rework
        publisher.submit_review(doc_id, reviewer_id=reviewer)
        publisher.approve(doc_id, reviewer_id=reviewer, comment="Fixed!")
        result = publisher.publish(doc_id)

        # Assert - Successfully published after rework
        assert result.success
        assert result.lifecycle_stage == DocumentLifecycle.PUBLISHED.value


# ============================================================================
# Suite 2: End-to-End Unpublish Workflow
# ============================================================================

class TestEndToEndUnpublishWorkflow:
    """Test unpublish workflow and file removal"""

    def test_unpublish_removes_public_file_preserves_source(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Published document
        WHEN: Unpublish document
        THEN: Public file removed, source preserved, state reverts to APPROVED
        """
        # Arrange - Publish document first
        doc_id = sample_doc.id
        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")
        result = publisher.publish(doc_id)

        dest_path = Path(result.destination_path)
        assert dest_path.exists()
        assert source_path.exists()

        # Act - Unpublish
        success = publisher.unpublish(doc_id, reason="Found critical error")

        # Assert
        assert success
        assert not dest_path.exists()  # Public file removed
        assert source_path.exists()   # Source preserved

        # Verify state
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value
        assert doc.unpublished_date is not None

    def test_unpublish_fails_if_not_published(self, publisher, sample_doc):
        """
        GIVEN: Document not in PUBLISHED state
        WHEN: Attempt unpublish
        THEN: ValidationError raised
        """
        # Arrange - Document in DRAFT state
        doc_id = sample_doc.id

        # Act & Assert
        with pytest.raises(ValidationError, match="not published"):
            publisher.unpublish(doc_id)


# ============================================================================
# Suite 3: List Unpublished Documents Query
# ============================================================================

class TestListUnpublishedDocuments:
    """Test query for documents ready to publish"""

    def test_lists_approved_public_documents(self, publisher, db, temp_workspace):
        """
        GIVEN: Mix of documents in various states
        WHEN: Query list_unpublished_documents
        THEN: Returns only APPROVED + PUBLIC documents
        """
        # Arrange - Create documents in various states
        docs_data = [
            # Should be listed (APPROVED + PUBLIC)
            ("doc1.md", DocumentLifecycle.APPROVED, DocumentVisibility.PUBLIC),
            ("doc2.md", DocumentLifecycle.APPROVED, DocumentVisibility.PUBLIC),

            # Should NOT be listed
            ("doc3.md", DocumentLifecycle.DRAFT, DocumentVisibility.PUBLIC),
            ("doc4.md", DocumentLifecycle.PUBLISHED, DocumentVisibility.PUBLIC),
            ("doc5.md", DocumentLifecycle.APPROVED, DocumentVisibility.PRIVATE),
        ]

        for filename, lifecycle, visibility in docs_data:
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=164,
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename=filename,
                file_path=f"docs/guides/user_guide/{filename}",
                title=f"Test {filename}",
                format=DocumentFormat.MARKDOWN,
                content=f"# {filename}",
                storage_mode=StorageMode.HYBRID,
                created_by="test-user"
            )
            doc.lifecycle_stage = lifecycle.value
            doc.visibility = visibility.value
            doc_methods.create_document_reference(db, doc)

        # Act
        unpublished = publisher.list_unpublished_documents()

        # Assert
        assert len(unpublished) == 2
        filenames = {doc.filename for doc in unpublished}
        assert filenames == {"doc1.md", "doc2.md"}

    def test_empty_list_when_no_unpublished_docs(self, publisher, sample_doc):
        """
        GIVEN: No documents in APPROVED + PUBLIC state
        WHEN: Query list_unpublished_documents
        THEN: Returns empty list
        """
        # Arrange - sample_doc is in DRAFT

        # Act
        unpublished = publisher.list_unpublished_documents()

        # Assert
        assert len(unpublished) == 0


# ============================================================================
# Suite 4: File System Operations
# ============================================================================

class TestFileSystemOperations:
    """Test file copy, move, delete operations"""

    def test_publish_creates_destination_directory(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Destination directory doesn't exist
        WHEN: Publish document
        THEN: Destination directory created automatically
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Remove destination directory
        dest_dir = temp_workspace / "docs" / "guides" / "user_guide"
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        # Act
        result = publisher.publish(doc_id)

        # Assert
        assert result.success
        dest_path = Path(result.destination_path)
        assert dest_path.exists()
        assert dest_path.parent.exists()

    def test_publish_preserves_file_content(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Source file with specific content
        WHEN: Publish document
        THEN: Destination file has identical content
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)

        content = "# Test\n\nSpecial chars: é, ñ, 中文\n\nEmoji: 🚀\n"
        source_path.write_text(content, encoding='utf-8')
        sample_doc.content = content
        doc_methods.update_document_reference(publisher.db, sample_doc)

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act
        result = publisher.publish(doc_id)

        # Assert
        dest_path = Path(result.destination_path)
        dest_content = dest_path.read_text(encoding='utf-8')
        assert dest_content == content

    def test_publish_handles_missing_source_file(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Source file doesn't exist in file system
        WHEN: Publish document (syncs from database)
        THEN: Source file created from database content, then published
        """
        # Arrange
        doc_id = sample_doc.id

        # Don't create source file
        source_path = Path(sample_doc.computed_path)
        assert not source_path.exists()

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act
        result = publisher.publish(doc_id)

        # Assert
        assert result.success
        assert source_path.exists()  # Synced from database

        dest_path = Path(result.destination_path)
        assert dest_path.exists()
        assert dest_path.read_text(encoding='utf-8') == sample_doc.content


# ============================================================================
# Suite 5: Database Updates
# ============================================================================

class TestDatabaseUpdates:
    """Test database field updates during publishing"""

    def test_publish_updates_all_database_fields(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Document ready to publish
        WHEN: Publish document
        THEN: All publish-related database fields updated
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act
        result = publisher.publish(doc_id, actor="admin", trigger="manual")

        # Assert
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
        assert doc.published_path is not None
        assert doc.published_date is not None
        assert isinstance(doc.published_date, datetime)

    def test_review_assignment_updates_metadata(self, publisher, sample_doc):
        """
        GIVEN: Document in DRAFT
        WHEN: Submit review with reviewer
        THEN: Reviewer metadata updated
        """
        # Arrange
        doc_id = sample_doc.id
        reviewer = "reviewer@example.com"

        # Act
        publisher.submit_review(doc_id, reviewer_id=reviewer)

        # Assert
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.reviewer_id == reviewer
        assert doc.reviewer_assigned_at is not None
        assert doc.review_status == "pending"

    def test_approval_updates_review_completion_metadata(self, publisher, sample_doc):
        """
        GIVEN: Document in REVIEW
        WHEN: Approve document
        THEN: Review completion metadata updated
        """
        # Arrange
        doc_id = sample_doc.id
        reviewer = "reviewer@test.com"
        comment = "Excellent documentation!"

        publisher.submit_review(doc_id, reviewer_id=reviewer)

        # Act
        publisher.approve(doc_id, reviewer_id=reviewer, comment=comment)

        # Assert
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.review_status == "approved"
        assert doc.review_comment == comment
        assert doc.review_completed_at is not None


# ============================================================================
# Suite 6: Error Handling & Edge Cases
# ============================================================================

class TestErrorHandling:
    """Test error conditions and edge cases"""

    def test_publish_fails_if_not_approved(self, publisher, sample_doc):
        """
        GIVEN: Document not in APPROVED state
        WHEN: Attempt publish
        THEN: ValidationError raised
        """
        # Arrange - Document in DRAFT
        doc_id = sample_doc.id

        # Act & Assert
        with pytest.raises(ValidationError, match="must be APPROVED"):
            publisher.publish(doc_id)

    def test_publish_fails_if_not_public(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Document with PRIVATE visibility
        WHEN: Attempt publish
        THEN: ValidationError raised
        """
        # Arrange
        doc_id = sample_doc.id
        sample_doc.visibility = DocumentVisibility.PRIVATE.value
        doc_methods.update_document_reference(publisher.db, sample_doc)

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act & Assert
        with pytest.raises(ValidationError, match="Only PUBLIC documents"):
            publisher.publish(doc_id)

    def test_approve_validates_reviewer_authorization(self, publisher, sample_doc):
        """
        GIVEN: Document assigned to reviewer1
        WHEN: reviewer2 attempts approval
        THEN: ValidationError raised
        """
        # Arrange
        doc_id = sample_doc.id
        publisher.submit_review(doc_id, reviewer_id="reviewer1@test.com")

        # Act & Assert
        with pytest.raises(ValidationError, match="not authorized"):
            publisher.approve(doc_id, reviewer_id="reviewer2@test.com")

    def test_reject_requires_reason(self, publisher, sample_doc):
        """
        GIVEN: Document in REVIEW
        WHEN: Reject without reason
        THEN: ValidationError raised
        """
        # Arrange
        doc_id = sample_doc.id
        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Act & Assert
        with pytest.raises(ValidationError, match="Rejection reason is required"):
            publisher.reject(doc_id, reviewer_id="reviewer@test.com", reason="")

    def test_operations_on_nonexistent_document(self, publisher):
        """
        GIVEN: Non-existent document ID
        WHEN: Attempt any operation
        THEN: ValidationError raised
        """
        # Act & Assert
        with pytest.raises(ValidationError, match="not found"):
            publisher.submit_review(99999)

        with pytest.raises(ValidationError, match="not found"):
            publisher.approve(99999, reviewer_id="test@test.com")

        with pytest.raises(ValidationError, match="not found"):
            publisher.publish(99999)


# ============================================================================
# Suite 7: Audit Trail Verification
# ============================================================================

class TestAuditTrail:
    """Test audit log creation for all actions"""

    def test_submit_review_creates_audit_entry(self, publisher, sample_doc):
        """
        GIVEN: Document in DRAFT
        WHEN: Submit for review
        THEN: Audit entry created with correct action
        """
        # Arrange
        doc_id = sample_doc.id

        # Act
        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Assert - Query audit log
        audit_entries = DocumentAuditAdapter.list_by_document(publisher.db, doc_id)
        assert len(audit_entries) > 0

        entry = audit_entries[-1]  # Most recent
        assert entry.action == "submit_review"
        assert entry.from_state == DocumentLifecycle.DRAFT.value
        assert entry.to_state == DocumentLifecycle.REVIEW.value

    def test_approve_creates_audit_entry(self, publisher, sample_doc):
        """
        GIVEN: Document in REVIEW
        WHEN: Approve document
        THEN: Audit entry created with reviewer and comment
        """
        # Arrange
        doc_id = sample_doc.id
        reviewer = "reviewer@test.com"
        comment = "Approved"

        publisher.submit_review(doc_id, reviewer_id=reviewer)

        # Act
        publisher.approve(doc_id, reviewer_id=reviewer, comment=comment)

        # Assert
        audit_entries = DocumentAuditAdapter.list_by_document(publisher.db, doc_id)
        approve_entries = [e for e in audit_entries if e.action == "approve"]

        assert len(approve_entries) == 1
        entry = approve_entries[0]
        assert entry.actor == reviewer
        assert entry.comment == comment
        assert entry.from_state == DocumentLifecycle.REVIEW.value
        assert entry.to_state == DocumentLifecycle.APPROVED.value

    def test_publish_creates_audit_entry_with_paths(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Approved document
        WHEN: Publish document
        THEN: Audit entry includes source and destination paths
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act
        result = publisher.publish(doc_id, actor="admin", trigger="manual")

        # Assert
        audit_entries = DocumentAuditAdapter.list_by_document(publisher.db, doc_id)
        publish_entries = [e for e in audit_entries if e.action == "publish"]

        assert len(publish_entries) == 1
        entry = publish_entries[0]
        assert entry.details is not None
        assert "source" in entry.details
        assert "destination" in entry.details
        assert "trigger" in entry.details
        assert entry.details["trigger"] == "manual"

    def test_reject_creates_two_audit_entries(self, publisher, sample_doc):
        """
        GIVEN: Document in REVIEW
        WHEN: Reject document
        THEN: Two audit entries created (reject + auto-revert)
        """
        # Arrange
        doc_id = sample_doc.id
        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Act
        publisher.reject(doc_id, reviewer_id="reviewer@test.com", reason="Needs work")

        # Assert
        audit_entries = DocumentAuditAdapter.list_by_document(publisher.db, doc_id)

        # Should have: submit_review, reject, auto_revert_to_draft
        reject_entry = next(e for e in audit_entries if e.action == "reject")
        revert_entry = next(e for e in audit_entries if e.action == "auto_revert_to_draft")

        assert reject_entry.to_state == DocumentLifecycle.REJECTED.value
        assert revert_entry.from_state == DocumentLifecycle.REJECTED.value
        assert revert_entry.to_state == DocumentLifecycle.DRAFT.value


# ============================================================================
# Suite 8: Transaction Rollback on Errors
# ============================================================================

class TestTransactionRollback:
    """Test database transaction handling on errors"""

    def test_publish_rollback_on_file_copy_error(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Approved document
        WHEN: Publish fails during file copy
        THEN: Database not updated, returns error result
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Act - Mock shutil.copy2 to raise error
        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            result = publisher.publish(doc_id)

        # Assert
        assert not result.success
        assert result.error is not None
        assert "Failed to copy file" in result.error

        # Verify database NOT updated
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value  # Still approved
        assert doc.published_path is None
        assert doc.published_date is None

    def test_state_consistent_after_partial_failure(self, publisher, sample_doc):
        """
        GIVEN: Document in valid state
        WHEN: Operation fails mid-way
        THEN: Document state remains consistent
        """
        # Arrange
        doc_id = sample_doc.id
        original_lifecycle = sample_doc.lifecycle_stage

        # Act - Submit with invalid reviewer (simulated failure)
        try:
            publisher.submit_review(doc_id, reviewer_id=None)
        except Exception:
            pass

        # Assert - State unchanged
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == original_lifecycle


# ============================================================================
# Suite 9: Sync Operations
# ============================================================================

class TestSyncOperations:
    """Test sync_all functionality"""

    def test_sync_detects_missing_destination(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Published document with missing public file
        WHEN: Run sync_all
        THEN: Public file recreated
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")
        result = publisher.publish(doc_id)

        # Delete public file
        dest_path = Path(result.destination_path)
        dest_path.unlink()
        assert not dest_path.exists()

        # Act
        sync_result = publisher.sync_all(dry_run=False)

        # Assert
        assert len(sync_result.stats["missing_dest"]) == 1
        assert dest_path.exists()  # Recreated

    def test_sync_dry_run_does_not_modify(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Published document with issues
        WHEN: Run sync_all with dry_run=True
        THEN: Issues reported but no changes made
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")
        result = publisher.publish(doc_id)

        dest_path = Path(result.destination_path)
        dest_path.unlink()

        # Act
        sync_result = publisher.sync_all(dry_run=True)

        # Assert
        assert sync_result.dry_run is True
        assert len(sync_result.stats["missing_dest"]) == 1
        assert not dest_path.exists()  # NOT recreated

    def test_sync_detects_content_mismatch(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Published document with modified public file
        WHEN: Run sync_all
        THEN: Content mismatch detected and fixed
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")
        result = publisher.publish(doc_id)

        # Modify public file
        dest_path = Path(result.destination_path)
        dest_path.write_text("MODIFIED CONTENT", encoding='utf-8')

        # Act
        sync_result = publisher.sync_all(dry_run=False)

        # Assert
        assert len(sync_result.stats["content_mismatch"]) == 1
        assert dest_path.read_text(encoding='utf-8') == sample_doc.content  # Restored


# ============================================================================
# Suite 10: Auto-Publish Rules
# ============================================================================

class TestAutoPublishRules:
    """Test automatic publishing after approval"""

    def test_user_guide_auto_publishes_on_approval(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: User guide with PUBLIC visibility
        WHEN: Approve document
        THEN: Automatically published
        """
        # Arrange
        doc_id = sample_doc.id
        assert sample_doc.document_type == DocumentType.USER_GUIDE

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Act - Approve (should trigger auto-publish)
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Assert - Document auto-published
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value
        assert doc.published_path is not None

    def test_private_document_does_not_auto_publish(self, publisher, sample_doc):
        """
        GIVEN: Document with PRIVATE visibility
        WHEN: Approve document
        THEN: NOT automatically published
        """
        # Arrange
        doc_id = sample_doc.id
        sample_doc.visibility = DocumentVisibility.PRIVATE.value
        doc_methods.update_document_reference(publisher.db, sample_doc)

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Act
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")

        # Assert - NOT published
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.APPROVED.value  # Not published
        assert doc.published_path is None

    def test_manual_publish_flag_overrides_auto_rules(self, publisher, db, temp_workspace):
        """
        GIVEN: Document type that normally doesn't auto-publish
        WHEN: Approve with publish_now=True
        THEN: Published immediately
        """
        # Arrange - Design doc (doesn't auto-publish normally)
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=164,
            category="architecture",
            document_type=DocumentType.DESIGN_DOC,
            filename="design.md",
            file_path="docs/architecture/design_doc/design.md",
            title="Design Document",
            format=DocumentFormat.MARKDOWN,
            content="# Design",
            storage_mode=StorageMode.HYBRID,
            created_by="test-user"
        )
        doc.lifecycle_stage = DocumentLifecycle.DRAFT.value
        doc.visibility = DocumentVisibility.PUBLIC.value

        created = doc_methods.create_document_reference(db, doc)
        doc_id = created.id

        source_path = Path(created.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(created.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")

        # Act - Force publish
        publisher.approve(doc_id, reviewer_id="reviewer@test.com", publish_now=True)

        # Assert
        doc = doc_methods.get_document_reference(db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.PUBLISHED.value


# ============================================================================
# Suite 11: Archive Operations
# ============================================================================

class TestArchiveOperations:
    """Test document archival"""

    def test_archive_from_any_state(self, publisher, sample_doc):
        """
        GIVEN: Document in any lifecycle state
        WHEN: Archive document
        THEN: Successfully transitions to ARCHIVED
        """
        # Arrange
        doc_id = sample_doc.id

        # Act
        success = publisher.archive(doc_id, remove_public=False)

        # Assert
        assert success
        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.ARCHIVED.value

    def test_archive_unpublishes_when_requested(self, publisher, sample_doc, temp_workspace):
        """
        GIVEN: Published document
        WHEN: Archive with remove_public=True
        THEN: Unpublished then archived
        """
        # Arrange
        doc_id = sample_doc.id

        source_path = Path(sample_doc.computed_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(sample_doc.content, encoding='utf-8')

        publisher.submit_review(doc_id, reviewer_id="reviewer@test.com")
        publisher.approve(doc_id, reviewer_id="reviewer@test.com")
        result = publisher.publish(doc_id)

        dest_path = Path(result.destination_path)
        assert dest_path.exists()

        # Act
        success = publisher.archive(doc_id, remove_public=True)

        # Assert
        assert success
        assert not dest_path.exists()  # Public file removed

        doc = doc_methods.get_document_reference(publisher.db, doc_id)
        assert doc.lifecycle_stage == DocumentLifecycle.ARCHIVED.value


# ============================================================================
# Integration Test Summary
# ============================================================================

"""
Test Coverage Summary:

Suite 1: End-to-End Publish Workflow (2 tests)
- Full workflow draft → review → approved → published
- Workflow with rejection and rework

Suite 2: End-to-End Unpublish Workflow (2 tests)
- Unpublish removes public file, preserves source
- Unpublish fails if not published

Suite 3: List Unpublished Documents Query (2 tests)
- Lists approved + public documents
- Empty list when no unpublished docs

Suite 4: File System Operations (3 tests)
- Creates destination directory
- Preserves file content
- Handles missing source file

Suite 5: Database Updates (3 tests)
- Updates all publish-related fields
- Updates review assignment metadata
- Updates review completion metadata

Suite 6: Error Handling & Edge Cases (5 tests)
- Fails if not approved
- Fails if not public
- Validates reviewer authorization
- Requires rejection reason
- Handles nonexistent documents

Suite 7: Audit Trail Verification (4 tests)
- Submit review creates audit entry
- Approve creates audit entry
- Publish creates audit entry with paths
- Reject creates two audit entries

Suite 8: Transaction Rollback on Errors (2 tests)
- Rollback on file copy error
- State consistent after partial failure

Suite 9: Sync Operations (3 tests)
- Detects missing destination
- Dry run does not modify
- Detects content mismatch

Suite 10: Auto-Publish Rules (3 tests)
- User guide auto-publishes
- Private document doesn't auto-publish
- Manual publish flag overrides

Suite 11: Archive Operations (2 tests)
- Archive from any state
- Archive unpublishes when requested

Total: 31 integration tests covering all critical paths
"""
