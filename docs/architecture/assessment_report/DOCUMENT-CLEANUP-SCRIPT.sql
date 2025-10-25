-- Document Database Cleanup Script
-- Generated: 2025-10-19
-- Purpose: Remove orphaned and invalid records from document_references table

-- ============================================================================
-- BACKUP FIRST!
-- ============================================================================
-- Before running this script, create a backup:
-- cp .agentpm/data/agentpm.db .agentpm/data/agentpm.db.backup-2025-10-19

-- ============================================================================
-- SECTION 1: Remove Missing Files (14 records)
-- ============================================================================
-- These files are tracked in database but do not exist on filesystem

-- Root-level files (missing)
DELETE FROM document_references WHERE id = 26;  -- O1-DEPLOYMENT-ARTIFACT-v0.1.1.md
DELETE FROM document_references WHERE id = 22;  -- R1-GATE-VALIDATION-REPORT.md
DELETE FROM document_references WHERE id = 69;  -- bad.md

-- Architecture documentation (missing)
DELETE FROM document_references WHERE id = 28;  -- docs/architecture/architecture/DOCUMENTATION-SYNTHESIS.md

-- Specification documentation (missing)
DELETE FROM document_references WHERE id = 2;   -- docs/architecture/specification/future-document.md

-- Technical specification (missing - also Python file)
DELETE FROM document_references WHERE id = 34;  -- docs/architecture/technical_specification/document.py

-- Artifacts (missing)
DELETE FROM document_references WHERE id = 4;   -- docs/artifacts/analysis/test-suite-analysis.md

-- Components documentation (missing)
DELETE FROM document_references WHERE id = 30;  -- docs/components/documents/FINAL-DOCUMENT-SYSTEM-DECISION.md
DELETE FROM document_references WHERE id = 29;  -- docs/components/documents/claude-final.md
DELETE FROM document_references WHERE id = 27;  -- docs/components/documents/claude-recommends.md

-- Testing documentation (missing)
DELETE FROM document_references WHERE id = 13;  -- docs/testing/test_plan/TEST_SUMMARY_INIT.md
DELETE FROM document_references WHERE id = 3;   -- docs/testing/test_plan/test-plan.md
DELETE FROM document_references WHERE id = 12;  -- docs/testing/test_plan/test_init_comprehensive.py (also Python)

-- E2E testing (missing)
DELETE FROM document_references WHERE id = 6;   -- testing/cli-e2e-test/E2E_TEST_REPORT.md

-- ============================================================================
-- SECTION 2: Remove Python Files (13 records - some overlap with Section 1)
-- ============================================================================
-- Python files should not be tracked as documentation

-- Architecture Python files
DELETE FROM document_references WHERE id = 37;  -- docs/architecture/architecture/event.py
DELETE FROM document_references WHERE id = 38;  -- docs/architecture/architecture/event_bus.py
DELETE FROM document_references WHERE id = 36;  -- docs/architecture/architecture/session.py

-- Implementation plan Python files
DELETE FROM document_references WHERE id = 47;  -- docs/architecture/implementation_plan/registry.py

-- Specification Python files
DELETE FROM document_references WHERE id = 39;  -- docs/architecture/specification/__init__.py

-- Technical specification Python files (ID 34 already deleted in Section 1)
DELETE FROM document_references WHERE id = 14;  -- docs/architecture/technical_specification/migration_0027.py
DELETE FROM document_references WHERE id = 33;  -- docs/architecture/technical_specification/migration_0031_documentation_system.py

-- Test plan Python files (ID 12 already deleted in Section 1)
DELETE FROM document_references WHERE id = 11;  -- docs/testing/test_plan/conftest.py
DELETE FROM document_references WHERE id = 9;   -- docs/testing/test_plan/test_migration_0027.py
DELETE FROM document_references WHERE id = 10;  -- docs/testing/test_plan/test_migration_sequence.py

-- Tests Python files
DELETE FROM document_references WHERE id = 17;  -- tests/cli/commands/test_init_comprehensive.py

-- ============================================================================
-- SECTION 3: Remove Template Files (1 record)
-- ============================================================================
-- Jinja2 templates are code, not documentation

DELETE FROM document_references WHERE id = 48;  -- docs/architecture/implementation_plan/agent_file.md.j2

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Count remaining records
SELECT 'Remaining records:' as check_type, COUNT(*) as count FROM document_references;

-- Show remaining records by entity type
SELECT 'By entity type:' as check_type, entity_type, COUNT(*) as count
FROM document_references
GROUP BY entity_type
ORDER BY count DESC;

-- Show remaining records by document type
SELECT 'By document type:' as check_type, document_type, COUNT(*) as count
FROM document_references
GROUP BY document_type
ORDER BY count DESC;

-- Show any remaining Python files (should be 0)
SELECT 'Python files remaining (should be 0):' as check_type, COUNT(*) as count
FROM document_references
WHERE file_path LIKE '%.py';

-- Show any remaining template files (should be 0)
SELECT 'Template files remaining (should be 0):' as check_type, COUNT(*) as count
FROM document_references
WHERE file_path LIKE '%.j2';

-- Show root-level files (CHANGELOG.md should remain)
SELECT 'Root-level files:' as check_type, file_path
FROM document_references
WHERE file_path NOT LIKE 'docs/%'
AND file_path NOT LIKE 'tests/%'
AND file_path NOT LIKE 'testing/%'
AND file_path NOT LIKE 'agentpm/%';

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- Total records to delete: 28 (some overlap between sections)
-- Unique IDs to delete:
--   Section 1 (missing): 26, 22, 69, 28, 2, 34, 4, 30, 29, 27, 13, 3, 12, 6 (14 records)
--   Section 2 (Python): 37, 38, 36, 47, 39, 14, 33, 11, 9, 10, 17 (11 new + 2 overlap)
--   Section 3 (templates): 48 (1 record)
--
-- Starting records: 76
-- Records to delete: 26 unique IDs
-- Expected remaining: 50 records
-- ============================================================================

-- ============================================================================
-- EXECUTION INSTRUCTIONS
-- ============================================================================
-- 1. Create backup: cp .agentpm/data/agentpm.db .agentpm/data/agentpm.db.backup-2025-10-19
-- 2. Run this script: sqlite3 .agentpm/data/agentpm.db < DOCUMENT-CLEANUP-SCRIPT.sql
-- 3. Verify results with verification queries above
-- 4. If issues found, restore backup: cp .agentpm/data/agentpm.db.backup-2025-10-19 .agentpm/data/agentpm.db
-- ============================================================================
