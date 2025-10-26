# DOC-020: Database-First Document Creation with Visibility

**Status**: ACTIVE
**Enforcement**: BLOCK (hard failure)
**Category**: Documentation Principles
**Priority**: CRITICAL
**Last Updated**: 2025-10-26
**Version**: 2.0.0

## Rule

**All document creation MUST use `apm document add` command. Direct file creation is PROHIBITED.**

All agents MUST create documents through the database-first document management system. Document visibility is automatically determined by document type and can be explicitly set during creation.

## Rationale

Database-first architecture ensures:
- ✅ All documents tracked in database
- ✅ Metadata properly maintained
- ✅ Consistent file path patterns
- ✅ Document lifecycle managed
- ✅ Entity relationships maintained

Without this rule, documents become orphaned files with:
- ❌ No database record
- ❌ No entity linkage (work item, task, project)
- ❌ No metadata (category, type, title, description)
- ❌ No lifecycle tracking (created, updated, archived)
- ❌ Inconsistent file naming and location

## Visibility System

Documents are automatically categorized by visibility scope, which determines their location and intended audience:

### Visibility Scopes

| Scope | Location | Audience | Purpose | Auto-Assigned When |
|-------|----------|----------|---------|-------------------|
| **private** | `.agentpm/docs/` | Internal system only | Agent workflows, internal specs, system metadata | Document type is `agent_workflow`, `internal_spec`, or `metadata` |
| **team** | `docs/` | Development team | Collaboration docs, work-in-progress, team guides | Default for most document types |
| **public** | `docs/` | End users | Published guides, API docs, user documentation | After calling `apm document publish <id>` |

### Visibility Rules

1. **Internal document types** (e.g., `agent_workflow`, `internal_spec`) are AUTOMATICALLY set to `private`
2. **Published documents** MUST have `visibility=public` and `published_at` timestamp
3. **Team documents** default to `team` visibility
4. **File paths** MUST match visibility scope:
   - `private` → `.agentpm/docs/{category}/{type}/{filename}`
   - `team`/`public` → `docs/{category}/{type}/{filename}`

### Path Auto-Generation

When using `apm document add`, the file path is automatically generated based on:
- Document category (planning, architecture, guides, reference, etc.)
- Document type (requirements, design_doc, user_guide, api_doc, etc.)
- Document title (slugified to create filename)
- Visibility scope (determines docs/ vs .agentpm/docs/)

**You do NOT need to specify `--file-path`** - it will be auto-generated. If you do provide one, it will be validated and corrected if needed.

## Correct Workflow

### 1. Prepare Content
Write your document content in a variable or prepare it.

### 2. Use apm document add (Path Auto-Generated)
```bash
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --category=planning \
  --type=requirements \
  --title="Phase 1 Completion Report" \
  --description="Comprehensive report of Phase 1 deliverables" \
  --content="$(cat <<'EOF'
# Phase 1 Completion Report

## Overview
Phase 1 successfully implemented...

## Deliverables
- InitOrchestrator service
- AgentGenerator service
...
EOF
)"

# Path will be AUTO-GENERATED as:
# docs/planning/requirements/phase-1-completion-report.md
```

### 2b. Optional: Specify Custom Path
```bash
# If you need a specific path, you can provide it
# (will be validated and corrected if needed)
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --file-path="docs/features/phase-1-completion.md" \
  --category=planning \
  --type=requirements \
  --title="Phase 1 Completion Report" \
  --description="Comprehensive report of Phase 1 deliverables" \
  --content="..."
```

### 3. Verify Creation
```bash
apm document list --entity-type=work-item --entity-id=158
ls docs/features/phase-1-completion.md
```

## Required Fields

Core required fields (path is auto-generated):

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `--entity-type` | ✅ | What this documents | `work-item`, `task`, `project` |
| `--entity-id` | ✅ | Which entity ID | `158` |
| `--category` | ✅ | Document category | `planning`, `architecture`, `guides` |
| `--type` | ✅ | Document type | `requirements`, `design_doc`, `user_guide` |
| `--title` | ✅ | Clear title | `Phase 1 Completion Report` |
| `--content` | ✅ | Actual content | `# Phase 1...` |
| `--description` | Recommended | Brief summary | `Comprehensive report...` |
| `--file-path` | Optional | Custom path (auto-generated if not provided) | `docs/features/spec.md` |

**Note**: The `--file-path` is now OPTIONAL. If you don't provide it, the system will automatically generate an appropriate path based on category, type, and title.

## File Path Patterns

Standard directory structure (auto-generated based on visibility and type):

