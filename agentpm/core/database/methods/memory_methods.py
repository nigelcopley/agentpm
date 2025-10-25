"""Memory file methods for CRUD and query operations.

This module provides database operations for MemoryFile entities.
Part of the three-layer pattern:
- Layer 1: Pydantic models (validation)
- Layer 2: Adapters (conversion)
- Layer 3: Methods (CRUD operations) ← THIS FILE

Methods:
- CRUD: create_memory_file, get_memory_file, update_memory_file, delete_memory_file
- Queries: list_memory_files, get_memory_file_by_type, get_stale_memory_files
- Validation: mark_validated, mark_stale, is_memory_file_current
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from agentpm.core.database.adapters.memory import MemoryFileAdapter
from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus,
)


def create_memory_file(db: 'DatabaseService', memory_file: MemoryFile) -> MemoryFile:
    """Create a new memory file record.

    Args:
        db: DatabaseService instance
        memory_file: MemoryFile model (id will be auto-assigned)

    Returns:
        MemoryFile with id populated

    Example:
        >>> from agentpm.core.database.models.memory import MemoryFile, MemoryFileType
        >>> memory = MemoryFile(
        ...     project_id=1,
        ...     file_type=MemoryFileType.RULES,
        ...     file_path=".claude/RULES.md",
        ...     content="# Rules\\n\\nContent...",
        ...     source_tables=["rules"],
        ...     generated_by="memory-generator",
        ...     generated_at="2025-10-21T10:00:00"
        ... )
        >>> created = create_memory_file(db, memory)
        >>> print(created.id)  # 1
    """
    with db.connect() as conn:
        data = MemoryFileAdapter.to_db(memory_file)

        # Remove id if present (auto-increment)
        data.pop('id', None)

        # Set timestamps if not provided
        now = datetime.now().isoformat()
        if not data.get('created_at'):
            data['created_at'] = now
        if not data.get('updated_at'):
            data['updated_at'] = now

        cursor = conn.execute('''
            INSERT INTO memory_files (
                project_id, session_id, file_type, file_path, file_hash,
                content, source_tables, template_version,
                confidence_score, completeness_score, validation_status,
                generated_by, generation_duration_ms,
                generated_at, validated_at, expires_at,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['project_id'], data['session_id'], data['file_type'],
            data['file_path'], data['file_hash'], data['content'],
            data['source_tables'], data['template_version'],
            data['confidence_score'], data['completeness_score'],
            data['validation_status'], data['generated_by'],
            data['generation_duration_ms'], data['generated_at'],
            data['validated_at'], data['expires_at'],
            data['created_at'], data['updated_at']
        ))
        conn.commit()

        memory_file.id = cursor.lastrowid
        memory_file.created_at = data['created_at']
        memory_file.updated_at = data['updated_at']
        return memory_file


def get_memory_file(db: 'DatabaseService', memory_file_id: int) -> Optional[MemoryFile]:
    """Get memory file by ID.

    Args:
        db: DatabaseService instance
        memory_file_id: Memory file ID

    Returns:
        MemoryFile model or None if not found

    Example:
        >>> memory = get_memory_file(db, 1)
        >>> if memory:
        ...     print(memory.file_type)  # MemoryFileType.RULES
    """
    with db.connect() as conn:
        cursor = conn.execute(
            'SELECT * FROM memory_files WHERE id = ?',
            (memory_file_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return MemoryFileAdapter.from_db(dict(row))


def get_memory_file_by_type(
    db: 'DatabaseService',
    project_id: int,
    file_type: MemoryFileType
) -> Optional[MemoryFile]:
    """Get memory file by project and type.

    Args:
        db: DatabaseService instance
        project_id: Project ID
        file_type: Type of memory file

    Returns:
        MemoryFile model or None if not found

    Example:
        >>> memory = get_memory_file_by_type(db, 1, MemoryFileType.RULES)
        >>> if memory:
        ...     print(memory.content[:50])  # First 50 chars
    """
    with db.connect() as conn:
        cursor = conn.execute(
            'SELECT * FROM memory_files WHERE project_id = ? AND file_type = ?',
            (project_id, file_type.value)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return MemoryFileAdapter.from_db(dict(row))


def list_memory_files(
    db: 'DatabaseService',
    project_id: Optional[int] = None,
    validation_status: Optional[ValidationStatus] = None,
    limit: Optional[int] = None
) -> List[MemoryFile]:
    """List memory files with optional filters.

    Args:
        db: DatabaseService instance
        project_id: Filter by project ID (optional)
        validation_status: Filter by validation status (optional)
        limit: Maximum number of results (optional)

    Returns:
        List of MemoryFile models

    Example:
        >>> # Get all validated memory files for project 1
        >>> memories = list_memory_files(db, project_id=1, validation_status=ValidationStatus.VALIDATED)
        >>> for memory in memories:
        ...     print(f"{memory.file_type}: {memory.file_path}")
    """
    with db.connect() as conn:
        query = 'SELECT * FROM memory_files WHERE 1=1'
        params: List[Any] = []

        if project_id is not None:
            query += ' AND project_id = ?'
            params.append(project_id)

        if validation_status is not None:
            query += ' AND validation_status = ?'
            params.append(validation_status.value)

        query += ' ORDER BY generated_at DESC'

        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [MemoryFileAdapter.from_db(dict(row)) for row in rows]


def get_stale_memory_files(db: 'DatabaseService', project_id: Optional[int] = None) -> List[MemoryFile]:
    """Get all stale memory files that need regeneration.

    Args:
        db: DatabaseService instance
        project_id: Filter by project ID (optional)

    Returns:
        List of stale MemoryFile models

    Example:
        >>> stale_files = get_stale_memory_files(db, project_id=1)
        >>> for memory in stale_files:
        ...     print(f"Regenerate: {memory.file_type}")
    """
    return list_memory_files(db, project_id=project_id, validation_status=ValidationStatus.STALE)


def update_memory_file(
    db: 'DatabaseService',
    memory_file_id: int,
    updates: Dict[str, Any]
) -> Optional[MemoryFile]:
    """Update memory file fields.

    Args:
        db: DatabaseService instance
        memory_file_id: Memory file ID
        updates: Dict of field names to new values

    Returns:
        Updated MemoryFile model or None if not found

    Example:
        >>> updates = {
        ...     'content': '# Updated Rules\\n\\nNew content...',
        ...     'validation_status': ValidationStatus.VALIDATED,
        ...     'validated_at': '2025-10-21T11:00:00'
        ... }
        >>> memory = update_memory_file(db, 1, updates)
    """
    # Get existing memory file
    memory_file = get_memory_file(db, memory_file_id)
    if not memory_file:
        return None

    with db.connect() as conn:
        # Convert updates to database format
        db_updates = MemoryFileAdapter.to_db_partial(updates)

        # Always update updated_at timestamp
        db_updates['updated_at'] = datetime.now().isoformat()

        # Build UPDATE query dynamically
        set_clause = ', '.join(f'{key} = ?' for key in db_updates.keys())
        values = list(db_updates.values())
        values.append(memory_file_id)

        conn.execute(
            f'UPDATE memory_files SET {set_clause} WHERE id = ?',
            values
        )
        conn.commit()

    # Return updated model
    return get_memory_file(db, memory_file_id)


def mark_validated(
    db: 'DatabaseService',
    memory_file_id: int,
    validated_at: Optional[str] = None
) -> Optional[MemoryFile]:
    """Mark memory file as validated.

    Args:
        db: DatabaseService instance
        memory_file_id: Memory file ID
        validated_at: Validation timestamp (defaults to now)

    Returns:
        Updated MemoryFile model or None if not found

    Example:
        >>> memory = mark_validated(db, 1)
        >>> print(memory.validation_status)  # ValidationStatus.VALIDATED
    """
    if validated_at is None:
        validated_at = datetime.now().isoformat()

    return update_memory_file(db, memory_file_id, {
        'validation_status': ValidationStatus.VALIDATED,
        'validated_at': validated_at
    })


def mark_stale(db: 'DatabaseService', memory_file_id: int) -> Optional[MemoryFile]:
    """Mark memory file as stale (needs regeneration).

    Args:
        db: DatabaseService instance
        memory_file_id: Memory file ID

    Returns:
        Updated MemoryFile model or None if not found

    Example:
        >>> memory = mark_stale(db, 1)
        >>> print(memory.validation_status)  # ValidationStatus.STALE
    """
    return update_memory_file(db, memory_file_id, {
        'validation_status': ValidationStatus.STALE
    })


def delete_memory_file(db: 'DatabaseService', memory_file_id: int) -> bool:
    """Delete memory file.

    Args:
        db: DatabaseService instance
        memory_file_id: Memory file ID

    Returns:
        True if deleted, False if not found

    Example:
        >>> success = delete_memory_file(db, 1)
        >>> print(success)  # True
    """
    with db.connect() as conn:
        cursor = conn.execute(
            'DELETE FROM memory_files WHERE id = ?',
            (memory_file_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def is_memory_file_current(
    db: 'DatabaseService',
    project_id: int,
    file_type: MemoryFileType,
    max_age_hours: int = 24
) -> bool:
    """Check if memory file is current (not stale and not too old).

    Args:
        db: DatabaseService instance
        project_id: Project ID
        file_type: Type of memory file
        max_age_hours: Maximum age in hours (default 24)

    Returns:
        True if current, False otherwise

    Example:
        >>> is_current = is_memory_file_current(db, 1, MemoryFileType.RULES, max_age_hours=24)
        >>> if not is_current:
        ...     print("Need to regenerate RULES.md")
    """
    memory_file = get_memory_file_by_type(db, project_id, file_type)

    if not memory_file:
        return False

    # Check if stale
    if memory_file.is_stale:
        return False

    # Check if expired
    if memory_file.is_expired:
        return False

    # Check age
    try:
        generated_at = datetime.fromisoformat(memory_file.generated_at)
        age_hours = (datetime.now() - generated_at).total_seconds() / 3600
        return age_hours <= max_age_hours
    except (ValueError, TypeError):
        return False
