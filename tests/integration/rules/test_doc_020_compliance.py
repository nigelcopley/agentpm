"""
Integration Tests for DOC-020: Database-First Document Creation Compliance

Tests comprehensive validation of DOC-020 rules including:
1. Visibility scope validation (private, public, internal)
2. File path consistency (private in .agentpm/docs/, public in docs/)
3. Type-specific enforcement (internal types must be private)
4. Publishing state validation (published docs cannot be private)
5. Multiple violations detection
6. CLI command integration (add, publish, unpublish)
7. End-to-end workflows

Architecture: Three-layer pattern (Models → Adapters → Methods → Validator → CLI)
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import Generator
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.rules.validators.document_validator import DocumentValidator
from agentpm.core.database.models.document_reference import DocumentReference
from agentpm.core.database.adapters.document_reference_adapter import DocumentReferenceAdapter
from agentpm.core.database.enums import (
    EntityType, DocumentType, DocumentFormat, DocumentCategory,
    DocumentVisibility, DocumentLifecycle
)
from agentpm.core.services.document_publisher import DocumentPublisher, ValidationError


@pytest.fixture
def temp_project_root(tmp_path) -> Generator[Path, None, None]:
    """Create temporary project structure."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create standard directory structure
    (project / "docs").mkdir()
    (project / ".agentpm" / "docs").mkdir(parents=True)

    # Create subdirectories for categories
    for category in ["guides", "architecture", "planning", "reference"]:
        (project / "docs" / category).mkdir()
        (project / ".agentpm" / "docs" / category).mkdir()

    yield project

    # Cleanup
    shutil.rmtree(project)


@pytest.fixture
def db_service(temp_project_root) -> Generator[DatabaseService, None, None]:
    """Create database service with schema."""
    db_path = temp_project_root / ".agentpm" / "data" / "agentpm.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create database schema (DatabaseService auto-runs migrations)
    db = DatabaseService(str(db_path))

    # Insert test data after migrations complete
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert test project first (required foreign key)
    cursor.execute("""
        INSERT INTO projects (id, name, path, status)
        VALUES (1, 'Test Project', '/tmp/test', 'active')
    """)

    # Insert test work item (using correct schema with 'name' not 'title')
    cursor.execute("""
        INSERT INTO work_items (id, project_id, name, type, status, is_continuous)
        VALUES (1, 1, 'Test Work Item', 'feature', 'draft', 0)
    """)

    conn.commit()
    conn.close()

    yield db

    # No close() method on DatabaseService - connection pooling handles cleanup


@pytest.fixture
def validator(temp_project_root, db_service) -> DocumentValidator:
    """Create document validator."""
    db_path = temp_project_root / ".agentpm" / "data" / "agentpm.db"
    return DocumentValidator(temp_project_root, db_path)


@pytest.fixture
def publisher(db_service) -> DocumentPublisher:
    """Create document publisher."""
    return DocumentPublisher(db_service)


class TestVisibilityScopeValidation:
    """Test Rule 1: Visibility must be 'private', 'public', or 'internal'"""

    def test_valid_private_visibility(self, validator):
        """Test private visibility is valid."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/planning/requirements/spec.md",
            document_type="requirements"
        )
        assert valid
        assert len(violations) == 0

    def test_valid_public_visibility(self, validator):
        """Test public visibility is valid."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/getting-started.md",
            document_type="user_guide"
        )
        assert valid
        assert len(violations) == 0

    def test_valid_internal_visibility(self, validator):
        """Test internal visibility is valid."""
        valid, violations = validator.validate_document_visibility(
            visibility="internal",
            file_path="docs/architecture/design_doc/auth-system.md",
            document_type="design_doc"
        )
        assert valid
        assert len(violations) == 0

    def test_invalid_visibility_team(self, validator):
        """Test invalid visibility value 'team'."""
        valid, violations = validator.validate_document_visibility(
            visibility="team",
            file_path="docs/planning/requirements/spec.md",
            document_type="requirements"
        )
        assert not valid
        assert len(violations) == 1
        assert "Invalid visibility 'team'" in violations[0]
        assert "private" in violations[0]
        assert "public" in violations[0]
        assert "internal" in violations[0]

    def test_invalid_visibility_restricted(self, validator):
        """Test invalid visibility value 'restricted'."""
        valid, violations = validator.validate_document_visibility(
            visibility="restricted",
            file_path="docs/planning/requirements/spec.md",
            document_type="requirements"
        )
        assert not valid
        assert "Invalid visibility" in violations[0]


