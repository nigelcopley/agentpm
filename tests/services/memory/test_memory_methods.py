"""
Tests for Memory File Methods

Tests the database methods in agentpm/core/database/methods/memory_methods.py

These are integration tests that use a real SQLite database.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus
)
from agentpm.core.database.methods import memory_methods


@pytest.fixture
def db(tmp_path):
    """Create a test database with memory_files table."""
    db_path = tmp_path / "test.db"
    db = DatabaseService(str(db_path))

    # Create required tables
    with db.connect() as conn:
        # Create projects table (required for foreign key)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                path TEXT NOT NULL,
                tech_stack TEXT DEFAULT '[]',
                detected_frameworks TEXT DEFAULT '[]',
                status TEXT DEFAULT 'initiated',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Create sessions table (optional for foreign key)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                project_id INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Create memory_files table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                session_id INTEGER,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                content TEXT NOT NULL,
                source_tables TEXT NOT NULL DEFAULT '[]',
                template_version TEXT NOT NULL DEFAULT '1.0.0',
                confidence_score REAL DEFAULT 1.0,
                completeness_score REAL DEFAULT 1.0,
                validation_status TEXT NOT NULL DEFAULT 'pending',
                generated_by TEXT NOT NULL,
                generation_duration_ms INTEGER,
                generated_at TEXT NOT NULL,
                validated_at TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
            )
        """)

        # Insert test project
        conn.execute("""
            INSERT INTO projects (id, name, path, created_at, updated_at)
            VALUES (1, 'Test Project', '/test/path', '2025-10-21T10:00:00', '2025-10-21T10:00:00')
        """)

        # Insert test project 2 (for multi-project tests)
        conn.execute("""
            INSERT INTO projects (id, name, path, created_at, updated_at)
            VALUES (2, 'Test Project 2', '/test/path2', '2025-10-21T10:00:00', '2025-10-21T10:00:00')
        """)

        # Insert test session
        conn.execute("""
            INSERT INTO sessions (id, session_id, project_id, created_at)
            VALUES (100, 'test-session-100', 1, '2025-10-21T10:00:00')
        """)

        conn.commit()

    yield db


class TestCreateMemoryFile:
    """Test create_memory_file()."""

    def test_create_minimal(self, db):
        """Test creating memory file with minimal fields."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )

        created = memory_methods.create_memory_file(db, memory)

        assert created.id == 1
        assert created.project_id == 1
        assert created.file_type == MemoryFileType.RULES
        assert created.created_at is not None
        assert created.updated_at is not None

    def test_create_with_all_fields(self, db):
        """Test creating memory file with all fields."""
        memory = MemoryFile(
            project_id=1,
            session_id=100,
            file_type=MemoryFileType.WORKFLOW,
            file_path=".claude/WORKFLOW.md",
            file_hash="abc123",
            content="# Workflow",
            source_tables=["work_items", "tasks"],
            template_version="1.0.0",
            confidence_score=0.95,
            completeness_score=0.90,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="memory-generator",
            generation_duration_ms=150,
            generated_at="2025-10-21T10:00:00",
            validated_at="2025-10-21T10:00:05",
            expires_at="2025-10-22T10:00:00"
        )

        created = memory_methods.create_memory_file(db, memory)

        assert created.id == 1
        assert created.session_id == 100
        assert created.file_hash == "abc123"
        assert created.source_tables == ["work_items", "tasks"]
        assert created.confidence_score == 0.95
        assert created.validation_status == ValidationStatus.VALIDATED


class TestGetMemoryFile:
    """Test get_memory_file()."""

    def test_get_existing(self, db):
        """Test getting existing memory file."""
        # Create a memory file
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        created = memory_methods.create_memory_file(db, memory)

        # Get it back
        retrieved = memory_methods.get_memory_file(db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.project_id == 1
        assert retrieved.file_type == MemoryFileType.RULES

    def test_get_nonexistent(self, db):
        """Test getting non-existent memory file returns None."""
        result = memory_methods.get_memory_file(db, 999)
        assert result is None


class TestGetMemoryFileByType:
    """Test get_memory_file_by_type()."""

    def test_get_by_type(self, db):
        """Test getting memory file by project and type."""
        # Create multiple memory files
        for file_type in [MemoryFileType.RULES, MemoryFileType.WORKFLOW]:
            memory = MemoryFile(
                project_id=1,
                file_type=file_type,
                file_path=f".claude/{file_type.value.upper()}.md",
                content=f"# {file_type.value}",
                generated_by="test",
                generated_at="2025-10-21T10:00:00"
            )
            memory_methods.create_memory_file(db, memory)

        # Get RULES file
        rules = memory_methods.get_memory_file_by_type(db, 1, MemoryFileType.RULES)
        assert rules is not None
        assert rules.file_type == MemoryFileType.RULES

        # Get WORKFLOW file
        workflow = memory_methods.get_memory_file_by_type(db, 1, MemoryFileType.WORKFLOW)
        assert workflow is not None
        assert workflow.file_type == MemoryFileType.WORKFLOW

    def test_get_by_type_wrong_project(self, db):
        """Test getting memory file with wrong project returns None."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        memory_methods.create_memory_file(db, memory)

        result = memory_methods.get_memory_file_by_type(db, 999, MemoryFileType.RULES)
        assert result is None


