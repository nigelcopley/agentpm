-- Category Alignment Migration Queries
-- Generated: 2025-10-19
-- Purpose: Fix document category misalignments identified in analysis

-- ==============================================================================
-- PRIORITY 1: CRITICAL - Delete Code Files from Document Registry
-- ==============================================================================

-- Preview code files to be deleted
SELECT id, file_path, document_type, category
FROM document_references
WHERE file_path LIKE '%.py' 
   OR file_path LIKE '%.j2'
   OR file_path = 'bad.md'
ORDER BY file_path;

-- Delete code files (11 documents)
-- UNCOMMENT TO EXECUTE:
-- DELETE FROM document_references WHERE file_path LIKE '%.py';
-- DELETE FROM document_references WHERE file_path LIKE '%.j2';
-- DELETE FROM document_references WHERE file_path = 'bad.md';

-- ==============================================================================
-- PRIORITY 2: HIGH - Reorganize Architecture Category
-- ==============================================================================

-- Move completion reports to communication/status_report
-- Preview:
SELECT id, file_path, document_type, 
       REPLACE(file_path, 'architecture/specification', 'communication/status_report') as new_path
FROM document_references
WHERE file_path LIKE '%architecture/specification/WI-%COMPLETION%'
   OR file_path LIKE '%architecture/specification/WI-%AUDIT%'
   OR file_path LIKE '%architecture/specification/WI-%SUMMARY%'
   OR file_path LIKE '%architecture/specification/TASK-%COMPLETION%';

-- Update (8 documents):
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references 
-- SET file_path = REPLACE(file_path, 'architecture/specification', 'communication/status_report'),
--     category = 'communication',
--     document_type = 'status_report'
-- WHERE file_path LIKE '%architecture/specification/WI-%COMPLETION%'
--    OR file_path LIKE '%architecture/specification/WI-%AUDIT%'
--    OR file_path LIKE '%architecture/specification/WI-%SUMMARY%'
--    OR file_path LIKE '%architecture/specification/TASK-%COMPLETION%';

-- Move implementation plans to planning
-- Preview:
SELECT id, file_path, document_type,
       REPLACE(file_path, 'architecture/implementation_plan', 'planning/project_plan') as new_path
FROM document_references
WHERE file_path LIKE '%architecture/implementation_plan/PLAN-%'
  AND file_path LIKE '%.md';

-- Update (2 documents):
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references
-- SET file_path = REPLACE(file_path, 'architecture/implementation_plan', 'planning/project_plan'),
--     category = 'planning',
--     document_type = 'project_plan'
-- WHERE file_path LIKE '%architecture/implementation_plan/PLAN-%'
--   AND file_path LIKE '%.md';

-- ==============================================================================
-- PRIORITY 2: HIGH - Consolidate Runbooks
-- ==============================================================================

-- Move runbooks to operations/runbook
-- Preview:
SELECT id, file_path, document_type,
       CASE 
         WHEN file_path = 'CHANGELOG.md' THEN 'docs/operations/runbook/CHANGELOG.md'
         WHEN file_path = 'O1-DEPLOYMENT-ARTIFACT-v0.1.1.md' THEN 'docs/operations/runbook/O1-DEPLOYMENT-ARTIFACT-v0.1.1.md'
         WHEN file_path LIKE 'docs/guides/runbook/%' THEN REPLACE(file_path, 'docs/guides/runbook', 'docs/operations/runbook')
         ELSE file_path
       END as new_path
FROM document_references
WHERE document_type = 'runbook';

-- Update (5 documents):
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references
-- SET file_path = 'docs/operations/runbook/CHANGELOG.md',
--     category = 'operations'
-- WHERE file_path = 'CHANGELOG.md';

-- UPDATE document_references
-- SET file_path = 'docs/operations/runbook/O1-DEPLOYMENT-ARTIFACT-v0.1.1.md',
--     category = 'operations'
-- WHERE file_path = 'O1-DEPLOYMENT-ARTIFACT-v0.1.1.md';

-- UPDATE document_references
-- SET file_path = REPLACE(file_path, 'docs/guides/runbook', 'docs/operations/runbook'),
--     category = 'operations'
-- WHERE file_path LIKE 'docs/guides/runbook/%';

-- ==============================================================================
-- PRIORITY 2: HIGH - Fix Testing Category
-- ==============================================================================

