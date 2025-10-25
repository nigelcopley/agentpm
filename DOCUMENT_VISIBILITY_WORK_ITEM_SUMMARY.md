# Work Item #164: Context-Aware Document Visibility System

**Status**: ✅ PLANNED (ready for implementation)  
**Priority**: 1 (CRITICAL)  
**Type**: Feature  
**Estimated Effort**: 56.5 hours (18 tasks)

---

## Overview

Implement a comprehensive, context-aware document visibility and lifecycle management system that:
- **Auto-generates file paths** from document metadata
- **Determines visibility** (public vs private) based on project context
- **Manages lifecycle** (draft → review → published → archived)
- **Enforces database-first** document creation (DOC-020 rule)

---

## Problem Statement

**Current Issues:**
- Documents created directly without database tracking (555 orphaned files)
- Inconsistent file naming and locations
- No visibility policy (all docs in one place)
- Agents bypass `apm document add` command
- No document lifecycle management
- Violation of database-first architecture

**Business Impact:**
- Poor documentation quality and discoverability
- Lack of proper access control (internal vs public docs)
- No audit trail for document changes
- Difficulty collaborating on documentation

---

## Acceptance Criteria

1. ✅ **File paths automatically generated** from category/type/title, overriding any provided path
2. ✅ **Context-aware visibility policy** determines public vs private placement based on team size, dev stage, and document type
3. ✅ **Publishing workflow implemented** (draft→review→published) with CLI commands
4. ✅ **All agents use** `apm document add` command exclusively (DOC-020 enforced)
5. ✅ **Incorrect file paths automatically corrected**, files moved to proper location

---

## Target Metrics

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Database-tracked docs** | ~0% (555 orphaned) | 100% | From chaos to full tracking |
| **Path generation time** | N/A | <100ms | Fast automatic generation |
| **Visibility accuracy** | N/A | >95% | Context-aware placement |
| **Agent DOC-020 compliance** | ~0% | 100% | Full enforcement |
| **Orphaned files** | 555 | 0 | Complete cleanup |

---

## Solution Architecture

### 1. **Document Storage Model**

```
.agentpm/docs/           # PRIVATE (source of truth, internal docs)
├── planning/            # Ideas, requirements, research
├── architecture/        # Design docs, ADRs, tech specs
├── processes/           # Test plans, implementation guides
├── operations/          # Runbooks, incident reports (sensitive)
├── communication/       # Status reports, session summaries
└── governance/          # Business pillars, stakeholder analysis

docs/                    # PUBLIC (published copies for users/contributors)
├── guides/              # User, developer, admin guides
│   ├── user_guide/
│   ├── developer_guide/
│   └── admin_guide/
├── reference/           # API docs, specifications
└── processes/           # Migration guides, integration guides
```

### 2. **Visibility Policy Matrix**

40+ document types across 8 categories, each with default visibility:

**Always Private:**
- Planning (ideas, requirements, research, analysis)
- Governance (business pillars, stakeholder analysis)
- Operations (runbooks, monitoring, incidents)
- Communication (status reports, session summaries)

**Always Public:**
- Guides (user, developer, admin, troubleshooting, FAQ)
- Reference (API docs, specifications)

**Context-Aware:**
- Architecture (private when drafting, public when stable)
- Processes (internal plans private, user-facing guides public)

### 3. **Context-Aware Scoring**

Evaluates project context to determine visibility:

**Project Context Factors:**
- Team size (solo | small | medium | large)
- Dev stage (development | staging | production)
- Collaboration model (private | internal | open_source)
- Document lifecycle (draft | review | published | archived)

**Scoring System (0-100):**
- 0-40: private (`.agentpm/docs/`)
- 40-60: restricted (team only)
- 60-100: public (`docs/`)

**Example:**
- Solo dev + development stage + user guide = 70 (public, users need it)
- Small team + production + runbook = 30 (private, sensitive)
- Open source + published ADR = 90 (public, transparency)

### 4. **Publishing Workflow**

```
1. CREATE (draft)
   ↓
   Location: .agentpm/docs/planning/requirements/my-spec.md
   Visibility: private
   Lifecycle: draft
   
2. SUBMIT FOR REVIEW
   ↓
   apm document submit-review 123
   
3. APPROVE
   ↓
   apm document approve 123
   Lifecycle: approved
   
4. PUBLISH (if public-facing)
   ↓
   apm document publish 123
   Copies to: docs/guides/user_guide/my-guide.md
   Visibility: public
   Lifecycle: published
   
5. SYNC
   ↓
   apm document sync  # Sync all published docs
```

---

## Tasks Breakdown (18 tasks, 56.5 hours)

### Design Phase (3 tasks, 10.5 hours)

1. **#1074** - Design Document Visibility Policy Matrix (4.0h)
   - Create comprehensive matrix for 40+ document types
   - Define default visibility, audience, review requirements
   - Consider context factors

2. **#1075** - Design File Path Generation Algorithm (3.0h)
   - Auto-generate paths from category/type/title
   - Slugification, conflict resolution, validation
   - Path correction for incorrect locations

3. **#1076** - Design Publishing Workflow (3.5h)
   - Complete lifecycle: draft→review→published→archived
   - Auto-publish triggers, review gates
   - Sync mechanisms

### Implementation Phase (8 tasks, 28.0 hours)

4. **#1077** - Create Database Schema Migration (2.5h)
   - Add visibility fields to `document_references`
   - Create `document_visibility_policies` table
   - Create `document_audit_log` table

5. **#1078** - Implement Document Visibility Policy Engine (4.0h)
   - `VisibilityPolicyEngine` class
   - Scoring system (0-100)
   - Policy matrix evaluation

