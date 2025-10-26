# Document Management User Guide

## Overview

AgentPM provides a comprehensive document management system that treats the **database as the source of truth**. Unlike traditional file-based documentation systems, AgentPM tracks all document metadata, content, and lifecycle stages in the database, ensuring consistency, traceability, and intelligent document organization.

### Key Concepts

- **Database-First**: All documents are created and managed through the database
- **Auto-Generated Paths**: File paths are automatically generated from metadata
- **Visibility Control**: Documents can be private, team-restricted, or public
- **Lifecycle Management**: Documents progress through draft → review → approved → published stages
- **Entity Linking**: Documents are linked to work items, tasks, ideas, or projects

## Document Visibility System

AgentPM uses a sophisticated visibility system to control where documents are stored and who can access them.

### Visibility Levels

| Visibility | Description | Storage Location | Use Cases |
|------------|-------------|------------------|-----------|
| **Private** | Internal-only, sensitive | `.agentpm/docs/` (git-ignored) | Research notes, personal drafts, sensitive data |
| **Restricted** | Team members only | `.agentpm/docs/` | Work-in-progress, internal specs |
| **Public** | External audience | `docs/` (git-tracked) | User guides, API docs, public specifications |

### Automatic Visibility Detection

The system automatically determines visibility based on document type:

**Always Private** (force_private=true):
- Personal notes and drafts
- Sensitive research reports
- Investigation reports
- Internal assessment reports

**Public When Approved** (force_public=true):
- User guides (user_guide)
- Admin guides (admin_guide)
- API documentation (api_doc)
- Public specifications (specification)

**Context-Aware** (scored):
- Architecture documents (design_doc, adr)
- Technical specifications
- Planning documents

### Visibility Scoring

For context-aware documents, visibility is calculated using:

**Base Score** (from document type policy):
- 0-30: Private
- 31-60: Restricted
- 61-100: Public

**Context Modifiers**:
- Team size: Solo (+0), Small (-10), Medium (-20), Large (-30)
- Development stage: Development (+0), Staging (+20), Production (+40)
- Collaboration model: Private (+0), Internal (-10), Open Source (+30)

**Example Calculation**:
```
Base Score: 50 (design_doc)
+ Team Size (solo): +0
+ Dev Stage (production): +40
+ Collab Model (open_source): +30
= Final Score: 120 → Public
```

## Creating Documents

### Database-First Workflow (RECOMMENDED)

**Always use the `apm document add` command** to create documents. This ensures proper database tracking and metadata.

#### Basic Example

```bash
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --category=guides \
  --type=user_guide \
  --title="Getting Started with AgentPM" \
  --content="$(cat <<'EOF_CONTENT'
# Getting Started with AgentPM

## Installation
...your content here...
EOF_CONTENT
)"
```

**What Happens**:
1. Document record created in database
2. File path auto-generated: `docs/guides/user_guide/getting-started-with-agentpm.md`
3. Visibility auto-detected: Public (user_guide → force_public)
4. Lifecycle stage: Draft
5. File created with content

#### With Explicit Path

```bash
apm document add \
  --entity-type=task \
  --entity-id=1091 \
  --category=architecture \
  --type=design_doc \
  --title="Database Schema Design" \
  --file-path="docs/architecture/database-schema.md"
```

**What Happens**:
1. System validates path matches category/type
2. If mismatch, path is corrected automatically
3. Example: `docs/old/schema.md` → `docs/architecture/design_doc/database-schema-design.md`

### File Path Generation Rules

**Automatic Path Structure**:
```
{visibility_dir}/{category}/{document_type}/{filename}
```

**Visibility Directories**:
- Private/Restricted: `.agentpm/docs/`
- Public: `docs/`

**Filename Generation**:
- Convert title to lowercase
- Replace spaces with hyphens
- Remove special characters
- Add `.md` extension
- Handle conflicts with numeric suffix

**Examples**:

| Title | Category | Type | Visibility | Generated Path |
|-------|----------|------|------------|----------------|
| "User Authentication Design" | architecture | design_doc | private | `.agentpm/docs/architecture/design_doc/user-authentication-design.md` |
| "API Reference" | reference | api_doc | public | `docs/reference/api_doc/api-reference.md` |
| "Getting Started" | guides | user_guide | public | `docs/guides/user_guide/getting-started.md` |

