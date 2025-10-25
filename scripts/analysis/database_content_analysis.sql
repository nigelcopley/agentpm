-- APM (Agent Project Manager) Database Content vs Schema Capability Analysis
-- Generated: 2025-10-16
-- Database: agentpm.db

.mode column
.headers on

-- ===================================================================
-- PART 1: TABLE POPULATION ANALYSIS
-- ===================================================================
SELECT '=== PART 1: TABLE POPULATION ANALYSIS ===' as section;
SELECT '';

SELECT
    'work_items' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT type) as unique_types,
    COUNT(phase) as phase_populated,
    COUNT(CASE WHEN business_context IS NOT NULL AND business_context != '' THEN 1 END) as business_context_filled,
    COUNT(parent_work_item_id) as has_parent,
    ROUND(AVG(CASE WHEN metadata = '{}' THEN 0 ELSE 1 END) * 100, 1) as metadata_usage_pct
FROM work_items;

SELECT
    'tasks' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT type) as unique_types,
    COUNT(assigned_to) as assigned_count,
    COUNT(CASE WHEN quality_metadata IS NOT NULL AND quality_metadata != '' THEN 1 END) as quality_metadata_filled,
    COUNT(effort_hours) as effort_estimated,
    COUNT(blocked_reason) as blocked_tasks
FROM tasks;

SELECT
    'projects' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT name) as unique_names,
    COUNT(tech_stack) as tech_stack_filled,
    0 as col4, 0 as col5, 0 as col6
FROM projects;

SELECT
    'sessions' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(context_snapshot) as context_snapshot_filled,
    0 as col4, 0 as col5, 0 as col6
FROM sessions;

SELECT
    'agents' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT role) as unique_roles,
    COUNT(CASE WHEN active = 1 THEN 1 END) as active_count,
    0 as col4, 0 as col5, 0 as col6
FROM agents;

SELECT
    'contexts' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT context_type) as unique_types,
    COUNT(entity_id) as linked_to_entities,
    COUNT(six_w_data) as six_w_populated,
    COUNT(confidence_score) as confidence_scored,
    0 as col6
FROM contexts;

SELECT
    'task_dependencies' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT dependency_type) as unique_types,
    COUNT(notes) as notes_filled,
    0 as col4, 0 as col5, 0 as col6
FROM task_dependencies;

SELECT
    'work_item_dependencies' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT dependency_type) as unique_types,
    0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM work_item_dependencies;

SELECT
    'session_events' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT event_type) as unique_event_types,
    0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM session_events;

SELECT
    'rules' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT category) as unique_categories,
    COUNT(CASE WHEN active = 1 THEN 1 END) as active_count,
    0 as col4, 0 as col5, 0 as col6
FROM rules;

SELECT
    'document_references' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT entity_type) as unique_entity_types,
    0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM document_references;

SELECT
    'evidence_sources' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT source_type) as unique_source_types,
    COUNT(captured_at) as captured_at_filled,
    0 as col4, 0 as col5, 0 as col6
FROM evidence_sources;

SELECT
    'ideas' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT status) as unique_statuses,
    COUNT(converted_to_work_item_id) as converted_count,
    COUNT(votes) as has_votes,
    0 as col5, 0 as col6
FROM ideas;

SELECT
    'agent_relationships' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT relationship_type) as unique_types,
    0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM agent_relationships;

SELECT
    'agent_tools' as table_name,
    COUNT(*) as total_rows,
    0 as col2, 0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM agent_tools;

SELECT
    'task_blockers' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT blocker_type) as unique_types,
    COUNT(resolved_at) as resolved_count,
    0 as col4, 0 as col5, 0 as col6
FROM task_blockers;

SELECT
    'work_item_summaries' as table_name,
    COUNT(*) as total_rows,
    0 as col2, 0 as col3, 0 as col4, 0 as col5, 0 as col6
FROM work_item_summaries;


-- ===================================================================
-- PART 2: RELATIONSHIP COVERAGE ANALYSIS
-- ===================================================================
SELECT '';
SELECT '=== PART 2: RELATIONSHIP COVERAGE ANALYSIS ===' as section;
SELECT '';

-- Work items with tasks
SELECT
    'work_items → tasks' as relationship,
    COUNT(DISTINCT wi.id) as entities_covered,
    (SELECT COUNT(*) FROM work_items) as total_entities,
    ROUND(COUNT(DISTINCT wi.id) * 100.0 / NULLIF((SELECT COUNT(*) FROM work_items), 0), 2) as coverage_percent
