# Phase 1 Critical Blocker Analysis

## Problem Identified

The adapter and methods files exist BUT are INCOMPLETE. They only handle the original fields, not the new metadata fields from Migration 0031.

### Missing Fields in Adapter/Methods

**Existing fields (working)**:
- entity_type, entity_id
- file_path, title, description
- document_type, format
- file_size_bytes, content_hash
- created_by, created_at, updated_at

**Missing fields (from Migration 0031)**:
- category (top-level category)
- document_type_dir (physical subdirectory) 
- segment_type (content classification)
- component (technical component)
- domain (business/technical domain)
- audience (target readers)
- maturity (lifecycle state)
- priority (importance level)
- tags (JSON array for search)
- phase (SDLC phase)
- work_item_id (link to work item)

## Impact

**HIGH SEVERITY**: Cannot use any of the Universal Documentation System features:
- Cannot set category when adding documents
- Cannot filter by metadata in searches
- Cannot use tags for organization
- Cannot track document maturity/lifecycle
- Quality gates will fail (no metadata to validate)

## Tasks Affected

- Task 563: Update DocumentReference adapter ← **MUST DO FIRST**
- Task 564: Implement document service methods ← **MUST DO FIRST**
- All other tasks blocked until these complete

## Required Actions

### 1. Update document_reference_adapter.py

**File**: `agentpm/core/database/adapters/document_reference_adapter.py`

**Changes needed in `to_db()` method**:
```python
def to_db(doc: DocumentReference) -> Dict[str, Any]:
    return {
        # Existing fields...
        'entity_type': doc.entity_type.value,
        'entity_id': doc.entity_id,
        'file_path': doc.file_path,
        'document_type': doc.document_type.value if doc.document_type else None,
        'title': doc.title,
        'description': doc.description,
        'file_size_bytes': doc.file_size_bytes,
        'content_hash': doc.content_hash,
        'format': doc.format.value if doc.format else None,
        'created_by': doc.created_by,
        'created_at': doc.created_at.isoformat() if doc.created_at else None,
        'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
        
        # NEW: Universal Documentation System metadata
        'category': doc.category,
        'document_type_dir': doc.document_type_dir,  # NEW field name from migration
        'segment_type': doc.segment_type,
        'component': doc.component,
        'domain': doc.domain,
        'audience': doc.audience,
        'maturity': doc.maturity,
        'priority': doc.priority,
        'tags': json.dumps(doc.tags) if doc.tags else None,  # List to JSON
        'phase': doc.phase,
        'work_item_id': doc.work_item_id,
    }
```

**Changes needed in `from_db()` method**:
```python
def from_db(row: Dict[str, Any]) -> DocumentReference:
    return DocumentReference(
        # Existing fields...
        id=row.get('id'),
        entity_type=EntityType(row['entity_type']),
        entity_id=row['entity_id'],
        file_path=row['file_path'],
        document_type=DocumentType(row['document_type']) if row.get('document_type') else None,
        title=row.get('title'),
        description=row.get('description'),
        file_size_bytes=row.get('file_size_bytes'),
        content_hash=row.get('content_hash'),
        format=DocumentFormat(row['format']) if row.get('format') else None,
        created_by=row.get('created_by'),
        created_at=_parse_datetime(row.get('created_at')),
        updated_at=_parse_datetime(row.get('updated_at')),
        
        # NEW: Universal Documentation System metadata
        category=row.get('category'),
        document_type_dir=row.get('document_type_dir'),  # NEW field name
        segment_type=row.get('segment_type'),
        component=row.get('component'),
        domain=row.get('domain'),
        audience=row.get('audience'),
        maturity=row.get('maturity'),
        priority=row.get('priority'),
        tags=json.loads(row['tags']) if row.get('tags') else [],  # JSON to List
        phase=row.get('phase'),
        work_item_id=row.get('work_item_id'),
    )
```

**New import needed**:
```python
import json  # For tags serialization
```

### 2. Update document_references.py (methods)

**File**: `agentpm/core/database/methods/document_references.py`

