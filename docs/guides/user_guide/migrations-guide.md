# Database Migrations Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-18
**Scope**: APM (Agent Project Manager) Database Schema Migrations

---

## Table of Contents

- [Overview](#overview)
- [Migration Framework](#migration-framework)
- [Running Migrations](#running-migrations)
- [Migration History](#migration-history)
- [Troubleshooting](#troubleshooting)
- [Development Guide](#development-guide)

---

## Overview

APM (Agent Project Manager) uses a **Django-inspired migration framework** to manage database schema changes incrementally. Each migration is a versioned Python file that can be applied (upgrade) or rolled back (downgrade).

### Key Principles

1. **Incremental Changes**: Apply schema changes one at a time
2. **Version Control**: All migrations tracked in git
3. **Rollback Safety**: Can undo migrations if issues arise
4. **Idempotent**: Migrations can be run multiple times safely
5. **Validated**: Pre/post checks ensure schema integrity

### Architecture

```
agentpm/core/database/migrations/
├── __init__.py
├── manager.py              # MigrationManager class
├── loader.py               # Migration file loader
├── models.py               # Migration metadata models
├── files/                  # Migration files directory
│   ├── migration_0001.py
│   ├── migration_0020.py
│   ├── migration_0027.py
│   └── migration_0029.py
└── README.md               # Migration catalog
```

---

## Migration Framework

### MigrationManager

The `MigrationManager` orchestrates migration execution:

```python
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.migrations import MigrationManager

db = DatabaseService('.aipm/data/aipm.db')
manager = MigrationManager(db)

# Discover available migrations
all_migrations = manager.discover_migrations()

# Get pending migrations
pending = manager.get_pending_migrations()

# Run all pending migrations
for migration in pending:
    manager.run_migration(migration)
```

### Migration File Structure

Each migration file follows this pattern:

```python
"""
Migration NNNN: Brief description

Detailed explanation of changes.

Dependencies:
- Migration XXXX (prerequisite)

Author: WI-XXX
Date: YYYY-MM-DD
"""

import sqlite3

def upgrade(conn: sqlite3.Connection) -> None:
    """Apply forward migration"""
    # Schema changes here
    pass

def downgrade(conn: sqlite3.Connection) -> None:
    """Rollback migration"""
    # Rollback logic here
    pass

def validate_pre(conn: sqlite3.Connection) -> bool:
    """Optional: Pre-migration validation"""
    return True

def validate_post(conn: sqlite3.Connection) -> bool:
    """Optional: Post-migration validation"""
    return True
```

---

## Running Migrations

### CLI Commands

```bash
# Check pending migrations
apm migrate --list

# Run all pending migrations
apm migrate

# Show applied migrations
apm migrate --show-applied

# Rollback specific migration
apm migrate --rollback 0027
```

### Programmatic Execution

```python
from agentpm.core.database import DatabaseService

db = DatabaseService('.aipm/data/aipm.db')
result = db.migrate()  # Runs all pending migrations
print(f"Applied {result} migration(s)")
```

### Verification

After running migrations, verify with:

```bash
# Check schema version
sqlite3 .aipm/data/aipm.db "SELECT MAX(version) FROM schema_migrations"

# Verify table schema
sqlite3 .aipm/data/aipm.db "PRAGMA table_info(agents)"

# Run integrity check
sqlite3 .aipm/data/aipm.db "PRAGMA integrity_check"

# Test application
apm status
apm agents list
```

---

## Migration History

### Migration 0027: Schema Fix for Agents Metadata

**Version**: 0027
**Date**: 2025-10-17
**Type**: Schema Fix
**Status**: Required

#### Problem

Migration 0020 recreated the `agents` table to fix the `tier` column type (TEXT → INTEGER), but inadvertently omitted the `metadata` column during table recreation.

**Error Observed**:
```
sqlite3.OperationalError: table agents has no column named metadata
```

This error occurred when:
- Migration 0029 attempted to INSERT agent records with `metadata` values
- Agent generation system tried to store behavioral rules
- Any code querying `agents.metadata` column

#### Solution

Migration 0027 adds the missing `metadata` column back to the `agents` table:

```sql
ALTER TABLE agents
ADD COLUMN metadata TEXT DEFAULT '{}'
```

#### Schema Change

**Before Migration 0027**:
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    sop_content TEXT,
    capabilities TEXT DEFAULT '[]',
    is_active INTEGER DEFAULT 1,
    agent_type TEXT DEFAULT NULL,
    file_path TEXT DEFAULT NULL,
    generated_at TIMESTAMP DEFAULT NULL,
    tier INTEGER CHECK(tier IN (1, 2, 3)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- metadata column MISSING
);
```

**After Migration 0027**:
```sql
CREATE TABLE agents (
    -- ... (all previous columns)
    tier INTEGER CHECK(tier IN (1, 2, 3)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'  -- ADDED
);
```

#### Affected Components

1. **Agent Generation System**
   - `agentpm/core/agents/generator.py`
   - Stores behavioral rules in `metadata` column

2. **Migration 0029 (Utility Agents)**
   - Inserts 5 utility agents with `metadata` values
   - **Dependency**: Must run AFTER migration 0027

3. **All CLI Commands Querying Agents**
   - `apm agents list`
   - `apm agents show <role>`
   - `apm status` (shows agent counts)

#### Verification Steps

```bash
# 1. Check column exists
sqlite3 .aipm/data/aipm.db "PRAGMA table_info(agents)" | grep metadata
# Expected: 14|metadata|TEXT|0|'{}'|0

# 2. Test agents list command
apm agents list
# Should not error

# 3. Verify migration 0029 can run
apm migrate --list
# Should show 0029 as pending (if not already applied)

# 4. Test agent metadata query
sqlite3 .aipm/data/aipm.db "SELECT role, metadata FROM agents LIMIT 1"
# Should return valid results
```

#### Rollback Procedure

**WARNING**: Rollback will **delete all metadata** stored in the `metadata` column.

1. **Backup database first**:
   ```bash
   cp .aipm/data/aipm.db .aipm/data/aipm.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **Verify backup**:
   ```bash
   sqlite3 .aipm/data/aipm.db.backup.* "SELECT COUNT(*) FROM agents"
   ```

3. **Run rollback**:
   ```bash
   apm migrate --rollback 0027
   ```

4. **Verify rollback succeeded**:
   ```bash
   sqlite3 .aipm/data/aipm.db "PRAGMA table_info(agents)" | grep metadata
   # Should return nothing (column removed)
   ```

5. **Restore agents if needed**:
   ```bash
   # If agents were corrupted, restore from backup
   cp .aipm/data/aipm.db.backup.* .aipm/data/aipm.db
   ```

#### Performance Impact

- **Execution Time**: <100ms (typical agents table has <100 rows)
- **Disk Space**: Minimal (+8 bytes per agent row for empty JSON `{}`)
- **Migration Type**: Additive (no data migration required)
- **Downtime**: None (schema change is atomic)

#### Dependencies

**Prerequisites** (must be applied before 0027):
- Migration 0020: Agents table exists with tier as INTEGER

**Dependents** (require 0027 to be applied):
- Migration 0029: Inserts utility agents with metadata values

**Relationship Diagram**:
```
0020 (Fix agents.tier) → 0027 (Add metadata) → 0029 (Utility agents)
```

#### Common Issues

**Issue 1**: "duplicate column name: metadata"

**Cause**: Migration 0027 already applied
**Solution**: Migration is idempotent, safe to ignore
**Verification**:
```bash
apm migrate --show-applied | grep 0027
```

**Issue 2**: Migration 0029 still fails with "no column named metadata"

**Cause**: Database cache issue or transaction not committed
**Solution**:
1. Restart application/CLI
2. Verify column exists: `PRAGMA table_info(agents)`
3. Check migration was recorded: `SELECT * FROM schema_migrations WHERE version='0027'`

**Issue 3**: Rollback fails with foreign key constraint error

**Cause**: Other tables reference agents.id with foreign keys
**Solution**: Rollback disables foreign keys temporarily (PRAGMA foreign_keys = OFF)
**Verification**: Check downgrade() function in migration_0027.py

---

## Troubleshooting

### General Migration Issues

#### Migrations Not Running

**Symptom**: `apm migrate` shows no pending migrations, but schema is wrong

**Diagnosis**:
```bash
# Check current schema version
sqlite3 .aipm/data/aipm.db "SELECT MAX(version) FROM schema_migrations"

# List all applied migrations
sqlite3 .aipm/data/aipm.db "SELECT version, description, applied_at FROM schema_migrations ORDER BY version"

# Compare with available migrations
ls -1 agentpm/core/database/migrations/files/ | grep migration_
```

**Solutions**:
1. **Migration file missing**: Copy from git history or regenerate
2. **Schema migrations table corrupted**: Restore from backup
3. **Migration already applied manually**: Add record to schema_migrations table

#### Migration Fails Mid-Execution

**Symptom**: Migration crashes, database in inconsistent state

**Diagnosis**:
```bash
# Check for partial migration
sqlite3 .aipm/data/aipm.db "SELECT * FROM schema_migrations WHERE version='NNNN'"

# Verify schema integrity
sqlite3 .aipm/data/aipm.db "PRAGMA integrity_check"

# Check foreign key violations
sqlite3 .aipm/data/aipm.db "PRAGMA foreign_key_check"
```

**Solutions**:
1. **Rollback failed migration**: `apm migrate --rollback NNNN`
2. **Restore from backup**: `cp .aipm/data/aipm.db.backup .aipm/data/aipm.db`
3. **Manually fix schema**: Use SQL to repair (advanced)
4. **Re-run migration**: If idempotent, can retry

#### Rollback Fails

**Symptom**: `apm migrate --rollback NNNN` errors or leaves database corrupted

**Diagnosis**:
```bash
# Check if downgrade() exists
grep -A 10 "def downgrade" agentpm/core/database/migrations/files/migration_NNNN.py

# Check for foreign key violations
sqlite3 .aipm/data/aipm.db "PRAGMA foreign_key_check"
```

**Solutions**:
1. **No downgrade() function**: Rollback not supported, restore from backup
2. **Foreign key violations**: Manually remove dependent data first
3. **SQLite limitations**: Some operations can't be rolled back (DROP TABLE)

### SQLite-Specific Issues

#### ALTER TABLE Limitations

SQLite has limited ALTER TABLE support:

**Supported**:
- `ADD COLUMN` (with limitations)

**NOT Supported** (before v3.35.0):
- `DROP COLUMN`
- `RENAME COLUMN`
- `ALTER COLUMN type`
- Modify constraints

**Workaround**: Table recreation pattern (see migration_0027.downgrade() for example)

#### Foreign Keys During Table Recreation

**Issue**: Foreign keys prevent table DROP/RECREATE

**Solution**: Temporarily disable foreign keys:
```python
def downgrade(conn):
    conn.execute("PRAGMA foreign_keys = OFF")
    # Recreate table
    conn.execute("PRAGMA foreign_keys = ON")
```

**Warning**: Ensure referential integrity maintained during recreation

---

## Development Guide

### Creating New Migrations

#### Step 1: Determine Version Number

```bash
# Find latest migration
ls -1 agentpm/core/database/migrations/files/ | tail -1
# Example output: migration_0029.py

# Next migration: 0030
```

#### Step 2: Create Migration File

```bash
# Create file
touch agentpm/core/database/migrations/files/migration_0030.py
```

#### Step 3: Write Migration

Use the template from ADR-005 (docs/components/database/adrs/005-migration-framework.md):

```python
"""
Migration 0030: Add feature_flags table

Adds feature_flags table for per-project feature toggles.

Dependencies:
- Migration 0001 (projects table exists)

Author: WI-XXX
Date: YYYY-MM-DD
"""

import sqlite3

def upgrade(conn: sqlite3.Connection) -> None:
    """Create feature_flags table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feature_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            flag_name TEXT NOT NULL,
            enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            UNIQUE(project_id, flag_name)
        )
    """)

def downgrade(conn: sqlite3.Connection) -> None:
    """Remove feature_flags table"""
    conn.execute("DROP TABLE IF EXISTS feature_flags")
```

#### Step 4: Test Migration

```bash
# Create test database
cp .aipm/data/aipm.db .aipm/data/aipm.db.test

# Test upgrade
python -c "
from agentpm.core.database.service import DatabaseService
db = DatabaseService('.aipm/data/aipm.db.test')
db.migrate()
"

# Verify schema
sqlite3 .aipm/data/aipm.db.test "PRAGMA table_info(feature_flags)"

# Test rollback
apm migrate --rollback 0030

# Clean up
rm .aipm/data/aipm.db.test
```

#### Step 5: Document Migration

Add entry to this guide under [Migration History](#migration-history)

#### Step 6: Commit

```bash
git add agentpm/core/database/migrations/files/migration_0030.py
git add docs/database/migrations-guide.md
git commit -m "feat(database): Add feature_flags table migration

- Migration 0030: Create feature_flags table
- Support per-project feature toggles
- Includes rollback strategy

Related: WI-XXX"
```

### Migration Best Practices

1. **Always make migrations idempotent**
   - Use `IF NOT EXISTS` / `IF EXISTS` clauses
   - Check for column existence before ALTER TABLE
   - Safe to run multiple times

2. **Include comprehensive docstrings**
   - Explain WHY migration is needed
   - Document dependencies
   - Describe rollback strategy
   - Provide verification steps

3. **Test both upgrade and downgrade**
   - Verify upgrade applies correctly
   - Verify downgrade removes changes
   - Ensure data preserved during rollback

4. **Consider SQLite limitations**
   - Use table recreation for unsupported operations
   - Disable foreign keys when recreating tables
   - Preserve indexes and triggers

5. **Document breaking changes**
   - Warn if migration loses data
   - Provide migration path for existing data
   - Update dependent code/docs

---

## References

- **ADR-005**: Professional Database Migration Framework
  - Location: `docs/components/database/adrs/005-migration-framework.md`
  - Details: Architecture, patterns, best practices

- **Migration Manager**: Implementation details
  - Location: `agentpm/core/database/migrations/manager.py`
  - API reference, usage examples

- **Schema Migration Analysis**: Historical analysis
  - Location: `docs/migrations/SCHEMA-MIGRATION-ANALYSIS.md`
  - Migration history, schema evolution

- **SQLite ALTER TABLE Documentation**
  - https://www.sqlite.org/lang_altertable.html
  - Limitations and supported operations

---

## Changelog

### 1.0.0 (2025-10-18)
- Initial migrations guide
- Comprehensive documentation for migration 0027
- Troubleshooting section
- Development guide for creating new migrations

---

**Maintained by**: APM (Agent Project Manager) Development Team
**Related Work Items**: WI-108 (Migration 0027 Documentation)
