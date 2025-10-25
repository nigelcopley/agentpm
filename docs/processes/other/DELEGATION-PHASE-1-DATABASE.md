# Phase 1 Delegation: Database Foundation for Universal Documentation System

## Delegation To
**Agent**: aipm-database-developer
**Priority**: CRITICAL (blocks all other phases)
**Tasks**: 558, 561, 562, 563, 564
**Estimated Effort**: 8 hours

---

## Context

Work Item #112 implements Universal Documentation System with 8 categories and rich metadata. 

**Current State**:
- Migration 0031 file exists but NOT applied (database at migration 0029)
- DocumentReference model INCOMPLETE (missing document_type_dir field)
- Adapter INCOMPLETE (missing 11 new metadata fields)
- Methods INCOMPLETE (missing metadata CRUD operations)

**Critical Path**: All CLI, hooks, gates, and testing depend on functional database layer.

---

## Tasks Overview

### Task 558: Analyze database schema requirements (DONE)
**Status**: Analysis complete
**Findings**:
- Migration 0031 exists with 11 new metadata fields
- Database NOT migrated yet (still at 0029)
- Model missing 1 field (document_type_dir)
- Adapter/methods need updates for 11 fields

### Task 561: Create database migration (DONE)
**Status**: Migration file exists
**Location**: `agentpm/core/database/migrations/files/migration_0031_documentation_system.py`
**Action Required**: Run migration on database

### Task 562: Update DocumentReference Pydantic model (CRITICAL)
**Status**: INCOMPLETE - Missing document_type_dir field
**Action Required**: Add missing field to model

### Task 563: Create document adapter (CRITICAL)
**Status**: EXISTS but INCOMPLETE
**Action Required**: Add 11 new metadata fields to adapter

### Task 564: Implement document service methods (CRITICAL)
**Status**: EXISTS but INCOMPLETE
**Action Required**: Update INSERT, add metadata CRUD methods

---

## Detailed Implementation Tasks

### STEP 1: Fix DocumentReference Model (Task 562)

**File**: `agentpm/core/database/models/document_reference.py`

**Problem**: Model missing `document_type_dir` field that migration 0031 adds to database.

**Solution**: Add field after line 47 (after `document_type` field):

```python
# Hierarchical categorization (NEW - Universal Documentation System)
category: Optional[str] = Field(None, description="Top-level category (planning, architecture, guides, etc.)")
document_type: Optional[DocumentType] = Field(None, description="Document classification")
document_type_dir: Optional[str] = Field(None, description="Physical subdirectory under category")  # ADD THIS LINE
```

**Why**: Migration 0031 creates `document_type_dir` column in database. Without this field in model:
- Pydantic will reject database rows with extra field
- Cannot set this value when creating documents
- Adapter conversion will fail

**Testing**: After change, verify model accepts document_type_dir parameter.

---

### STEP 2: Run Migration 0031 (Task 561)

**Command**:
```bash
cd /Users/nigelcopley/.project_manager/aipm-v2
python -m agentpm.core.database.migrations.runner
```

**Expected Output**:
```
🔧 Migration 0031: Add Universal Documentation System columns
  📋 Adding 11 new columns...
  ✅ Added column: category
  ✅ Added column: document_type_dir
  ... (9 more columns)
  📋 Creating indexes...
  ✅ Created index: idx_doc_category
  ... (7 more indexes)
  ✅ Migration 0031 completed successfully
```

**Verification**:
```bash
sqlite3 .aipm/aipm.db "PRAGMA table_info(document_references);" | grep category
# Should show: category|TEXT|0||0
```

**Why**: Database must have new columns before adapter/methods can use them.

---

### STEP 3: Update Document Adapter (Task 563)

**File**: `agentpm/core/database/adapters/document_reference_adapter.py`

**Required Changes**:

1. **Add import**:
```python
import json  # Add after existing imports
```

2. **Update `to_db()` method** - Add after line 42:
```python
def to_db(doc: DocumentReference) -> Dict[str, Any]:
    return {
        # ... existing fields ...
        'created_at': doc.created_at.isoformat() if doc.created_at else None,
        'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
        
        # NEW: Universal Documentation System metadata
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
    }
```

3. **Update `from_db()` method** - Add after line 69:
```python
def from_db(row: Dict[str, Any]) -> DocumentReference:
    return DocumentReference(
        # ... existing fields ...
        created_at=_parse_datetime(row.get('created_at')),
        updated_at=_parse_datetime(row.get('updated_at')),
        
        # NEW: Universal Documentation System metadata
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
    )
```

**Testing**:
- Create DocumentReference with all metadata fields
- Call to_db() - verify JSON dict has all 11 new fields
- Call from_db() with database row - verify model populated correctly
- Verify tags serialization: ['tag1', 'tag2'] ↔ '["tag1", "tag2"]'

---

### STEP 4: Update Document Methods (Task 564)

**File**: `agentpm/core/database/methods/document_references.py`