FROM work_items wi
INNER JOIN tasks t ON t.work_item_id = wi.id;

-- Tasks with dependencies
SELECT
    'tasks → dependencies' as relationship,
    COUNT(DISTINCT d.task_id) as entities_covered,
    (SELECT COUNT(*) FROM tasks) as total_entities,
    ROUND(COUNT(DISTINCT d.task_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM tasks), 0), 2) as coverage_percent
FROM task_dependencies d;

-- Work items with dependencies
SELECT
    'work_items → dependencies' as relationship,
    COUNT(DISTINCT d.work_item_id) as entities_covered,
    (SELECT COUNT(*) FROM work_items) as total_entities,
    ROUND(COUNT(DISTINCT d.work_item_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM work_items), 0), 2) as coverage_percent
FROM work_item_dependencies d;

-- Work items with contexts
SELECT
    'work_items → contexts' as relationship,
    COUNT(DISTINCT c.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM work_items) as total_entities,
    ROUND(COUNT(DISTINCT c.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM work_items), 0), 2) as coverage_percent
FROM contexts c
WHERE c.entity_type = 'work_item';

-- Tasks with contexts
SELECT
    'tasks → contexts' as relationship,
    COUNT(DISTINCT c.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM tasks) as total_entities,
    ROUND(COUNT(DISTINCT c.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM tasks), 0), 2) as coverage_percent
FROM contexts c
WHERE c.entity_type = 'task';

-- Work items with document references
SELECT
    'work_items → documents' as relationship,
    COUNT(DISTINCT dr.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM work_items) as total_entities,
    ROUND(COUNT(DISTINCT dr.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM work_items), 0), 2) as coverage_percent
FROM document_references dr
WHERE dr.entity_type = 'work_item';

-- Tasks with document references
SELECT
    'tasks → documents' as relationship,
    COUNT(DISTINCT dr.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM tasks) as total_entities,
    ROUND(COUNT(DISTINCT dr.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM tasks), 0), 2) as coverage_percent
FROM document_references dr
WHERE dr.entity_type = 'task';

-- Work items with evidence
SELECT
    'work_items → evidence' as relationship,
    COUNT(DISTINCT es.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM work_items) as total_entities,
    ROUND(COUNT(DISTINCT es.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM work_items), 0), 2) as coverage_percent
FROM evidence_sources es
WHERE es.entity_type = 'work_item';

-- Tasks with evidence
SELECT
    'tasks → evidence' as relationship,
    COUNT(DISTINCT es.entity_id) as entities_covered,
    (SELECT COUNT(*) FROM tasks) as total_entities,
    ROUND(COUNT(DISTINCT es.entity_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM tasks), 0), 2) as coverage_percent
FROM evidence_sources es
WHERE es.entity_type = 'task';

-- Sessions with events
SELECT
    'sessions → events' as relationship,
    COUNT(DISTINCT se.session_id) as entities_covered,
    (SELECT COUNT(*) FROM sessions) as total_entities,
    ROUND(COUNT(DISTINCT se.session_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM sessions), 0), 2) as coverage_percent
FROM session_events se;

-- Agents with relationships
SELECT
    'agents → relationships' as relationship,
    COUNT(DISTINCT ar.agent_id) as entities_covered,
    (SELECT COUNT(*) FROM agents) as total_entities,
    ROUND(COUNT(DISTINCT ar.agent_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM agents), 0), 2) as coverage_percent
FROM agent_relationships ar;

-- Agents with tools
SELECT
    'agents → tools' as relationship,
    COUNT(DISTINCT at.agent_id) as entities_covered,
    (SELECT COUNT(*) FROM agents) as total_entities,
    ROUND(COUNT(DISTINCT at.agent_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM agents), 0), 2) as coverage_percent
FROM agent_tools at;


-- ===================================================================
-- PART 3: DATA DISTRIBUTION BY TYPE/STATUS
-- ===================================================================
SELECT '';
SELECT '=== PART 3: DATA DISTRIBUTION BY TYPE/STATUS ===' as section;
SELECT '';

SELECT 'work_items by type' as category, type as value, COUNT(*) as count
FROM work_items
GROUP BY type;