-- Move test reports to testing/test_report
-- Preview:
SELECT id, file_path, document_type,
       REPLACE(file_path, 'testing/other', 'testing/test_report') as new_path
FROM document_references
WHERE file_path LIKE '%testing/other/%REPORT%'
  AND file_path LIKE '%.md';

-- Update:
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references
-- SET file_path = REPLACE(file_path, 'testing/other', 'testing/test_report'),
--     document_type = 'test_report'
-- WHERE file_path LIKE '%testing/other/%REPORT%'
--   AND file_path LIKE '%.md';

-- Move audit reports to communication
-- Preview:
SELECT id, file_path, document_type,
       REPLACE(file_path, 'testing/test_plan', 'communication/status_report') as new_path
FROM document_references
WHERE file_path LIKE '%testing/test_plan/WI-%AUDIT%';

-- Update:
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references
-- SET file_path = REPLACE(file_path, 'testing/test_plan', 'communication/status_report'),
--     category = 'communication',
--     document_type = 'status_report'
-- WHERE file_path LIKE '%testing/test_plan/WI-%AUDIT%';

-- ==============================================================================
-- PRIORITY 3: MEDIUM - Refine Document Types
-- ==============================================================================

-- Update "other" types to specific types in communication
-- Preview:
SELECT id, file_path, document_type,
       CASE
         WHEN file_path LIKE '%SESSION-SUMMARY%' THEN 'status_report'
         WHEN file_path LIKE '%AUDIT%' THEN 'status_report'
         WHEN file_path LIKE '%SUMMARY%' THEN 'status_report'
         WHEN file_path LIKE '%REPORT%' THEN 'status_report'
         ELSE document_type
       END as new_type
FROM document_references
WHERE category = 'communication' 
  AND document_type = 'other';

-- Update (7 documents):
-- UNCOMMENT TO EXECUTE:
-- UPDATE document_references
-- SET document_type = CASE
--       WHEN file_path LIKE '%SESSION-SUMMARY%' THEN 'status_report'
--       WHEN file_path LIKE '%AUDIT%' THEN 'status_report'
--       WHEN file_path LIKE '%SUMMARY%' THEN 'status_report'
--       WHEN file_path LIKE '%REPORT%' THEN 'status_report'
--       ELSE document_type
--     END
-- WHERE category = 'communication' 
--   AND document_type = 'other';

-- ==============================================================================
-- VALIDATION QUERIES
-- ==============================================================================

-- Count documents by category (after migration)
SELECT category, COUNT(*) as count
FROM document_references
GROUP BY category
ORDER BY category;

-- Count documents by type (after migration)
SELECT document_type, COUNT(*) as count
FROM document_references
GROUP BY document_type
ORDER BY document_type;

-- Find any remaining misalignments
SELECT id, file_path, category, document_type
FROM document_references
WHERE (category = '' OR category IS NULL)
   OR (file_path LIKE '%.py')
   OR (file_path LIKE '%.j2')
   OR (file_path = 'bad.md')
ORDER BY category, file_path;

-- Category-type alignment check
SELECT category, document_type, COUNT(*) as count
FROM document_references
GROUP BY category, document_type
ORDER BY category, count DESC;

-- Expected final counts:
-- Total documents: 69 (after removing 11 code files)
-- Categories: 9 (architecture, communication, guides, operations, planning, testing, governance, processes, reference)
-- All documents should have non-empty category
-- No .py or .j2 files should remain

-- ==============================================================================
-- CLEANUP VERIFICATION
-- ==============================================================================

-- Verify no code files remain
SELECT COUNT(*) as code_files_remaining
FROM document_references
WHERE file_path LIKE '%.py' OR file_path LIKE '%.j2';
-- Expected: 0

-- Verify no uncategorized documents
SELECT COUNT(*) as uncategorized_documents
FROM document_references
WHERE category = '' OR category IS NULL;
-- Expected: 0 (after WI-113 migration)

-- Verify category distribution
SELECT 
  category,
  COUNT(*) as total_docs,
  GROUP_CONCAT(DISTINCT document_type) as doc_types
FROM document_references
GROUP BY category
ORDER BY total_docs DESC;

-- ==============================================================================
-- END OF MIGRATION QUERIES
-- ==============================================================================
