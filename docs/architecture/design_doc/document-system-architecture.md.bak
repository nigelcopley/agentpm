# Document System Architecture - Developer Guide

Technical documentation for the Universal Documentation System with 3-layer path validation enforcement.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [DocumentReference Model](#documentreference-model)
3. [Path Validation](#path-validation)
4. [Database Enforcement](#database-enforcement)
5. [Category Mapping](#category-mapping)
6. [Adding Document Types](#adding-document-types)
7. [Adding Categories](#adding-categories)
8. [Migration Patterns](#migration-patterns)
9. [Testing](#testing)

---

## Architecture Overview

### 3-Layer Validation Architecture

The document system enforces path compliance at **3 layers** for defense-in-depth:

```
┌──────────────────────────────────────────┐
│ Layer 1: Pydantic Model Validation      │
│ ├─ DocumentReference.validate_path_...  │
│ ├─ Validates docs/ prefix                │
│ ├─ Checks minimum depth (4 parts)        │
│ └─ Verifies category/type consistency    │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│ Layer 2: CLI Interactive Guidance       │
│ ├─ _validate_and_guide_path()           │
│ ├─ Suggests correct paths                │
│ ├─ Offers auto-correction                │
│ └─ Allows informed overrides             │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│ Layer 3: Database CHECK Constraint      │
│ ├─ SQL-level enforcement                 │
│ ├─ Prevents non-compliant inserts        │
│ ├─ Exception patterns (README.md, etc.)  │
│ └─ Last line of defense                  │
└──────────────────────────────────────────┘
```

### Component Locations

| Component | File | Responsibility |
|-----------|------|----------------|
| Pydantic Model | `agentpm/core/database/models/document_reference.py` | Data validation |
| Database Adapter | `agentpm/core/database/adapters/document_reference_adapter.py` | SQLite ↔ Pydantic |
| Business Logic | `agentpm/core/database/methods/document_references.py` | CRUD operations |
| CLI Commands | `agentpm/cli/commands/document/` | User interface |
| Enumerations | `agentpm/core/database/enums/types.py` | Type definitions |
| Migration | `agentpm/core/database/migrations/files/migration_0032_...` | Schema changes |

---

## DocumentReference Model

### Model Definition

```python
from pydantic import BaseModel, Field, field_validator
from agentpm.core.database.enums import DocumentType, DocumentCategory


class DocumentReference(BaseModel):
    """Universal Documentation System model."""

    # Entity linkage
    entity_type: EntityType
    entity_id: int

    # Hierarchical categorization
    category: Optional[str]  # Top-level (planning, architecture, etc.)
    document_type: Optional[DocumentType]  # Classification

    # File metadata
    file_path: str  # Required format: docs/{category}/{document_type}/{filename}
    title: Optional[str]
    description: Optional[str]
    file_size_bytes: Optional[int]
    content_hash: Optional[str]  # SHA256 for integrity
    format: Optional[DocumentFormat]

    # Rich metadata (NEW in migration_0032)
    segment_type: Optional[str]
    component: Optional[str]
    domain: Optional[str]
    audience: Optional[str]
    maturity: Optional[str]
    priority: Optional[str]
    tags: List[str]

    # Workflow integration
    phase: Optional[str]  # D1, P1, I1, R1, O1, E1
    work_item_id: Optional[int]

    # Lifecycle
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Field Validators

#### Path Structure Validation

```python
@field_validator('file_path')
@classmethod
def validate_path_structure(cls, v: str, info) -> str:
    """
    Validate path follows docs/{category}/{document_type}/{filename}.
    
    Enforcement:
    1. Must start with 'docs/'
    2. Must have minimum 4 parts (docs/cat/type/file)
    3. Category in path must match 'category' field (if set)
    4. Document type in path must match 'document_type' field (if set)
    """
    if not v.startswith('docs/'):
        raise ValueError(f"Document path must start with 'docs/'. Got: {v}")
    
    parts = v.split('/')
    if len(parts) < 4:
        raise ValueError(
            f"Path must follow pattern: docs/{{category}}/{{document_type}}/{{filename}}. "
            f"Got: {v}"
        )
    
    # Validate category consistency
    if 'category' in info.data and info.data['category'] is not None:
        if parts[1] != info.data['category']:
            raise ValueError(
                f"Path category '{parts[1]}' doesn't match field category '{info.data['category']}'"
            )
    
    # Validate document_type consistency  
    if 'document_type' in info.data and info.data['document_type'] is not None:
        if parts[2] != info.data['document_type']:
            raise ValueError(
                f"Path document_type '{parts[2]}' doesn't match field document_type '{info.data['document_type']}'"
            )
    
    return v
```

### Helper Methods

#### construct_path()

```python
@staticmethod
def construct_path(category: str, document_type: str, filename: str) -> str:
    """
    Construct canonical document path.
    
    Args:
        category: One of 8 categories (planning, architecture, etc.)
        document_type: Document type (requirements, design, etc.)
        filename: Base filename (e.g., auth-functional.md)
    
    Returns:
        Canonical path: docs/{category}/{document_type}/{filename}
    
    Example:
        >>> DocumentReference.construct_path("planning", "requirements", "auth.md")
        "docs/planning/requirements/auth.md"
    """
    return f"docs/{category}/{document_type}/{filename}"
```

#### parse_path()

```python
@staticmethod
def parse_path(file_path: str) -> dict:
    """
    Parse path to extract category, document_type, filename.
    
    Args:
        file_path: Full path (e.g., docs/planning/requirements/auth.md)
    
    Returns:
        Dict with category, document_type, filename
    
    Raises:
        ValueError: If path doesn't match expected structure
    
    Example:
        >>> DocumentReference.parse_path("docs/planning/requirements/auth.md")
        {"category": "planning", "document_type": "requirements", "filename": "auth.md"}
    """
    parts = file_path.split('/')
    if len(parts) < 4 or parts[0] != 'docs':
        raise ValueError(
            f"Invalid path structure. Expected: docs/{{category}}/{{document_type}}/{{filename}}. "
            f"Got: {file_path}"
        )
    
    return {
        'category': parts[1],
        'document_type': parts[2],
        'filename': '/'.join(parts[3:])  # Handle nested filenames
    }
```

---

## Path Validation

### CLI Layer Validation

The CLI provides **interactive guidance** for path compliance:

```python
def _validate_and_guide_path(file_path: str, document_type: str, console: Console) -> str:
    """
    Validate path and provide guidance if non-compliant.
    
    Workflow:
    1. Check if path starts with 'docs/'
    2. If not, infer category from document_type
    3. Generate suggested corrected path
    4. Display guidance with category descriptions
    5. Offer to use suggested path
    6. Allow informed override if user insists
    """
    if not file_path.startswith('docs/'):
        # Infer category from document_type mapping
        category = CATEGORY_MAPPING.get(document_type, 'communication')
        
        # Generate suggested path
        filename = Path(file_path).name
        suggested = f"docs/{category}/{document_type}/{filename}"
        
        # Display guidance
        console.print("[yellow]⚠️  Path does not follow standard structure[/yellow]")
        console.print(f"💡 Recommended: {suggested}")
        console.print("📁 Standard: docs/{category}/{document_type}/{filename}")
        
        # Display all categories with descriptions
        _display_category_help(console)
        
        # Interactive decision
        if click.confirm("Use recommended path?", default=True):
            return suggested
        elif click.confirm("Continue with non-standard path?", default=False):
            return file_path
        else:
            raise click.Abort()
    
    return file_path
```

### Database Layer Validation

The database enforces path compliance via **CHECK constraint**:

```sql
-- Migration 0032: Enforce docs/ prefix with exceptions
ALTER TABLE document_references ADD CONSTRAINT check_path_structure CHECK (
  -- Standard path: docs/{category}/{document_type}/{filename}
  file_path LIKE 'docs/%'
  
  -- Exceptions for special files
  OR file_path LIKE 'README%'
  OR file_path LIKE 'CHANGELOG%'
  OR file_path LIKE 'LICENSE%'
  OR file_path LIKE 'CONTRIBUTING%'
  OR file_path LIKE '.claude/agents/%'
  OR file_path LIKE '_RULES/%'
);
```

**Rationale for exceptions**:
- `README.md` - Repository root documentation (standard practice)
- `CHANGELOG.md` - Version history at root (standard practice)
- `LICENSE` - Legal files belong at root (legal requirement)
- `CONTRIBUTING.md` - Contribution guidelines at root (standard practice)
- `.claude/agents/*.md` - Agent definition files (tooling requirement)
- `_RULES/*.md` - Rules system files (tooling requirement)

---

## Database Enforcement

### Migration Script

The CHECK constraint is added via migration:

```python
# migration_0032_enforce_docs_path.py

def upgrade(db_path: Path) -> None:
    """Add CHECK constraint to enforce docs/ prefix."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add CHECK constraint with exception patterns
        cursor.execute("""
            ALTER TABLE document_references 
            ADD CONSTRAINT check_path_structure 
            CHECK (
                file_path LIKE 'docs/%'
                OR file_path LIKE 'README%'
                OR file_path LIKE 'CHANGELOG%'
                OR file_path LIKE 'LICENSE%'
                OR file_path LIKE 'CONTRIBUTING%'
                OR file_path LIKE '.claude/agents/%'
                OR file_path LIKE '_RULES/%'
            )
        """)
        
        conn.commit()
        print("✅ CHECK constraint added successfully")
        
    except sqlite3.IntegrityError as e:
        # Existing non-compliant paths found
        print(f"⚠️  Constraint violation: {e}")
        print("Run: apm document migrate-to-structure")
        raise
    finally:
        conn.close()
```

### Handling Constraint Violations

If constraint violation occurs during migration:

```python
try:
    cursor.execute("ALTER TABLE document_references ADD CONSTRAINT ...")
except sqlite3.IntegrityError:
    # Find violating paths
    cursor.execute("""
        SELECT id, file_path FROM document_references
        WHERE file_path NOT LIKE 'docs/%'
          AND file_path NOT LIKE 'README%'
          AND file_path NOT LIKE 'CHANGELOG%'
          ...
    """)
    
    violations = cursor.fetchall()
    print(f"Found {len(violations)} non-compliant paths")
    print("Fix with: apm document migrate-to-structure")
```

---

## Category Mapping

### CATEGORY_MAPPING Dictionary

Maps document types to their canonical category:

```python
# agentpm/cli/commands/document/add.py

CATEGORY_MAPPING = {
    # Planning documents
    'requirements': 'planning',
    'user_story': 'planning',
    'use_case': 'planning',
    'refactoring_guide': 'planning',
    'implementation_plan': 'planning',
    
    # Architecture documents
    'architecture': 'architecture',
    'design': 'architecture',
    'adr': 'architecture',
    'technical_specification': 'architecture',
    
    # Guide documents
    'user_guide': 'guides',
    'admin_guide': 'guides',
    'troubleshooting': 'guides',
    'migration_guide': 'guides',
    
    # Reference documents
    'specification': 'reference',
    'api_doc': 'reference',
    
    # Process documents
    'test_plan': 'processes',
    
    # Governance documents
    'quality_gates_specification': 'governance',
    
    # Operations documents
    'runbook': 'operations',
    
    # Communication documents
    'business_pillars_analysis': 'communication',
    'market_research_report': 'communication',
    'competitive_analysis': 'communication',
    'stakeholder_analysis': 'communication',
}
```

### Using Category Mapping

```python
def get_category_for_type(document_type: str) -> str:
    """Get canonical category for a document type."""
    return CATEGORY_MAPPING.get(document_type, 'communication')  # Default fallback

def validate_category_type_match(category: str, document_type: str) -> bool:
    """Check if category matches document_type's mapped category."""
    expected_category = CATEGORY_MAPPING.get(document_type)
    if expected_category and category != expected_category:
        return False
    return True
```

---

## Adding Document Types

### Step-by-Step Guide

**1. Add to DocumentType enum** (`agentpm/core/database/enums/types.py`):

```python
class DocumentType(str, Enum):
    # ... existing types ...
    
    # NEW: Add your document type
    NEW_TYPE = "new_type"
    
    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            # ... existing labels ...
            cls.NEW_TYPE.value: "New Type - Description here",
        }
```

**2. Add to CATEGORY_MAPPING** (`agentpm/cli/commands/document/add.py`):

```python
CATEGORY_MAPPING = {
    # ... existing mappings ...
    'new_type': 'appropriate_category',  # Choose from 8 categories
}
```

**3. Add to document types display** (`agentpm/cli/commands/document/types.py`):

```python
def _show_document_types_table(console: Console):
    categories = {
        "📋 Appropriate Category": {
            # ... existing types ...
            "new_type": "Description of new document type",
        },
    }
```

**4. Update migration** (if adding to existing database):

```python
# Create a new migration file: migration_NNNN_add_new_doc_type.py

def upgrade(db_path: Path) -> None:
    """Add NEW_TYPE to DocumentType enum."""
    # SQLite doesn't support enum modification
    # No schema change needed - values stored as strings
    print("✅ NEW_TYPE added to DocumentType enum (code-level only)")
```

**5. Add tests**:

```python
def test_new_document_type():
    """Test new document type path validation."""
    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=1,
        file_path="docs/appropriate_category/new_type/example.md",
        document_type=DocumentType.NEW_TYPE,
    )
    
    assert doc.file_path == "docs/appropriate_category/new_type/example.md"
    assert doc.document_type == DocumentType.NEW_TYPE
```

---

## Adding Categories

### When to Add a New Category

**Only add a new category if**:
- None of the existing 8 categories fit
- The category represents a truly distinct organizational need
- Multiple document types would belong to this category

**Existing 8 categories are designed to be universal**. Consider carefully before adding.

### Step-by-Step Guide

**1. Add to DocumentCategory enum** (`agentpm/core/database/enums/types.py`):

```python
class DocumentCategory(str, Enum):
    # ... existing categories ...
    
    # NEW: Add your category (RARE - usually not needed)
    NEW_CATEGORY = "new_category"
```

**2. Update category descriptions** (all CLI files showing categories):

- `agentpm/cli/commands/document/add.py` - Interactive guidance
- `agentpm/cli/commands/document/types.py` - Category display
- Documentation files

**3. Create directory structure**:

```bash
mkdir -p docs/new_category/{document_type}/
```

**4. Update validation**:

No code changes needed - validation is enum-based.

**5. Update documentation**:

- User guide: Add category description
- Developer guide: Document category purpose
- Examples: Provide sample documents

---

## Migration Patterns

### Bulk Path Migration

The `migrate-to-structure` command handles bulk migrations:

```python
# agentpm/cli/commands/document/migrate.py

def migrate_document_paths(db, dry_run=False):
    """
    Migrate all non-compliant document paths to standard structure.
    
    Algorithm:
    1. Query all documents from database
    2. Filter non-compliant paths (not starting with docs/)
    3. For each document:
       a. Infer category from document_type
       b. Extract filename from current path
       c. Construct new path: docs/{category}/{document_type}/{filename}
       d. Update database (if not dry-run)
    4. Report statistics
    """
    docs = doc_methods.list_all_document_references(db)
    
    non_compliant = [d for d in docs if not d.file_path.startswith('docs/')]
    
    migrations = []
    for doc in non_compliant:
        category = CATEGORY_MAPPING.get(doc.document_type, 'communication')
        filename = Path(doc.file_path).name
        new_path = f"docs/{category}/{doc.document_type}/{filename}"
        
        migrations.append({
            'id': doc.id,
            'old_path': doc.file_path,
            'new_path': new_path,
            'category': category,
        })
    
    if dry_run:
        print_migration_preview(migrations)
        return
    
    # Execute migrations
    for migration in migrations:
        try:
            doc_methods.update_document_reference(
                db, 
                migration['id'], 
                file_path=migration['new_path']
            )
        except Exception as e:
            print(f"❌ Failed to migrate {migration['id']}: {e}")
    
    print_migration_summary(migrations)
```

### Manual Path Correction

For individual documents:

```python
# Update single document path
doc_methods.update_document_reference(
    db,
    document_id=42,
    file_path="docs/architecture/design/corrected-path.md"
)
```

---

## Testing

### Unit Tests

Test path validation at model level:

```python
# tests/unit/core/database/models/test_document_reference.py

def test_path_validation_docs_prefix():
    """Test path must start with docs/."""
    with pytest.raises(ValueError, match="must start with 'docs/'"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="architecture/design/file.md",  # Missing docs/
        )

def test_path_validation_minimum_depth():
    """Test path must have minimum 4 parts."""
    with pytest.raises(ValueError, match="must follow pattern"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/design.md",  # Only 2 parts
        )

def test_path_validation_category_consistency():
    """Test category in path must match field."""
    with pytest.raises(ValueError, match="doesn't match field category"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category="architecture",
            file_path="docs/planning/design/file.md",  # Category mismatch
        )
```

### Integration Tests

Test CLI commands:

```python
# tests/integration/cli/commands/test_document_add.py

def test_document_add_with_path_guidance(cli_runner, test_db):
    """Test interactive path correction."""
    result = cli_runner.invoke(
        document_add,
        [
            '--entity-type=work_item',
            '--entity-id=1',
            '--file-path=design/file.md',  # Non-compliant
            '--type=design',
        ],
        input='y\n'  # Accept suggested path
    )
    
    assert "Recommended path structure" in result.output
    assert "docs/architecture/design/file.md" in result.output
    
    # Verify document created with correct path
    doc = doc_methods.get_document_reference(test_db, 1)
    assert doc.file_path == "docs/architecture/design/file.md"
```

### Database Tests

Test CHECK constraint enforcement:

```python
# tests/integration/database/test_document_constraints.py

def test_check_constraint_enforcement(test_db):
    """Test database rejects non-compliant paths."""
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO document_references (file_path, ...)
            VALUES ('invalid/path.md', ...)
        """)

def test_check_constraint_allows_exceptions(test_db):
    """Test database allows exception patterns."""
    cursor.execute("""
        INSERT INTO document_references (file_path, ...)
        VALUES ('README.md', ...)
    """)
    # Should succeed without error
```

### Coverage Target

- **Model validation**: >95% coverage
- **CLI commands**: >90% coverage
- **Database methods**: >90% coverage
- **Integration paths**: All happy + error paths

---

## Architecture Decisions

### ADR: 3-Layer Validation

**Context**: Need to enforce path structure without breaking user experience

**Decision**: Implement validation at 3 layers:
1. Pydantic (data integrity)
2. CLI (user guidance)
3. Database (final enforcement)

**Rationale**:
- Defense in depth
- Progressive enhancement
- Graceful degradation
- Clear error messages

**Consequences**:
- More code complexity
- Better user experience
- Stronger guarantees
- Easier debugging

### ADR: 8 Universal Categories

**Context**: Need categories that work for any project type

**Decision**: Use 8 universal categories (planning, architecture, guides, reference, processes, governance, operations, communication)

**Rationale**:
- Generalizable across domains
- Sufficient granularity
- Not too many options
- Clear boundaries

**Consequences**:
- Some documents may not fit perfectly
- Default fallback to 'communication'
- Requires good documentation

---

## Performance Considerations

### Path Validation Performance

- **Pydantic validation**: <1ms per document
- **CLI guidance**: User-interactive (not performance-critical)
- **Database constraint**: <1ms per insert/update

### Query Performance

All path queries use LIKE operator - ensure indexes:

```sql
CREATE INDEX idx_document_references_file_path 
ON document_references(file_path);
```

### Bulk Operations

Migration handles bulk updates efficiently:

```python
# Batch updates in transaction
with db.transaction():
    for migration in migrations:
        update_document_reference(db, migration['id'], migration['new_path'])
```

---

## Troubleshooting

### Common Development Issues

**Issue**: Path validation fails unexpectedly

**Debug**:
```python
# Enable validation debugging
doc = DocumentReference.construct(
    file_path="docs/planning/requirements/test.md",
    # ... other fields ...
)
# Check validation info
print(doc.model_dump())
```

**Issue**: CHECK constraint fails after migration

**Solution**: Run migration in dry-run mode first:
```bash
apm document migrate-to-structure --dry-run
```

**Issue**: Category mapping inconsistent

**Solution**: Verify CATEGORY_MAPPING matches DocumentType enum:
```python
# Verify all document types have category mapping
for doc_type in DocumentType:
    category = CATEGORY_MAPPING.get(doc_type.value)
    if not category:
        print(f"Missing mapping: {doc_type.value}")
```

---

## References

- **Pydantic Documentation**: https://docs.pydantic.dev/
- **SQLite CHECK Constraints**: https://www.sqlite.org/lang_createtable.html#check_constraints
- **APM (Agent Project Manager) Three-Tier Architecture**: `docs/components/agents/architecture/three-tier-orchestration.md`
- **User Guide**: `docs/guides/user_guide/document-management.md`
- **Migration Runbook**: `docs/operations/runbook/document-migration-runbook.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-10-19
**Related**: WI-113 (Document Path Validation Enforcement)
