-- Document Compliance Analysis Queries
-- Database: .aipm/data/aipm.db
-- Table: document_references
-- Generated: 2025-10-19

-- ============================================================================
-- QUICK COMPLIANCE CHECK
-- ============================================================================

-- Overall compliance summary
SELECT
    COUNT(*) as total_documents,
    SUM(CASE WHEN file_path LIKE 'docs/%' THEN 1 ELSE 0 END) as compliant,
    SUM(CASE WHEN file_path NOT LIKE 'docs/%' THEN 1 ELSE 0 END) as non_compliant,
    ROUND(100.0 * SUM(CASE WHEN file_path LIKE 'docs/%' THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_rate
FROM document_references;

-- ============================================================================
-- NON-COMPLIANT DOCUMENTS (DETAILED)
-- ============================================================================

-- All documents outside docs/ hierarchy
SELECT
    id,
    file_path,
    document_type,
    entity_type,
    entity_id,
    created_at,
    CASE
        WHEN file_path = 'bad.md' THEN 'DELETE - test file'
        WHEN file_path LIKE '%.py' THEN 'REMOVE_FROM_DB - source code'
        WHEN file_path LIKE 'tests/%' THEN 'MOVE to docs/testing/'
        WHEN file_path LIKE 'testing/%' THEN 'MOVE to docs/testing/'
        WHEN file_path LIKE 'agentpm/%' THEN 'MOVE to docs/guides/'
        ELSE 'MOVE to docs/'
    END as recommended_action
FROM document_references
WHERE file_path NOT LIKE 'docs/%'
ORDER BY
    CASE
        WHEN file_path = 'bad.md' THEN 1
        WHEN file_path LIKE '%.py' THEN 2
        ELSE 3
    END,
    file_path;

-- ============================================================================
-- DOCUMENT TYPE DISTRIBUTION
-- ============================================================================

-- Count by document type with compliance breakdown
SELECT
    document_type,
    COUNT(*) as total,
    SUM(CASE WHEN file_path LIKE 'docs/%' THEN 1 ELSE 0 END) as compliant,
    SUM(CASE WHEN file_path NOT LIKE 'docs/%' THEN 1 ELSE 0 END) as non_compliant,
    ROUND(100.0 * SUM(CASE WHEN file_path LIKE 'docs/%' THEN 1 ELSE 0 END) / COUNT(*), 1) as compliance_pct
FROM document_references
GROUP BY document_type
ORDER BY total DESC;

-- ============================================================================
-- CATEGORY DISTRIBUTION
-- ============================================================================

-- Documents by top-level category under docs/
SELECT
    CASE
        WHEN file_path LIKE 'docs/%'
        THEN SUBSTR(file_path, 6, INSTR(SUBSTR(file_path, 6) || '/', '/') - 1)
        ELSE 'NON-COMPLIANT'
    END as category,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM document_references), 1) as percentage
FROM document_references
GROUP BY category
ORDER BY count DESC;

-- ============================================================================
-- TYPE-TO-LOCATION MAPPING ANALYSIS
-- ============================================================================

-- Check if document types are in their expected locations
WITH expected_locations AS (
    SELECT 'specification' as doc_type, 'docs/architecture/specification/' as expected_path UNION ALL
    SELECT 'architecture', 'docs/architecture/architecture/' UNION ALL
    SELECT 'implementation_plan', 'docs/planning/implementation_plan/' UNION ALL
    SELECT 'test_plan', 'docs/testing/test_plan/' UNION ALL
    SELECT 'user_guide', 'docs/guides/user_guide/' UNION ALL
    SELECT 'runbook', 'docs/guides/runbook/' UNION ALL
    SELECT 'requirements', 'docs/planning/requirements/' UNION ALL
    SELECT 'quality_gates_specification', 'docs/governance/quality_gates_specification/' UNION ALL
    SELECT 'adr', 'docs/architecture/adr/' UNION ALL
    SELECT 'design', 'docs/architecture/design/' UNION ALL
    SELECT 'technical_specification', 'docs/architecture/technical_specification/'
)
SELECT
    dr.document_type,
    COUNT(*) as total,
    SUM(CASE WHEN dr.file_path LIKE el.expected_path || '%' THEN 1 ELSE 0 END) as in_expected_location,
    SUM(CASE WHEN dr.file_path NOT LIKE el.expected_path || '%' THEN 1 ELSE 0 END) as in_wrong_location,
    ROUND(100.0 * SUM(CASE WHEN dr.file_path LIKE el.expected_path || '%' THEN 1 ELSE 0 END) / COUNT(*), 1) as compliance_pct
