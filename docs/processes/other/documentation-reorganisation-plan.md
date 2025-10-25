# Documentation Reorganisation Plan

**Date:** 2025-01-27  
**Status:** Implementation Plan  
**Context:** Full documentation review to ensure compliance with `docs/{category}/{document_type}/filename.md` structure

---

## Current State Analysis

### Root-Level Markdown Files (Need to be Moved)

**Files to Keep in Root:**
- `README.md` - Standard project file
- `CHANGELOG.md` - Standard project file  
- `LICENSE.md` - Standard project file
- `CLAUDE.md` - As requested by user
- `GEMINI.md` - As requested by user

**Files to Move:**

1. **Assessment/Status Reports** → `docs/architecture/assessment_report/`
   - `AGENT_SYSTEM_ASSESSMENT_SUMMARY.md` → `docs/architecture/assessment_report/agent-system-assessment-summary.md`
   - `DOCUMENT_STRUCTURE_CONSISTENCY_REPORT.md` → `docs/architecture/assessment_report/document-structure-consistency-report.md`
   - `TEST_SUITE_SUMMARY.md` → `docs/architecture/assessment_report/test-suite-summary.md`

2. **Implementation/Development** → `docs/processes/implementation/`
   - `IMPLEMENTATION-SUMMARY.md` → `docs/processes/implementation/implementation-summary.md`
   - `DEVELOPMENT.md` → `docs/processes/implementation/development.md`
   - `SBOM_CLI_IMPLEMENTATION.md` → `docs/processes/implementation/sbom-cli-implementation.md`
   - `PRESET_SYSTEM_IMPLEMENTATION.md` → `docs/processes/implementation/preset-system-implementation.md`

3. **Release/Operations** → `docs/operations/release/`
   - `RELEASE.md` → `docs/operations/release/release.md`
   - `RELEASE_CHECKLIST.md` → `docs/operations/release/release-checklist.md`
   - `PRE_RELEASE_CHECKLIST.md` → `docs/operations/release/pre-release-checklist.md`
   - `CLEAN_RELEASE_GUIDE.md` → `docs/operations/release/clean-release-guide.md`
   - `ROOT_CLEANUP_SUMMARY.md` → `docs/operations/release/root-cleanup-summary.md`

4. **Migration/Technical** → `docs/processes/migration/`
   - `MIGRATION_SUMMARY.md` → `docs/processes/migration/migration-summary.md`
   - `COVERAGE-OVERRIDE-FIX.md` → `docs/processes/migration/coverage-override-fix.md`

5. **Task/Work Item Completions** → `docs/processes/completion/`
   - `TASK-947-BRANDING-TEST-COMPLETION.md` → `docs/processes/completion/task-947-branding-test-completion.md`
   - `FIX_SUMMARY_TASK_1003.md` → `docs/processes/completion/fix-summary-task-1003.md`
   - `WI-141-TASK-933-COMPLETION.md` → `docs/processes/completion/wi-141-task-933-completion.md`
   - `WI-148-COMPLETION-SUMMARY.md` → `docs/processes/completion/wi-148-completion-summary.md`

6. **Session/Communication** → `docs/communication/session/`
   - `SESSION-HANDOVER-2025-10-25.md` → `docs/communication/session/session-handover-2025-10-25.md`

7. **Research/Analysis** → `docs/planning/research/`
   - `fitness_result.md` → `docs/planning/research/fitness-result.md`
   - `GITHUB_SETUP_OPTIONS.md` → `docs/planning/research/github-setup-options.md`

### Non-Standard Locations (Need to be Moved)

1. **claudedocs/** → `docs/planning/research/`
   - `claudedocs/research_apm_market_positioning_2025-10-25.md` → `docs/planning/research/research-apm-market-positioning-2025-10-25.md`

2. **agentpm/web/** → `docs/architecture/web/`
   - `agentpm/web/WEB_CONSOLIDATION_TASKS.md` → `docs/architecture/web/web-consolidation-tasks.md`
   - `agentpm/web/WEB_CONSOLIDATION_WORK_ITEM.md` → `docs/architecture/web/web-consolidation-work-item.md`

---

## Database Integration Plan

### Document Reference Updates

Each moved document needs to be:
1. **Physically moved** to new location
2. **Database record updated** with new `file_path`
3. **Metadata enriched** with proper `category`, `document_type`, and other fields
4. **Content hash updated** if content changes

### Database Schema Compliance

All documents must comply with:
- **Path Structure**: `docs/{category}/{document_type}/{filename}.md`
- **Categories**: planning, architecture, guides, reference, processes, governance, operations, communication
- **Document Types**: As defined in `DocumentType` enum
- **Database Storage**: Hybrid approach (metadata in DB, content in files)

---

## Implementation Steps

### Phase 1: Directory Structure Creation
1. Create missing directories:
   - `docs/architecture/assessment_report/`
   - `docs/processes/implementation/`
   - `docs/operations/release/`
   - `docs/processes/migration/`
   - `docs/processes/completion/`
   - `docs/communication/session/`
   - `docs/planning/research/`
   - `docs/architecture/web/`

### Phase 2: Document Migration
1. Move files to new locations
2. Update file paths to use kebab-case naming
3. Preserve content integrity

### Phase 3: Database Updates
1. Update existing `document_references` records
2. Create new records for previously untracked documents
3. Enrich metadata with proper categorization

### Phase 4: Verification
1. Verify all documents follow naming conventions
2. Confirm database records are accurate
3. Test document discovery and search

---

## Quality Gates

### CI-007: Document Path Validation
- All documents must be in `docs/{category}/{document_type}/` structure
- File names must use kebab-case
- No root-level markdown files (except exceptions)

### CI-008: Database Consistency
- All documents must have database records
- File paths in database must match actual file locations
- Metadata must be properly categorised

---

## Success Metrics

- **100%** of documents in proper structure
- **100%** of documents tracked in database
- **0** root-level markdown files (except exceptions)
- **Consistent** naming conventions across all documents

---

**Next Steps:**
1. Execute directory creation
2. Move documents systematically
3. Update database records
4. Verify compliance
