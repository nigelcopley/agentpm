"""
Unit tests for document add path guidance and validation.

Tests the `_validate_and_guide_path` function in document/add.py
"""

import pytest
from unittest.mock import MagicMock, patch
from click.exceptions import Abort
from rich.console import Console
from agentpm.cli.commands.document.add import _validate_and_guide_path


class TestPathGuidanceValidPaths:
    """Test path guidance for already-valid paths."""

    def test_valid_path_passes_unchanged(self):
        """
        GIVEN a path that already follows docs/ structure
        WHEN validating path
        THEN path is returned unchanged without prompts
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "docs/planning/requirements/feature.md"
        document_type = "requirements"

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == file_path
        console.print.assert_not_called()  # No warnings displayed

    def test_valid_path_with_nested_structure(self):
        """
        GIVEN a valid path with nested subdirectories
        WHEN validating path
        THEN path is returned unchanged
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "docs/architecture/design/subsystems/auth/oauth2.md"
        document_type = "design"

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == file_path

    def test_valid_path_all_categories(self):
        """
        GIVEN valid paths for all standard categories
        WHEN validating paths
        THEN all pass unchanged
        """
        # Arrange
        console = MagicMock(spec=Console)
        valid_paths = [
            ("docs/planning/requirements/test.md", "requirements"),
            ("docs/architecture/design/test.md", "design"),
            ("docs/guides/user_guide/test.md", "user_guide"),
            ("docs/reference/specification/test.md", "specification"),
            ("docs/operations/runbook/test.md", "runbook"),
            ("docs/governance/quality_gates_specification/test.md", "quality_gates_specification"),
        ]

        for file_path, doc_type in valid_paths:
            # Act
            result = _validate_and_guide_path(file_path, doc_type, console)

            # Assert
            assert result == file_path, f"Failed for {file_path}"


class TestPathGuidanceNonCompliantPaths:
    """Test path guidance for non-compliant paths."""

    @patch('click.confirm')
    def test_non_docs_path_suggests_correction_accept(self, mock_confirm):
        """
        GIVEN a path not starting with docs/
        WHEN user accepts suggested path
        THEN corrected path is returned
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "requirements.md"
        document_type = "requirements"
        mock_confirm.return_value = True  # User accepts suggestion

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == "docs/planning/requirements/requirements.md"
        # Verify warning was displayed
        assert console.print.call_count > 0
        warning_calls = [str(call) for call in console.print.call_args_list]
        assert any("does not follow standard structure" in str(call) for call in warning_calls)

    @patch('click.confirm')
    def test_non_docs_path_decline_suggestion_accept_override(self, mock_confirm):
        """
        GIVEN a path not starting with docs/
        WHEN user declines suggestion but accepts override
        THEN original path is returned
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "legacy/requirements.md"
        document_type = "requirements"
        # First confirm (use suggested): False
        # Second confirm (continue with non-standard): True
        mock_confirm.side_effect = [False, True]

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == "legacy/requirements.md"

    @patch('click.confirm')
    def test_non_docs_path_decline_both_aborts(self, mock_confirm):
        """
        GIVEN a path not starting with docs/
        WHEN user declines both suggestion and override
        THEN Abort exception is raised
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "bad/path.md"
        document_type = "requirements"
        mock_confirm.side_effect = [False, False]  # Decline both prompts

        # Act & Assert
        with pytest.raises(Abort):
            _validate_and_guide_path(file_path, document_type, console)

    @patch('click.confirm')
    def test_category_inference_from_document_type(self, mock_confirm):
        """
        GIVEN non-compliant paths with various document types
        WHEN user accepts suggestion
        THEN correct category is inferred
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True

        test_cases = [
            ("requirements.md", "requirements", "docs/planning/requirements/requirements.md"),
            ("design.md", "design", "docs/architecture/design/design.md"),
            ("guide.md", "user_guide", "docs/guides/user_guide/guide.md"),
            ("spec.md", "specification", "docs/reference/specification/spec.md"),
            ("runbook.md", "runbook", "docs/operations/runbook/runbook.md"),
        ]

        for file_path, doc_type, expected_path in test_cases:
            # Act
            result = _validate_and_guide_path(file_path, doc_type, console)

            # Assert
            assert result == expected_path, f"Failed for {doc_type}"


