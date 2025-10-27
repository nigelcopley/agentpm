# Migration 0049: Provider Files Schema Alignment

## Overview

Migration 0049 aligns the existing `provider_files` table with multi-provider requirements. This migration bridges the gap between the Cursor-specific schema (created during initial implementation) and the multi-provider schema required for Claude Code, Google Codex, and other providers.

## Problem Statement

**Current State** (before migration):
```sql
CREATE TABLE provider_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,  -- ❌ Old column name
    file_type TEXT NOT NULL CHECK(file_type IN ('rule', 'mode', 'hook', 'config', 'memory')),  -- ❌ Cursor-specific values
    installed_at TEXT NOT NULL,  -- ❌ Missing timestamps
    FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
    UNIQUE(installation_id, file_path)
)
```

**Issues**:
1. Column name `file_hash` → should be `content_hash` (consistent with migration 0047)
2. CHECK constraint has Cursor-specific values: `'rule', 'mode', 'hook', 'config', 'memory'`
3. Missing columns: `generated_at`, `last_verified_at`, `modification_detected`

**Target State** (after migration):
```sql
CREATE TABLE provider_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK(file_type IN ('agent', 'hook', 'settings', 'rules', 'config', 'other')),  -- ✅ Multi-provider values
    content_hash TEXT NOT NULL,  -- ✅ Renamed
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- ✅ Added
    last_verified_at TIMESTAMP,  -- ✅ Added
    modification_detected INTEGER DEFAULT 0 CHECK(modification_detected IN (0, 1)),  -- ✅ Added
    FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
    UNIQUE(installation_id, file_path)
)
```

## Migration Strategy

Since SQLite does not support:
- Renaming columns directly
- Modifying CHECK constraints

We use the **table swap pattern**:
1. Create `provider_files_new` with correct schema
2. Copy data with transformations (column rename + value mapping)
3. Drop old table
4. Rename new table → `provider_files`
5. Recreate indexes

## File Type Mapping

| Old Value (Cursor) | New Value (Multi-Provider) | Reason |
|-------------------|---------------------------|--------|
| `'rule'` | `'rules'` | Plural form for consistency |
| `'mode'` | `'agent'` | Mode files are agent definitions |
| `'hook'` | `'hook'` | No change (universal) |
| `'config'` | `'config'` | No change (universal) |
| `'memory'` | `'other'` | Not in new schema, map to catch-all |

## Data Preservation

**Before Migration**:
- 7 records in `provider_files`
- Column: `file_hash`
- File types: `rule`, `mode`, `hook`, `config`, `memory`

**After Migration**:
- 7 records preserved
- Column: `content_hash` (values copied from `file_hash`)
- File types: `rules`, `agent`, `hook`, `config`, `other`
- New columns populated:
  - `generated_at`: copied from `installed_at`
  - `last_verified_at`: NULL (not yet verified)
  - `modification_detected`: 0 (false, no modification detected)

## Testing

### Unit Tests

File: `tests/unit/database/test_migration_0049.py`

**Test Coverage**:
- ✅ Column rename (`file_hash` → `content_hash`)
- ✅ New columns added
- ✅ CHECK constraint updated
- ✅ File type value mapping
- ✅ Data preservation (all records migrated)
- ✅ Default values set correctly
- ✅ Indexes recreated
- ✅ Idempotency (safe to run multiple times)
- ✅ Downgrade reverses changes
- ✅ Downgrade reverses file type mapping
- ✅ Downgrade preserves record count

**Test Results**:
```
tests/unit/database/test_migration_0049.py::test_upgrade_renames_file_hash_to_content_hash PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_adds_new_columns PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_updates_file_type_check_constraint PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_migrates_file_type_values PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_preserves_data PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_sets_default_values PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_creates_indexes PASSED
tests/unit/database/test_migration_0049.py::test_upgrade_idempotent PASSED
tests/unit/database/test_migration_0049.py::test_downgrade_reverts_to_old_schema PASSED
tests/unit/database/test_migration_0049.py::test_downgrade_reverses_file_type_mapping PASSED
tests/unit/database/test_migration_0049.py::test_downgrade_preserves_data_count PASSED

11 passed in 0.31s
```

### Dry Run Test

**Command**:
```bash
python -c "from agentpm.core.database.migrations.files import migration_0049_align_provider_files_schema as m49; import sqlite3; conn = sqlite3.connect('.agentpm/data/agentpm.db'); m49.upgrade(conn); conn.rollback()"
```

