"""
Test Document Path Generator Service

Tests for automatic document path generation from metadata.
Covers slugification, path construction, conflict resolution,
validation, and path correction.

Part of Work Item #164: Auto-Generate Document File Paths
Task #1079: Implement File Path Generator Service
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from agentpm.core.services.document_path_generator import (
    DocumentPathGenerator,
    GeneratedPathResult,
    CorrectionResult,
)
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.enums import EntityType


@pytest.fixture
def mock_db():
    """Mock database service."""
    db = Mock(spec=DatabaseService)
    return db


@pytest.fixture
def generator(mock_db):
    """Create path generator with mock database."""
    return DocumentPathGenerator(mock_db)


# =============================================================================
# CATEGORY A: SLUGIFICATION TESTS
# =============================================================================

class TestSlugification:
    """Test title slugification with various inputs."""

    def test_simple_title(self, generator):
        """Test simple title slugification."""
        result = generator.slugify("Authentication Requirements")
        assert result == "authentication-requirements"

    def test_title_with_punctuation(self, generator):
        """Test title with punctuation marks."""
        result = generator.slugify("OAuth 2.0: Implementation Guide")
        assert result == "oauth-2-0-implementation-guide"

    def test_title_with_special_characters(self, generator):
        """Test title with special characters."""
        result = generator.slugify("Test Plan #158 - OAuth")
        assert result == "test-plan-158-oauth"

    def test_title_with_parentheses(self, generator):
        """Test title with parentheses."""
        result = generator.slugify("User Guide (Getting Started)")
        assert result == "user-guide-getting-started"

    def test_unicode_with_accents(self, generator):
        """Test Unicode characters with accents."""
        result = generator.slugify("Configuración de Autenticación")
        assert result == "configuracion-de-autenticacion"

    def test_mixed_unicode(self, generator):
        """Test mixed Unicode characters."""
        result = generator.slugify("Système de Señalización (Niño)")
        assert result == "systeme-de-senalizacion-nino"

    def test_uppercase_to_lowercase(self, generator):
        """Test uppercase conversion."""
        result = generator.slugify("OAuth 2.0 Integration Guide")
        assert result == "oauth-2-0-integration-guide"

    def test_multiple_spaces(self, generator):
        """Test multiple consecutive spaces."""
        result = generator.slugify("Multiple   Spaces    Here")
        assert result == "multiple-spaces-here"

    def test_leading_trailing_spaces(self, generator):
        """Test leading and trailing spaces."""
        result = generator.slugify("  Leading and Trailing  ")
        assert result == "leading-and-trailing"

    def test_empty_title(self, generator):
        """Test empty title."""
        result = generator.slugify("")
        assert result == ""

    def test_whitespace_only_title(self, generator):
        """Test whitespace-only title."""
        result = generator.slugify("   ")
        assert result == ""

    def test_special_characters_only(self, generator):
        """Test title with only special characters."""
        result = generator.slugify("!@#$%^&*()")
        assert result == ""

    def test_very_long_title(self, generator):
        """Test very long title truncation."""
        long_title = "This is an extremely long title that exceeds the maximum allowed length and needs to be truncated at a word boundary to maintain readability"
        result = generator.slugify(long_title, max_length=100)

        # Should be truncated at word boundary
        assert len(result) <= 100
        assert not result.endswith('-')
        assert result.startswith("this-is-an-extremely-long-title")

    def test_title_with_numbers(self, generator):
        """Test title with numbers."""
        result = generator.slugify("Version 2.0 Release Notes")
        assert result == "version-2-0-release-notes"

    def test_title_with_underscores(self, generator):
        """Test title with underscores (should be preserved)."""
        result = generator.slugify("api_documentation_v2")
        assert result == "api_documentation_v2"

    def test_consecutive_hyphens_collapsed(self, generator):
        """Test consecutive hyphens are collapsed to single."""
        result = generator.slugify("Multiple---Hyphens---Here")
        assert result == "multiple-hyphens-here"


# =============================================================================
# CATEGORY B: FALLBACK SLUG TESTS
# =============================================================================

class TestFallbackSlug:
    """Test fallback slug generation."""

    def test_fallback_with_entity_id(self, generator):
        """Test fallback using entity type and ID."""
        result = generator.generate_fallback_slug("work_item", 158)
        assert result == "work-item-158"

    def test_fallback_with_timestamp(self, generator):
        """Test fallback using timestamp."""
        timestamp = datetime(2025, 10, 25, 14, 30, 0)
        result = generator.generate_fallback_slug("task", 1075, timestamp)
        assert result == "document-20251025-143000"

    def test_fallback_task_entity(self, generator):
        """Test fallback for task entity."""
        result = generator.generate_fallback_slug("task", 1075)
        assert result == "task-1075"

    def test_fallback_project_entity(self, generator):
        """Test fallback for project entity."""
        result = generator.generate_fallback_slug("project", 1)
        assert result == "project-1"


# =============================================================================
# CATEGORY C: BASE DIRECTORY DETERMINATION TESTS
# =============================================================================

class TestBaseDirectoryDetermination:
    """Test base directory determination from visibility and lifecycle."""

    def test_private_draft(self, generator):
        """Test private draft document."""
        result = generator.determine_base_dir("private", "draft")
        assert result == ".agentpm/docs"

    def test_private_published(self, generator):
        """Test private published document."""
        result = generator.determine_base_dir("private", "published")
        assert result == ".agentpm/docs"

    def test_restricted_draft(self, generator):
        """Test restricted draft document."""
        result = generator.determine_base_dir("restricted", "draft")
        assert result == ".agentpm/docs"

    def test_restricted_published(self, generator):
        """Test restricted published document."""
        result = generator.determine_base_dir("restricted", "published")
        assert result == ".agentpm/docs"

    def test_public_draft(self, generator):
        """Test public draft document (still private)."""
        result = generator.determine_base_dir("public", "draft")
        assert result == ".agentpm/docs"

    def test_public_review(self, generator):
        """Test public review document (still private)."""
        result = generator.determine_base_dir("public", "review")
        assert result == ".agentpm/docs"

    def test_public_approved(self, generator):
        """Test public approved document (still private)."""
        result = generator.determine_base_dir("public", "approved")
        assert result == ".agentpm/docs"

    def test_public_published(self, generator):
        """Test public published document (goes to docs/)."""
        result = generator.determine_base_dir("public", "published")
        assert result == "docs"

    def test_public_archived(self, generator):
        """Test public archived document (back to private)."""
        result = generator.determine_base_dir("public", "archived")
        assert result == ".agentpm/docs"


# =============================================================================
# CATEGORY D: PATH CONSTRUCTION TESTS
# =============================================================================

class TestPathConstruction:
    """Test path construction from components."""

    def test_construct_private_path(self, generator):
        """Test constructing private document path."""
        path = generator.construct_path(
            ".agentpm/docs",
            "planning",
            "requirements",
            "auth-functional.md"
        )
        assert str(path) == ".agentpm/docs/planning/requirements/auth-functional.md"

    def test_construct_public_path(self, generator):
        """Test constructing public document path."""
        path = generator.construct_path(
            "docs",
            "guides",
            "user_guide",
            "getting-started.md"
        )
        assert str(path) == "docs/guides/user_guide/getting-started.md"

    def test_construct_architecture_path(self, generator):
        """Test constructing architecture document path."""
        path = generator.construct_path(
            ".agentpm/docs",
            "architecture",
            "design_doc",
            "database-schema.md"
        )
        assert str(path) == ".agentpm/docs/architecture/design_doc/database-schema.md"


# =============================================================================
# CATEGORY E: CONFLICT RESOLUTION TESTS
# =============================================================================

class TestConflictResolution:
    """Test filename conflict resolution."""

    def test_no_conflict(self, generator, mock_db):
        """Test path with no conflicts."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            path = Path("docs/planning/requirements/auth.md")
            result = generator.resolve_conflicts(path, "work_item", 158)

            assert result == path

    def test_same_entity_reuses_path(self, generator, mock_db):
        """Test same entity reuses existing path."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            # First call: same entity doc found
            mock_doc = Mock()
            mock_doc.entity_type.value = "work_item"
            mock_doc.entity_id = 158
            mock_get.side_effect = [mock_doc]

            path = Path("docs/planning/requirements/auth.md")
            result = generator.resolve_conflicts(path, "work_item", 158)

            assert result == path

    def test_different_entity_gets_suffix(self, generator, mock_db):
        """Test different entity gets numeric suffix."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            # First call: same entity check returns None
            # Second call: any entity check returns existing doc
            # Third call: check -2 variant returns None
            mock_doc = Mock()
            mock_doc.entity_type.value = "work_item"
            mock_doc.entity_id = 158
            mock_get.side_effect = [None, mock_doc, None]

            path = Path("docs/planning/requirements/auth.md")
            result = generator.resolve_conflicts(path, "work_item", 159)

            assert str(result) == "docs/planning/requirements/auth-2.md"

    def test_multiple_conflicts(self, generator, mock_db):
        """Test resolving multiple conflicts."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_doc = Mock()
            # Same entity check, any check, -2 check, -3 check (free)
            mock_get.side_effect = [None, mock_doc, mock_doc, None]

            path = Path("docs/planning/requirements/auth.md")
            result = generator.resolve_conflicts(path, "work_item", 160)

            assert str(result) == "docs/planning/requirements/auth-3.md"


# =============================================================================
# CATEGORY F: PATH VALIDATION TESTS
# =============================================================================

class TestPathValidation:
    """Test path validation rules."""

    def test_valid_public_path(self, generator):
        """Test valid public document path."""
        is_valid, errors = generator.validate_path("docs/planning/requirements/auth.md")
        assert is_valid is True
        assert len(errors) == 0

    def test_valid_private_path(self, generator):
        """Test valid private document path."""
        is_valid, errors = generator.validate_path(".agentpm/docs/architecture/design_doc/system.md")
        assert is_valid is True
        assert len(errors) == 0

    def test_absolute_path_rejected(self, generator):
        """Test absolute path is rejected."""
        is_valid, errors = generator.validate_path("/etc/passwd")
        assert is_valid is False
        assert any("relative" in e.lower() for e in errors)

    def test_directory_traversal_rejected(self, generator):
        """Test directory traversal is rejected."""
        is_valid, errors = generator.validate_path("docs/../../../etc/passwd")
        assert is_valid is False
        assert any(".." in e for e in errors)

    def test_wrong_base_directory(self, generator):
        """Test wrong base directory is rejected."""
        is_valid, errors = generator.validate_path("var/log/app.md")
        assert is_valid is False
        assert any("docs/" in e or ".agentpm/docs/" in e for e in errors)

    def test_insufficient_depth(self, generator):
        """Test insufficient path depth."""
        is_valid, errors = generator.validate_path("docs/planning/auth.md")
        assert is_valid is False
        assert any("pattern" in e.lower() for e in errors)

    def test_wrong_extension(self, generator):
        """Test non-markdown extension is rejected."""
        is_valid, errors = generator.validate_path("docs/planning/requirements/auth.txt")
        assert is_valid is False
        assert any(".md" in e for e in errors)

    def test_invalid_characters(self, generator):
        """Test invalid characters are rejected."""
        is_valid, errors = generator.validate_path("docs/planning/requirements/auth<test>.md")
        assert is_valid is False
        assert any("invalid character" in e.lower() for e in errors)

    def test_path_too_long(self, generator):
        """Test path exceeding Windows MAX_PATH."""
        long_path = "docs/" + "a" * 260
        is_valid, errors = generator.validate_path(long_path)
        assert is_valid is False
        assert any("too long" in e.lower() for e in errors)

    def test_reserved_windows_name(self, generator):
        """Test reserved Windows filename."""
        is_valid, errors = generator.validate_path("docs/planning/requirements/CON.md")
        assert is_valid is False
        assert any("reserved" in e.lower() for e in errors)


# =============================================================================
# CATEGORY G: PATH CORRECTION TESTS
# =============================================================================

class TestPathCorrection:
    """Test path correction logic."""

    def test_no_path_provided(self, generator):
        """Test when no path is provided."""
        result = generator.correct_path(
            None,
            "docs/planning/requirements/auth.md",
            False
        )

        assert result.final_path == "docs/planning/requirements/auth.md"
        assert result.was_corrected is False
        assert result.needs_move is False

    def test_correct_path_provided(self, generator):
        """Test when correct path is provided."""
        result = generator.correct_path(
            "docs/planning/requirements/auth.md",
            "docs/planning/requirements/auth.md",
            True
        )

        assert result.final_path == "docs/planning/requirements/auth.md"
        assert result.was_corrected is False
        assert result.needs_move is False

    def test_wrong_path_file_exists(self, generator):
        """Test wrong path with existing file (should move)."""
        result = generator.correct_path(
            "docs/old/auth.md",
            "docs/planning/requirements/auth.md",
            True
        )

        assert result.final_path == "docs/planning/requirements/auth.md"
        assert result.was_corrected is True
        assert result.needs_move is True
        assert result.move_from == "docs/old/auth.md"
        assert "moved" in result.correction_reason.lower()

    def test_wrong_path_file_not_exists(self, generator):
        """Test wrong path with no file (should ignore)."""
        result = generator.correct_path(
            "docs/old/auth.md",
            "docs/planning/requirements/auth.md",
            False
        )

        assert result.final_path == "docs/planning/requirements/auth.md"
        assert result.was_corrected is True
        assert result.needs_move is False
        assert "ignored" in result.correction_reason.lower()


# =============================================================================
# CATEGORY H: INTEGRATION TESTS
# =============================================================================

class TestFullPathGeneration:
    """Test complete path generation workflow."""

    def test_private_requirements_document(self, generator, mock_db):
        """Test generating path for private requirements document."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            result = generator.generate_path(
                title="Phase 1 Completion Report",
                category="planning",
                doc_type="requirements",
                entity_type="work_item",
                entity_id=158,
                visibility="private",
                lifecycle="draft"
            )

            assert result.final_path == ".agentpm/docs/planning/requirements/phase-1-completion-report.md"
            assert result.filename == "phase-1-completion-report.md"
            assert result.directory == ".agentpm/docs/planning/requirements"
            assert result.is_valid is True

    def test_public_published_guide(self, generator, mock_db):
        """Test generating path for public published guide."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            result = generator.generate_path(
                title="Getting Started Guide",
                category="guides",
                doc_type="user_guide",
                entity_type="work_item",
                entity_id=164,
                visibility="public",
                lifecycle="published"
            )

            assert result.final_path == "docs/guides/user_guide/getting-started-guide.md"
            assert result.is_valid is True

    def test_empty_title_uses_fallback(self, generator, mock_db):
        """Test empty title uses fallback slug."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            result = generator.generate_path(
                title="",
                category="planning",
                doc_type="requirements",
                entity_type="work_item",
                entity_id=158,
                visibility="private",
                lifecycle="draft"
            )

            assert result.final_path == ".agentpm/docs/planning/requirements/work-item-158.md"
            assert result.is_valid is True

    def test_special_chars_only_uses_fallback(self, generator, mock_db):
        """Test special characters only uses fallback slug."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            # Mock datetime for consistent testing
            with patch('agentpm.core.services.document_path_generator.datetime') as mock_dt:
                mock_dt.utcnow.return_value = datetime(2025, 10, 25, 14, 30, 0)

                result = generator.generate_path(
                    title="!@#$%^&*()",
                    category="planning",
                    doc_type="requirements",
                    entity_type="work_item",
                    entity_id=164,
                    visibility="private",
                    lifecycle="draft"
                )

                # Should use entity-based fallback when timestamp not passed
                assert "work-item-164" in result.final_path or "document-" in result.final_path

    def test_path_correction_with_move(self, generator, mock_db, tmp_path):
        """Test path correction with file move."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            # Create source file
            old_file = tmp_path / "docs" / "old" / "auth.md"
            old_file.parent.mkdir(parents=True, exist_ok=True)
            old_file.write_text("test content")

            with patch.object(Path, 'exists', return_value=True):
                result = generator.generate_path(
                    title="Authentication Requirements",
                    category="planning",
                    doc_type="requirements",
                    entity_type="work_item",
                    entity_id=158,
                    visibility="private",
                    lifecycle="draft",
                    provided_path="docs/old/auth.md"
                )

                assert result.was_corrected is True
                assert result.needs_move is True
                assert result.final_path == ".agentpm/docs/planning/requirements/authentication-requirements.md"


