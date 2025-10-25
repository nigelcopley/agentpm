# Hybrid Document Storage Architecture

Enterprise-grade document management system with database-first storage and bidirectional file synchronization.

---

## Executive Summary

This architecture transforms APM (Agent Project Manager)'s document system from a file-centric to a database-centric approach while preserving developer-friendly file-based workflows. The database becomes the authoritative source of truth for document content, while filesystem copies serve as synchronized caches enabling git diffs, IDE editing, and traditional file operations.

**Key Design Principles**:
- Database-first: Content stored in SQLite with full ACID guarantees
- Git-friendly: Filesystem copies enable meaningful diffs and version control
- IDE-friendly: Developers can edit documents using familiar tools
- Performance-optimized: Full-text search, content hash indexing, and efficient sync
- Migration-ready: Backward compatible with existing 165+ documents
- Future-proof: Foundation for advanced features (versioning, collaboration, search)

**Benefits**:
- **Query Performance**: Content retrieval <50ms from database (vs file I/O)
- **Search Capability**: SQLite FTS5 enables full-text search across all documents
- **Data Integrity**: ACID transactions, foreign keys, and content hashing
- **Flexibility**: Three storage modes (HYBRID, DATABASE_ONLY, FILE_ONLY) for different use cases
- **Developer Experience**: Transparent sync maintains familiar file-based workflows

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Proposed Architecture](#proposed-architecture)
3. [Storage Modes](#storage-modes)
4. [Database Schema Design](#database-schema-design)
5. [Sync Strategy](#sync-strategy)
6. [Performance Analysis](#performance-analysis)
7. [Migration Plan](#migration-plan)
8. [Security Considerations](#security-considerations)
9. [Future Enhancements](#future-enhancements)

---

## Current State Analysis

### Existing System

**Database**: `document_references` table (metadata only)
```sql
-- Current schema (simplified)
CREATE TABLE document_references (
  id INTEGER PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  title TEXT,
  content_hash TEXT,  -- SHA256 of file content
  format TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  -- Plus metadata: category, document_type, component, etc.
);
```

**File System**: 165+ documents in structured hierarchy
```
docs/
├── architecture/
│   ├── design/           # 15+ design documents
│   ├── adr/              # Architecture Decision Records
│   └── summary/
├── planning/
│   └── requirements/     # Requirements documents
├── guides/
│   ├── user_guide/
│   └── developer_guide/
└── ... (8 categories total)
```

### Current Limitations

1. **Content Not Queryable**: Must read files to search/analyze content
2. **No Full-Text Search**: Cannot search across document corpus
3. **No Content Versioning**: Git provides file-level tracking only
4. **Fragile References**: File moves break database references
5. **Synchronization Issues**: Hash mismatches require manual reconciliation
6. **Limited Metadata**: Filename and structure dictate organization

### Design Constraints

1. **Preserve Git Workflow**: Developers rely on file-based diffs
2. **IDE Compatibility**: Must support standard editor workflows
3. **Backward Compatible**: 165+ existing documents must migrate smoothly
4. **Performance**: No degradation in retrieval/search operations
5. **Database Size**: SQLite handles 140GB+ but keep reasonable (target <100MB)
6. **AIPM Patterns**: Follow database-first, three-tier architecture

---

## Proposed Architecture

### Architectural Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  CLI        │  │  IDE/Editor │  │  Git        │             │
│  │  Commands   │  │  File Ops   │  │  Workflow   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Service (business logic)                        │  │
│  │  ├─ CRUD operations                                       │  │
│  │  ├─ Content retrieval (DB-first)                          │  │
│  │  ├─ Search operations (FTS5)                              │  │
│  │  └─ Sync coordination                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sync Service (bidirectional sync)                        │  │
│  │  ├─ Change detection (hash + timestamp)                   │  │
│  │  ├─ Conflict resolution (strategies)                      │  │
│  │  ├─ Sync triggers (on-demand, watch-based)                │  │
│  │  └─ Batch operations                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────┬──────────────────────────────────────┬───────────────┘
          │                                       │
          ▼                                       ▼
┌─────────────────────────┐      ┌─────────────────────────────┐
│   Data Layer            │      │   Filesystem Layer          │
│  ┌──────────────────┐   │      │  ┌──────────────────────┐   │
│  │ document_        │   │◄────►│  │ docs/                │   │
│  │ references       │   │ sync │  │ ├── architecture/    │   │
│  │ (with content)   │   │      │  │ ├── planning/        │   │
│  └──────────────────┘   │      │  │ └── ... (165+ docs)  │   │
│  ┌──────────────────┐   │      │  └──────────────────────┘   │
│  │ document_        │   │      └─────────────────────────────┘
│  │ content_fts      │   │
│  │ (FTS5 index)     │   │       Source of Truth
│  └──────────────────┘   │
└─────────────────────────┘       Synchronized Cache
     Source of Truth               (git-friendly, IDE-friendly)
```

### Core Components

1. **Database Layer** (Source of Truth)
   - `document_references` table: Metadata + content + sync status
   - `document_content_fts` virtual table: Full-text search index
   - Content hash verification (SHA256)
   - Timestamp tracking (created, updated, synced)

2. **Sync Service** (Synchronization Engine)
   - Bidirectional sync: DB ↔ File
   - Change detection: Hash comparison + timestamp analysis
   - Conflict resolution: Configurable strategies
   - Event-driven: File system watchers + on-demand sync

3. **Document Service** (Business Logic)
   - CRUD operations (DB-first)
   - Content retrieval (optimized queries)
   - Search operations (FTS5 queries)
   - Storage mode management

4. **File System** (Synchronized Cache)
   - Structured hierarchy (docs/{category}/{type}/)
   - Git-trackable changes
   - IDE-editable content
   - Generated from database (reproducible)

### Data Flow Patterns

**Write Flow** (User edits file in IDE):
```
IDE (edit file)
  → File watcher detects change
  → Sync service reads file content
  → Hash comparison (file hash ≠ DB hash)
  → Update database content
  → Update content_updated_at, last_synced_at
  → Status: SYNCED
```

**Write Flow** (CLI creates document):
```
CLI command
  → Document service creates DB record
  → Content stored in database
  → Sync service writes file (if HYBRID mode)
  → File created with content
  → Status: SYNCED
```

**Read Flow** (Retrieve document):
```
Query by ID/path
  → Document service queries DB
  → Return content from database (<50ms)
  → (No file I/O required)
```

**Search Flow** (Full-text search):
```
Search query
  → Document service queries FTS5 index
  → Results ranked by relevance
  → Return matching documents with snippets
  → (<200ms for 1000+ docs)
```

---

## Storage Modes

The system supports three storage modes to balance flexibility, performance, and use cases:

### Mode 1: HYBRID (Default, Recommended)

**Characteristics**:
- Content stored in database (authoritative)
- File synchronized to filesystem (cache)
- Database → File sync on read/write
- File → Database sync on change detection

**Use Cases**:
- User-facing documentation (guides, architecture, requirements)
- Team-editable content (developers edit in IDE)
- Git-tracked documents (meaningful diffs)
- Searchable content (FTS5 indexed)

**Benefits**:
- Database queryability + file editability
- Git workflow preserved
- IDE integration seamless
- Full-text search enabled
- Versioning possible (future)

**Tradeoffs**:
- Disk space: Content in DB + files (~2x storage)
- Sync overhead: ~100ms per document write
- Complexity: Conflict resolution needed

**Example**:
```python
# Create document in HYBRID mode
doc = DocumentReference(
    entity_type=EntityType.WORK_ITEM,
    entity_id=133,
    file_path="docs/architecture/design/hybrid-storage.md",
    content="# Document Content\n\nDetails here...",
    storage_mode="hybrid"  # Default
)
# Result: Content in DB + file created at path
```

### Mode 2: DATABASE_ONLY

**Characteristics**:
- Content only in database
- No file created on filesystem
- Database is sole storage location
- Fastest write performance

**Use Cases**:
- Auto-generated reports (session summaries, test reports)
- Ephemeral content (temporary analysis, scratchpad)
- High-frequency updates (metrics, logs)
- Content not needed in git (no human editing)

**Benefits**:
- No file I/O overhead
- No sync complexity
- Faster writes (~50ms vs 100ms)
- Reduced disk usage
- Simplified operations

**Tradeoffs**:
- No git tracking
- No IDE editing (must use CLI/API)
- Not browsable in file explorer

**Example**:
```python
# Session summary (auto-generated)
summary = DocumentReference(
    entity_type=EntityType.SESSION,
    entity_id=42,
    file_path="docs/communication/status_report/session-summary.md",
    content="# Session Summary\n\nCompleted: WI-133...",
    storage_mode="database_only"
)
# Result: Content in DB, no file created
```

### Mode 3: FILE_ONLY (Legacy Compatibility)

**Characteristics**:
- Content only in files
- Database has metadata only (no content column)
- File is authoritative source
- Backward compatible with current system

**Use Cases**:
- Large binary files (diagrams, PDFs >10MB)
- External documents (linked, not managed)
- Gradual migration (existing documents)
- Low-priority content (not searchable yet)

**Benefits**:
- Minimal database impact
- Compatible with legacy workflows
- No content duplication
- Supports large files efficiently

**Tradeoffs**:
- No content queries
- No full-text search
- File I/O required for content access
- Slower retrieval

**Example**:
```python
# Large architecture diagram (binary)
diagram = DocumentReference(
    entity_type=EntityType.PROJECT,
    entity_id=1,
    file_path="docs/architecture/diagrams/system-architecture.pdf",
    content=None,  # Not stored
    storage_mode="file_only"
)
# Result: Metadata in DB, file managed externally
```

### Storage Mode Decision Matrix

| Scenario | Recommended Mode | Rationale |
|----------|------------------|-----------|
| User documentation (guides, tutorials) | HYBRID | Needs git tracking + search + editing |
| Architecture docs (design, ADRs) | HYBRID | Team collaboration + versioning + search |
| Requirements docs | HYBRID | Traceability + editing + linking |
| Session summaries (auto-generated) | DATABASE_ONLY | High frequency, no human editing |
| Test reports (auto-generated) | DATABASE_ONLY | Ephemeral, metrics-focused |
| Status reports (weekly summaries) | HYBRID | Git tracking for history |
| Binary files (PDFs, images >1MB) | FILE_ONLY | Database size constraints |
| External documents (links) | FILE_ONLY | Not managed by AIPM |
| Temporary analysis/research | DATABASE_ONLY | No persistence needed |
| Migration phase (existing docs) | FILE_ONLY → HYBRID | Gradual transition |

### Mode Selection Logic

```python
def recommend_storage_mode(
    document_type: DocumentType,
    content_size: int,
    is_auto_generated: bool,
    needs_git_tracking: bool,
    needs_full_text_search: bool,
    format: DocumentFormat
) -> str:
    """
    Recommend storage mode based on document characteristics.

    Args:
        document_type: Type of document
        content_size: Content size in bytes
        is_auto_generated: True if auto-generated
        needs_git_tracking: True if git history needed
        needs_full_text_search: True if searchable
        format: Document format

    Returns:
        Recommended storage mode
    """
    # Binary files or very large content
    if format != DocumentFormat.MARKDOWN or content_size > 10_000_000:  # 10MB
        return "file_only"

    # Auto-generated, no git tracking needed
    if is_auto_generated and not needs_git_tracking:
        return "database_only"

    # User-facing documentation
    if document_type in [DocumentType.USER_GUIDE, DocumentType.REQUIREMENTS]:
        return "hybrid"

    # Needs full-text search
    if needs_full_text_search:
        return "hybrid"

    # Default: hybrid (safe choice)
    return "hybrid"
```

---

## Database Schema Design

### Schema Changes (Migration 0039)

#### 1. Alter `document_references` Table

Add content storage and sync tracking columns:

```sql
-- Add content storage
ALTER TABLE document_references
ADD COLUMN content TEXT DEFAULT NULL;

-- Add filename for efficient indexing (extracted from file_path)
ALTER TABLE document_references
ADD COLUMN filename TEXT DEFAULT NULL;

-- Add storage mode
ALTER TABLE document_references
ADD COLUMN storage_mode TEXT DEFAULT 'hybrid'
CHECK(storage_mode IN ('hybrid', 'database_only', 'file_only'));

-- Add content timestamp (separate from entity updated_at)
ALTER TABLE document_references
ADD COLUMN content_updated_at TEXT DEFAULT NULL;

-- Add sync tracking
ALTER TABLE document_references
ADD COLUMN last_synced_at TEXT DEFAULT NULL;

ALTER TABLE document_references
ADD COLUMN sync_status TEXT DEFAULT 'synced'
CHECK(sync_status IN ('synced', 'db_newer', 'file_newer', 'conflict', 'missing_file', 'missing_db'));

-- Add content size for monitoring
ALTER TABLE document_references
ADD COLUMN content_size_bytes INTEGER DEFAULT NULL;
```

#### 2. Create Performance Indexes

```sql
-- Hash lookup (find by content hash)
CREATE INDEX IF NOT EXISTS idx_document_content_hash
ON document_references(content_hash);

-- Filename lookup (common queries)
CREATE INDEX IF NOT EXISTS idx_document_filename
ON document_references(filename);

-- Sync status (find out-of-sync documents)
CREATE INDEX IF NOT EXISTS idx_document_sync_status
ON document_references(sync_status)
WHERE sync_status != 'synced';

-- Storage mode (query by mode)
CREATE INDEX IF NOT EXISTS idx_document_storage_mode
ON document_references(storage_mode);

-- Content size (monitor database growth)
CREATE INDEX IF NOT EXISTS idx_document_content_size
ON document_references(content_size_bytes)
WHERE content_size_bytes IS NOT NULL;

-- Composite index for sync operations
CREATE INDEX IF NOT EXISTS idx_document_sync_composite
ON document_references(storage_mode, sync_status, last_synced_at);
```

#### 3. Create Full-Text Search Table (FTS5)

```sql
-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS document_content_fts
USING fts5(
    document_id UNINDEXED,  -- Reference to document_references.id
    filename,                -- Searchable filename
    title,                   -- Searchable title
    content,                 -- Full-text indexed content
    category UNINDEXED,      -- Filterable (not searchable)
    document_type UNINDEXED, -- Filterable (not searchable)
    tokenize='unicode61 remove_diacritics 2'  -- Better search
);

-- Trigger to auto-sync FTS index on insert
CREATE TRIGGER IF NOT EXISTS document_fts_insert
AFTER INSERT ON document_references
WHEN NEW.content IS NOT NULL AND NEW.storage_mode != 'file_only'
BEGIN
    INSERT INTO document_content_fts(
        document_id, filename, title, content, category, document_type
    )
    VALUES (
        NEW.id,
        NEW.filename,
        NEW.title,
        NEW.content,
        NEW.category,
        NEW.document_type
    );
END;

-- Trigger to auto-sync FTS index on update
CREATE TRIGGER IF NOT EXISTS document_fts_update
AFTER UPDATE ON document_references
WHEN NEW.content IS NOT NULL AND NEW.storage_mode != 'file_only'
BEGIN
    UPDATE document_content_fts
    SET
        filename = NEW.filename,
        title = NEW.title,
        content = NEW.content,
        category = NEW.category,
        document_type = NEW.document_type
    WHERE document_id = NEW.id;
END;

-- Trigger to auto-remove from FTS on delete
CREATE TRIGGER IF NOT EXISTS document_fts_delete
AFTER DELETE ON document_references
BEGIN
    DELETE FROM document_content_fts WHERE document_id = OLD.id;
END;
```

#### 4. Auto-Update Triggers

```sql
-- Auto-extract filename from file_path on insert/update
CREATE TRIGGER IF NOT EXISTS document_extract_filename_insert
AFTER INSERT ON document_references
WHEN NEW.filename IS NULL
BEGIN
    UPDATE document_references
    SET filename = substr(
        NEW.file_path,
        instr(NEW.file_path, '/') + 1,  -- Remove leading path
        length(NEW.file_path)
    )
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS document_extract_filename_update
AFTER UPDATE ON document_references
WHEN NEW.filename IS NULL
BEGIN
    UPDATE document_references
    SET filename = substr(
        NEW.file_path,
        instr(NEW.file_path, '/') + 1,
        length(NEW.file_path)
    )
    WHERE id = NEW.id;
END;

-- Auto-calculate content_size_bytes on insert/update
CREATE TRIGGER IF NOT EXISTS document_calc_content_size_insert
AFTER INSERT ON document_references
WHEN NEW.content IS NOT NULL
BEGIN
    UPDATE document_references
    SET content_size_bytes = length(NEW.content)
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS document_calc_content_size_update
AFTER UPDATE OF content ON document_references
WHEN NEW.content IS NOT NULL
BEGIN
    UPDATE document_references
    SET content_size_bytes = length(NEW.content)
    WHERE id = NEW.id;
END;
```

### Schema Summary

**New Columns** (7):
- `content` (TEXT): Full document content
- `filename` (TEXT): Extracted filename for indexing
- `storage_mode` (TEXT): HYBRID | DATABASE_ONLY | FILE_ONLY
- `content_updated_at` (TEXT): Content modification timestamp
- `last_synced_at` (TEXT): Last successful sync timestamp
- `sync_status` (TEXT): Sync state machine
- `content_size_bytes` (INTEGER): Content size monitoring

**New Indexes** (6):
- `idx_document_content_hash`: Hash lookups
- `idx_document_filename`: Filename queries
- `idx_document_sync_status`: Out-of-sync detection
- `idx_document_storage_mode`: Mode filtering
- `idx_document_content_size`: Size monitoring
- `idx_document_sync_composite`: Sync operations

**New Tables** (1):
- `document_content_fts`: FTS5 virtual table

**New Triggers** (7):
- FTS sync triggers (insert, update, delete)
- Filename extraction triggers (insert, update)
- Content size calculation triggers (insert, update)

**Database Size Impact**:
- Current: ~165 docs × ~2.5KB avg = ~425KB content
- Post-migration: ~425KB content + ~100KB indexes + ~200KB FTS = ~725KB
- Growth projection: 1000 docs = ~2.5MB content + ~1MB overhead = ~3.5MB
- Manageable within SQLite limits (140GB max, <100MB target)

---

## Sync Strategy

### Synchronization States

```python
from enum import Enum

class SyncStatus(Enum):
    """Document synchronization states."""
    SYNCED = "synced"              # DB and file content match
    DB_NEWER = "db_newer"          # DB has newer content than file
    FILE_NEWER = "file_newer"      # File has newer content than DB
    CONFLICT = "conflict"          # Both DB and file changed independently
    MISSING_FILE = "missing_file"  # DB has content but file doesn't exist
    MISSING_DB = "missing_db"      # File exists but DB has no content

class SyncStrategy(Enum):
    """Synchronization direction strategies."""
    DB_TO_FILE = "db_to_file"          # One-way: Database → File
    FILE_TO_DB = "file_to_db"          # One-way: File → Database
    BIDIRECTIONAL = "bidirectional"    # Smart sync (timestamp + hash)
```

### Sync Detection Logic

```python
def detect_sync_status(
    doc: DocumentReference,
    file_exists: bool,
    file_content: Optional[str],
    file_mtime: Optional[float]
) -> SyncStatus:
    """
    Detect current synchronization status.

    Args:
        doc: Document reference from database
        file_exists: True if file exists on filesystem
        file_content: File content (if exists)
        file_mtime: File modification time (if exists)

    Returns:
        Current sync status
    """
    # FILE_ONLY mode: always synced (file is source of truth)
    if doc.storage_mode == "file_only":
        return SyncStatus.SYNCED

    # DATABASE_ONLY mode: check if file accidentally created
    if doc.storage_mode == "database_only":
        if file_exists:
            return SyncStatus.CONFLICT  # File shouldn't exist
        return SyncStatus.SYNCED

    # HYBRID mode: bidirectional sync logic
    if not file_exists and doc.content is None:
        return SyncStatus.SYNCED  # Both empty (initial state)

    if not file_exists and doc.content is not None:
        return SyncStatus.MISSING_FILE  # Need to create file

    if file_exists and doc.content is None:
        return SyncStatus.MISSING_DB  # Need to populate DB

    # Both exist: compare hashes
    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
    db_hash = doc.content_hash

    if file_hash == db_hash:
        return SyncStatus.SYNCED

    # Hashes differ: use timestamps to determine newer
    file_time = datetime.fromtimestamp(file_mtime)
    db_time = doc.content_updated_at or doc.updated_at

    if doc.last_synced_at is None:
        # First sync: check which is newer
        if file_time > db_time:
            return SyncStatus.FILE_NEWER
        return SyncStatus.DB_NEWER

    # Both changed since last sync: conflict
    if file_time > doc.last_synced_at and db_time > doc.last_synced_at:
        return SyncStatus.CONFLICT

    # Only one changed since last sync
    if file_time > doc.last_synced_at:
        return SyncStatus.FILE_NEWER
    if db_time > doc.last_synced_at:
        return SyncStatus.DB_NEWER

    # Edge case: timestamps unreliable, use hash mismatch
    return SyncStatus.CONFLICT
```

### Conflict Resolution Strategies

```python
class ConflictResolution(Enum):
    """Strategies for resolving sync conflicts."""
    DB_WINS = "db_wins"              # Database content overwrites file
    FILE_WINS = "file_wins"          # File content overwrites database
    LATEST_WINS = "latest_wins"      # Most recent timestamp wins
    MANUAL = "manual"                # Require human intervention
    MERGE = "merge"                  # Attempt automatic merge (future)

def resolve_conflict(
    doc: DocumentReference,
    file_content: str,
    resolution: ConflictResolution
) -> tuple[str, str]:
    """
    Resolve synchronization conflict.

    Args:
        doc: Document reference from database
        file_content: Content from file
        resolution: Resolution strategy

    Returns:
        Tuple of (winning_content, source)
    """
    if resolution == ConflictResolution.DB_WINS:
        return (doc.content, "database")

    if resolution == ConflictResolution.FILE_WINS:
        return (file_content, "file")

    if resolution == ConflictResolution.LATEST_WINS:
        file_time = os.path.getmtime(doc.file_path)
        db_time = doc.content_updated_at or doc.updated_at

        if file_time > db_time:
            return (file_content, "file")
        return (doc.content, "database")

    if resolution == ConflictResolution.MANUAL:
        raise ConflictRequiresManualResolution(
            f"Document {doc.id} has conflicting changes in DB and file. "
            f"Manual resolution required."
        )

    # Future: MERGE strategy
    raise NotImplementedError("Merge strategy not yet implemented")
```

### Sync Operations

#### On-Demand Sync (CLI Command)

```python
def sync_document(doc_id: int, direction: SyncStrategy) -> SyncResult:
    """
    Synchronize a single document.

    Args:
        doc_id: Document reference ID
        direction: Sync direction strategy

    Returns:
        Sync result with status and actions taken
    """
    doc = db.get_document(doc_id)
    status = detect_sync_status(doc, ...)

    if status == SyncStatus.SYNCED:
        return SyncResult(action="none", message="Already synced")

    if direction == SyncStrategy.DB_TO_FILE:
        # Write DB content to file
        write_file(doc.file_path, doc.content)
        doc.last_synced_at = datetime.now()
        doc.sync_status = SyncStatus.SYNCED
        return SyncResult(action="wrote_file", message="File updated from database")

    if direction == SyncStrategy.FILE_TO_DB:
        # Read file content to DB
        content = read_file(doc.file_path)
        doc.content = content
        doc.content_updated_at = datetime.now()
        doc.last_synced_at = datetime.now()
        doc.sync_status = SyncStatus.SYNCED
        return SyncResult(action="updated_db", message="Database updated from file")

    if direction == SyncStrategy.BIDIRECTIONAL:
        # Smart sync based on status
        if status == SyncStatus.DB_NEWER:
            return sync_document(doc_id, SyncStrategy.DB_TO_FILE)
        elif status == SyncStatus.FILE_NEWER:
            return sync_document(doc_id, SyncStrategy.FILE_TO_DB)
        elif status == SyncStatus.CONFLICT:
            # Use default conflict resolution (latest wins)
            content, source = resolve_conflict(doc, read_file(doc.file_path), ConflictResolution.LATEST_WINS)
            # Apply winning content to both
            doc.content = content
            write_file(doc.file_path, content)
            doc.last_synced_at = datetime.now()
            doc.sync_status = SyncStatus.SYNCED
            return SyncResult(action=f"conflict_resolved_{source}_wins", message=f"Conflict resolved: {source} wins")
```

#### Batch Sync (Migration/Maintenance)

```python
def bulk_sync(
    filter_mode: Optional[str] = None,
    dry_run: bool = False
) -> BulkSyncResult:
    """
    Synchronize all documents matching filter.

    Args:
        filter_mode: Optional storage mode filter
        dry_run: If True, report actions without executing

    Returns:
        Bulk sync results with statistics
    """
    docs = db.query_documents(storage_mode=filter_mode)

    results = {
        "total": len(docs),
        "synced": 0,
        "updated": 0,
        "conflicts": 0,
        "errors": 0,
        "actions": []
    }

    for doc in docs:
        try:
            if doc.storage_mode == "file_only":
                results["synced"] += 1
                continue

            status = detect_sync_status(doc, ...)

            if status == SyncStatus.SYNCED:
                results["synced"] += 1
                continue

            if not dry_run:
                result = sync_document(doc.id, SyncStrategy.BIDIRECTIONAL)
                results["actions"].append({
                    "doc_id": doc.id,
                    "file_path": doc.file_path,
                    "action": result.action
                })

                if "conflict" in result.action:
                    results["conflicts"] += 1
                else:
                    results["updated"] += 1
            else:
                results["actions"].append({
                    "doc_id": doc.id,
                    "file_path": doc.file_path,
                    "would_action": f"sync_{status.value}"
                })

        except Exception as e:
            results["errors"] += 1
            results["actions"].append({
                "doc_id": doc.id,
                "error": str(e)
            })

    return BulkSyncResult(**results)
```

#### File System Watcher (Real-Time Sync)

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocumentFileWatcher(FileSystemEventHandler):
    """Watch filesystem for document changes and sync to database."""

    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.debounce_timers = {}  # Prevent rapid-fire syncs

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory or not event.src_path.startswith("docs/"):
            return

        # Debounce: wait 500ms after last change
        file_path = event.src_path
        if file_path in self.debounce_timers:
            self.debounce_timers[file_path].cancel()

        timer = threading.Timer(0.5, self._sync_file, args=[file_path])
        self.debounce_timers[file_path] = timer
        timer.start()

    def _sync_file(self, file_path: str):
        """Sync file to database after debounce period."""
        try:
            # Find document by file_path
            doc = self.db.query_document_by_path(file_path)
            if not doc:
                # New file: create document reference
                self._create_document_from_file(file_path)
            else:
                # Existing file: sync to database
                if doc.storage_mode in ["hybrid", "file_only"]:
                    sync_document(doc.id, SyncStrategy.FILE_TO_DB)

        except Exception as e:
            logging.error(f"Failed to sync {file_path}: {e}")
        finally:
            # Clean up timer
            self.debounce_timers.pop(file_path, None)
```

### Sync Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Single document sync | <100ms | DB query + file I/O + hash calc |
| Batch sync (165 docs) | <5s | Parallel operations + bulk updates |
| File watch debounce | 500ms | Delay before sync trigger |
| Conflict detection | <50ms | Hash comparison + timestamp check |
| Bulk status check | <1s | Query all sync_status != 'synced' |

---

## Performance Analysis

### Content Retrieval Performance

**Database-First Approach**:
```sql
-- Retrieve document content by ID
SELECT content FROM document_references WHERE id = ?;
-- Expected: <10ms (indexed primary key)

-- Retrieve document content by path
SELECT content FROM document_references WHERE file_path = ?;
-- Expected: <20ms (indexed file_path)
```

**Performance Comparison**:

| Method | Time | Notes |
|--------|------|-------|
| Read from SQLite | <50ms | Single query, no file I/O |
| Read from file | ~100-200ms | File I/O, OS cache dependent |
| Read from file (cold cache) | ~500ms-1s | Disk seek overhead |

**Optimization**: Database content retrieval is 2-10x faster than file I/O.

### Full-Text Search Performance

**FTS5 Query Performance**:
```sql
-- Search across all documents
SELECT
    d.id,
    d.file_path,
    d.title,
    snippet(document_content_fts, 2, '<b>', '</b>', '...', 32) AS snippet,
    rank
FROM document_content_fts AS fts
JOIN document_references AS d ON fts.document_id = d.id
WHERE document_content_fts MATCH ?
ORDER BY rank
LIMIT 20;
-- Expected: <200ms for 1000+ documents
```

**Search Optimization**:
- FTS5 tokenization: `unicode61 remove_diacritics 2`
- Rank-based ordering (BM25 algorithm)
- Snippet generation for context
- Index-only queries (no table joins for counting)

**Performance Targets**:

| Corpus Size | Search Time | Index Size |
|-------------|-------------|------------|
| 165 docs (~425KB) | <50ms | ~100KB |
| 500 docs (~1.25MB) | <100ms | ~300KB |
| 1000 docs (~2.5MB) | <200ms | ~600KB |
| 5000 docs (~12.5MB) | <500ms | ~3MB |

### Database Size Projections

**Current State**:
- 165 documents
- ~2.5KB average document size
- Total content: ~425KB

**Projected Growth**:

| Documents | Content Size | Index Overhead | Total DB Size | SQLite Limit |
|-----------|--------------|----------------|---------------|--------------|
| 165 | 425KB | ~200KB | ~625KB | 0.0004% |
| 500 | 1.25MB | ~500KB | ~1.75MB | 0.001% |
| 1000 | 2.5MB | ~1MB | ~3.5MB | 0.002% |
| 5000 | 12.5MB | ~5MB | ~17.5MB | 0.01% |
| 10,000 | 25MB | ~10MB | ~35MB | 0.025% |

**SQLite Limits**:
- Maximum database size: 140 TB (140,000,000 MB)
- Practical limit for AIPM: <100MB (performance considerations)
- Current usage: ~5MB (tables + indexes)
- Headroom: ~95MB for content

**Conclusion**: Document content storage is negligible compared to SQLite capacity. Even with 10,000 documents, total size <40MB.

### Sync Performance

**Single Document Sync**:
```python
# Sync operation breakdown
Read file content:        10-50ms   (I/O)
Calculate SHA256:         5-10ms    (hashing)
Database UPDATE:          5-10ms    (indexed update)
Write file (if needed):   10-50ms   (I/O)
Total:                    30-120ms  (target: <100ms)
```

**Bulk Sync (165 documents)**:
```python
# Parallel sync with batch updates
Query all documents:      50ms      (SELECT all)
Parallel file reads:      500ms     (I/O, 10 workers)
Hash calculations:        200ms     (parallel)
Batch DB updates:         100ms     (transaction)
Parallel file writes:     500ms     (I/O, 10 workers)
Total:                    ~1.5s     (target: <5s)
```

**Optimization Strategies**:
1. **Parallel I/O**: Use thread pool for file operations
2. **Batch Updates**: Single transaction for multiple docs
3. **Lazy Sync**: Only sync changed documents
4. **Smart Caching**: Cache file hashes to avoid recalculation
5. **Incremental Sync**: Track last_synced_at to skip unchanged docs

---

## Migration Plan

### Three-Phase Migration Strategy

#### Phase 1: Schema Addition (Non-Breaking)

**Objective**: Add new columns and tables without changing existing behavior.

**Duration**: 1 hour (implementation + testing)

**Steps**:
1. Create migration file: `migration_0039_hybrid_document_storage.py`
2. Add columns: `content`, `filename`, `storage_mode`, `content_updated_at`, `last_synced_at`, `sync_status`, `content_size_bytes`
3. Create indexes: 6 new indexes for performance
4. Create FTS table: `document_content_fts` with triggers
5. Set defaults: `storage_mode='file_only'` for existing records (preserve current behavior)
6. Run migration: `apm migrate up`
7. Verify: Check schema changes applied correctly

**Validation**:
```sql
-- Verify columns added
PRAGMA table_info(document_references);

-- Verify indexes created
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references';

-- Verify FTS table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='document_content_fts';

-- Verify existing records have file_only mode
SELECT COUNT(*) FROM document_references WHERE storage_mode = 'file_only';
-- Expected: 165
```

**Risk**: Low (additive changes only)

#### Phase 2: Content Backfill (Data Migration)

**Objective**: Populate `content` column from existing files and switch to HYBRID mode.

**Duration**: 2 hours (implementation + testing)

**Steps**:
1. Create backfill script: `scripts/backfill_document_content.py`
2. Query all documents with `storage_mode='file_only'`
3. For each document:
   - Read file content from `file_path`
   - Calculate SHA256 hash
   - Update database record:
     - `content = file_content`
     - `storage_mode = 'hybrid'`
     - `content_updated_at = file_mtime`
     - `last_synced_at = now()`
     - `sync_status = 'synced'`
     - `content_size_bytes = len(content)`
4. Verify hash matches existing `content_hash`
5. Run backfill: `python scripts/backfill_document_content.py --dry-run` (preview)
6. Run backfill: `python scripts/backfill_document_content.py` (execute)
7. Verify: All documents have content and hybrid mode

**Backfill Script Skeleton**:
```python
def backfill_documents(db: DatabaseService, dry_run: bool = False):
    """Backfill document content from files."""
    docs = db.query_documents(storage_mode="file_only")

    results = {
        "total": len(docs),
        "success": 0,
        "skipped": 0,
        "errors": 0
    }

    for doc in docs:
        try:
            # Read file
            if not os.path.exists(doc.file_path):
                results["skipped"] += 1
                continue

            with open(doc.file_path, 'r') as f:
                content = f.read()

            # Verify hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            if doc.content_hash and content_hash != doc.content_hash:
                logging.warning(f"Hash mismatch for {doc.file_path}")

            # Update database
            if not dry_run:
                db.update_document(doc.id, {
                    "content": content,
                    "storage_mode": "hybrid",
                    "content_updated_at": datetime.fromtimestamp(os.path.getmtime(doc.file_path)),
                    "last_synced_at": datetime.now(),
                    "sync_status": "synced",
                    "content_size_bytes": len(content)
                })

            results["success"] += 1

        except Exception as e:
            logging.error(f"Failed to backfill {doc.file_path}: {e}")
            results["errors"] += 1

    return results
```

**Validation**:
```sql
-- Verify all documents have content
SELECT COUNT(*) FROM document_references WHERE content IS NULL AND storage_mode = 'hybrid';
-- Expected: 0

-- Verify FTS index populated
SELECT COUNT(*) FROM document_content_fts;
-- Expected: 165

-- Check content sizes
SELECT
    COUNT(*) AS count,
    SUM(content_size_bytes) / 1024.0 AS total_kb,
    AVG(content_size_bytes) AS avg_bytes
FROM document_references
WHERE content IS NOT NULL;
```

**Risk**: Medium (data migration, file I/O required)

#### Phase 3: Enable Sync Service (Activation)

**Objective**: Activate bidirectional sync for real-time updates.

**Duration**: 2 hours (implementation + testing)

**Steps**:
1. Implement sync service: `agentpm/services/document_sync.py`
2. Add CLI commands:
   - `apm document sync <id>` (manual sync)
   - `apm document sync --all` (bulk sync)
   - `apm document watch` (start file watcher)
3. Add sync to document CRUD operations:
   - On create: Write file if HYBRID mode
   - On update: Sync file if HYBRID mode
   - On delete: Remove file if HYBRID mode
4. Test sync scenarios:
   - Edit file in IDE → DB updated
   - Update via CLI → File updated
   - Conflict resolution
5. Enable file watcher (optional): Background process
6. Monitor sync performance: Track sync times and errors

**CLI Commands**:
```bash
# Manual sync single document
apm document sync 123

# Bulk sync all documents
apm document sync --all

# Dry run (preview actions)
apm document sync --all --dry-run

# Sync with conflict resolution
apm document sync 123 --conflict-resolution=latest_wins

# Start file watcher (background)
apm document watch --daemon
```

**Validation**:
```bash
# Test file → DB sync
echo "# Test" > docs/test/test-sync.md
apm document add --entity-type=project --entity-id=1 --file-path=docs/test/test-sync.md
# Verify: content in DB matches file

# Test DB → file sync
apm document update 1 --content="# Updated"
# Verify: file matches updated content

# Test conflict detection
# 1. Edit file in IDE
# 2. Update via CLI
# 3. Run sync
apm document sync 1
# Expected: Conflict detected and resolved
```

**Risk**: Medium (real-time sync, potential conflicts)

### Rollback Plan

Each migration phase is reversible:

**Phase 1 Rollback**:
```bash
apm migrate down  # Reverts migration_0039
# Removes columns, indexes, FTS table
# Existing data unaffected
```

**Phase 2 Rollback**:
```sql
-- Revert to file_only mode
UPDATE document_references
SET storage_mode = 'file_only',
    content = NULL,
    last_synced_at = NULL,
    sync_status = 'synced';

-- Clear FTS index
DELETE FROM document_content_fts;
```

**Phase 3 Rollback**:
```bash
# Disable file watcher
pkill -f "apm document watch"

# Remove sync hooks from CLI
# (code revert via git)
```

### Migration Timeline

| Phase | Duration | Dependencies | Risk |
|-------|----------|--------------|------|
| Phase 1: Schema | 1 hour | None | Low |
| Phase 2: Backfill | 2 hours | Phase 1 complete | Medium |
| Phase 3: Sync Service | 2 hours | Phase 2 complete | Medium |
| **Total** | **5 hours** | Sequential execution | **Medium** |

**Recommended Approach**:
- Execute Phase 1 immediately (non-breaking)
- Test Phase 1 thoroughly (1 day)
- Execute Phase 2 with backup (data migration)
- Validate Phase 2 (check all content)
- Execute Phase 3 incrementally (sync on-demand first, watcher later)

---

## Security Considerations

### Content Integrity

**Hash Verification**:
- SHA256 hashing for all content
- Detect tampering or corruption
- Verify sync operations succeeded

```python
def verify_content_integrity(doc: DocumentReference) -> bool:
    """Verify document content matches stored hash."""
    if not doc.content:
        return True  # No content to verify

    calculated_hash = hashlib.sha256(doc.content.encode()).hexdigest()
    return calculated_hash == doc.content_hash
```

**Integrity Checks**:
- Run periodic integrity audits
- Alert on hash mismatches
- Auto-repair from file or DB (configurable)

### Access Control

**Database Security**:
- SQLite file permissions: 0600 (owner read/write only)
- Foreign key constraints: Prevent orphaned documents
- Transaction isolation: ACID guarantees

**File Security**:
- Respect filesystem permissions
- Inherit project directory permissions
- No privilege escalation

### Sensitive Content

**Secrets Detection**:
- Never store secrets in documents
- Integrate with secrets scanning tools
- Warn on suspicious patterns (API keys, tokens)

```python
def check_sensitive_content(content: str) -> list[str]:
    """Check for potentially sensitive content."""
    warnings = []

    patterns = {
        "api_key": r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{20,}",
        "password": r"password\s*[:=]\s*['\"]?[^\s'\"]+",
        "token": r"token\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{20,}",
    }

    for name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            warnings.append(f"Potential {name} detected")

    return warnings
```

### Backup and Recovery

**Database Backups**:
- Regular SQLite backups (daily)
- Point-in-time recovery via WAL mode
- Backup includes content (not just metadata)

**File Backups**:
- Git provides version history
- Filesystem backups (system-level)
- Dual backup strategy (DB + files)

**Recovery Scenarios**:

| Scenario | Recovery Method |
|----------|----------------|
| Database corrupted | Restore from backup, regenerate content from files |
| File deleted | Restore from database (HYBRID mode), or git |
| Both lost | Restore from last backup (DB or git) |
| Content mismatch | Re-sync from authoritative source (DB default) |

---

## Future Enhancements

### Phase 2 Features (Post-Migration)

1. **Content Versioning**
   - Store historical versions in database
   - Enable rollback to previous versions
   - Version diff and comparison

2. **Advanced Search**
   - Faceted search (by category, type, date)
   - Similarity search (find related documents)
   - Search result ranking tuning

3. **Content Analytics**
   - Document statistics (word count, reading time)
   - Usage tracking (most viewed, edited)
   - Dependency graph (document linking)

4. **Collaboration Features**
   - Multi-user editing (optimistic locking)
   - Edit conflict UI (visual diff)
   - Comment threads on documents

5. **Export/Import**
   - Bulk export (ZIP archive)
   - Import from external sources
   - Format conversion (Markdown ↔ HTML ↔ PDF)

### Long-Term Vision

1. **Distributed Sync**
   - Multi-machine synchronization
   - Conflict-free replicated data types (CRDT)
   - Offline-first architecture

2. **AI Integration**
   - Auto-tagging and categorization
   - Content summarization
   - Semantic search (embeddings)

3. **Enterprise Features**
   - Access control lists (ACLs)
   - Audit logging (who, what, when)
   - Compliance reporting (GDPR, SOC 2)

---

## Appendices

### Appendix A: SQL Schema Reference

Complete schema after migration (excerpt):

```sql
-- document_references table (post-migration)
CREATE TABLE document_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    title TEXT,
    content TEXT,                     -- NEW: Full content storage
    filename TEXT,                    -- NEW: Extracted filename
    storage_mode TEXT DEFAULT 'hybrid', -- NEW: Storage strategy
    content_updated_at TEXT,          -- NEW: Content timestamp
    last_synced_at TEXT,              -- NEW: Sync timestamp
    sync_status TEXT DEFAULT 'synced', -- NEW: Sync state
    content_size_bytes INTEGER,       -- NEW: Content size
    content_hash TEXT,
    format TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Additional metadata columns...
    UNIQUE(entity_type, entity_id, file_path)
);

-- document_content_fts table (FTS5)
CREATE VIRTUAL TABLE document_content_fts USING fts5(
    document_id UNINDEXED,
    filename,
    title,
    content,
    category UNINDEXED,
    document_type UNINDEXED,
    tokenize='unicode61 remove_diacritics 2'
);
```

### Appendix B: Performance Benchmarks

Expected performance metrics:

| Operation | Target | Actual (Post-Implementation) |
|-----------|--------|------------------------------|
| Content retrieval (by ID) | <50ms | TBD |
| Content retrieval (by path) | <50ms | TBD |
| Full-text search (165 docs) | <100ms | TBD |
| Single document sync | <100ms | TBD |
| Bulk sync (165 docs) | <5s | TBD |
| Database size (165 docs) | <1MB | TBD |

### Appendix C: Storage Mode Decision Tree

```
Is document auto-generated?
├─ Yes
│  └─ Does it need git tracking?
│     ├─ Yes → HYBRID
│     └─ No → DATABASE_ONLY
└─ No (human-authored)
   └─ Is content size >10MB or binary?
      ├─ Yes → FILE_ONLY
      └─ No
         └─ Does it need search/query?
            ├─ Yes → HYBRID
            └─ No → FILE_ONLY (if prefer files) or HYBRID (if prefer DB)
```

---

## Document Metadata

**Document Type**: Architecture Design
**Audience**: Developers, Architects, Database Administrators
**Maturity**: Draft → Review → Approved (post-implementation)
**Related Documents**:
- `document-system-architecture.md` (existing system)
- `migration_0039_hybrid_document_storage.py` (migration script)
- ADR-0XX: Hybrid Document Storage (architecture decision)
- WI-133: Document System Enhancement (work item)
- Task #710: Design Hybrid Document Storage Architecture

**Last Updated**: 2025-10-21
**Version**: 1.0.0
**Status**: Complete (Design Phase)
