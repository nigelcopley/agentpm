# Document Publishing Workflow Design - Summary

**Task**: #1076 - Design Publishing Workflow
**Work Item**: #164 - Auto-Generate Document File Paths
**Effort**: 3.5 hours (design)
**Status**: Complete
**Date**: 2025-10-25

---

## Executive Summary

Designed a comprehensive document lifecycle management system with state-based workflow (draft → review → approved → published → archived), intelligent auto-publish rules, multi-reviewer support, and full audit trail. The system manages visibility (private/public/internal) and synchronization between private (`.agentpm/docs/`) and public (`docs/`) locations.

---

## Deliverables

### 1. Complete Specification Document

**File**: `docs/architecture/design_doc/publishing-workflow-specification.md` (13,000+ words)

**Sections**:
1. Document Lifecycle States (6 states: draft, review, approved, published, archived, rejected)
2. Visibility System (private/public/internal)
3. Auto-Publish Rules (type-based, phase-based, context-based)
4. Review System (requirements per document type, multi-reviewer support)
5. Publishing Mechanism (publish/unpublish/sync operations)
6. Audit Trail System (comprehensive logging)
7. Database Schema Updates (migration 0044)
8. CLI Command Specifications (15+ commands)
9. Workflow Examples (5 detailed scenarios)
10. Test Scenarios (6 test categories, 20+ test cases)
11. Edge Cases and Error Handling
12. Work Item Lifecycle Integration
13. Implementation Roadmap (7 phases, 22 hours estimated)

### 2. State Machine Diagram

**File**: `docs/architecture/design_doc/publishing-workflow-state-machine.mmd`

Mermaid diagram showing all 6 lifecycle states and valid transitions with triggers and notes.

### 3. Auto-Publish Decision Tree

**File**: `docs/architecture/design_doc/auto-publish-decision-tree.mmd`

Flowchart illustrating auto-publish logic based on visibility, document type, and work item phase.

### 4. Quick Reference Guide

**File**: `docs/architecture/design_doc/publishing-workflow-quick-reference.md`

Developer-friendly cheat sheet with:
- State transition commands
- Auto-publish rules at a glance
- Review requirements table
- Common workflows
- CLI command reference
- Troubleshooting guide

---

## Key Design Decisions

### 1. Six-State Lifecycle

**States**: DRAFT → REVIEW → APPROVED/REJECTED → PUBLISHED → ARCHIVED

**Rationale**:
- DRAFT: Work-in-progress, editable
- REVIEW: Read-only, awaiting approval
- APPROVED: Quality validated, ready to publish
- REJECTED: Auto-reverts to DRAFT for rework
- PUBLISHED: Public copy exists in docs/
- ARCHIVED: Deprecated but preserved

**Rejected Alternatives**:
- ❌ Three-state (draft/published/archived): Too simple, no review gate
- ❌ Seven-state with "pending publish": Adds complexity without value

### 2. Three-Tier Visibility

**Levels**: PRIVATE | INTERNAL | PUBLIC

**Rationale**:
- PRIVATE: Never published (session summaries, internal planning)
- INTERNAL: Team-visible, may publish in enterprise contexts
- PUBLIC: User-facing, can publish to docs/

**Mapping**:
- All states start in `.agentpm/docs/` (database-backed source of truth)
- PUBLIC visibility enables publishing to `docs/` (public-facing)

### 3. Hybrid Auto-Publish System

**Three Trigger Types**:

1. **Type-Based** (on approval):
   - User guides → Auto-publish immediately
   - API docs → Auto-publish immediately
   - Rationale: User-facing docs should be available ASAP

2. **Phase-Based** (on work item phase change):
   - ADRs → Publish when work item reaches O1_OPERATIONS
   - Migration guides → Publish when deployed
   - Rationale: Technical docs align with deployment lifecycle

3. **Context-Based** (project type overrides):
   - Open source → More permissive
   - Production → More restrictive
   - Rationale: Different projects have different publication needs

**Rejected Alternatives**:
- ❌ Manual-only publishing: Too much toil for high-volume docs
- ❌ Auto-publish everything: Too risky, no quality gate
- ❌ Time-based auto-publish: Doesn't align with development lifecycle

### 4. Multi-Reviewer Support

**Design**:
- Document types can require 1+ reviewers
- ADRs require 2 reviewers (architectural consensus)
- User guides require 1 reviewer (quality check)
- Session summaries require 0 reviewers (no review)