### Required Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `--entity-type` | ✅ | What this documents | `work-item`, `task`, `idea`, `project` |
| `--entity-id` | ✅ | Which entity ID | `158` |
| `--category` | ✅ | Document category | `guides`, `architecture`, `planning` |
| `--type` | ✅ | Document type | `user_guide`, `design_doc`, `adr` |
| `--title` | ✅ | Clear title | `"Getting Started Guide"` |
| `--content` | Recommended | Document content | Markdown text |
| `--file-path` | Optional | Override path | Auto-generated if omitted |
| `--description` | Recommended | Brief summary | `"Introduction for new users"` |

### Available Categories and Types

Use `apm document types` to see all available combinations:

**Categories**:
- `planning`: Requirements, research, analysis
- `architecture`: Design docs, ADRs, technical specs
- `guides`: User, admin, developer guides
- `reference`: API docs, specifications
- `processes`: Implementation plans, test plans
- `governance`: Business pillars, quality gates
- `operations`: Runbooks, deployment guides
- `communication`: Status reports, summaries

## Document Lifecycle Stages

Documents progress through a defined lifecycle with quality gates:

### Stage Progression

```
DRAFT → REVIEW → APPROVED → PUBLISHED → ARCHIVED
         ↓
      REJECTED → (auto-reverts to DRAFT)
```

### Stage Descriptions

| Stage | Description | Actions Available |
|-------|-------------|-------------------|
| **DRAFT** | Initial creation, work in progress | Edit content, submit for review |
| **REVIEW** | Under review by assigned reviewer | Approve, reject, request changes |
| **APPROVED** | Review passed, ready to publish | Publish, edit, archive |
| **PUBLISHED** | Live in public docs/ directory | Unpublish, archive |
| **REJECTED** | Review failed, needs rework | Auto-reverted to DRAFT |
| **ARCHIVED** | No longer active | Restore to previous stage |

### Lifecycle Commands

**Submit for Review**:
```bash
# Document must be in DRAFT stage
apm document submit-review <document-id> \
  --reviewer="reviewer@example.com" \
  --priority=normal
```

**Approve Document**:
```bash
# Document must be in REVIEW stage
# Only assigned reviewer can approve
apm document approve <document-id> \
  --reviewer="reviewer@example.com" \
  --comment="Looks good, approved for publishing"
```

**Reject Document**:
```bash
# Document must be in REVIEW stage
# Auto-reverts to DRAFT for rework
apm document reject <document-id> \
  --reviewer="reviewer@example.com" \
  --reason="Needs more detail in section 3"
```

## Publishing Workflow

Publishing moves approved documents from private storage to public visibility.

### Prerequisites

Before publishing, document must be:
1. ✅ Lifecycle stage: APPROVED
2. ✅ Visibility: PUBLIC
3. ✅ Content exists and is valid
4. ✅ File path follows structure

### Publish Command

```bash
apm document publish <document-id>
```

**What Happens**:
1. Validates document is APPROVED and PUBLIC
2. Source file: `.agentpm/docs/guides/user_guide/example.md`
3. Destination: `docs/guides/user_guide/example.md`
4. Copies file preserving content
5. Updates lifecycle_stage = 'published'
6. Sets published_path and published_date
7. Creates audit log entry

### Auto-Publish

Some document types auto-publish when approved:

**Auto-Publish Types**:
- user_guide
- admin_guide
- api_doc
- specification

**Example**:
```bash
# 1. Approve document
apm document approve 42 --reviewer="admin"

# 2. System automatically publishes
# (if document type = user_guide and visibility = public)

# 3. Check status
apm document show 42
# Lifecycle: published
# Published Path: docs/guides/user_guide/getting-started.md
```

### Unpublish

Remove document from public docs/ while keeping source:

```bash
apm document unpublish <document-id> \
  --reason="Needs updates before re-publishing"
```

**What Happens**:
1. Removes file from `docs/` directory
2. Reverts lifecycle_stage to 'approved'
3. Keeps source in `.agentpm/docs/` (database source of truth)
4. Creates audit log entry

