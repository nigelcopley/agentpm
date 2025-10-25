"""
Document References CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for DocumentReference entities with document tracking and organization.

Pattern: Type-safe method signatures with DocumentReference model
Methods: create_document_reference, get_document_reference, list_document_references,
         update_document_reference, delete_document_reference, get_documents_by_entity,
         get_documents_by_type
"""

from typing import Optional, List
import sqlite3

from ..models import DocumentReference
from ..adapters.document_reference_adapter import DocumentReferenceAdapter
from ..enums import EntityType, DocumentType, DocumentFormat


def create_document_reference(service, document: DocumentReference) -> DocumentReference:
    """
    Create a new document reference.

    Args:
        service: DatabaseService instance
        document: DocumentReference model to create

    Returns:
        Created DocumentReference with database ID

    Example:
        >>> doc = DocumentReference(
        ...     entity_type=EntityType.TASK,
        ...     entity_id=240,
        ...     file_path="docs/components/agents/New/integration-plan.md",
        ...     document_type=DocumentType.DESIGN,
        ...     title="Integration Architecture",
        ...     format=DocumentFormat.MARKDOWN,
        ...     created_by="system-architect"
        ... )
        >>> created = create_document_reference(db, doc)
    """
    # Convert model to database format
    db_data = DocumentReferenceAdapter.to_db(document)

    query = """
        INSERT INTO document_references (
            entity_type, entity_id, file_path,
            document_type, title, description,
            file_size_bytes, content_hash, format,
            created_by, created_at, updated_at,
            category, document_type_dir, segment_type, component, domain,
            audience, maturity, priority, tags, phase, work_item_id,
            content, filename, storage_mode, content_updated_at, last_synced_at, sync_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['entity_type'],
        db_data['entity_id'],
        db_data['file_path'],
        db_data['document_type'],
        db_data['title'],
        db_data['description'],
        db_data['file_size_bytes'],
        db_data['content_hash'],
        db_data['format'],
        db_data['created_by'],
        db_data['created_at'],
        db_data['updated_at'],
        db_data.get('category'),
        db_data.get('document_type_dir'),
        db_data.get('segment_type'),
        db_data.get('component'),
        db_data.get('domain'),
        db_data.get('audience'),
        db_data.get('maturity'),
        db_data.get('priority'),
        db_data.get('tags'),
        db_data.get('phase'),
        db_data.get('work_item_id'),
        db_data.get('content'),
        db_data.get('filename'),
        db_data.get('storage_mode'),
        db_data.get('content_updated_at'),
        db_data.get('last_synced_at'),
        db_data.get('sync_status'),
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        doc_id = cursor.lastrowid

    return get_document_reference(service, doc_id)


def get_document_reference(service, doc_id: int) -> Optional[DocumentReference]:
    """
    Get document reference by ID.

    Args:
        service: DatabaseService instance
        doc_id: Document reference ID

    Returns:
        DocumentReference if found, None otherwise
    """
    query = "SELECT * FROM document_references WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (doc_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return DocumentReferenceAdapter.from_db(dict(row))


def list_document_references(
    service,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[int] = None,
    document_type: Optional[DocumentType] = None,
    format: Optional[DocumentFormat] = None,
    created_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[DocumentReference]:
    """
    List document references with optional filters.

    Args:
        service: DatabaseService instance
        entity_type: Filter by entity type (project, work_item, task)
        entity_id: Filter by entity ID
        document_type: Filter by document type (architecture, design, etc.)
        format: Filter by document format (markdown, yaml, etc.)
        created_by: Filter by creator identifier
        limit: Maximum number of results

    Returns:
        List of DocumentReference models sorted by creation time (newest first)

    Example:
        >>> # Get all documents for a task
        >>> docs = list_document_references(
        ...     db, entity_type=EntityType.TASK, entity_id=240
        ... )
        >>> # Get all architecture documents
        >>> arch_docs = list_document_references(
        ...     db, document_type=DocumentType.ARCHITECTURE
        ... )
    """
    query = "SELECT * FROM document_references WHERE 1=1"
    params = []

    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)

    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)

    if document_type:
        query += " AND document_type = ?"
        params.append(document_type.value)

    if format:
        query += " AND format = ?"
        params.append(format.value)

    if created_by:
        query += " AND created_by = ?"
        params.append(created_by)

    query += " ORDER BY created_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [DocumentReferenceAdapter.from_db(dict(row)) for row in rows]


def update_document_reference(service, document: DocumentReference) -> Optional[DocumentReference]:
    """
    Update document reference with validation.

    Args:
        service: DatabaseService instance
        document: DocumentReference model with updated fields

    Returns:
        Updated DocumentReference if found, None otherwise

    Example:
        >>> # Update document reference
        >>> doc = get_document_reference(db, 1)
        >>> doc.title = "Updated Title"
        >>> doc.description = "New description"
        >>> updated = update_document_reference(db, doc)
    """
    if not document.id:
        return None

    db_data = DocumentReferenceAdapter.to_db(document)

    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE document_references SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), document.id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_document_reference(service, document.id)


def delete_document_reference(service, doc_id: int) -> bool:
    """
    Delete document reference by ID.

    Note: This only removes the database reference, not the actual file.

    Args:
        service: DatabaseService instance
        doc_id: Document reference ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM document_references WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (doc_id,))
        return cursor.rowcount > 0