SELECT '';
SELECT 'work_items by status' as category, status as value, COUNT(*) as count
FROM work_items
GROUP BY status;

SELECT '';
SELECT 'tasks by type' as category, type as value, COUNT(*) as count
FROM tasks
GROUP BY type;

SELECT '';
SELECT 'tasks by status' as category, status as value, COUNT(*) as count
FROM tasks
GROUP BY status;

SELECT '';
SELECT 'agents by role' as category, role as value, COUNT(*) as count
FROM agents
GROUP BY role;

SELECT '';
SELECT 'contexts by type' as category, context_type as value, COUNT(*) as count
FROM contexts
GROUP BY context_type;

SELECT '';
SELECT 'sessions by status' as category, status as value, COUNT(*) as count
FROM sessions
GROUP BY status;

SELECT '';
SELECT 'rules by category' as category, category as value, COUNT(*) as count
FROM rules
GROUP BY category;

SELECT '';
SELECT 'ideas by status' as category, status as value, COUNT(*) as count
FROM ideas
GROUP BY status;


-- ===================================================================
-- PART 4: DATA QUALITY ISSUES
-- ===================================================================
SELECT '';
SELECT '=== PART 4: DATA QUALITY ISSUES ===' as section;
SELECT '';

-- Tasks without valid work_items
SELECT
    'Orphaned tasks (invalid work_item)' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM tasks
WHERE work_item_id NOT IN (SELECT id FROM work_items);

-- Work items without any tasks
SELECT
    'Work items with no tasks' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM work_items wi
WHERE NOT EXISTS (SELECT 1 FROM tasks t WHERE t.work_item_id = wi.id);

-- Tasks without assigned_to
SELECT
    'Unassigned tasks' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM tasks
WHERE assigned_to IS NULL OR assigned_to = '';

-- Contexts without entity reference
SELECT
    'Orphaned contexts (no entity)' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM contexts
WHERE entity_id IS NULL;

-- Task dependencies with invalid references
SELECT
    'Invalid task_dependencies' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(d.id, ', '), 1, 80) as affected_ids_sample
FROM task_dependencies d
LEFT JOIN tasks t1 ON d.task_id = t1.id
LEFT JOIN tasks t2 ON d.depends_on_task_id = t2.id
WHERE t1.id IS NULL OR t2.id IS NULL;

-- Work items with NULL phase
SELECT
    'Work items with NULL phase' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM work_items
WHERE phase IS NULL;

-- Work items missing business_context
SELECT
    'Work items missing business_context' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM work_items
WHERE business_context IS NULL OR business_context = '';

-- Tasks with NULL effort_hours
SELECT
    'Tasks missing effort estimate' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM tasks
WHERE effort_hours IS NULL;

-- Blocked tasks without blocked_reason
SELECT
    'Blocked tasks missing reason' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM tasks
WHERE status = 'blocked' AND (blocked_reason IS NULL OR blocked_reason = '');

-- Work items with empty metadata
SELECT
    'Work items with empty metadata' as issue,
    COUNT(*) as count,
    SUBSTR(GROUP_CONCAT(id, ', '), 1, 80) as affected_ids_sample
FROM work_items
WHERE metadata = '{}';


-- ===================================================================
-- PART 5: EMPTY TABLES (UNUSED SCHEMA)
-- ===================================================================
SELECT '';
SELECT '=== PART 5: EMPTY TABLES (UNUSED SCHEMA) ===' as section;
SELECT '';

SELECT 'agent_relationships' as table_name, COUNT(*) as row_count FROM agent_relationships
UNION ALL SELECT 'agent_tools', COUNT(*) FROM agent_tools
UNION ALL SELECT 'contexts', COUNT(*) FROM contexts
UNION ALL SELECT 'document_references', COUNT(*) FROM document_references
UNION ALL SELECT 'evidence_sources', COUNT(*) FROM evidence_sources
UNION ALL SELECT 'ideas', COUNT(*) FROM ideas
UNION ALL SELECT 'session_events', COUNT(*) FROM session_events
UNION ALL SELECT 'task_blockers', COUNT(*) FROM task_blockers
UNION ALL SELECT 'task_dependencies', COUNT(*) FROM task_dependencies
UNION ALL SELECT 'work_item_dependencies', COUNT(*) FROM work_item_dependencies
UNION ALL SELECT 'work_item_summaries', COUNT(*) FROM work_item_summaries;
