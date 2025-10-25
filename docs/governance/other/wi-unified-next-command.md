# Unified Work Item Next Command - Implementation Summary

## Overview

Redesigned `apm work-item next` to be a unified phase + status progression command that intelligently validates gate requirements and provides helpful feedback.

## Changes Made

### 1. Refactored `agentpm/cli/commands/work_item/next.py`

**Before**: Simple status-only progression (draft→ready→active→review→done→archived)
**After**: Unified phase + status progression with gate validation

**Key Features**:
- ✅ Uses `PhaseProgressionService` for gate validation
- ✅ Type-aware phase sequences (FEATURE: 6 phases, BUGFIX: I1→R1)
- ✅ Rich feedback on gate validation (pass/fail with details)
- ✅ Confidence scoring with color coding (RED/YELLOW/GREEN)
- ✅ Requirements table showing current vs required metrics
- ✅ Suggested fix commands based on missing requirements
- ✅ Next phase requirements and instructions
- ✅ Contextual next steps guidance

### 2. Added Deprecation Warning to `phase-advance`

**File**: `agentpm/cli/commands/work_item/phase_advance.py`

**Changes**:
- Added deprecation notice in docstring
- Added runtime warning displayed to users
- Recommends using `apm work-item next` instead

## User Experience

### Gate Passes - Success Flow

```bash
$ apm work-item next 1

Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL
Current Status: draft

✅ Phase Gate: PASSED

Confidence: 85% (GREEN)

Phase Progression:
  NULL → D1_DISCOVERY
  draft → draft

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements, assess technical feasibility

Required task types:
  • analysis
  • research
  • design

Next Steps:
  apm task list --work-item-id=1  # View tasks
  apm task create "Analysis" --work-item-id=1 --type=analysis
  apm work-item next 1  # Advance when P1_PLAN requirements met
```

### Gate Fails - Helpful Feedback

```bash
$ apm work-item next 1

Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL
Current Status: draft

Checking NULL phase gate requirements...

Requirement              Current  Required  Status
────────────────────────────────────────────────
Business Context        45 chars   50+ chars   ❌
Acceptance Criteria            1          3+   ❌
Risks Identified               0          1+   ❌
6W Context Quality           45%        70%+   ❌

Confidence: 45% (RED)

❌ Phase Gate: FAILED

Missing Requirements:
  • business_context too short (45 chars, need ≥50)
  • Need ≥3 acceptance criteria (found 1)
  • At least 1 risk must be identified (found 0)
  • 6W context confidence too low (45%, need ≥70%)

How to Fix:
  apm work-item update 1 --business-context="[detailed context]"
  apm work-item update 1 --add-acceptance-criterion="[criterion]"
  apm work-item update 1 --add-risk="[risk description]"

  # Try again after fixing requirements:
  apm work-item next 1

When requirements are met:
  Phase: NULL → D1_DISCOVERY
  Status: draft → draft
```

## Technical Implementation

### Architecture

```
CLI Command (next.py)
  ↓
PhaseProgressionService
  ↓
PhaseValidator (type-specific sequences)
  ↓
Gate Validators (D1, P1, I1, R1, O1, E1)
  ↓
PhaseTransitionResult
  ↓
Rich Console Feedback
```

### Key Services Used

1. **PhaseProgressionService**: Orchestrates gate validation and phase advancement
   - `advance_to_next_phase(work_item_id)` - Main entry point
   - `validate_current_gate(work_item_id)` - Gate validation
   - `PHASE_TO_STATUS` - Deterministic phase→status mapping

2. **PhaseValidator**: Type-specific phase sequences
   - `get_next_allowed_phase(work_item)` - Next phase lookup
   - `get_phase_requirements(phase, type)` - Phase requirements
   - `PHASE_SEQUENCES` - Type-specific phase sequences

3. **Gate Validators**: Phase-specific validation logic
   - `D1GateValidator` - Discovery phase requirements
   - `P1GateValidator` - Planning phase requirements
   - `I1GateValidator` - Implementation phase requirements
   - `R1GateValidator` - Review phase requirements
   - `O1GateValidator` - Operations phase requirements
   - `E1GateValidator` - Evolution phase requirements

### Data Flow

