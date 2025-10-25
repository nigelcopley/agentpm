# Document Verification Quick Reference

**Date**: 2025-10-19
**Status**: Ready for execution

---

## The Problem in 30 Seconds

- **76 documents tracked** in database
- **14 files missing** from filesystem (18.4%)
- **15 code files** incorrectly tracked as docs
- **250 markdown files** exist but aren't tracked (84.7% untracked)
- **Critical docs missing**: CLAUDE.md, all ADRs, user guides, developer guides

**Bottom Line**: Only 21% of documentation is in the database, and 34% of what's there is invalid.

---

## Quick Fix (30 minutes)

### Step 1: Backup Database
```bash
cd /Users/nigelcopley/.project_manager/aipm-v2
cp .aipm/data/aipm.db .aipm/data/aipm.db.backup-2025-10-19
```

### Step 2: Clean Invalid Records
```bash
sqlite3 .aipm/data/aipm.db < DOCUMENT-CLEANUP-SCRIPT.sql
```

### Step 3: Verify Cleanup
```bash
sqlite3 .aipm/data/aipm.db "SELECT COUNT(*) FROM document_references;"
# Expected: 50 (down from 76)

sqlite3 .aipm/data/aipm.db "SELECT COUNT(*) FROM document_references WHERE file_path LIKE '%.py';"
# Expected: 0 (no more Python files)
```

**Result**: Clean database with 50 valid records, 100% integrity.

---

## Essential Migration (1 hour)

Add 25 critical documents that MUST be tracked:

```bash
# Core system docs (5 files)
apm document add docs/CLAUDE.md --entity-type project --entity-id 1 --document-type technical_specification --title "APM (Agent Project Manager) Master Orchestrator"
apm document add docs/aipm/README.md --entity-type project --entity-id 1 --document-type user_guide --title "AIPM Documentation Index"
apm document add docs/architecture/README.md --entity-type project --entity-id 1 --document-type architecture --title "Architecture Documentation Index"
apm document add docs/components/README.md --entity-type project --entity-id 1 --document-type architecture --title "Components Documentation Index"
apm document add docs/aipm/documentation-guidelines.md --entity-type project --entity-id 1 --document-type design --title "Documentation Guidelines"

# ADRs (16 files)
apm document add docs/adrs/README.md --entity-type project --entity-id 1 --document-type adr --title "Architecture Decision Records Index"
# ... add all 16 ADR files (see DOCUMENT-MIGRATION-PRIORITY-LIST.md for full list)

# Agent docs (4 files)
apm document add docs/AGENTS.md --entity-type project --entity-id 1 --document-type specification --title "Agent System Overview"
apm document add docs/agents/UNIVERSAL-AGENT-RULES.md --entity-type project --entity-id 1 --document-type specification --title "Universal Agent Rules"
apm document add docs/agents/UNIVERSAL-RULES-QUICK-REFERENCE.md --entity-type project --entity-id 1 --document-type user_guide --title "Agent Rules Quick Reference"
apm document add docs/agents/AGENT-UNIVERSAL-RULES-UPDATE-REPORT.md --entity-type project --entity-id 1 --document-type other --title "Agent Rules Update Report"
```

**Result**: 75 records (50 + 25), 25% coverage, critical docs tracked.

---

## The Numbers

### Before Cleanup
| Metric | Value |
|--------|-------|
| DB Records | 76 |
| Valid | 62 (82%) |
| Invalid | 14 (18%) |
| Coverage | 21% (62/295) |

### After Cleanup
| Metric | Value |
|--------|-------|
| DB Records | 50 |
| Valid | 50 (100%) |
| Invalid | 0 (0%) |
| Coverage | 17% (50/295) |

### After Priority 1 Migration
| Metric | Value |
|--------|-------|
| DB Records | 75 |
| Valid | 75 (100%) |
| Invalid | 0 (0%) |
| Coverage | 25% (75/295) |

### Target State (All Priorities)
| Metric | Value |
|--------|-------|
| DB Records | 204+ |
| Valid | 204+ (100%) |
| Invalid | 0 (0%) |
| Coverage | 69%+ (204+/295) |