# =============================================================================
# CATEGORY I: FILE MOVE TESTS
# =============================================================================

class TestFileMoveOperation:
    """Test file move operations."""

    def test_move_file_success(self, generator, tmp_path):
        """Test successful file move."""
        # Create source file
        from_path = tmp_path / "old" / "doc.md"
        from_path.parent.mkdir(parents=True, exist_ok=True)
        from_path.write_text("test content")

        # Create result with move needed
        result = GeneratedPathResult(
            final_path=str(tmp_path / "new" / "doc.md"),
            filename="doc.md",
            directory=str(tmp_path / "new"),
            was_corrected=True,
            original_path=str(from_path),
            correction_reason="Test move",
            needs_move=True,
            move_from=str(from_path),
            is_valid=True,
            validation_errors=[]
        )

        # Execute move
        moved = generator.move_file_to_correct_location(result)

        assert moved is True
        assert Path(result.final_path).exists()
        assert not from_path.exists()

    def test_move_file_not_needed(self, generator):
        """Test move when not needed."""
        result = GeneratedPathResult(
            final_path="docs/test.md",
            filename="test.md",
            directory="docs",
            was_corrected=False,
            original_path=None,
            correction_reason="",
            needs_move=False,
            move_from=None,
            is_valid=True,
            validation_errors=[]
        )

        moved = generator.move_file_to_correct_location(result)
        assert moved is False

    def test_move_file_source_not_exists(self, generator, tmp_path):
        """Test move when source file doesn't exist."""
        result = GeneratedPathResult(
            final_path=str(tmp_path / "new" / "doc.md"),
            filename="doc.md",
            directory=str(tmp_path / "new"),
            was_corrected=True,
            original_path=str(tmp_path / "old" / "doc.md"),
            correction_reason="Test move",
            needs_move=True,
            move_from=str(tmp_path / "old" / "doc.md"),
            is_valid=True,
            validation_errors=[]
        )

        with pytest.raises(FileNotFoundError):
            generator.move_file_to_correct_location(result)


