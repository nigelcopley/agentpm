"""Memory File adapter for Pydantic ↔ SQLite conversion.

This module provides type-safe conversion between MemoryFile Pydantic models
and SQLite database rows. Part of the three-layer pattern:
- Layer 1: Pydantic models (validation)
- Layer 2: Adapters (conversion) ← THIS FILE
- Layer 3: Methods (CRUD operations)
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus,
)


class MemoryFileAdapter:
    """Convert between MemoryFile Pydantic models and SQLite rows.

    This adapter handles all type conversions:
    - Enums → strings (to_db)
    - Lists → JSON arrays (to_db)
    - datetime → ISO strings (to_db)
    - Reverse conversions (from_db)
    """

    @staticmethod
    def to_db(memory_file: MemoryFile) -> Dict[str, Any]:
        """Convert MemoryFile model to SQLite dict.

        Args:
            memory_file: MemoryFile Pydantic model

        Returns:
            Dictionary ready for SQLite INSERT/UPDATE

        Example:
            >>> memory = MemoryFile(project_id=1, file_type="rules", ...)
            >>> data = MemoryFileAdapter.to_db(memory)
            >>> cursor.execute("INSERT INTO memory_files ...", data)
        """
        return {
            'id': memory_file.id,
            'project_id': memory_file.project_id,
            'session_id': memory_file.session_id,
            'file_type': memory_file.file_type.value,
            'file_path': memory_file.file_path,
            'file_hash': memory_file.file_hash,
            'content': memory_file.content,
            'source_tables': json.dumps(memory_file.source_tables),
            'template_version': memory_file.template_version,
            'confidence_score': memory_file.confidence_score,
            'completeness_score': memory_file.completeness_score,
            'validation_status': memory_file.validation_status.value,
            'generated_by': memory_file.generated_by,
            'generation_duration_ms': memory_file.generation_duration_ms,
            'generated_at': memory_file.generated_at,
            'validated_at': memory_file.validated_at,
            'expires_at': memory_file.expires_at,
            'created_at': memory_file.created_at,
            'updated_at': memory_file.updated_at,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> MemoryFile:
        """Convert SQLite row to MemoryFile model.

        Args:
            row: SQLite row as dict (use sqlite3.Row or row_factory)

        Returns:
            MemoryFile Pydantic model with all validations applied

        Example:
            >>> cursor.execute("SELECT * FROM memory_files WHERE id = ?", (1,))
            >>> row = cursor.fetchone()
            >>> memory = MemoryFileAdapter.from_db(row)
        """
        # Parse source_tables JSON → List[str]
        source_tables = json.loads(row.get('source_tables', '[]'))

        return MemoryFile(
            id=row['id'],
            project_id=row['project_id'],
            session_id=row.get('session_id'),
            file_type=MemoryFileType(row['file_type']),
            file_path=row['file_path'],
            file_hash=row.get('file_hash'),
            content=row['content'],
            source_tables=source_tables,
            template_version=row.get('template_version', '1.0.0'),
            confidence_score=row.get('confidence_score', 1.0),
            completeness_score=row.get('completeness_score', 1.0),
            validation_status=ValidationStatus(row.get('validation_status', 'pending')),
            generated_by=row['generated_by'],
            generation_duration_ms=row.get('generation_duration_ms'),
            generated_at=row['generated_at'],
            validated_at=row.get('validated_at'),
            expires_at=row.get('expires_at'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )

    @staticmethod
    def to_db_partial(updates: Dict[str, Any]) -> Dict[str, Any]:
        """Convert partial updates to SQLite-compatible format.

        Useful for UPDATE operations where only some fields change.
        Handles enum, list, and datetime conversions automatically.

        Args:
            updates: Dict of field names to new values

        Returns:
            Dict with converted values ready for SQLite

        Example:
            >>> updates = {'validation_status': ValidationStatus.VALIDATED, 'validated_at': '2025-10-21T10:00:00'}
            >>> db_updates = MemoryFileAdapter.to_db_partial(updates)
            >>> cursor.execute("UPDATE memory_files SET ... WHERE ...", db_updates)
        """
        result = {}

        for key, value in updates.items():
            if value is None:
                result[key] = None
            elif key == 'file_type' and isinstance(value, MemoryFileType):
                result[key] = value.value
            elif key == 'validation_status' and isinstance(value, ValidationStatus):
                result[key] = value.value
            elif key == 'source_tables' and isinstance(value, list):
                result[key] = json.dumps(value)
            elif key in ('generated_at', 'validated_at', 'expires_at', 'created_at', 'updated_at'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
            else:
                result[key] = value

        return result
