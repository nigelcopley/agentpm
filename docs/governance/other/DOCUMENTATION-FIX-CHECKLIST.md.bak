# Documentation Fix Checklist

**Based on**: DOCUMENTATION-CONFLICTS-AUDIT-2025-10-18.md
**Status**: 🔴 Not Started
**Last Updated**: 2025-10-18

---

## Phase 1: Critical Fixes (P0) ⏰ **DO FIRST** - Est. 8-12 hours

### 1. V1/V2 Distinction (5 minutes)
- [ ] Add "AIPM V1 LEGACY DOCUMENTATION" banner to `/Users/nigelcopley/.project_manager/CLAUDE.md`
- [ ] Add "APM (Agent Project Manager) ACTIVE DOCUMENTATION" banner to `aipm-v2/CLAUDE.md`

### 2. Fix Broken _RULES/ Links (30 minutes)
- [ ] `docs/components/testing/README.md:493` → Update to `apm rules list -c testing`
- [ ] `docs/components/testing/README.md:494` → Update to `apm rules list -c development`
- [ ] `docs/components/testing/README.md:495` → Update to `apm rules list -c code_quality`
- [ ] `docs/components/security/README.md:516` → Update to `apm rules list -c operational`
- [ ] `docs/components/plugins/README.md:340` → Update to `apm rules list -c architecture`
- [ ] `docs/components/plugins/README.md:341` → Update to `apm rules list -c development`
- [ ] `agentpm/core/agents/definitions/README.md:338` → Update reference
- [ ] `docs/components/hooks/examples/session-start.sh:109` → Update comment

### 3. Reconcile Command Interface (4-6 hours) ⚠️ **REQUIRES DECISION**
- [ ] **STEP 1**: Check actual implementation in `agentpm/cli/commands/task.py`
  - Which commands exist: `validate`, `accept`, `start`, `submit-review`, `approve` OR `next`?
- [ ] **STEP 2**: Choose Pattern A (explicit) or Pattern B (next)
- [ ] **STEP 3**: Update `aipm-v2/CLAUDE.md` to match reality
- [ ] **STEP 4**: Update `docs/components/workflow/next-command-guide.md`
- [ ] **STEP 5**: Update `docs/components/workflow/6-state-workflow-system.md`

### 4. Clarify Database-First Architecture (2-3 hours)
- [ ] `docs/components/rules/README.md:12` → Add init vs runtime distinction
- [ ] `docs/components/rules/README.md:159` → Clarify "YAML Catalog (init-time only)"
- [ ] `docs/components/rules/README.md:244-265` → Add phase separation
- [ ] `docs/components/rules/README.md` → Add "Source of Truth: Database" section
- [ ] `docs/components/rules/comprehensive-rules-system.md:70-73` → Separate init/runtime flows
- [ ] `docs/components/rules/comprehensive-rules-system.md:36` → Update terminology

### 5. Fix /tools/ Path (1 minute)
- [ ] `docs/reports/workflow-health-assessment-2025-10-16.md:436` → Change to `scripts/validation/validate_task.sh`

---

## Phase 2: High Priority (P1) 📋 **DO NEXT** - Est. 6-8 hours

### 6. Standardize Agent Count (1 hour)
- [ ] Find all references to "11 agents" or "46 agents"
- [ ] Replace with "50 agents" throughout V2 docs
- [ ] Update agent structure descriptions to match 3-tier reality

### 7. Update ROADMAP.md (15 minutes)
- [ ] `docs/components/cli/ROADMAP.md:48` → Move `task complete` to ✅ Completed
- [ ] `docs/components/cli/ROADMAP.md:168` → Move `task update` to ✅ Completed
- [ ] Update `work-item update` status

### 8. Fix Phase-State Mapping (1 hour)
- [ ] `docs/components/workflow/6-state-workflow-system.md:181-189` → Correct E1_EVOLUTION mapping
- [ ] Remove `ARCHIVED → E1_EVOLUTION`
- [ ] Add note: "E1_EVOLUTION applies to DONE/O1 work (continuous improvement)"

