# APM (Agent Project Manager) Database Content - Quick Reference Card

**Date**: 2025-10-16 | **Database**: agentpm.db | **Schema Utilization**: 11%

---

## 📊 At a Glance

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tables** | 18 | ✅ Complete |
| **Tables with Data** | 2 | ⚠️ Minimal (11%) |
| **Empty Tables** | 15 | 🔴 Unused (89%) |
| **Total Rows** | 26 | (1 project + 25 rules) |

---

## ✅ ACTIVE TABLES (Has Data)

### projects (1 row)
```
Project: aipm-v2
Status: initiated
Tech Stack: [] (empty)
```

### rules (25 rows)
```
Categories:
- Development Principles: 17 rules (6 blocking)
- Technology Standards: 2 rules
- Workflow Rules: 6 rules (5 blocking)

Enforcement:
- BLOCK: 11 rules (hard stops)
- LIMIT: 4 rules (soft limits)
- WARN: 10 rules (advisory)
```

---

## 🔴 CRITICAL GAPS (Core Features Unused)

| Table | Rows | Why Critical | Impact |
|-------|------|--------------|--------|
| `work_items` | 0 | Core AIPM feature | No work tracking |
| `tasks` | 0 | Core AIPM feature | No task management |
| `agents` | 0 | Orchestration system | Agent system inactive |
| `contexts` | 0 | 6W intelligence | Context framework unused |
| `sessions` | 0 | Session tracking | No session history |

---

## ⚪ EMPTY TABLES (Supporting Features)

**All have 0 rows:**
- task_dependencies
- work_item_dependencies
- document_references
- evidence_sources
- ideas
- session_events
- task_blockers
- work_item_summaries
- agent_relationships
- agent_tools

---

## 🔍 Key Findings

### 1. Schema vs Data Mismatch
- **Schema**: Sophisticated, comprehensive (19 tables)
- **Data**: Minimal, only rules active (2 tables)
- **Gap**: 89% of schema capability unused

### 2. Missing Core AIPM Data
- ❌ No work items tracked
- ❌ No tasks managed
- ❌ No agents defined
- ❌ No 6W contexts
- ❌ No session history

### 3. Only Rules System Active
- ✅ 25 rules defined
- ✅ Time-boxing configured (4h impl, 6h test)
- ✅ Enforcement levels working

---

## 🎯 Immediate Actions

### 1️⃣ CREATE SAMPLE DATA
```sql
-- Test core schema with 2-3 work items
-- Test 5-10 tasks linked to work items
-- Verify constraints work
```

### 2️⃣ POPULATE AGENTS
```bash
# Import from .claude/agents/
# Populate agents table
# Link tools and relationships
```

### 3️⃣ TEST 6W FRAMEWORK
```sql
-- Create contexts for work items
-- Test confidence scoring (0.0-1.0)
-- Verify RED/YELLOW/GREEN bands
```

### 4️⃣ ENABLE SESSION TRACKING
```python
# Populate sessions table
# Capture session events
# Test lifecycle (active → completed)
```

---

## 📈 Relationship Coverage

**All relationships have 0% coverage:**

```
work_items (0) ←→ tasks (0)
work_items (0) ←→ contexts (0)
tasks (0) ←→ dependencies (0)
tasks (0) ←→ evidence (0)
sessions (0) ←→ events (0)
agents (0) ←→ tools (0)
```

---

## 🔧 Metadata Fields Status

| Field | Status | Purpose |
|-------|--------|---------|
| `work_items.metadata` | UNUSED | Custom work data |
| `tasks.quality_metadata` | UNUSED | CI gate tracking |
| `sessions.metadata` | UNUSED | Session context |
| `rules.config` | **ACTIVE** | Rule configuration ✅ |
| `contexts.six_w_data` | UNUSED | 6W framework |
| `contexts.confidence_score` | UNUSED | Context scoring |

---

## 🚦 Data Quality

### ✅ No Issues Found
- No orphaned records (tables empty)
- No invalid FKs (no relationships)
- No missing required fields (no data)
- Schema integrity: **PERFECT**

---

## 💡 Questions to Answer

1. **Is 11% usage intentional?**
   - Staged rollout? (planned)
   - Over-engineered? (too complex)

2. **Which tables are needed for v2?**
   - Keep all 19 tables? (future-ready)
   - Remove unused? (simplify)

3. **Where's the work data?**
   - Database not primary storage?
   - Different database location?
   - File-based instead?

---

## 📋 Sample Queries

### Check All Table Populations
```sql
SELECT
    name as table_name,
    (SELECT COUNT(*) FROM sqlite_master sm2
     WHERE sm2.name = sm.name) as row_count
FROM sqlite_master sm
WHERE type = 'table' AND name NOT LIKE 'sqlite_%';
```

### View Active Rules
```sql
SELECT rule_id, name, category, enforcement_level
FROM rules
WHERE enabled = 1
ORDER BY category, rule_id;
```

### Check Foreign Key Relationships
```sql
SELECT * FROM pragma_foreign_key_list('work_items');
SELECT * FROM pragma_foreign_key_list('tasks');
SELECT * FROM pragma_foreign_key_list('contexts');
```

---

## 📄 Full Report

**Detailed Analysis**: `DATABASE_CONTENT_ANALYSIS_REPORT.md`
**SQL Queries**: `database_content_analysis.sql`

---

**Generated**: 2025-10-16
**Database**: agentpm.db
**Total Tables**: 18
**Schema Utilization**: 11% (2 of 18 tables populated)
**Status**: Schema excellent, data minimal
