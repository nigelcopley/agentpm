"""
Unit tests for document migration helper functions.

Tests the core logic of migration without CLI integration complexity.
"""

import pytest
from pathlib import Path
from agentpm.cli.commands.document.migrate import (
    infer_category,
    construct_target_path,
    calculate_checksum,
    CATEGORY_MAPPING
)
from agentpm.core.database.enums import DocumentType


class TestCategoryInference:
    """Test category inference from document types."""

    def test_infer_category_requirements_to_planning(self):
        """
        GIVEN DocumentType.REQUIREMENTS
        WHEN inferring category
        THEN 'planning' is returned
        """
        # Arrange & Act
        result = infer_category(DocumentType.REQUIREMENTS)

        # Assert
        assert result == "planning"

    def test_infer_category_design_to_architecture(self):
        """
        GIVEN DocumentType.DESIGN
        WHEN inferring category
        THEN 'architecture' is returned
        """
        # Arrange & Act
        result = infer_category(DocumentType.DESIGN)

        # Assert
        assert result == "architecture"

    def test_infer_category_user_guide_to_guides(self):
        """
        GIVEN DocumentType.USER_GUIDE
        WHEN inferring category
        THEN 'guides' is returned
        """
        # Arrange & Act
        result = infer_category(DocumentType.USER_GUIDE)

        # Assert
        assert result == "guides"

    def test_infer_category_test_plan_to_testing(self):
        """
        GIVEN DocumentType.TEST_PLAN
        WHEN inferring category
        THEN 'testing' is returned
        """
        # Arrange & Act
        result = infer_category(DocumentType.TEST_PLAN)

        # Assert
        assert result == "testing"

    def test_infer_category_with_override(self):
        """
        GIVEN manual category override
        WHEN inferring category
        THEN override value is returned regardless of document type
        """
        # Arrange & Act
        result = infer_category(DocumentType.REQUIREMENTS, override="archive")

        # Assert
        assert result == "archive"

    def test_infer_category_none_type_defaults_to_communication(self):
        """
        GIVEN None document type
        WHEN inferring category
        THEN 'communication' (default) is returned
        """
        # Arrange & Act
        result = infer_category(None)

        # Assert
        assert result == "communication"

    def test_infer_category_unmapped_type_defaults_to_communication(self):
        """
        GIVEN document type not in mapping
        WHEN inferring category
        THEN 'communication' (default) is returned
        """
        # Arrange & Act
        result = infer_category(DocumentType.OTHER)

        # Assert
        assert result == "communication"