### 9. Complete Agent Templates (4-6 hours) ⚠️ **OR MARK INACTIVE**
- [ ] **Option A**: Complete `.claude/agents/planner.md` placeholders
  - [ ] Extract patterns from codebase
  - [ ] Define planner-specific quality gates
  - [ ] Add concrete examples
- [ ] **Option B**: Mark as inactive/template
  - [ ] Add "TEMPLATE - NOT ACTIVE" banner
  - [ ] Document intended usage
- [ ] **Repeat for** `.claude/agents/reviewer.md`

---

## Phase 3: Polish (P2-P4) ✨ **NICE TO HAVE** - Est. 4-6 hours

### 10. Create Database Component README (30 minutes)
- [ ] Create `docs/components/database/README.md`
- [ ] Link to `docs/developer-guide/02-three-layer-pattern.md`
- [ ] Document database-first architecture principle

### 11. Skills Integration Clarification (15 minutes)
- [ ] Determine if `/aipm-v2-skill/` is deprecated or active
- [ ] Add status banner to `AIPM-V2-SKILLS-INTEGRATION-SUMMARY.md`
- [ ] Archive if deprecated

### 12. Update Command Counts (5 minutes)
- [ ] `docs/components/cli/README.md:77` → Update to "30+ commands"
- [ ] `docs/components/cli/user-guide.md:13` → Update metadata

### 13-18. Minor Fixes (2-3 hours)
- [ ] Mark internal script in UPDATE-REPORT.md
- [ ] Clarify tests/ vs tests-BAK/ usage
- [ ] Verify agent documentation paths
- [ ] Spot-check Universal Rules placement (sample 5 agents)
- [ ] Update migration guide paths for portability
- [ ] Add note to ADR-001 about rejected alternatives

---

## Validation After Each Phase

### After Phase 1:
```bash
# Verify no _RULES references (except historical)
grep -r "_RULES/" docs/ | grep -v "historical\|migration\|analysis"

# Verify no /tools/ references
grep -r "/tools/" docs/

# Verify command consistency
grep -r "apm task" docs/components/workflow/ | grep -E "validate|accept|start|next"
```

### After Phase 2:
```bash
# Verify agent count standardized
grep -r "11 agents\|46 agents" docs/

# Verify ROADMAP updated
grep "task complete" docs/components/cli/ROADMAP.md

# Verify phase mapping
grep "E1_EVOLUTION" docs/components/workflow/
```

### After Phase 3:
```bash
# Run full documentation audit
find docs/ -name "*.md" -exec grep -l "TODO\|FIXME\|Action needed" {} \;

# Check for broken links
# (Manual review recommended)
```

---

## Progress Tracking

| Phase | Tasks | Completed | Status | Est. Hours | Actual Hours |
|-------|-------|-----------|--------|------------|--------------|
| Phase 1 (P0) | 5 | 0 | 🔴 Not Started | 8-12 | - |
| Phase 2 (P1) | 4 | 0 | ⚪ Pending | 6-8 | - |
| Phase 3 (P2-P4) | 9 | 0 | ⚪ Pending | 4-6 | - |
| **TOTAL** | **18** | **0** | **0%** | **18-26 hours** | **-** |

---

## Notes

**Started**: ___________
**Phase 1 Complete**: ___________
**Phase 2 Complete**: ___________
**Phase 3 Complete**: ___________
**Final Review**: ___________

**Blockers/Issues**:
-
-

**Decisions Made**:
- Command Interface Choice (Pattern A/B): __________
- Agent Template Status (Complete/Inactive): __________
-

---

## Quick Reference

**Audit Report**: `docs/DOCUMENTATION-CONFLICTS-AUDIT-2025-10-18.md`
**This Checklist**: `docs/DOCUMENTATION-FIX-CHECKLIST.md`

**Priority Definitions**:
- **P0 (Critical)**: User-facing errors, broken links, major confusion
- **P1 (High)**: Architectural inconsistencies, misleading information
- **P2 (Medium)**: Missing documentation, minor inconsistencies
- **P3 (Low)**: Polish, nice-to-haves, optimization
- **P4 (Optional)**: Future improvements

**Next Steps After Completion**:
1. Run full documentation audit again
2. Update this checklist with actual hours
3. Add CI checks to prevent regression
4. Consider documentation review process
