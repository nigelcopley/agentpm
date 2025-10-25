# ADR-001: Hybrid Document Storage with Database-First Architecture

**Status**: Proposed

**Date**: 2025-10-21

**Deciders**: AIPM Architecture Team

**Related**: WI-133, Task #710, migration_0039

---

## Context

APM (Agent Project Manager)'s current document system stores metadata in the SQLite database while keeping document content exclusively in files. This creates several limitations:

1. **Content Not Queryable**: Cannot search or analyze document content without file I/O
2. **No Full-Text Search**: No capability to search across the document corpus
3. **Performance Overhead**: File I/O required for every content access (100-500ms vs <50ms DB query)
4. **Limited Metadata**: Cannot store structured content annotations or versions
5. **Sync Fragility**: Hash mismatches require manual reconciliation
6. **Missing Features**: No foundation for versioning, collaboration, or advanced search

**Current Architecture**:
```
Database: Metadata only (file_path, title, content_hash)
Filesystem: All content (165+ markdown files in docs/)
Source of Truth: Files
```

**Requirements**:
- Maintain git-friendly workflows (developers rely on file diffs)
- Enable full-text search across all documents
- Improve content retrieval performance (<50ms target)
- Support future features (versioning, collaboration, AI integration)
- Preserve backward compatibility during migration
- Follow AIPM database-first architecture principles

---

## Decision

We will implement a **hybrid document storage architecture** where:

1. **Database is Source of Truth**
   - Document content stored in `document_references.content` column (TEXT)
   - Full-text search enabled via SQLite FTS5 virtual table
   - Content hash verification (SHA256) for integrity
   - Structured metadata and annotations

2. **Files are Synchronized Cache**
   - Filesystem copies generated from database
   - Enable git workflow (diffs, version control, branching)
   - Support IDE editing (familiar developer experience)
   - Bidirectional sync with conflict detection

3. **Three Storage Modes**
   - **HYBRID** (default): Content in DB + file sync (recommended)
   - **DATABASE_ONLY**: Content only in DB (auto-generated reports)
   - **FILE_ONLY**: Legacy mode (large binaries, gradual migration)

4. **Bidirectional Synchronization**
   - DB → File: Write files when content changes
   - File → DB: Detect file changes and update database
   - Conflict resolution: Configurable strategies (latest wins, DB wins, manual)
   - Real-time sync: Optional file system watcher

**Architecture**:
```
┌─────────────────────────────────────────┐
│         Database (Source of Truth)      │
│  ┌────────────────────────────────┐    │
│  │ document_references            │    │
│  │ ├─ content (TEXT)              │◄───┼──── Full-text queryable
│  │ ├─ storage_mode                │    │
│  │ ├─ sync_status                 │    │
│  │ └─ content_hash                │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │ document_content_fts (FTS5)    │    │
│  │ └─ Full-text search index      │◄───┼──── Fast search (<200ms)
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
                   ↕ Sync Service (bidirectional)
┌─────────────────────────────────────────┐
│    Filesystem (Synchronized Cache)      │
│  docs/                                   │
│  ├─ architecture/design/ (git-tracked) │
│  ├─ planning/requirements/              │
│  └─ ... (165+ documents)                │
└─────────────────────────────────────────┘
```

---

## Alternatives Considered

### Alternative 1: File-Only (Status Quo)

**Approach**: Keep content exclusively in files, database has metadata only.

**Pros**:
- Simple, no changes needed
- Familiar git workflow
- IDE integration native
- Minimal database size

**Cons**:
- No content queries (must read files)
- No full-text search capability
- Slow content access (file I/O overhead)
- Cannot build advanced features (versioning, collaboration)
- No data integrity guarantees (file corruption)

**Rejected**: Doesn't address core requirements (search, performance, future features).

### Alternative 2: Database-Only

**Approach**: Store all content in database, no files generated.

**Pros**:
- Fastest queries (<50ms)
- Full-text search built-in
- Data integrity guaranteed (ACID)
- Simplest architecture (no sync)
- Smallest disk footprint