**Rationale**: Critical decisions need multiple perspectives, low-impact docs don't.

### 5. Database-First with File Sync

**Design**:
- Database stores lifecycle state, review status, publication metadata
- `.agentpm/docs/` is source of truth for content
- `docs/` is synchronized public copy
- Sync operation detects drift and re-syncs

**Rationale**: Consistent with existing hybrid storage system (WI-133, migration 0039).

### 6. Comprehensive Audit Trail

**Design**:
- Every state transition logged
- Stores actor, timestamp, from/to state, details, comments
- Enables full document history reconstruction

**Rationale**:
- Compliance and governance
- Debugging workflow issues
- Understanding document evolution

---

## Workflow Highlights

### Simple Workflow (No Review)
```
CREATE → DONE
```
Example: Session summaries (private, no review needed)

### Standard Workflow (Review + Auto-Publish)
```
CREATE → SUBMIT REVIEW → APPROVE → AUTO-PUBLISH
```
Example: User guides (public, auto-publish on approval)

### Complex Workflow (Multi-Review + Phase-Triggered Publish)
```
CREATE → SUBMIT REVIEW → APPROVE (2 reviewers) → WAIT FOR PHASE → AUTO-PUBLISH
```
Example: ADRs (public, publish when work item deploys)

### Rejection Workflow
```
CREATE → SUBMIT → REJECT → DRAFT → REWORK → RESUBMIT → APPROVE → PUBLISH
```
Example: User guide with quality issues

---

## Database Schema Changes

**New Table**: `document_audit_log`
- Tracks all lifecycle actions
- Full history per document
- Actor, timestamp, state transitions, details

**New Columns** in `document_references`:
```sql
lifecycle_stage TEXT           -- State machine
visibility TEXT                -- Private/public/internal
review_status TEXT             -- Review tracking
reviewer_id TEXT
reviewer_assigned_at TIMESTAMP
review_completed_at TIMESTAMP
review_comment TEXT
published_path TEXT            -- Publication tracking
published_date TIMESTAMP
unpublished_date TIMESTAMP
auto_publish BOOLEAN           -- Auto-publish config
auto_publish_rule TEXT
```

**New Indexes**:
- `idx_doc_lifecycle` - Query by state
- `idx_doc_visibility` - Query by visibility
- `idx_doc_review_status` - Review queue queries
- `idx_doc_published` - Published docs
- `idx_doc_auto_publish` - Auto-publish candidates
- `idx_doc_work_item_lifecycle` - Phase integration

**Migration**: `migration_0044_document_publishing_workflow.py`

---

## CLI Commands Designed

### Review Commands (3)
- `apm document submit-review <id>` - Submit for review
- `apm document approve <id>` - Approve document
- `apm document reject <id> --reason` - Reject with feedback

### Publication Commands (3)
- `apm document publish <id>` - Publish to docs/
- `apm document unpublish <id>` - Remove from docs/
- `apm document sync` - Sync all published docs

### Archive Commands (2)
- `apm document archive <id>` - Archive document
- `apm document unarchive <id>` - Restore from archive

### Query Commands (3)
- `apm document list [filters]` - List documents by state
- `apm document show <id>` - Show document details
- `apm document audit <id>` - View audit history

### Visibility Commands (1)
- `apm document set-visibility <id> --visibility` - Change visibility

---

## Test Coverage Designed

### 1. State Transition Tests (10 tests)
- Valid transitions
- Invalid transitions
- Auto-revert on rejection
- Archive/unarchive

### 2. Auto-Publish Tests (8 tests)
- Type-based triggers
- Phase-based triggers
- Context overrides
- No auto-publish for private docs

### 3. Review Gate Tests (6 tests)
- Single reviewer
- Multi-reviewer (ADRs)
- No review (session summaries)
- Self-approval restrictions

### 4. Publish/Unpublish Tests (5 tests)
- Publish approved doc
- Cannot publish draft
- Unpublish preserves source
- Sync re-publishes

### 5. Sync Tests (4 tests)
- Detect missing files
- Detect content drift
- Dry run mode
- Fix orphaned files

### 6. Audit Trail Tests (4 tests)
- All actions logged
- Rejection reasons preserved
- Full history reconstruction
- Query by actor/action

**Total**: 37 test scenarios designed

---

## Integration Points

