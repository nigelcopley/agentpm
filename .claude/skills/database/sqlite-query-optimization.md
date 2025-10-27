---
# Skill Metadata (Level 1)
name: sqlite-query-optimization
display_name: SQLite Query Optimization
description: Performance optimization: indexes, query planning, JOIN strategies, pagination patterns
category: database
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:
  - Read
  - Bash

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.597054
updated_at: 2025-10-27T18:34:16.597054
---

# SQLite Query Optimization

## Description
Performance optimization: indexes, query planning, JOIN strategies, pagination patterns

**Category**: database

---

## Instructions (Level 2)

# SQLite Query Optimization

## Index Strategy

### Covering Indexes
```sql
-- Query: SELECT name, category FROM skills WHERE enabled = 1
-- Optimal index (covering):
CREATE INDEX idx_skills_enabled_covering ON skills(enabled, name, category);
```

### Composite Indexes
```sql
-- Query: SELECT * FROM agent_skills WHERE agent_id = ? AND skill_id = ?
-- Optimal index:
CREATE INDEX idx_agent_skills_composite ON agent_skills(agent_id, skill_id);
```

## Query Patterns

### Efficient JOINs
```sql
-- Use indexes on JOIN columns
SELECT s.*, ags.priority
FROM skills s
JOIN agent_skills ags ON s.id = ags.skill_id
WHERE ags.agent_id = ?
ORDER BY ags.priority DESC;
```

### Pagination
```sql
-- Use LIMIT/OFFSET with ORDER BY
SELECT * FROM skills
WHERE enabled = 1
ORDER BY category, name
LIMIT 20 OFFSET 40;
```

## Best Practices
1. **Index foreign keys**: Always index JOIN columns
2. **Use EXPLAIN QUERY PLAN**: Verify index usage
3. **Avoid SELECT ***: Only select needed columns
4. **Limit result sets**: Use LIMIT for pagination
5. **Order consistently**: ORDER BY indexed columns

## Anti-Patterns
❌ Missing indexes on WHERE clauses
❌ SELECT * with large tables
❌ OFFSET pagination without indexes
❌ OR conditions (use IN instead)

---

## Resources (Level 3)

### Examples
- `SELECT with covering indexes`
- `Efficient JOIN patterns`
- `Pagination with LIMIT/OFFSET`

### Templates
- `optimized_query_patterns.sql`

### Documentation
- [docs/architecture/query-optimization-guide.md](docs/architecture/query-optimization-guide.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring SQLite Query Optimization",
  prompt=\"\"\"
  Apply sqlite-query-optimization skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the SQLite Query Optimization skill.
  \"\"\"
)
```

---

**Skill ID**: 3
**Generated**: 2025-10-27T18:35:40.564535
**Status**: Enabled
