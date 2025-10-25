# Document Publishing Workflow - Design Documentation Index

**Task**: #1076 - Design Publishing Workflow
**Work Item**: #164 - Auto-Generate Document File Paths
**Status**: ✅ Complete
**Date**: 2025-10-25

---

## Overview

This directory contains the complete design specification for the APM (Agent Project Manager) document publishing workflow system. The system manages document lifecycle from creation through publication with automated publishing, quality gates, and comprehensive audit trails.

---

## Documentation Files

### 1. Complete Specification (PRIMARY)

**File**: [publishing-workflow-specification.md](./publishing-workflow-specification.md)

**Size**: 60 KB (13,000+ words)

**Contents**:
- Document lifecycle states and transitions
- Visibility system (private/public/internal)
- Auto-publish rules (type-based, phase-based, context-based)
- Review system with multi-reviewer support
- Publishing/unpublishing/sync mechanisms
- Audit trail system
- Database schema updates (migration 0044)
- CLI command specifications (15+ commands)
- Detailed workflow examples
- Comprehensive test scenarios (37 tests)
- Edge case handling
- Work item lifecycle integration
- Implementation roadmap (22 hours, 7 phases)

**Audience**: Developers, architects, implementers

**Use**: Complete reference for implementation

---

### 2. State Machine Diagram

**File**: [publishing-workflow-state-machine.mmd](./publishing-workflow-state-machine.mmd)

**Format**: Mermaid diagram

**Contents**:
- All 6 lifecycle states (DRAFT, REVIEW, APPROVED, PUBLISHED, ARCHIVED, REJECTED)
- Valid state transitions with triggers
- Who can perform each transition
- Location and visibility per state

**Audience**: All stakeholders

**Use**: Visual reference for workflow states

**Render**: Use Mermaid-compatible viewer or GitHub

---

### 3. Auto-Publish Decision Tree

**File**: [auto-publish-decision-tree.mmd](./auto-publish-decision-tree.mmd)

**Format**: Mermaid flowchart

**Contents**:
- Decision logic for auto-publish triggers
- Visibility checks
- Type-based rules
- Phase-based rules
- Context overrides

**Audience**: Developers, product managers

**Use**: Understanding when documents auto-publish

**Render**: Use Mermaid-compatible viewer or GitHub

---

### 4. Quick Reference Guide

**File**: [publishing-workflow-quick-reference.md](./publishing-workflow-quick-reference.md)

**Size**: 9 KB

**Contents**:
- State transition cheat sheet
- Auto-publish rules at a glance
- Review requirements table
- Common workflows with examples
- CLI command reference
- Troubleshooting guide
- Best practices

**Audience**: Developers, agents, operators

**Use**: Day-to-day workflow reference

---

### 5. Design Summary

**File**: [publishing-workflow-design-summary.md](./publishing-workflow-design-summary.md)

**Size**: 13 KB

**Contents**:
- Executive summary
- Deliverables overview
- Key design decisions with rationale
- Workflow highlights
- Database schema changes
- CLI commands designed
- Test coverage summary
- Integration points
- Implementation roadmap
- Risk mitigation
- Success criteria

**Audience**: Project managers, stakeholders, reviewers

**Use**: Understanding design decisions and scope

---

## Quick Navigation

### I Want To...

**Understand the workflow** → Start with [Quick Reference](./publishing-workflow-quick-reference.md)

**See visual flow** → View [State Machine Diagram](./publishing-workflow-state-machine.mmd)

**Understand auto-publish logic** → View [Auto-Publish Decision Tree](./auto-publish-decision-tree.mmd)

**Implement the system** → Read [Complete Specification](./publishing-workflow-specification.md)

**Review design decisions** → Read [Design Summary](./publishing-workflow-design-summary.md)