**Required Changes**:

1. **Update `create_document_reference()`** - Replace lines 46-66:
```python
def create_document_reference(service, document: DocumentReference) -> DocumentReference:
    """Create a new document reference with Universal Documentation System metadata"""
    db_data = DocumentReferenceAdapter.to_db(document)

    query = """
        INSERT INTO document_references (
            entity_type, entity_id, file_path, document_type, title, description,
            file_size_bytes, content_hash, format, created_by, created_at, updated_at,
            category, document_type_dir, segment_type, component, domain,
            audience, maturity, priority, tags, phase, work_item_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['entity_type'], db_data['entity_id'], db_data['file_path'],
        db_data['document_type'], db_data['title'], db_data['description'],
        db_data['file_size_bytes'], db_data['content_hash'], db_data['format'],
        db_data['created_by'], db_data['created_at'], db_data['updated_at'],
        db_data.get('category'), db_data.get('document_type_dir'),
        db_data.get('segment_type'), db_data.get('component'), db_data.get('domain'),
        db_data.get('audience'), db_data.get('maturity'), db_data.get('priority'),
        db_data.get('tags'), db_data.get('phase'), db_data.get('work_item_id'),
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        doc_id = cursor.lastrowid

    return get_document_reference(service, doc_id)
```

2. **Add metadata search method** - Add after line 421:
```python
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
```

3. **Add category count method** - Add after search method:
```python
def count_documents_by_category(service) -> dict:
    """
    Count documents by category.
    
    Returns:
        Dict mapping category names to document counts
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
```

4. **Add maturity count method**:
```python
def count_documents_by_maturity(service) -> dict:
    """
    Count documents by maturity level.
    
    Returns:
        Dict mapping maturity levels to document counts
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
```

**Testing**:
- Create document with metadata fields
- Verify all fields saved to database
- Search by category - verify filtering works
- Search by tags - verify JSON LIKE query works
- Count by category/maturity - verify aggregation works

---

## Success Criteria

After completing all tasks, verify:

1. ✅ DocumentReference model has `document_type_dir` field
2. ✅ Migration 0031 applied successfully to database
3. ✅ Database has 23 columns (12 original + 11 new)
4. ✅ Adapter converts all 23 fields correctly
5. ✅ Tags serialize/deserialize: List ↔ JSON
6. ✅ create_document_reference() saves all metadata
7. ✅ search_documents_by_metadata() filters correctly
8. ✅ Existing CLI commands still work (backward compatible)
9. ✅ Can create document with metadata: category, tags, component, etc.
10. ✅ Can query documents by metadata filters

---

## Testing Commands

```bash
# 1. Verify migration applied
sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM pragma_table_info('document_references');"
# Expected: 23 (12 original + 11 new)

# 2. Test document creation with metadata
apm document add --entity-type work-item --entity-id 112 \
  --file-path "docs/test-doc.md" \
  --category "architecture" \
  --title "Test Document"
# Expected: Document created with category field

# 3. Verify tags JSON
sqlite3 .aipm/aipm.db "SELECT tags FROM document_references WHERE id=1;"
# Expected: ["tag1", "tag2"] or null

# 4. Test existing commands still work
apm document list --entity-type work-item --entity-id 112
# Expected: Lists documents without errors
```

---

## Files to Modify

1. `agentpm/core/database/models/document_reference.py` - Add document_type_dir field
2. `agentpm/core/database/adapters/document_reference_adapter.py` - Add 11 metadata fields
3. `agentpm/core/database/methods/document_references.py` - Update INSERT, add search methods

**Do NOT modify**:
- Migration file (already correct)
- CLI commands (will work once adapter/methods fixed)
- Enums (already correct)

---

## Dependencies

**Must complete in order**:
1. Task 562 (Fix model) - FIRST
2. Task 561 (Run migration) - SECOND
3. Task 563 (Update adapter) - THIRD
4. Task 564 (Update methods) - FOURTH

**Why sequential**:
- Model must match migration schema
- Migration must run before testing adapter
- Adapter must work before methods can use it
- Methods build on adapter

---

## Deliverables

1. Updated DocumentReference model with document_type_dir field
2. Migration 0031 applied to database (verified with PRAGMA)
3. Updated adapter with all 11 metadata fields + tags JSON handling
4. Updated methods with metadata INSERT and search functions
5. Test results showing all success criteria met
6. No regressions in existing CLI commands

---

## Next Phase

Once Phase 1 complete, can proceed to:
- Phase 2: Directory structure + migration (needs document_methods working)
- Phase 3: Advanced CLI commands (needs service layer)
- Phase 4: Quality gates + hooks
- Phase 5: Testing
- Phase 6: Documentation

---

**Estimated Completion**: 8 hours
**Blocker Status**: CRITICAL - Nothing else can proceed
**Agent**: aipm-database-developer
**Verification**: Will verify all success criteria before marking I1 gate complete
