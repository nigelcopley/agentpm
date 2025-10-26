"""
Document Reference Adapter - Model ↔ Database Conversion

Handles conversion between DocumentReference domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)

Migration: 0011 (document_references table)
Migration: 0031 (Universal Documentation System metadata)
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.document_reference import DocumentReference
from ..enums import EntityType, DocumentType, DocumentFormat, StorageMode, SyncStatus


class DocumentReferenceAdapter:
    """
    Handles DocumentReference model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, document: DocumentReference) -> DocumentReference:
        """
        Create a new document reference (CLI entry point).

        Three-layer pattern:
          1. Validate Pydantic model (automatic via type hints)
          2. Delegate to methods layer
          3. Return validated DocumentReference

        Args:
            service: DatabaseService instance
            document: Validated DocumentReference Pydantic model

        Returns:
            Created DocumentReference with database ID

        Example:
            >>> from agentpm.core.database.adapters import DocumentReferenceAdapter
            >>> doc = DocumentReference(entity_type=EntityType.WORK_ITEM, entity_id=5, ...)
            >>> created = DocumentReferenceAdapter.create(db, doc)
        """
        from ..methods import document_references as doc_methods
        return doc_methods.create_document_reference(service, document)

    @staticmethod
    def get(service, doc_id: int) -> Optional[DocumentReference]:
        """
        Get document reference by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            doc_id: Document reference ID

        Returns:
            DocumentReference if found, None otherwise
        """
        from ..methods import document_references as doc_methods
        return doc_methods.get_document_reference(service, doc_id)

    @staticmethod
    def list(service, entity_type: Optional[EntityType] = None,
             entity_id: Optional[int] = None,
             document_type: Optional[DocumentType] = None,
             format: Optional[DocumentFormat] = None,
             created_by: Optional[str] = None,
             limit: Optional[int] = None) -> List[DocumentReference]:
        """
        List document references with optional filters (CLI entry point).

        Args:
            service: DatabaseService instance
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            document_type: Optional document type filter
            format: Optional document format filter
            created_by: Optional creator filter
            limit: Optional limit on results

        Returns:
            List of DocumentReference models
        """
        from ..methods import document_references as doc_methods
        return doc_methods.list_document_references(
            service,
            entity_type=entity_type,
            entity_id=entity_id,
            document_type=document_type,
            format=format,
            created_by=created_by,
            limit=limit
        )

    @staticmethod
    def update(service, document: DocumentReference) -> Optional[DocumentReference]:
        """
        Update document reference (CLI entry point).

        Args:
            service: DatabaseService instance
            document: DocumentReference model with updated fields

        Returns:
            Updated DocumentReference if found, None otherwise

        Raises:
            ValidationError: If document.id is None
        """
        from ..methods import document_references as doc_methods
        return doc_methods.update_document_reference(service, document)

    @staticmethod
    def delete(service, doc_id: int) -> bool:
        """
        Delete document reference by ID (CLI entry point).

        Note: This only removes the database reference, not the actual file.

        Args:
            service: DatabaseService instance
            doc_id: Document reference ID

        Returns:
            True if deleted, False if not found
        """
        from ..methods import document_references as doc_methods
        return doc_methods.delete_document_reference(service, doc_id)

    # ============================================================================
    # MODEL CONVERSION (Internal Use)
    # ============================================================================

    @staticmethod
    def to_db(doc: DocumentReference) -> Dict[str, Any]:
        """
        Convert DocumentReference model to database row format.

        Args:
            doc: DocumentReference domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'entity_type': doc.entity_type.value,  # Enum to string
            'entity_id': doc.entity_id,
            'file_path': doc.file_path,
            'document_type': doc.document_type.value if doc.document_type else None,  # Enum to string
            'title': doc.title,
            'description': doc.description,
            'file_size_bytes': doc.file_size_bytes,
            'content_hash': doc.content_hash,
            'format': doc.format.value if doc.format else None,  # Enum to string
            'created_by': doc.created_by,
            'created_at': doc.created_at.isoformat() if doc.created_at else None,
            'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,

            # Universal Documentation System metadata (Migration 0031)
            'category': doc.category,
            'document_type_dir': doc.document_type_dir,
            'segment_type': doc.segment_type,
            'component': doc.component,
            'domain': doc.domain,
            'audience': doc.audience,
            'maturity': doc.maturity,
            'priority': doc.priority,
            'tags': json.dumps(doc.tags) if doc.tags else None,  # List → JSON string
            'phase': doc.phase,
            'work_item_id': doc.work_item_id,

            # Content storage (Migration 0039 - WI-133)
            'content': doc.content,
            'filename': doc.filename,
            'storage_mode': doc.storage_mode.value if doc.storage_mode else 'hybrid',  # Enum to string
            'content_updated_at': doc.content_updated_at.isoformat() if doc.content_updated_at else None,
            'last_synced_at': doc.last_synced_at.isoformat() if doc.last_synced_at else None,
            'sync_status': doc.sync_status.value if doc.sync_status else 'synced',  # Enum to string

            # Visibility and lifecycle (Migration 0044 - WI-164)
            'visibility': doc.visibility,
            'lifecycle_stage': doc.lifecycle_stage,
            'published_path': doc.published_path,
            'published_date': doc.published_date.isoformat() if doc.published_date else None,
            'unpublished_date': doc.unpublished_date.isoformat() if doc.unpublished_date else None,
            'review_status': doc.review_status,
            'reviewer_id': doc.reviewer_id,
            'reviewer_assigned_at': doc.reviewer_assigned_at.isoformat() if doc.reviewer_assigned_at else None,
            'review_comment': doc.review_comment,
            'review_completed_at': doc.review_completed_at.isoformat() if doc.review_completed_at else None,
            'auto_publish': doc.auto_publish,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> DocumentReference:
        """
        Convert database row to DocumentReference model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated DocumentReference model
        """
        return DocumentReference(
            id=row.get('id'),
            entity_type=EntityType(row['entity_type']),  # String to Enum
            entity_id=row['entity_id'],
            file_path=row['file_path'],
            document_type=DocumentType(row['document_type']) if row.get('document_type') else None,  # String to Enum
            title=row.get('title'),
            description=row.get('description'),
            file_size_bytes=row.get('file_size_bytes'),
            content_hash=row.get('content_hash'),
            format=DocumentFormat(row['format']) if row.get('format') else None,  # String to Enum
            created_by=row.get('created_by'),
            created_at=_parse_datetime(row.get('created_at')) or datetime.utcnow(),
            updated_at=_parse_datetime(row.get('updated_at')) or datetime.utcnow(),

            # Universal Documentation System metadata (Migration 0031)
            category=row.get('category'),
            document_type_dir=row.get('document_type_dir'),
            segment_type=row.get('segment_type'),
            component=row.get('component'),
            domain=row.get('domain'),
            audience=row.get('audience'),
            maturity=row.get('maturity'),
            priority=row.get('priority'),
            tags=json.loads(row['tags']) if row.get('tags') else [],  # JSON string → List
            phase=row.get('phase'),
            work_item_id=row.get('work_item_id'),

            # Content storage (Migration 0039 - WI-133)
            content=row.get('content'),
            filename=row.get('filename'),
            storage_mode=StorageMode(row['storage_mode']) if row.get('storage_mode') else StorageMode.HYBRID,  # String to Enum
            content_updated_at=_parse_datetime(row.get('content_updated_at')),
            last_synced_at=_parse_datetime(row.get('last_synced_at')),
            sync_status=SyncStatus(row['sync_status']) if row.get('sync_status') else SyncStatus.SYNCED,  # String to Enum

            # Visibility and lifecycle (Migration 0044 - WI-164)
            visibility=row.get('visibility'),
            lifecycle_stage=row.get('lifecycle_stage'),
            published_path=row.get('published_path'),
            published_date=_parse_datetime(row.get('published_date')),
            unpublished_date=_parse_datetime(row.get('unpublished_date')),
            review_status=row.get('review_status'),
            reviewer_id=row.get('reviewer_id'),
            reviewer_assigned_at=_parse_datetime(row.get('reviewer_assigned_at')),
            review_comment=row.get('review_comment'),
            review_completed_at=_parse_datetime(row.get('review_completed_at')),
            auto_publish=row.get('auto_publish'),
        )


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