6. **#1079** - Implement File Path Generator Service (3.5h)
   - `DocumentPathGenerator` service
   - Auto-generate from metadata
   - Path validation and correction

7. **#1080** - Implement Publishing Workflow Service (4.0h)
   - `DocumentPublisher` service
   - Methods: submit_review, approve, publish, unpublish, sync
   - File copying, audit logging

8. **#1081** - Create Document Publishing CLI Commands (3.5h)
   - `apm document publish/unpublish/sync`
   - `apm document submit-review/approve`
   - `apm document set-visibility`

9. **#1082** - Update `document add` Command (3.0h)
   - Auto-generate file paths (make --file-path optional)
   - Validate against generated path
   - Move file if incorrect location

10. **#1083** - Update DOC-020 Validator (2.5h)
    - Check visibility compliance
    - Validate published docs in correct location
    - Detect orphaned files

11. **#1084** - Create Document Migration Script (3.0h)
    - Move 555 orphaned docs to correct locations
    - Update database records
    - Preserve old paths as aliases

### Testing Phase (4 tasks, 15.5 hours)

12. **#1085** - Unit Tests for Visibility Policy Engine (4.0h)
    - Test all document types and contexts
    - Verify scoring algorithm >95% accuracy

13. **#1086** - Unit Tests for Path Generator (3.0h)
    - Test path generation, slugification, conflicts
    - Edge cases: special chars, long titles

14. **#1087** - Integration Tests for Publishing Workflow (5.0h)
    - Test complete lifecycle
    - Verify file copying, audit logs
    - Test unpublish/re-publish

15. **#1088** - Validation Tests for DOC-020 Compliance (3.5h)
    - Test direct file creation blocked
    - Verify agent compliance
    - 0 orphaned documents after migration

### Documentation Phase (3 tasks, 7.5 hours)

16. **#1089** - Update DOC-020 Rule Documentation (2.0h)
    - Add visibility policy, auto-path generation
    - Publishing workflow examples

17. **#1090** - Update CLAUDE.md with Visibility Workflow (2.5h)
    - Update Section 10 with complete workflow
    - Auto-path generation examples
    - Agent delegation patterns

18. **#1091** - Create Document Management User Guide (3.0h)
    - Comprehensive user guide at `docs/guides/user_guide/document-management.md`
    - Creating docs, visibility policies, publishing
    - **Use `apm document add` to create it!** (dogfooding)

---

## Dependencies

**Blocks:**
- Frictionless Installation (WI-157) - Phase 6 documentation tasks
- Any future documentation work

**Depends On:**
- DOC-020 rule (✅ already created)
- `apm document add` command (✅ already exists)
- Database schema (✅ ready for migration)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Breaking existing doc references** | Medium | Medium | Migration script updates DB records, preserve old paths as aliases |
| **Agents bypass document command** | High | High | Automated CI validation, clear CLAUDE.md instructions, DOC-020 enforcement |
| **Complex visibility rules confusing** | Low | Medium | Clear documentation, sensible defaults, override capability |
| **Migration script misses files** | Medium | Low | Dry-run mode, comprehensive testing, manual verification |
| **Performance impact (<100ms target)** | Low | Low | Caching, optimized algorithm, benchmarking |

---

## Implementation Phases

### Week 1: Design & Foundation
- **Tasks**: #1074, #1075, #1076, #1077
- **Deliverables**: Policy matrix, algorithm design, database schema
- **Milestone**: Design approved, migration ready

### Week 2: Core Services
- **Tasks**: #1078, #1079, #1080
- **Deliverables**: Policy engine, path generator, publisher service
- **Milestone**: Core functionality working

### Week 3: CLI & Integration
- **Tasks**: #1081, #1082, #1083, #1084
- **Deliverables**: CLI commands, auto-path in add command, migration script
- **Milestone**: Complete system functional

### Week 4: Testing & Validation
- **Tasks**: #1085, #1086, #1087, #1088
- **Deliverables**: Comprehensive test suite, 0 orphaned files
- **Milestone**: Quality gates passed

### Week 5: Documentation & Polish
- **Tasks**: #1089, #1090, #1091
- **Deliverables**: Updated rules, CLAUDE.md, user guide
- **Milestone**: Ready for production

---

## Success Criteria

✅ **All 18 tasks completed** with quality gates passed  
✅ **100% of documents** created via database (0 orphaned)  
✅ **File path generation** <100ms average  
✅ **Visibility accuracy** >95% across all contexts  
✅ **Agent DOC-020 compliance** 100%  
✅ **555 orphaned files** migrated successfully  
✅ **Publishing workflow** fully functional  
✅ **Test coverage** >90% for new code  
✅ **Documentation** complete and accurate  

---

## Related Documents

- **Design Specification**: `document-visibility-policy-design.md`
- **DOC-020 Rule**: `docs/rules/DOC-020_DATABASE_FIRST_DOCUMENTS.md`
- **CLAUDE.md**: Section 10 (Database-First Document Creation)
- **Implementation Plan**: This document

---

## Next Steps

1. **Review & approve** this work item plan
2. **Start Design Phase** (Week 1):
   - Task #1074: Design visibility policy matrix
   - Task #1075: Design path generation algorithm
   - Task #1076: Design publishing workflow
3. **Create work item documentation** using `apm document add` (dogfooding!)
4. **Begin implementation** following 5-week plan

---

**Status**: ✅ READY FOR IMPLEMENTATION  
**Created**: 2025-10-25  
**Estimated Completion**: 5 weeks (56.5 hours)  
**Priority**: CRITICAL (enables proper documentation management)

---

**This work item transforms APM's documentation from untracked chaos to a fully managed, context-aware, lifecycle-driven system that respects database-first architecture and adapts to team needs.**