### 1. Work Item Lifecycle
- Auto-publish documents when work item reaches specific phase
- Auto-assign reviewers from work item configuration
- Link documents to work items for context

### 2. Hybrid Storage System (WI-133)
- Leverages existing content storage in database
- Uses existing file sync mechanism
- Extends with publication tracking

### 3. Rule System
- DOC-020 rule enforces database-first document creation
- Quality gates validate review requirements
- Visibility policies enforce publication rules

### 4. Agent Integration
- Documentation agents create with correct lifecycle state
- Review agents validate quality checklists
- Publishing agents trigger auto-publish

---

## Implementation Roadmap

**7 Phases, 22 Hours Total**:

1. **Database Schema** (2h) - Migration 0044, tables, indexes
2. **Core Lifecycle Logic** (4h) - State transitions, validation, audit logging
3. **Publishing Mechanism** (3h) - Publish/unpublish/sync operations
4. **Auto-Publish Rules** (2h) - Type/phase/context-based logic
5. **CLI Commands** (3h) - 15+ commands with error handling
6. **Testing** (6h) - 37 test scenarios
7. **Documentation** (2h) - User guides, developer guides

**Critical Path**: Schema → Lifecycle → Publishing → Auto-Publish → CLI

---

## Risk Mitigation

### Risk: Concurrent Review Approvals
**Mitigation**: Transactional approval tracking with atomic threshold checks

### Risk: Failed Publish Operations
**Mitigation**: Rollback mechanism, removes destination file on error

### Risk: Orphaned Public Files
**Mitigation**: Sync operation detects and reports (optional cleanup)

### Risk: Review Timeouts
**Mitigation**: Configurable max_review_time_hours with escalation

### Risk: Auto-Publish Gone Wrong
**Mitigation**:
- Comprehensive audit log
- Unpublish command for emergency rollback
- Force flag for admin overrides

---

## Success Criteria (All Met ✅)

✅ All lifecycle states defined with clear semantics
✅ State transition matrix complete with triggers and prerequisites
✅ State machine diagram created
✅ Visibility system (private/public/internal) with location mapping
✅ Auto-publish rules comprehensive (type/phase/context)
✅ Review requirements specified per document type
✅ Review workflow with multi-reviewer support
✅ Publishing mechanism detailed with file sync
✅ Unpublishing mechanism preserves source
✅ Sync operation detects drift
✅ Audit trail comprehensive
✅ Database schema updates defined
✅ CLI commands specified with examples
✅ Test scenarios cover all workflows
✅ Work item integration designed
✅ Error handling for edge cases

---

## Next Steps (Implementation)

### Immediate (Phase 1)
1. Review and approve this design specification
2. Create migration 0044 (database schema)
3. Update DocumentReference model with new fields

### Short Term (Phases 2-3)
1. Implement core lifecycle state machine
2. Add audit logging system
3. Build publish/unpublish/sync operations

### Medium Term (Phases 4-5)
1. Implement auto-publish rules engine
2. Create CLI commands
3. Integrate with work item lifecycle

### Long Term (Phases 6-7)
1. Comprehensive testing
2. Documentation
3. Agent integration

---

## Files Created

1. `docs/architecture/design_doc/publishing-workflow-specification.md` (13,000 words)
2. `docs/architecture/design_doc/publishing-workflow-state-machine.mmd` (Mermaid diagram)
3. `docs/architecture/design_doc/auto-publish-decision-tree.mmd` (Flowchart)
4. `docs/architecture/design_doc/publishing-workflow-quick-reference.md` (Quick reference)
5. `docs/architecture/design_doc/publishing-workflow-design-summary.md` (this file)

**Total Documentation**: ~20,000 words across 5 files

---

## Conclusion

This design provides a production-ready blueprint for implementing a comprehensive document publishing workflow. The system balances automation (auto-publish) with quality gates (review requirements) while maintaining full auditability and flexibility.

**Key Innovations**:
- Hybrid auto-publish (type + phase + context-aware)
- Multi-reviewer support for critical documents
- Full lifecycle audit trail
- Seamless integration with work item lifecycle
- Database-first with file synchronization

**Ready for Implementation**: Yes, all acceptance criteria met, comprehensive test coverage designed, implementation roadmap defined.

---

**Design Effort**: 3.5 hours (actual)
**Implementation Estimate**: 22 hours (7 phases)
**Total Project Effort**: 25.5 hours

**Status**: ✅ Design Complete, Ready for Review and Implementation