FROM document_references dr
LEFT JOIN expected_locations el ON dr.document_type = el.doc_type
WHERE dr.document_type != 'other'
GROUP BY dr.document_type
ORDER BY in_wrong_location DESC, total DESC;

-- ============================================================================
-- DOCUMENTS WITH 'other' TYPE (NEEDS CLASSIFICATION)
-- ============================================================================

-- All documents typed as 'other' - candidates for reclassification
SELECT
    id,
    file_path,
    entity_type,
    entity_id,
    created_at,
    CASE
        WHEN file_path LIKE '%SUMMARY%' THEN 'SUGGEST: specification or requirements'
        WHEN file_path LIKE '%REPORT%' THEN 'SUGGEST: specification or architecture'
        WHEN file_path LIKE '%PROGRESS%' THEN 'SUGGEST: requirements or specification'
        WHEN file_path LIKE '%SESSION%' THEN 'SUGGEST: runbook or requirements'
        WHEN file_path LIKE '%DELEGATION%' THEN 'SUGGEST: implementation_plan'
        ELSE 'NEEDS_MANUAL_REVIEW'
    END as suggested_type
FROM document_references
WHERE document_type = 'other'
ORDER BY file_path;

-- ============================================================================
-- ENTITY LINKAGE ANALYSIS
-- ============================================================================

-- Distribution by entity type
SELECT
    entity_type,
    COUNT(*) as document_count,
    COUNT(DISTINCT entity_id) as unique_entities,
    ROUND(1.0 * COUNT(*) / COUNT(DISTINCT entity_id), 2) as avg_docs_per_entity
FROM document_references
GROUP BY entity_type
ORDER BY document_count DESC;

-- Work items with most documentation
SELECT
    entity_id as work_item_id,
    COUNT(*) as document_count,
    GROUP_CONCAT(DISTINCT document_type) as document_types
FROM document_references
WHERE entity_type = 'work_item'
GROUP BY entity_id
HAVING COUNT(*) >= 3
ORDER BY document_count DESC;

-- ============================================================================
-- LOCATION DEPTH ANALYSIS
-- ============================================================================

-- Check directory depth (should be docs/category/type/filename.md)
SELECT
    file_path,
    document_type,
    LENGTH(file_path) - LENGTH(REPLACE(file_path, '/', '')) as depth,
    CASE
        WHEN file_path NOT LIKE 'docs/%' THEN 'NON-COMPLIANT: Not in docs/'
        WHEN LENGTH(file_path) - LENGTH(REPLACE(file_path, '/', '')) < 2 THEN 'SHALLOW: Missing subcategory'
        WHEN LENGTH(file_path) - LENGTH(REPLACE(file_path, '/', '')) = 2 THEN 'OPTIMAL: docs/category/file'
        WHEN LENGTH(file_path) - LENGTH(REPLACE(file_path, '/', '')) = 3 THEN 'OPTIMAL: docs/category/type/file'
        ELSE 'DEEP: May be over-nested'
    END as depth_assessment
FROM document_references
ORDER BY depth, file_path;

-- ============================================================================
-- MIGRATION PRIORITY QUERY
-- ============================================================================

