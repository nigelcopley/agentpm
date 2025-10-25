# Context Capture UX Analysis

**Date**: 2025-10-17
**Objective**: Understand why only 16 of 106 work items (15%) have contexts and fix the adoption barrier

## Executive Summary

**Current State**: 15% context adoption (16/106 work items with contexts)
**Primary Issue**: Context creation is COMPLETELY OPTIONAL with NO prompting
**Root Cause**: Users must remember complex CLI flags manually — no guidance, no defaults, no interactive flow

**Impact**:
- 90 work items operating with ZERO 6W context
- Agents making decisions without WHO/WHAT/WHERE/WHY/WHEN/HOW data
- Context system exists but is essentially unused

---

## 1. Context Creation Flow Analysis

### 1.1 Current CLI Command

```bash
apm work-item create "User Authentication" \
  --type=feature \
  --priority=1 \
  --business-context "Secure user access" \
  --acceptance-criteria '["Users can login", "JWT tokens issued"]' \
  --who "Small business owners" \
  --what "OAuth2 authentication system" \
  --where "auth-service, user-api, frontend" \
  --when "Q2 2025" \
  --why "Protect user data, Enable personalization" \
  --how "OAuth2 flow, JWT tokens, Redis session store"
```

**Problems**:
1. ✅ 6W flags exist (`--who`, `--what`, `--where`, `--when`, `--why`, `--how`)
2. ❌ ALL flags are **optional** — no validation, no prompts
3. ❌ NO guidance on what to enter
4. ❌ NO defaults based on work item type
5. ❌ NO interactive questionnaire mode
6. ❌ Requires memorizing 6 flags + JSON syntax for criteria

### 1.2 What Actually Happens

**Creation Flow** (lines 276-308 in `work_item/create.py`):
```python
# Only creates context IF any 6W fields provided
if any([six_w_who, six_w_what, six_w_where, six_w_when, six_w_why, six_w_how]):
    # Create UnifiedSixW structure
    six_w_data = UnifiedSixW(...)
    context = Context(...)
    context_methods.create_context(db, context)
```

**Result**:
- If user forgets flags → NO context created
- If user provides 1 field → Partial context (low quality)
- System never prompts for missing information

### 1.3 Update Flow

**Current Update Command** (lines 41-172 in `work_item/update.py`):
```bash
apm work-item update 5 --name "New name" --priority 2
```

**Problems**:
❌ NO `--who`, `--what`, `--where`, `--when`, `--why`, `--how` flags
❌ Cannot add or update 6W context after creation
❌ Must use raw metadata JSON manipulation (expert-level only)

---

## 2. Context Update Commands

### 2.1 Available Commands

```bash
# General context commands
apm context show --work-item-id=5    # View existing context
apm context refresh --work-item-id=5  # Regenerate (plugin-based)
apm context status                    # Freshness metrics

# Rich context (for ideas, not work items)
apm idea context 5                    # View idea context
apm idea add-context 5 ...            # Add rich context
```

**Problems**:
❌ NO `apm work-item add-context` command
❌ NO `apm work-item update-context` command
❌ NO interactive context editor
❌ Rich context commands only work for ideas, not work items

---

## 3. Automatic Context Extraction

### 3.1 Current Auto-Extraction

**Source**: `agentpm/core/context/assembly_service.py`

```python
def assemble_work_item_context(self, work_item_id: int) -> dict:
    """Assembles context from existing data"""
    # Pulls from:
    # 1. Work item metadata (business_context, acceptance_criteria)
    # 2. Project-level context
    # 3. Plugin-detected patterns
    # 4. Existing 6W context (if created at creation time)
```

**What It Does**:
✅ Reads existing context from database
✅ Merges hierarchical context (project → work item)
✅ Calculates confidence scores

**What It DOESN'T Do**:
❌ Extract 6W from description field
❌ Extract 6W from business_context field
❌ Suggest missing context fields
❌ Auto-populate based on work item type

### 3.2 Smart Defaults by Type

**Current Reality**: ZERO smart defaults

**What Should Happen**:

| Work Item Type | Auto-Populated Fields |
|----------------|-----------------------|
| **feature** | WHO: From acceptance criteria, WHAT: Feature name, WHERE: Affected services from metadata |
| **bugfix** | WHY: Bug description, WHERE: Affected code paths, WHEN: Priority-based urgency |
| **research** | WHAT: Research question, WHY: Business value, HOW: Research methodology |
| **planning** | WHAT: Planning scope, WHY: Strategic value, WHEN: Planning timeline |

**Gap**: None of this exists

