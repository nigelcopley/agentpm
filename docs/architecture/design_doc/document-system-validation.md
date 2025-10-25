# Document Path Validation System Architecture

**Component**: Universal Documentation System - Path Validation Layer
**Work Item**: WI-113 (Document Path Validation Enforcement)
**Version**: 1.0.0
**Last Updated**: 2025-10-20

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Validation Layers](#validation-layers)
4. [CHECK Constraint Design](#check-constraint-design)
5. [Migration System](#migration-system)
6. [Exception Handling](#exception-handling)
7. [Testing Strategy](#testing-strategy)

---

## Overview

### Purpose

The Document Path Validation System enforces a standardized path structure across all project documentation:

```
docs/{category}/{document_type}/{filename}
```

This ensures:
- **Predictable discovery**: Developers know where to find documentation
- **Automated tooling**: Scripts can reliably navigate documentation
- **Clean organization**: Related documents are logically grouped
- **AI agent integration**: Agents can systematically process documentation
- **Migration safety**: Path changes are validated and reversible

### Design Goals

1. **Multi-Layer Defense**: Validation at Pydantic, CLI, and Database levels
2. **User-Friendly Guidance**: Interactive path correction with suggestions
3. **Safe Migration**: Atomic transactions with automatic rollback
4. **Flexible Exceptions**: Support for legacy files and special cases
5. **Zero Breaking Changes**: Existing documents can be migrated gradually

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  (apm document add, apm document migrate-to-structure)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              CLI Validation Layer                           │
│  • Path structure guidance                                  │
│  • Interactive correction suggestions                       │
│  • Category inference from document type                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           Pydantic Model Validation                         │
│  • Field-level validators (@field_validator)                │
│  • Path structure validation                                │
│  • Category-path consistency checks                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           Database CHECK Constraint                         │
│  • Final enforcement layer (cannot be bypassed)             │
│  • SQLite CHECK constraint on file_path column             │
│  • Exception patterns for legacy files                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Document Creation Flow:**

```
1. User provides file_path
   ↓
2. CLI validates and guides (if non-compliant)
   ↓
3. Pydantic model validates structure
   ↓
4. Database CHECK constraint enforces compliance
   ↓
5. Document reference created (or error raised)
```

**Migration Flow:**

```
1. Query database for non-compliant paths
   ↓
2. Infer categories from document_type
   ↓
3. Construct target paths (docs/{category}/{type}/{filename})
   ↓
4. Create backups of physical files
   ↓
5. Move files and calculate checksums
   ↓
6. Update database atomically (with transaction)
   ↓
7. On error: Rollback database + restore backups
```

---

## Validation Layers

### Layer 1: CLI Validation (User-Friendly)

**Location**: `agentpm/cli/commands/document/add.py`

**Function**: `_validate_and_guide_path()`

**Behavior**:
- Detects non-compliant paths
- Infers category from document_type
- Generates suggested compliant path
- Offers interactive correction
- Allows override with confirmation

**Example Interaction**:

```
$ apm document add --entity-type=work_item --entity-id=113 \
    --file-path="design/doc-system.md" --type=design

⚠️  Path does not follow standard structure

💡 Recommended path structure:
   docs/architecture/design/doc-system.md

📁 Standard structure:
   docs/{category}/{document_type}/{filename}

📂 Valid categories:
   • architecture  - System design, technical architecture
   • planning      - Requirements, user stories, plans
   • guides        - User guides, tutorials, how-tos
   [...]

Use recommended path? [Y/n]:
```

**Key Features**:
- Non-blocking (user can proceed with non-standard path)
- Educational (shows category descriptions)
- Convenient (auto-correction with one keystroke)

**Implementation**:

```python
def _validate_and_guide_path(file_path: str, document_type: str, console: Console) -> str:
    """Validate path and provide guidance if non-compliant."""
    if not file_path.startswith('docs/'):
        # Infer category from document_type
        category = CATEGORY_MAPPING.get(document_type, 'communication')

        # Generate suggested path
        filename = Path(file_path).name
        suggested = f"docs/{category}/{document_type}/{filename}"

        # Display guidance and offer correction
        console.print("💡 Recommended path structure:")
        console.print(f"   {suggested}")

        if click.confirm("Use recommended path?", default=True):
            return suggested

    return file_path
```

---

### Layer 2: Pydantic Model Validation (Type-Safe)

**Location**: `agentpm/core/database/models/document_reference.py`

**Validator**: `@field_validator('file_path')`

**Validation Rules**:

1. **Primary Rule**: Path must start with `docs/`
2. **Exception Patterns**: Allow legacy files (README.md, etc.)
3. **Structure Check**: Minimum 4 parts (docs/category/type/filename)
4. **Category Consistency**: Path category must match field category (if set)

**Implementation**:

```python
@field_validator('file_path')
@classmethod
def validate_path_structure(cls, v: str, info) -> str:
    """Validate path follows docs/ structure with exceptions."""
    is_valid = (
        # Primary rule: Must start with 'docs/'
        v.startswith('docs/')
        # Exception 1: Project root markdown files
        or v in ('CHANGELOG.md', 'README.md', 'LICENSE.md')
        # Exception 2: Project root artifacts
        or (v.endswith('.md') and '/' not in v)
        # Exception 3: Module documentation
        or v.startswith('agentpm/') and v.endswith('/README.md')
        # Exception 4: Test reports and test code
        or v.startswith('testing/')
        or v.startswith('tests/')
    )

    if not is_valid:
        raise ValueError(
            f"Document path must start with 'docs/' or be an allowed exception. "
            f"Got: {v}"
        )

    # For docs/ paths, validate structure
    if v.startswith('docs/'):
        parts = v.split('/')
        if len(parts) < 4:
            raise ValueError(
                f"Path must follow pattern: docs/{{category}}/{{document_type}}/{{filename}}. "
                f"Got: {v}"
            )

        # Validate category matches if available
        if 'category' in info.data and info.data['category'] is not None:
            if parts[1] != info.data['category']:
                raise ValueError(
                    f"Path category '{parts[1]}' doesn't match field category '{info.data['category']}'"
                )

    return v
```

**Key Design Decisions**:
- **Permissive on read**: Allows existing non-compliant paths (migration support)
- **Strict on write**: New documents must comply
- **Clear error messages**: Includes expected pattern in ValueError
- **Category validation**: Optional (None allowed for flexibility)

---

### Layer 3: Database CHECK Constraint (Ultimate Enforcement)

**Location**: `agentpm/core/database/migrations/files/migration_0032_enforce_docs_path.py`

**Purpose**: Final enforcement layer that cannot be bypassed (even by direct SQL)

**Constraint Logic**:

```sql
CHECK (
    -- Primary rule: Must start with 'docs/'
    file_path LIKE 'docs/%'

    -- Exception 1: Project root markdown files
    OR file_path IN ('CHANGELOG.md', 'README.md', 'LICENSE.md')

    -- Exception 2: Project root artifacts (*.md files without /)
    OR (file_path LIKE '%.md' AND file_path NOT LIKE '%/%')

    -- Exception 3: Module documentation
    OR file_path GLOB 'agentpm/*/README.md'

    -- Exception 4: Test reports and test code
    OR file_path LIKE 'testing/%'
    OR file_path LIKE 'tests/%'
)
```

**Why CHECK Constraint?**

1. **Cannot be bypassed**: Even direct SQL inserts are validated
2. **Performance**: Validated at database level (no app logic required)
3. **Data integrity**: Guarantees no non-compliant paths in database
4. **Migration safety**: Prevents accidental creation of legacy paths post-migration

**SQLite Implementation Note**:

SQLite doesn't support `ADD CONSTRAINT` for CHECK constraints, so migration recreates the table:

```python
def upgrade(conn: sqlite3.Connection) -> None:
    """Add CHECK constraint to enforce docs/ path structure"""
    # Step 1: Create new table with CHECK constraint
    conn.execute("CREATE TABLE document_references_new (...)")

    # Step 2: Copy all data from old table
    conn.execute("INSERT INTO document_references_new SELECT * FROM document_references")

    # Step 3: Drop old table
    conn.execute("DROP TABLE document_references")

    # Step 4: Rename new table
    conn.execute("ALTER TABLE document_references_new RENAME TO document_references")

    # Step 5: Recreate indexes
    conn.execute("CREATE INDEX idx_doc_category ON document_references(category)")
    # ... additional indexes
```

---

## CHECK Constraint Design

### Exception Patterns Rationale

| Pattern | Reason | Example |
|---------|--------|---------|
| `README.md` | Repository root documentation | Project overview |
| `CHANGELOG.md` | Version history at root | Release notes |
| `*.md` (root) | Legacy artifacts | `DEPLOYMENT-GUIDE.md` |
| `agentpm/*/README.md` | Module documentation | `agentpm/core/README.md` |
| `testing/*` | Test reports | `testing/coverage-report.html` |
| `tests/*` | Test code | `tests/conftest.py` |

### Path Pattern Examples

**Valid Paths**:

```
✓ docs/architecture/design/database-schema.md
✓ docs/planning/requirements/auth-functional.md
✓ docs/guides/user_guide/getting-started.md
✓ README.md
✓ CHANGELOG.md
✓ agentpm/core/README.md
✓ tests/conftest.py
```

**Invalid Paths**:

```
✗ design/doc-system.md                    (missing docs/ prefix)
✗ docs/design.md                          (insufficient depth)
✗ docs/architecture/my-doc.md             (missing document_type)
✗ src/documentation/guide.md              (wrong prefix)
```

---

## Migration System

### Architecture

**Command**: `apm document migrate-to-structure`

**Components**:

1. **Query Engine**: Identify non-compliant documents
2. **Category Inference**: Map document_type → category
3. **Path Constructor**: Build target paths
4. **Backup Manager**: Create file copies before moving
5. **Checksum Validator**: SHA-256 verification
6. **Transaction Manager**: Atomic database updates

### Migration Algorithm

```python
def migrate_document_raw(doc_data, doc_type, category, target_path, project_root, db):
    """Migrate a single document with safety guarantees."""
    source_file = project_root / doc_data['file_path']
    target_file = project_root / target_path

    # Step 1: Create backup
    backup_path = create_backup(source_file, project_root)

    try:
        # Step 2: Calculate checksum before move
        checksum_before = calculate_checksum(source_file)

        # Step 3: Create target directory
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Step 4: Move file
        shutil.move(str(source_file), str(target_file))

        # Step 5: Verify checksum after move
        checksum_after = calculate_checksum(target_file)
        if checksum_before != checksum_after:
            # Rollback: restore from backup
            shutil.copy2(backup_path, source_file)
            target_file.unlink()
            return False, "Checksum mismatch! Rolled back."

        # Step 6: Update database (atomic transaction)
        parsed = DocumentReference.parse_path(target_path)
        with db.transaction() as conn:
            conn.execute("""
                UPDATE document_references
                SET file_path = ?,
                    category = ?,
                    document_type_dir = ?,
                    content_hash = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (target_path, parsed['category'], parsed['document_type'],
                  checksum_after, doc_data['id']))

        return True, f"Migrated: {doc_data['file_path']} → {target_path}"

    except Exception as e:
        # Rollback on error: restore from backup
        if backup_path and backup_path.exists():
            if not source_file.exists():
                shutil.copy2(backup_path, source_file)
            if target_file.exists():
                target_file.unlink()
        return False, f"Migration failed: {str(e)}"
```

### Safety Mechanisms

1. **Backups**: Files copied to `.aipm/backups/document-migration/` before moving
2. **Checksums**: SHA-256 hashes calculated before/after move
3. **Transactions**: Database updates wrapped in atomic transactions
4. **Rollback**: Automatic restoration on any error
5. **Dry-Run**: Preview mode to validate migration plan
6. **Confirmation**: Explicit user consent required for --execute

### Category Inference Logic

**Mapping**: `agentpm/cli/commands/document/migrate.py`

```python
CATEGORY_MAPPING = {
    # Planning & Analysis
    DocumentType.IDEA: "planning",
    DocumentType.REQUIREMENTS: "planning",
    DocumentType.USER_STORY: "planning",

    # Architecture & Design
    DocumentType.ARCHITECTURE: "architecture",
    DocumentType.DESIGN: "architecture",
    DocumentType.ADR: "architecture",

    # Documentation & Guides
    DocumentType.USER_GUIDE: "guides",
    DocumentType.ADMIN_GUIDE: "guides",
    DocumentType.TROUBLESHOOTING: "guides",

    # Testing & Quality
    DocumentType.TEST_PLAN: "testing",

    # Operations
    DocumentType.RUNBOOK: "operations",

    # Communication (default fallback)
    DocumentType.OTHER: "communication",
}
```

**Inference Process**:

1. Check for manual override (`--category` flag)
2. Look up document_type in CATEGORY_MAPPING
3. Fall back to "communication" if type unknown
4. Construct path: `docs/{category}/{document_type.value}/{filename}`

---

## Exception Handling

### Why Exceptions Are Necessary

1. **Legacy Support**: Existing projects have root-level files
2. **Standard Conventions**: README.md, CHANGELOG.md are standard root files
3. **Module Documentation**: In-code README files provide context
4. **Test Reports**: Generated reports shouldn't be in docs/
5. **Gradual Migration**: Allow projects to migrate over time

### Exception Design Philosophy

**Principle**: "Be strict for new documents, permissive for existing ones"

- **New Documents**: Must follow `docs/` structure (enforced by CLI + Pydantic)
- **Existing Documents**: Can remain in legacy paths (allowed by CHECK constraint)
- **Migration Path**: Gradual compliance via `migrate-to-structure` command

### Adding New Exceptions

To add a new exception pattern:

1. **Update Pydantic Validator**:
   ```python
   # agentpm/core/database/models/document_reference.py
   @field_validator('file_path')
   def validate_path_structure(cls, v: str, info) -> str:
       is_valid = (
           v.startswith('docs/')
           or v.startswith('new-pattern/')  # New exception
       )
   ```

2. **Update CHECK Constraint** (via new migration):
   ```sql
   -- migration_00XX.py
   CHECK (
       file_path LIKE 'docs/%'
       OR file_path LIKE 'new-pattern/%'  -- New exception
   )
   ```

3. **Document Exception** in user guide

4. **Add Test Case** for exception validation

---

## Testing Strategy

### Test Coverage

**Target**: 95% coverage for validation logic

**Test Files**:
- `tests/core/database/models/test_document_reference.py` - Model validation
- `tests/cli/commands/document/test_add.py` - CLI guidance
- `tests/core/database/migrations/test_migration_0032.py` - CHECK constraint
- `tests/integration/test_document_migration.py` - End-to-end migration

### Test Cases

**1. Pydantic Model Validation Tests**:

```python
def test_validate_compliant_path():
    """Valid docs/ path passes validation"""
    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=1,
        file_path="docs/architecture/design/system.md"
    )
    assert doc.file_path == "docs/architecture/design/system.md"

def test_validate_non_compliant_path_raises():
    """Non-compliant path raises ValueError"""
    with pytest.raises(ValueError, match="must start with 'docs/'"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="design/system.md"
        )

def test_validate_exception_pattern_readme():
    """README.md exception allowed"""
    doc = DocumentReference(
        entity_type=EntityType.PROJECT,
        entity_id=1,
        file_path="README.md"
    )
    assert doc.file_path == "README.md"

def test_validate_insufficient_depth():
    """Path with <4 parts raises ValueError"""
    with pytest.raises(ValueError, match="must follow pattern"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/design.md"
        )
```

**2. CHECK Constraint Tests**:

```python
def test_check_constraint_blocks_invalid_path(db):
    """Database CHECK constraint prevents invalid paths"""
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint"):
        with db.transaction() as conn:
            conn.execute("""
                INSERT INTO document_references (
                    entity_type, entity_id, file_path
                ) VALUES (?, ?, ?)
            """, ("work_item", 1, "invalid/path.md"))

def test_check_constraint_allows_exception(db):
    """CHECK constraint allows exception patterns"""
    with db.transaction() as conn:
        conn.execute("""
            INSERT INTO document_references (
                entity_type, entity_id, file_path
            ) VALUES (?, ?, ?)
        """, ("project", 1, "README.md"))
    # Should not raise
```

**3. Migration Tests**:

```python
def test_migration_dry_run_identifies_non_compliant(db):
    """Dry-run identifies documents needing migration"""
    # Create non-compliant document
    create_document(db, file_path="design/doc.md")

    # Run dry-run
    result = runner.invoke(cli, ['document', 'migrate-to-structure', '--dry-run'])

    assert "design/doc.md" in result.output
    assert "docs/architecture/design/doc.md" in result.output

def test_migration_creates_backups(db, tmp_path):
    """Migration creates backups before moving files"""
    # Setup
    source_file = tmp_path / "design" / "doc.md"
    source_file.parent.mkdir()
    source_file.write_text("test content")

    # Execute migration
    result = runner.invoke(cli, ['document', 'migrate-to-structure', '--execute'])

    # Verify backup created
    backup_dir = tmp_path / ".aipm" / "backups" / "document-migration"
    assert backup_dir.exists()
    assert len(list(backup_dir.glob("*.md"))) > 0

def test_migration_rollback_on_checksum_mismatch(db, tmp_path, monkeypatch):
    """Migration rolls back if checksum validation fails"""
    # Mock checksum mismatch
    def mock_checksum_after(path):
        return "invalid-checksum"

    monkeypatch.setattr('migrate.calculate_checksum', mock_checksum_after)

    # Execute migration
    result = runner.invoke(cli, ['document', 'migrate-to-structure', '--execute'])

    # Verify rollback
    assert "Checksum mismatch! Rolled back." in result.output
    assert original_file.exists()  # File restored
```

**4. CLI Guidance Tests**:

```python
def test_cli_offers_path_correction(runner):
    """CLI offers interactive path correction"""
    result = runner.invoke(cli, [
        'document', 'add',
        '--entity-type=work_item',
        '--entity-id=1',
        '--file-path=design/doc.md',
        '--type=design'
    ], input='y\n')  # Accept suggestion

    assert "Recommended path structure" in result.output
    assert "docs/architecture/design/doc.md" in result.output
    assert "Use recommended path?" in result.output
```

### Performance Tests

```python
def test_migration_performance_1000_documents(db, tmp_path):
    """Migration handles 1000 documents within 30 seconds"""
    # Create 1000 non-compliant documents
    for i in range(1000):
        create_document(db, file_path=f"legacy/doc-{i}.md")

    # Execute migration with timing
    start = time.time()
    result = runner.invoke(cli, ['document', 'migrate-to-structure', '--execute', '--no-backup'])
    duration = time.time() - start

    assert duration < 30  # Complete within 30 seconds
    assert "1000" in result.output  # All documents migrated
```

---

## Summary

### Key Design Principles

1. **Defense in Depth**: Three validation layers (CLI, Pydantic, Database)
2. **User Experience First**: Interactive guidance over strict enforcement
3. **Safe Migration**: Backups, checksums, atomic transactions
4. **Gradual Compliance**: Exceptions allow legacy support
5. **Cannot Bypass**: Database CHECK constraint is final enforcement

### Architecture Benefits

- **Predictable**: Standard path structure enforced at database level
- **Discoverable**: Categories and types enable systematic navigation
- **Safe**: Migration includes multiple safety mechanisms
- **Flexible**: Exceptions support legacy files and special cases
- **Testable**: Comprehensive test coverage at all layers

### Related Work Items

- **WI-113**: Document Path Validation Enforcement (this work)
- **WI-112**: Universal Documentation System (parent work)
- **Task 597**: Documentation for path validation system

---

**Version**: 1.0.0
**Last Updated**: 2025-10-20
**Related**: WI-113, Migration 0032, DocumentReference Model
