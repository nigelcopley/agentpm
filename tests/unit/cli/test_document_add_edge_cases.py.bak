"""
Comprehensive edge case tests for document add command to achieve ≥90% coverage.

Tests uncovered branches, error paths, and validation logic.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
from click.exceptions import Abort
from rich.console import Console

from agentpm.cli.commands.document.add import (
    _validate_and_guide_path,
    _detect_document_type,
    _detect_document_format,
    _generate_title_from_path,
    _format_file_size,
    _detect_category_from_path,
    _validate_category_type_consistency,
    _normalize_entity_type,
    CATEGORY_MAPPING
)


class TestValidateAndGuidePathEdgeCases:
    """Test uncovered edge cases in path validation."""

    def test_absolute_path_rejected(self):
        """
        GIVEN an absolute file path
        WHEN validating path
        THEN Abort exception is raised with guidance
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "/absolute/path/to/file.md"
        document_type = "requirements"

        # Act & Assert
        with pytest.raises(Abort):
            _validate_and_guide_path(file_path, document_type, console)

        # Verify error message was displayed
        assert console.print.call_count > 0
        calls = [str(call) for call in console.print.call_args_list]
        assert any("Absolute paths are not allowed" in str(call) for call in calls)

    def test_path_too_short_aborts(self):
        """
        GIVEN a path with fewer than 4 parts (docs/category/type/file)
        WHEN validating path
        THEN Abort exception is raised
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "docs/planning/file.md"  # Only 3 parts
        document_type = "requirements"

        # Act & Assert
        with pytest.raises(Abort):
            _validate_and_guide_path(file_path, document_type, console)

        # Verify error message
        calls = [str(call) for call in console.print.call_args_list]
        assert any("incomplete" in str(call).lower() for call in calls)

    def test_strict_mode_rejects_non_docs_path(self):
        """
        GIVEN strict validation mode enabled
        WHEN path doesn't start with docs/
        THEN Abort exception is raised immediately without prompts
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "legacy/file.md"
        document_type = "requirements"

        # Act & Assert
        with pytest.raises(Abort):
            _validate_and_guide_path(file_path, document_type, console, strict=True)

        # Verify no user prompts (strict mode)
        calls = [str(call) for call in console.print.call_args_list]
        assert any("must start with 'docs/'" in str(call) for call in calls)


class TestDetectDocumentType:
    """Test document type detection from file paths."""

    def test_detect_adr_type(self):
        """
        GIVEN path containing 'adr/' or 'decision/'
        WHEN detecting document type
        THEN 'adr' is returned
        """
        assert _detect_document_type("docs/adr/001-decision.md") == "adr"
        assert _detect_document_type("docs/decision/architecture.md") == "adr"
        assert _detect_document_type("docs/decisions/choice.md") == "adr"

    def test_detect_architecture_type(self):
        """Test architecture document detection."""
        assert _detect_document_type("docs/architecture/system.md") == "architecture"
        assert _detect_document_type("docs/arch/design.md") == "architecture"

    def test_detect_api_doc_type(self):
        """Test API documentation detection."""
        assert _detect_document_type("docs/api/endpoints.md") == "api_doc"
        assert _detect_document_type("docs/api-docs/swagger.yaml") == "api_doc"
        assert _detect_document_type("docs/openapi/spec.json") == "api_doc"

    def test_detect_user_guide_type(self):
        """Test user guide detection."""
        assert _detect_document_type("docs/user-guide/intro.md") == "user_guide"
        assert _detect_document_type("docs/user_guide/getting-started.md") == "user_guide"
        assert _detect_document_type("docs/manual/usage.md") == "user_guide"
        assert _detect_document_type("docs/tutorial/basics.md") == "user_guide"

    def test_detect_test_plan_type(self):
        """Test test plan detection."""
        assert _detect_document_type("docs/test-plan/acceptance.md") == "test_plan"
        assert _detect_document_type("docs/testing/strategy.md") == "test_plan"
        assert _detect_document_type("docs/qa/checklist.md") == "test_plan"

    def test_detect_troubleshooting_type(self):
        """Test troubleshooting document detection."""
        assert _detect_document_type("docs/troubleshooting/common-issues.md") == "troubleshooting"
        assert _detect_document_type("docs/troubleshoot/debugging.md") == "troubleshooting"
        assert _detect_document_type("docs/debug/guide.md") == "troubleshooting"

    def test_detect_user_story_type(self):
        """Test user story detection."""
        assert _detect_document_type("docs/user-story/auth.md") == "user_story"
        assert _detect_document_type("docs/stories/payment.md") == "user_story"

    def test_detect_other_deployment_type(self):
        """Test deployment guide returns 'other' (not in enum)."""
        assert _detect_document_type("docs/deployment/guide.md") == "other"
        assert _detect_document_type("docs/deploy/instructions.md") == "other"
        assert _detect_document_type("docs/operations/runbook.md") == "other"

    def test_detect_other_changelog_type(self):
        """Test changelog returns 'other' (not in enum)."""
        assert _detect_document_type("docs/changelog/v1.0.md") == "other"
        assert _detect_document_type("docs/release-notes/latest.md") == "other"

    def test_detect_defaults_to_specification(self):
        """Test unknown paths default to 'specification'."""
        assert _detect_document_type("docs/unknown/file.md") == "specification"
        assert _detect_document_type("random/path.md") == "specification"