```python
# 1. Load work item
work_item = wi_methods.get_work_item(db, work_item_id)

# 2. Initialize progression service
progression_service = PhaseProgressionService(db)

# 3. Attempt phase advancement (with gate validation)
result = progression_service.advance_to_next_phase(work_item_id)

# 4. Handle result
if result.success:
    # Show success feedback
    _show_advancement_success(console, work_item, result, progression_service)
else:
    # Show helpful feedback with missing requirements
    _show_gate_failed_feedback(console, work_item, result, progression_service)
```

## Type-Specific Phase Sequences

### FEATURE (Full Lifecycle - 6 Phases)
```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION
   (draft)      (ready)        (active)        (review)      (done)        (archived)
```

### BUGFIX (Fast Track - 2 Phases)
```
I1_IMPLEMENTATION → R1_REVIEW
     (active)        (review)
```

### RESEARCH (Investigation Only - 2 Phases)
```
D1_DISCOVERY → P1_PLAN
   (draft)      (ready)
```

### ENHANCEMENT (Similar to Feature - 5 Phases)
```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → E1_EVOLUTION
   (draft)      (ready)        (active)        (review)    (archived)
```

## Gate Validation Details

### D1_DISCOVERY Gate Requirements

**Required Information**:
- Business context: ≥50 characters
- Acceptance criteria: ≥3 criteria
- Risks: ≥1 identified risk
- 6W context: ≥70% confidence (if available)

**Confidence Calculation**:
- Business context quality: 0-0.25
- Acceptance criteria count: 0-0.25
- Risk assessment: 0-0.25
- Artifacts quality: 0-0.25
- **Total**: 0.0-1.0

**Confidence Thresholds**:
- < 0.50: CRITICAL (red)
- 0.50-0.69: RED (yellow)
- 0.70-0.84: YELLOW (blue)
- ≥ 0.85: GREEN (green)

### P1_PLAN Gate Requirements

**Required Information**:
- Tasks created: ≥1 per work item type
- All tasks have effort estimates
- Dependencies mapped
- Technical design complete

### I1_IMPLEMENTATION Gate Requirements

**Required Information**:
- All implementation tasks completed
- Tests written and passing
- Code documentation complete
- Code review approved

### R1_REVIEW Gate Requirements

**Required Information**:
- Quality review passed
- Acceptance criteria verified
- Stakeholder approval obtained

### O1_OPERATIONS Gate Requirements

**Required Information**:
- Deployment complete
- Monitoring active
- User training complete

### E1_EVOLUTION Gate Requirements

**Required Information**:
- Performance analyzed
- User feedback collected
- Evolution planned

## Migration Strategy

### Phase 1: Soft Deprecation (Current)
- ✅ New `work-item next` command available
- ✅ `phase-advance` shows deprecation warning
- ✅ Both commands work (user choice)

### Phase 2: Strong Deprecation (Future Release)
- Update documentation to recommend `next` only
- Add stronger warnings to `phase-advance`
- Track usage metrics

### Phase 3: Removal (Future Major Version)
- Remove `phase-advance` command
- Keep only `work-item next`

## Testing Strategy

### Manual Testing Checklist

1. **NULL → D1_DISCOVERY**
   - [ ] Create new work item (phase=NULL)
   - [ ] Run `apm work-item next <id>` without meeting requirements
   - [ ] Verify gate fails with helpful feedback
   - [ ] Add requirements (business_context, ACs, risks)
   - [ ] Run `apm work-item next <id>` again
   - [ ] Verify phase advances to D1_DISCOVERY

2. **D1_DISCOVERY → P1_PLAN**
   - [ ] Work item in D1_DISCOVERY phase
   - [ ] Run `apm work-item next <id>`
   - [ ] Verify gate validation checks D1 requirements
   - [ ] Verify phase advances to P1_PLAN when requirements met

3. **Full Lifecycle (FEATURE)**
   - [ ] Test complete FEATURE lifecycle: D1→P1→I1→R1→O1→E1
   - [ ] Verify status changes: draft→ready→active→review→done→archived

4. **Type-Specific Sequences**
   - [ ] Test BUGFIX (I1→R1 only)
   - [ ] Test RESEARCH (D1→P1 only)
   - [ ] Verify type-specific phase sequences work correctly

