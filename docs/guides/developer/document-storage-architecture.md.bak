# Document Storage Architecture - Developer Guide

Technical guide to APM (Agent Project Manager)'s hybrid document storage system implementation, architecture, and extension patterns.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Hybrid Storage Strategy](#hybrid-storage-strategy)
3. [Database Schema](#database-schema)
4. [Sync Algorithm](#sync-algorithm)
5. [FTS5 Search Implementation](#fts5-search-implementation)
6. [Extending the System](#extending-the-system)
7. [Performance Considerations](#performance-considerations)
8. [Testing Guide](#testing-guide)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Document Storage System                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  Pydantic Models │  │  Database Layer  │  │  Filesystem     │  │
│  │                  │  │                  │  │  Layer          │  │
│  │ • DocumentRef    │◄─┤ • SQLite         │◄─┤ • Path mgmt     │  │
│  │ • Validation     │  │ • FTS5 indexes   │  │ • File I/O      │  │
│  │ • Serialization  │  │ • Transactions   │  │ • Hash verify   │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
│          ▲                     ▲                      ▲             │
│          │                     │                      │             │
│  ┌───────┴─────────────────────┴──────────────────────┴─────────┐  │
│  │              Service Layer (Business Logic)                   │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ • ContentSyncService     • SearchService                      │  │
│  │ • ConflictResolver       • IndexManager                       │  │
│  │ • IntegrityValidator     • MetadataExtractor                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│          ▲                                                           │
│          │                                                           │
│  ┌───────┴────────────────────────────────────────────────────┐    │
│  │                    CLI Commands                             │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ • document add        • document search                     │    │
│  │ • document sync       • document verify                     │    │
│  │ • document regenerate • document reindex                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Components |
|-------|---------------|------------|
| **CLI** | User interaction, command routing | Click commands, argument parsing |
| **Service** | Business logic, coordination | Sync, search, conflict resolution |
| **Database** | Persistence, indexing, queries | SQLite, FTS5, transactions |
| **Model** | Data validation, serialization | Pydantic models, validators |
| **Filesystem** | File I/O, path management | Path construction, hash verification |

### Data Flow

**Document Creation**:
```python
CLI (document add)
  → Service (validate_and_create)
    → Model (DocumentReference validation)
      → Database (insert with content)
        → FTS5 (index content)
      → Filesystem (write file)
        → Hash (compute SHA-256)
      → Database (update hash)
```

**Document Search**:
```python
CLI (document search)
  → Service (search_content)
    → FTS5 (full-text query)
      → Ranking (BM25 algorithm)
    → Database (fetch metadata)
      → Model (deserialize)
    → Service (format snippets)
  → CLI (display results)
```

**Document Sync**:
```python
CLI (document sync)
  → Service (sync_document)
    → Filesystem (read file content + hash)
    → Database (read stored content + hash)
    → Service (compare hashes)
      → If match: No-op
      → If mismatch: ConflictResolver
        → Strategy: db-wins | file-wins | manual | merge
        → Action: Update database or file
        → FTS5 (reindex if content changed)
```

---

## Hybrid Storage Strategy

### Core Principle: Database as Source of Truth

**Philosophy**:
- Database is the **authoritative source** for all content
- Files are **regenerable cache** optimized for git and IDE workflows
- Sync keeps both in sync, but database wins by default

### Why Hybrid?

| Requirement | Database-Only | File-Only | Hybrid |
|-------------|---------------|-----------|--------|
| Single source of truth | ✅ | ❌ | ✅ (database) |
| Git-friendly diffs | ❌ | ✅ | ✅ (files) |
| IDE editing support | ❌ | ✅ | ✅ (files) |
| Full-text search | ✅ | ❌ | ✅ (FTS5) |
| Metadata queries | ✅ | ❌ | ✅ (database) |
| Transaction safety | ✅ | ❌ | ✅ (database) |
| Complexity | Low | Low | **Medium** |

### Storage Responsibilities

**Database Stores**:
- Full document content (`content` TEXT field)
- All metadata (category, type, tags, etc.)
- Content hash (SHA-256 for integrity)
- FTS5 indexes (for search)
- Timestamps (created, updated)

**Filesystem Stores**:
- File copies (synchronized from database)
- Git-trackable changes
- IDE-editable versions

**Not Duplicated**:
- Metadata (database only)
- FTS5 indexes (database only)
- Binary content (future: separate blob storage)

### Sync Guarantees

1. **Idempotency**: Syncing same content multiple times has no effect
2. **Atomicity**: Database updates are transactional (rollback on error)
3. **Consistency**: Content hash ensures integrity
4. **Isolation**: Concurrent syncs use database locks
5. **Durability**: Database persists to disk immediately

---

## Database Schema

### Core Table: `document_references`

```sql
CREATE TABLE IF NOT EXISTS document_references (
    -- Identity
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Entity Association
    entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
    entity_id INTEGER NOT NULL CHECK(entity_id > 0),

    -- File Metadata
    file_path TEXT NOT NULL CHECK(length(file_path) > 0),
    title TEXT,
    description TEXT,
    file_size_bytes INTEGER CHECK(file_size_bytes >= 0),
    content_hash TEXT,  -- SHA-256 hash
    format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),

    -- Content Storage (NEW in WI-133)
    content TEXT,  -- Full document content

    -- Classification
    category TEXT,  -- planning, architecture, guides, etc.
    document_type TEXT CHECK(document_type IN ('requirements', 'design', ...)),
    document_type_dir TEXT,

    -- Rich Metadata
    segment_type TEXT,
    component TEXT,
    domain TEXT,
    audience TEXT,
    maturity TEXT,
    priority TEXT,
    tags TEXT,  -- JSON array

    -- Workflow
    phase TEXT,
    work_item_id INTEGER,

    -- Lifecycle
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(entity_type, entity_id, file_path),
    CHECK (
        file_path LIKE 'docs/%'
        OR file_path IN ('CHANGELOG.md', 'README.md', 'LICENSE.md')
        OR (file_path LIKE '%.md' AND file_path NOT LIKE '%/%')
        OR file_path GLOB 'agentpm/*/README.md'
        OR file_path LIKE 'testing/%'
        OR file_path LIKE 'tests/%'
    )
);
```

### FTS5 Virtual Table (NEW in WI-133)

```sql
-- Full-text search index
CREATE VIRTUAL TABLE document_content_fts USING fts5(
    document_id UNINDEXED,
    file_path,
    title,
    content,
    content=document_references,
    content_rowid=id
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER document_ai AFTER INSERT ON document_references BEGIN
    INSERT INTO document_content_fts(document_id, file_path, title, content)
    VALUES (new.id, new.file_path, new.title, new.content);
END;

CREATE TRIGGER document_ad AFTER DELETE ON document_references BEGIN
    INSERT INTO document_content_fts(document_content_fts, document_id, file_path, title, content)
    VALUES('delete', old.id, old.file_path, old.title, old.content);
END;

CREATE TRIGGER document_au AFTER UPDATE ON document_references BEGIN
    INSERT INTO document_content_fts(document_content_fts, document_id, file_path, title, content)
    VALUES('delete', old.id, old.file_path, old.title, old.content);
    INSERT INTO document_content_fts(document_id, file_path, title, content)
    VALUES (new.id, new.file_path, new.title, new.content);
END;
```

### Indexes for Performance

```sql
-- Category filtering
CREATE INDEX idx_doc_category ON document_references(category);

-- Document type filtering
CREATE INDEX idx_doc_type_dir ON document_references(document_type_dir);

-- Combined category + type
CREATE INDEX idx_doc_cat_type ON document_references(category, document_type_dir);

-- Maturity lifecycle queries
CREATE INDEX idx_doc_maturity ON document_references(maturity);

-- Component-based queries
CREATE INDEX idx_doc_component ON document_references(component);

-- Hash lookups (integrity checks)
CREATE INDEX idx_doc_hash ON document_references(content_hash);
```

### Schema Evolution

**Migration Strategy**:
```python
# migration_0034_document_content_storage.py

def upgrade(db: Database):
    """Add content storage and FTS5 indexes."""

    # 1. Add content column
    db.execute("""
        ALTER TABLE document_references
        ADD COLUMN content TEXT
    """)

    # 2. Create FTS5 virtual table
    db.execute("""
        CREATE VIRTUAL TABLE document_content_fts USING fts5(
            document_id UNINDEXED,
            file_path,
            title,
            content,
            content=document_references,
            content_rowid=id
        )
    """)

    # 3. Create sync triggers
    create_fts5_triggers(db)

    # 4. Populate content from existing files
    sync_existing_documents(db)

    # 5. Build FTS5 index
    db.execute("INSERT INTO document_content_fts(document_content_fts) VALUES('rebuild')")

def downgrade(db: Database):
    """Remove content storage (data loss!)."""
    db.execute("DROP TABLE document_content_fts")
    # Note: Cannot drop column in SQLite, requires table recreation
```

---

## Sync Algorithm

### Conflict Detection

```python
class ContentSyncService:
    """Bidirectional content synchronization."""

    def sync_document(
        self,
        file_path: str,
        strategy: SyncStrategy = SyncStrategy.DB_WINS
    ) -> SyncResult:
        """
        Sync document between database and filesystem.

        Algorithm:
        1. Read file content + compute hash
        2. Read database content + stored hash
        3. Compare hashes:
           - Match: No-op (already in sync)
           - Mismatch: Conflict detected
        4. Apply resolution strategy
        5. Update database or file
        6. Recompute and store new hash
        7. Reindex FTS5 if content changed
        """

        # 1. Read file
        file_content = self._read_file(file_path)
        file_hash = self._compute_hash(file_content)

        # 2. Read database
        doc = self.db.document_methods.get_by_path(file_path)
        db_content = doc.content
        db_hash = doc.content_hash

        # 3. Compare hashes
        if file_hash == db_hash:
            return SyncResult(status="in_sync", action="none")

        # 4. Conflict detected - apply strategy
        conflict = Conflict(
            file_content=file_content,
            file_hash=file_hash,
            db_content=db_content,
            db_hash=db_hash,
            file_modified=self._get_file_mtime(file_path),
            db_modified=doc.updated_at
        )

        resolution = self._resolve_conflict(conflict, strategy)

        # 5. Apply resolution
        if resolution.action == "update_db":
            self._update_database(doc.id, file_content, file_hash)
            return SyncResult(status="synced", action="db_updated")

        elif resolution.action == "update_file":
            self._write_file(file_path, db_content)
            return SyncResult(status="synced", action="file_updated")

        elif resolution.action == "merge":
            merged_content = self._merge_content(file_content, db_content)
            self._update_database(doc.id, merged_content, self._compute_hash(merged_content))
            self._write_file(file_path, merged_content)
            return SyncResult(status="merged", action="both_updated")

        else:
            raise ValueError(f"Unknown resolution action: {resolution.action}")

    def _resolve_conflict(
        self,
        conflict: Conflict,
        strategy: SyncStrategy
    ) -> Resolution:
        """Apply conflict resolution strategy."""

        if strategy == SyncStrategy.DB_WINS:
            return Resolution(action="update_file", reason="db_authoritative")

        elif strategy == SyncStrategy.FILE_WINS:
            return Resolution(action="update_db", reason="file_newer")

        elif strategy == SyncStrategy.MANUAL:
            # Prompt user for choice
            choice = self._prompt_user(conflict)
            return Resolution(action=choice, reason="user_selected")

        elif strategy == SyncStrategy.MERGE:
            # Attempt automatic merge
            if self._can_merge_safely(conflict):
                return Resolution(action="merge", reason="no_conflicts")
            else:
                # Fall back to manual
                return self._resolve_conflict(conflict, SyncStrategy.MANUAL)

        else:
            raise ValueError(f"Unknown strategy: {strategy}")
```

### Hash Computation

```python
import hashlib

class HashService:
    """Content integrity via SHA-256 hashing."""

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute SHA-256 hash of content.

        Args:
            content: Document content as string

        Returns:
            Hex-encoded SHA-256 hash (64 chars)
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_integrity(file_path: str, expected_hash: str) -> bool:
        """
        Verify file content matches expected hash.

        Args:
            file_path: Path to file
            expected_hash: Expected SHA-256 hash

        Returns:
            True if hash matches, False otherwise
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        actual_hash = HashService.compute_hash(content)
        return actual_hash == expected_hash
```

### Transaction Safety

```python
class DocumentService:
    """Transactional document operations."""

    def create_document_with_content(
        self,
        doc: DocumentReference,
        content: str
    ) -> DocumentReference:
        """
        Atomically create document in database and filesystem.

        Rollback on any error to maintain consistency.
        """
        try:
            # Begin database transaction
            with self.db.transaction():
                # 1. Compute hash
                content_hash = HashService.compute_hash(content)

                # 2. Insert database record
                doc.content = content
                doc.content_hash = content_hash
                doc.file_size_bytes = len(content.encode('utf-8'))
                doc_id = self.db.document_methods.create(doc)

                # 3. Write file (outside transaction)
                # If this fails, transaction rollback deletes DB record
                self._write_file(doc.file_path, content)

                # 4. Verify file written correctly
                if not HashService.verify_integrity(doc.file_path, content_hash):
                    raise IntegrityError("File hash mismatch after write")

                # Transaction commits automatically
                return self.db.document_methods.get(doc_id)

        except Exception as e:
            # Transaction rolled back automatically
            # Clean up file if it was written
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            raise DocumentCreationError(f"Failed to create document: {e}")
```

---

## FTS5 Search Implementation

### Full-Text Search Architecture

```python
class DocumentSearchService:
    """FTS5-powered document search."""

    def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search documents using FTS5.

        Args:
            query: Search terms (supports FTS5 syntax)
            filters: Metadata filters (category, type, etc.)
            limit: Max results to return

        Returns:
            List of search results with snippets and ranking
        """

        # Build FTS5 query
        fts_query = self._build_fts_query(query)

        # Build filter WHERE clauses
        filter_clauses = self._build_filters(filters) if filters else []

        # Execute search
        sql = f"""
            SELECT
                dr.id,
                dr.file_path,
                dr.title,
                dr.document_type,
                dr.category,
                dr.maturity,
                snippet(document_content_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                bm25(document_content_fts) as rank
            FROM document_content_fts fts
            JOIN document_references dr ON dr.id = fts.document_id
            WHERE fts MATCH ?
                {' AND '.join(filter_clauses) if filter_clauses else ''}
            ORDER BY rank
            LIMIT ?
        """

        results = self.db.execute(sql, (fts_query, limit))

        return [
            SearchResult(
                id=row['id'],
                file_path=row['file_path'],
                title=row['title'],
                snippet=row['snippet'],
                rank=row['rank'],
                metadata=self._extract_metadata(row)
            )
            for row in results
        ]

    def _build_fts_query(self, query: str) -> str:
        """
        Build FTS5 query from user input.

        Supports:
        - Phrase matching: "exact phrase"
        - Boolean: term1 AND term2, term1 OR term2
        - Wildcards: auth*
        - Column search: title:design
        """
        # Sanitize and validate query
        # Add column prefixes for multi-field search
        return f"{query}"  # Simplified - add advanced parsing

    def _build_filters(self, filters: SearchFilters) -> List[str]:
        """Build SQL WHERE clauses from filters."""
        clauses = []

        if filters.category:
            clauses.append(f"dr.category = '{filters.category}'")

        if filters.document_type:
            clauses.append(f"dr.document_type = '{filters.document_type}'")

        if filters.maturity:
            clauses.append(f"dr.maturity = '{filters.maturity}'")

        if filters.component:
            clauses.append(f"dr.component = '{filters.component}'")

        return clauses
```

### FTS5 Query Examples

**Basic Search**:
```sql
SELECT * FROM document_content_fts WHERE document_content_fts MATCH 'authentication';
```

**Phrase Search**:
```sql
SELECT * FROM document_content_fts WHERE document_content_fts MATCH '"OAuth2 flow"';
```

**Boolean Search**:
```sql
SELECT * FROM document_content_fts WHERE document_content_fts MATCH 'authentication AND oauth2';
```

**Wildcard Search**:
```sql
SELECT * FROM document_content_fts WHERE document_content_fts MATCH 'auth*';
```

**Column-Specific Search**:
```sql
SELECT * FROM document_content_fts WHERE document_content_fts MATCH 'title:design';
```

**Ranked Results with Snippets**:
```sql
SELECT
    file_path,
    title,
    snippet(document_content_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
    bm25(document_content_fts) as rank
FROM document_content_fts
WHERE document_content_fts MATCH 'hybrid storage'
ORDER BY rank
LIMIT 10;
```

### Index Maintenance

```python
class FTS5IndexManager:
    """FTS5 index maintenance."""

    def rebuild_index(self):
        """Rebuild entire FTS5 index from document_references."""
        self.db.execute("""
            INSERT INTO document_content_fts(document_content_fts)
            VALUES('rebuild')
        """)

    def optimize_index(self):
        """Optimize FTS5 index (merge segments)."""
        self.db.execute("""
            INSERT INTO document_content_fts(document_content_fts)
            VALUES('optimize')
        """)

    def verify_index_integrity(self) -> bool:
        """Verify FTS5 index matches source table."""
        self.db.execute("""
            INSERT INTO document_content_fts(document_content_fts)
            VALUES('integrity-check')
        """)
        # Returns True if check passes
```

---

## Extending the System

### Adding New Document Types

**1. Update Enum**:
```python
# agentpm/core/database/enums/types.py

class DocumentType(str, Enum):
    # ... existing types ...

    # Add new type
    TECHNICAL_MEMO = "technical_memo"
```

**2. Update Category Mapping**:
```python
# agentpm/core/database/enums/types.py

DOCUMENT_CATEGORY_MAP = {
    # ... existing mappings ...
    DocumentType.TECHNICAL_MEMO: DocumentCategory.COMMUNICATION,
}
```

**3. Create Migration**:
```python
# migration_0035_add_technical_memo.py

def upgrade(db: Database):
    # SQLite CHECK constraint requires table recreation
    # Use ALTER TABLE workaround or recreate table
    pass
```

**4. Update CLI**:
```python
# agentpm/cli/commands/document.py

# Type automatically available via enum
# No changes needed!
```

### Adding Custom Metadata Fields

**1. Add Column**:
```python
# migration_0036_custom_metadata.py

def upgrade(db: Database):
    db.execute("""
        ALTER TABLE document_references
        ADD COLUMN custom_metadata TEXT  -- JSON
    """)
```

**2. Update Model**:
```python
# agentpm/core/database/models/document_reference.py

class DocumentReference(BaseModel):
    # ... existing fields ...

    custom_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom metadata as JSON"
    )

    @field_validator('custom_metadata', mode='before')
    @classmethod
    def parse_custom_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
```

**3. Update Adapter**:
```python
# agentpm/core/database/adapters/document_reference_adapter.py

class DocumentReferenceAdapter:
    @staticmethod
    def to_db(doc: DocumentReference) -> dict:
        db_dict = {...}

        # Serialize custom metadata
        if doc.custom_metadata:
            db_dict['custom_metadata'] = json.dumps(doc.custom_metadata)

        return db_dict
```

### Custom Sync Strategies

```python
class CustomSyncStrategy:
    """Custom conflict resolution strategy."""

    def resolve(self, conflict: Conflict) -> Resolution:
        """
        Custom resolution logic.

        Example: Choose based on file size
        """
        file_size = len(conflict.file_content)
        db_size = len(conflict.db_content)

        if file_size > db_size:
            # File has more content, likely newer
            return Resolution(action="update_db", reason="file_larger")
        else:
            return Resolution(action="update_file", reason="db_larger")

# Register custom strategy
SyncStrategy.register("size-based", CustomSyncStrategy)

# Use in CLI
apm document sync --file-path="..." --strategy=size-based
```

---

## Performance Considerations

### Database Performance

**Indexes**:
- Add indexes for frequently queried columns
- Avoid over-indexing (slows writes)
- Use composite indexes for multi-column queries

**FTS5 Performance**:
- Rebuild index periodically: `INSERT INTO fts(fts) VALUES('optimize')`
- Use column-specific queries: `title:design` instead of `design`
- Limit result sets: Always use `LIMIT` clause

**Transaction Batching**:
```python
# Slow: Individual transactions
for doc in documents:
    db.document_methods.create(doc)

# Fast: Batch transaction
with db.transaction():
    for doc in documents:
        db.document_methods.create(doc)
```

### Filesystem Performance

**Bulk Operations**:
```python
# Slow: Sync one at a time
for doc in documents:
    sync_service.sync_document(doc.file_path)

# Fast: Parallel sync
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(sync_service.sync_document, doc.file_path)
        for doc in documents
    ]
    results = [f.result() for f in futures]
```

**Caching**:
```python
class CachedDocumentService:
    """Cache frequently accessed documents."""

    def __init__(self):
        self.cache = LRUCache(maxsize=100)

    def get_document(self, doc_id: int) -> DocumentReference:
        if doc_id in self.cache:
            return self.cache[doc_id]

        doc = self.db.document_methods.get(doc_id)
        self.cache[doc_id] = doc
        return doc
```

### Large Document Handling

**Streaming Content**:
```python
def stream_large_document(file_path: str) -> Iterator[str]:
    """Stream large document in chunks."""
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(8192)  # 8KB chunks
            if not chunk:
                break
            yield chunk
```

**Content Compression** (Future):
```python
import zlib

def compress_content(content: str) -> bytes:
    """Compress content before storing."""
    return zlib.compress(content.encode('utf-8'))

def decompress_content(compressed: bytes) -> str:
    """Decompress stored content."""
    return zlib.decompress(compressed).decode('utf-8')
```

---

## Testing Guide

### Unit Tests

**Test Document Creation**:
```python
def test_create_document_with_content(db, tmp_path):
    """Test document creation stores content in both DB and file."""

    # Arrange
    service = DocumentService(db)
    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=133,
        file_path=str(tmp_path / "docs/test.md"),
        document_type=DocumentType.DESIGN,
        title="Test Document"
    )
    content = "# Test\n\nThis is test content."

    # Act
    created = service.create_document_with_content(doc, content)

    # Assert
    # Database has content
    assert created.content == content
    assert created.content_hash == HashService.compute_hash(content)

    # File exists with same content
    assert os.path.exists(doc.file_path)
    with open(doc.file_path, 'r') as f:
        assert f.read() == content

    # FTS5 indexed
    results = service.search("test content")
    assert len(results) == 1
    assert results[0].id == created.id
```

**Test Sync Algorithm**:
```python
def test_sync_detects_conflict(db, tmp_path):
    """Test sync detects hash mismatch."""

    # Arrange
    service = ContentSyncService(db)
    doc = create_test_document(db, tmp_path)

    # Modify file (external edit)
    with open(doc.file_path, 'w') as f:
        f.write("# Modified Content")

    # Act
    result = service.sync_document(doc.file_path, strategy=SyncStrategy.DB_WINS)

    # Assert
    assert result.status == "synced"
    assert result.action == "file_updated"

    # File now matches database
    with open(doc.file_path, 'r') as f:
        assert f.read() == doc.content
```

### Integration Tests

**Test End-to-End Workflow**:
```python
def test_document_lifecycle(cli_runner, db, tmp_path):
    """Test complete document lifecycle."""

    # 1. Create document
    result = cli_runner.invoke(cli, [
        'document', 'add',
        '--entity-type=work_item',
        '--entity-id=133',
        f'--file-path={tmp_path}/docs/test.md',
        '--type=design',
        '--content=# Test Document'
    ])
    assert result.exit_code == 0

    # 2. Verify file created
    assert os.path.exists(tmp_path / 'docs/test.md')

    # 3. Edit file
    with open(tmp_path / 'docs/test.md', 'a') as f:
        f.write('\n\nAdditional content')

    # 4. Sync changes
    result = cli_runner.invoke(cli, [
        'document', 'sync',
        f'--file-path={tmp_path}/docs/test.md'
    ])
    assert result.exit_code == 0

    # 5. Search content
    result = cli_runner.invoke(cli, [
        'document', 'search',
        'Additional content'
    ])
    assert result.exit_code == 0
    assert 'test.md' in result.output
```

### Performance Tests

**Test FTS5 Performance**:
```python
import time

def test_search_performance(db):
    """Test FTS5 search scales with document count."""

    # Create 1000 documents
    for i in range(1000):
        create_test_document(db, f"Document {i}", f"Content for doc {i}")

    # Measure search time
    start = time.time()
    results = db.search("content")
    elapsed = time.time() - start

    # Should complete in < 100ms
    assert elapsed < 0.1
    assert len(results) <= 50  # Limit enforced
```

**Test Sync Performance**:
```python
def test_bulk_sync_performance(db, tmp_path):
    """Test syncing 100 documents completes quickly."""

    # Create 100 documents
    docs = [create_test_document(db, tmp_path, i) for i in range(100)]

    # Modify all files
    for doc in docs:
        with open(doc.file_path, 'a') as f:
            f.write('\nModified')

    # Measure sync time
    start = time.time()
    service = ContentSyncService(db)
    results = [service.sync_document(doc.file_path) for doc in docs]
    elapsed = time.time() - start

    # Should complete in < 5 seconds
    assert elapsed < 5.0
    assert all(r.status == 'synced' for r in results)
```

---

## Troubleshooting

### Common Issues

**Issue: FTS5 not available**

```python
# Check if FTS5 compiled
import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.execute("PRAGMA compile_options")
options = [row[0] for row in cursor.fetchall()]
assert 'ENABLE_FTS5' in options
```

**Issue: Hash mismatches after legitimate edits**

```python
# Expected behavior! Sync to update hash
service.sync_document(file_path, strategy=SyncStrategy.FILE_WINS)
```

**Issue: Slow FTS5 queries**

```python
# Optimize index
db.execute("INSERT INTO document_content_fts(document_content_fts) VALUES('optimize')")
```

---

## Next Steps

- **User Guide**: See `docs/guides/user_guide/document-content-management.md`
- **ADR**: See `docs/planning/adr/ADR-015-hybrid-document-storage.md`
- **API Reference**: See `agentpm/core/database/methods/document_references.py`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Related**: WI-133 (Hybrid Document Storage System)
**Status**: Draft (pending implementation)
