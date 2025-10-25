"""
Document Audit Log CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for DocumentAuditLog entities with comprehensive audit tracking.

Pattern: Type-safe method signatures with DocumentAuditLog model
Methods: create_audit_entry, get_audit_entry, get_document_history,
         get_audit_by_actor, get_audit_by_action, get_recent_audits
"""

from typing import Optional, List
import sqlite3

from ..models.document_audit_log import DocumentAuditLog
from ..adapters.document_audit_adapter import DocumentAuditAdapter


def create_audit_entry(service, entry: DocumentAuditLog) -> DocumentAuditLog:
    """
    Create a new audit log entry.

    Args:
        service: DatabaseService instance
        entry: DocumentAuditLog model to create

    Returns:
        Created DocumentAuditLog with database ID

    Example:
        >>> from agentpm.core.database.models.document_audit_log import DocumentAuditLog
        >>> entry = DocumentAuditLog(
        ...     document_id=123,
        ...     action="publish",
        ...     actor="system",
        ...     from_state="approved",
        ...     to_state="published",
        ...     details={"source": "...", "destination": "..."}
        ... )
        >>> created = create_audit_entry(db, entry)
    """
    # Convert model to database format
    db_data = DocumentAuditAdapter.to_db(entry)

    query = """
        INSERT INTO document_audit_log (
            document_id, action, actor, timestamp,
            from_state, to_state, details, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['document_id'],
        db_data['action'],
        db_data['actor'],
        db_data['timestamp'],
        db_data['from_state'],
        db_data['to_state'],
        db_data['details'],
        db_data['comment'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        entry_id = cursor.lastrowid

    return get_audit_entry(service, entry_id)


def get_audit_entry(service, entry_id: int) -> Optional[DocumentAuditLog]:
    """
    Get audit log entry by ID.

    Args:
        service: DatabaseService instance
        entry_id: Audit log entry ID

    Returns:
        DocumentAuditLog if found, None otherwise
    """
    query = "SELECT * FROM document_audit_log WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (entry_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return DocumentAuditAdapter.from_db(dict(row))


def get_document_history(
    service,
    document_id: int,
    limit: int = 100
) -> List[DocumentAuditLog]:
    """
    Get full audit history for a document.

    Args:
        service: DatabaseService instance
        document_id: Document reference ID
        limit: Maximum number of entries (default: 100)

    Returns:
        List of DocumentAuditLog models sorted by timestamp (newest first)

    Example:
        >>> history = get_document_history(db, 123)
        >>> for entry in history:
        ...     print(f"{entry.action}: {entry.from_state} → {entry.to_state}")
    """
    query = """
        SELECT * FROM document_audit_log
        WHERE document_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (document_id, limit))
        rows = cursor.fetchall()

    return [DocumentAuditAdapter.from_db(dict(row)) for row in rows]


def get_audit_by_actor(
    service,
    actor: str,
    limit: int = 100
) -> List[DocumentAuditLog]:
    """
    Get audit entries by actor (user or agent).

    Args:
        service: DatabaseService instance
        actor: User email or agent identifier
        limit: Maximum number of entries (default: 100)

    Returns:
        List of DocumentAuditLog models sorted by timestamp (newest first)

    Example:
        >>> entries = get_audit_by_actor(db, "tech-lead@example.com")
        >>> print(f"Found {len(entries)} actions by tech-lead")
    """
    query = """
        SELECT * FROM document_audit_log
        WHERE actor = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (actor, limit))
        rows = cursor.fetchall()

    return [DocumentAuditAdapter.from_db(dict(row)) for row in rows]


def get_audit_by_action(
    service,
    action: str,
    since: Optional[str] = None,
    limit: int = 100
) -> List[DocumentAuditLog]:
    """
    Get audit entries for specific action type.

    Args:
        service: DatabaseService instance
        action: Action type (create, publish, approve, etc.)
        since: Optional ISO timestamp to filter (only entries after this time)
        limit: Maximum number of entries (default: 100)

    Returns:
        List of DocumentAuditLog models sorted by timestamp (newest first)

    Example:
        >>> publishes = get_audit_by_action(db, "publish")
        >>> print(f"Found {len(publishes)} publish actions")
    """
    if since:
        query = """
            SELECT * FROM document_audit_log
            WHERE action = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params = (action, since, limit)
    else:
        query = """
            SELECT * FROM document_audit_log
            WHERE action = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params = (action, limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

    return [DocumentAuditAdapter.from_db(dict(row)) for row in rows]


def get_recent_audits(
    service,
    limit: int = 100
) -> List[DocumentAuditLog]:
    """
    Get most recent audit entries across all documents.

    Args:
        service: DatabaseService instance
        limit: Maximum number of entries (default: 100)

    Returns:
        List of DocumentAuditLog models sorted by timestamp (newest first)

    Example:
        >>> recent = get_recent_audits(db, limit=20)
        >>> print(f"Last {len(recent)} document actions")
    """
    query = """
        SELECT * FROM document_audit_log
        ORDER BY timestamp DESC
        LIMIT ?
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (limit,))
        rows = cursor.fetchall()

    return [DocumentAuditAdapter.from_db(dict(row)) for row in rows]


def count_audits_by_action(service) -> dict:
    """
    Count audit entries by action type.

    Args:
        service: DatabaseService instance

    Returns:
        Dict mapping action types to counts

    Example:
        >>> counts = count_audits_by_action(db)
        >>> counts
        {'publish': 45, 'approve': 38, 'reject': 7, 'create': 52}
    """
    query = """
        SELECT action, COUNT(*) as count
        FROM document_audit_log
        GROUP BY action
        ORDER BY count DESC
    """

    with service.connect() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}
