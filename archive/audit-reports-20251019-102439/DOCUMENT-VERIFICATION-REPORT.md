# Document Database Verification Report

**Date**: 2025-10-19
**Database**: /Users/nigelcopley/.project_manager/aipm-v2/.aipm/data/aipm.db
**Table**: document_references

---

## Executive Summary

**Database Status**: 76 document records tracked
**Filesystem Status**: 295 markdown files found in docs/
**Verification Results**:
- Files found on filesystem: **62** (81.6%)
- Files MISSING from filesystem: **14** (18.4%)
- Untracked files (exist but not in DB): **250**

---

## Critical Findings

### 1. Missing Files (In Database but Not on Disk)

The following 14 files are tracked in the database but do NOT exist on the filesystem:

#### **Root-level files (3)**
1. `O1-DEPLOYMENT-ARTIFACT-v0.1.1.md` (ID: 26, entity: work_item 109, type: runbook)
2. `R1-GATE-VALIDATION-REPORT.md` (ID: 22, entity: work_item 109, type: requirements)
3. `bad.md` (ID: 69, entity: project 1, type: other)

**Status**: These files were likely moved to docs/ subdirectories or deleted. Root-level documents should be tracked in `docs/` instead.

#### **Architecture Documentation (1)**
4. `docs/architecture/architecture/DOCUMENTATION-SYNTHESIS.md` (ID: 28, entity: project 1, type: architecture)

#### **Specification Documentation (1)**
5. `docs/architecture/specification/future-document.md` (ID: 2, entity: work_item 1, type: specification)

#### **Technical Specification (1)**
6. `docs/architecture/technical_specification/document.py` (ID: 34, entity: work_item 112, type: technical_specification)

**Note**: This is a Python file, not markdown. Should not be tracked as documentation.

#### **Artifacts (1)**
7. `docs/artifacts/analysis/test-suite-analysis.md` (ID: 4, entity: idea 45, type: technical_specification)

#### **Components Documentation (3)**
8. `docs/components/documents/FINAL-DOCUMENT-SYSTEM-DECISION.md` (ID: 30, entity: project 1, type: architecture)
9. `docs/components/documents/claude-final.md` (ID: 29, entity: project 1, type: technical_specification)
10. `docs/components/documents/claude-recommends.md` (ID: 27, entity: project 1, type: design)

#### **Testing Documentation (3)**
11. `docs/testing/test_plan/TEST_SUMMARY_INIT.md` (ID: 13, entity: task 554, type: test_plan)
12. `docs/testing/test_plan/test-plan.md` (ID: 3, entity: work_item 1, type: test_plan)
13. `docs/testing/test_plan/test_init_comprehensive.py` (ID: 12, entity: task 554, type: test_plan)

**Note**: Item 13 is a Python file, not documentation.

#### **E2E Testing (1)**
14. `testing/cli-e2e-test/E2E_TEST_REPORT.md` (ID: 6, entity: work_item 109, type: requirements)

**Status**: This directory exists but the specific file does not.

---

### 2. Untracked Files (On Disk but Not in Database)

**Total**: 250 markdown files exist in docs/ but are NOT tracked in the database.

#### **Critical Untracked Documentation Categories**:

**ADRs (Architecture Decision Records)** - 16 files:
- `docs/adrs/ADR-001-provider-abstraction-architecture.md`
- `docs/adrs/ADR-002-context-compression-strategy.md`
- `docs/adrs/ADR-003-sub-agent-communication-protocol.md`
- `docs/adrs/ADR-004-evidence-storage-and-retrieval.md`
- `docs/adrs/ADR-006-document-store-and-knowledge-management.md`
- `docs/adrs/ADR-007-human-in-the-loop-workflows.md`
- `docs/adrs/ADR-008-data-privacy-and-security.md`
- `docs/adrs/ADR-009-event-system-and-integrations.md`
- `docs/adrs/ADR-010-dependency-management-and-scheduling.md`
- `docs/adrs/ADR-011-cost-tracking-and-resource-management.md`
- `docs/adrs/ADR-012-pyramid-of-software-development-principles.md`
- `docs/adrs/ADR-013-comprehensive-impact-analysis-workflow.md`
- `docs/adrs/ADR-014-phase-status-relationship.md`
- `docs/06-decisions/ADR-000-documentation-system-architecture.md`
- `docs/adrs/README.md`
- `docs/decisions/README.md`