### List Unpublished Documents

Find approved documents ready to publish:

```bash
apm document list-unpublished
```

Shows all documents that are:
- Lifecycle: APPROVED
- Visibility: PUBLIC
- Not yet published

## Viewing Documents

### Show Document Details

```bash
apm document show <document-id>
```

**Output Includes**:
- Document metadata (title, description, type, category)
- Entity linkage (work item, task, idea)
- Visibility and audience
- Lifecycle stage and dates
- Review status and reviewer
- File paths (computed and published)
- Content preview
- Audit log entries

### List Documents

**All documents**:
```bash
apm document list
```

**Filter by entity**:
```bash
apm document list --entity-type=work-item --entity-id=158
```

**Filter by category**:
```bash
apm document list --category=guides
```

**Filter by type**:
```bash
apm document list --type=user_guide
```

## Updating Documents

### Update Metadata

```bash
apm document update <document-id> \
  --title="Updated Title" \
  --description="Updated description" \
  --visibility=public
```

**Updatable Fields**:
- title
- description
- visibility
- audience
- review_status
- reviewer_id

### Update Content

To update document content:

1. **Edit database record**:
```bash
# Read current content
apm document show <document-id>

# Update with new content
apm document update <document-id> \
  --content="$(cat <<'EOF'
# Updated Content
...
EOF
)"
```

2. **Sync to file**:
```bash
# System automatically syncs database → file
# Or use sync command
apm document sync <document-id>
```

## Document Audit Trail

Every document action is logged in the audit trail.

### View Audit Log

```bash
apm document show <document-id>
```

**Logged Actions**:
- submit_review
- approve
- reject
- publish
- unpublish
- archive
- update_metadata
- update_content

**Audit Entry Fields**:
- Timestamp
- Action type
- Actor (who performed it)
- From/to state transition
- Comment/reason
- Additional details (JSON)

## Best Practices

### 1. Always Use Database-First

❌ **Don't**:
```bash
# Direct file creation bypasses database
echo "# Guide" > docs/guide.md
```

✅ **Do**:
```bash
# Database-first creates file AND tracks metadata
apm document add \
  --entity-type=project \
  --entity-id=1 \
  --category=guides \
  --type=user_guide \
  --title="Guide" \
  --content="# Guide"
```

### 2. Link Documents to Entities

Every document should be linked to:
- Work item (features, improvements, fixes)
- Task (implementation work)
- Idea (proposals, concepts)
- Project (project-level docs)

**Why**: Enables context-aware queries and automatic organization.

### 3. Choose Appropriate Visibility

Consider your audience:

| Document Type | Visibility | Rationale |
|---------------|------------|-----------|
| User guides | Public | External users need access |
| API docs | Public | Developers need reference |
| Architecture ADRs | Context-aware | May be public for open source |
| Research notes | Private | Internal working documents |
| Security analysis | Private | Sensitive information |

### 4. Use Review Workflow

For important public documents:

```bash
# 1. Create as draft
apm document add --category=guides --type=user_guide ...

# 2. Submit for review
apm document submit-review <id> --reviewer="tech-lead@example.com"

# 3. Reviewer approves
apm document approve <id> --reviewer="tech-lead@example.com"

# 4. Auto-publish (or manual)
apm document publish <id>
```

### 5. Maintain Audit Trail

Use meaningful comments:

```bash
# Good: Specific reason
apm document reject 42 \
  --reason="Section 3.2 needs more code examples. See PR comments."

# Bad: Vague reason
apm document reject 42 --reason="Needs work"
```

### 6. Regular Sync Checks

Ensure database and files stay in sync:

```bash
# Check for mismatches
apm document sync-all --dry-run

# Fix any issues
apm document sync-all
```

## Troubleshooting

### Document Not Found

**Problem**: `Document X not found`

**Solution**:
1. Check document exists: `apm document list`
2. Verify ID is correct
3. Check entity linkage: `apm work-item show <entity-id>`

### Cannot Transition Lifecycle

**Problem**: `Document must be in DRAFT state to submit for review`