def get_documents_by_entity(
    service,
    entity_type: EntityType,
    entity_id: int,
    document_type: Optional[DocumentType] = None
) -> List[DocumentReference]:
    """
    Get all documents for a specific entity.

    Convenience method for retrieving complete document list for a project, work item, or task.

    Args:
        service: DatabaseService instance
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID
        document_type: Optional filter by document type

    Returns:
        List of DocumentReference models sorted by creation time (newest first)

    Example:
        >>> # Get all documents for task #240
        >>> docs = get_documents_by_entity(db, EntityType.TASK, 240)
        >>> # Get only design documents for work item #43
        >>> design_docs = get_documents_by_entity(
        ...     db, EntityType.WORK_ITEM, 43, DocumentType.DESIGN
        ... )
    """
    return list_document_references(
        service,
        entity_type=entity_type,
        entity_id=entity_id,
        document_type=document_type
    )


def get_documents_by_type(
    service,
    document_type: DocumentType,
    entity_type: Optional[EntityType] = None,
    limit: Optional[int] = None
) -> List[DocumentReference]:
    """
    Get all documents of a specific type.

    Useful for browsing all architecture docs, ADRs, test plans, etc. across the project.

    Args:
        service: DatabaseService instance
        document_type: Document type to filter (architecture, design, adr, etc.)
        entity_type: Optional filter by entity type
        limit: Maximum number of results

    Returns:
        List of DocumentReference models

    Example:
        >>> # Get all architecture documents
        >>> arch_docs = get_documents_by_type(db, DocumentType.ARCHITECTURE_DOC)
        >>> # Get all task-level ADRs
        >>> task_adrs = get_documents_by_type(
        ...     db, DocumentType.ADR, EntityType.TASK
        ... )
    """
    return list_document_references(
        service,
        document_type=document_type,
        entity_type=entity_type,
        limit=limit
    )


def get_recent_documents(
    service,
    entity_type: Optional[EntityType] = None,
    limit: int = 20
) -> List[DocumentReference]:
    """
    Get recently created documents.

    Args:
        service: DatabaseService instance
        entity_type: Optional filter by entity type
        limit: Maximum number of results (default: 20)

    Returns:
        List of DocumentReference models sorted by creation time (newest first)

    Example:
        >>> # Get 20 most recent documents
        >>> recent = get_recent_documents(db)
        >>> # Get recent task-level documents
        >>> recent_tasks = get_recent_documents(db, EntityType.TASK)
    """
    return list_document_references(
        service,
        entity_type=entity_type,
        limit=limit
    )


