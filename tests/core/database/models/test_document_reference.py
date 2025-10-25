"""
Comprehensive tests for DocumentReference model path validation.

Tests the strict path validation logic that enforces:
docs/{category}/{document_type}/{filename} structure.

Task: #590 - Create comprehensive path validation tests
Work Item: #113 - Document Path Validation Enforcement
"""

import pytest
from pydantic import ValidationError
from agentpm.core.database.models.document_reference import DocumentReference
from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat


class TestDocumentReferencePathValidation:
    """Test suite for DocumentReference path validation logic."""

    # ========================================================================
    # POSITIVE TESTS - Valid Paths
    # ========================================================================

    def test_valid_path_planning_requirements(self):
        """
        GIVEN a compliant path with docs/planning/requirements structure
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            file_path="docs/planning/requirements/auth-functional.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/auth-functional.md"
        assert doc.category == "planning"
        assert doc.document_type == DocumentType.REQUIREMENTS

    def test_valid_path_architecture_design(self):
        """
        GIVEN a compliant path with docs/architecture/design structure
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=100,
            category="architecture",
            document_type=DocumentType.DESIGN,
            file_path="docs/architecture/design/database-schema.md"
        )

        # Assert
        assert doc.file_path == "docs/architecture/design/database-schema.md"
        assert doc.category == "architecture"

    def test_valid_path_guides_user_guide(self):
        """
        GIVEN a compliant path with docs/guides/user_guide structure
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.PROJECT,
            entity_id=1,
            category="guides",
            document_type=DocumentType.USER_GUIDE,
            file_path="docs/guides/user_guide/getting-started.md"
        )

        # Assert
        assert doc.file_path == "docs/guides/user_guide/getting-started.md"

    def test_valid_path_operations_runbook(self):
        """
        GIVEN a compliant path with docs/operations/runbook structure
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=50,
            category="operations",
            document_type=DocumentType.RUNBOOK,
            file_path="docs/operations/runbook/deployment-procedure.md"
        )

        # Assert
        assert doc.file_path == "docs/operations/runbook/deployment-procedure.md"

    def test_valid_path_with_nested_subdirectories(self):
        """
        GIVEN a compliant path with additional nested directories
        WHEN creating a DocumentReference
        THEN validation should pass (nested structures allowed)
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=200,
            category="architecture",
            document_type=DocumentType.DESIGN,
            file_path="docs/architecture/design/subsystems/auth/oauth2.md"
        )

        # Assert
        assert doc.file_path == "docs/architecture/design/subsystems/auth/oauth2.md"

    def test_valid_path_all_categories(self):
        """
        GIVEN paths for all 8 valid categories
        WHEN creating DocumentReferences
        THEN all should pass validation
        """
        categories = [
            "planning",
            "architecture",
            "guides",
            "reference",
            "operations",
            "migrations",
            "decisions",
            "features"
        ]

        for category in categories:
            # Arrange & Act
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category=category,
                document_type=DocumentType.DESIGN,
                file_path=f"docs/{category}/design/test.md"
            )

            # Assert
            assert doc.category == category
            assert doc.file_path.startswith("docs/")

    # ========================================================================
    # NEGATIVE TESTS - Invalid Paths (Missing docs/ prefix)
    # ========================================================================

    def test_invalid_path_missing_docs_prefix(self):
        """
        GIVEN a path without docs/ prefix
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path="planning/requirements/test.md"
            )

        # Verify error message
        assert "must start with 'docs/'" in str(exc_info.value)

    def test_invalid_path_absolute_path(self):
        """
        GIVEN an absolute file system path
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.TASK,
                entity_id=50,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path="/absolute/path/to/file.md"
            )

        # Verify error message
        assert "must start with 'docs/'" in str(exc_info.value)

    def test_valid_path_root_file_exception(self):
        """
        GIVEN a file path for allowed root files (README.md, CHANGELOG.md, LICENSE.md)
        WHEN creating a DocumentReference
        THEN validation should pass (exception allowed)
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            document_type=DocumentType.OTHER,
            file_path="README.md"
        )

        # Assert
        assert doc.file_path == "README.md"

    # ========================================================================
    # NEGATIVE TESTS - Invalid Paths (Too Short)
    # ========================================================================

    def test_invalid_path_too_short_missing_category_and_type(self):
        """
        GIVEN a path with only docs/ and filename
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path="docs/incomplete.md"
            )

        # Verify error message
        assert "must follow pattern: docs/{category}/{document_type}/{filename}" in str(exc_info.value)

    def test_invalid_path_missing_document_type(self):
        """
        GIVEN a path missing the document_type level
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.TASK,
                entity_id=100,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path="docs/planning/test.md"
            )

        # Verify error message
        assert "must follow pattern: docs/{category}/{document_type}/{filename}" in str(exc_info.value)

    # ========================================================================
    # NEGATIVE TESTS - Category/Type Mismatch
    # ========================================================================

    def test_invalid_path_category_mismatch(self):
        """
        GIVEN a path where category in path doesn't match category field
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category="planning",  # Field says "planning"
                document_type=DocumentType.REQUIREMENTS,
                file_path="docs/architecture/requirements/test.md"  # Path says "architecture"
            )

        # Verify error message
        assert "doesn't match field category" in str(exc_info.value)

    def test_valid_path_document_type_flexible(self):
        """
        GIVEN a path where document_type directory doesn't match document_type field
        WHEN creating a DocumentReference
        THEN validation should pass (flexible classification allowed)

        Note: Path structure is for organization, document_type field is for classification.
        This allows flexible document organization while maintaining proper classification.
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,  # Field says "requirements"
            file_path="docs/planning/design/test.md"  # Path says "design" (directory)
        )

        # Assert
        assert doc.document_type == DocumentType.REQUIREMENTS
        assert "docs/planning/design/" in doc.file_path

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_edge_case_empty_path(self):
        """
        GIVEN an empty string as file_path
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path=""
            )

        # Verify min_length constraint triggered
        assert "String should have at least" in str(exc_info.value) or "must start with 'docs/'" in str(exc_info.value)

    def test_edge_case_very_long_path(self):
        """
        GIVEN a very long but valid path (under 500 char limit)
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange
        long_filename = "very_long_filename_" + "x" * 400 + ".md"
        long_path = f"docs/planning/requirements/{long_filename}"

        # Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            file_path=long_path
        )

        # Assert
        assert doc.file_path == long_path
        assert len(doc.file_path) < 500

    def test_edge_case_path_exceeds_max_length(self):
        """
        GIVEN a path exceeding 500 character limit
        WHEN creating a DocumentReference
        THEN ValidationError should be raised
        """
        # Arrange
        long_filename = "very_long_filename_" + "x" * 500 + ".md"
        long_path = f"docs/planning/requirements/{long_filename}"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                file_path=long_path
            )

        # Verify max_length constraint triggered
        assert "String should have at most" in str(exc_info.value)

    def test_edge_case_special_characters_in_filename(self):
        """
        GIVEN a path with special characters in filename
        WHEN creating a DocumentReference
        THEN validation should pass (special chars allowed in filename)
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            file_path="docs/planning/requirements/auth-2.0_v1.final.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/auth-2.0_v1.final.md"

    def test_edge_case_unicode_characters_in_filename(self):
        """
        GIVEN a path with unicode characters in filename
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            file_path="docs/planning/requirements/文档.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/文档.md"

    def test_edge_case_path_with_spaces(self):
        """
        GIVEN a path with spaces in directory/file names
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            file_path="docs/planning/requirements/auth system.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/auth system.md"

    def test_edge_case_multiple_nested_levels(self):
        """
        GIVEN a path with many nested subdirectories after document_type
        WHEN creating a DocumentReference
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=1,
            category="architecture",
            document_type=DocumentType.DESIGN,
            file_path="docs/architecture/design/level1/level2/level3/level4/deep.md"
        )

        # Assert
        assert doc.file_path == "docs/architecture/design/level1/level2/level3/level4/deep.md"

    # ========================================================================
    # HELPER METHOD TESTS
    # ========================================================================

    def test_construct_path_method(self):
        """
        GIVEN category, document_type, and filename
        WHEN calling DocumentReference.construct_path()
        THEN should return properly formatted path
        """
        # Arrange
        category = "planning"
        document_type = "requirements"
        filename = "auth-functional.md"

        # Act
        path = DocumentReference.construct_path(category, document_type, filename)

        # Assert
        assert path == "docs/planning/requirements/auth-functional.md"

    def test_parse_path_method_valid(self):
        """
        GIVEN a valid document path
        WHEN calling DocumentReference.parse_path()
        THEN should return dict with category, document_type, filename
        """
        # Arrange
        path = "docs/planning/requirements/auth-functional.md"

        # Act
        parsed = DocumentReference.parse_path(path)

        # Assert
        assert parsed["category"] == "planning"
        assert parsed["document_type"] == "requirements"
        assert parsed["filename"] == "auth-functional.md"

    def test_parse_path_method_with_nested_filename(self):
        """
        GIVEN a path with nested subdirectories in filename portion
        WHEN calling DocumentReference.parse_path()
        THEN should correctly join nested parts as filename
        """
        # Arrange
        path = "docs/architecture/design/subsystems/auth/oauth2.md"

        # Act
        parsed = DocumentReference.parse_path(path)

        # Assert
        assert parsed["category"] == "architecture"
        assert parsed["document_type"] == "design"
        assert parsed["filename"] == "subsystems/auth/oauth2.md"

    def test_parse_path_method_invalid(self):
        """
        GIVEN an invalid path structure
        WHEN calling DocumentReference.parse_path()
        THEN should raise ValueError
        """
        # Arrange
        invalid_path = "planning/requirements/test.md"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            DocumentReference.parse_path(invalid_path)

        # Verify error message
        assert "Invalid path structure" in str(exc_info.value)

    def test_validation_without_category_field(self):
        """
        GIVEN no category field provided (fields optional at model level)
        WHEN creating a DocumentReference with valid path
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/test.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/test.md"
        assert doc.category is None  # Not set from path

    def test_validation_without_document_type_field(self):
        """
        GIVEN no document_type field provided (fields optional at model level)
        WHEN creating a DocumentReference with valid path
        THEN validation should pass
        """
        # Arrange & Act
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/test.md"
        )

        # Assert
        assert doc.file_path == "docs/planning/requirements/test.md"
        assert doc.document_type is None  # Not set from path


class TestDocumentReferenceCoverage:
    """Additional tests to ensure >90% coverage of validation logic."""

    def test_minimal_valid_document(self):
        """Test minimal valid DocumentReference creation."""
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/test.md"
        )
        assert doc.id is None
        assert doc.entity_type == EntityType.WORK_ITEM
        assert doc.entity_id == 1

    def test_full_document_with_all_metadata(self):
        """Test DocumentReference with all optional fields."""
        doc = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=100,
            category="architecture",
            document_type=DocumentType.DESIGN,
            file_path="docs/architecture/design/system.md",
            title="System Architecture",
            description="High-level system design",
            file_size_bytes=4096,
            content_hash="abc123",
            format=DocumentFormat.MARKDOWN,
            segment_type="technical",
            component="auth",
            domain="security",
            audience="developer",
            maturity="approved",
            priority="high",
            tags=["architecture", "security", "oauth2"],
            phase="I1",
            work_item_id=50,
            created_by="test-agent"
        )

        assert doc.title == "System Architecture"
        assert doc.tags == ["architecture", "security", "oauth2"]
        assert doc.maturity == "approved"
