# Backlog Cleanup - Quick Reference Card

**Date**: 2025-10-21 | **Status**: Ready for Execution

---

## TL;DR

```
REVIEWED: 48 work items
CLOSE:    21 items (test/obsolete)
ACTIVATE:  3 items (launch-critical) - OPTIONAL
DEFER:    24 items (v1.1 + v1.2+)

EXECUTION TIME: 30 minutes
IMPACT: Backlog health POOR → EXCELLENT
```

---

## Option 1: Automated Cleanup

```bash
# Execute cleanup script (interactive)
./scripts/backlog-cleanup.sh
```

**What it does**:
1. Closes 21 test/obsolete items
2. Marks WI-133 as DONE
3. Asks about activating WI-142/143/144
4. Tags v1.1 items (12)
5. Archives v1.2+ items (10)

**Time**: 5 minutes interactive + 25 minutes automated

---

## Option 2: Manual Cleanup

### Step 1: Close Test Items (18 items)
```bash
for id in 84 85 86 87 91 92 93 94 95 96 97 98 99 105 106 110 130 136; do
  apm work-item update $id --status=cancelled --note="Test item cleanup"
done
```

### Step 2: Complete Items (1 item)
```bash
apm work-item update 133 --status=done --note="All tasks complete"
```

### Step 3: Close Obsolete (3 items)
```bash
apm work-item update 80 --status=cancelled --note="Feature exists"
apm work-item update 82 --status=cancelled --note="Not needed"
apm work-item update 127 --status=cancelled --note="Merge into WI-128"
```

### Step 4: Activate Launch Items (OPTIONAL)
```bash
apm work-item update 143 --status=ready --priority=1  # E2E Testing (8h)
apm work-item update 144 --status=ready --priority=1  # Live Testing (4h)
apm work-item update 142 --status=ready --priority=1  # orcx Repo (8.5h)
```

---

## Decision Tree

```
START
  │
  ├─ Need quick cleanup only?
  │    └─ Run script, skip activation → DONE in 5 min
  │
  ├─ Launching v1.0 this week?
  │    └─ Run script, activate items → Review WI-142/143/144
  │
  └─ Just reviewing backlog?
       └─ Read docs/planning/status_report/backlog-cleanup-review.md
```

---

## The 3 Launch-Critical Items

| ID | Name | Hours | Include in Launch? |
|----|------|-------|--------------------|
| WI-143 | Preflight E2E Testing | 8.0h | YES - matches Option B QA |
| WI-144 | Live Project Testing | 4.0h | YES - validates real usage |
| WI-142 | orcx Public Repository | 8.5h | MAYBE - needed for public release |

**Total Additional Effort**: 20.5 hours

**Question**: Is v1.0 launch public or private?
- **Public** → Include all 3 items
- **Private** → Skip WI-142, add post-launch

---

## v1.1 Roadmap Snapshot

**Week 1-2**: Testing & Quality (56h)
- WI-139: CLI audit recommendations (48h)
- WI-131: Prevent done task updates (8h)

**Week 3-4**: Docs & UX (72h)
- WI-111: Unified documentation (24h)
- WI-141: Web frontend polish (20h)
- WI-135: Document CLI integration (8h)
- WI-122: Doc quality rules (12h)
- WI-83: Task notes modal (8h)

**Month 2**: Features & Analysis (80h)
- WI-129: System harmony (16h)
- WI-128: Roadmap generation (12h)
- WI-124: LLM standards (24h)
- WI-79: Bug management (16h)
- WI-101: Dashboard modernization (12h)

**Total v1.1**: 208 hours (~5-6 weeks)

---

## Before & After

### Before Cleanup
```
Status: POOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Draft (unknown):  47 items ⚠️
Ready:             1 item
Active:            5 items ✓
Review:            1 item
Done:             58 items ✓
Other:            30 items

Clarity: LOW
```

