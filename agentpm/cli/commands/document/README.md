# Document Management CLI Commands

Comprehensive document management system for linking documents to work items, tasks, and ideas. Tracks document metadata, supports multiple formats, and provides intelligent auto-detection.

## Overview

The document management system provides a structured way to:

- **Link documents** to entities (work items, tasks, ideas, projects)
- **Track metadata** (type, format, title, description, file size)
- **Auto-detect** document types and formats from file paths
- **Manage lifecycle** (create, read, update, delete)
- **Support multiple formats** (Markdown, PDF, HTML, YAML, JSON, Office documents)
- **Enforce validation** (file existence, path security)

## Quick Start

```bash
# Add a document to a work item
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/api-specification.md" \
    --type=specification --title="API Specification"

# List all documents for an entity
apm document list --entity-type=task --entity-id=12

# Show document details
apm document show 25

# Update document metadata
apm document update 25 --title="Updated API Spec"

# Delete document reference
apm document delete 25
```

## Commands

### `apm document add`

Add a document reference to an entity (work item, task, idea, or project).

**Usage:**
```bash
apm document add --entity-type=<type> --entity-id=<id> \
    --file-path=<path> [OPTIONS]
```

**Required Options:**
- `--entity-type`: Type of entity (`work_item`, `task`, `idea`, `project`)
- `--entity-id`: ID of the entity to link document to
- `--file-path`: Relative path to document file from project root

**Optional Options:**
- `--type`: Document type (auto-detected from path if not specified)
- `--title`: Document title (auto-generated from filename if not specified)
- `--description`: Document description
- `--format`: Document format (auto-detected from extension if not specified)
- `--created-by`: Creator identifier (default: current user from environment)
- `--validate-file`: Validate file exists and is readable (default: enabled)

**Examples:**
```bash
# Add with auto-detection
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/architecture/system-overview.md"

# Add with explicit type and title
apm document add --entity-type=task --entity-id=12 \
    --file-path="docs/design/user-auth.md" \
    --type=design --title="User Authentication Design"

# Add with description and custom creator
apm document add --entity-type=idea --entity-id=8 \
    --file-path="docs/requirements/feature.md" \
    --type=requirements \
    --description="Initial feature requirements" \
    --created-by="product_manager"
```

**Auto-Detection Features:**
- **Document Type**: Inferred from path patterns (e.g., `architecture/` → `architecture`)
- **Document Format**: Inferred from file extension (e.g., `.md` → `markdown`)
- **Title**: Generated from filename (e.g., `api-spec.md` → "Api Spec")
- **File Validation**: Checks file exists and is readable by default

---

### `apm document list`

List document references with optional filtering.

**Usage:**
```bash
apm document list [OPTIONS]
```

**Filter Options:**
- `--entity-type`: Filter by entity type (`work_item`, `task`, `idea`, `project`)
- `--entity-id`: Filter by specific entity ID
- `--type`: Filter by document type (see Document Types section)
- `--format`: Filter by document format (see Document Formats section)
- `--created-by`: Filter by creator identifier
- `--limit`: Maximum number of documents to show (default: 50)

**Output Options:**
- `--format`: Output format (`table`, `json`) (default: `table`)

**Examples:**
```bash
# List all documents for a work item
apm document list --entity-type=work-item --entity-id=5

# List all design documents
apm document list --type=design

# List all markdown documents
apm document list --format=markdown

# List documents created by specific user
apm document list --created-by=ai_agent

# List with JSON output for scripting
apm document list --entity-type=task --entity-id=12 --format=json

# List with custom limit
apm document list --limit=100
```

**Output:**
- Table view shows: ID, Entity, File Path, Type, Format, Size, Creator, Date
- JSON view provides complete metadata for programmatic use

---

### `apm document show`

Show detailed information about a document reference.

**Usage:**
```bash
apm document show <document_id> [OPTIONS]
```

**Options:**
- `--include-content`: Include document content preview (first 500 characters)
- `--format`: Output format (`rich`, `json`) (default: `rich`)

**Examples:**
```bash
# Show document details
apm document show 25

# Show with content preview
apm document show 25 --include-content

# Show in JSON format
apm document show 25 --format=json
```

**Information Shown:**
- Document metadata (ID, title, description)
- File details (path, size, format, content hash)
- Entity linkage (type and ID)
- Creation information (creator, timestamps)
- File existence verification
- Content preview (if requested)