class TestListMemoryFiles:
    """Test list_memory_files()."""

    def test_list_all(self, db):
        """Test listing all memory files."""
        # Create 3 memory files
        for i, file_type in enumerate([MemoryFileType.RULES, MemoryFileType.WORKFLOW, MemoryFileType.AGENTS]):
            memory = MemoryFile(
                project_id=1,
                file_type=file_type,
                file_path=f".claude/{file_type.value.upper()}.md",
                content=f"# {file_type.value}",
                generated_by="test",
                generated_at=f"2025-10-21T10:0{i}:00"
            )
            memory_methods.create_memory_file(db, memory)

        files = memory_methods.list_memory_files(db)
        assert len(files) == 3

    def test_list_by_project(self, db):
        """Test listing memory files filtered by project."""
        # Create files for different projects
        for project_id in [1, 2]:
            memory = MemoryFile(
                project_id=project_id,
                file_type=MemoryFileType.RULES,
                file_path=".claude/RULES.md",
                content="# Rules",
                generated_by="test",
                generated_at="2025-10-21T10:00:00"
            )
            memory_methods.create_memory_file(db, memory)

        files = memory_methods.list_memory_files(db, project_id=1)
        assert len(files) == 1
        assert files[0].project_id == 1

    def test_list_by_validation_status(self, db):
        """Test listing memory files filtered by validation status."""
        # Create files with different statuses
        for status in [ValidationStatus.VALIDATED, ValidationStatus.STALE, ValidationStatus.PENDING]:
            memory = MemoryFile(
                project_id=1,
                file_type=MemoryFileType.RULES if status == ValidationStatus.VALIDATED else MemoryFileType.WORKFLOW if status == ValidationStatus.STALE else MemoryFileType.AGENTS,
                file_path=f".claude/{status.value}.md",
                content=f"# {status.value}",
                validation_status=status,
                generated_by="test",
                generated_at="2025-10-21T10:00:00"
            )
            memory_methods.create_memory_file(db, memory)

        validated = memory_methods.list_memory_files(db, validation_status=ValidationStatus.VALIDATED)
        assert len(validated) == 1
        assert validated[0].validation_status == ValidationStatus.VALIDATED

    def test_list_with_limit(self, db):
        """Test listing memory files with limit."""
        # Create 5 files
        for i in range(5):
            memory = MemoryFile(
                project_id=1,
                file_type=list(MemoryFileType)[i],
                file_path=f".claude/FILE{i}.md",
                content=f"# File {i}",
                generated_by="test",
                generated_at=f"2025-10-21T10:0{i}:00"
            )
            memory_methods.create_memory_file(db, memory)

        files = memory_methods.list_memory_files(db, limit=2)
        assert len(files) == 2


class TestGetStaleMemoryFiles:
    """Test get_stale_memory_files()."""

    def test_get_stale_files(self, db):
        """Test getting only stale memory files."""
        # Create mix of validated and stale files
        for status in [ValidationStatus.VALIDATED, ValidationStatus.STALE]:
            memory = MemoryFile(
                project_id=1,
                file_type=MemoryFileType.RULES if status == ValidationStatus.VALIDATED else MemoryFileType.WORKFLOW,
                file_path=f".claude/{status.value}.md",
                content=f"# {status.value}",
                validation_status=status,
                generated_by="test",
                generated_at="2025-10-21T10:00:00"
            )
            memory_methods.create_memory_file(db, memory)

        stale = memory_methods.get_stale_memory_files(db)
        assert len(stale) == 1
        assert stale[0].validation_status == ValidationStatus.STALE


