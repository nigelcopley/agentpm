# Workflow Health Action Checklist
**Date**: 2025-10-16 | **Sprint**: 7 days | **Goal**: Fix critical bottlenecks

---

## 🚨 CRITICAL ACTIONS (Days 1-6)

### Day 1: Fix Low Active Task Rate (Part 1)
**Problem**: Only 5 tasks (1%) active out of 522 total

- [ ] **1.1 Implement Auto-Activation** (2 hours)
  - [ ] Update `apm task start <id>` to auto-transition draft→active
  - [ ] Add validation: Cannot start a draft task without auto-activation
  - [ ] Test: Create draft task → start → verify status = active
  - **File**: `agentpm/cli/commands/task/start.py`

- [ ] **1.2 Create Work Queue Command** (2 hours)
  - [ ] Implement `apm task next` to show prioritized draft tasks
  - [ ] Sort by: priority (high→low), due_date (soon→later), effort (small→large)
  - [ ] Display: ID, priority, effort, due_date, work_item, title
  - **File**: `agentpm/cli/commands/task/next.py` (NEW)

- [ ] **1.3 Test Auto-Activation** (1 hour)
  - [ ] Create 10 test draft tasks
  - [ ] Run `apm task start <id>` on each
  - [ ] Verify all transition to active
  - [ ] Check: `apm task list --status active` shows 15 tasks (5 + 10)

**Expected Outcome**: Active tasks increase from 5 → 15 (3× improvement)

---

### Day 2: Fix Low Active Task Rate (Part 2)

- [ ] **2.1 Implement Batch Activation** (2 hours)
  - [ ] Create `apm task activate --batch` command
  - [ ] Accept: `--count N` (activate top N from queue)
  - [ ] Accept: `--work-item <id>` (activate all tasks for WI)
  - [ ] Accept: `--priority high` (activate all high-priority tasks)
  - **File**: `agentpm/cli/commands/task/activate.py` (NEW)

- [ ] **2.2 Add Pre-Work Validation** (1 hour)
  - [ ] Update git pre-commit hook
  - [ ] Check: If task file modified, task must be active
  - [ ] Block commit if working on draft/done task
  - **File**: `.git/hooks/pre-commit`

- [ ] **2.3 Batch Activate Priority Tasks** (1 hour)
  - [ ] Run: `apm task next --count 50`
  - [ ] Identify top 50 high-priority tasks
  - [ ] Run: `apm task activate --batch --count 50`
  - [ ] Verify: `apm task list --status active` shows 65 tasks (15 + 50)

**Expected Outcome**: Active tasks increase from 15 → 65 (13× improvement from baseline)

---

### Day 3: Enforce Phase Compliance (Part 1)

**Problem**: 8/12 active work items (67%) lack phase assignment

- [ ] **3.1 Assign Phases to Existing Active Items** (2 hours)
  ```bash
  # Review each work item and assign appropriate phase
  apm work-item show 077  # Review → Assign phase
  apm work-item show 078  # Review → Assign phase
  apm work-item show 074  # Review → Assign phase
  apm work-item show 100  # Review → Assign phase
  apm work-item show 102  # Review → Assign phase
  apm work-item show 103  # Review → Assign phase
  apm work-item show 081  # Review → Assign phase
  apm work-item show 104  # Review → Assign phase
  ```
  - [ ] For each: Analyze work item type and current tasks
  - [ ] Assign phase: D1, P1, I1, R1, O1, or E1
  - [ ] Document rationale in work item description
  - **Expected**: 0/12 active items lack phase

- [ ] **3.2 Update Work Item Validation** (2 hours)
  - [ ] Add rule: "Active work items MUST have phase"
  - [ ] Update `apm work-item validate <id>`
  - [ ] Reject validation if active + no phase
  - **File**: `agentpm/core/workflow/validators.py`

**Expected Outcome**: Phase compliance 33% → 100%

---

### Day 4: Enforce Phase Compliance (Part 2)