class TestConstructTargetPath:
    """Test target path construction."""

    def test_construct_target_path_basic(self):
        """
        GIVEN filename, category, and document type
        WHEN constructing target path
        THEN correct docs/{category}/{document_type}/{filename} path is returned
        """
        # Arrange & Act
        result = construct_target_path(
            filename="requirements.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )

        # Assert
        assert result == "docs/planning/requirements/requirements.md"

    def test_construct_target_path_architecture(self):
        """
        GIVEN design document parameters
        WHEN constructing target path
        THEN correct architecture path is returned
        """
        # Arrange & Act
        result = construct_target_path(
            filename="system-design.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )

        # Assert
        assert result == "docs/architecture/design/system-design.md"

    def test_construct_target_path_guides(self):
        """
        GIVEN user guide parameters
        WHEN constructing target path
        THEN correct guides path is returned
        """
        # Arrange & Act
        result = construct_target_path(
            filename="getting-started.md",
            category="guides",
            document_type=DocumentType.USER_GUIDE
        )

        # Assert
        assert result == "docs/guides/user_guide/getting-started.md"

    def test_construct_target_path_with_nested_filename(self):
        """
        GIVEN filename with subdirectories
        WHEN constructing target path
        THEN nested structure is preserved in filename part
        """
        # Arrange & Act
        result = construct_target_path(
            filename="auth/oauth2.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )

        # Assert
        assert result == "docs/architecture/design/auth/oauth2.md"

    def test_construct_target_path_none_document_type(self):
        """
        GIVEN None document type
        WHEN constructing target path
        THEN 'other' is used as document_type directory
        """
        # Arrange & Act
        result = construct_target_path(
            filename="misc.md",
            category="communication",
            document_type=None
        )

        # Assert
        assert result == "docs/communication/other/misc.md"


class TestCalculateChecksum:
    """Test file checksum calculation."""

    def test_calculate_checksum_valid_file(self, tmp_path):
        """
        GIVEN a file with content
        WHEN calculating checksum
        THEN SHA-256 hash is returned
        """
        # Arrange
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        # Act
        checksum = calculate_checksum(test_file)

        # Assert
        assert checksum is not None
        assert len(checksum) == 64  # SHA-256 produces 64 hex characters
        assert checksum == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    def test_calculate_checksum_nonexistent_file(self, tmp_path):
        """
        GIVEN nonexistent file path
        WHEN calculating checksum
        THEN None is returned
        """
        # Arrange
        nonexistent = tmp_path / "does_not_exist.txt"

        # Act
        checksum = calculate_checksum(nonexistent)

        # Assert
        assert checksum is None

    def test_calculate_checksum_empty_file(self, tmp_path):
        """
        GIVEN empty file
        WHEN calculating checksum
        THEN checksum of empty content is returned
        """
        # Arrange
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()

        # Act
        checksum = calculate_checksum(empty_file)

        # Assert
        assert checksum is not None
        assert len(checksum) == 64
        # SHA-256 of empty file
        assert checksum == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_calculate_checksum_large_file(self, tmp_path):
        """
        GIVEN large file (>4KB to test chunked reading)
        WHEN calculating checksum
        THEN correct checksum is returned
        """
        # Arrange
        large_file = tmp_path / "large.txt"
        # Create 10KB file
        content = "A" * (10 * 1024)
        large_file.write_text(content)

        # Act
        checksum = calculate_checksum(large_file)

        # Assert
        assert checksum is not None
        assert len(checksum) == 64

    def test_calculate_checksum_deterministic(self, tmp_path):
        """
        GIVEN same file content
        WHEN calculating checksum multiple times
        THEN same checksum is returned each time
        """
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("Deterministic content")

        # Act
        checksum1 = calculate_checksum(test_file)
        checksum2 = calculate_checksum(test_file)

        # Assert
        assert checksum1 == checksum2


class TestCategoryMapping:
    """Test category mapping completeness."""

    def test_all_planning_types_mapped(self):
        """
        GIVEN planning-related document types
        WHEN checking mapping
        THEN all map to 'planning' category
        """
        # Arrange
        planning_types = [
            DocumentType.REQUIREMENTS,
            DocumentType.USER_STORY,
            DocumentType.USE_CASE,
        ]

        # Act & Assert
        for doc_type in planning_types:
            assert CATEGORY_MAPPING.get(doc_type) == "planning"

    def test_all_architecture_types_mapped(self):
        """
        GIVEN architecture-related document types
        WHEN checking mapping
        THEN all map to 'architecture' category
        """
        # Arrange
        architecture_types = [
            DocumentType.ARCHITECTURE,
            DocumentType.DESIGN,
            DocumentType.SPECIFICATION,
            DocumentType.TECHNICAL_SPECIFICATION,
            DocumentType.ADR,
        ]

        # Act & Assert
        for doc_type in architecture_types:
            assert CATEGORY_MAPPING.get(doc_type) == "architecture"

    def test_all_guide_types_mapped(self):
        """
        GIVEN guide-related document types
        WHEN checking mapping
        THEN all map to 'guides' category
        """
        # Arrange
        guide_types = [
            DocumentType.USER_GUIDE,
            DocumentType.ADMIN_GUIDE,
            DocumentType.API_DOC,
            DocumentType.TROUBLESHOOTING,
        ]

        # Act & Assert
        for doc_type in guide_types:
            assert CATEGORY_MAPPING.get(doc_type) == "guides"


class TestMigrationIntegration:
    """Integration tests for migration workflow."""

    def test_end_to_end_path_construction(self):
        """
        GIVEN legacy document parameters
        WHEN going through full migration path construction
        THEN correct target path is produced
        """
        # Arrange
        filename = "api-spec.md"
        doc_type = DocumentType.API_DOC

        # Act
        category = infer_category(doc_type)
        target_path = construct_target_path(filename, category, doc_type)

        # Assert
        assert category == "guides"
        assert target_path == "docs/guides/api_doc/api-spec.md"

    def test_migration_with_manual_override(self):
        """
        GIVEN legacy document with manual category override
        WHEN constructing migration path
        THEN override category is used
        """
        # Arrange
        filename = "old-doc.md"
        doc_type = DocumentType.DESIGN
        manual_category = "archive"

        # Act
        category = infer_category(doc_type, override=manual_category)
        target_path = construct_target_path(filename, category, doc_type)

        # Assert
        assert category == "archive"
        assert target_path == "docs/archive/design/old-doc.md"