class TestDetectDocumentFormat:
    """Test document format detection from file extensions."""

    def test_detect_markdown_format(self):
        """Test markdown file detection."""
        assert _detect_document_format("file.md") == "markdown"

    def test_detect_html_formats(self):
        """Test HTML file detection."""
        assert _detect_document_format("file.html") == "html"
        assert _detect_document_format("file.htm") == "html"

    def test_detect_pdf_format(self):
        """Test PDF file detection."""
        assert _detect_document_format("file.pdf") == "pdf"

    def test_detect_text_format(self):
        """Test plain text file detection."""
        assert _detect_document_format("file.txt") == "text"

    def test_detect_json_format(self):
        """Test JSON file detection."""
        assert _detect_document_format("file.json") == "json"

    def test_detect_yaml_formats(self):
        """Test YAML file detection."""
        assert _detect_document_format("file.yaml") == "yaml"
        assert _detect_document_format("file.yml") == "yaml"

    def test_detect_other_format(self):
        """Test unknown extensions default to 'other'."""
        assert _detect_document_format("file.xyz") == "other"
        assert _detect_document_format("file") == "other"
        assert _detect_document_format("file.docx") == "other"

    def test_case_insensitive_detection(self):
        """Test format detection is case-insensitive."""
        assert _detect_document_format("FILE.MD") == "markdown"
        assert _detect_document_format("FILE.YAML") == "yaml"


class TestGenerateTitleFromPath:
    """Test title generation from file paths."""

    def test_generate_title_from_simple_filename(self):
        """Test title generation from simple filename."""
        assert _generate_title_from_path("requirements.md") == "Requirements"

    def test_generate_title_with_hyphens(self):
        """Test title generation with hyphens."""
        result = _generate_title_from_path("user-authentication-design.md")
        assert result == "User Authentication Design"

    def test_generate_title_with_underscores(self):
        """Test title generation with underscores."""
        result = _generate_title_from_path("api_specification_v2.md")
        assert result == "Api Specification V2"

    def test_generate_title_with_mixed_separators(self):
        """Test title generation with mixed separators."""
        result = _generate_title_from_path("oauth2_auth-flow.md")
        assert result == "Oauth2 Auth Flow"

    def test_generate_title_from_path_with_directories(self):
        """Test title generation extracts just the filename."""
        result = _generate_title_from_path("docs/planning/requirements/feature-spec.md")
        assert result == "Feature Spec"


class TestFormatFileSize:
    """Test file size formatting."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        assert _format_file_size(512) == "512 B"
        assert _format_file_size(1023) == "1023 B"

    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        assert _format_file_size(1024) == "1.0 KB"
        assert _format_file_size(2048) == "2.0 KB"
        assert _format_file_size(1536) == "1.5 KB"

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert _format_file_size(1024 * 1024) == "1.0 MB"
        assert _format_file_size(1024 * 1024 * 2) == "2.0 MB"
        assert _format_file_size(1024 * 1024 * 1.5) == "1.5 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabytes."""
        assert _format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert _format_file_size(1024 * 1024 * 1024 * 2) == "2.0 GB"


class TestDetectCategoryFromPath:
    """Test category detection from path structure."""

    def test_detect_category_from_valid_path(self):
        """Test category detection from docs/ path."""
        assert _detect_category_from_path("docs/planning/requirements/test.md") == "planning"
        assert _detect_category_from_path("docs/architecture/design/test.md") == "architecture"
        assert _detect_category_from_path("docs/guides/user_guide/test.md") == "guides"

    def test_detect_category_invalid_category_returns_none(self):
        """Test invalid category returns None."""
        assert _detect_category_from_path("docs/invalid_category/type/test.md") is None

    def test_detect_category_non_docs_path_returns_none(self):
        """Test non-docs/ paths return None."""
        assert _detect_category_from_path("legacy/file.md") is None
        assert _detect_category_from_path("requirements.md") is None

    def test_detect_category_too_short_path_returns_category_if_valid(self):
        """Test paths with 2 parts still return category if valid (docs/category)."""
        # Category is returned even for short paths if category is valid
        assert _detect_category_from_path("docs/planning") == "planning"
        assert _detect_category_from_path("docs/architecture") == "architecture"
        # Empty or just docs/ returns None
        assert _detect_category_from_path("docs/") is None