```
docs/                          # Team and public visibility
  ├── features/                # Legacy location (being migrated)
  ├── planning/                # Planning documents (category)
  │   ├── requirements/       # Requirements docs (type: requirements)
  │   ├── user_story/         # User stories (type: user_story)
  │   └── use_case/           # Use cases (type: use_case)
  ├── architecture/            # Architecture docs (category)
  │   ├── design_doc/         # Design docs (type: design_doc)
  │   ├── adr/                # Architecture Decision Records (type: adr)
  │   └── technical_spec/     # Technical specifications (type: technical_spec)
  ├── guides/                  # User/developer guides (category)
  │   ├── user_guide/         # User guides (type: user_guide)
  │   ├── developer_guide/    # Developer guides (type: developer_guide)
  │   └── admin_guide/        # Admin guides (type: admin_guide)
  ├── reference/               # API docs, references (category)
  │   └── api_doc/            # API documentation (type: api_doc)
  ├── processes/               # Process documentation (category)
  │   ├── runbook/            # Runbooks (type: runbook)
  │   └── deployment_guide/   # Deployment guides (type: deployment_guide)
  └── operations/              # Operations docs (category)
      ├── monitoring_guide/   # Monitoring guides (type: monitoring_guide)
      └── incident_report/    # Incident reports (type: incident_report)

.agentpm/docs/                 # Private visibility (internal only)
  ├── internal/                # Internal documentation (category)
  │   ├── agent_workflow/     # Agent SOPs (type: agent_workflow)
  │   ├── internal_spec/      # Internal specs (type: internal_spec)
  │   └── metadata/           # System metadata (type: metadata)
  └── governance/              # Internal governance (category)
      └── quality_gates_spec/ # Quality gates (type: quality_gates_spec)
```

## Violations

❌ **PROHIBITED**:

```python
# WRONG: Direct file creation with Write tool
Write(
    file_path="docs/features/my-feature.md",
    content="# My Feature"
)

# WRONG: Bash file creation with echo
Bash(command="echo '# My Feature' > docs/features/my-feature.md")

# WRONG: Bash file creation with cat
Bash(command="cat > docs/features/my-feature.md << 'EOF'\n# My Feature\nEOF")

# WRONG: Creating file without database record
# (Any method that bypasses apm document add)
```

## Detection Patterns

The validator scans for these violation patterns:

1. **Write tool with docs/ path**:
   ```python
   Write(file_path="docs/...")  # VIOLATION
   ```