**Cons**:
- No git workflow (major disruption)
- No IDE editing (must use CLI/API)
- Not browsable in file explorer
- Team resistance (unfamiliar workflow)
- Cannot leverage git features (branching, PRs, diffs)

**Rejected**: Breaks developer workflows, too disruptive for team.

### Alternative 3: File-First with Database Cache

**Approach**: Files are source of truth, database caches content for search.

**Pros**:
- Preserves file-centric workflow
- Enables search capability
- Minimal disruption
- Git remains primary

**Cons**:
- Files still authoritative (slower queries)
- Cache invalidation complexity
- Doesn't improve content access speed
- Still requires file I/O for writes
- Database becomes stale risk

**Rejected**: Doesn't achieve performance goals, complex cache management.

### Alternative 4: Hybrid with File Priority

**Approach**: Similar to our decision but files win conflicts by default.

**Pros**:
- Developer-friendly (files preferred)
- Git workflow preserved
- Search capability enabled

**Cons**:
- Database not authoritative (inconsistent source of truth)
- Performance benefits reduced (must check files)
- Conflict resolution biased (DB changes lost)
- Doesn't align with AIPM database-first principles

**Rejected**: Violates AIPM architecture principles, unclear authority.

---

## Consequences

### Positive

1. **Performance Improvement**
   - Content retrieval: 100-500ms (file I/O) → <50ms (DB query)
   - Full-text search: Impossible → <200ms (FTS5)
   - Bulk operations: 10x faster (no file I/O)

2. **New Capabilities**
   - Full-text search across all documents
   - Content-based queries (find docs with X)
   - Foundation for versioning (store historical content)
   - Foundation for collaboration (optimistic locking)
   - Foundation for AI features (embeddings, summarization)

3. **Data Integrity**
   - ACID transactions (atomic updates)
   - Foreign key constraints (referential integrity)
   - Content hash verification (detect corruption)
   - Automatic backups (SQLite WAL mode)

4. **Developer Experience**
   - Git workflow preserved (file diffs, branching, PRs)
   - IDE editing unchanged (transparent sync)
   - File explorer browsing maintained
   - Familiar markdown editing

5. **Architecture Alignment**
   - Database-first (aligns with APM (Agent Project Manager) principles)
   - Single source of truth (database)
   - Service-oriented (sync service)
   - Modular (storage modes)

### Negative

1. **Complexity Increase**
   - Bidirectional sync logic required
   - Conflict resolution strategies needed
   - Sync status tracking (state machine)
   - More testing surface area

2. **Disk Usage**
   - Content in both DB and files (~2x storage)
   - Current: ~425KB content → ~850KB total
   - Projected (1000 docs): ~2.5MB content → ~5MB total
   - Still negligible (SQLite supports 140TB, target <100MB)

3. **Migration Effort**
   - 3-phase migration required (schema, backfill, sync)
   - 165+ existing documents to migrate
   - ~5 hours implementation + testing
   - Risk of data loss if not careful (backups critical)

4. **Operational Overhead**
   - Sync service monitoring needed
   - Conflict detection and resolution
   - Periodic integrity checks (hash verification)
   - File watcher process (optional, adds complexity)

5. **Learning Curve**
   - Developers must understand storage modes
   - CLI commands for content management
   - Conflict resolution procedures
   - Sync troubleshooting

### Neutral

1. **Database Size Impact**
   - +~500KB for 165 documents (content + indexes)
   - +~3MB for 1000 documents (projected growth)
   - Acceptable for SQLite (handles up to 140TB)
   - Current DB: ~5MB → Post-migration: ~5.5MB

2. **Backward Compatibility**
   - FILE_ONLY mode preserves legacy behavior
   - Gradual migration possible
   - Existing workflows unchanged during Phase 1
   - Breaking changes only if forced to HYBRID mode

3. **Future Flexibility**
   - Foundation for versioning (store version history)
   - Foundation for CRDT (distributed sync)
   - Foundation for AI (embeddings, semantic search)
   - May require additional schema changes

---

## Implementation Plan