---

## 4. Barriers to Adoption

### 4.1 Cognitive Load

**Problem**: Users must remember:
- 6 different CLI flags (`--who`, `--what`, `--where`, `--when`, `--why`, `--how`)
- JSON syntax for acceptance criteria
- Context model structure
- When to use which flag

**Evidence**:
```bash
# Typical user behavior (90 work items):
apm work-item create "Add OAuth2" --type=feature

# What they SHOULD do but don't:
apm work-item create "Add OAuth2" --type=feature \
  --who "Enterprise customers" \
  --what "OAuth2 authentication" \
  --where "auth-service" \
  --when "Q2 2025" \
  --why "Security compliance" \
  --how "OAuth2 flow with JWT"
```

### 4.2 Visibility Problem

**Problem**: Users don't see the value of 6W context

**Evidence**:
- No warnings when context is missing
- No quality scores shown during creation
- No "context completeness" indicator in `apm status`
- Agent failures don't explicitly mention missing context

### 4.3 Workflow Friction

**Problem**: Context creation is ONE-TIME ONLY at creation

**User Journey**:
1. User creates work item quickly: `apm work-item create "Feature" --type=feature`
2. Later realizes they need more context
3. Tries `apm work-item update 5 --who "Users"` → **FAILS** (command doesn't exist)
4. Tries `apm context update 5` → **FAILS** (command doesn't exist)
5. Gives up → 90 work items with NO context

### 4.4 Discovery Problem

**Problem**: Users don't know 6W context exists

**Evidence**:
```bash
apm work-item create --help
# Shows 46 lines of help text
# 6W flags buried at lines 52-79
# No examples showing 6W usage prominently
```

---

## 5. Data Quality Analysis

### 5.1 Context Distribution

```sql
-- 106 total work items
-- 16 with contexts (15%)
-- 90 without contexts (85%)

SELECT
  COUNT(*) as total,
  AVG(CASE WHEN six_w_data IS NOT NULL THEN 1 ELSE 0 END) as has_6w_pct,
  AVG(confidence_score) as avg_confidence
FROM contexts
WHERE entity_type = 'work_item';

-- Results: 15% have 6W data, avg confidence 0.81
```

### 5.2 Context Quality

**Work Items WITH Context** (sample):

| WI ID | Confidence | Band | 6W Completeness |
|-------|-----------|------|-----------------|
| 3 | 0.885 | GREEN | ✅ All 6W fields populated |
| 25 | 0.96 | GREEN | ✅ All 6W fields + rich metadata |
| 40 | NULL | NULL | ⚠️ Legacy format (who/what/where strings) |
| 46 | 0.96 | GREEN | ✅ All 6W fields populated |
| 59 | 0.70 | YELLOW | ⚠️ Missing some 6W fields |

**Pattern**: When context exists, it's usually HIGH QUALITY (avg 0.81 confidence)
**Issue**: It just doesn't exist for 85% of work items

---

## 6. Recommended Solutions

### 6.1 HIGH PRIORITY: Interactive Context Builder

**Create**: `apm work-item context-wizard <id>`

```bash
$ apm work-item context-wizard 5

╭─── Context Wizard: WI-5 "Add OAuth2" ───╮
│                                           │
│ Let's capture the 6W context for this    │
│ work item to help agents understand it.  │
│                                           │
│ ✅ WHO: Who is this for?                 │
│    → Enterprise customers, developers    │
│                                           │
│ ✅ WHAT: What is being built?            │
│    → OAuth2 authentication system        │
│                                           │
│ ⏭️  WHERE: Which services/components?    │
│    [Press Enter to skip, type to add]    │
│    → auth-service, user-api              │
│                                           │
│ ... (continues through all 6W)           │
│                                           │
│ Context Completeness: ████████░░ 80%     │
│ Confidence Score: 0.85 (GREEN)           │
│                                           │
│ [S]ave  [C]ancel  [P]review              │
╰───────────────────────────────────────────╯
```

**Features**:
- ✅ Interactive prompts with examples
- ✅ Smart defaults based on work item type
- ✅ Skip optional fields
- ✅ Real-time completeness feedback
- ✅ Can be run AFTER work item creation
- ✅ Can update existing context

**Implementation**:
```python
# agentpm/cli/commands/work_item/context_wizard.py
@click.command()
@click.argument('work_item_id', type=int)
@click.option('--non-interactive', is_flag=True, help='Use smart defaults only')
def context_wizard(work_item_id: int, non_interactive: bool):
    """Interactive 6W context builder for work items"""
    # 1. Load existing work item + context (if any)
    # 2. Show current completeness score
    # 3. Prompt for missing fields with smart defaults
    # 4. Validate + save context
    # 5. Show before/after confidence scores
```

### 6.2 HIGH PRIORITY: Auto-Extract from Description

**Add**: `apm work-item extract-context <id>`

```bash
$ apm work-item create "Add OAuth2 authentication for enterprise customers" \
  --type=feature \
  --description "Implement OAuth2 flow with JWT tokens for auth-service and user-api"

✅ Work item created: Add OAuth2 authentication for enterprise customers

🤖 AI Context Extraction:
   Detected WHO: enterprise customers
   Detected WHAT: OAuth2 authentication
   Detected WHERE: auth-service, user-api
   Detected HOW: OAuth2 flow with JWT tokens

   Accept extracted context? [Y/n]: Y

✅ Context created with confidence 0.75 (YELLOW)
💡 Run `apm work-item context-wizard 5` to improve context quality
```

**Implementation**:
```python
# agentpm/core/context/extraction.py
def extract_6w_from_text(text: str, work_item_type: str) -> UnifiedSixW:
    """
    Use NLP patterns to extract 6W from free-form text

    Patterns:
    - WHO: "for {users}", "customers", "developers", "@mentions"
    - WHAT: Nouns in title/description
    - WHERE: Service names, file paths, component names
    - WHEN: Dates, quarters, "before X", "after Y"
    - WHY: "because", "to enable", "for compliance"
    - HOW: Technical terms, patterns, frameworks
    """
```

### 6.3 HIGH PRIORITY: Context Quality Gates

**Add warnings when context is missing/incomplete**:

```bash
$ apm work-item validate 5

⚠️  Work Item Quality Issues:
   ❌ Missing 6W context (0% complete)
   ⚠️  No WHO specified (who is this for?)
   ⚠️  No WHY specified (what's the business value?)

   Impact: Agents will make decisions with limited context

   Fix: apm work-item context-wizard 5

$ apm work-item start 5

⚠️  Warning: This work item has LOW context quality (0.0)
   Agents may struggle without 6W context.

   Would you like to add context now? [Y/n]: Y
   [Launches context wizard]
```

### 6.4 MEDIUM PRIORITY: Update Command Enhancement

**Add 6W flags to update command**:

```bash
# Current (BROKEN):
apm work-item update 5 --who "Enterprise customers"  # ❌ Flag doesn't exist

# Proposed (WORKING):
apm work-item update 5 --who "Enterprise customers"  # ✅ Updates 6W context
apm work-item update 5 --add-implementer "@alice"   # ✅ Adds to WHO
apm work-item update 5 --add-service "auth-api"     # ✅ Adds to WHERE
```

**Implementation**:
```python
# agentpm/cli/commands/work_item/update.py (add after line 35)
@click.option('--who', 'six_w_who', help='Update WHO dimension')
@click.option('--what', 'six_w_what', help='Update WHAT dimension')
@click.option('--where', 'six_w_where', help='Update WHERE dimension')
@click.option('--when', 'six_w_when', help='Update WHEN dimension')
@click.option('--why', 'six_w_why', help='Update WHY dimension')
@click.option('--how', 'six_w_how', help='Update HOW dimension')
def update(ctx, work_item_id, ..., six_w_who, six_w_what, ...):
    # Update or create context if 6W fields provided
    if any([six_w_who, six_w_what, ...]):
        context = get_entity_context(db, EntityType.WORK_ITEM, work_item_id)
        if context:
            # Update existing context
            update_context_6w(db, context.id, ...)
        else:
            # Create new context
            create_context_6w(db, work_item_id, ...)
```

### 6.5 MEDIUM PRIORITY: Smart Defaults by Type

**Auto-populate based on work item type**:

```python
# agentpm/core/context/defaults.py
DEFAULT_6W_BY_TYPE = {
    WorkItemType.FEATURE: {
        'who': ['end_users', 'developers'],  # Extract from acceptance criteria
        'what': 'derived_from_name',         # Use work item name
        'where': 'derived_from_metadata',    # Extract from artifacts.code_paths
        'why': 'derived_from_business_context',
    },
    WorkItemType.BUGFIX: {
        'why': 'Fix critical bug impacting users',
        'where': 'derived_from_description',  # Extract service names
        'when': 'Urgent (P1/P2) or Normal (P3+)',
    },
    WorkItemType.RESEARCH: {
        'what': 'derived_from_name',
        'why': 'derived_from_business_context',
        'how': 'Research methodology TBD',
    }
}
```

### 6.6 LOW PRIORITY: Visibility Improvements

**Show context quality in status commands**:

```bash
$ apm status

📊 Project Health: aipm-v2
   ✅ Work Items: 106 total
   ⚠️  Context Quality: 15% have 6W context (16/106)

   Needs Context: 90 work items
   Top Priority: WI-72, WI-83, WI-95 (active features)

   💡 Improve: apm work-item context-wizard <id>

$ apm work-item list

ID   Name                        Type      Status    Context
---  --------------------------  --------  --------  -----------
72   Add user dashboard          feature   active    ❌ 0% (NONE)
83   Implement caching           feature   active    ❌ 0% (NONE)
95   OAuth2 integration          feature   active    ⚠️ 40% (YELLOW)
25   Database migrations         enhance   active    ✅ 96% (GREEN)
```

### 6.7 LOW PRIORITY: Documentation & Examples

**Add prominent 6W examples to help**:

```bash
$ apm work-item create --help

Examples:
  # Quick creation (minimal)
  apm work-item create "Add OAuth2" --type=feature

  # With 6W context (RECOMMENDED for agent quality)
  apm work-item create "Add OAuth2" --type=feature \
    --who "Enterprise customers" \
    --what "OAuth2 authentication system" \
    --where "auth-service, user-api" \
    --when "Q2 2025" \
    --why "Security compliance requirement" \
    --how "OAuth2 flow with JWT tokens"

  # Interactive context builder
  apm work-item create "Add OAuth2" --type=feature --interactive
  [Launches context wizard]
```

---

## 7. Implementation Priority

### Phase 1: Immediate (Week 1)
1. ✅ **Context Wizard** (`apm work-item context-wizard <id>`)
   - Interactive prompts for all 6W fields
   - Smart defaults by work item type
   - Can update existing context

2. ✅ **Quality Gates** (warnings when context missing)
   - Add to `apm work-item validate`
   - Add to `apm work-item start`
   - Show in `apm status`

### Phase 2: Quick Wins (Week 2)
3. ✅ **Auto-Extract from Description**
   - NLP patterns to extract 6W from text
   - Run automatically on creation
   - Ask user to confirm extracted values

4. ✅ **Update Command Enhancement**
   - Add 6W flags to `apm work-item update`
   - Support creating context after creation
   - Support incremental updates

### Phase 3: Polish (Week 3)
5. ✅ **Smart Defaults by Type**
   - Auto-populate based on work item type
   - Use existing metadata fields
   - Calculate confidence scores

6. ✅ **Visibility Improvements**
   - Show context quality in `apm status`
   - Add context column to `apm work-item list`
   - Color-code by confidence band

### Phase 4: Optional (Week 4)
7. ✅ **Documentation & Examples**
   - Update help text with prominent 6W examples
   - Create tutorial for context best practices
   - Add troubleshooting guide

---

## 8. Success Metrics

**Target**: 80% context adoption within 1 month of deployment

**Metrics**:
- Context adoption rate: 15% → 80%
- Average confidence score: 0.81 → 0.85+
- Context completeness: 60% → 90% (6W fields populated)
- User complaints about missing context: Track in issues

**Validation**:
```sql
-- Monthly context health check
SELECT
  COUNT(*) as total_work_items,
  SUM(CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END) as with_context,
  ROUND(AVG(c.confidence_score), 2) as avg_confidence,
  SUM(CASE WHEN c.confidence_band = 'GREEN' THEN 1 ELSE 0 END) as green_band
FROM work_items wi
LEFT JOIN contexts c ON c.entity_type = 'work_item' AND c.entity_id = wi.id
WHERE wi.status != 'archived';
```

---

## 9. Technical Debt to Address

### 9.1 Inconsistent Context Models

**Problem**: Work item #40 uses legacy format:
```json
{
  "who": "APM (Agent Project Manager) development team",  // String (old format)
  "what": "Eliminate dual V1/V2 systems",  // String (old format)
  ...
}
```

**New format**:
```json
{
  "end_users": ["enterprise customers"],  // List (new format)
  "implementers": ["@alice"],             // List (new format)
  ...
}
```

**Fix**: Migration script to normalize all contexts to UnifiedSixW format

### 9.2 Missing Context Update API

**Problem**: No Python API for updating context after creation

**Current**:
```python
# Can only create context during work item creation
context = Context(...)
context_methods.create_context(db, context)
```

**Needed**:
```python
# Should support updating existing context
context_methods.update_work_item_context(
    db,
    work_item_id=5,
    who=["enterprise customers"],
    what=["OAuth2 authentication"],
    ...
)
```

### 9.3 No Context Validation

**Problem**: Can save partial/invalid context with no warnings

**Current**: Accepts any 6W data, even if incomplete

**Needed**: Validation rules
```python
def validate_6w_completeness(six_w: UnifiedSixW) -> ValidationResult:
    """
    Validate 6W completeness and quality

    Required fields:
    - WHO: At least 1 end_user OR implementer
    - WHAT: At least 1 functional_requirement
    - WHY: business_value must be non-empty

    Recommended fields:
    - WHERE: At least 1 affected_service
    - WHEN: Either deadline or dependencies_timeline
    - HOW: suggested_approach or existing_patterns
    """
```

---

## 10. Conclusion

**Root Cause**: Context creation is completely optional with no prompting, no defaults, no guidance, and no ability to update after creation.

**Impact**: 85% of work items have NO context, severely limiting agent effectiveness.

**Solution**:
1. **Context Wizard** (interactive prompt)
2. **Auto-extraction** (from description/metadata)
3. **Quality gates** (warnings when missing)
4. **Update commands** (add context after creation)
5. **Smart defaults** (by work item type)

**Expected Outcome**: 80% context adoption, higher quality agent decisions, better user experience.

---

## Appendix A: User Workflows

### Workflow 1: New User (Current Experience)

```bash
# User creates work item quickly
$ apm work-item create "Add OAuth2" --type=feature
✅ Work item created: Add OAuth2

# Agent tries to work on it
$ apm task start 5
🤖 Agent: I need more context. Who is this for? What are the requirements?

# User tries to add context
$ apm work-item update 5 --who "Enterprise customers"
❌ Error: unknown option '--who'

# User gives up → 90 work items with no context
```

### Workflow 2: New User (Proposed Experience)

```bash
# User creates work item quickly
$ apm work-item create "Add OAuth2 authentication for enterprise customers" --type=feature
✅ Work item created: Add OAuth2 authentication for enterprise customers

🤖 AI Context Extraction:
   Detected WHO: enterprise customers
   Detected WHAT: OAuth2 authentication

   Accept extracted context? [Y/n]: Y

✅ Context created (60% complete, YELLOW)
💡 Improve quality: apm work-item context-wizard 5

# Later, user wants to improve context
$ apm work-item context-wizard 5
[Interactive prompts fill in missing fields]

✅ Context updated (95% complete, GREEN)
```

### Workflow 3: Expert User (Current Experience)

```bash
# Expert uses all flags correctly
$ apm work-item create "Add OAuth2" --type=feature \
  --who "Enterprise customers" \
  --what "OAuth2 authentication" \
  --where "auth-service" \
  --when "Q2 2025" \
  --why "Security compliance" \
  --how "OAuth2 flow"

✅ Work item created with context (100% complete, GREEN)

# This works BUT only 10 users know about it
```

---

## Appendix B: Database Schema Reference

```sql
-- contexts table schema
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    context_type TEXT CHECK(context_type IN ('work_item_context', ...)),
    entity_type TEXT CHECK(entity_type IN ('work_item', ...)),
    entity_id INTEGER,
    six_w_data TEXT,  -- JSON: UnifiedSixW structure
    confidence_score REAL CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    confidence_band TEXT CHECK(confidence_band IN ('RED', 'YELLOW', 'GREEN')),
    confidence_factors TEXT,  -- JSON: breakdown of scoring
    context_data TEXT,  -- JSON: rich context for ideas
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    UNIQUE(context_type, entity_type, entity_id)
);

-- UnifiedSixW structure (stored as JSON in six_w_data)
{
  "end_users": ["enterprise customers", "developers"],
  "implementers": ["@alice", "@bob"],
  "reviewers": ["@tech-lead"],
  "functional_requirements": ["OAuth2 flow", "JWT tokens"],
  "technical_constraints": ["Must use existing auth-service"],
  "acceptance_criteria": ["Users can login", "Tokens expire"],
  "affected_services": ["auth-service", "user-api"],
  "repositories": ["aipm-v2"],
  "deployment_targets": ["production"],
  "deadline": "2025-06-30T00:00:00",
  "dependencies_timeline": ["After user-service upgrade"],
  "business_value": "Enable enterprise SSO integration",
  "risk_if_delayed": "HIGH: Blocks enterprise sales",
  "suggested_approach": "OAuth2 with PKCE flow",
  "existing_patterns": ["Existing auth patterns in auth-service"]
}
```

---

**End of Analysis**
