-- work_item_summaries Table Schema Proposal
-- Purpose: Store session-level context, decisions, and narrative arc for work items
-- Use Case: Enable session-start agents to efficiently gather context from previous work

CREATE TABLE work_item_summaries (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Key (what work item does this summarize?)
    work_item_id INTEGER NOT NULL,

    -- Session Identification
    session_date TEXT NOT NULL,           -- YYYY-MM-DD format (ISO 8601)
    session_duration_hours REAL,          -- Optional: track session length

    -- Summary Content (Human & AI readable)
    summary_text TEXT NOT NULL,           -- Markdown formatted narrative

    -- Structured Metadata (AI parseable, JSON format)
    -- Example: {"key_decisions": [...], "technical_changes": [...], "blockers_resolved": [...]}
    context_metadata TEXT,                -- JSON blob

    -- Attribution & Audit Trail
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_by TEXT,                      -- Agent identifier or username

    -- Categorization (optional, for future filtering)
    summary_type TEXT DEFAULT 'session', -- 'session', 'milestone', 'decision', 'retrospective'

    -- Constraints
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,

    -- Ensure session_date is valid ISO 8601 date
    CHECK (session_date IS date(session_date))
);

-- Indexes for Performance
-- Query pattern: "Get all summaries for work item X, ordered by date"
CREATE INDEX idx_work_item_summaries_work_item
    ON work_item_summaries(work_item_id, session_date DESC);

-- Query pattern: "Get recent summaries across all work items"
CREATE INDEX idx_work_item_summaries_date
    ON work_item_summaries(session_date DESC);

-- Query pattern: "Find summaries by type (session vs milestone)"
CREATE INDEX idx_work_item_summaries_type
    ON work_item_summaries(work_item_id, summary_type, session_date DESC);

-- Example Data Structure for context_metadata JSON:
/*
{
  "key_decisions": [
    "Decided to use 3-layer DB pattern everywhere",
    "Approved 8h plugin integration scope"
  ],
  "technical_changes": [
    "Added 7 state transition commands",
    "Fixed PluginOrchestrator exports"
  ],
  "tasks_completed": [11, 13, 14, 15, 16, 6],
  "blockers_resolved": [
    "Orchestrator test failures (import issues)"
  ],
  "open_questions": [
    "Should we support plugin hot-reloading?"
  ],
  "lessons_learned": [
    "Documentation-first prevents implementation confusion"
  ],
  "metrics": {
    "duration_hours": 7.5,
    "code_loc": 1000,
    "tests_added": 8,
    "docs_words": 70000
  }
}
*/

-- Example Queries:

-- Get all summaries for a work item (chronological)
-- SELECT * FROM work_item_summaries
-- WHERE work_item_id = 6
-- ORDER BY session_date ASC;

-- Get most recent summary for context loading
-- SELECT * FROM work_item_summaries
-- WHERE work_item_id = 6
-- ORDER BY session_date DESC
-- LIMIT 1;

-- Get last N session summaries (for session-start agent)
-- SELECT * FROM work_item_summaries
-- WHERE work_item_id = 6
-- ORDER BY session_date DESC
-- LIMIT 5;

-- Get all milestone summaries
-- SELECT * FROM work_item_summaries
-- WHERE summary_type = 'milestone'
-- ORDER BY session_date DESC;
