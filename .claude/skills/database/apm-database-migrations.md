---
# Skill Metadata (Level 1)
name: apm-database-migrations
display_name: APM Database Migrations
description: SQLite migration best practices: idempotent operations, data preservation, rollback safety
category: database
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:
  - Read
  - Write
  - Bash

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.595701
updated_at: 2025-10-27T18:34:16.595705
---

# APM Database Migrations

## Description
SQLite migration best practices: idempotent operations, data preservation, rollback safety

**Category**: database

---

## Instructions (Level 2)

# APM Database Migrations

## Overview
SQLite migration best practices for APM database schema evolution.

## Principles
1. **Idempotent operations**: Safe to run multiple times
2. **Data preservation**: Never lose existing data
3. **Rollback safety**: Migrations can be reversed
4. **Backward compatibility**: Gradual schema evolution

## Pattern
```sql
-- Migration: 0050_add_skills_tables.sql

-- Check if table exists
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT,
    instructions TEXT NOT NULL,
    resources TEXT,  -- JSON
    provider_config TEXT,  -- JSON
    enabled INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_enabled ON skills(enabled);
```

## Best Practices
- Always use `CREATE TABLE IF NOT EXISTS`
- Always use `CREATE INDEX IF NOT EXISTS`
- Use TEXT for JSON data (SQLite limitation)
- Add constraints inline (PRIMARY KEY, NOT NULL, UNIQUE)
- Use triggers for updated_at timestamps
- Test migrations on copy of database first

## Anti-Patterns
❌ DROP TABLE without backup
❌ ALTER TABLE without data migration
❌ Missing IF NOT EXISTS checks
❌ Breaking changes without version bump

---

## Resources (Level 3)

### Examples
- `0050_add_skills_tables.sql`
- `0051_add_hooks_tables.sql`
- `0052_add_memory_tables.sql`

### Templates
- `migration_template.sql`

### Documentation
- [docs/architecture/database-migration-patterns.md](docs/architecture/database-migration-patterns.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Database Migrations",
  prompt=\"\"\"
  Apply apm-database-migrations skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Database Migrations skill.
  \"\"\"
)
```

---

**Skill ID**: 1
**Generated**: 2025-10-27T18:35:40.560634
**Status**: Enabled