- [ ] **4.1 Implement Auto-Phase Assignment** (2 hours)
  - [ ] Update `apm work-item start <id>`
  - [ ] Auto-assign phase based on type:
    - `feature` → P1_plan (start with planning)
    - `bugfix` → I1_implementation (go straight to fix)
    - `enhancement` → P1_plan (plan enhancements)
    - `research` → D1_definition (define research scope)
  - **File**: `agentpm/cli/commands/work_item/start.py`

- [ ] **4.2 Create Phase Transition Command** (2 hours)
  - [ ] Implement `apm work-item next-phase <id>`
  - [ ] Validate gate requirements before transition
  - [ ] Enforce allowed transitions: D1→P1→I1→R1→O1→E1
  - [ ] Update work item phase field
  - **File**: `agentpm/cli/commands/work_item/next_phase.py` (NEW)

- [ ] **4.3 Test Phase Workflow** (1 hour)
  - [ ] Create test work item in P1_plan
  - [ ] Run: `apm work-item next-phase <id>` → I1_implementation
  - [ ] Run: `apm work-item next-phase <id>` → R1_review
  - [ ] Verify: Phase transitions follow D1→P1→I1→R1→O1→E1

**Expected Outcome**: 100% phase compliance + auto-assignment working

---

### Day 5: Complete Task Planning (Part 1)

**Problem**: 11 work items have 0 tasks (cannot execute)

- [ ] **5.1 Identify Work Items Without Tasks** (1 hour)
  ```sql
  SELECT wi.id, wi.name, wi.status
  FROM work_items wi
  LEFT JOIN tasks t ON wi.id = t.work_item_id
  WHERE t.id IS NULL AND wi.status NOT IN ('draft', 'cancelled')
  ORDER BY wi.id;
  ```
  - [ ] Generate list of 11 work items
  - [ ] Review each work item's description and acceptance criteria
  - [ ] Determine if tasks needed or work item should be archived

- [ ] **5.2 Break Down First 5 Work Items** (3 hours)
  - [ ] For each work item:
    - [ ] Review acceptance criteria
    - [ ] Decompose into ≤4h tasks
    - [ ] Create tasks: `apm task create --work-item <id>`
    - [ ] Assign effort, priority, agent
  - [ ] Target: 3-7 tasks per work item
  - [ ] Ensure each task ≤4h (time-boxing compliance)

**Expected Outcome**: 11 orphans → 6 orphans

---

### Day 6: Complete Task Planning (Part 2)

- [ ] **6.1 Break Down Remaining 6 Work Items** (3 hours)
  - [ ] Continue task decomposition
  - [ ] Use same process as Day 5
  - [ ] Focus on implementation-ready tasks

- [ ] **6.2 Add Planning Gate Validation** (2 hours)
  - [ ] Update `apm work-item validate <id>`
  - [ ] Add rule: "Non-draft work items MUST have ≥1 task"
  - [ ] Reject validation if active/ready + no tasks
  - **File**: `agentpm/core/workflow/validators.py`

- [ ] **6.3 Verify Task Planning Complete** (1 hour)
  ```sql
  SELECT COUNT(*) FROM work_items wi
  LEFT JOIN tasks t ON wi.id = t.work_item_id
  WHERE t.id IS NULL AND wi.status NOT IN ('draft', 'cancelled');
  ```
  - [ ] Expected result: 0 work items
  - [ ] Run: `apm status` to verify
  - [ ] Document any remaining orphans with rationale

**Expected Outcome**: 0 work items without tasks

---

## 🔧 SUPPORTING ACTIONS (Days 1-6, Parallel)

### Clean Up Test Data (Ongoing)

- [ ] **A1. Identify Test Work Items** (30 min)
  ```sql
  SELECT id, name FROM work_items WHERE name LIKE '%Test Work Item%';
  ```
  - [ ] Generate list of test entries
  - [ ] Verify they are truly test data (not real work)

- [ ] **A2. Archive or Delete Test Data** (1 hour)
  - [ ] If test data needed: Archive
  - [ ] If test data not needed: Delete
  - [ ] Run: `apm work-item delete <id>` or `apm work-item archive <id>`
  - [ ] Expected: 29 drafts → ~10 drafts (cleanup ~19 test items)

