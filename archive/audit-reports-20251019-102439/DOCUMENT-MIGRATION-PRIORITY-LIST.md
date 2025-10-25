# Document Migration Priority List

**Purpose**: Identify untracked documentation that should be added to the database
**Total Untracked**: 250 markdown files
**Current Coverage**: 21% (62/295 files)
**Target Coverage**: >90% (265+ files)

---

## Priority 1: CRITICAL (Must Track Immediately)

### Core System Documentation (5 files)
These are essential system-level documentation:

1. `/Users/nigelcopley/.project_manager/aipm-v2/docs/CLAUDE.md`
   - Type: technical_specification
   - Entity: project
   - Reason: Primary AI orchestration instructions

2. `/Users/nigelcopley/.project_manager/aipm-v2/docs/aipm/README.md`
   - Type: user_guide
   - Entity: project
   - Reason: Main project documentation entry point

3. `/Users/nigelcopley/.project_manager/aipm-v2/docs/architecture/README.md`
   - Type: architecture
   - Entity: project
   - Reason: Architecture documentation index

4. `/Users/nigelcopley/.project_manager/aipm-v2/docs/components/README.md`
   - Type: architecture
   - Entity: project
   - Reason: Components documentation index

5. `/Users/nigelcopley/.project_manager/aipm-v2/docs/aipm/documentation-guidelines.md`
   - Type: design
   - Entity: project
   - Reason: Documentation standards and policies

### Architecture Decision Records (16 files)
ADRs document critical architectural decisions:

6. `/Users/nigelcopley/.project_manager/aipm-v2/docs/adrs/README.md`
   - Type: adr
   - Entity: project

7-21. All ADR files in `docs/adrs/`:
   - ADR-001 through ADR-014
   - docs/06-decisions/ADR-000-documentation-system-architecture.md
   - Type: adr
   - Entity: project (or link to specific work items if available)

### Agent System Documentation (4 files)
Critical for multi-agent architecture:

22. `/Users/nigelcopley/.project_manager/aipm-v2/docs/AGENTS.md`
    - Type: specification
    - Entity: project

23. `/Users/nigelcopley/.project_manager/aipm-v2/docs/agents/UNIVERSAL-AGENT-RULES.md`
    - Type: specification
    - Entity: project

24. `/Users/nigelcopley/.project_manager/aipm-v2/docs/agents/UNIVERSAL-RULES-QUICK-REFERENCE.md`
    - Type: user_guide
    - Entity: project

25. `/Users/nigelcopley/.project_manager/aipm-v2/docs/agents/AGENT-UNIVERSAL-RULES-UPDATE-REPORT.md`
    - Type: other
    - Entity: project

**Priority 1 Total**: 25 files

---

## Priority 2: HIGH (User-Facing Documentation)

### User Guides (10 files)
Essential for end users:

26-30. Core user guides:
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/01-getting-started.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/02-quick-reference.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/03-cli-commands.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/04-phase-workflow.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/05-troubleshooting.md`
   - Type: user_guide
   - Entity: project

31. `/Users/nigelcopley/.project_manager/aipm-v2/docs/user-guides/README.md`
    - Type: user_guide
    - Entity: project

32-35. Specialized user guides:
   - `docs/user-guides/ideas-workflow.md`
   - `docs/user-guides/rich-context-user-guide.md`
   - `docs/user-guides/documentation-audit-report.md`
   - `docs/user-guides/WALKTHROUGH-SUMMARY.md`
   - Type: user_guide
   - Entity: project

### Developer Guides (4 files)
Essential for contributors:

36-38. Core developer guides:
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/developer-guide/01-architecture-overview.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/developer-guide/02-three-layer-pattern.md`
   - `/Users/nigelcopley/.project_manager/aipm-v2/docs/developer-guide/03-contributing.md`
   - Type: developer_guide
   - Entity: project

39. `/Users/nigelcopley/.project_manager/aipm-v2/docs/developer-guide/provider-generator-system.md`
    - Type: technical_specification
    - Entity: project

### User Journeys (5 files)
User persona documentation:

40-44. User journey documents:
   - `docs/user-journeys/README.md`
   - `docs/user-journeys/solo-developer-startup.md`
   - `docs/user-journeys/consultant-client-project.md`
   - `docs/user-journeys/enterprise-team-migration.md`
   - `docs/user-journeys/open-source-maintainer.md`
   - Type: user_guide
   - Entity: project

**Priority 2 Total**: 19 files

---

## Priority 3: MEDIUM (Technical Documentation)

### Specifications (8 files)
High-level system specifications:

45-52. Specification documents:
   - `docs/specifications/AIPM-V2-COMPLETE-SPECIFICATION.md`
   - `docs/specifications/6W-QUESTIONS-ANSWERED.md`
   - `docs/specifications/COMPREHENSIVE-IMPACT-ANALYSIS-SPECIFICATION.md`
   - `docs/specifications/DOCUMENT-STORE-INTEGRATION.md`
   - `docs/specifications/EXECUTIVE-SUMMARY.md`
   - `docs/specifications/GAP-ANALYSIS-AND-ROADMAP.md`
   - `docs/specifications/SESSION-DELIVERABLES-SUMMARY.md`
   - Type: specification
   - Entity: project

### Migration Documentation (4 files)
Database migration guides:

53-56. Migration documents:
   - `docs/migrations/README.md`
   - `docs/migrations/migration-0031-documentation-system.md`
   - `docs/migrations/outcome-based-phase-gates.md`
   - `docs/migrations/SCHEMA-MIGRATION-ANALYSIS.md`
   - Type: technical_specification
   - Entity: project or link to migration work items

### Component-Specific Documentation (10 files)