5. **Error Cases**
   - [ ] Work item not found
   - [ ] Already at final phase
   - [ ] Invalid phase state

6. **UI/UX**
   - [ ] Requirements table displays correctly
   - [ ] Confidence colors match thresholds
   - [ ] Fix suggestions are helpful and accurate
   - [ ] Next steps guidance is clear

### Automated Testing (Future)

```python
# Test gate validation
def test_d1_gate_validation():
    """Test D1 gate validates business_context, ACs, risks"""
    wi = create_work_item(type=FEATURE, phase=NULL)
    result = progression_service.advance_to_next_phase(wi.id)
    assert not result.success
    assert "business_context" in result.missing_requirements

# Test phase advancement
def test_phase_advancement():
    """Test phase advances when gate passes"""
    wi = create_work_item_with_requirements(type=FEATURE, phase=NULL)
    result = progression_service.advance_to_next_phase(wi.id)
    assert result.success
    assert result.new_phase == Phase.D1_DISCOVERY

# Test type-specific sequences
def test_bugfix_sequence():
    """Test BUGFIX only goes through I1→R1"""
    wi = create_work_item(type=BUGFIX, phase=NULL)
    phases = phase_validator.get_allowed_phases(BUGFIX)
    assert phases == [Phase.I1_IMPLEMENTATION, Phase.R1_REVIEW]
```

## Documentation Updates Needed

### User Documentation
- [ ] Update `docs/user-guides/workflow-commands.md` with new `next` command
- [ ] Add examples of gate validation feedback
- [ ] Document phase sequences for each work item type
- [ ] Add troubleshooting guide for common gate failures

### Developer Documentation
- [ ] Document `PhaseProgressionService` API
- [ ] Document gate validator implementation pattern
- [ ] Add architecture diagram showing service integration
- [ ] Document confidence scoring algorithm

### CLI Help
- [x] Updated `apm work-item next --help` docstring
- [x] Added deprecation notice to `apm work-item phase-advance --help`

## Benefits

### User Experience
- **Unified Command**: One command for phase + status progression (simpler)
- **Helpful Feedback**: Clear requirements table, confidence scores, fix suggestions
- **Type-Aware**: Automatically follows correct phase sequence for work item type
- **Guided Workflow**: Next steps suggestions based on current phase

### Code Quality
- **DRY**: Eliminated duplicate phase/status logic
- **Type-Safe**: Strong typing with Phase and WorkItemStatus enums
- **Testable**: Service-based architecture with clear contracts
- **Maintainable**: Single source of truth for phase progression logic

### System Integrity
- **Gate Enforcement**: Cannot bypass requirements without explicit --force
- **Audit Trail**: All phase transitions logged via event system
- **Confidence Tracking**: Quality metrics for information completeness
- **Validation**: Phase sequences enforced at service layer

## Future Enhancements

### Short-Term
1. Implement `--force` mode (skip gate validation)
2. Add `--dry-run` mode (validate without advancing)
3. Show gate validation history (past attempts)

### Medium-Term
1. Interactive mode for fixing requirements (guided prompts)
2. Bulk advancement (multiple work items)
3. Custom gate requirements (project-specific rules)

### Long-Term
1. AI-assisted requirement completion (suggest ACs, risks)
2. Automated evidence collection (from git, Jira, etc.)
3. Predictive confidence scoring (ML-based quality prediction)

## Related Work Items

- WI-60: Context Assembly System (provides 6W confidence)
- WI-373: Phase Gate Validation System (foundation for this work)
- WI-Task: Testing Strategy Implementation (test coverage for gates)

## References

- `agentpm/core/workflow/phase_progression_service.py` - Phase progression logic
- `agentpm/core/workflow/phase_validator.py` - Type-specific sequences
- `agentpm/core/workflow/phase_gates/` - Gate validators (D1-E1)
- `agentpm/cli/commands/work_item/next.py` - Unified CLI command
- `agentpm/cli/commands/work_item/phase_advance.py` - Deprecated command

---

**Status**: Implementation Complete ✅
**Testing**: Manual testing required
**Documentation**: Updates needed
**Deployment**: Ready for testing in dev environment