-- Documents to migrate, ordered by priority
SELECT
    CASE
        WHEN file_path = 'bad.md' THEN 1
        WHEN file_path LIKE '%.py' THEN 2
        WHEN file_path NOT LIKE 'docs/%' THEN 3
        WHEN document_type = 'other' THEN 4
        WHEN file_path LIKE 'docs/components/%' THEN 5
        ELSE 6
    END as priority,
    id,
    file_path,
    document_type,
    entity_type,
    entity_id,
    CASE
        WHEN file_path = 'bad.md' THEN 'DELETE FILE'
        WHEN file_path LIKE '%.py' THEN 'REMOVE FROM document_references'
        WHEN file_path = 'CHANGELOG.md' THEN 'MOVE to docs/guides/runbook/CHANGELOG.md'
        WHEN file_path = 'O1-DEPLOYMENT-ARTIFACT-v0.1.1.md' THEN 'MOVE to docs/operations/runbook/O1-DEPLOYMENT-ARTIFACT-v0.1.1.md'
        WHEN file_path = 'R1-GATE-VALIDATION-REPORT.md' THEN 'MOVE to docs/governance/quality_gates_specification/R1-GATE-VALIDATION-REPORT.md'
        WHEN file_path = 'agentpm/web/README.md' THEN 'MOVE to docs/guides/user_guide/web-admin-guide.md'
        WHEN file_path LIKE 'testing/%' THEN 'MOVE to docs/testing/test_plan/' || SUBSTR(file_path, INSTR(file_path, '/') + 1)
        WHEN file_path LIKE 'tests/%' THEN 'MOVE to docs/testing/test_plan/' || REPLACE(file_path, 'tests/cli/commands/', '')
        WHEN document_type = 'other' THEN 'RECLASSIFY document_type'
        WHEN file_path LIKE 'docs/components/%' THEN 'CONSIDER REDISTRIBUTION to primary category'
        ELSE 'REVIEW'
    END as action
FROM document_references
WHERE
    priority <= 5
ORDER BY priority, file_path;

-- ============================================================================
-- DUPLICATE PATH DETECTION
-- ============================================================================

-- Check for duplicate file paths (data integrity)
SELECT
    file_path,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(id) as document_ids
FROM document_references
GROUP BY file_path
HAVING COUNT(*) > 1;

-- ============================================================================
-- RECENT ADDITIONS (COMPLIANCE TRACKING)
-- ============================================================================

-- Documents added in last 24 hours with compliance status
SELECT
    id,
    file_path,
    document_type,
    CASE
        WHEN file_path LIKE 'docs/%' THEN 'COMPLIANT'
        ELSE 'NON-COMPLIANT'
    END as compliance_status,
    created_at,
    created_by
FROM document_references
WHERE created_at >= datetime('now', '-1 day')
ORDER BY created_at DESC;

-- ============================================================================
-- ORPHANED DOCUMENTS (ENTITIES MAY NOT EXIST)
-- ============================================================================

-- This query would need to be run with JOINs to work_items/tasks tables
-- Placeholder for when cross-table validation is needed
SELECT
    dr.id,
    dr.file_path,
    dr.entity_type,
    dr.entity_id,
    'NEEDS_VALIDATION' as status
FROM document_references dr
WHERE dr.entity_type IN ('work_item', 'task', 'idea')
-- AND NOT EXISTS (SELECT 1 FROM work_items wi WHERE wi.id = dr.entity_id AND dr.entity_type = 'work_item')
-- Uncomment above when running with full schema
ORDER BY dr.entity_type, dr.entity_id;

-- ============================================================================
-- SUMMARY VIEW (CREATE AS VIEW FOR REGULAR MONITORING)
-- ============================================================================

-- Comprehensive compliance dashboard
CREATE TEMP VIEW IF NOT EXISTS document_compliance_summary AS
SELECT
    (SELECT COUNT(*) FROM document_references) as total_documents,
    (SELECT COUNT(*) FROM document_references WHERE file_path LIKE 'docs/%') as compliant_location,
    (SELECT COUNT(*) FROM document_references WHERE file_path NOT LIKE 'docs/%') as non_compliant_location,
    (SELECT COUNT(*) FROM document_references WHERE document_type = 'other') as needs_classification,
    (SELECT COUNT(DISTINCT document_type) FROM document_references) as unique_types,
    (SELECT COUNT(DISTINCT SUBSTR(file_path, 6, INSTR(SUBSTR(file_path, 6) || '/', '/') - 1))
     FROM document_references WHERE file_path LIKE 'docs/%') as unique_categories,
    ROUND(100.0 * (SELECT COUNT(*) FROM document_references WHERE file_path LIKE 'docs/%') /
          (SELECT COUNT(*) FROM document_references), 2) as compliance_percentage;

-- Query the summary
SELECT * FROM document_compliance_summary;