def count_documents_by_type(
    service,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[int] = None
) -> dict:
    """
    Count documents by document type.

    Args:
        service: DatabaseService instance
        entity_type: Optional filter by entity type
        entity_id: Optional filter by entity ID

    Returns:
        Dict mapping document types to counts

    Example:
        >>> # Count all documents by type
        >>> counts = count_documents_by_type(db)
        >>> counts
        {'architecture': 5, 'design': 12, 'adr': 8, 'test_plan': 6}
        >>> # Count documents for specific entity
        >>> task_counts = count_documents_by_type(
        ...     db, entity_type=EntityType.TASK, entity_id=240
        ... )
    """
    query = """
        SELECT document_type, COUNT(*) as count
        FROM document_references
        WHERE 1=1
    """
    params = []

    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)

    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)

    query += " GROUP BY document_type"

    with service.connect() as conn:
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}


def get_document_by_path(
    service,
    file_path: str,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[int] = None
) -> Optional[DocumentReference]:
    """
    Get document reference by file path.

    Args:
        service: DatabaseService instance
        file_path: Relative file path from project root
        entity_type: Optional entity type filter (for UNIQUE constraint)
        entity_id: Optional entity ID filter (for UNIQUE constraint)

    Returns:
        DocumentReference if found, None otherwise

    Example:
        >>> # Find document by path
        >>> doc = get_document_by_path(
        ...     db,
        ...     "docs/components/agents/New/integration-plan.md",
        ...     entity_type=EntityType.TASK,
        ...     entity_id=240
        ... )
    """
    query = "SELECT * FROM document_references WHERE file_path = ?"
    params = [file_path]

    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)

    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        row = cursor.fetchone()

    if not row:
        return None

    return DocumentReferenceAdapter.from_db(dict(row))


def search_documents_by_metadata(
    service,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    component: Optional[str] = None,
    domain: Optional[str] = None,
    audience: Optional[str] = None,
    maturity: Optional[str] = None,
    phase: Optional[str] = None,
    limit: Optional[int] = None
) -> List[DocumentReference]:
    """
    Search documents by Universal Documentation System metadata.

    Args:
        service: DatabaseService instance
        category: Filter by category (planning, architecture, guides, etc.)
        tags: Filter by tags (documents matching ANY tag)
        component: Filter by component
        domain: Filter by domain
        audience: Filter by audience (developer, user, admin, stakeholder)
        maturity: Filter by maturity (draft, review, approved, deprecated)
        phase: Filter by SDLC phase
        limit: Maximum results

    Returns:
        List of matching DocumentReference models

    Example:
        >>> # Find all architecture documents
        >>> docs = search_documents_by_metadata(db, category="architecture")
        >>> # Find documents with specific tags
        >>> docs = search_documents_by_metadata(db, tags=["api", "rest"])
        >>> # Find developer guides
        >>> docs = search_documents_by_metadata(
        ...     db, category="guides", audience="developer"
        ... )
    """
    query = "SELECT * FROM document_references WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if tags:
        # Search for documents containing ANY of the provided tags
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        query += f" AND ({' OR '.join(tag_conditions)})"

    if component:
        query += " AND component = ?"
        params.append(component)

    if domain:
        query += " AND domain = ?"
        params.append(domain)

    if audience:
        query += " AND audience = ?"
        params.append(audience)

    if maturity:
        query += " AND maturity = ?"
        params.append(maturity)

    if phase:
        query += " AND phase = ?"
        params.append(phase)

    query += " ORDER BY created_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [DocumentReferenceAdapter.from_db(dict(row)) for row in rows]