class TestFilePathConsistency:
    """Test Rule 2: File path must match visibility"""

    def test_private_in_agentpm_docs(self, validator):
        """Test private documents must be in .agentpm/docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/planning/requirements/internal-spec.md",
            document_type="requirements"
        )
        assert valid
        assert len(violations) == 0

    def test_private_in_public_docs_fails(self, validator):
        """Test private documents cannot be in docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path="docs/planning/requirements/spec.md",
            document_type="requirements"
        )
        assert not valid
        assert len(violations) == 1
        assert "Private document must be in .agentpm/docs/" in violations[0]
        assert "Move to .agentpm/docs/" in violations[0]

    def test_public_in_docs(self, validator):
        """Test public documents must be in docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/guide.md",
            document_type="user_guide"
        )
        assert valid
        assert len(violations) == 0

    def test_public_in_agentpm_docs_fails(self, validator):
        """Test public documents cannot be in .agentpm/docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            document_type="user_guide"
        )
        assert not valid
        assert len(violations) == 1
        assert "Public document cannot be in .agentpm/docs/" in violations[0]
        assert "Move to docs/" in violations[0]

    def test_internal_in_docs(self, validator):
        """Test internal documents must be in docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="internal",
            file_path="docs/architecture/design_doc/design.md",
            document_type="design_doc"
        )
        assert valid
        assert len(violations) == 0

    def test_internal_in_agentpm_docs_fails(self, validator):
        """Test internal documents cannot be in .agentpm/docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="internal",
            file_path=".agentpm/docs/architecture/design_doc/design.md",
            document_type="design_doc"
        )
        assert not valid
        assert "Internal document cannot be in .agentpm/docs/" in violations[0]


class TestTypeSpecificEnforcement:
    """Test Rule 3: Internal types must be private"""

    @pytest.mark.parametrize("internal_type", [
        "test_plan",
        "test_report",
        "coverage_report",
        "validation_report",
        "analysis_report",
        "investigation_report",
        "assessment_report",
        "session_summary",
        "internal_note"
    ])
    def test_internal_type_with_private_visibility(self, validator, internal_type):
        """Test internal document types with private visibility (valid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=f".agentpm/docs/processes/{internal_type}/report.md",
            document_type=internal_type
        )
        assert valid, f"Failed for {internal_type}: {violations}"
        assert len(violations) == 0

    @pytest.mark.parametrize("internal_type", [
        "test_plan",
        "test_report",
        "coverage_report",
        "analysis_report",
        "investigation_report",
        "session_summary"
    ])
    def test_internal_type_with_public_visibility_fails(self, validator, internal_type):
        """Test internal document types with public visibility (invalid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path=f"docs/processes/{internal_type}/report.md",
            document_type=internal_type
        )
        assert not valid, f"Should fail for {internal_type}"
        assert len(violations) >= 1
        # Check for the type-specific error
        assert any("is internal and must be 'private'" in v for v in violations), \
            f"Expected internal type error for {internal_type}, got: {violations}"

    @pytest.mark.parametrize("internal_type", [
        "test_plan",
        "analysis_report"
    ])
    def test_internal_type_with_internal_visibility_fails(self, validator, internal_type):
        """Test internal document types with internal visibility (invalid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="internal",
            file_path=f"docs/processes/{internal_type}/report.md",
            document_type=internal_type
        )
        assert not valid
        assert any("is internal and must be 'private'" in v for v in violations)

    def test_public_type_with_public_visibility(self, validator):
        """Test public document types with public visibility (valid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/guide.md",
            document_type="user_guide"
        )
        assert valid
        assert len(violations) == 0