**Agent Documentation** - 4 files:
- `docs/AGENTS.md`
- `docs/agents/AGENT-UNIVERSAL-RULES-UPDATE-REPORT.md`
- `docs/agents/UNIVERSAL-AGENT-RULES.md`
- `docs/agents/UNIVERSAL-RULES-QUICK-REFERENCE.md`

**Core Documentation** - 6 files:
- `docs/CLAUDE.md`
- `docs/aipm/README.md`
- `docs/aipm/documentation-guidelines.md`
- `docs/architecture/README.md`
- `docs/components/README.md`
- `docs/features/README.md`

**Analysis Documents** - ~80 files in `docs/analysis/`:
- System reviews, agent analysis, database analysis, integration analysis
- Strategic planning documents
- Technical deep-dives
- Component subsystem architectures

**User Guides** - 10 files:
- `docs/user-guides/01-getting-started.md`
- `docs/user-guides/02-quick-reference.md`
- `docs/user-guides/03-cli-commands.md`
- `docs/user-guides/04-phase-workflow.md`
- `docs/user-guides/05-troubleshooting.md`
- `docs/user-guides/README.md`
- Plus additional specialized guides

**Developer Guides** - 3 files:
- `docs/developer-guide/01-architecture-overview.md`
- `docs/developer-guide/02-three-layer-pattern.md`
- `docs/developer-guide/03-contributing.md`

**Reports** - ~30 files in `docs/reports/`:
- Audit reports, completion summaries, health assessments
- Migration summaries, workflow analysis

**Specifications** - 8 files in `docs/specifications/`:
- Complete system specifications
- Impact analysis specifications
- Executive summaries

**Work Items Documentation** - ~15 files in `docs/work-items/`:
- Design documents for specific work items
- Implementation plans and analysis

---

### 3. Path Validation Issues

**Non-Markdown Files in Database**:
1. `docs/architecture/architecture/event.py` (ID: 37)
2. `docs/architecture/architecture/event_bus.py` (ID: 38)
3. `docs/architecture/architecture/session.py` (ID: 36)
4. `docs/architecture/implementation_plan/registry.py` (ID: 47)
5. `docs/architecture/specification/__init__.py` (ID: 39)
6. `docs/architecture/technical_specification/document.py` (ID: 34)
7. `docs/architecture/technical_specification/migration_0027.py` (ID: 14)
8. `docs/architecture/technical_specification/migration_0031_documentation_system.py` (ID: 33)
9. `docs/testing/test_plan/conftest.py` (ID: 11)
10. `docs/testing/test_plan/test_init_comprehensive.py` (ID: 12)
11. `docs/testing/test_plan/test_migration_0027.py` (ID: 9)
12. `docs/testing/test_plan/test_migration_sequence.py` (ID: 10)
13. `tests/cli/commands/test_init_comprehensive.py` (ID: 17)

**Issue**: 13 Python files are incorrectly tracked as documentation. These should be removed from document_references table.

**YAML Files in Database**:
1. `docs/planning/implementation_plan/wi-113-p1-gate-validation.yaml` (ID: 66)
2. `docs/planning/implementation_plan/wi-113-plan-snapshot.yaml` (ID: 65)

**Status**: YAML files can be valid documentation but need validation.

**Template Files**:
1. `docs/architecture/implementation_plan/agent_file.md.j2` (ID: 48)

**Status**: Jinja2 templates are code, not documentation. Should be removed.

---

## Database Statistics

**Total Records**: 76

**By Entity Type**:
- work_item: 43 records (56.6%)
- task: 21 records (27.6%)
- project: 7 records (9.2%)
- idea: 1 record (1.3%)

**By Document Type**:
- specification: 10 records
- test_plan: 10 records
- other: 10 records
- architecture: 8 records
- implementation_plan: 7 records
- user_guide: 6 records
- technical_specification: 5 records
- runbook: 5 records
- requirements: 5 records
- quality_gates_specification: 3 records
- design: 2 records
- adr: 1 record