### Update Documentation (Ongoing)

- [ ] **B1. Document New Commands** (1 hour)
  - [ ] `apm task next` usage guide
  - [ ] `apm task activate --batch` usage guide
  - [ ] `apm work-item next-phase` usage guide
  - **File**: `docs/user-guide/commands.md`

- [ ] **B2. Update Workflow Guide** (1 hour)
  - [ ] Add section: "Activating Tasks"
  - [ ] Add section: "Phase-Based Workflow"
  - [ ] Add section: "Task Planning Requirements"
  - **File**: `docs/user-guide/workflow.md`

---

## 📊 VERIFICATION CHECKLIST (Day 7)

### Verification Queries

- [ ] **V1. Active Task Rate**
  ```sql
  SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
      ROUND(SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct
  FROM tasks;
  ```
  - [ ] **Expected**: active ≥ 50 (10%)
  - [ ] **Baseline**: 5 (1%)
  - [ ] **Target Met**: ✅ / ❌

- [ ] **V2. Phase Compliance**
  ```sql
  SELECT
      COUNT(*) as total,
      SUM(CASE WHEN phase IS NULL OR phase = '' THEN 1 ELSE 0 END) as no_phase
  FROM work_items
  WHERE status = 'active';
  ```
  - [ ] **Expected**: no_phase = 0
  - [ ] **Baseline**: 8
  - [ ] **Target Met**: ✅ / ❌

- [ ] **V3. Task Planning**
  ```sql
  SELECT COUNT(*) as orphans
  FROM work_items wi
  LEFT JOIN tasks t ON wi.id = t.work_item_id
  WHERE t.id IS NULL AND wi.status NOT IN ('draft', 'cancelled');
  ```
  - [ ] **Expected**: orphans = 0
  - [ ] **Baseline**: 11
  - [ ] **Target Met**: ✅ / ❌

- [ ] **V4. Draft Backlog**
  ```sql
  SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as draft,
      ROUND(SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct
  FROM tasks;
  ```
  - [ ] **Expected**: draft < 156 (30%)
  - [ ] **Baseline**: 281 (54%)
  - [ ] **Target Met**: ✅ / ❌

### Success Criteria

- [ ] **Active Tasks**: 50+ (10% of total) ✅ / ❌
- [ ] **Phase Compliance**: 100% of active work items ✅ / ❌
- [ ] **Task Planning**: 0 work items without tasks ✅ / ❌
- [ ] **Draft Backlog**: <30% of total tasks ✅ / ❌

### Generate Updated Report

- [ ] **Run Workflow Analysis Again**
  ```bash
  cd /Users/nigelcopley/.project_manager/aipm-v2
  # Run the same analysis script as 2025-10-16
  ```

- [ ] **Compare Metrics**
  | Metric | Before | After | Improvement |
  |--------|--------|-------|-------------|
  | Active Tasks | 5 (1%) | ??? | ??? |
  | Phase Compliance | 4/12 (33%) | ??? | ??? |
  | Task Planning | 80/91 (88%) | ??? | ??? |
  | Draft Backlog | 281 (54%) | ??? | ??? |

- [ ] **Document Lessons Learned**
  - What worked well?
  - What didn't work?
  - What would we do differently?
  - What automation should be prioritized next?

---

## 🎯 SUCCESS DEFINITION

**Sprint Complete When**:
1. ✅ Active tasks ≥ 50 (10× baseline)
2. ✅ Phase compliance = 100%
3. ✅ Task planning = 100%
4. ✅ Draft backlog < 30%
5. ✅ All validation rules enforced
6. ✅ Documentation updated
7. ✅ Verification queries pass

**Next Sprint Focus**:
- Workflow automation (auto-transitions)
- Metrics dashboard (real-time health)
- WIP limits (prevent overload)
- Agent assignment optimization

---

**Created**: 2025-10-16
**Sprint Duration**: 7 days
**Review Date**: 2025-10-23
**Owner**: AIPM Development Team
