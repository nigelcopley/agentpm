"""
Tests for DOC-020 Document Validator - Visibility Validation

Tests the visibility validation rules added to DocumentValidator:
1. visibility must be 'private', 'public', or 'internal'
2. File path consistency (private in .agentpm/docs/, public/internal in docs/)
3. Internal types must be private
4. Published documents must match file location
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path

from agentpm.core.rules.validators.document_validator import DocumentValidator


class TestDocumentVisibilityValidation:
    """Test visibility validation rules."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test documents."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        # Create database schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE document_references (
                id INTEGER PRIMARY KEY,
                visibility TEXT DEFAULT 'private',
                file_path TEXT NOT NULL,
                document_type TEXT,
                lifecycle_stage TEXT DEFAULT 'draft',
                published_path TEXT,
                title TEXT
            )
        """)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        db_path.unlink()

    @pytest.fixture
    def validator(self, temp_db):
        """Create validator with temp database."""
        project_root = Path("/tmp/test_project")
        return DocumentValidator(project_root, temp_db)

    def test_valid_visibility_values(self, validator):
        """Test that only private, public, internal are valid."""
        # Valid values
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/test.md",
            document_type="requirements"
        )
        assert valid
        assert len(violations) == 0

        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/test.md",
            document_type="user_guide"
        )
        assert valid
        assert len(violations) == 0

        valid, violations = validator.validate_document_visibility(
            visibility="internal",
            file_path="docs/test.md",
            document_type="design_doc"
        )
        assert valid
        assert len(violations) == 0

        # Invalid value
        valid, violations = validator.validate_document_visibility(
            visibility="team",  # Invalid - should be 'internal'
            file_path="docs/test.md",
            document_type="requirements"
        )
        assert not valid
        assert len(violations) == 1
        assert "Invalid visibility 'team'" in violations[0]

    def test_file_path_consistency_private(self, validator):
        """Test private documents must be in .agentpm/docs/."""
        # Valid: private in .agentpm/docs/
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/internal/spec.md",
            document_type="requirements"
        )
        assert valid
        assert len(violations) == 0

        # Invalid: private in docs/
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path="docs/features/spec.md",
            document_type="requirements"
        )
        assert not valid
        assert len(violations) == 1
        assert "Private document must be in .agentpm/docs/" in violations[0]

    def test_file_path_consistency_public(self, validator):
        """Test public/internal documents must be in docs/."""
        # Valid: public in docs/
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide.md",
            document_type="user_guide"
        )
        assert valid
        assert len(violations) == 0

        # Invalid: public in .agentpm/docs/
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path=".agentpm/docs/guides/user_guide.md",
            document_type="user_guide"
        )
        assert not valid
        assert len(violations) == 1
        assert "Public document cannot be in .agentpm/docs/" in violations[0]

    def test_internal_types_must_be_private(self, validator):
        """Test internal document types must have private visibility."""
        internal_types = [
            'test_plan', 'test_report', 'coverage_report',
            'analysis_report', 'investigation_report', 'session_summary'
        ]

        for doc_type in internal_types:
            # Valid: internal type with private visibility
            valid, violations = validator.validate_document_visibility(
                visibility="private",
                file_path=f".agentpm/docs/internal/{doc_type}.md",
                document_type=doc_type
            )
            assert valid, f"Failed for {doc_type}"
            assert len(violations) == 0

            # Invalid: internal type with public visibility
            valid, violations = validator.validate_document_visibility(
                visibility="public",
                file_path=f"docs/{doc_type}.md",
                document_type=doc_type
            )
            assert not valid, f"Should fail for {doc_type}"
            assert any("is internal and must be 'private'" in v for v in violations)

    def test_published_documents_cannot_be_private(self, validator):
        """Test published documents cannot have private visibility."""
        # Valid: published with public visibility
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide.md",
            document_type="user_guide",
            lifecycle_stage="published",
            published_path="docs/guides/user_guide.md"
        )
        assert valid
        assert len(violations) == 0

        # Invalid: published with private visibility
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/guides/user_guide.md",
            document_type="user_guide",
            lifecycle_stage="published"
        )
        assert not valid
        assert len(violations) == 1
        assert "Published document cannot be 'private'" in violations[0]

    def test_published_path_must_be_in_docs(self, validator):
        """Test published_path must be in docs/."""
        # Invalid: published_path in .agentpm/docs/
        valid, violations = validator.validate_document_visibility(
            visibility="public",
            file_path="docs/guides/user_guide.md",
            document_type="user_guide",
            lifecycle_stage="published",
            published_path=".agentpm/docs/guides/user_guide.md"
        )
        assert not valid
        assert any("published_path in docs/" in v for v in violations)

    def test_validate_visibility_for_document_id(self, validator, temp_db):
        """Test validation by document ID."""
        # Insert test document
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO document_references
            (visibility, file_path, document_type, lifecycle_stage, title)
            VALUES (?, ?, ?, ?, ?)
        """, ("private", "docs/test.md", "requirements", "draft", "Test Doc"))
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Validate - should fail (private in docs/)
        valid, violations = validator.validate_visibility_for_document_id(doc_id)
        assert not valid
        assert len(violations) == 1
        assert "Private document must be in .agentpm/docs/" in violations[0]

    def test_validate_all_document_visibility(self, validator, temp_db):
        """Test validation of all documents in database."""
        # Insert test documents
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Valid document
        cursor.execute("""
            INSERT INTO document_references
            (visibility, file_path, document_type, title)
            VALUES (?, ?, ?, ?)
        """, ("private", ".agentpm/docs/spec.md", "requirements", "Valid Doc"))

        # Invalid document (private in docs/)
        cursor.execute("""
            INSERT INTO document_references
            (visibility, file_path, document_type, title)
            VALUES (?, ?, ?, ?)
        """, ("private", "docs/spec.md", "requirements", "Invalid Doc"))

        # Invalid document (test_plan as public)
        cursor.execute("""
            INSERT INTO document_references
            (visibility, file_path, document_type, title)
            VALUES (?, ?, ?, ?)
        """, ("public", "docs/test.md", "test_plan", "Invalid Test Plan"))

        conn.commit()
        conn.close()

        # Validate all
        valid, violations = validator.validate_all_document_visibility()
        assert not valid
        assert len(violations) == 2  # Two invalid documents

        # Check violations contain document IDs
        assert any("Document #2" in v for v in violations)
        assert any("Document #3" in v for v in violations)

    def test_multiple_violations_single_document(self, validator):
        """Test document can have multiple violations."""
        # Document with multiple issues:
        # 1. Internal type (test_plan) but public visibility
        # 2. Published but private
        valid, violations = validator.validate_document_visibility(
            visibility="private",
            file_path=".agentpm/docs/test.md",
            document_type="test_plan",
            lifecycle_stage="published"
        )
        assert not valid
        # Should have violation for published + private
        assert any("Published document cannot be 'private'" in v for v in violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