class TestPublishingStateValidation:
    """Test Rule 4: Published documents cannot be private"""

    def test_published_with_public_visibility(self, validator):
        """Test published documents with public visibility (valid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/guide.md",
            document_type="user_guide",
            lifecycle_stage="published",
            published_path="docs/guides/user_guide/guide.md"
        )
        assert valid
        assert len(violations) == 0

    def test_published_with_private_visibility_fails(self, validator):
        """Test published documents with private visibility (invalid)."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            document_type="user_guide",
            lifecycle_stage="published"
        )
        assert not valid
        assert len(violations) >= 1
        assert any("Published document cannot be 'private'" in v for v in violations)

    def test_published_path_in_docs(self, validator):
        """Test published_path must be in docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/guide.md",
            document_type="user_guide",
            lifecycle_stage="published",
            published_path="docs/guides/user_guide/guide.md"
        )
        assert valid
        assert len(violations) == 0

    def test_published_path_in_agentpm_docs_fails(self, validator):
        """Test published_path cannot be in .agentpm/docs/."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide/guide.md",
            document_type="user_guide",
            lifecycle_stage="published",
            published_path=".agentpm/docs/guides/user_guide/guide.md"
        )
        assert not valid
        assert any("published_path in docs/" in v for v in violations)

    def test_draft_with_any_visibility(self, validator):
        """Test draft documents can have any visibility."""
        for visibility in ["private", "public", "internal"]:
            file_path = ".agentpm/docs/guide.md" if visibility == "private" else "docs/guide.md"
            valid, violations = validator.validate_document_visibility(
                visibility=visibility,
                file_path=file_path,
                document_type="user_guide",
                lifecycle_stage="draft"
            )
            # Should pass or only fail on path consistency, not lifecycle
            if not valid:
                assert not any("draft" in v.lower() for v in violations), \
                    f"Should not fail on draft lifecycle for {visibility}"


class TestMultipleViolations:
    """Test detection of multiple violations in single document"""

    def test_private_in_wrong_location_and_published(self, validator):
        """Test document with both path violation and publishing violation."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path="docs/guides/user_guide/guide.md",  # Wrong location
            document_type="user_guide",
            lifecycle_stage="published"  # Cannot be published + private
        )
        assert not valid
        assert len(violations) >= 2
        assert any("Private document must be in .agentpm/docs/" in v for v in violations)
        assert any("Published document cannot be 'private'" in v for v in violations)

    def test_internal_type_public_visibility_wrong_path(self, validator):
        """Test internal type with public visibility in wrong location."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path=".agentpm/docs/processes/test_plan/plan.md",  # Wrong for public
            document_type="test_plan"  # Internal type
        )
        assert not valid
        assert len(violations) >= 2
        # Should have type violation + path violation
        assert any("is internal and must be 'private'" in v for v in violations)
        assert any("Public document cannot be in .agentpm/docs/" in v for v in violations)

    def test_all_violations_at_once(self, validator):
        """Test document violating all rules."""
        valid, violations = validator.validate_document_visibility(
            visibility="team",  # Invalid visibility
            file_path="docs/processes/test_plan/plan.md",
            document_type="test_plan",  # Internal type needs private
            lifecycle_stage="published"  # Published needs public
        )
        assert not valid
        # Should have at least invalid visibility error (early return)
        assert len(violations) >= 1
        assert "Invalid visibility 'team'" in violations[0]


