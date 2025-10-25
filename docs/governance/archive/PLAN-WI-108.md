# Implementation Plan: WI-108 - Fix Migration Schema Mismatch

**Artifact Type**: `plan.snapshot`
**Work Item ID**: 108
**Status**: P1 Gate PASSED
**Created**: 2025-10-18
**Planning Orchestrator**: Completed

---

## Executive Summary

**Problem**: Migration 0020 recreated agents table without metadata column, but migration 0029 tries to INSERT with metadata field, causing schema errors on every CLI command.

**Solution**: Migration 0027 adds the missing metadata column with proper idempotency checks.

**Effort**: 8.5 hours total (5 tasks)
**Critical Path**: 8.5 hours (sequential workflow)
**Priority**: 1 (Critical - blocks all CLI commands)

---

## Task Breakdown

### Task 548: Analyze migration 0027 implementation
- **Type**: ANALYSIS
- **Effort**: 1.5 hours
- **Status**: draft
- **Dependencies**: None (entry point)
- **Agent**: aipm-database-developer

**Objective**: Review migration 0027 code to verify correctness and identify any issues.

**Acceptance Criteria**:
1. Migration 0027 code reviewed
2. Idempotency verified (PRAGMA table_info check)
3. Dependencies mapped (after 0020, before 0029)
4. Current database state documented

**Deliverables**:
- Analysis report on migration 0027 implementation
- Documentation of migration sequence
- Assessment of idempotency mechanism
- Current database schema state

---

### Task 549: Verify migration 0027 execution or create fix migration
- **Type**: BUGFIX
- **Effort**: 2.0 hours
- **Status**: draft
- **Dependencies**: Task 548 (must complete first)
- **Agent**: aipm-database-developer

**Objective**: Ensure migration 0027 executes successfully and adds metadata column.

**Acceptance Criteria**:
1. Migration execution verified
2. Metadata column exists in agents table
3. Column has DEFAULT '{}' constraint
4. Idempotency verified (can run multiple times safely)

**Implementation Notes**:
- Use ALTER TABLE agents ADD COLUMN metadata TEXT DEFAULT '{}'
- Include PRAGMA table_info check for idempotency
- Test on both fresh and existing databases

**Deliverables**:
- Migration execution confirmed OR
- New migration created if needed
- Verification that metadata column exists
- Test results showing idempotency

---

### Task 550: Test migration 0027/0029 sequence
- **Type**: TESTING
- **Effort**: 2.5 hours
- **Status**: draft
- **Dependencies**: Task 549 (must complete first)
- **Agent**: aipm-testing-specialist

**Objective**: Create integration test for full migration sequence.

**Acceptance Criteria**:
1. Integration test created
2. Test verifies metadata column exists
3. Test verifies migration 0029 succeeds
4. Test includes idempotency checks
5. Test passes on clean database

**Test Requirements**:
- Test type: Integration
- Minimum coverage: 90%
- Test migration sequence: 0020 → 0027 → 0029
- Verify data preservation

**Deliverables**:
- Integration test file: `tests/integration/test_migration_0027_0029_sequence.py`
- Test coverage report
- Documentation of test scenarios
- Passing test results

---

### Task 551: Verify apm status executes without errors
- **Type**: TESTING
- **Effort**: 1.0 hour
- **Status**: draft
- **Dependencies**: Task 550 (must complete first)
- **Agent**: aipm-testing-specialist

**Objective**: Verify CLI commands work after migration fix.

**Acceptance Criteria**:
1. `apm status` runs without errors
2. `apm agents list` works
3. `apm init` completes successfully
4. No schema mismatch errors in logs

**Deliverables**:
- CLI command execution tests
- Verification that all commands work
- Log analysis showing no errors
- Test results

---

### Task 552: Document migration fix and database schema
- **Type**: DOCUMENTATION
- **Effort**: 1.5 hours
- **Status**: draft
- **Dependencies**: Task 551 (must complete first)
- **Agent**: aipm-documentation-specialist

**Objective**: Document the root cause, fix, and updated schema.

**Acceptance Criteria**:
1. Migration 0027 documented with root cause
2. Database schema docs updated
3. Troubleshooting guide updated
4. Migration sequence documented

**Deliverables**:
- Updated migration documentation
- Updated database schema docs
- Troubleshooting guide entry
- Migration sequence diagram

---

## Dependencies Graph

```
548 (ANALYSIS 1.5h)
 ↓
549 (BUGFIX 2.0h)
 ↓
550 (TESTING 2.5h)
 ↓
551 (TESTING 1.0h)
 ↓
552 (DOCUMENTATION 1.5h)
```