class TestValidateCategoryTypeConsistency:
    """Test category and document type consistency validation."""

    def test_category_path_mismatch_aborts(self):
        """
        GIVEN category field doesn't match path
        WHEN validating consistency
        THEN Abort exception is raised
        """
        # Arrange
        console = MagicMock(spec=Console)
        category = "planning"
        doc_type = "requirements"
        file_path = "docs/architecture/requirements/test.md"  # Path says architecture

        # Act & Assert
        with pytest.raises(Abort):
            _validate_category_type_consistency(category, doc_type, file_path, console)

    def test_document_type_path_mismatch_aborts(self):
        """
        GIVEN document_type field doesn't match path
        WHEN validating consistency
        THEN Abort exception is raised
        """
        # Arrange
        console = MagicMock(spec=Console)
        category = "planning"
        doc_type = "requirements"  # Field says requirements
        file_path = "docs/planning/design/test.md"  # Path says design

        # Act & Assert
        with pytest.raises(Abort):
            _validate_category_type_consistency(category, doc_type, file_path, console)

    def test_category_type_mapping_warning(self):
        """
        GIVEN category/type mapping is illogical but not wrong
        WHEN validating consistency
        THEN warning is displayed but no abort
        """
        # Arrange
        console = MagicMock(spec=Console)
        category = "operations"  # User specified operations
        doc_type = "requirements"  # But requirements typically go in planning
        file_path = "docs/operations/requirements/test.md"

        # Act - should complete without exception
        _validate_category_type_consistency(category, doc_type, file_path, console)

        # Assert - warning should be displayed
        calls = [str(call) for call in console.print.call_args_list]
        assert any("may be inconsistent" in str(call).lower() for call in calls)

    def test_consistent_category_type_no_warning(self):
        """
        GIVEN consistent category and type
        WHEN validating consistency
        THEN no warnings or errors
        """
        # Arrange
        console = MagicMock(spec=Console)
        category = "planning"
        doc_type = "requirements"
        file_path = "docs/planning/requirements/test.md"

        # Act
        _validate_category_type_consistency(category, doc_type, file_path, console)

        # Assert - no output
        console.print.assert_not_called()


class TestNormalizeEntityType:
    """Test entity type normalization callback."""

    def test_normalize_work_item_hyphenated(self):
        """Test work-item is normalized to work_item."""
        result = _normalize_entity_type(None, None, "work-item")
        assert result == "work_item"

    def test_normalize_already_underscored(self):
        """Test already underscored values pass through."""
        result = _normalize_entity_type(None, None, "work_item")
        assert result == "work_item"

    def test_normalize_none_value(self):
        """Test None value is handled."""
        result = _normalize_entity_type(None, None, None)
        assert result is None

    def test_normalize_task(self):
        """Test non-hyphenated values pass through."""
        result = _normalize_entity_type(None, None, "task")
        assert result == "task"


class TestCategoryMapping:
    """Test CATEGORY_MAPPING completeness."""

    def test_mapping_covers_all_planning_types(self):
        """Test all planning document types are mapped."""
        planning_types = ['requirements', 'user_story', 'use_case', 'refactoring_guide', 'implementation_plan']
        for doc_type in planning_types:
            assert CATEGORY_MAPPING.get(doc_type) == 'planning', f"{doc_type} should map to planning"

    def test_mapping_covers_all_architecture_types(self):
        """Test all architecture document types are mapped."""
        arch_types = ['architecture', 'design', 'adr', 'technical_specification']
        for doc_type in arch_types:
            assert CATEGORY_MAPPING.get(doc_type) == 'architecture', f"{doc_type} should map to architecture"

    def test_mapping_covers_all_guide_types(self):
        """Test all guide document types are mapped."""
        guide_types = ['user_guide', 'admin_guide', 'troubleshooting', 'migration_guide']
        for doc_type in guide_types:
            assert CATEGORY_MAPPING.get(doc_type) == 'guides', f"{doc_type} should map to guides"

    def test_mapping_covers_reference_types(self):
        """Test reference document types are mapped."""
        assert CATEGORY_MAPPING.get('specification') == 'reference'
        assert CATEGORY_MAPPING.get('api_doc') == 'reference'

    def test_mapping_covers_process_types(self):
        """Test process document types are mapped."""
        assert CATEGORY_MAPPING.get('test_plan') == 'processes'

    def test_mapping_covers_governance_types(self):
        """Test governance document types are mapped."""
        assert CATEGORY_MAPPING.get('quality_gates_specification') == 'governance'

    def test_mapping_covers_operations_types(self):
        """Test operations document types are mapped."""
        assert CATEGORY_MAPPING.get('runbook') == 'operations'

    def test_mapping_covers_communication_types(self):
        """Test communication document types are mapped."""
        comm_types = ['business_pillars_analysis', 'market_research_report',
                      'competitive_analysis', 'stakeholder_analysis']
        for doc_type in comm_types:
            assert CATEGORY_MAPPING.get(doc_type) == 'communication', f"{doc_type} should map to communication"
