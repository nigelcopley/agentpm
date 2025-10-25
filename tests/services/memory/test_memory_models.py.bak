"""
Tests for Memory File Models

Tests the Pydantic models in agentpm/core/database/models/memory.py
"""

import pytest
from datetime import datetime, timedelta

from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus
)


class TestMemoryFileType:
    """Test MemoryFileType enum."""

    def test_all_file_types(self):
        """Test all memory file types are defined."""
        assert MemoryFileType.RULES.value == "rules"
        assert MemoryFileType.PRINCIPLES.value == "principles"
        assert MemoryFileType.WORKFLOW.value == "workflow"
        assert MemoryFileType.AGENTS.value == "agents"
        assert MemoryFileType.CONTEXT.value == "context"
        assert MemoryFileType.PROJECT.value == "project"
        assert MemoryFileType.IDEAS.value == "ideas"

    def test_enum_count(self):
        """Test we have exactly 7 memory file types."""
        assert len(list(MemoryFileType)) == 7


class TestValidationStatus:
    """Test ValidationStatus enum."""

    def test_all_statuses(self):
        """Test all validation statuses are defined."""
        assert ValidationStatus.PENDING.value == "pending"
        assert ValidationStatus.VALIDATED.value == "validated"
        assert ValidationStatus.STALE.value == "stale"
        assert ValidationStatus.FAILED.value == "failed"


class TestMemoryFile:
    """Test MemoryFile model."""

    def test_create_minimal(self):
        """Test creating memory file with minimal required fields."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules\n\nContent...",
            generated_by="memory-generator",
            generated_at="2025-10-21T10:00:00"
        )

        assert memory.project_id == 1
        assert memory.file_type == MemoryFileType.RULES
        assert memory.file_path == ".claude/RULES.md"
        assert memory.content == "# Rules\n\nContent..."
        assert memory.generated_by == "memory-generator"
        assert memory.generated_at == "2025-10-21T10:00:00"

    def test_create_with_all_fields(self):
        """Test creating memory file with all fields."""
        memory = MemoryFile(
            id=1,
            project_id=1,
            session_id=100,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            file_hash="abc123",
            content="# Rules\n\nContent...",
            source_tables=["rules", "projects"],
            template_version="1.0.0",
            confidence_score=0.95,
            completeness_score=0.90,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="memory-generator",
            generation_duration_ms=150,
            generated_at="2025-10-21T10:00:00",
            validated_at="2025-10-21T10:00:05",
            expires_at="2025-10-22T10:00:00",
            created_at="2025-10-21T10:00:00",
            updated_at="2025-10-21T10:00:05"
        )

        assert memory.id == 1
        assert memory.session_id == 100
        assert memory.file_hash == "abc123"
        assert memory.source_tables == ["rules", "projects"]
        assert memory.confidence_score == 0.95
        assert memory.completeness_score == 0.90
        assert memory.validation_status == ValidationStatus.VALIDATED

    def test_default_values(self):
        """Test default values are applied correctly."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )

        assert memory.id is None
        assert memory.session_id is None
        assert memory.file_hash is None
        assert memory.source_tables == []
        assert memory.template_version == "1.0.0"
        assert memory.confidence_score == 1.0
        assert memory.completeness_score == 1.0
        assert memory.validation_status == ValidationStatus.PENDING

    def test_confidence_score_validation(self):
        """Test confidence score must be between 0.0 and 1.0."""
        with pytest.raises(ValueError):
            MemoryFile(
                project_id=1,
                file_type=MemoryFileType.RULES,
                file_path=".claude/RULES.md",
                content="# Rules",
                generated_by="test",
                generated_at="2025-10-21T10:00:00",
                confidence_score=1.5  # Invalid
            )

        with pytest.raises(ValueError):
            MemoryFile(
                project_id=1,
                file_type=MemoryFileType.RULES,
                file_path=".claude/RULES.md",
                content="# Rules",
                generated_by="test",
                generated_at="2025-10-21T10:00:00",
                confidence_score=-0.1  # Invalid
            )

    def test_is_stale_property(self):
        """Test is_stale property."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.STALE
        )
        assert memory.is_stale is True

        memory.validation_status = ValidationStatus.VALIDATED
        assert memory.is_stale is False

    def test_is_validated_property(self):
        """Test is_validated property."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.VALIDATED
        )
        assert memory.is_validated is True

        memory.validation_status = ValidationStatus.PENDING
        assert memory.is_validated is False

    def test_is_expired_property_with_no_expiry(self):
        """Test is_expired returns False when no expires_at set."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        assert memory.is_expired is False

    def test_is_expired_property_with_future_expiry(self):
        """Test is_expired returns False for future expiry."""
        future = (datetime.now() + timedelta(hours=24)).isoformat()
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            expires_at=future
        )
        assert memory.is_expired is False

    def test_is_expired_property_with_past_expiry(self):
        """Test is_expired returns True for past expiry."""
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            expires_at=past
        )
        assert memory.is_expired is True

    def test_config_from_attributes(self):
        """Test Pydantic config allows ORM mode."""
        # This is implicitly tested by the adapter tests
        assert MemoryFile.model_config['from_attributes'] is True
