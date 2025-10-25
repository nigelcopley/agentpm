# Migration Test Suite: 0020→0027→0029

Comprehensive integration test suite for database migration sequence that fixes the agents.metadata column issue.

## Overview

This test suite validates the migration sequence:
- **Migration 0020**: Recreated agents table with tier column fix (accidentally omitted metadata)
- **Migration 0027**: Adds metadata TEXT column back to agents table
- **Migration 0029**: Inserts 5 utility agents using the metadata column

## Test Files

### test_migration_0027.py
**11 tests across 5 test suites**

Focused tests for migration 0027 (add metadata column):

1. **TestMigration0027SchemaChanges** (2 tests)
   - `test_metadata_column_added_to_agents_table`: Verifies column exists with correct type
   - `test_metadata_column_nullable`: Ensures backwards compatibility

2. **TestMigration0027Idempotency** (2 tests)
   - `test_migration_0027_idempotent`: Running twice doesn't error
   - `test_migration_0027_skips_if_column_exists`: Detects existing column

3. **TestMigration0027DataPreservation** (2 tests)
   - `test_existing_agent_data_preserved`: Agent records unchanged during migration
   - `test_metadata_default_value_for_new_agents`: New agents get default '{}'

4. **TestMigration0027UpgradeDowngrade** (2 tests)
   - `test_upgrade_then_downgrade_cycle`: Complete migration cycle
   - `test_downgrade_preserves_non_metadata_fields`: Safe rollback

5. **TestMigration0027EdgeCases** (3 tests)
   - `test_migration_on_empty_agents_table`: Works with no data
   - `test_metadata_can_store_json`: Complex JSON storage validation
   - `test_migration_recorded_in_registry`: Audit trail verification

**Coverage**: 100% of migration_0027.py

### test_migration_sequence.py
**15 tests across 7 test suites**

Integration tests for the complete migration sequence:

1. **TestFreshDatabaseMigrationSequence** (3 tests)
   - Fresh database from scratch
   - Utility agent creation
   - Metadata structure validation

2. **TestExistingDatabaseMigration** (2 tests)
   - Migration on database with existing agents
   - Sequential migration application

3. **TestMigration0029Idempotency** (2 tests)
   - No duplicate utility agents
   - Skip detection when agents exist

4. **TestMigrationSequenceValidation** (2 tests)
   - Complete schema verification
   - Index validation

5. **TestMigration0029NoProject** (1 test)
   - Graceful skip when no project exists

6. **TestMigrationChainIntegrity** (3 tests)
   - Migration chain gap detection (expected due to consolidation)
   - Migration recording verification
   - Pending migrations tracking

7. **TestUtilityAgentDetails** (2 tests)
   - Utility agent configuration verification
   - Active status validation

**Coverage**: 92% of migration_0029.py

### conftest.py
**8 reusable fixtures**

Shared test infrastructure:

- `temp_db_path`: Temporary SQLite database files
- `fresh_db_service`: Database with all migrations applied
- `empty_db_service`: Database without auto-migrations
- `migration_manager`: MigrationManager instance
- `schema_inspector`: Schema inspection utilities
- `test_project_factory`: Create test projects
- `test_agent_factory`: Create test agents
- `migration_state_factory`: Apply migrations to specific version

## Test Coverage

### By Acceptance Criteria

**AC1: Fresh Database Migration Sequence** ✅
- test_fresh_database_full_migration_sequence
- test_utility_agents_have_metadata
- test_utility_agents_metadata_structure

**AC2: Existing Database Migration** ✅
- test_migration_0027_on_database_with_existing_agents
- test_migration_0029_adds_utility_agents_after_0027

**AC3: Idempotency** ✅
- test_migration_0027_idempotent
- test_migration_0027_skips_if_column_exists
- test_migration_0029_idempotent
- test_migration_0029_skips_if_agents_exist

