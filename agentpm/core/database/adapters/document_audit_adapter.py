"""
Document Audit Log Adapter - Model ↔ Database Conversion

Handles conversion between DocumentAuditLog domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)

Migration: 0044 (document_audit_log table)
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.document_audit_log import DocumentAuditLog


class DocumentAuditAdapter:
    """
    Handles DocumentAuditLog model <-> Database row conversions.

    This is the BOUNDARY LAYER between services and database methods.
    Services should call these methods, NOT methods directly.
    """

    @staticmethod
    def to_db(entry: DocumentAuditLog) -> Dict[str, Any]:
        """
        Convert DocumentAuditLog model to database row format.

        Args:
            entry: DocumentAuditLog domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'document_id': entry.document_id,
            'action': entry.action,
            'actor': entry.actor,
            'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
            'from_state': entry.from_state,
            'to_state': entry.to_state,
            'details': json.dumps(entry.details) if entry.details else None,
            'comment': entry.comment,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> DocumentAuditLog:
        """
        Convert database row to DocumentAuditLog model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated DocumentAuditLog model
        """
        return DocumentAuditLog(
            id=row.get('id'),
            document_id=row['document_id'],
            action=row['action'],
            actor=row['actor'],
            timestamp=_parse_datetime(row.get('timestamp')) or datetime.utcnow(),
            from_state=row.get('from_state'),
            to_state=row.get('to_state'),
            details=json.loads(row['details']) if row.get('details') else None,
            comment=row.get('comment'),
        )

    @staticmethod
    def create(service, entry: DocumentAuditLog) -> DocumentAuditLog:
        """
        Create a new audit log entry (Service entry point).

        Args:
            service: DatabaseService instance
            entry: Validated DocumentAuditLog Pydantic model

        Returns:
            Created DocumentAuditLog with database ID
        """
        from ..methods import document_audit as audit_methods
        return audit_methods.create_audit_entry(service, entry)

    @staticmethod
    def get(service, entry_id: int) -> Optional[DocumentAuditLog]:
        """
        Get audit log entry by ID (Service entry point).

        Args:
            service: DatabaseService instance
            entry_id: Audit log entry ID

        Returns:
            DocumentAuditLog if found, None otherwise
        """
        from ..methods import document_audit as audit_methods
        return audit_methods.get_audit_entry(service, entry_id)

    @staticmethod
    def list_for_document(
        service,
        document_id: int,
        limit: int = 100
    ) -> List[DocumentAuditLog]:
        """
        List audit log entries for a document (Service entry point).

        Args:
            service: DatabaseService instance
            document_id: Document reference ID
            limit: Maximum number of entries (default: 100)

        Returns:
            List of DocumentAuditLog models (newest first)
        """
        from ..methods import document_audit as audit_methods
        return audit_methods.get_document_history(service, document_id, limit)


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from database value"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None