**Know when docs auto-publish** → Check Auto-Publish Rules in [Quick Reference](./publishing-workflow-quick-reference.md#auto-publish-rules-when-does-it-publish-automatically)

**Write tests** → See Test Scenarios in [Complete Specification](./publishing-workflow-specification.md#10-test-scenarios)

**Understand database changes** → See Schema Updates in [Complete Specification](./publishing-workflow-specification.md#7-database-schema-updates)

**Learn CLI commands** → See CLI Reference in [Quick Reference](./publishing-workflow-quick-reference.md#cli-commands-reference)

---

## Key Concepts at a Glance

### Lifecycle States (6)

```
DRAFT → REVIEW → APPROVED → PUBLISHED
                    ↓
                 REJECTED → (auto-revert to DRAFT)
                    ↓
                 ARCHIVED
```

### Visibility Levels (3)

- **PRIVATE**: Never published (`.agentpm/docs/` only)
- **INTERNAL**: Team-visible, may publish in enterprise contexts
- **PUBLIC**: User-facing, can publish to `docs/`

### Auto-Publish Triggers (3 Types)

1. **Type-Based**: User guides, API docs → Auto-publish on approval
2. **Phase-Based**: ADRs, migration guides → Auto-publish when work item reaches O1_OPERATIONS
3. **Context-Based**: Open source projects → More permissive rules

### Review Requirements

- **User Guide**: 1 reviewer, 48 hours
- **ADR**: 2 reviewers, 72 hours (architectural consensus)
- **Session Summary**: 0 reviewers (no review)

---

## Implementation Status

### Design Phase: ✅ Complete

- [x] Lifecycle states defined
- [x] State transitions specified
- [x] Auto-publish rules designed
- [x] Review system designed
- [x] Publishing mechanism detailed
- [x] Audit trail specified
- [x] Database schema defined
- [x] CLI commands specified
- [x] Test scenarios created
- [x] Documentation complete

### Implementation Phase: ⏸️ Not Started

**Next Steps**:
1. Review and approve design specification
2. Create migration 0044 (database schema)
3. Implement core lifecycle state machine
4. Build publish/unpublish/sync operations
5. Implement auto-publish rules engine
6. Create CLI commands
7. Write tests
8. Update documentation

**Estimated Effort**: 22 hours (7 phases)

See [Implementation Roadmap](./publishing-workflow-specification.md#14-implementation-roadmap) for details.

---

## Related Documentation

### APM (Agent Project Manager) Core

- **CLAUDE.md**: Main orchestration guide (database-first architecture)
- **Database Schema**: `.agentpm/data.sqlite` (migration 0043 current)
- **Document Storage**: Migration 0039 (hybrid storage system)

### Work Item #164

- **Title**: Auto-Generate Document File Paths
- **Type**: Feature
- **Status**: Draft (in planning)
- **Tasks**: 18 total (this is task #1076)

### Related Features

- **WI-133**: Hybrid Document Storage (completed, migration 0039)
- **DOC-020 Rule**: Database-first document creation (enforced)

---

## Acceptance Criteria Status

✅ All lifecycle states defined with clear semantics
✅ State transition matrix complete with triggers and prerequisites
✅ State machine diagram created
✅ Visibility system (private/public/internal) with location mapping
✅ Auto-publish rules comprehensive (type/phase/context)
✅ Review requirements specified per document type
✅ Publishing/unpublishing mechanisms detailed
✅ Sync operation designed
✅ Audit trail comprehensive
✅ Database schema updates defined
✅ CLI commands specified with examples
✅ Test scenarios cover all workflows and edge cases

**All acceptance criteria met. Design ready for implementation.**

---

## File Sizes

```
publishing-workflow-specification.md   60 KB  (complete reference)
publishing-workflow-quick-reference.md  9 KB  (cheat sheet)
publishing-workflow-design-summary.md  13 KB  (design overview)
publishing-workflow-state-machine.mmd   1 KB  (state diagram)
auto-publish-decision-tree.mmd          1 KB  (decision tree)
```

**Total**: ~84 KB documentation, ~20,000 words

---

## Questions?

### Design Questions

Contact: Task #1076 author (ac-writer agent) or work item owner

### Implementation Questions

See [Complete Specification](./publishing-workflow-specification.md) sections:
- Section 5: Publishing Mechanism (implementation details)
- Section 14: Implementation Roadmap (phases and estimates)
- Section 10: Test Scenarios (testing approach)

### Workflow Questions

See [Quick Reference Guide](./publishing-workflow-quick-reference.md):
- Common workflows section
- CLI commands reference
- Troubleshooting guide

---

**Last Updated**: 2025-10-25
**Design Version**: 1.0.0
**Status**: ✅ Design Complete, Ready for Implementation