### After Cleanup
```
Status: EXCELLENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cancelled:        51 items (+21) ✓
Done:             59 items (+1) ✓
Ready:             4 items (+3) ← launch items
Draft (v1.1):     12 items ← managed
Draft (v1.2+):    10 items ← archived
Active:            5 items ✓
Review:            1 item

Clarity: HIGH
```

---

## Success Metrics

**Cleanup Complete When**:
- [ ] 21 items cancelled
- [ ] 1 item marked done (WI-133)
- [ ] 0 test items in backlog
- [ ] v1.1 items documented (12)
- [ ] v1.2+ items archived (10)
- [ ] Backlog health = EXCELLENT

**Launch Ready When** (if activating):
- [ ] WI-142/143/144 activated
- [ ] Tasks created for each
- [ ] Timeline updated
- [ ] Team informed

---

## Files Created

1. **Full Analysis** (21KB)
   `/docs/planning/status_report/backlog-cleanup-review.md`
   - Detailed rationale for all 48 items
   - Effort estimates
   - Task breakdowns
   - Integration with launch plan

2. **Executive Summary** (6KB)
   `/docs/planning/status_report/BACKLOG-CLEANUP-SUMMARY.md`
   - Quick stats
   - Key decisions
   - Approval section

3. **Cleanup Script** (5KB)
   `/scripts/backlog-cleanup.sh`
   - Automated execution
   - Interactive prompts
   - Progress tracking

4. **Quick Reference** (this file)
   `/docs/planning/status_report/BACKLOG-QUICK-REFERENCE.md`
   - One-page overview
   - Decision tree
   - Fast execution

---

## FAQ

**Q: Do I need to activate WI-142/143/144?**
A: Only if launching publicly in next 7 days. Otherwise defer to post-launch.

**Q: What happens to closed items?**
A: Remain in database with cancelled status. Can resurrect if needed.

**Q: Is WI-133 really done?**
A: YES! All 8 tasks complete, feature operational. Just needs status update.

**Q: Can I defer v1.1 items further?**
A: Yes. Prioritize based on user feedback after v1.0 launch.

**Q: How long does cleanup take?**
A: 5-30 minutes depending on method (automated vs manual).

---

## One-Liner Commands

```bash
# Quick status check
apm status

# See what will be closed
apm work-item show 84 87 91 99 133

# Execute full cleanup
./scripts/backlog-cleanup.sh

# Check results
apm work-item list --status=cancelled | tail -25
apm work-item list --status=ready
```

---

## Next Actions

**Immediately**:
1. Review this card
2. Decide: Run cleanup now or review full analysis first?
3. Decide: Activate launch items or defer?

**After Cleanup**:
1. Verify status: `apm status`
2. Create tasks for activated items (if any)
3. Update launch timeline (if activated items)
4. Communicate to team

**Post-Launch**:
1. Begin v1.1 Priority 1 items
2. Adjust based on user feedback
3. Re-prioritize v1.1 backlog

---

**Prepared**: 2025-10-21
**Execution Time**: 5-30 minutes
**Impact**: HIGH (backlog clarity + launch readiness)
**Risk**: LOW (reversible actions)

---

## Print-Friendly Checklist

```
BACKLOG CLEANUP CHECKLIST

Phase 1: Close Items
□ Close 18 test items (84-99)
□ Mark WI-133 as DONE
□ Close WI-80, 82 (obsolete)
□ Close WI-127 (duplicate)

Phase 2: Launch Decision
□ Review WI-142/143/144
□ Decide: Public or private launch?
□ Activate if public launch
□ Create tasks if activated

Phase 3: Document v1.1
□ Tag 12 items for v1.1
□ Archive 10 items for v1.2+
□ Verify backlog health

Phase 4: Communicate
□ Update team on cleanup
□ Share v1.1 roadmap
□ Update launch plan (if changed)

COMPLETE! ✓
```

---

*One page. All the info. Make it happen.*