**AC4: Schema Validation** ✅
- test_metadata_column_added_to_agents_table
- test_metadata_column_nullable
- test_agents_table_schema_after_sequence
- test_agents_table_indexes_after_sequence

### Edge Cases Covered

- Empty agents table
- No project exists (migration 0029 requirement)
- Complex JSON metadata storage
- Migration chain gap detection
- Column already exists
- Agents already exist

### Code Coverage

| File | Coverage | Lines | Missing |
|------|----------|-------|---------|
| migration_0027.py | 100% | 26 | 0 |
| migration_0029.py | 92% | 36 | 3 (downgrade function) |

## Running Tests

### Run All Migration Tests
```bash
pytest tests/core/database/migrations/ -v
```

### Run Specific Test Suite
```bash
# Migration 0027 tests only
pytest tests/core/database/migrations/test_migration_0027.py -v

# Migration sequence tests only
pytest tests/core/database/migrations/test_migration_sequence.py -v
```

### Run with Coverage
```bash
pytest tests/core/database/migrations/ \
  --cov=agentpm/core/database/migrations/files/migration_0027 \
  --cov=agentpm/core/database/migrations/files/migration_0029 \
  --cov-report=term-missing
```

### Run Specific Test
```bash
pytest tests/core/database/migrations/test_migration_0027.py::TestMigration0027Idempotency::test_migration_0027_idempotent -v
```

## Test Results

**Total Tests**: 26
**Passed**: 26 ✅
**Failed**: 0
**Coverage Target**: ≥90% (TEST-023)
**Coverage Achieved**:
- migration_0027.py: 100%
- migration_0029.py: 92%
**Quality Gate**: ✅ PASSED

## Test Patterns

All tests follow APM (Agent Project Manager) testing standards:

- ✅ **AAA Pattern**: Arrange, Act, Assert (TEST-007)
- ✅ **Clear Names**: Descriptive test names (TEST-001)
- ✅ **Fixtures**: Proper setup/teardown (TEST-006)
- ✅ **Project-Relative**: Imports use project structure (TEST-001)
- ✅ **Coverage**: ≥90% for new code (TEST-023)

## Key Testing Insights

### Migration 0027 Idempotency
Migration 0027 detects if the metadata column already exists using `PRAGMA table_info(agents)` and skips the ALTER TABLE if found. This prevents errors when running migrations multiple times.

### Migration 0029 Project Requirement
Migration 0029 requires at least one project to exist in the database before creating utility agents. If no project exists, it prints a warning and skips agent creation. This is validated in `test_migration_0029_skips_if_no_project`.

### Migration Chain Gaps
Migration 0018 consolidated migrations 0001-0017, creating expected gaps in the version sequence. The `validate_migration_chain()` method correctly returns `False` due to these gaps, which is expected behavior and tested in `test_migration_chain_has_expected_gaps`.

### Schema Evolution
The test fixtures handle schema evolution gracefully by detecting column existence before insertion. For example, `test_project_factory` checks for the `metadata` column before deciding which INSERT statement to use.

## Maintenance Notes

### Adding New Migration Tests

When adding new migration tests:

1. Use existing fixtures from `conftest.py`
2. Follow AAA pattern consistently
3. Test both upgrade and downgrade paths
4. Include idempotency tests
5. Verify schema changes with `schema_inspector`
6. Add edge case tests

### Fixture Updates

If migration schema changes:

1. Update `test_project_factory` to handle new columns
2. Update `test_agent_factory` to handle new columns
3. Add new fixtures to `conftest.py` if needed
4. Document schema detection logic

## Related Documentation

- Migration 0027: `agentpm/core/database/migrations/files/migration_0027.py`
- Migration 0029: `agentpm/core/database/migrations/files/migration_0029.py`
- Migration Manager: `agentpm/core/database/migrations/manager.py`
- Testing Standards: `_RULES/TEST-*.md`

## Authors

- Test Implementer Sub-Agent
- Coverage Target: WI-108 Task #550
- Created: 2025-10-18
