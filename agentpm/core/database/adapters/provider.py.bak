"""
Provider Adapters - Layer 2: Database Conversion

Converts between Pydantic models and database representations.
Handles JSON serialization/deserialization for complex fields.

Pattern: Static methods for bidirectional conversion
Architecture: Database layer (core/database/) - NOT provider-specific
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from agentpm.core.database.models.provider import (
    ProviderInstallation,
    CursorMemory,
    InstallationStatus,
    ProviderType,
)


class ProviderInstallationAdapter:
    """
    Adapter for ProviderInstallation model.

    Converts between Pydantic model and database row.
    """

    @staticmethod
    def to_db(installation: ProviderInstallation) -> Dict[str, Any]:
        """
        Convert Pydantic model to database row.

        Args:
            installation: ProviderInstallation model

        Returns:
            Dictionary suitable for database insertion
        """
        return {
            "project_id": installation.project_id,
            "provider_type": installation.provider_type.value,
            "provider_version": installation.provider_version,
            "install_path": installation.install_path,
            "status": installation.status.value,
            "config": json.dumps(installation.config),
            "installed_files": json.dumps(installation.installed_files),
            "file_hashes": json.dumps(installation.file_hashes),
            "installed_at": installation.installed_at.isoformat(),
            "updated_at": installation.updated_at.isoformat(),
            "last_verified_at": (
                installation.last_verified_at.isoformat()
                if installation.last_verified_at
                else None
            ),
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> ProviderInstallation:
        """
        Convert database row to Pydantic model.

        Args:
            row: Database row as dictionary

        Returns:
            ProviderInstallation model
        """
        return ProviderInstallation(
            id=row["id"],
            project_id=row["project_id"],
            provider_type=ProviderType(row["provider_type"]),
            provider_version=row["provider_version"],
            install_path=row["install_path"],
            status=InstallationStatus(row["status"]),
            config=json.loads(row["config"]) if row["config"] else {},
            installed_files=json.loads(row["installed_files"]) if row["installed_files"] else [],
            file_hashes=json.loads(row["file_hashes"]) if row["file_hashes"] else {},
            installed_at=datetime.fromisoformat(row["installed_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_verified_at=(
                datetime.fromisoformat(row["last_verified_at"])
                if row.get("last_verified_at")
                else None
            ),
        )


class CursorMemoryAdapter:
    """
    Adapter for CursorMemory model.

    Converts between Pydantic model and database row.
    """

    @staticmethod
    def to_db(memory: CursorMemory) -> Dict[str, Any]:
        """
        Convert Pydantic model to database row.

        Args:
            memory: CursorMemory model

        Returns:
            Dictionary suitable for database insertion
        """
        return {
            "project_id": memory.project_id,
            "name": memory.name,
            "description": memory.description,
            "category": memory.category,
            "content": memory.content,
            "tags": json.dumps(memory.tags),
            "file_path": memory.file_path,
            "file_hash": memory.file_hash,
            "source_learning_id": memory.source_learning_id,
            "last_synced_at": (
                memory.last_synced_at.isoformat()
                if memory.last_synced_at
                else None
            ),
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat(),
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> CursorMemory:
        """
        Convert database row to Pydantic model.

        Args:
            row: Database row as dictionary

        Returns:
            CursorMemory model
        """
        return CursorMemory(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            category=row["category"],
            content=row["content"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            file_path=row["file_path"],
            file_hash=row.get("file_hash"),
            source_learning_id=row.get("source_learning_id"),
            last_synced_at=(
                datetime.fromisoformat(row["last_synced_at"])
                if row.get("last_synced_at")
                else None
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class ProviderFileAdapter:
    """
    Adapter for provider file metadata.

    Tracks installed files and their integrity.
    """

    @staticmethod
    def to_db(
        installation_id: int,
        file_path: str,
        file_hash: str,
        file_type: str,
    ) -> Dict[str, Any]:
        """
        Convert file metadata to database row.

        Args:
            installation_id: Provider installation ID
            file_path: Relative file path
            file_hash: SHA-256 hash of file content
            file_type: File type (rule, mode, hook, config, memory)

        Returns:
            Dictionary suitable for database insertion
        """
        return {
            "installation_id": installation_id,
            "file_path": file_path,
            "file_hash": file_hash,
            "file_type": file_type,
            "installed_at": datetime.now().isoformat(),
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert database row to file metadata dict.

        Args:
            row: Database row as dictionary

        Returns:
            File metadata dictionary
        """
        return {
            "id": row["id"],
            "installation_id": row["installation_id"],
            "file_path": row["file_path"],
            "file_hash": row["file_hash"],
            "file_type": row["file_type"],
            "installed_at": datetime.fromisoformat(row["installed_at"]),
        }