### Phase 1: Schema Addition (1 hour)

**Deliverable**: Migration 0039 applied, schema ready

- Add columns: `content`, `filename`, `storage_mode`, `content_updated_at`, `last_synced_at`, `sync_status`, `content_size_bytes`
- Create indexes: 6 performance indexes
- Create FTS table: `document_content_fts`
- Create triggers: Auto-extract filename, auto-calc size, FTS sync
- Default mode: `file_only` (preserve current behavior)

**Risk**: Low (additive changes only)

### Phase 2: Content Backfill (2 hours)

**Deliverable**: All documents have content in database

- Read all 165+ files
- Populate `content` column
- Switch to `storage_mode='hybrid'`
- Verify hash matches
- Populate FTS index

**Risk**: Medium (data migration, requires backups)

### Phase 3: Sync Service (2 hours)

**Deliverable**: Bidirectional sync operational

- Implement sync service
- Add CLI commands (`apm document sync`)
- Optional: File watcher for real-time sync
- Conflict resolution strategies
- Monitoring and logging

**Risk**: Medium (real-time sync, conflict handling)

**Total Timeline**: 5 hours (sequential execution)

---

## Validation Criteria

### Success Metrics

1. **Performance**
   - Content retrieval: <50ms (90th percentile)
   - Full-text search: <200ms for 1000+ documents
   - Sync operation: <100ms per document

2. **Reliability**
   - Zero data loss during migration
   - 100% hash match after backfill
   - <1% conflict rate in normal operations

3. **Usability**
   - Git workflow unchanged
   - IDE editing transparent
   - Sync conflicts <5% of operations

4. **Scalability**
   - Database size <100MB for 10,000 documents
   - Search performance linear (O(log n))
   - Sync time <5s for bulk operations

### Acceptance Criteria

- [ ] Migration 0039 applied successfully
- [ ] All 165+ documents have content in database
- [ ] FTS search returns results <200ms
- [ ] Content retrieval <50ms
- [ ] Git diff shows meaningful changes
- [ ] IDE editing updates database
- [ ] Conflict resolution works for all strategies
- [ ] Rollback tested and verified
- [ ] Documentation complete (architecture, user guide, developer guide)

---

## References

- **Design Document**: `docs/architecture/design/hybrid-document-storage-architecture.md`
- **Migration**: `agentpm/core/database/migrations/files/migration_0039_hybrid_document_storage.py`
- **Work Item**: WI-133 "Document System Enhancement - Database Content Storage with File Sync"
- **Task**: #710 "Design Hybrid Document Storage Architecture"
- **Current System**: `docs/architecture/design/document-system-architecture.md`

---

## Notes

**Database-First Philosophy**:
This decision aligns with APM (Agent Project Manager)'s database-first architecture where the database is the single source of truth and files are generated artifacts. This pattern is consistent with:
- Work items (database → git issues)
- Tasks (database → project files)
- Contexts (database → assembled views)
- Sessions (database → checkpoints)

**Git Compatibility**:
While database-first, we preserve git workflows by maintaining synchronized filesystem copies. This is a pragmatic compromise that enables:
- Meaningful diffs (see content changes)
- Branch workflows (test changes in branches)
- PR reviews (review content changes)
- IDE integration (familiar editing)

**Future Evolution**:
This architecture enables future enhancements:
- Content versioning (store historical snapshots)
- Collaborative editing (optimistic locking, CRDTs)
- AI integration (embeddings, semantic search, summarization)
- Advanced search (faceted search, filters, ranking)
- Offline sync (replicate to local DB, sync when online)

**Risks Mitigated**:
- Data loss: Dual storage (DB + files), regular backups
- Performance degradation: Database queries faster than file I/O
- Developer disruption: Transparent sync, familiar workflows
- Migration complexity: 3-phase approach, extensive testing
- Conflict chaos: Clear resolution strategies, logging

---

**Last Updated**: 2025-10-21
**Status**: Proposed (awaiting implementation)
**Next Steps**: Implement migration_0039, backfill content, activate sync service