**Critical Path**: 8.5 hours (all tasks sequential)

**Parallelization Opportunities**: None (each task depends on previous completion)

---

## Time-Box Compliance

| Task Type       | Limit | Actual | Status |
|-----------------|-------|--------|--------|
| ANALYSIS        | ≤8h   | 1.5h   | ✅ PASS |
| BUGFIX          | ≤4h   | 2.0h   | ✅ PASS |
| TESTING         | ≤6h   | 3.5h   | ✅ PASS |
| DOCUMENTATION   | ≤4h   | 1.5h   | ✅ PASS |

**Total Effort**: 8.5 hours
**All tasks comply with time-boxing rules** (DP-001 through DP-006)

---

## Acceptance Criteria Mapping

| AC | Description | Mapped To |
|----|-------------|-----------|
| AC1 | Migration creates metadata TEXT column with DEFAULT '{}' | Task 549 |
| AC2 | Migration is idempotent (checks if column exists) | Tasks 548, 549, 550 |
| AC3 | All existing agents retain data after migration | Task 550 |
| AC4 | Migration 0029 runs successfully without errors | Tasks 549, 550 |
| AC5 | `apm status` executes without schema errors | Task 551 |

**All acceptance criteria covered** ✅

---

## Risk Mitigation Plans

### Risk 1: Data Loss During Migration
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Migration 0027 includes idempotency check (PRAGMA table_info)
- ALTER TABLE ADD COLUMN is non-destructive
- Integration test verifies data preservation (Task 550)
- Migration includes downgrade() function for rollback

**Monitoring**: Task 550 integration test validates data integrity

---

### Risk 2: Migration Ordering Issues
**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- Task 548 validates migration dependencies
- Migration 0027 must run after 0020, before 0029
- MigrationManager enforces sequential execution
- Integration test validates full sequence (Task 550)

**Monitoring**: Task 548 analysis verifies correct ordering

---

### Risk 3: Idempotency Failure
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Migration uses PRAGMA table_info to check column existence
- Task 550 specifically tests idempotency
- Can run migration multiple times safely
- Early exit if column already exists

**Monitoring**: Task 550 tests multiple migration runs

---

### Risk 4: Schema Mismatch in Production
**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- Task 551 validates CLI commands work correctly
- Comprehensive testing before deployment
- Migration includes rollback capability
- Documentation updated with troubleshooting (Task 552)

**Monitoring**: Task 551 CLI command verification

---

## Agent Assignments

| Task | Agent Role | Rationale |
|------|-----------|-----------|
| 548 | aipm-database-developer | Database schema analysis expertise |
| 549 | aipm-database-developer | Migration implementation expertise |
| 550 | aipm-testing-specialist | Integration testing expertise |
| 551 | aipm-testing-specialist | CLI testing expertise |
| 552 | aipm-documentation-specialist | Documentation expertise |

---

## Quality Gates

### P1 Gate (Planning) - ✅ PASSED

- ✅ Tasks decomposed with clear objectives (5 tasks)
- ✅ All tasks within time-box limits
- ✅ Dependencies explicitly mapped
- ✅ Estimates align with acceptance criteria
- ✅ Agent assignments appropriate
- ✅ Risk mitigations planned
- ✅ Follows BUGFIX workflow (WR-003: ANALYSIS+FIX+TEST)

### I1 Gate Requirements (Next Phase)

Will require:
- All implementation tasks completed
- All testing tasks passing
- Test coverage ≥90% (TEST-023)
- Documentation updated
- No regressions in CLI commands

---

## Next Steps

1. **Submit to Implementation Orchestrator** for task execution
2. **Start with Task 548** (analysis) - no blockers
3. **Sequential execution** through Task 552
4. **Validate I1 gate** after all tasks complete
5. **Advance to R1 Review** for quality validation

---

## Appendix: Migration Details

### Migration 0020 Issue
- Recreated agents table to fix tier column
- **Omitted metadata column** (original schema had it)
- Line 307-326 in migration_0020.py

### Migration 0027 Fix
- Adds metadata TEXT column with DEFAULT '{}'
- Includes idempotency check (PRAGMA table_info)
- Line 38-41 in migration_0027.py

### Migration 0029 Dependency
- Inserts 5 new utility agents
- Line 180: Uses metadata field in INSERT statement
- **Requires migration 0027 to run first**

---

**Plan Validated By**: Planning Orchestrator
**P1 Gate Status**: ✅ PASS
**Ready for Implementation**: YES
**Estimated Completion**: 8.5 hours (sequential)