**Update `create_document_reference()` INSERT query**:
```python
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
    # NEW fields
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
)
```

**Add new filter methods**:
```python
def search_documents(
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
    """Search documents by Universal Documentation System metadata"""
    # Implementation with WHERE clauses for new fields
    # Tags search needs JSON querying
```

### 3. Verify DocumentReference Model

**File**: `agentpm/core/database/models/document_reference.py`

Check that model has field called `document_type_dir` (Migration 0031 uses this name).

**CRITICAL**: Migration 0031 uses `document_type_dir` but DocumentReference model might use different field name!

Need to verify field name consistency between:
- Migration schema: `document_type_dir`
- Pydantic model: Check actual field name
- Adapter: Must match both

## Timeline Impact

**Original Phase 1 estimate**: 6 hours (Tasks 563 + 564)

**Revised estimate**: 
- Task 563 (Adapter update): 3 hours (was 3 hours) ✅ Same
- Task 564 (Methods update): 5 hours (was 4 hours) ⚠️ +1 hour (need search methods)

**Total Phase 1**: 8 hours (was 6 hours)

**Critical Path Delay**: +2 hours
**Downstream Impact**: All other phases delayed by 2 hours

## Delegation Instructions

**Agent**: aipm-database-developer

**Tasks**: 563, 564 (sequential - adapter first, then methods)

**Prompt**:
```
Update document adapter and methods to support Universal Documentation System metadata.

CRITICAL: Migration 0031 added 11 new metadata fields to document_references table. 
The adapter and methods files exist but only handle original fields.

Task 563: Update document_reference_adapter.py
- Add 11 new metadata fields to to_db() method
- Add 11 new metadata fields to from_db() method  
- Handle tags JSON serialization (List ↔ JSON string)
- Import json module
- Verify field name: model uses 'document_type_dir' or different name?

Task 564: Update document_references.py
- Update create_document_reference() INSERT to include 11 new fields
- Update list_document_references() to support new filters
- Add search_documents() method for metadata search
- Add count_by_category() method
- Add count_by_maturity() method
- Handle tags JSON querying in WHERE clauses

New fields from Migration 0031:
1. category (TEXT)
2. document_type_dir (TEXT) ← Verify this field name in model!
3. segment_type (TEXT)
4. component (TEXT)
5. domain (TEXT)
6. audience (TEXT)
7. maturity (TEXT)
8. priority (TEXT)
9. tags (TEXT - JSON array)
10. phase (TEXT)
11. work_item_id (INTEGER)

Follow AIPM three-layer pattern:
- Models: Pydantic DocumentReference (already has fields)
- Adapters: Convert model ↔ database
- Methods: CRUD with metadata support

Test with:
- Create document with all metadata fields
- Query by category, tags, component, etc.
- Verify tags JSON serialization works
- Check all filters work correctly

References:
- Migration: agentpm/core/database/migrations/files/migration_0031_documentation_system.py
- Model: agentpm/core/database/models/document_reference.py
- Adapter: agentpm/core/database/adapters/document_reference_adapter.py
- Methods: agentpm/core/database/methods/document_references.py
```

## Success Criteria

1. ✅ Adapter handles all 11 new metadata fields
2. ✅ Methods INSERT includes all new fields
3. ✅ Tags JSON serialization works (List ↔ JSON)
4. ✅ Search methods support metadata filters
5. ✅ All existing CLI commands still work
6. ✅ Can add document with category, tags, component, etc.
7. ✅ Can filter documents by metadata
8. ✅ No schema mismatch errors

## Risks

**Risk**: Field name mismatch between migration and model
- Migration uses: `document_type_dir`
- Model might use: Different name?
- **Mitigation**: Verify model field names first, align adapter

**Risk**: Tags JSON querying complexity in SQLite
- JSON queries in WHERE clauses can be tricky
- **Mitigation**: Use simple LIKE '%tag%' initially, optimize later

**Risk**: Breaking existing CLI commands
- Adding fields could break existing add/list/show commands
- **Mitigation**: Use .get() for optional fields, maintain backward compatibility
