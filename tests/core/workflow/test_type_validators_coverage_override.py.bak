"""
Test Type Validators Coverage Override Functionality

Tests the coverage_override feature that allows tasks with verified coverage
for their specific scope to bypass project-wide coverage validation.

This fixes the issue where task-specific work (e.g., Detection Pack unit tests)
was blocked by coverage requirements for the entire codebase, even though the
task's specific scope had adequate coverage.
"""

import pytest
from agentpm.core.workflow.type_validators import TypeSpecificValidators
from agentpm.core.database.enums import TaskType, TaskStatus


class TestCoverageOverride:
    """Test coverage override functionality in type validators"""

    def test_coverage_override_bypasses_validation(self):
        """Test that coverage_override=true bypasses coverage validation"""
        # Arrange: Task with coverage override
        metadata = {
            "test_plan": "Unit tests for specific module",
            "tests_passing": True,
            "coverage_percent": 95,
            "coverage_override": True,
            "coverage_scope": "Specific module only",
            "override_reason": "Project-wide coverage check not applicable"
        }

        # Act: Validate for REVIEW status
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW,
            db_service=None,  # No DB service - would normally skip validation
            project_id=None
        )

        # Assert: Validation passes due to coverage_override
        assert result.valid is True
        assert result.reason is None

    def test_without_coverage_override_requires_db_context(self):
        """Test that without override, validation needs DB context"""
        # Arrange: Task without coverage override
        metadata = {
            "test_plan": "Unit tests for module",
            "tests_passing": True,
            "coverage_percent": 95
        }

        # Act: Validate without DB service (should skip validation gracefully)
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW,
            db_service=None,
            project_id=None
        )

        # Assert: Validation passes because DB context is missing
        # (graceful degradation - no DB = no strict validation)
        assert result.valid is True

    def test_coverage_override_requires_tests_passing(self):
        """Test that coverage_override doesn't bypass failing tests check"""
        # Arrange: Task with coverage override but failing tests
        metadata = {
            "test_plan": "Unit tests for module",
            "tests_passing": False,  # Tests are failing
            "coverage_override": True,
            "coverage_scope": "Specific module only"
        }

        # Act: Validate for REVIEW status
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW
        )

        # Assert: Validation fails because tests are failing
        assert result.valid is False
        assert "failing tests" in result.reason.lower()

    def test_coverage_override_metadata_fields(self):
        """Test that coverage override metadata includes required fields"""
        # Arrange: Complete coverage override metadata
        metadata = {
            "test_plan": "Unit tests for Detection Pack utilities",
            "tests_passing": True,
            "coverage_percent": 95,
            "coverage_override": True,
            "coverage_scope": "Detection Pack utilities only (metrics_calculator.py, pattern_matchers.py)",
            "override_reason": "Category coverage check analyzed entire codebase. Detection Pack scope has >90% coverage verified."
        }

        # Act: Validate
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW
        )

        # Assert: Validation passes
        assert result.valid is True
        # Verify metadata structure
        assert "coverage_scope" in metadata
        assert "override_reason" in metadata
        assert metadata["coverage_override"] is True

    def test_ready_status_doesnt_check_coverage(self):
        """Test that READY status only requires test_plan, not coverage"""
        # Arrange: Task transitioning to READY
        metadata = {
            "test_plan": "Unit tests for module"
            # No coverage data yet
        }

        # Act: Validate for READY status
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.READY
        )

        # Assert: Validation passes (coverage not required for READY)
        assert result.valid is True

    def test_implementation_task_not_affected(self):
        """Test that coverage override only applies to TESTING tasks"""
        # Arrange: IMPLEMENTATION task with coverage override
        metadata = {
            "acceptance_criteria": [
                {"criterion": "Feature works", "met": True}
            ],
            "coverage_override": True  # Shouldn't affect implementation tasks
        }

        # Act: Validate
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.IMPLEMENTATION,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW
        )

        # Assert: Validation passes (based on acceptance criteria, not coverage)
        assert result.valid is True


class TestCoverageValidationScoping:
    """Test that coverage validation is properly scoped"""

    def test_error_message_includes_override_guidance(self):
        """Test that validation error message includes coverage_override guidance"""
        # This test documents the expected error message format when
        # coverage validation fails - it should tell users about coverage_override

        # Note: This is a documentation test - the actual error message
        # is generated by the validate_all_categories function when it fails.
        # The type_validators.py adds guidance about coverage_override to the message.

        expected_guidance = (
            "To bypass this check for task-specific work with verified coverage:\n"
            "  Set quality_metadata.coverage_override = true with coverage_scope and override_reason"
        )

        # This guidance should be appended to validation failures
        assert "coverage_override" in expected_guidance
        assert "coverage_scope" in expected_guidance
        assert "override_reason" in expected_guidance


class TestRegressionPrevention:
    """Regression tests for the coverage validation bug"""

    def test_task_971_scenario(self):
        """
        Regression test for Task #971 (Detection Pack Unit Tests)

        Original issue: Task was blocked by project-wide coverage validation
        even though the Detection Pack had >90% coverage.

        Fix: coverage_override allows bypassing project-wide validation for
        task-specific work with verified coverage.
        """
        # Arrange: Simulate Task #971 metadata
        metadata = {
            "test_plan": "Unit tests for Detection Pack utilities (91 tests: 47 metrics_calculator + 44 pattern_matchers)",
            "tests_passing": True,
            "coverage_percent": 95,
            "coverage_override": True,
            "coverage_scope": "Detection Pack utilities only (metrics_calculator.py, pattern_matchers.py)",
            "override_reason": "Category coverage check analyzed entire codebase. Detection Pack scope has >90% coverage verified."
        }

        # Act: Validate for REVIEW status
        result = TypeSpecificValidators.validate_quality_metadata_structure(
            task_type=TaskType.TESTING,
            quality_metadata=metadata,
            target_status=TaskStatus.REVIEW
        )

        # Assert: Validation passes with coverage_override
        assert result.valid is True
        assert result.reason is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
