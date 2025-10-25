# Context Capture UX Analysis - Executive Summary

**Analysis Date**: 2025-10-17
**Issue**: Only 16 of 106 work items (15%) have 6W context populated
**Impact**: 85% of work items operating without WHO/WHAT/WHERE/WHY/WHEN/HOW data

---

## Key Findings

### 1. Root Cause: Context is Completely Optional with No Guidance

```bash
# What users do (90 work items):
apm work-item create "Add OAuth2" --type=feature

# What they SHOULD do but don't:
apm work-item create "Add OAuth2" --type=feature \
  --who "Enterprise customers" \
  --what "OAuth2 authentication" \
  --where "auth-service" \
  --when "Q2 2025" \
  --why "Security compliance" \
  --how "OAuth2 flow"
```

**Problems**:
- ❌ All 6W flags are **optional** — no prompts, no validation
- ❌ Users must memorize 6 CLI flags + JSON syntax
- ❌ NO warnings when context is missing
- ❌ NO ability to add context after creation (`--who` flag doesn't exist in update command)
- ❌ NO smart defaults based on work item type
- ❌ NO auto-extraction from description/business_context

### 2. User Workflow Breaks

**Typical User Journey** (90 work items):
1. Create work item quickly: `apm work-item create "Feature" --type=feature`
2. Later realize they need context
3. Try: `apm work-item update 5 --who "Users"` → **FAILS** ❌
4. Try: `apm context update 5` → **FAILS** ❌
5. Give up → Work item has ZERO context forever

### 3. Context Quality When It Exists

**Good News**: When context exists, it's high quality (avg 0.81 confidence, 5/16 are GREEN band)

**Pattern**:
- Users who remember the flags → Excellent context
- Users who forget (85%) → Zero context

---

## Recommended Solutions

### Phase 1: IMMEDIATE (Week 1)

#### 1. Context Wizard (Interactive Builder)
```bash
$ apm work-item context-wizard 5

╭─── Context Wizard: WI-5 "Add OAuth2" ───╮
│ WHO: Who is this for?                    │
│ → Enterprise customers, developers       │
│                                           │
│ WHAT: What is being built?               │
│ → OAuth2 authentication system           │
│                                           │
│ Context Completeness: ████████░░ 80%     │
│ Confidence Score: 0.85 (GREEN)           │
╰───────────────────────────────────────────╯
```

**Features**:
- ✅ Interactive prompts with examples
- ✅ Works AFTER work item creation (fixes update problem)
- ✅ Smart defaults by work item type
- ✅ Real-time completeness feedback

#### 2. Quality Gates (Missing Context Warnings)
```bash
$ apm work-item validate 5
⚠️  Missing 6W context (0% complete)
   ❌ No WHO specified
   ❌ No WHY specified
   Fix: apm work-item context-wizard 5

$ apm work-item start 5
⚠️  Warning: Low context quality (0.0)
   Would you like to add context now? [Y/n]
```

### Phase 2: Quick Wins (Week 2)

#### 3. Auto-Extract from Description
```bash
$ apm work-item create "Add OAuth2 authentication for enterprise customers" \
  --type=feature \
  --description "Implement OAuth2 flow in auth-service"

🤖 AI Context Extraction:
   Detected WHO: enterprise customers
   Detected WHAT: OAuth2 authentication
   Detected WHERE: auth-service
   Accept extracted context? [Y/n]: Y

✅ Context created (75% complete, YELLOW)
💡 Improve: apm work-item context-wizard 5
```

#### 4. Update Command Enhancement
```bash
# Add 6W flags to update command:
apm work-item update 5 --who "Enterprise customers"  ✅ WORKS
apm work-item update 5 --why "Security compliance"   ✅ WORKS
```

### Phase 3: Polish (Week 3)

#### 5. Smart Defaults by Type
```python
# Auto-populate based on work item type
WorkItemType.FEATURE → who=['end_users'], what='derived_from_name'
WorkItemType.BUGFIX  → why='Fix bug', where='derived_from_description'
WorkItemType.RESEARCH → what='derived_from_name', how='Research methodology'
```

#### 6. Visibility Improvements
```bash
$ apm status
⚠️  Context Quality: 15% have 6W context (16/106)
   Needs Context: 90 work items
   Top Priority: WI-72, WI-83, WI-95

$ apm work-item list
ID   Name                Type     Status   Context
72   User dashboard      feature  active   ❌ 0% (NONE)
25   DB migrations       enhance  active   ✅ 96% (GREEN)
```

---

## Success Metrics

**Target**: 80% context adoption within 1 month

**Current State**:
- Context adoption: 15% (16/106)
- Avg confidence: 0.81
- Completeness: ~60%

**Target State**:
- Context adoption: 80% (85/106)
- Avg confidence: 0.85+
- Completeness: 90%+

---

## Implementation Files

**Analysis Document**: `docs/analysis/context-capture-ux-analysis.md` (full 50-page analysis)

**Key Files to Modify**:
1. `agentpm/cli/commands/work_item/create.py` (add auto-extraction)
2. `agentpm/cli/commands/work_item/update.py` (add 6W flags)
3. `agentpm/cli/commands/work_item/context_wizard.py` (NEW - interactive builder)
4. `agentpm/cli/commands/work_item/validate.py` (add context warnings)
5. `agentpm/core/context/extraction.py` (NEW - NLP extraction)
6. `agentpm/core/context/defaults.py` (NEW - smart defaults)

---

## Next Steps

1. Review full analysis: `docs/analysis/context-capture-ux-analysis.md`
2. Prioritize solutions (recommend Phase 1 immediate implementation)
3. Create implementation plan with time estimates
4. Build context wizard (highest impact, fixes 85% of problem)
5. Add quality gates (makes problem visible to users)

---

## Technical Debt Discovered

1. **Inconsistent Context Models**: Work item #40 uses legacy string format (`"who": "string"`) instead of UnifiedSixW list format (`"end_users": ["string"]`)

2. **Missing Update API**: No Python method for updating context after creation (only create during work item creation)

3. **No Validation**: Can save partial/invalid context with no warnings

4. **No Context Commands for Work Items**: Rich context commands only work for ideas (`apm idea context`), not work items (`apm work-item context` doesn't exist)

---

**Conclusion**: Context system is well-designed but completely unused due to poor UX. Interactive context wizard + auto-extraction will increase adoption from 15% to 80%.

**Detailed Analysis**: See `docs/analysis/context-capture-ux-analysis.md` for complete findings, user workflows, implementation details, and code examples.
