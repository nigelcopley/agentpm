# Migration 0031: Universal Documentation System

**Status**: ✅ Applied
**Applied At**: 2025-10-18 15:51:21
**Migration File**: `agentpm/core/database/migrations/files/migration_0031_documentation_system.py`

## Overview

This migration enhances the `document_references` table with comprehensive metadata to support the Universal Documentation System with hierarchical path structure.

## Path Structure

```
docs/{category}/{document_type}/{filename}
```

### Examples
- `docs/planning/requirements/auth-functional.md`
- `docs/architecture/design/database-schema.md`
- `docs/guides/user_guide/getting-started.md`
- `docs/reference/api/endpoints.md`

## Schema Changes

### New Columns (11 total)

| Column | Type | Description | Purpose |
|--------|------|-------------|---------|
| `category` | TEXT | Top-level category | One of 8 categories for organization |
| `document_type_dir` | TEXT | Physical subdirectory | Subdirectory under category |
| `segment_type` | TEXT | Content classification | narrative, reference, procedural, analytical |
| `component` | TEXT | Technical component | Related system component |
| `domain` | TEXT | Business/technical domain | Domain classification |
| `audience` | TEXT | Target audience | developer, user, admin, stakeholder |
| `maturity` | TEXT | Document lifecycle state | draft, review, approved, deprecated |
| `priority` | TEXT | Importance level | critical, high, medium, low |
| `tags` | TEXT | JSON array | Searchable tags |
| `phase` | TEXT | SDLC phase | discovery, planning, implementation, review, ops, evolution |
| `work_item_id` | INTEGER | Related work item | Foreign key to work_items table |

### New Indexes (8 total)

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_doc_category` | category | Fast category lookup |
| `idx_doc_type_dir` | document_type_dir | Fast document type lookup |
| `idx_doc_cat_type` | category, document_type_dir | Composite lookup |
| `idx_doc_component` | component | Component filtering |
| `idx_doc_domain` | domain | Domain filtering |
| `idx_doc_work_item` | work_item_id | Work item association |
| `idx_doc_audience` | audience | Audience filtering |
| `idx_doc_maturity` | maturity | Maturity filtering |

## 8 Categories

### 1. **planning**
Requirements, analysis, research, roadmaps

**Document Types**:
- requirements
- analysis
- research
- roadmaps

### 2. **architecture**
Design, ADRs, patterns, integration

**Document Types**:
- design
- adrs
- patterns
- integration

### 3. **guides**
User guides, developer guides, admin guides, troubleshooting

**Document Types**:
- user_guide
- developer_guide
- admin_guide
- troubleshooting

### 4. **reference**
API docs, CLI reference, schema, configuration

**Document Types**:
- api
- cli
- schema
- config

### 5. **processes**
Workflows, procedures, templates

**Document Types**:
- workflows
- procedures
- templates

### 6. **governance**
Policies, standards, compliance

**Document Types**:
- policies
- standards
- compliance

### 7. **operations**
Runbooks, deployment guides, monitoring

**Document Types**:
- runbooks
- deployment
- monitoring

### 8. **communication**
Announcements, reports, presentations

**Document Types**:
- announcements
- reports
- presentations

## Backward Compatibility

- All new columns are **nullable** (no NOT NULL constraints)
- Existing records are **preserved** without modification
- No data migration required
- Existing queries continue to work unchanged

## Upgrade Path

```python
# Migration adds 11 columns
ALTER TABLE document_references ADD COLUMN category TEXT
ALTER TABLE document_references ADD COLUMN document_type_dir TEXT
# ... (9 more columns)

# Creates 8 indexes
CREATE INDEX idx_doc_category ON document_references(category)
CREATE INDEX idx_doc_type_dir ON document_references(document_type_dir)
# ... (6 more indexes)
```

## Downgrade Path

The downgrade recreates the table without the new columns:

1. Create backup table with original schema
2. Copy data (original columns only)
3. Drop original table
4. Rename backup to original name

This preserves data while removing the new columns.

## Usage Examples

### Query by Category
```sql
SELECT * FROM document_references
WHERE category = 'planning'
  AND document_type_dir = 'requirements';