**Top Work Items**:
- WI-113: 10 documents
- WI-109: 5 documents
- WI-108: 4 documents

---

## Recommendations

### Immediate Actions (Priority: CRITICAL)

1. **Clean Up Orphaned Records**
   ```bash
   # Remove 14 missing files from database
   apm document delete <id>  # For each missing file
   ```

2. **Remove Python/Code Files**
   ```bash
   # Remove 13 Python files incorrectly tracked as docs
   # IDs: 37, 38, 36, 47, 39, 34, 14, 33, 11, 12, 9, 10, 17
   ```

3. **Remove Template Files**
   ```bash
   # Remove agent_file.md.j2 (ID: 48)
   ```

### High Priority Actions

4. **Track Core Documentation**
   - Add CLAUDE.md to database (critical system documentation)
   - Add all ADRs (16 files) - architectural decisions must be tracked
   - Add agent documentation (4 files)
   - Add core READMEs (docs/aipm/README.md, docs/architecture/README.md, etc.)

5. **Track User/Developer Guides**
   - Add 10 user guide files
   - Add 3 developer guide files
   - These are user-facing documentation

### Medium Priority Actions

6. **Track Analysis Documents**
   - Review ~80 analysis documents
   - Determine which are current vs historical
   - Track active/reference documents
   - Archive or delete outdated analysis

7. **Track Reports**
   - Review ~30 report files
   - Link to appropriate work items
   - Determine retention policy for historical reports

8. **Track Specifications**
   - Add 8 specification documents
   - Link to appropriate work items/features

### Low Priority Actions

9. **Review YAML Files**
   - Determine if YAML planning documents should be tracked
   - Create policy for non-markdown documentation

10. **Establish Documentation Policies**
    - File type whitelist (markdown only? or include YAML, templates?)
    - Location policies (all docs in docs/ directory)
    - Naming conventions
    - Lifecycle management (when to archive/delete)

---

## Database Integrity Issues

### Root-Level Documents
**Problem**: 3 database records point to root-level files (CHANGELOG.md exists, 2 are missing)
**Solution**: Enforce docs/ path constraint in schema (already exists in code)

### Python Files as Documentation
**Problem**: 13 Python files tracked as documentation
**Solution**: Add format validation to reject .py files

### Missing Directories
**Problem**: Some documents reference non-existent paths
**Solution**: Validate parent directory exists before creating record

---

## Filesystem Statistics

**Total Markdown Files in docs/**: 295
**Tracked in Database**: 62 (21.0%)
**Untracked**: 250 (84.7%)
**Missing from Disk**: 14 (4.7%)

**Coverage Gap**: Only 21% of documentation is tracked in the database.

---

## SQL Cleanup Queries

### Remove Missing Files
```sql
-- Remove 14 orphaned records
DELETE FROM document_references WHERE id IN (
  26, 22, 69, 28, 2, 34, 4, 30, 29, 27, 13, 3, 12, 6
);
```

### Remove Python Files
```sql
-- Remove 13 Python files
DELETE FROM document_references WHERE id IN (
  37, 38, 36, 47, 39, 34, 14, 33, 11, 12, 9, 10, 17
);
```

### Remove Template Files
```sql
-- Remove Jinja2 template
DELETE FROM document_references WHERE id = 48;
```

**Total Records to Remove**: 28 (36.8% of database)
**Remaining Valid Records**: 48

---

## Next Steps

1. **Execute cleanup queries** to remove orphaned and invalid records
2. **Run document migration CLI** to add untracked core documentation
3. **Establish documentation governance** policies
4. **Create automated validation** to prevent future issues
5. **Schedule periodic audits** to maintain database-filesystem sync

---

## Conclusion

The document tracking system has significant integrity issues:

- **18.4% of tracked files are missing** from the filesystem
- **36.8% of database records are invalid** (missing files + code files)
- **84.7% of documentation is untracked** in the database

**Recommended Action**: Execute immediate cleanup, then run comprehensive migration to achieve >90% documentation coverage.

**Estimated Effort**:
- Cleanup: 30 minutes
- Core documentation migration: 2 hours
- Full documentation migration: 4-6 hours
- Policy implementation: 2 hours

**Total**: 8-10 hours to achieve full database-filesystem integrity.