---

### `apm document update`

Update document reference metadata.

**Usage:**
```bash
apm document update <document_id> [OPTIONS]
```

**Update Options:**
- `--file-path`: Update file path
- `--type`: Update document type
- `--title`: Update document title
- `--description`: Update document description
- `--format`: Update document format
- `--validate-file`: Validate updated file exists (default: enabled)

**Examples:**
```bash
# Update document title
apm document update 25 --title="Updated API Specification"

# Update type and description
apm document update 25 \
    --type=specification \
    --description="Latest version of API spec"

# Update file path
apm document update 25 \
    --file-path="docs/api/v2/specification.md"

# Update multiple fields
apm document update 25 \
    --title="New Title" \
    --type=design \
    --description="Updated design document"
```

**Behavior:**
- Only specified fields are updated
- File size and content hash recalculated if file path changes
- File validation performed by default
- Shows before/after comparison of changes

---

### `apm document delete`

Delete a document reference from the database.

**Usage:**
```bash
apm document delete <document_id> [OPTIONS]
```

**Options:**
- `--force`: Delete without confirmation prompt
- `--delete-file`: Also delete the actual file from filesystem

**Examples:**
```bash
# Delete document reference (keep file)
apm document delete 25

# Delete document reference and file
apm document delete 25 --delete-file

# Delete without confirmation
apm document delete 25 --force
```

**Warnings:**
- Action cannot be undone
- By default, only removes database record (file preserved)
- Use `--delete-file` with caution (permanently removes file)
- Shows confirmation prompt unless `--force` is used

---

## Document Types Taxonomy

Documents are organized into categories based on their purpose in the development lifecycle:

### Planning Documents
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `idea` | Initial concept or proposal | `ideas/`, `proposals/` |
| `requirements` | Requirements specifications | `requirements/`, `reqs/`, `specs/` |
| `user_story` | User stories and narratives | `user-story/`, `stories/` |
| `use_case` | Use case descriptions | `use-case/`, `scenarios/` |
| `business_pillars_analysis` | Business analysis documents | `business/`, `analysis/` |
| `market_research_report` | Market research findings | `market/`, `research/` |
| `competitive_analysis` | Competitive landscape analysis | `competitive/`, `competitors/` |
| `stakeholder_analysis` | Stakeholder mapping and analysis | `stakeholders/` |

### Architecture & Design
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `architecture` | System architecture documents | `architecture/`, `arch/`, `system-design/` |
| `design` | Design specifications and diagrams | `design/`, `designs/`, `mockup/` |
| `technical_specification` | Technical specifications | `technical/`, `tech-spec/` |
| `adr` | Architecture Decision Records | `adr/`, `decision/`, `decisions/` |

### Implementation
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `specification` | General specifications | Auto-detected default |
| `api_doc` | API documentation | `api/`, `api-docs/`, `swagger/`, `openapi/` |
| `implementation_plan` | Implementation planning docs | `implementation/`, `plan/` |
| `refactoring_guide` | Refactoring guidelines | `refactoring/`, `refactor/` |

### Operations & Deployment
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `deployment_guide` | Deployment and operations guides | `deployment/`, `deploy/`, `ops/` |
| `migration_guide` | Migration and upgrade guides | `migration/`, `upgrade/` |
| `runbook` | Operational runbooks | `runbook/`, `playbook/` |
| `admin_guide` | Administrator documentation | `admin/`, `administration/` |

### Testing & Quality
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `test_plan` | Testing plans and strategies | `test-plan/`, `testing/`, `qa/` |
| `quality_gates_specification` | Quality gate definitions | `quality/`, `gates/` |

### User-Facing Documentation
| Type | Description | Typical Path Patterns |
|------|-------------|----------------------|
| `user_guide` | User documentation and guides | `user-guide/`, `manual/`, `tutorial/` |
| `troubleshooting` | Troubleshooting and support docs | `troubleshooting/`, `debug/`, `support/` |
| `changelog` | Release notes and changelogs | `changelog/`, `release-notes/` |

### Other
| Type | Description | Use Case |
|------|-------------|----------|
| `other` | Miscellaneous documents | Documents not fitting other categories |

---

## Document Formats

Supported document formats with auto-detection from file extensions:

| Format | Description | Extensions | Use Case |
|--------|-------------|------------|----------|
| `markdown` | Markdown files | `.md` | Documentation, specs, guides |
| `yaml` | YAML configuration files | `.yaml`, `.yml` | Configuration, structured data |
| `json` | JSON data files | `.json` | API specs, data, configuration |
| `pdf` | PDF documents | `.pdf` | Reports, presentations, deliverables |
| `html` | HTML files | `.html`, `.htm` | Web documentation, reports |
| `text` | Plain text files | `.txt` | Notes, logs, simple docs |
| `docx` | Microsoft Word documents | `.docx` | Formal documentation, reports |
| `xlsx` | Microsoft Excel spreadsheets | `.xlsx` | Data, requirements matrices |
| `pptx` | Microsoft PowerPoint | `.pptx` | Presentations, architecture diagrams |
| `other` | Other formats | Any other extension | Custom or specialized formats |

---

## Auto-Detection Rules

The system automatically detects document type and format to reduce manual entry:

### Document Type Detection

Path pattern matching (case-insensitive):

```
Path contains "architecture/" → type: architecture
Path contains "design/" → type: design
Path contains "api/" → type: api_docs
Path contains "user-guide" → type: user_guide
Path contains "test-plan" → type: test_plan
Path contains "deployment" → type: deployment_guide
Path contains "troubleshooting" → type: troubleshooting
Path contains "changelog" → type: changelog
Path contains "requirements" → type: requirements
Path contains "user-story" → type: user_story
Path contains "adr/" → type: adr
Default → type: specification
```

### Format Detection

Extension-based mapping:

```
.md → markdown
.html, .htm → html
.pdf → pdf
.txt → text
.json → json
.yaml, .yml → yaml
.docx → docx
.xlsx → xlsx
.pptx → pptx
Other → other
```

### Title Generation

Automatic title from filename:

```
Input: "api-specification.md"
Steps:
1. Remove extension: "api-specification"
2. Replace separators: "api specification"
3. Capitalize words: "Api Specification"
Output: "Api Specification"
```

---

## Integration Patterns

### Work Items Integration

Link documents to work items for comprehensive context:

```bash
# Add architecture document to feature work item
apm document add --entity-type=work-item --entity-id=42 \
    --file-path="docs/architecture/payment-system.md" \
    --type=architecture

# View all documents for work item
apm document list --entity-type=work-item --entity-id=42

# Show work item with documents
apm work-item show 42
```

### Tasks Integration

Attach task-specific documentation:

```bash
# Add design doc to design task
apm document add --entity-type=task --entity-id=123 \
    --file-path="docs/design/user-auth-flow.md" \
    --type=design

# Add implementation plan to implementation task
apm document add --entity-type=task --entity-id=124 \
    --file-path="docs/implementation/auth-implementation.md" \
    --type=implementation_plan

# View task documents
apm document list --entity-type=task --entity-id=123
```

### Ideas Integration

Capture idea documentation before work item creation:

```bash
# Add requirements to idea
apm document add --entity-type=idea --entity-id=8 \
    --file-path="docs/ideas/mobile-app-requirements.md" \
    --type=requirements

# Add market research to idea
apm document add --entity-type=idea --entity-id=8 \
    --file-path="docs/research/mobile-market-analysis.pdf" \
    --type=market_research_report

# When idea becomes work item, documents transfer automatically
apm idea create-work-item 8
```

### Quality Gates Integration

Document quality gates for validation:

```bash
# Add quality gates specification to work item
apm document add --entity-type=work-item --entity-id=42 \
    --file-path="docs/quality/payment-system-gates.md" \
    --type=quality_gates_specification

# Reference during validation
apm work-item validate 42
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: File Not Found Error

**Symptom:**
```
❌ File not found: docs/api-spec.md
   Expected at: /path/to/project/docs/api-spec.md
```

**Causes:**
1. File path is incorrect
2. File doesn't exist yet
3. Path is absolute instead of relative

**Solutions:**
```bash
# Verify file exists
ls -la docs/api-spec.md

# Check current directory
pwd

# Use relative path from project root
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/api-spec.md"  # Relative, not absolute

# Create file first if it doesn't exist
mkdir -p docs && touch docs/api-spec.md
```

---

#### Issue: Path Security Validation

**Symptom:**
```
❌ Path is not a file: docs/../../../etc/passwd
```

**Cause:**
Security validation prevents directory traversal attacks

**Solution:**
```bash
# Use proper relative paths (no ..)
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/api-spec.md"  # ✅ Good