57-66. Component documentation:
   - `docs/components/documents/COMPREHENSIVE-DOCUMENT-SYSTEM.md`
   - `docs/components/documents/FINAL-UNIVERSAL-DOCUMENT-SYSTEM.md`
   - `docs/components/documents/PURE-METADATA-APPROACH.md`
   - `docs/components/documents/SEGMENTATION-STRATEGY.md`
   - `docs/components/documents/UNIVERSAL-DOCUMENT-SYSTEM.md`
   - `docs/architecture/CONTEXT-DELIVERY-HIERARCHY-SPECIFICATION.md`
   - `docs/architecture/CONTEXT-DELIVERY-SUMMARY.md`
   - `docs/architecture/UNIFIED-CONTEXT-DELIVERY-SYSTEM.md`
   - `docs/architecture/context-delivery-diagram.md`
   - `docs/api/rich-context-api.md`
   - Type: architecture/specification
   - Entity: project or specific work items

**Priority 3 Total**: 22 files

---

## Priority 4: LOW (Analysis & Reports)

### System Analysis Documents (~30 critical files from ~80 total)
Select most relevant analysis documents:

67-96. Analysis documents:
   - `docs/analysis/DATABASE_CONTENT_ANALYSIS_REPORT.md`
   - `docs/analysis/DATABASE_CONTENT_QUICK_REFERENCE.md`
   - `docs/analysis/production-database-health-report.md`
   - `docs/analysis/STRATEGIC-DOCS-REALITY-CHECK.md`
   - `docs/analysis/consolidation_summary.md`
   - `docs/analysis/file-vs-database-system-inventory.md`
   - All files in `docs/analysis/system-review/` (10 files)
   - All files in `docs/analysis/agents/claude-code/` (7 files)
   - Select files from agents/generic/ (3-4 files)
   - Type: analysis
   - Entity: project or specific work items

### Reports (~20 critical files from ~30 total)
Select active/reference reports:

97-116. Report documents:
   - `docs/reports/APM_AUDIT_EXECUTIVE_SUMMARY.md`
   - `docs/reports/APM_COMMAND_AUDIT_REPORT.md`
   - `docs/reports/cli-command-audit-summary.md`
   - `docs/reports/database-systems-health-report.md`
   - `docs/reports/workflow-health-executive-summary.md`
   - `docs/reports/WORKFLOW-ANALYSIS-REPORT.md`
   - `docs/reports/RULES-SYSTEM-AUDIT.md`
   - `docs/reports/schema-gap-analysis-2025-10-16.md`
   - Plus 10-12 more active reports
   - Type: analysis/other
   - Entity: link to work items where applicable

**Priority 4 Total**: ~50 files (selective)

---

## Priority 5: CONTEXTUAL (Work Item Specific)

### Work Item Documentation (~15 files)
Link to specific work items:

117-131. Work item documents:
   - All files in `docs/work-items/` subdirectories
   - Type: design/implementation_plan/requirements
   - Entity: Link to specific work item IDs

### Design Documents (~20 files)
Architecture and design proposals:

132-151. Design documents:
   - All files in `docs/design/` directory
   - Type: design/architecture
   - Entity: Link to work items or project

### Features Documentation (3 files)

152-154. Feature documents:
   - `docs/features/README.md`
   - `docs/features/pydantic-types-exposure.md`
   - `docs/features/context-wizard-implementation.md`
   - Type: specification
   - Entity: Link to feature work items

**Priority 5 Total**: ~38 files

---

## DEFER OR ARCHIVE

### Historical Analysis (Skip for now)
- Older analysis documents with dates <2025-10-10
- Superseded analysis documents
- One-time exploration documents

### Duplicate/Redundant Documentation
- Multiple versions of same content
- Draft documents with final versions available

### External Research (Selective)
- `docs/external-research/` - Track only critical reference documents
- Most external research is transient

---

## Migration Execution Strategy

### Phase 1: Critical Core (Priority 1) - 25 files
**Command**:
```bash
# Use document CLI to add each file
apm document add <file_path> \
  --entity-type project \
  --entity-id 1 \
  --document-type <type> \
  --title "<title>"
```

**Estimated Time**: 1 hour

### Phase 2: User-Facing (Priority 2) - 19 files
**Estimated Time**: 45 minutes

### Phase 3: Technical Docs (Priority 3) - 22 files
**Estimated Time**: 1 hour

### Phase 4: Analysis & Reports (Priority 4) - 50 files (selective)
**Estimated Time**: 2 hours

### Phase 5: Contextual Docs (Priority 5) - 38 files
**Estimated Time**: 1.5 hours

**Total Migration Time**: ~6.5 hours
**Total Files to Add**: ~154 files (selective from 250 untracked)
**Expected Final Coverage**: ~85% (216/295 files)

---

## Automation Opportunity

Create a migration script to batch-add files:

```python
# migration_script.py
documents_to_add = [
    {
        "file_path": "docs/CLAUDE.md",
        "entity_type": "project",
        "entity_id": 1,
        "document_type": "technical_specification",
        "title": "APM (Agent Project Manager) Master Orchestrator"
    },
    # ... more documents
]

for doc in documents_to_add:
    subprocess.run([
        "apm", "document", "add", doc["file_path"],
        "--entity-type", doc["entity_type"],
        "--entity-id", str(doc["entity_id"]),
        "--document-type", doc["document_type"],
        "--title", doc["title"]
    ])
```

---

## Next Steps

1. **Execute cleanup script** to remove invalid records (26 deletions)
2. **Start Priority 1 migration** (25 critical files)
3. **Validate** each batch before proceeding
4. **Continue through priorities** 2-5 as time allows
5. **Create automated migration script** for remaining files

**Success Criteria**: >90% documentation coverage with valid, accessible files only.