2. **Bash with echo redirection to docs/**:
   ```bash
   echo "..." > docs/...  # VIOLATION
   ```

3. **Bash with cat redirection to docs/**:
   ```bash
   cat > docs/... << EOF  # VIOLATION
   ```

4. **Files in docs/ without database records**:
   - Automated scan checks all `.md`, `.txt`, `.rst` files
   - Compares against `document_references` table
   - Reports orphaned files

## Remediation

If violation detected:

### Step 1: Delete the Directly Created File
```bash
rm docs/path/to/file.md
```

### Step 2: Recreate Using Proper Command
```bash
# Prepare the content
CONTENT=$(cat <<'EOF'
# Your Document Title

Your content here...
EOF
)

# Create via database
apm document add \
  --entity-type=work-item \
  --entity-id=<ID> \
  --file-path="docs/path/to/file.md" \
  --category=<category> \
  --type=<type> \
  --title="<title>" \
  --description="<description>" \
  --content="$CONTENT"
```

### Step 3: Verify Database Record
```bash
apm document list --entity-type=work-item --entity-id=<ID>
```

## Exceptions

**NONE**. This rule has NO exceptions.

All documentation must go through database, including:
- Feature specifications
- Architecture documents
- Design documents
- User guides
- Developer guides
- API documentation
- ADRs (Architecture Decision Records)
- Runbooks
- Incident reports
- Meeting notes
- Planning documents

**Even README.md at project root must use database if it documents a work item.**

## Validation

The rule is enforced through:

1. **Static Analysis**:
   - Scans agent code/prompts for Write/Bash tool usage
   - Detects file creation patterns in docs/

2. **Runtime Validation**:
   - Checks all files in docs/ have database records
   - Reports orphaned files (files without database entries)

3. **Pre-Commit Hooks** (future):
   - Validate all docs/ files before commit
   - Block commits with orphaned files

## Examples

### ✅ Correct: Feature Specification

```bash
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --file-path="docs/features/database-first-documents.md" \
  --category=planning \
  --type=requirements \
  --title="Database-First Document Management" \
  --description="Specification for DOC-020 rule implementation" \
  --content="$(cat <<'EOF'
# Database-First Document Management

## Overview
This feature implements BLOCK-level enforcement...

## Requirements
1. All documents must use apm document add
2. Direct file creation is prohibited
3. Validator detects violations

## Acceptance Criteria
- [ ] DOC-020 rule created in database
- [ ] Validator implemented
- [ ] CLAUDE.md updated
- [ ] Tests pass
EOF
)"
```

### ✅ Correct: Architecture Decision Record

```bash
apm document add \
  --entity-type=project \
  --entity-id=1 \
  --file-path="docs/architecture/adrs/001-database-first-documents.md" \
  --category=architecture \
  --type=adr \
  --title="ADR-001: Database-First Document Management" \
  --description="Architecture decision to enforce database-first document creation" \
  --content="$(cat <<'EOF'
# ADR-001: Database-First Document Management

## Status
Accepted

## Context
Documents were being created directly as files without database records...

## Decision
All document creation must go through database via apm document add command...

## Consequences
- Positive: Complete document tracking
- Positive: Metadata consistency
- Negative: Slightly more verbose workflow
EOF
)"
```

### ✅ Correct: User Guide

```bash
apm document add \
  --entity-type=work-item \
  --entity-id=158 \
  --file-path="docs/guides/user/document-management.md" \
  --category=guides \
  --type=user_guide \
  --title="Document Management User Guide" \
  --description="How to create and manage documents in APM" \
  --content="$(cat <<'EOF'
# Document Management User Guide

## Creating Documents

All documents must be created using the `apm document add` command...

## Step-by-Step

1. Prepare your content
2. Use apm document add command
3. Verify creation

## Examples
...
EOF
)"
```

### ❌ Incorrect: Direct File Creation

```python
# WRONG - Violation of DOC-020
Write(
    file_path="docs/features/my-feature.md",
    content="# My Feature\n\nThis is my feature..."
)

# RESULT: File created without database record
# REMEDIATION: Delete file, recreate via apm document add
```

### ❌ Incorrect: Bash File Creation

```bash
# WRONG - Violation of DOC-020
echo "# My Feature" > docs/features/my-feature.md

# RESULT: File created without database record
# REMEDIATION: Delete file, recreate via apm document add
```

## Publishing Workflow

Documents can progress through visibility levels:

```
private → team → public (published)
```

### Publishing a Document

```bash
# 1. Create document (defaults to team visibility)
apm document add \
  --entity-type=work-item \
  --entity-id=164 \
  --category=guides \
  --type=user_guide \
  --title="Document Management Guide" \
  --content="..."

# 2. Review and refine
apm document update <id> --content="<updated content>"

# 3. Publish to users (when ready)
apm document publish <id>
```

Publishing a document:
- Sets `visibility = 'public'`
- Sets `published_at = <timestamp>`
- Triggers validation checks
- May require approval workflow (depending on configuration)

### Document Lifecycle States

| State | Description | Visibility | Typical Audience |
|-------|-------------|------------|------------------|
| `draft` | Work in progress | private/team | Author only |
| `review` | Under review | team | Reviewers + author |
| `approved` | Review passed | team | Team members |
| `published` | Public release | public | End users |
| `archived` | Deprecated | team | Historical reference |

## See Also

- `apm document add --help` - Full command documentation
- `apm document types` - Available categories and types
- `apm document publish --help` - Publishing command documentation
- `docs/architecture/three-tier-architecture.md` - Database-first architecture
- `CLAUDE.md` - Master orchestrator instructions (includes DOC-020 enforcement)
- `agentpm/core/database/schema.md` - Database schema documentation

## Enforcement History

- **2025-10-25**: DOC-020 created as BLOCK-level rule
- **2025-10-25**: Validator implementation added
- **2025-10-25**: CLAUDE.md updated with hard rule
- **2025-10-25**: Documentation created (v1.0.0)
- **2025-10-26**: Added visibility system documentation (v2.0.0)
- **2025-10-26**: Updated for auto-generated file paths
- **2025-10-26**: Added publishing workflow section
- **2025-10-26**: Enhanced directory structure with private docs support

## Related Rules

- **DP-001**: Database-First Architecture (general principle)
- **DP-002**: Three-Tier Pattern (models, adapters, methods)
- **WF-004**: All work documented in database
- **CI-004**: Documentation coverage requirements

## Related Work Items

- **WI-164**: Auto-Generate Document File Paths (visibility system implementation)
- **WI-133**: Hybrid Storage System (database + file storage)

---

**Version**: 2.0.0
**Last Updated**: 2025-10-26
**Rule ID**: DOC-020
**Enforcement**: BLOCK (hard failure)
**Status**: ACTIVE