def count_documents_by_category(service) -> dict:
    """
    Count documents by category.

    Args:
        service: DatabaseService instance

    Returns:
        Dict mapping category names to document counts

    Example:
        >>> counts = count_documents_by_category(db)
        >>> counts
        {'architecture': 12, 'guides': 8, 'reference': 5}
    """
    query = """
        SELECT category, COUNT(*) as count
        FROM document_references
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """

    with service.connect() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}


def count_documents_by_maturity(service) -> dict:
    """
    Count documents by maturity level.

    Args:
        service: DatabaseService instance

    Returns:
        Dict mapping maturity levels to document counts

    Example:
        >>> counts = count_documents_by_maturity(db)
        >>> counts
        {'approved': 15, 'review': 5, 'draft': 8, 'deprecated': 2}
    """
    query = """
        SELECT maturity, COUNT(*) as count
        FROM document_references
        WHERE maturity IS NOT NULL
        GROUP BY maturity
        ORDER BY count DESC
    """

    with service.connect() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}


# ============================================================================
# Content Storage Methods (WI-133: Hybrid Storage System - Migration 0039)
# ============================================================================


def create_document_with_content(
    service,
    document: DocumentReference,
    content: str
) -> DocumentReference:
    """
    Create document with content stored in database.

    For hybrid storage: Database stores content + metadata, file sync is automatic.
    Sets content_updated_at and sync_status=PENDING to trigger file sync.

    Args:
        service: DatabaseService instance
        document: DocumentReference model
        content: Full document text content

    Returns:
        Created DocumentReference with content

    Example:
        >>> from agentpm.core.database.enums import EntityType, DocumentType, StorageMode, SyncStatus
        >>> from datetime import datetime
        >>> doc = DocumentReference(
        ...     entity_type=EntityType.WORK_ITEM,
        ...     entity_id=133,
        ...     category="architecture",
        ...     document_type=DocumentType.DESIGN_DOC,
        ...     filename="hybrid-storage.md",
        ...     file_path="docs/architecture/design_doc/hybrid-storage.md",
        ...     title="Hybrid Storage Design",
        ...     storage_mode=StorageMode.HYBRID
        ... )
        >>> content = "# Hybrid Storage\\n\\nDatabase is source of truth..."
        >>> created = create_document_with_content(db, doc, content)
        >>> assert created.content == content
        >>> assert created.sync_status == SyncStatus.PENDING
    """
    from datetime import datetime
    from ..enums import SyncStatus

    # Set content and timestamps
    document.content = content
    document.content_updated_at = datetime.utcnow()
    document.sync_status = SyncStatus.PENDING  # Mark for file sync

    # Create document
    return create_document_reference(service, document)


def update_document_content(
    service,
    document_id: int,
    content: str
) -> Optional[DocumentReference]:
    """
    Update document content and mark for sync.

    Updates content in database (source of truth) and marks document for file sync.
    File sync daemon will detect PENDING status and write file.

    Args:
        service: DatabaseService instance
        document_id: Document reference ID
        content: New document content

    Returns:
        Updated DocumentReference, or None if not found

    Example:
        >>> doc = get_document_reference(db, 1)
        >>> updated = update_document_content(db, 1, "# Updated Content\\n\\nNew text...")
        >>> assert updated.content == "# Updated Content\\n\\nNew text..."
        >>> assert updated.sync_status == SyncStatus.PENDING
        >>> assert updated.content_updated_at is not None
    """
    from datetime import datetime
    from ..enums import SyncStatus

    doc = get_document_reference(service, document_id)
    if not doc:
        return None

    # Update content and timestamps
    doc.content = content
    doc.content_updated_at = datetime.utcnow()
    doc.sync_status = SyncStatus.PENDING  # Mark for file sync

    return update_document_reference(service, doc)