class TestDatabaseIntegration:
    """Test validation integrated with database operations"""

    def test_validate_document_by_id(self, db_service, validator, temp_project_root):
        """Test validation of document by database ID."""
        # Create document in database
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/spec.md",  # Wrong for private
            category=DocumentCategory.PLANNING,
            document_type=DocumentType.REQUIREMENTS,
            title="Test Spec",
            visibility="private",  # Violation: private in docs/
            lifecycle_stage="draft"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Validate
        valid, violations = validator.validate_visibility_for_document_id(created.id)

        assert not valid
        assert len(violations) == 1
        assert "Private document must be in .agentpm/docs/" in violations[0]

    def test_validate_all_documents_in_database(self, db_service, validator):
        """Test validation of all documents in database."""
        # Create valid document
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/planning/requirements/spec1.md",
            category=DocumentCategory.PLANNING,
            document_type=DocumentType.REQUIREMENTS,
            title="Valid Private Doc",
            visibility="private",
            lifecycle_stage="draft"
        )
        DocumentReferenceAdapter.create(db_service, doc1)

        # Create invalid document (private in docs/)
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/spec2.md",
            category=DocumentCategory.PLANNING,
            document_type=DocumentType.REQUIREMENTS,
            title="Invalid Private Doc",
            visibility="private",
            lifecycle_stage="draft"
        )
        DocumentReferenceAdapter.create(db_service, doc2)

        # Create invalid document (test_plan as public)
        doc3 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/processes/test_plan/plan.md",
            category=DocumentCategory.PROCESSES,
            document_type=DocumentType.TEST_PLAN,
            title="Invalid Test Plan",
            visibility="public",
            lifecycle_stage="draft"
        )
        DocumentReferenceAdapter.create(db_service, doc3)

        # Validate all
        valid, violations = validator.validate_all_document_visibility()

        assert not valid
        assert len(violations) == 2  # Two invalid documents

        # Check violations reference document IDs
        assert any("Document #" in v for v in violations)
        assert any("Invalid Private Doc" in v for v in violations)
        assert any("Invalid Test Plan" in v for v in violations)


class TestPublisherIntegration:
    """Test validation in DocumentPublisher workflows"""

    def test_publish_requires_approved_state(self, db_service, publisher):
        """Test publish fails if not in approved state."""
        # Create draft document
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="User Guide",
            visibility="public",
            lifecycle_stage="draft",  # Not approved
            content="# Guide\nContent here"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Try to publish
        with pytest.raises(ValidationError) as exc_info:
            publisher.publish(created.id)

        assert "must be APPROVED to publish" in str(exc_info.value)
        assert "draft" in str(exc_info.value)

    def test_publish_requires_public_visibility(self, db_service, publisher):
        """Test publish fails if not public visibility."""
        # Create approved but private document
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="User Guide",
            visibility="private",  # Not public
            lifecycle_stage=DocumentLifecycle.APPROVED.value,  # Must be approved to test visibility check
            content="# Guide\nContent here"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Try to publish
        with pytest.raises(ValidationError) as exc_info:
            publisher.publish(created.id)

        assert "Only PUBLIC documents can be published" in str(exc_info.value)
        assert "private" in str(exc_info.value)

    def test_publish_requires_content(self, db_service, publisher):
        """Test publish fails if no content."""
        # Create approved public document without content
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="User Guide",
            visibility="public",
            lifecycle_stage=DocumentLifecycle.APPROVED.value,  # Must be approved
            content=None  # No content
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Try to publish
        with pytest.raises(ValidationError) as exc_info:
            publisher.publish(created.id)

        assert "no content to publish" in str(exc_info.value)

    def test_unpublish_requires_published_state(self, db_service, publisher):
        """Test unpublish fails if not in published state."""
        # Create approved document (not published)
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="User Guide",
            visibility="public",
            lifecycle_stage=DocumentLifecycle.APPROVED.value,  # Not published
            content="# Guide\nContent here"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Try to unpublish
        with pytest.raises(ValidationError) as exc_info:
            publisher.unpublish(created.id)

        assert "not published" in str(exc_info.value)
        assert "approved" in str(exc_info.value).lower()


