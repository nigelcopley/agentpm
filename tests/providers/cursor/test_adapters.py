"""
Unit tests for Cursor provider adapters (Layer 2).

Tests DB ↔ Model conversion including:
- ProviderInstallationAdapter
- CursorMemoryAdapter
- ProviderFileAdapter
- JSON serialization
- Date/path conversions

Coverage target: 95%
"""

import pytest
import json
from datetime import datetime

from agentpm.core.database.adapters.provider import (
    ProviderInstallationAdapter,
    CursorMemoryAdapter,
    ProviderFileAdapter,
)
from agentpm.core.database.models.provider import (
    ProviderInstallation,
    CursorMemory,
    ProviderType,
    InstallationStatus,
)


class TestProviderInstallationAdapter:
    """Test ProviderInstallationAdapter."""

    def test_to_db_conversion(self):
        """
        GIVEN ProviderInstallation model
        WHEN calling to_db()
        THEN database row dict is returned with JSON-serialized fields
        """
        # Arrange
        installation = ProviderInstallation(
            id=1,
            project_id=10,
            provider_type=ProviderType.CURSOR,
            provider_version="1.0.0",
            install_path="/path/.cursor",
            status=InstallationStatus.INSTALLED,
            config={"test": "value", "enabled": True},
            installed_files=["rules/test.mdc", ".cursorignore"],
            file_hashes={"rules/test.mdc": "abc123", ".cursorignore": "def456"},
            installed_at=datetime(2025, 10, 20, 10, 0, 0),
            updated_at=datetime(2025, 10, 20, 11, 0, 0),
            last_verified_at=datetime(2025, 10, 20, 12, 0, 0),
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(installation)

        # Assert
        assert db_row["project_id"] == 10
        assert db_row["provider_type"] == "cursor"
        assert db_row["provider_version"] == "1.0.0"
        assert db_row["install_path"] == "/path/.cursor"
        assert db_row["status"] == "installed"

        # Check JSON serialization
        assert isinstance(db_row["config"], str)
        config = json.loads(db_row["config"])
        assert config["test"] == "value"
        assert config["enabled"] is True

        assert isinstance(db_row["installed_files"], str)
        files = json.loads(db_row["installed_files"])
        assert len(files) == 2
        assert "rules/test.mdc" in files

        assert isinstance(db_row["file_hashes"], str)
        hashes = json.loads(db_row["file_hashes"])
        assert hashes["rules/test.mdc"] == "abc123"

        # Check datetime serialization
        assert db_row["installed_at"] == "2025-10-20T10:00:00"
        assert db_row["updated_at"] == "2025-10-20T11:00:00"
        assert db_row["last_verified_at"] == "2025-10-20T12:00:00"

    def test_to_db_with_null_last_verified(self):
        """
        GIVEN ProviderInstallation with None last_verified_at
        WHEN calling to_db()
        THEN last_verified_at is None in database row
        """
        # Arrange
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
            last_verified_at=None,
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(installation)

        # Assert
        assert db_row["last_verified_at"] is None

    def test_to_db_with_empty_collections(self):
        """
        GIVEN ProviderInstallation with empty lists/dicts
        WHEN calling to_db()
        THEN empty JSON arrays/objects are created
        """
        # Arrange
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
            config={},
            installed_files=[],
            file_hashes={},
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(installation)

        # Assert
        assert db_row["config"] == "{}"
        assert db_row["installed_files"] == "[]"
        assert db_row["file_hashes"] == "{}"

    def test_from_db_conversion(self):
        """
        GIVEN database row dict
        WHEN calling from_db()
        THEN ProviderInstallation model is returned with deserialized fields
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 10,
            "provider_type": "cursor",
            "provider_version": "1.0.0",
            "install_path": "/path/.cursor",
            "status": "installed",
            "config": '{"test": "value", "enabled": true}',
            "installed_files": '["rules/test.mdc", ".cursorignore"]',
            "file_hashes": '{"rules/test.mdc": "abc123"}',
            "installed_at": "2025-10-20T10:00:00",
            "updated_at": "2025-10-20T11:00:00",
            "last_verified_at": "2025-10-20T12:00:00",
        }

        # Act
        installation = ProviderInstallationAdapter.from_db(db_row)

        # Assert
        assert installation.id == 1
        assert installation.project_id == 10
        assert installation.provider_type == ProviderType.CURSOR
        assert installation.provider_version == "1.0.0"
        assert installation.install_path == "/path/.cursor"
        assert installation.status == InstallationStatus.INSTALLED

        # Check deserialized collections
        assert installation.config == {"test": "value", "enabled": True}
        assert installation.installed_files == ["rules/test.mdc", ".cursorignore"]
        assert installation.file_hashes == {"rules/test.mdc": "abc123"}

        # Check deserialized datetimes
        assert installation.installed_at == datetime(2025, 10, 20, 10, 0, 0)
        assert installation.updated_at == datetime(2025, 10, 20, 11, 0, 0)
        assert installation.last_verified_at == datetime(2025, 10, 20, 12, 0, 0)

    def test_from_db_with_null_last_verified(self):
        """
        GIVEN database row with None last_verified_at
        WHEN calling from_db()
        THEN model has None last_verified_at
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 1,
            "provider_type": "cursor",
            "provider_version": "1.0.0",
            "install_path": "/path/.cursor",
            "status": "installed",
            "config": "{}",
            "installed_files": "[]",
            "file_hashes": "{}",
            "installed_at": "2025-10-20T10:00:00",
            "updated_at": "2025-10-20T10:00:00",
            "last_verified_at": None,
        }

        # Act
        installation = ProviderInstallationAdapter.from_db(db_row)

        # Assert
        assert installation.last_verified_at is None

    def test_from_db_with_empty_json_strings(self):
        """
        GIVEN database row with empty JSON strings
        WHEN calling from_db()
        THEN model has empty collections
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 1,
            "provider_type": "cursor",
            "provider_version": "1.0.0",
            "install_path": "/path/.cursor",
            "status": "installed",
            "config": "",
            "installed_files": "",
            "file_hashes": "",
            "installed_at": "2025-10-20T10:00:00",
            "updated_at": "2025-10-20T10:00:00",
        }

        # Act
        installation = ProviderInstallationAdapter.from_db(db_row)

        # Assert
        assert installation.config == {}
        assert installation.installed_files == []
        assert installation.file_hashes == {}

    def test_round_trip_conversion(self):
        """
        GIVEN ProviderInstallation model
        WHEN converting to_db() then from_db()
        THEN data is preserved
        """
        # Arrange
        original = ProviderInstallation(
            id=1,
            project_id=10,
            provider_type=ProviderType.CURSOR,
            provider_version="1.2.3",
            install_path="/test/.cursor",
            status=InstallationStatus.PARTIAL,
            config={"key": "value"},
            installed_files=["file1.mdc", "file2.mdc"],
            file_hashes={"file1.mdc": "hash1"},
            installed_at=datetime(2025, 10, 20, 10, 0, 0),
            updated_at=datetime(2025, 10, 20, 11, 0, 0),
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(original)
        reconstructed = ProviderInstallationAdapter.from_db({**db_row, "id": 1})

        # Assert
        assert reconstructed.project_id == original.project_id
        assert reconstructed.provider_type == original.provider_type
        assert reconstructed.provider_version == original.provider_version
        assert reconstructed.install_path == original.install_path
        assert reconstructed.status == original.status
        assert reconstructed.config == original.config
        assert reconstructed.installed_files == original.installed_files
        assert reconstructed.file_hashes == original.file_hashes


class TestCursorMemoryAdapter:
    """Test CursorMemoryAdapter."""

    def test_to_db_conversion(self):
        """
        GIVEN CursorMemory model
        WHEN calling to_db()
        THEN database row dict is returned
        """
        # Arrange
        memory = CursorMemory(
            id=1,
            project_id=10,
            name="test-memory",
            description="Test memory",
            category="testing",
            content="# Test\n\nContent here.",
            tags=["test", "demo"],
            file_path="test-memory.md",
            file_hash="abc123",
            source_learning_id=5,
            last_synced_at=datetime(2025, 10, 20, 10, 0, 0),
            created_at=datetime(2025, 10, 20, 9, 0, 0),
            updated_at=datetime(2025, 10, 20, 11, 0, 0),
        )

        # Act
        db_row = CursorMemoryAdapter.to_db(memory)

        # Assert
        assert db_row["project_id"] == 10
        assert db_row["name"] == "test-memory"
        assert db_row["description"] == "Test memory"
        assert db_row["category"] == "testing"
        assert db_row["content"] == "# Test\n\nContent here."
        assert db_row["file_path"] == "test-memory.md"
        assert db_row["file_hash"] == "abc123"
        assert db_row["source_learning_id"] == 5

        # Check JSON serialization
        assert isinstance(db_row["tags"], str)
        tags = json.loads(db_row["tags"])
        assert tags == ["test", "demo"]

        # Check datetime serialization
        assert db_row["last_synced_at"] == "2025-10-20T10:00:00"
        assert db_row["created_at"] == "2025-10-20T09:00:00"
        assert db_row["updated_at"] == "2025-10-20T11:00:00"

    def test_to_db_with_null_optional_fields(self):
        """
        GIVEN CursorMemory with None optional fields
        WHEN calling to_db()
        THEN None values are preserved
        """
        # Arrange
        memory = CursorMemory(
            project_id=1,
            name="test",
            description="Test",
            content="Content",
            file_path="test.md",
            file_hash=None,
            source_learning_id=None,
            last_synced_at=None,
        )

        # Act
        db_row = CursorMemoryAdapter.to_db(memory)

        # Assert
        assert db_row["file_hash"] is None
        assert db_row["source_learning_id"] is None
        assert db_row["last_synced_at"] is None

    def test_to_db_with_empty_tags(self):
        """
        GIVEN CursorMemory with empty tags
        WHEN calling to_db()
        THEN empty JSON array is created
        """
        # Arrange
        memory = CursorMemory(
            project_id=1,
            name="test",
            description="Test",
            content="Content",
            file_path="test.md",
            tags=[],
        )

        # Act
        db_row = CursorMemoryAdapter.to_db(memory)

        # Assert
        assert db_row["tags"] == "[]"

    def test_from_db_conversion(self):
        """
        GIVEN database row dict
        WHEN calling from_db()
        THEN CursorMemory model is returned
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 10,
            "name": "test-memory",
            "description": "Test memory",
            "category": "testing",
            "content": "# Test\n\nContent",
            "tags": '["test", "demo"]',
            "file_path": "test.md",
            "file_hash": "abc123",
            "source_learning_id": 5,
            "last_synced_at": "2025-10-20T10:00:00",
            "created_at": "2025-10-20T09:00:00",
            "updated_at": "2025-10-20T11:00:00",
        }

        # Act
        memory = CursorMemoryAdapter.from_db(db_row)

        # Assert
        assert memory.id == 1
        assert memory.project_id == 10
        assert memory.name == "test-memory"
        assert memory.description == "Test memory"
        assert memory.category == "testing"
        assert memory.content == "# Test\n\nContent"
        assert memory.tags == ["test", "demo"]
        assert memory.file_path == "test.md"
        assert memory.file_hash == "abc123"
        assert memory.source_learning_id == 5
        assert memory.last_synced_at == datetime(2025, 10, 20, 10, 0, 0)
        assert memory.created_at == datetime(2025, 10, 20, 9, 0, 0)
        assert memory.updated_at == datetime(2025, 10, 20, 11, 0, 0)

    def test_from_db_with_null_optional_fields(self):
        """
        GIVEN database row with None optional fields
        WHEN calling from_db()
        THEN model has None values
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 1,
            "name": "test",
            "description": "Test",
            "category": "general",
            "content": "Content",
            "tags": "[]",
            "file_path": "test.md",
            "file_hash": None,
            "source_learning_id": None,
            "last_synced_at": None,
            "created_at": "2025-10-20T10:00:00",
            "updated_at": "2025-10-20T10:00:00",
        }

        # Act
        memory = CursorMemoryAdapter.from_db(db_row)

        # Assert
        assert memory.file_hash is None
        assert memory.source_learning_id is None
        assert memory.last_synced_at is None

    def test_from_db_with_empty_tags_string(self):
        """
        GIVEN database row with empty tags string
        WHEN calling from_db()
        THEN model has empty list
        """
        # Arrange
        db_row = {
            "id": 1,
            "project_id": 1,
            "name": "test",
            "description": "Test",
            "category": "general",
            "content": "Content",
            "tags": "",
            "file_path": "test.md",
            "created_at": "2025-10-20T10:00:00",
            "updated_at": "2025-10-20T10:00:00",
        }

        # Act
        memory = CursorMemoryAdapter.from_db(db_row)

        # Assert
        assert memory.tags == []

    def test_round_trip_conversion(self):
        """
        GIVEN CursorMemory model
        WHEN converting to_db() then from_db()
        THEN data is preserved
        """
        # Arrange
        original = CursorMemory(
            id=1,
            project_id=10,
            name="memory-1",
            description="Memory 1",
            category="tech",
            content="Content here",
            tags=["tag1", "tag2"],
            file_path="memory-1.md",
            file_hash="hash123",
            source_learning_id=5,
            last_synced_at=datetime(2025, 10, 20, 10, 0, 0),
            created_at=datetime(2025, 10, 20, 9, 0, 0),
            updated_at=datetime(2025, 10, 20, 11, 0, 0),
        )

        # Act
        db_row = CursorMemoryAdapter.to_db(original)
        reconstructed = CursorMemoryAdapter.from_db({**db_row, "id": 1})

        # Assert
        assert reconstructed.project_id == original.project_id
        assert reconstructed.name == original.name
        assert reconstructed.description == original.description
        assert reconstructed.category == original.category
        assert reconstructed.content == original.content
        assert reconstructed.tags == original.tags
        assert reconstructed.file_path == original.file_path
        assert reconstructed.file_hash == original.file_hash
        assert reconstructed.source_learning_id == original.source_learning_id


class TestProviderFileAdapter:
    """Test ProviderFileAdapter."""

    def test_to_db_conversion(self):
        """
        GIVEN file metadata
        WHEN calling to_db()
        THEN database row dict is returned
        """
        # Arrange
        installation_id = 10
        file_path = "rules/aipm-master.mdc"
        file_hash = "abc123def456"
        file_type = "rule"

        # Act
        db_row = ProviderFileAdapter.to_db(
            installation_id, file_path, file_hash, file_type
        )

        # Assert
        assert db_row["installation_id"] == 10
        assert db_row["file_path"] == "rules/aipm-master.mdc"
        assert db_row["file_hash"] == "abc123def456"
        assert db_row["file_type"] == "rule"
        assert "installed_at" in db_row
        # Verify datetime is ISO format
        datetime.fromisoformat(db_row["installed_at"])

    def test_to_db_different_file_types(self):
        """
        GIVEN different file types
        WHEN calling to_db()
        THEN file_type is preserved
        """
        # Arrange
        file_types = ["rule", "mode", "hook", "config", "memory"]

        # Act & Assert
        for file_type in file_types:
            db_row = ProviderFileAdapter.to_db(1, "test.file", "hash", file_type)
            assert db_row["file_type"] == file_type

    def test_from_db_conversion(self):
        """
        GIVEN database row dict
        WHEN calling from_db()
        THEN file metadata dict is returned
        """
        # Arrange
        db_row = {
            "id": 1,
            "installation_id": 10,
            "file_path": "rules/test.mdc",
            "file_hash": "abc123",
            "file_type": "rule",
            "installed_at": "2025-10-20T10:00:00",
        }

        # Act
        metadata = ProviderFileAdapter.from_db(db_row)

        # Assert
        assert metadata["id"] == 1
        assert metadata["installation_id"] == 10
        assert metadata["file_path"] == "rules/test.mdc"
        assert metadata["file_hash"] == "abc123"
        assert metadata["file_type"] == "rule"
        assert metadata["installed_at"] == datetime(2025, 10, 20, 10, 0, 0)

    def test_round_trip_conversion(self):
        """
        GIVEN file metadata
        WHEN converting to_db() then from_db()
        THEN data is preserved
        """
        # Arrange
        installation_id = 5
        file_path = "modes/test.json"
        file_hash = "hash123"
        file_type = "mode"

        # Act
        db_row = ProviderFileAdapter.to_db(
            installation_id, file_path, file_hash, file_type
        )
        # Add id for from_db
        db_row["id"] = 1
        metadata = ProviderFileAdapter.from_db(db_row)

        # Assert
        assert metadata["installation_id"] == installation_id
        assert metadata["file_path"] == file_path
        assert metadata["file_hash"] == file_hash
        assert metadata["file_type"] == file_type
        assert isinstance(metadata["installed_at"], datetime)


class TestAdapterEdgeCases:
    """Test edge cases and error handling in adapters."""

    def test_provider_installation_with_complex_config(self):
        """
        GIVEN ProviderInstallation with nested config
        WHEN converting to_db() and from_db()
        THEN nested structure is preserved
        """
        # Arrange
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
            config={
                "nested": {
                    "level1": {
                        "level2": ["item1", "item2"],
                        "enabled": True,
                    }
                },
                "list": [1, 2, 3],
            },
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(installation)
        reconstructed = ProviderInstallationAdapter.from_db({**db_row, "id": 1})

        # Assert
        assert reconstructed.config["nested"]["level1"]["level2"] == ["item1", "item2"]
        assert reconstructed.config["nested"]["level1"]["enabled"] is True
        assert reconstructed.config["list"] == [1, 2, 3]

    def test_cursor_memory_with_multiline_content(self):
        """
        GIVEN CursorMemory with multiline content
        WHEN converting to_db() and from_db()
        THEN content is preserved with line breaks
        """
        # Arrange
        content = """# Title

Multiple
Lines
Of
Content

- Bullet 1
- Bullet 2

End."""
        memory = CursorMemory(
            project_id=1,
            name="test",
            description="Test",
            content=content,
            file_path="test.md",
        )

        # Act
        db_row = CursorMemoryAdapter.to_db(memory)
        reconstructed = CursorMemoryAdapter.from_db({**db_row, "id": 1})

        # Assert
        assert reconstructed.content == content

    def test_datetime_precision_preservation(self):
        """
        GIVEN ProviderInstallation with precise datetime
        WHEN converting to_db() and from_db()
        THEN datetime precision is preserved
        """
        # Arrange
        precise_time = datetime(2025, 10, 20, 14, 30, 45, 123456)
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
            installed_at=precise_time,
            updated_at=precise_time,
        )

        # Act
        db_row = ProviderInstallationAdapter.to_db(installation)
        reconstructed = ProviderInstallationAdapter.from_db({**db_row, "id": 1})

        # Assert
        assert reconstructed.installed_at == precise_time
        assert reconstructed.updated_at == precise_time