def get_document_content(service, document_id: int) -> Optional[str]:
    """
    Retrieve document content from database.

    Database is source of truth for content. File is synchronized cache.

    Args:
        service: DatabaseService instance
        document_id: Document reference ID

    Returns:
        Document content string, or None if not found or no content

    Example:
        >>> content = get_document_content(db, 1)
        >>> if content:
        ...     print(content[:100])  # First 100 chars
    """
    doc = get_document_reference(service, document_id)
    return doc.content if doc else None


def get_documents_needing_sync(service) -> List[DocumentReference]:
    """
    Get documents where sync_status != 'synced'.

    Used by file sync daemon to find documents that need file updates.
    Includes documents with status: PENDING, CONFLICT, ERROR.

    Args:
        service: DatabaseService instance

    Returns:
        List of DocumentReference models needing sync

    Example:
        >>> # Sync daemon workflow
        >>> docs = get_documents_needing_sync(db)
        >>> for doc in docs:
        ...     if doc.sync_status == SyncStatus.PENDING:
        ...         write_file(doc.computed_path, doc.content)
        ...         mark_synced(db, doc.id)
        ...     elif doc.sync_status == SyncStatus.CONFLICT:
        ...         resolve_conflict(db, doc)
    """
    from ..enums import SyncStatus

    query = """
        SELECT * FROM document_references
        WHERE sync_status != ?
        ORDER BY content_updated_at DESC
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (SyncStatus.SYNCED.value,))
        rows = cursor.fetchall()

    return [DocumentReferenceAdapter.from_db(dict(row)) for row in rows]


def mark_document_synced(
    service,
    document_id: int
) -> Optional[DocumentReference]:
    """
    Mark document as synced after successful file write.

    Updates sync_status=SYNCED and last_synced_at timestamp.
    Called by file sync daemon after writing file.

    Args:
        service: DatabaseService instance
        document_id: Document reference ID

    Returns:
        Updated DocumentReference, or None if not found

    Example:
        >>> # After successful file write
        >>> doc = mark_document_synced(db, 1)
        >>> assert doc.sync_status == SyncStatus.SYNCED
        >>> assert doc.last_synced_at is not None
    """
    from datetime import datetime
    from ..enums import SyncStatus

    doc = get_document_reference(service, document_id)
    if not doc:
        return None

    doc.sync_status = SyncStatus.SYNCED
    doc.last_synced_at = datetime.utcnow()

    return update_document_reference(service, doc)


def search_document_content(
    service,
    search_query: str,
    limit: Optional[int] = 20
) -> List[DocumentReference]:
    """
    Full-text search across document content, titles, and filenames.

    Uses FTS5 virtual table for fast search.
    Searches content, title, and filename fields.

    Args:
        service: DatabaseService instance
        search_query: Search query (FTS5 syntax)
        limit: Maximum results (default: 20)

    Returns:
        List of matching DocumentReference models ranked by relevance

    Example:
        >>> # Search for "authentication" in content
        >>> docs = search_document_content(db, "authentication")
        >>> # Search for phrase
        >>> docs = search_document_content(db, '"hybrid storage"')
        >>> # Search with boolean operators
        >>> docs = search_document_content(db, "database AND sync")
    """
    # Note: FTS search requires FTS table populated
    # This is a placeholder for future implementation when sync system is active
    query = """
        SELECT dr.*
        FROM document_references dr
        JOIN document_content_fts fts ON dr.id = fts.document_id
        WHERE document_content_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """

    try:
        with service.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (search_query, limit or 20))
            rows = cursor.fetchall()

        return [DocumentReferenceAdapter.from_db(dict(row)) for row in rows]
    except sqlite3.OperationalError:
        # FTS table might not be populated yet, fall back to LIKE search
        fallback_query = """
            SELECT * FROM document_references
            WHERE content LIKE ? OR title LIKE ? OR filename LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """
        pattern = f"%{search_query}%"

        with service.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                fallback_query,
                (pattern, pattern, pattern, limit or 20)
            )
            rows = cursor.fetchall()

        return [DocumentReferenceAdapter.from_db(dict(row)) for row in rows]