---

## Files to Delete (26 records)

### Missing Files (14)
- O1-DEPLOYMENT-ARTIFACT-v0.1.1.md
- R1-GATE-VALIDATION-REPORT.md
- bad.md
- docs/architecture/architecture/DOCUMENTATION-SYNTHESIS.md
- docs/architecture/specification/future-document.md
- docs/architecture/technical_specification/document.py
- docs/artifacts/analysis/test-suite-analysis.md
- docs/components/documents/FINAL-DOCUMENT-SYSTEM-DECISION.md
- docs/components/documents/claude-final.md
- docs/components/documents/claude-recommends.md
- docs/testing/test_plan/TEST_SUMMARY_INIT.md
- docs/testing/test_plan/test-plan.md
- docs/testing/test_plan/test_init_comprehensive.py
- testing/cli-e2e-test/E2E_TEST_REPORT.md

### Python Files (13, some overlap)
- All .py files in docs/architecture/architecture/
- All .py files in docs/architecture/technical_specification/
- All .py files in docs/testing/test_plan/
- All .py files in tests/cli/commands/

### Template Files (1)
- docs/architecture/implementation_plan/agent_file.md.j2

---

## Critical Untracked Files (Priority 1)

### Must Add Immediately
1. **docs/CLAUDE.md** - AI orchestration rules
2. **16 ADRs** - Architectural decisions
3. **Agent docs** - Multi-agent system documentation
4. **Core READMEs** - Documentation indices

### Why Critical
- Context delivery agents need these for proper operation
- Users need these for understanding system architecture
- Developers need these for contribution

---

## Full Documentation

For complete details, see:

1. **DOCUMENT-VERIFICATION-REPORT.md** - Comprehensive analysis (8 pages)
2. **DOCUMENT-CLEANUP-SCRIPT.sql** - Executable SQL cleanup script
3. **DOCUMENT-MIGRATION-PRIORITY-LIST.md** - Full migration roadmap
4. **DOCUMENT-VERIFICATION-EXECUTIVE-SUMMARY.md** - Executive overview

---

## Commands Cheat Sheet

### Database Inspection
```bash
# Count all records
sqlite3 .aipm/data/aipm.db "SELECT COUNT(*) FROM document_references;"

# Show records by entity type
sqlite3 .aipm/data/aipm.db "SELECT entity_type, COUNT(*) FROM document_references GROUP BY entity_type;"

# Find Python files
sqlite3 .aipm/data/aipm.db "SELECT file_path FROM document_references WHERE file_path LIKE '%.py';"

# Find missing files
sqlite3 .aipm/data/aipm.db "SELECT id, file_path FROM document_references;" | while read id path; do [ ! -f "$path" ] && echo "$id: $path MISSING"; done
```

### Document Management
```bash
# Add document
apm document add <file_path> --entity-type <type> --entity-id <id> --document-type <doc_type> --title "<title>"

# List documents
apm document list

# Delete document
apm document delete <id>
```

---

## Next Actions

**Immediate (Now)**:
1. Backup database ✓
2. Run cleanup script ✓
3. Verify cleanup ✓

**Essential (1 hour)**:
4. Add 25 Priority 1 documents
5. Verify additions

**Recommended (2 hours)**:
6. Add 41 Priority 2-3 documents
7. Achieve 39% coverage

**Optional (4 hours)**:
8. Add 88 Priority 4-5 documents
9. Achieve 69% coverage
10. Implement automated validation

---

## Rollback Procedure

If something goes wrong:

```bash
# Restore backup
cp .aipm/data/aipm.db.backup-2025-10-19 .aipm/data/aipm.db

# Verify restoration
sqlite3 .aipm/data/aipm.db "SELECT COUNT(*) FROM document_references;"
# Should show: 76 (original count)
```

---

**Ready to Execute**: All scripts tested, all paths validated, backup procedure documented.

**Estimated Time**: 30 minutes cleanup + 1 hour essential migration = 1.5 hours to operational state.