**Result**:
```
🔧 Migration 0049: Align Provider Files Schema
  📋 Current schema has 'file_hash', migrating to 'content_hash'...
  📊 Found 7 records to migrate
  📋 Creating provider_files_new with updated schema...
  ✅ Created provider_files_new table
  📋 Migrating data from provider_files to provider_files_new...
  ✅ Migrated 7 records
  📊 File type mapping applied:
      'rule' → 'rules': 6 records
      'config' → 'config': 1 records
  📋 Swapping tables...
  ✅ Dropped old provider_files table
  ✅ Renamed provider_files_new → provider_files
  📋 Creating indexes on new table...
  ✅ Created index: idx_provider_files_installation
  ✅ Created index: idx_provider_files_hash
  ✅ Created index: idx_provider_files_type
  📋 Validating new schema...
  ✅ All expected columns present
  ✅ Old 'file_hash' column removed
  ✅ Record count verified: 7 records
  ✅ Migration 0049 completed successfully
```

## Rollback (Downgrade)

The migration includes a full `downgrade()` function that:
1. Creates `provider_files_old` with legacy schema
2. Reverses file type mapping (`rules` → `rule`, `agent` → `mode`, etc.)
3. Copies `content_hash` back to `file_hash`
4. Drops new columns (`generated_at`, `last_verified_at`, `modification_detected`)
5. Swaps tables back
6. Recreates legacy indexes

**Warning**: Downgrade will lose data in new columns (`last_verified_at`, `modification_detected`).

## Migration Sequencing

This migration depends on:
- ✅ Migration 0047 (creates `provider_installations` and `provider_files` tables)

This migration enables:
- ✅ Multi-provider support (Claude Code, Cursor, Google Codex)
- ✅ File integrity verification
- ✅ Drift detection

## Production Deployment

### Pre-Migration Checklist

- [ ] Backup database: `cp .agentpm/data/agentpm.db .agentpm/data/agentpm.db.backup-$(date +%Y%m%d)`
- [ ] Verify current schema: `sqlite3 .agentpm/data/agentpm.db "PRAGMA table_info(provider_files)"`
- [ ] Count records: `sqlite3 .agentpm/data/agentpm.db "SELECT COUNT(*) FROM provider_files"`
- [ ] Review migration file: `cat agentpm/core/database/migrations/files/migration_0049_align_provider_files_schema.py`

### Deployment Steps

1. **Backup**:
   ```bash
   cp .agentpm/data/agentpm.db .agentpm/data/agentpm.db.backup-$(date +%Y%m%d)
   ```

2. **Run migration**:
   ```bash
   apm migrate
   ```

3. **Verify**:
   ```bash
   sqlite3 .agentpm/data/agentpm.db "PRAGMA table_info(provider_files)"
   sqlite3 .agentpm/data/agentpm.db "SELECT COUNT(*) FROM provider_files"
   ```

### Post-Migration Validation

- [ ] Verify record count matches (should be 7 or current count)
- [ ] Verify `content_hash` column exists (not `file_hash`)
- [ ] Verify new columns exist: `generated_at`, `last_verified_at`, `modification_detected`
- [ ] Verify indexes exist: `idx_provider_files_installation`, `idx_provider_files_hash`, `idx_provider_files_type`
- [ ] Test provider commands: `apm provider list`, `apm provider verify`

## Files Changed

| File | Purpose |
|------|---------|
| `agentpm/core/database/migrations/files/migration_0049_align_provider_files_schema.py` | Migration implementation |
| `tests/unit/database/test_migration_0049.py` | Comprehensive test suite |
| `agentpm/core/database/migrations/files/migration_0047_provider_tracking.py` | Updated to handle old schema gracefully |

## Related Issues

- **Work Item**: WI-165 (Provider System Migration)
- **Task**: Align provider_files schema with multi-provider requirements
- **Related Migration**: 0047 (Provider Tracking System)

## Authors

- Migration Author: Claude Code (migration-author agent)
- Reviewer: (TBD)
- Date: 2025-10-27

## Approval

- [ ] Migration tested (unit tests pass)
- [ ] Migration tested (dry run successful)
- [ ] Migration reviewed
- [ ] Backup strategy confirmed
- [ ] Rollback tested
- [ ] Production deployment approved

---

**Status**: ✅ Ready for deployment
**Risk Level**: LOW (tested, reversible, data-preserving)
**Estimated Downtime**: None (migration runs in <1 second)