# Avoid directory traversal
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/../../other-project/file.md"  # ❌ Bad
```

---

#### Issue: Wrong Document Type Auto-Detection

**Symptom:**
Document auto-detected as wrong type (e.g., `specification` instead of `design`)

**Cause:**
File path doesn't match expected patterns

**Solutions:**
```bash
# Option 1: Specify type explicitly
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/my-design.md" \
    --type=design  # Explicit override

# Option 2: Reorganize files to match patterns
mv docs/my-design.md docs/design/my-design.md  # Path now matches pattern

# Option 3: Accept auto-detection and update later
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/my-design.md"
apm document update 25 --type=design
```

---

#### Issue: Entity Not Found

**Symptom:**
```
❌ Work item not found: ID 999
```

**Cause:**
Referenced entity doesn't exist in database

**Solutions:**
```bash
# Verify entity exists
apm work-item show 5  # Check work item exists
apm task show 12      # Check task exists
apm idea show 8       # Check idea exists

# List entities to find correct ID
apm work-item list
apm task list
apm idea list

# Create entity first if needed
apm work-item add --title="New Feature" --type=feature
```

---

#### Issue: File Validation Disabled But Needed

**Symptom:**
Document added but file doesn't exist, causing issues later

**Cause:**
Used `--no-validate-file` when validation was needed

**Solution:**
```bash
# Always use validation (default behavior)
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/api-spec.md"
    # File validation enabled by default

# Only disable validation for legitimate reasons
# (e.g., file will be created by automated process)
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/generated-report.pdf" \
    --no-validate-file  # Only if you know what you're doing
```

---

## Best Practices

### 1. Use Relative Paths

Always use paths relative to project root:

```bash
# ✅ Good - Relative path
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/api-spec.md"

# ❌ Bad - Absolute path
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="/Users/username/project/docs/api-spec.md"
```

### 2. Organize Files by Type

Structure directories to match auto-detection patterns:

```
docs/
├── architecture/     # Auto-detected as architecture
├── design/          # Auto-detected as design
├── api/            # Auto-detected as api_docs
├── requirements/   # Auto-detected as requirements
├── testing/        # Auto-detected as test_plan
└── user-guides/    # Auto-detected as user_guide
```

### 3. Leverage Auto-Detection

Let the system detect type and format when possible:

```bash
# ✅ Good - Let system auto-detect
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/architecture/system-design.md"
    # Auto-detects: type=architecture, format=markdown, title="System Design"

# ❌ Unnecessary - Manual specification when auto-detect works
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/architecture/system-design.md" \
    --type=architecture --format=markdown --title="System Design"
```

### 4. Add Descriptions for Complex Documents

Provide context through descriptions:

```bash
apm document add --entity-type=work-item --entity-id=5 \
    --file-path="docs/architecture/payment-system.md" \
    --description="Payment system architecture including fraud detection, \
payment processing, and reconciliation components"
```

### 5. Link Documents Early

Add documents when creating entities:

```bash
# Create work item
apm work-item add --title="Payment System" --type=feature

# Immediately add documentation
apm document add --entity-type=work-item --entity-id=42 \
    --file-path="docs/requirements/payment-requirements.md"
apm document add --entity-type=work-item --entity-id=42 \
    --file-path="docs/architecture/payment-architecture.md"
```

### 6. Use Consistent Naming

Follow naming conventions for documents:

```bash
# ✅ Good - Descriptive, kebab-case
docs/architecture/payment-system-design.md
docs/api/payment-api-specification.md
docs/testing/payment-integration-tests.md

# ❌ Avoid - Vague, inconsistent
docs/design.md
docs/api_spec_v2_FINAL.md
docs/TestDoc123.md
```

### 7. Keep Documents Updated

Update document metadata when files change:

```bash
# Update title and description when content changes
apm document update 25 \
    --title="Payment API Specification v2.0" \
    --description="Updated with webhook endpoints and async processing"
```

### 8. Clean Up Deleted Documents

Remove document references when files are deleted:

```bash
# Delete document reference when file no longer exists
apm document delete 25

# Or delete both reference and file
apm document delete 25 --delete-file
```

---

## See Also

- **Work Items**: `apm work-item show <id>` - View work item with documents
- **Tasks**: `apm task show <id>` - View task with documents
- **Ideas**: `apm idea show <id>` - View idea with documents
- **Context System**: `apm context show` - View assembled context including documents

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Status**: Production Ready