**Solution**:
1. Check current state: `apm document show <id>`
2. Valid transitions:
   - DRAFT → REVIEW (submit-review)
   - REVIEW → APPROVED (approve)
   - REVIEW → REJECTED → DRAFT (reject)
   - APPROVED → PUBLISHED (publish)

### Path Already Exists

**Problem**: `File path already exists`

**Solution**:
System auto-adds numeric suffix:
- `getting-started.md`
- `getting-started-2.md`
- `getting-started-3.md`

### Visibility Mismatch

**Problem**: Document is private but should be public

**Solution**:
```bash
# Update visibility
apm document update <id> --visibility=public

# Re-evaluate and move file if needed
apm document migrate-visibility <id>
```

## Advanced Features

### Batch Operations

**Publish all approved documents**:
```bash
# List unpublished
apm document list-unpublished

# Publish each
for id in $(apm document list-unpublished --format=ids); do
  apm document publish $id
done
```

### Visibility Migration

**Migrate documents after project settings change**:
```bash
# Update project settings
apm project update --collaboration-model=open_source

# Re-evaluate all document visibility
apm document migrate-visibility --all
```

### Content Sync

**Sync published documents**:
```bash
# Dry run (report only)
apm document sync-all --dry-run

# Actual sync
apm document sync-all
```

**What it checks**:
- Source file exists in `.agentpm/docs/`
- Destination matches `published_path`
- Content checksums match
- Orphaned files in `docs/` not in database

## Command Reference

### Document Creation

```bash
apm document add [OPTIONS]
```

**Required Options**:
- `--entity-type` (work-item|task|idea|project)
- `--entity-id` (integer)
- `--category` (planning|architecture|guides|reference|processes|governance|operations|communication)
- `--type` (see `apm document types`)
- `--title` (string)

**Optional Options**:
- `--file-path` (auto-generated if omitted)
- `--content` (markdown text)
- `--description` (string)
- `--format` (markdown|yaml|json|pdf|html|docx|text|other)
- `--created-by` (defaults to current user)

### Document Viewing

```bash
# Show details
apm document show <document-id>

# List all
apm document list

# List for entity
apm document list --entity-type=work-item --entity-id=158

# List by category
apm document list --category=guides

# List unpublished
apm document list-unpublished
```

### Document Lifecycle

```bash
# Submit for review
apm document submit-review <id> --reviewer=<email> [--priority=normal]

# Approve
apm document approve <id> --reviewer=<email> [--comment="..."] [--publish-now]

# Reject
apm document reject <id> --reviewer=<email> --reason="..."

# Publish
apm document publish <id>

# Unpublish
apm document unpublish <id> [--reason="..."]

# Archive
apm document archive <id>
```

### Document Updates

```bash
apm document update <id> [OPTIONS]
```

**Options**:
- `--title` (string)
- `--description` (string)
- `--visibility` (private|restricted|public)
- `--audience` (internal|team|contributors|users|public)
- `--content` (markdown text)

### Utilities

```bash
# Show available types
apm document types

# Sync all published documents
apm document sync-all [--dry-run]

# Migrate visibility
apm document migrate-visibility [--document-id=<id>] [--all]

# Delete document reference
apm document delete <id>
```

## Related Documentation

- **Architecture**: `docs/architecture/design_doc/publishing-workflow-specification.md`
- **Developer Guide**: `docs/guides/developer_guide/document-management-api.md`
- **Rule Documentation**: `docs/governance/quality_gates_spec/DOC-020_DATABASE_FIRST_DOCUMENTS.md`
- **Three-Tier Architecture**: `docs/architecture/design_doc/three-tier-architecture.md`

## Summary

AgentPM's document management system provides:

✅ **Database-First**: Single source of truth
✅ **Auto-Paths**: Intelligent file path generation
✅ **Visibility Control**: Private, team, public
✅ **Lifecycle Management**: Draft → Review → Approved → Published
✅ **Audit Trail**: Complete action history
✅ **Entity Linking**: Documents tied to work items/tasks
✅ **Publishing Workflow**: Controlled release process

**Golden Rule**: Always use `apm document add` for creating documents. Never create docs/ files directly.