```

### Query by Component
```sql
SELECT * FROM document_references
WHERE component = 'database'
  AND maturity = 'approved';
```

### Query by Audience
```sql
SELECT * FROM document_references
WHERE audience = 'developer'
  AND category = 'guides';
```

### Query by Work Item
```sql
SELECT * FROM document_references
WHERE work_item_id = 42;
```

## Performance

- **Indexes**: 8 indexes for efficient querying
- **Composite Index**: `idx_doc_cat_type` for category + document_type queries
- **Foreign Key Index**: `idx_doc_work_item` for work item associations

## Validation

### Schema Validation
```bash
sqlite3 agentpm.db "PRAGMA table_info(document_references);"
# Should show 24 columns (13 original + 11 new)
```

### Index Validation
```bash
sqlite3 agentpm.db "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references';"
# Should show 8 new indexes starting with idx_doc_*
```

### Migration History
```bash
sqlite3 agentpm.db "SELECT version, description, applied_at FROM schema_migrations WHERE version='0031';"
# Should show migration 0031 with timestamp
```

## Testing

### Manual Testing
```bash
# Apply migration
python3 -c "
from agentpm.core.database.migrations.files.migration_0031_documentation_system import upgrade
import sqlite3
conn = sqlite3.connect('agentpm.db')
upgrade(conn)
conn.commit()
conn.close()
"

# Verify schema
sqlite3 agentpm.db "PRAGMA table_info(document_references);"

# Verify indexes
sqlite3 agentpm.db "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references';"
```

### Test Downgrade
```bash
# Apply downgrade
python3 -c "
from agentpm.core.database.migrations.files.migration_0031_documentation_system import downgrade
import sqlite3
conn = sqlite3.connect('agentpm.db')
downgrade(conn)
conn.commit()
conn.close()
"

# Verify original schema restored
sqlite3 agentpm.db "PRAGMA table_info(document_references);"
# Should show 13 original columns only
```

## Next Steps

1. **Update Pydantic Models**: Create `DocumentReference` model with new fields
2. **Update Adapters**: Create adapter methods for new columns
3. **Update Methods**: Create business logic for document management
4. **Create CLI Commands**: Add `apm document` commands for CRUD operations
5. **Update Documentation**: Add user guide for Universal Documentation System

## Related Files

- Migration: `agentpm/core/database/migrations/files/migration_0031_documentation_system.py`
- Models: `agentpm/core/models/document_reference.py` (to be created)
- Adapters: `agentpm/core/database/adapters/document_adapter.py` (to be updated)
- Methods: `agentpm/core/methods/document_methods.py` (to be created)
- CLI: `agentpm/cli/commands/document.py` (to be created)

## Compliance

- ✅ **DP-001**: Effort ≤4 hours
- ✅ **DP-004**: Database-first principles followed
- ✅ **TES-001**: Project-relative paths used
- ✅ **SEC-001**: No user input, no validation needed
- ✅ **WF-001**: Migration versioned and tracked
- ✅ **Backward Compatibility**: All columns nullable
- ✅ **Reversibility**: Downgrade path implemented
- ✅ **Data Preservation**: Existing records unaffected

## Summary

Migration 0031 successfully adds comprehensive metadata to the `document_references` table, enabling the Universal Documentation System with hierarchical path structure. All changes are backward compatible and reversible.

**Key Achievements**:
- ✅ 11 new columns added (all nullable)
- ✅ 8 indexes created for efficient querying
- ✅ Zero data loss or corruption
- ✅ Upgrade and downgrade paths tested
- ✅ Schema validation passed
- ✅ Migration recorded in schema_migrations table
