# Document Hybrid Storage Test Suite

Comprehensive test suite for WI-133: Document System Enhancement with Database Content Storage and File Sync.

## Overview

This test suite validates the hybrid document storage system where:
- **Database** is the source of truth for document content
- **Files** are synchronized copies for git-friendly diffs and IDE editing
- **Search** enables full-text queries across all documents
- **CLI** provides user-friendly content management

## Test Structure

```
tests/
├── services/document/          # Service layer tests
│   ├── conftest.py            # Shared fixtures
│   ├── test_content_storage.py   # Content CRUD (20 tests)
│   ├── test_file_sync.py         # File sync (40 tests)
│   └── test_search.py            # Search (33 tests)
├── cli/commands/
│   └── test_document_content.py  # CLI commands (30 tests)
├── scripts/
│   └── test_document_migration.py # Migration (25 tests)
└── e2e/
    └── test_document_e2e_content.py # E2E workflows (20 tests)
```

**Total: 168 tests**

## Test Categories

### 1. Content Storage Tests (`test_content_storage.py`)

Tests database content management:
- Create documents with content
- Update document content
- Retrieve document content
- Content hash validation
- Storage mode transitions
- Sync status tracking

**Coverage**: Document content storage service (≥90%)

### 2. File Sync Tests (`test_file_sync.py`)

Tests bidirectional file synchronization:
- DB→File sync (one-way)
- File→DB sync (one-way)
- Bidirectional smart sync
- Conflict detection
- Conflict resolution strategies
- Missing file/DB handling
- Bulk operations
- Performance benchmarks

**Coverage**: File sync service (≥90%)

### 3. Search Tests (`test_search.py`)

Tests full-text document search:
- Keyword and phrase queries
- Entity filtering
- Document type filtering
- Ranking and relevance
- Snippet generation
- Highlight positions
- Search performance (<200ms)
- Pagination

**Coverage**: Document search service (≥90%)

### 4. CLI Tests (`test_document_content.py`)

Tests CLI commands:
- `apm document add --content`
- `apm document sync` (various modes)
- `apm document search`
- `apm document get-content`
- `apm document set-content`
- Error handling
- Rich output formatting

**Coverage**: Document content CLI (≥90%)

### 5. Migration Tests (`test_document_migration.py`)

Tests migration from file-only to hybrid:
- Successful migration
- Dry-run mode
- Missing file handling
- Hash verification
- Rollback capability
- Progress reporting

**Coverage**: Migration script (≥90%)

### 6. E2E Tests (`test_document_e2e_content.py`)

Tests complete workflows:
- Create→Edit→Search→Sync lifecycle
- Multi-document operations
- Cross-entity search
- Content integrity over time
- Real-world scenarios (developer, writer, git workflows)

**Coverage**: Complete system integration (≥90%)

## Current Status

**⚠️ All tests are currently skipped** with `pytest.skip("Awaiting implementation of...")`.

These tests follow **Test-Driven Development (TDD)** principles:
1. **Tests written first** to specify expected behavior
2. **Implementation** will make tests pass
3. **Refactoring** while maintaining green tests

## Running Tests

### Run All Document Tests
```bash
pytest tests/services/document/ -v
```

### Run Specific Test File
```bash
pytest tests/services/document/test_content_storage.py -v
```

### Run Specific Test Class
```bash
pytest tests/services/document/test_file_sync.py::TestBidirectionalSync -v
```

### Run Single Test
```bash
pytest tests/services/document/test_search.py::TestFullTextSearch::test_search_simple_keyword -v
```

### Run with Coverage
```bash
pytest tests/services/document/ --cov=agentpm.services.document --cov-report=html
```

### Skip Performance Tests
```bash
pytest tests/services/document/ -m "not performance"
```

## Test Patterns

### AAA Pattern

All tests follow **Arrange-Act-Assert**:

```python
def test_create_document_with_content(self, db_service, work_item):
    """
    GIVEN a document with content
    WHEN creating document with content storage
    THEN document is saved with content in database
    """
    # Arrange - Set up test data
    content = "# Test Document\n\nThis is test content."
    doc = DocumentReference(...)

    # Act - Execute the operation
    result = create_document_with_content(db_service, doc, content)

    # Assert - Verify expectations
    assert result.id is not None
    assert result.content == content
    assert result.content_hash is not None
```

### Fixtures

Common fixtures available (see `conftest.py`):
- `db_service` - Initialized database service
- `project` - Test project
- `work_item` - Test work item
- `task` - Test task
- `tmp_path` - Temporary directory for files
- `cli_runner` - Click CLI test runner
- `benchmark` - Performance benchmark fixture

## Acceptance Criteria Coverage

Each test maps to acceptance criteria from WI-133:

**AC1: Content Storage**
- ✓ Store document content in database
- ✓ Content hash validation
- ✓ Content retrieval

**AC2: File Sync**
- ✓ DB→File sync
- ✓ File→DB sync
- ✓ Bidirectional sync
- ✓ Conflict resolution

**AC3: Search**
- ✓ Full-text search
- ✓ Entity filtering
- ✓ Performance <200ms

**AC4: CLI Commands**
- ✓ Content management commands
- ✓ Sync commands
- ✓ Search commands

**AC5: Migration**
- ✓ Migrate existing documents
- ✓ Hash verification
- ✓ Rollback capability

**AC6: E2E Workflows**
- ✓ Complete lifecycles
- ✓ Real-world scenarios
- ✓ Content integrity

## Performance Targets

### Search Performance
- Small corpus (10 docs): <50ms
- Medium corpus (100 docs): <200ms
- Large corpus (1000 docs): <500ms (target <200ms)

### Sync Performance
- 10 small documents: <100ms
- 10 medium documents: <500ms
- 100 documents: <5s

## Next Steps

1. **Implement content storage service** (`agentpm/services/document/content_storage.py`)
2. **Un-skip relevant tests** and verify they pass
3. **Implement file sync service** (`agentpm/services/document/file_sync.py`)
4. **Un-skip sync tests** and verify
5. **Continue** through search, CLI, migration
6. **Run full test suite** and verify ≥90% coverage
7. **Performance tuning** based on benchmark results

## Contributing

When implementing features:

1. **Un-skip tests** for the feature you're implementing
2. **Run tests** to see failures (red)
3. **Implement** until tests pass (green)
4. **Refactor** while keeping tests green
5. **Add edge case tests** as needed
6. **Update this README** if test structure changes

## Questions?

See:
- WI-133: Document System Enhancement
- Task #716: Create Comprehensive Test Suite for Document Storage
- Design Doc: `docs/architecture/design/hybrid-document-storage.md` (TBD)