class TestEndToEndWorkflows:
    """Test complete workflows with validation"""

    def test_draft_to_published_workflow(self, db_service, publisher, temp_project_root):
        """Test complete workflow: draft → review → approved → published."""
        # Step 1: Create draft document
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/getting-started.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="Getting Started",
            visibility="public",
            lifecycle_stage=DocumentLifecycle.DRAFT.value,
            content="# Getting Started\n\nWelcome to our platform!"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Create source file
        source_file = temp_project_root / doc.file_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(doc.content)

        # Step 2: Submit for review
        assert publisher.submit_review(created.id)

        # Step 3: Approve
        assert publisher.approve(created.id, reviewer_id="test@example.com")

        # Step 4: Publish
        result = publisher.publish(created.id, actor="test@example.com")

        assert result.success
        assert result.lifecycle_stage == "published"
        assert "docs/guides/" in result.destination_path

        # Verify published file exists
        published_file = temp_project_root / result.destination_path
        assert published_file.exists()
        assert published_file.read_text() == doc.content

    def test_reject_and_rework_workflow(self, db_service, publisher):
        """Test workflow: draft → review → rejected → draft (rework)."""
        # Create draft and submit for review
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/guides/user_guide/guide.md",
            category=DocumentCategory.GUIDES,
            document_type=DocumentType.USER_GUIDE,
            title="User Guide",
            visibility="public",
            lifecycle_stage=DocumentLifecycle.DRAFT.value,
            content="# Guide\nIncomplete content"
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Submit for review
        assert publisher.submit_review(created.id)

        # Reject with reason
        assert publisher.reject(
            created.id,
            reviewer_id="test@example.com",
            reason="Content is incomplete and needs more detail"
        )

        # Verify reverted to draft
        updated = db_service.get_one(
            "SELECT lifecycle_stage FROM document_references WHERE id = ?",
            (created.id,)
        )
        assert updated[0] == "draft"

    def test_private_internal_document_workflow(self, db_service, publisher):
        """Test workflow for internal/private documents (no publishing)."""
        # Create private test plan
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path=".agentpm/docs/processes/test_plan/feature-test-plan.md",
            category=DocumentCategory.PROCESSES,
            document_type=DocumentType.TEST_PLAN,
            title="Feature Test Plan",
            visibility="private",
            lifecycle_stage=DocumentLifecycle.DRAFT.value,
            content="# Test Plan\n\n## Test Cases\n..."
        )
        created = DocumentReferenceAdapter.create(db_service, doc)

        # Submit and approve
        assert publisher.submit_review(created.id)
        assert publisher.approve(created.id, reviewer_id="test@example.com")

        # Try to publish - should fail
        with pytest.raises(ValidationError) as exc_info:
            publisher.publish(created.id)

        assert "Only PUBLIC documents can be published" in str(exc_info.value)


class TestErrorMessages:
    """Test error messages are clear and actionable"""

    def test_invalid_visibility_error_message(self, validator):
        """Test invalid visibility error provides valid options."""
        valid, violations = validator.validate_document_visibility(
            visibility="team",
            file_path="docs/guide.md",
            document_type="user_guide"
        )

        assert not valid
        error = violations[0]
        assert "Invalid visibility 'team'" in error
        assert "private" in error
        assert "public" in error
        assert "internal" in error

    def test_path_mismatch_error_message(self, validator):
        """Test path mismatch error provides guidance."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path="docs/guide.md",
            document_type="user_guide"
        )

        assert not valid
        error = violations[0]
        assert "Private document must be in .agentpm/docs/" in error
        assert "Move to .agentpm/docs/" in error or "change visibility" in error

    def test_internal_type_error_message(self, validator):
        """Test internal type error explains requirement."""
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/processes/test_plan/plan.md",
            document_type="test_plan"
        )

        assert not valid
        error = [v for v in violations if "internal" in v][0]
        assert "test_plan" in error
        assert "is internal and must be 'private'" in error

    def test_publishing_state_error_message(self, validator):
        """Test publishing state error is clear."""
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/guide.md",
            document_type="user_guide",
            lifecycle_stage="published"
        )

        assert not valid
        error = [v for v in violations if "published" in v.lower()][0]
        assert "Published document cannot be 'private'" in error
        assert "approved" in error or "public" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