class TestUpdateMemoryFile:
    """Test update_memory_file()."""

    def test_update_content(self, db):
        """Test updating memory file content."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules v1",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        created = memory_methods.create_memory_file(db, memory)

        updates = {
            'content': '# Rules v2 - Updated',
            'file_hash': 'new_hash_123'
        }
        updated = memory_methods.update_memory_file(db, created.id, updates)

        assert updated is not None
        assert updated.content == '# Rules v2 - Updated'
        assert updated.file_hash == 'new_hash_123'

    def test_update_validation_status(self, db):
        """Test updating validation status."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.PENDING
        )
        created = memory_methods.create_memory_file(db, memory)

        updates = {
            'validation_status': ValidationStatus.VALIDATED,
            'validated_at': '2025-10-21T10:05:00'
        }
        updated = memory_methods.update_memory_file(db, created.id, updates)

        assert updated.validation_status == ValidationStatus.VALIDATED
        assert updated.validated_at == '2025-10-21T10:05:00'

    def test_update_nonexistent(self, db):
        """Test updating non-existent file returns None."""
        result = memory_methods.update_memory_file(db, 999, {'content': 'test'})
        assert result is None

    def test_update_sets_updated_at(self, db):
        """Test update automatically sets updated_at timestamp."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        created = memory_methods.create_memory_file(db, memory)
        original_updated_at = created.updated_at

        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)

        updates = {'content': 'Updated content'}
        updated = memory_methods.update_memory_file(db, created.id, updates)

        assert updated.updated_at != original_updated_at


class TestMarkValidated:
    """Test mark_validated()."""

    def test_mark_validated_with_timestamp(self, db):
        """Test marking file as validated with specific timestamp."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.PENDING
        )
        created = memory_methods.create_memory_file(db, memory)

        validated = memory_methods.mark_validated(db, created.id, "2025-10-21T10:05:00")

        assert validated.validation_status == ValidationStatus.VALIDATED
        assert validated.validated_at == "2025-10-21T10:05:00"

    def test_mark_validated_auto_timestamp(self, db):
        """Test marking file as validated with auto timestamp."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.PENDING
        )
        created = memory_methods.create_memory_file(db, memory)

        validated = memory_methods.mark_validated(db, created.id)

        assert validated.validation_status == ValidationStatus.VALIDATED
        assert validated.validated_at is not None


class TestMarkStale:
    """Test mark_stale()."""

    def test_mark_stale(self, db):
        """Test marking file as stale."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00",
            validation_status=ValidationStatus.VALIDATED
        )
        created = memory_methods.create_memory_file(db, memory)

        stale = memory_methods.mark_stale(db, created.id)

        assert stale.validation_status == ValidationStatus.STALE


class TestDeleteMemoryFile:
    """Test delete_memory_file()."""

    def test_delete_existing(self, db):
        """Test deleting existing memory file."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at="2025-10-21T10:00:00"
        )
        created = memory_methods.create_memory_file(db, memory)

        result = memory_methods.delete_memory_file(db, created.id)
        assert result is True

        # Verify it's gone
        retrieved = memory_methods.get_memory_file(db, created.id)
        assert retrieved is None

    def test_delete_nonexistent(self, db):
        """Test deleting non-existent file returns False."""
        result = memory_methods.delete_memory_file(db, 999)
        assert result is False


class TestIsMemoryFileCurrent:
    """Test is_memory_file_current()."""

    def test_current_file(self, db):
        """Test current file returns True."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at=datetime.now().isoformat(),
            validation_status=ValidationStatus.VALIDATED
        )
        memory_methods.create_memory_file(db, memory)

        result = memory_methods.is_memory_file_current(db, 1, MemoryFileType.RULES, max_age_hours=24)
        assert result is True

    def test_stale_file(self, db):
        """Test stale file returns False."""
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at=datetime.now().isoformat(),
            validation_status=ValidationStatus.STALE
        )
        memory_methods.create_memory_file(db, memory)

        result = memory_methods.is_memory_file_current(db, 1, MemoryFileType.RULES)
        assert result is False

    def test_expired_file(self, db):
        """Test expired file returns False."""
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at=datetime.now().isoformat(),
            expires_at=past,
            validation_status=ValidationStatus.VALIDATED
        )
        memory_methods.create_memory_file(db, memory)

        result = memory_methods.is_memory_file_current(db, 1, MemoryFileType.RULES)
        assert result is False

    def test_old_file(self, db):
        """Test old file returns False."""
        old_date = (datetime.now() - timedelta(hours=48)).isoformat()
        memory = MemoryFile(
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="# Rules",
            generated_by="test",
            generated_at=old_date,
            validation_status=ValidationStatus.VALIDATED
        )
        memory_methods.create_memory_file(db, memory)

        result = memory_methods.is_memory_file_current(db, 1, MemoryFileType.RULES, max_age_hours=24)
        assert result is False

    def test_nonexistent_file(self, db):
        """Test non-existent file returns False."""
        result = memory_methods.is_memory_file_current(db, 1, MemoryFileType.RULES)
        assert result is False
