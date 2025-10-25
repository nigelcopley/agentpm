# Document Management User Guide

Complete guide to using APM (Agent Project Manager)'s document management system with path validation enforcement.

---

## Table of Contents

1. [Overview](#overview)
2. [Path Structure](#path-structure)
3. [Document Categories](#document-categories)
4. [Document Types](#document-types)
5. [Adding Documents](#adding-documents)
6. [Migrating Documents](#migrating-documents)
7. [Exception Patterns](#exception-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What is the Document System?

APM (Agent Project Manager)'s document management system provides a **Universal Documentation System** that:

- **Links documents to entities** (projects, work items, tasks, ideas)
- **Enforces consistent path structure** across all documentation
- **Tracks document metadata** (type, category, format, size, hash)
- **Enables multi-dimensional search** via rich metadata
- **Validates path compliance** at 3 layers (Pydantic, CLI, Database)

### Why Path Structure Matters

Consistent path structure enables:

- **Predictable discovery**: Developers know exactly where to find documentation
- **Automated tooling**: Scripts can reliably locate and process documents
- **Clean organization**: Related documents are grouped logically
- **AI agent integration**: Agents can navigate documentation systematically
- **Migration safety**: Moving documents becomes safe and automated

---

## Path Structure

### Required Format

All documents **MUST** follow this canonical path structure:

```
docs/{category}/{document_type}/{filename}
```

**Examples**:

```
docs/architecture/design/database-schema.md
docs/planning/requirements/auth-functional.md
docs/guides/user_guide/getting-started.md
docs/reference/api_doc/rest-endpoints.md
docs/operations/runbook/deployment-procedure.md
```

### Path Components

| Component | Description | Valid Values |
|-----------|-------------|--------------|
| `docs/` | Fixed prefix (required) | Always `docs/` |
| `{category}` | Top-level grouping | 8 categories (see below) |
| `{document_type}` | Document classification | 25+ types (see below) |
| `{filename}` | File name with extension | Any valid filename |

### Validation Layers

The path structure is enforced at **3 layers**:

1. **Pydantic Model Layer** (`DocumentReference.validate_path_structure()`)
   - Validates `docs/` prefix
   - Checks minimum path depth (4 parts)
   - Verifies category/type consistency

2. **CLI Layer** (`apm document add`)
   - Guides users to correct paths
   - Offers auto-correction suggestions
   - Allows interactive path fixes

3. **Database Layer** (CHECK constraint)
   - Final enforcement at database level
   - Prevents non-compliant paths from being stored
   - Exception patterns for special cases (README.md, etc.)

---

## Document Categories

APM (Agent Project Manager) uses **8 universal categories** that work for any project type:

### 1. Planning (`planning/`)

**Purpose**: Strategic planning, requirements, and feature definitions

**Common Document Types**:
- `requirements` - Functional and non-functional requirements
- `user_story` - User-focused feature descriptions
- `use_case` - Detailed user interaction scenarios
- `refactoring_guide` - Code improvement and refactoring guidance
- `implementation_plan` - Step-by-step implementation roadmaps

**Examples**:
```
docs/planning/requirements/auth-system-requirements.md
docs/planning/user_story/user-login-flow.md
docs/planning/implementation_plan/phase-1-rollout.md
```

### 2. Architecture (`architecture/`)

**Purpose**: Technical design, system architecture, and decisions

**Common Document Types**:
- `architecture` - System architecture and technical design
- `design` - Detailed component and interface design
- `adr` - Architecture Decision Records
- `technical_specification` - Detailed technical implementation specs

**Examples**:
```
docs/architecture/design/database-schema.md
docs/architecture/adr/001-microservices-architecture.md
docs/architecture/architecture/system-overview.md
```

### 3. Guides (`guides/`)

**Purpose**: User-facing documentation, tutorials, and how-tos

**Common Document Types**:
- `user_guide` - End-user documentation and tutorials
- `admin_guide` - Administrator and operations documentation
- `troubleshooting` - Problem resolution and debugging guides
- `migration_guide` - System upgrade and migration instructions

**Examples**:
```
docs/guides/user_guide/getting-started.md
docs/guides/admin_guide/server-configuration.md
docs/guides/troubleshooting/common-errors.md
```

### 4. Reference (`reference/`)

**Purpose**: API documentation, specifications, and technical references

**Common Document Types**:
- `api_doc` - API reference and integration guides
- `specification` - Technical specifications and requirements

**Examples**:
```
docs/reference/api_doc/rest-api-v1.md
docs/reference/specification/data-model-spec.md
```

### 5. Processes (`processes/`)

**Purpose**: Team workflows, testing procedures, and standards

**Common Document Types**:
- `test_plan` - Testing strategy and test case documentation

**Examples**:
```
docs/processes/test_plan/integration-testing-strategy.md
docs/processes/test_plan/e2e-test-scenarios.md
```

### 6. Governance (`governance/`)

**Purpose**: Quality standards, policies, and compliance

**Common Document Types**:
- `quality_gates_specification` - Quality standards and validation criteria

**Examples**:
```
docs/governance/quality_gates_specification/code-review-checklist.md
docs/governance/quality_gates_specification/security-standards.md
```

### 7. Operations (`operations/`)

**Purpose**: Deployment, monitoring, and operational procedures

**Common Document Types**:
- `runbook` - Operational procedures and runbooks

**Examples**:
```
docs/operations/runbook/deployment-procedure.md
docs/operations/runbook/incident-response.md
docs/operations/runbook/backup-restore.md
```

### 8. Communication (`communication/`)

**Purpose**: Stakeholder reports, business analysis, and presentations

**Common Document Types**:
- `business_pillars_analysis` - Business foundation and strategic pillars
- `market_research_report` - Market analysis and competitive landscape
- `competitive_analysis` - Competitor feature and strategy analysis
- `stakeholder_analysis` - Stakeholder needs and impact assessment

**Examples**:
```
docs/communication/business_pillars_analysis/market-positioning.md
docs/communication/stakeholder_analysis/user-personas.md
```

---

## Document Types

### Viewing Available Types

Use the CLI to view all available document types with descriptions:

```bash
# Show all types, formats, and statuses
apm document types

# Show only document types
apm document types --type=document-type

# Show in list format
apm document types --format=list

# Show in JSON format (for scripting)
apm document types --format=json
```

### Category Mapping

Each document type maps to a specific category:

| Document Type | Category | Purpose |
|---------------|----------|---------|
| requirements | planning | Requirements documents |
| user_story | planning | User stories |
| use_case | planning | Use cases |
| implementation_plan | planning | Implementation plans |
| refactoring_guide | planning | Refactoring guides |
| architecture | architecture | Architecture docs |
| design | architecture | Design documents |
| adr | architecture | Architecture decisions |
| technical_specification | architecture | Technical specs |
| user_guide | guides | User documentation |
| admin_guide | guides | Admin documentation |
| troubleshooting | guides | Troubleshooting guides |
| migration_guide | guides | Migration instructions |
| api_doc | reference | API documentation |
| specification | reference | Specifications |
| test_plan | processes | Test plans |
| quality_gates_specification | governance | Quality standards |
| runbook | operations | Operational runbooks |
| business_pillars_analysis | communication | Business analysis |
| market_research_report | communication | Market research |
| competitive_analysis | communication | Competitive analysis |
| stakeholder_analysis | communication | Stakeholder docs |

---

## Adding Documents

### Basic Usage

Add a document reference to an entity:

```bash
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="docs/architecture/design/doc-system.md" \
  --type=design \
  --title="Documentation System Architecture"
```

### Auto-Detection

The CLI can auto-detect many properties:

```bash
# Auto-detect type, format, and title
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="docs/architecture/design/doc-system.md"

# CLI will infer:
# - type: design (from path pattern)
# - format: markdown (from .md extension)
# - title: "Doc System" (from filename)
```

### Interactive Path Correction

If you provide a non-compliant path, the CLI will guide you:

```bash
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="design/doc-system.md" \
  --type=design

# Output:
# ⚠️  Path does not follow standard structure
#
# 💡 Recommended path structure:
#    docs/architecture/design/doc-system.md
#
# 📁 Standard structure:
#    docs/{category}/{document_type}/{filename}
#
# 📂 Valid categories:
#    • architecture  - System design, technical architecture
#    • planning      - Requirements, user stories, plans
#    [... full category list ...]
#
# Use recommended path? [Y/n]:
```

### Optional Metadata

Add rich metadata for better discoverability:

```bash
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="docs/architecture/design/doc-system.md" \
  --type=design \
  --title="Documentation System Architecture" \
  --description="Complete technical design for the Universal Documentation System" \
  --created-by="doc-toucher"
```

### Skipping File Validation

For documents that don't exist yet:

```bash
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="docs/planning/requirements/future-feature.md" \
  --type=requirements \
  --no-validate-file
```

---

## Migrating Documents

### When to Migrate

Use migration when:

- Documents exist but don't follow the standard path structure
- You're reorganizing documentation for compliance
- You need to fix path violations in bulk
- Upgrading from pre-WI-113 documentation structure

### Migration Command Overview

The `apm document migrate-to-structure` command provides:

- **Dry-run mode**: Preview changes before executing
- **Automatic backups**: Copy files before moving (default: enabled)
- **Checksum validation**: SHA-256 verification prevents corruption
- **Atomic transactions**: Database updates rollback on error
- **Category inference**: Automatically maps document types to categories
- **Safe defaults**: Requires explicit confirmation before making changes

### Step 1: Dry-Run Analysis

**ALWAYS** run a dry-run first to preview changes:

```bash
apm document migrate-to-structure --dry-run
```

**Example Output:**

```
Document Migration Analysis

Found 50 document(s) requiring migration

┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃     ┃ Current Path                   ┃ Target Path                    ┃ Category           ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ →   │ WI-112-IMPLEMENTATION.md       │ docs/planning/                 │ planning (from     │
│     │                                │ implementation_plan/           │ implementation_    │
│     │                                │ WI-112-IMPLEMENTATION.md       │ plan)              │
├─────┼────────────────────────────────┼────────────────────────────────┼────────────────────┤
│ →   │ design/doc-system.md           │ docs/architecture/design/      │ architecture       │
│     │                                │ doc-system.md                  │ (from design)      │
├─────┼────────────────────────────────┼────────────────────────────────┼────────────────────┤
│ →   │ README-agents.md               │ docs/guides/user_guide/        │ guides (from       │
│     │                                │ README-agents.md               │ user_guide)        │
└─────┴────────────────────────────────┴────────────────────────────────┴────────────────────┘

Summary

Total documents: 50
Categories: architecture (15), planning (20), guides (10), operations (5)
Estimated disk space: 1.23 MB
Backup mode: enabled

--dry-run mode: No changes made
Use --execute to perform migration
```

### Step 2: Review Migration Plan

**Analyze the dry-run output:**

1. **Check target paths** - Verify categories are correct
2. **Review category mapping** - Ensure document types map to expected categories
3. **Identify issues** - Look for unexpected paths or missing files
4. **Plan exceptions** - Note any documents needing manual handling

**Category Inference Logic:**

| Document Type | Auto-Inferred Category | Override Example |
|---------------|------------------------|------------------|
| requirements | planning | `--category=archive` |
| design | architecture | - |
| user_guide | guides | - |
| runbook | operations | - |
| test_plan | processes | - |

### Step 3: Execute Migration

Once satisfied with the plan, execute the migration:

```bash
apm document migrate-to-structure --execute
```

**Interactive Confirmation:**

```
⚠️  WARNING: This will move physical files and update database records.

Continue with migration? [y/N]:
```

**Migration Progress:**

```
Starting migration...

Migrating: WI-112-IMPLEMENTATION.md
  Backup created: .aipm/backups/document-migration/WI-112-IMPLEMENTATION-20251020-143022.md
  ✓ Migrated: WI-112-IMPLEMENTATION.md → docs/planning/implementation_plan/WI-112-IMPLEMENTATION.md

Migrating: design/doc-system.md
  Backup created: .aipm/backups/document-migration/doc-system-20251020-143023.md
  ✓ Migrated: design/doc-system.md → docs/architecture/design/doc-system.md

Migration Complete

✓ Successful: 45
✗ Failed: 5
Total processed: 50

Backups stored in: .aipm/backups/document-migration
```

### Step 4: Post-Migration Verification

Verify migration success:

```bash
# Check updated database records
apm document list --entity-type=work_item --entity-id=113

# Verify files exist at new paths
ls docs/planning/implementation_plan/
ls docs/architecture/design/

# Verify backups created
ls .aipm/backups/document-migration/
```

### Advanced Options

**Override Category Inference:**

```bash
# Force all documents to specific category
apm document migrate-to-structure --execute --category=archive
```

**Disable Backups (USE WITH CAUTION):**

```bash
# Skip backup creation (faster, but risky)
apm document migrate-to-structure --execute --no-backup
```

**Combination Example:**

```bash
# Dry-run with category override
apm document migrate-to-structure --dry-run --category=communication
```

### Migration Safety Features

The migration system includes multiple safety mechanisms:

1. **Transaction Safety**: Database updates are atomic (all-or-nothing)
2. **Backup Mode**: Files copied before moving (can restore on error)
3. **Checksum Validation**: SHA-256 hashes verified before/after move
4. **Dry-Run Mode**: Preview changes without modifications
5. **Confirmation Prompt**: Explicit user consent required for --execute
6. **Automatic Rollback**: On any error, backups restored and database reverted

### Troubleshooting Migration

**Issue: Migration fails with "Target already exists"**

```bash
# Solution: Check for duplicate files
find docs/ -name "my-doc.md"

# If duplicate is unwanted, remove it first
rm docs/architecture/design/my-doc.md

# Re-run migration
apm document migrate-to-structure --execute
```

**Issue: Checksum mismatch after migration**

```
✗ Migration failed: Checksum mismatch! Rolled back.
```

**Solution**: File was modified during migration (rare). Check file permissions:

```bash
ls -la my-doc.md
chmod 644 my-doc.md  # Ensure readable/writable
```

**Issue: Database constraint violation**

```
✗ Migration failed: CHECK constraint failed: document_references
```

**Solution**: Path doesn't meet validation rules. Check exceptions in [Exception Patterns](#exception-patterns)

### Manual Migration Fallback

If automated migration fails, migrate documents manually:

```bash
# 1. Create target directory
mkdir -p docs/architecture/design

# 2. Move file
mv design/doc-system.md docs/architecture/design/

# 3. Update database record
apm document update <doc-id> \
  --file-path="docs/architecture/design/doc-system.md"
```

---

## Exception Patterns

### Non-docs/ Paths Allowed

Certain paths are **exempt** from the `docs/` prefix requirement:

| Pattern | Allowed? | Reason |
|---------|----------|--------|
| `README.md` | ✅ Yes | Repository root documentation |
| `CHANGELOG.md` | ✅ Yes | Version history at root |
| `LICENSE` | ✅ Yes | Legal file at root |
| `CONTRIBUTING.md` | ✅ Yes | Contribution guidelines at root |
| `.claude/agents/*.md` | ✅ Yes | Agent definition files |
| `_RULES/*.md` | ✅ Yes | Rules system files |
| Custom root files | ✅ Yes | Project-specific exceptions |

### Database CHECK Constraint

The database enforces path compliance with exceptions:

```sql
CHECK (
  file_path LIKE 'docs/%'  -- Standard path
  OR file_path LIKE 'README%'
  OR file_path LIKE 'CHANGELOG%'
  OR file_path LIKE 'LICENSE%'
  OR file_path LIKE 'CONTRIBUTING%'
  OR file_path LIKE '.claude/agents/%'
  OR file_path LIKE '_RULES/%'
)
```

---

## Troubleshooting

### Error: "Document path must start with 'docs/'"

**Problem**: Path doesn't follow required structure

**Solution**:
```bash
# Wrong:
apm document add --file-path="design/my-doc.md"

# Correct:
apm document add --file-path="docs/architecture/design/my-doc.md"
```

### Error: "Path must follow pattern: docs/{category}/{document_type}/{filename}"

**Problem**: Path depth is insufficient (less than 4 parts)

**Solution**:
```bash
# Wrong:
apm document add --file-path="docs/design.md"

# Correct:
apm document add --file-path="docs/architecture/design/my-design.md"
```

### Error: "Path category 'X' doesn't match field category 'Y'"

**Problem**: Category in path doesn't match document_type's mapped category

**Solution**: Use category mapping (see [Document Types](#category-mapping))

```bash
# Wrong (design maps to 'architecture', not 'planning'):
apm document add \
  --file-path="docs/planning/design/my-doc.md" \
  --type=design

# Correct:
apm document add \
  --file-path="docs/architecture/design/my-doc.md" \
  --type=design
```

### Error: "File not found"

**Problem**: File doesn't exist at specified path

**Solution 1**: Create the file first
```bash
mkdir -p docs/architecture/design
touch docs/architecture/design/my-doc.md
apm document add --file-path="docs/architecture/design/my-doc.md"
```

**Solution 2**: Skip validation for future files
```bash
apm document add \
  --file-path="docs/architecture/design/my-doc.md" \
  --no-validate-file
```

### Migration Issues

**Problem**: Migration dry-run shows unexpected paths

**Solution**: Review category mapping and adjust manually if needed

```bash
# 1. Run dry-run
apm document migrate-to-structure --dry-run > migration-plan.txt

# 2. Review plan
cat migration-plan.txt

# 3. For any incorrect paths, update manually:
apm document update <doc-id> --file-path="correct/path/here.md"

# 4. Execute migration for remaining documents
apm document migrate-to-structure
```

### Database Constraint Violation

**Problem**: Direct database insert fails with CHECK constraint

**Solution**: Always use CLI commands, which handle path validation:

```bash
# Don't: Direct database manipulation
sqlite3 .aipm/aipm.db "INSERT INTO document_references ..."

# Do: Use CLI
apm document add --file-path="docs/..." --type=...
```

---

## Next Steps

- **View all documents**: `apm document list --entity-type=work_item --entity-id=<id>`
- **Search documents**: Use rich metadata filters (coming soon)
- **Update metadata**: `apm document update <doc-id> --title="New Title"`
- **Developer guide**: See `docs/guides/developer_guide/document-system-architecture.md`
- **Migration runbook**: See `docs/operations/runbook/document-migration-runbook.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-19
**Related**: WI-113 (Document Path Validation Enforcement)