class TestPathGuidanceDisplays:
    """Test that guidance messages are displayed correctly."""

    @patch('click.confirm')
    def test_displays_recommended_path(self, mock_confirm):
        """
        GIVEN non-compliant path
        WHEN validating
        THEN recommended path is displayed
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "test.md"
        document_type = "requirements"

        # Act
        _validate_and_guide_path(file_path, document_type, console)

        # Assert
        print_calls = [str(call) for call in console.print.call_args_list]
        # Should display recommended structure
        assert any("Recommended path structure" in str(call) for call in print_calls)
        assert any("docs/planning/requirements/test.md" in str(call) for call in print_calls)

    @patch('click.confirm')
    def test_displays_category_list(self, mock_confirm):
        """
        GIVEN non-compliant path
        WHEN validating
        THEN list of valid categories is displayed
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "test.md"
        document_type = "requirements"

        # Act
        _validate_and_guide_path(file_path, document_type, console)

        # Assert
        print_calls = [str(call) for call in console.print.call_args_list]
        # Should display category information
        assert any("Valid categories" in str(call) for call in print_calls)
        assert any("architecture" in str(call) for call in print_calls)
        assert any("planning" in str(call) for call in print_calls)
        assert any("guides" in str(call) for call in print_calls)

    @patch('click.confirm')
    def test_displays_standard_structure_pattern(self, mock_confirm):
        """
        GIVEN non-compliant path
        WHEN validating
        THEN standard structure pattern is displayed
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "test.md"
        document_type = "requirements"

        # Act
        _validate_and_guide_path(file_path, document_type, console)

        # Assert
        print_calls = [str(call) for call in console.print.call_args_list]
        # Should display structure pattern
        assert any("docs/{category}/{document_type}/{filename}" in str(call) for call in print_calls)


class TestPathGuidanceEdgeCases:
    """Test edge cases in path guidance."""

    @patch('click.confirm')
    def test_unmapped_document_type_defaults_to_communication(self, mock_confirm):
        """
        GIVEN document type not in mapping
        WHEN user accepts suggestion
        THEN communication category is used as default
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "unknown.md"
        document_type = "other"  # Not in standard mapping

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == "docs/communication/other/unknown.md"

    @patch('click.confirm')
    def test_preserves_filename_with_special_characters(self, mock_confirm):
        """
        GIVEN filename with special characters
        WHEN user accepts suggestion
        THEN filename is preserved exactly
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "test-file_v2.1-FINAL.md"
        document_type = "requirements"

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        assert result == "docs/planning/requirements/test-file_v2.1-FINAL.md"
        assert "test-file_v2.1-FINAL.md" in result

    @patch('click.confirm')
    def test_preserves_nested_filename_structure(self, mock_confirm):
        """
        GIVEN filename with path separators
        WHEN user accepts suggestion
        THEN nested structure is preserved
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "auth/oauth2/spec.md"
        document_type = "specification"

        # Act
        result = _validate_and_guide_path(file_path, document_type, console)

        # Assert
        # Should preserve path structure in filename
        assert "spec.md" in result
        assert result.startswith("docs/")


class TestPathGuidanceCoverage:
    """Additional coverage for path guidance scenarios."""

    def test_no_guidance_for_compliant_paths(self):
        """
        GIVEN compliant path
        WHEN validating
        THEN no user interaction occurs
        """
        # Arrange
        console = MagicMock(spec=Console)
        file_path = "docs/planning/requirements/test.md"
        document_type = "requirements"

        # Act
        with patch('click.confirm') as mock_confirm:
            result = _validate_and_guide_path(file_path, document_type, console)

            # Assert
            mock_confirm.assert_not_called()  # No user prompts
            assert result == file_path

    @patch('click.confirm')
    def test_guidance_message_includes_emojis(self, mock_confirm):
        """
        GIVEN non-compliant path
        WHEN displaying guidance
        THEN user-friendly emojis are included
        """
        # Arrange
        console = MagicMock(spec=Console)
        mock_confirm.return_value = True
        file_path = "test.md"
        document_type = "requirements"

        # Act
        _validate_and_guide_path(file_path, document_type, console)

        # Assert
        print_calls = [str(call) for call in console.print.call_args_list]
        # Should include emoji indicators
        assert any("⚠️" in str(call) or "💡" in str(call) or "📁" in str(call) or "📂" in str(call)
                   for call in print_calls)
