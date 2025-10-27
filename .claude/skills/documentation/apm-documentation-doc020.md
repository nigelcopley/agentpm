---
# Skill Metadata (Level 1)
name: apm-documentation-doc020
display_name: APM Documentation - DOC-020 Compliance
description: Database-first documentation: ALWAYS use 'apm document add' command, NEVER Write/Edit for docs/
category: documentation
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:
  - Bash

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.597370
updated_at: 2025-10-27T18:34:16.597370
---

# APM Documentation - DOC-020 Compliance

## Description
Database-first documentation: ALWAYS use 'apm document add' command, NEVER Write/Edit for docs/

**Category**: documentation

---

## Instructions (Level 2)

# APM Documentation - DOC-020 Compliance

## CRITICAL RULE: Database-First Documents

**ALWAYS use**: `apm document add` command
**NEVER use**: Write/Edit/Bash for docs/ directory

## Rule: DOC-020
- **Enforcement**: BLOCK (hard failure)
- **Category**: Documentation Principles
- **Priority**: CRITICAL

## Correct Pattern

### ✅ ALWAYS Do This:
```bash
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --category=planning \
  --type=requirements \
  --title="Phase 1 Specification" \
  --description="Comprehensive specification for Phase 1" \
  --content="$(cat <<'EOF'
# Phase 1 Specification

## Overview
...
EOF
)"
```

### ❌ NEVER Do This:
```python
# PROHIBITED - Violation of DOC-020
Write(file_path="docs/features/spec.md", content="...")
Edit(file_path="docs/guide.md", old_string="...", new_string="...")
Bash(command="echo '...' > docs/file.md")
```

## Required Fields
| Field | Required | Example |
|-------|----------|---------|
| `--entity-type` | ✅ | `work-item`, `task`, `project` |
| `--entity-id` | ✅ | `158` |
| `--category` | ✅ | `planning`, `architecture`, `guides` |
| `--type` | ✅ | `requirements`, `design_doc`, `user_guide` |
| `--title` | ✅ | `Phase 1 Specification` |
| `--content` | ✅ | Full markdown content |
| `--description` | Recommended | Brief summary |

## File Path Patterns
```
docs/
  ├── features/           # category: planning, type: requirements
  ├── architecture/       # category: architecture
  │   ├── design/        # type: design_doc
  │   └── adrs/          # type: adr
  ├── guides/            # category: guides
  │   ├── user/          # type: user_guide
  │   ├── developer/     # type: developer_guide
  │   └── admin/         # type: admin_guide
  ├── reference/         # category: reference
  ├── processes/         # category: processes
  └── operations/        # category: operations
```

## Why This Rule Exists
1. **Database is source of truth**: All documents tracked
2. **Entity linkage**: Documents linked to work items, tasks
3. **Metadata completeness**: Category, type, title maintained
4. **Consistent file naming**: Standard path patterns enforced
5. **Document lifecycle**: Creation, updates, archival tracked

---

## Resources (Level 3)

### Examples
- `apm document add --entity-type=work-item --entity-id=158 ...`
- `Context-aware path generation`
- `Visibility scopes: private/team/public`

### Templates
- `document_add_command_template.sh`

### Documentation
- [docs/rules/DOC-020_DATABASE_FIRST_DOCUMENTS.md](docs/rules/DOC-020_DATABASE_FIRST_DOCUMENTS.md)
- [.agentpm/docs/processes/runbook/document-visibility-and-lifecycle-workflow.md](.agentpm/docs/processes/runbook/document-visibility-and-lifecycle-workflow.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Documentation - DOC-020 Compliance",
  prompt=\"\"\"
  Apply apm-documentation-doc020 skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Documentation - DOC-020 Compliance skill.
  \"\"\"
)
```

---

**Skill ID**: 4
**Generated**: 2025-10-27T18:35:40.564649
**Status**: Enabled