# =============================================================================
# CATEGORY J: EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_generated_path_raises_error(self, generator, mock_db):
        """Test that invalid generated path raises ValueError."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            mock_get.return_value = None

            # This should generate an invalid path (wrong base)
            with patch.object(generator, 'determine_base_dir', return_value='wrong/base'):
                with pytest.raises(ValueError) as exc_info:
                    generator.generate_path(
                        title="Test Document",
                        category="planning",
                        doc_type="requirements",
                        entity_type="work_item",
                        entity_id=158,
                        visibility="private",
                        lifecycle="draft"
                    )

                assert "validation" in str(exc_info.value).lower()

    def test_max_conflicts_raises_error(self, generator, mock_db):
        """Test maximum conflicts raises RuntimeError."""
        with patch('agentpm.core.database.methods.document_references.get_document_by_path') as mock_get:
            # Always return a document (conflict on every attempt)
            # First call: same entity check returns None
            # All subsequent calls: different entity doc exists
            mock_doc = Mock()
            mock_doc.entity_type.value = "work_item"
            mock_doc.entity_id = 999  # Different entity
            mock_get.side_effect = [None] + [mock_doc] * 2000  # Many conflicts

            with pytest.raises(RuntimeError) as exc_info:
                generator.resolve_conflicts(
                    Path("docs/planning/requirements/auth.md"),
                    "work_item",
                    158
                )

            assert "1000 attempts" in str(exc_info.value)

    def test_unicode_edge_cases(self, generator):
        """Test various Unicode edge cases."""
        # Emoji
        result = generator.slugify("Test 👍 Document")
        assert "test" in result
        assert "document" in result

        # Chinese characters - will become empty after ASCII transliteration
        result = generator.slugify("测试文档")
        # Chinese characters don't transliterate to ASCII, so slug will be empty
        assert result == ""

        # Mixed scripts - only Latin characters survive
        result = generator.slugify("Test Тест تست")
        assert "test" in result
        # Cyrillic and Arabic won't transliterate, so we just get "test"
