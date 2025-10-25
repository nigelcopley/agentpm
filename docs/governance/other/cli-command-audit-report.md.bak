# CLI Command Audit Report

**Date**: 2025-10-17
**Scope**: All 50 agent files in `.claude/agents/`
**Reference**: `docs/CLI-COMMAND-INVENTORY.md`

---

## Executive Summary

**Total Agent Files**: 50
**Files with Issues**: 1
**Commands to Remove**: 16 instances of `apm audit`

### Findings

✅ **CORRECT Commands** (User request was partially incorrect):
- `apm task approve` - EXISTS (lines 663-675)
- `apm task submit-review` - EXISTS (lines 647-661)
- `apm task request-changes` - EXISTS (lines 679-692)
- `apm work-item approve` - EXISTS (lines 316-330)
- `apm work-item submit-review` - EXISTS (lines 300-314)
- `apm work-item request-changes` - EXISTS (lines 332-346)
- `apm work-item phase-validate` - EXISTS (lines 389-399)
- `apm work-item phase-advance` - EXISTS (lines 402-413)
- `apm task next` - EXISTS (lines 723-735)
- `apm work-item next` - EXISTS (lines 363-375)

❌ **NON-EXISTENT Commands** (Need removal):
- `apm audit log` - NOT FOUND
- `apm audit list` - NOT FOUND
- `apm audit show` - NOT FOUND
- `apm audit link` - NOT FOUND

---

## Detailed Analysis

### Commands That Exist (No Changes Needed)

| Command | Location in Inventory | Status |
|---------|----------------------|--------|
| `apm task approve` | Line 663 | ✅ Valid |
| `apm task submit-review` | Line 647 | ✅ Valid |
| `apm task request-changes` | Line 679 | ✅ Valid |
| `apm work-item approve` | Line 316 | ✅ Valid |
| `apm work-item submit-review` | Line 300 | ✅ Valid |
| `apm work-item request-changes` | Line 332 | ✅ Valid |
| `apm work-item phase-validate` | Line 389 | ✅ Valid |
| `apm work-item phase-advance` | Line 402 | ✅ Valid |
| `apm task next` | Line 723 | ✅ Valid |
| `apm work-item next` | Line 363 | ✅ Valid |

### Commands That Don't Exist (Require Removal)

| Command | Usage Count | Files |
|---------|------------|-------|
| `apm audit log` | 10 | `.claude/agents/utilities/audit-logger.md` |
| `apm audit list` | 4 | `.claude/agents/utilities/audit-logger.md` |
| `apm audit show` | 1 | `.claude/agents/utilities/audit-logger.md` |
| `apm audit link` | 2 | `.claude/agents/utilities/audit-logger.md` |

**Total Instances**: 16 (all in single file)

---

## Files Requiring Changes

### 1. `.claude/agents/utilities/audit-logger.md`

**Issue**: Contains 16 references to non-existent `apm audit` commands

**Recommended Action**:
- **Option A**: Remove the file entirely (audit functionality not implemented in CLI)
- **Option B**: Update to use alternative commands:
  - `apm audit log` → `apm summary create` (with type=decision)
  - `apm audit list` → `apm summary list` (with type filter)
  - `apm audit show` → `apm summary show`
  - `apm audit link` → `apm summary create` (with entity linkage)

**Lines to Fix**:
- Line 94: `apm audit log \`
- Line 104-107: `apm audit list` variants
- Line 112: `apm audit show`
- Line 117-118: `apm audit link` variants
- Lines 135, 153, 171, 189, 207, 266, 351, 364: Additional `apm audit log` instances

---

## Recommended Solution

### Immediate Action: Remove Non-Existent Commands

Since `apm audit` commands don't exist and no migration path is documented, recommend:

1. **Delete** `.claude/agents/utilities/audit-logger.md` (audit agent not functional)
2. **Update documentation** to clarify that audit trail is captured via:
   - `apm summary create` for decision records
   - `apm session add-decision` for key decisions
   - Automatic event logging in database

### Alternative: Map to Summary Commands

If audit functionality is needed, remap to existing summary system:

```bash
# Old (non-existent)
apm audit log --work-item-id=123 --type=architecture --decision="..." --rationale="..."

# New (use summary commands)
apm summary create \
  --entity-type=work-item \
  --entity-id=123 \
  --summary-type=decision \
  --content="Decision: ... Rationale: ..." \
  --metadata='{"decision_type": "architecture"}'
```

---

## User Request Clarification

**Original Request**:
> "Replace `apm task approve`, `apm work-item phase-validate`, etc. with `apm task next`"

**Reality**:
- `apm task approve` ✅ EXISTS and is CORRECT (lines 663-675)
- `apm work-item phase-validate` ✅ EXISTS and is CORRECT (lines 389-399)
- `apm task next` ✅ EXISTS but serves DIFFERENT purpose (smart prioritization, not status transition)

**Clarification Needed**:
- `apm task next` gets NEXT task to work on (line 723)
- `apm task approve` APPROVES a task in REVIEW status (line 663)
- These are NOT interchangeable commands

**Recommendation**: Do NOT replace status transition commands with `next` command. They serve different purposes.

---

## Commands Summary

### Workflow State Transitions (Keep These)
```bash
# Task workflow
apm task validate <id>           # PROPOSED → VALIDATED
apm task accept <id> --agent     # VALIDATED → ACCEPTED
apm task start <id>              # ACCEPTED → IN_PROGRESS
apm task submit-review <id>      # IN_PROGRESS → REVIEW
apm task approve <id>            # REVIEW → COMPLETED (by different agent)
apm task request-changes <id>    # REVIEW → IN_PROGRESS (rework)

# Work item workflow
apm work-item validate <id>
apm work-item accept <id> --agent
apm work-item start <id>
apm work-item submit-review <id>
apm work-item approve <id>
apm work-item request-changes <id>
```

### Smart Prioritization (Different Purpose)
```bash
apm task next              # Get next task to work on
apm work-item next         # Get next work item to work on
apm idea next              # Get next idea to review
```

### Phase Management (Keep These)
```bash
apm work-item phase-status <id>      # Show phase gate status
apm work-item phase-validate <id>    # Validate phase advancement
apm work-item phase-advance <id>     # Advance to next phase
```

### Non-Existent (Remove These)
```bash
apm audit log       # ❌ NOT FOUND
apm audit list      # ❌ NOT FOUND
apm audit show      # ❌ NOT FOUND
apm audit link      # ❌ NOT FOUND
```

---

## Conclusion

**Action Required**: Remove 1 file with non-existent commands

**No Action Required**: 49 agent files use correct, existing CLI commands

**User Request Status**: Partially incorrect - most commands mentioned actually exist and are valid
