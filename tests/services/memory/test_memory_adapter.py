"""
Tests for Memory File Adapter

Tests the adapter layer in agentpm/core/database/adapters/memory.py
"""

import pytest
import json
from datetime import datetime

from agentpm.core.database.adapters.memory import MemoryFileAdapter
from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus
)


class TestMemoryFileAdapter:
    """Test MemoryFileAdapter conversions."""

    def test_to_db_minimal(self):
        """Test converting minimal memory file to database format."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules\n\nContent...",
            generated_by="memory-generator",
            generated_at="2025-10-21T10:00:00"
        )

        data = MemoryFileAdapter.to_db(memory)

        assert data['project_id'] == 1
        assert data['file_type'] == "rules"
        assert data['file_path'] == ".claude/RULES.md"
        assert data['content'] == "# Rules\n\nContent..."
        assert data['generated_by'] == "memory-generator"
        assert data['generated_at'] == "2025-10-21T10:00:00"
        assert data['source_tables'] == "[]"  # JSON encoded empty list
        assert data['validation_status'] == "pending"

    def test_to_db_with_all_fields(self):
        """Test converting full memory file to database format."""
        memory = MemoryFile(
            id=1,
            project_id=1,
            session_id=100,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            file_hash="abc123",
            content="# Rules",
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

        data = MemoryFileAdapter.to_db(memory)

        assert data['id'] == 1
        assert data['session_id'] == 100
        assert data['file_hash'] == "abc123"
        assert data['source_tables'] == '["rules", "projects"]'
        assert data['confidence_score'] == 0.95
        assert data['completeness_score'] == 0.90
        assert data['validation_status'] == "validated"
        assert data['generation_duration_ms'] == 150

    def test_from_db_minimal(self):
        """Test converting minimal database row to memory file."""
        row = {
            'id': 1,
            'project_id': 1,
            'session_id': None,
            'file_type': 'rules',
            'file_path': '.claude/RULES.md',
            'file_hash': None,
            'content': '# Rules',
            'source_tables': '[]',
            'template_version': '1.0.0',
            'confidence_score': 1.0,
            'completeness_score': 1.0,
            'validation_status': 'pending',
            'generated_by': 'memory-generator',
            'generation_duration_ms': None,
            'generated_at': '2025-10-21T10:00:00',
            'validated_at': None,
            'expires_at': None,
            'created_at': '2025-10-21T10:00:00',
            'updated_at': '2025-10-21T10:00:00'
        }

        memory = MemoryFileAdapter.from_db(row)

        assert memory.id == 1
        assert memory.project_id == 1
        assert memory.session_id is None
        assert memory.file_type == MemoryFileType.RULES
        assert memory.file_path == '.claude/RULES.md'
        assert memory.content == '# Rules'
        assert memory.source_tables == []
        assert memory.validation_status == ValidationStatus.PENDING

    def test_from_db_with_all_fields(self):
        """Test converting full database row to memory file."""
        row = {
            'id': 1,
            'project_id': 1,
            'session_id': 100,
            'file_type': 'rules',
            'file_path': '.claude/RULES.md',
            'file_hash': 'abc123',
            'content': '# Rules',
            'source_tables': '["rules", "projects"]',
            'template_version': '1.0.0',
            'confidence_score': 0.95,
            'completeness_score': 0.90,
            'validation_status': 'validated',
            'generated_by': 'memory-generator',
            'generation_duration_ms': 150,
            'generated_at': '2025-10-21T10:00:00',
            'validated_at': '2025-10-21T10:00:05',
            'expires_at': '2025-10-22T10:00:00',
            'created_at': '2025-10-21T10:00:00',
            'updated_at': '2025-10-21T10:00:05'
        }

        memory = MemoryFileAdapter.from_db(row)

        assert memory.id == 1
        assert memory.session_id == 100
        assert memory.file_hash == 'abc123'
        assert memory.source_tables == ["rules", "projects"]
        assert memory.confidence_score == 0.95
        assert memory.completeness_score == 0.90
        assert memory.validation_status == ValidationStatus.VALIDATED
        assert memory.generation_duration_ms == 150

    def test_roundtrip_conversion(self):
        """Test converting to DB and back preserves data."""
        original = MemoryFile(
            project_id=1,
            session_id=100,
            file_type=MemoryFileType.WORKFLOW,
            file_path=".claude/WORKFLOW.md",
            file_hash="abc123",
            content="# Workflow",
            source_tables=["work_items", "tasks"],
            confidence_score=0.95,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )

        # Convert to DB format
        db_data = MemoryFileAdapter.to_db(original)

        # Add id (simulating database insert)
        db_data['id'] = 1
        db_data['created_at'] = "2025-10-21T10:00:00"
        db_data['updated_at'] = "2025-10-21T10:00:00"

        # Convert back to model
        restored = MemoryFileAdapter.from_db(db_data)

        # Verify critical fields match
        assert restored.project_id == original.project_id
        assert restored.session_id == original.session_id
        assert restored.file_type == original.file_type
        assert restored.file_path == original.file_path
        assert restored.content == original.content
        assert restored.source_tables == original.source_tables
        assert restored.confidence_score == original.confidence_score
        assert restored.validation_status == original.validation_status

    def test_to_db_partial_with_enum(self):
        """Test partial conversion with enum values."""
        updates = {
            'validation_status': ValidationStatus.VALIDATED,
            'file_type': MemoryFileType.RULES
        }

        db_updates = MemoryFileAdapter.to_db_partial(updates)

        assert db_updates['validation_status'] == 'validated'
        assert db_updates['file_type'] == 'rules'

    def test_to_db_partial_with_list(self):
        """Test partial conversion with list values."""
        updates = {
            'source_tables': ['rules', 'projects', 'agents']
        }

        db_updates = MemoryFileAdapter.to_db_partial(updates)

        assert db_updates['source_tables'] == '["rules", "projects", "agents"]'

    def test_to_db_partial_with_datetime(self):
        """Test partial conversion with datetime values."""
        dt = datetime(2025, 10, 21, 10, 0, 0)
        updates = {
            'generated_at': dt,
            'validated_at': dt.isoformat()
        }

        db_updates = MemoryFileAdapter.to_db_partial(updates)

        assert db_updates['generated_at'] == '2025-10-21T10:00:00'
        assert db_updates['validated_at'] == '2025-10-21T10:00:00'

    def test_to_db_partial_with_none(self):
        """Test partial conversion with None values."""
        updates = {
            'session_id': None,
            'file_hash': None,
            'validated_at': None
        }

        db_updates = MemoryFileAdapter.to_db_partial(updates)

        assert db_updates['session_id'] is None
        assert db_updates['file_hash'] is None
        assert db_updates['validated_at'] is None

    def test_to_db_partial_mixed_types(self):
        """Test partial conversion with mixed types."""
        updates = {
            'validation_status': ValidationStatus.STALE,
            'source_tables': ['rules'],
            'confidence_score': 0.85,
            'validated_at': None,
            'generation_duration_ms': 200
        }

        db_updates = MemoryFileAdapter.to_db_partial(updates)

        assert db_updates['validation_status'] == 'stale'
        assert db_updates['source_tables'] == '["rules"]'
        assert db_updates['confidence_score'] == 0.85
        assert db_updates['validated_at'] is None
        assert db_updates['generation_duration_ms'] == 200
