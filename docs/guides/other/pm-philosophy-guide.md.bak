# Project Management Philosophy Guide
## How PM Philosophy Guides AI Agent Behavior in AIPM

**Purpose:** Prevent overengineering by establishing clear project management constraints
**Key Insight:** AI agents need boundaries to stay focused and avoid scope creep

---

## Overview

The `ProjectManagementPhilosophy` enum controls how AI agents approach:
- Planning (comprehensive vs minimal)
- Documentation (complete vs just-enough)
- Execution (structured vs iterative)
- Decision-making (upfront vs just-in-time)

**This prevents AI from defaulting to "document everything exhaustively"**

---

## The Four Philosophies

### LEAN: "Build to Learn"

**When to Use:**
- Startups or new initiatives
- Uncertain requirements
- Need fast validation
- Limited budget/time

**AI Agent Behavior:**
```yaml
Planning:
  - Create Micro-MVP (1-2 weeks)
  - Defer everything not essential
  - Validate before expanding

Documentation:
  - README + Quick Start only
  - No comprehensive specs until validated
  - Code is documentation

Execution:
  - Ship smallest possible feature
  - Measure actual usage
  - Iterate based on data

Decision Making:
  - Decide just-in-time
  - Prefer reversible decisions
  - Document decisions, not possibilities
```

**Example Projects:**
- AIPM Micro-MVP (fix session hooks, validate in 2 weeks)
- New product validation
- Proof of concept

**AI Instructions in Context:**
```
PM Philosophy: LEAN

Constraints for AI:
- Build only what's explicitly requested
- No speculative features
- No comprehensive planning docs
- Validate with working code, not specs
- If unsure about scope: Choose smaller
```

---

### AGILE: "Iterative Excellence"

**When to Use:**
- Software products with evolving requirements
- Teams practicing Scrum/Kanban
- Need flexibility and adaptation
- Regular stakeholder feedback

**AI Agent Behavior:**
```yaml
Planning:
  - Sprint-based (2-week iterations)
  - User stories + acceptance criteria
  - Backlog grooming

Documentation:
  - User stories (as a user, I want...)
  - Acceptance criteria (given/when/then)
  - Sprint retrospectives
  - No heavy upfront specs

Execution:
  - Deliver working increment each sprint
  - Time-boxed tasks (4h max)
  - Daily progress tracking

Decision Making:
  - Defer until needed (last responsible moment)
  - Prefer reversible decisions
  - Retrospect and adapt
```

**Example Projects:**
- SaaS product development
- Web applications
- Mobile apps
- Projects with active user feedback

**AI Instructions in Context:**
```
PM Philosophy: AGILE

Constraints for AI:
- Time-box all tasks (IMPLEMENTATION ≤4h)
- Focus on working software, not perfect software
- Deliver every 2 weeks (sprint)
- Accept changing requirements
- Docs: User stories and acceptance criteria only
```

---

### PMBOK: "Comprehensive Structure"

**When to Use:**
- Enterprise projects
- Regulated industries
- Fixed scope and budget
- Compliance requirements
- Multi-year initiatives

**AI Agent Behavior:**
```yaml
Planning:
  - Comprehensive project plan upfront
  - All phases defined (Initiation → Planning → Execution → Monitoring → Closing)
  - Work Breakdown Structure (WBS)
  - Critical path analysis

Documentation:
  - Project charter
  - Requirements specification
  - Design documents
  - Test plans
  - All deliverables documented

Execution:
  - Follow plan systematically
  - Formal change control
  - Dependency management
  - Risk register maintenance

Decision Making:
  - Architecture Decision Records (ADRs) for all decisions
  - Formal review and approval
  - Complete alternatives analysis
```

**Example Projects:**
- Government contracts
- Healthcare systems (HIPAA compliance)
- Financial systems (SOC 2, PCI DSS)
- Infrastructure projects

**AI Instructions in Context:**
```
PM Philosophy: PMBOK

Constraints for AI:
- Create comprehensive specifications before coding
- Document all architectural decisions (ADRs)
- Analyze all alternatives formally
- Manage dependencies explicitly
- Track critical path
- Formal review gates
```

---

### AIPM_HYBRID: "Pragmatic Balance" (Default)

**When to Use:**
- Complex software projects
- AI-assisted development
- Need structure but not bureaucracy
- Balance speed and quality

**AI Agent Behavior:**
```yaml
Planning:
  - Phased approach (D1→P1→I1→R1→O1→E1)
  - Validation gates between phases
  - Just-enough planning (not comprehensive, not minimal)

Documentation:
  - Evidence-based decisions (link to sources)
  - Key ADRs (not all decisions, just important ones)
  - Working docs (updated as you go)

Execution:
  - Time-boxed tasks (Agile influence: 4h implementation)
  - Dependency tracking (PMBOK influence: critical path)
  - Iterative with structure (both Agile and PMBOK)

Decision Making:
  - Evidence required (sources, confidence scoring)
  - Risk-based review (low risk = auto, high risk = human)
  - Documented but pragmatic
```

**Example Projects:**
- APM (Agent Project Manager) (this project)
- Multi-tenant SaaS platforms
- Complex integrations
- Enterprise software products

**AI Instructions in Context:**
```
PM Philosophy: AIPM_HYBRID (default)

Constraints for AI:
- Phased delivery with validation gates
- Time-box tasks: IMPL ≤4h, TEST ≤6h, DESIGN ≤8h
- Evidence-based decisions (link to sources)
- Risk-based human review (>0.7 risk = human approval)
- Track dependencies for critical path
- Document key decisions (ADRs), not everything
```

---

## How AI Agents Use This

### Session Start (Context Loading)

```python
# .claude/hooks/session-start.py
project = load_project()
pm_philosophy = project.pm_philosophy  # ProjectManagementPhilosophy.LEAN

print(f"PM Philosophy: {pm_philosophy.value.upper()}")

if pm_philosophy == ProjectManagementPhilosophy.LEAN:
    print("Focus: Minimal viable solution, validate fast")
elif pm_philosophy == ProjectManagementPhilosophy.AGILE:
    print("Focus: Working software, time-boxed iterations")
elif pm_philosophy == ProjectManagementPhilosophy.PMBOK:
    print("Focus: Comprehensive planning, formal processes")
else:  # AIPM_HYBRID
    print("Focus: Balanced approach, evidence-based decisions")
```

### Planning Decisions

```python
# AI agent deciding how to plan
def create_implementation_plan(feature, project):
    pm_phil = project.pm_philosophy

    if pm_phil == ProjectManagementPhilosophy.LEAN:
        # Micro-MVP approach
        return {
            "scope": "Smallest possible that demonstrates value",
            "timeline": "1-2 weeks",
            "docs": ["README.md"],
            "validation": "Ship and measure usage"
        }

    elif pm_phil == ProjectManagementPhilosophy.AGILE:
        # Sprint planning
        return {
            "scope": "User stories for 2-week sprint",
            "timeline": "2-week sprint",
            "docs": ["user_stories.md", "acceptance_criteria.md"],
            "validation": "Sprint demo and retrospective"
        }

    elif pm_phil == ProjectManagementPhilosophy.PMBOK:
        # Comprehensive planning
        return {
            "scope": "Complete WBS, all deliverables defined",
            "timeline": "All phases planned upfront",
            "docs": ["charter.md", "requirements.md", "design/", "test_plans/"],
            "validation": "Formal review gates"
        }

    else:  # AIPM_HYBRID
        # Balanced approach
        return {
            "scope": "Core features + validation gates",
            "timeline": "8 weeks, phased",
            "docs": ["spec.md", "key_adrs/", "api_docs/"],
            "validation": "Gate at weeks 2, 4, 6, 8"
        }
```

### Documentation Decisions

```python
# AI agent about to create docs
def should_create_comprehensive_specs(pm_philosophy):
    if pm_philosophy == ProjectManagementPhilosophy.LEAN:
        return False  # Defer docs until validated

    elif pm_philosophy == ProjectManagementPhilosophy.AGILE:
        return False  # User stories only, not specs

    elif pm_philosophy == ProjectManagementPhilosophy.PMBOK:
        return True  # Comprehensive specs required

    else:  # AIPM_HYBRID
        return "PARTIAL"  # Key specs, not everything
```

---

## Setting PM Philosophy

### On Project Init

```bash
# New project with LEAN philosophy
apm init "Startup MVP" --pm-philosophy=lean

# New project with AGILE
apm init "SaaS Product" --pm-philosophy=agile

# New project with PMBOK
apm init "Enterprise System" --pm-philosophy=pmbok

# New project with default (AIPM_HYBRID)
apm init "Complex Project"  # Defaults to aipm_hybrid
```

### Update Existing Project

```bash
# Check current philosophy
apm project show

# Update to LEAN (recommended for AIPM dogfooding)
apm project update --pm-philosophy=lean

# AI agents will now:
# - Prioritize Micro-MVP over comprehensive planning
# - Create minimal docs (not 200,000 words of specs)
# - Validate before expanding
```

### Query Projects by Philosophy

```bash
# Find all LEAN projects
apm project list --pm-philosophy=lean

# Find projects needing comprehensive docs (PMBOK)
apm project list --pm-philosophy=pmbok
```

---

## Philosophy Decision Matrix

| Project Characteristic | LEAN | AGILE | PMBOK | AIPM_HYBRID |
|------------------------|------|-------|-------|-------------|
| **Requirements** | Uncertain | Evolving | Fixed | Mixed |
| **Timeline** | Days-Weeks | Weeks-Months | Months-Years | Weeks-Months |
| **Budget** | Bootstrap | Funded | Enterprise | Moderate |
| **Team Size** | 1-3 | 3-10 | 10-100 | 2-20 |
| **Risk Tolerance** | High | Medium | Low | Medium |
| **Compliance Needs** | None | Low | High | Medium |
| **Documentation** | Minimal | User Stories | Comprehensive | Balanced |
| **Planning Horizon** | Just-in-time | 2-week sprints | All upfront | Phased |

### Recommended by Project Type

**Startup/New Product:**
→ LEAN (validate fast, minimal waste)

**SaaS Product:**
→ AGILE (iterative, user feedback)

**Enterprise/Regulated:**
→ PMBOK (compliance, audit trail)

**Complex AI Project:**
→ AIPM_HYBRID (structure + flexibility)

---

## Real-World Example: This Session

**What Happened:**
```
Project: APM (Agent Project Manager) Dogfooding
PM Philosophy: Not set (defaulted to comprehensive)

Result:
- AI created 11 ADRs (200,000 words)
- Comprehensive 20-week plan
- Overengineered the solution

Problem: No constraints on AI elaboration
```

**What Should Have Happened:**
```
Project: APM (Agent Project Manager) Dogfooding
PM Philosophy: LEAN

Result:
- AI recommends 2-week Micro-MVP immediately
- Defers comprehensive specs until validated
- Focuses on smallest working solution

Benefit: Prevents overengineering, forces validation
```

**Recommendation:**
```bash
# Set AIPM dogfooding to LEAN
cd /Users/nigelcopley/.project_manager/aipm-v2
apm project update --pm-philosophy=lean

# Future sessions will see:
# "PM Philosophy: LEAN - Prioritize Micro-MVP, validate before expanding"

# AI behavior changes:
# - Suggests minimal solutions first
# - Defers comprehensive planning
# - Focuses on working code over specs
```

---

## Migration Guide

### For Existing Projects

**Step 1: Identify Current Approach**
```
Review project:
- Heavy documentation? → Probably PMBOK-leaning
- Sprints and iterations? → Probably Agile
- MVP focus? → Probably Lean
- Mixed? → AIPM_HYBRID
```

**Step 2: Set Philosophy**
```bash
apm project update --pm-philosophy=<choice>
```

**Step 3: Update Context**
```bash
# Refresh context so AI agents see new philosophy
apm context refresh --project
```

**Step 4: Verify**
```bash
# Check context includes philosophy
apm context show --project

# Should show:
# PM Philosophy: lean
# Constraints: Minimal planning, validate fast, eliminate waste
```

---

## Impact on AI Behavior

### Before PM Philosophy

**AI Agent Planning:**
```
User: "Fix the session hooks"

AI: *Creates comprehensive plan*
- Week 1: Provider abstraction interface
- Week 2: Claude Code adapter
- Week 3: Sub-agent framework
- Week 4-5: Compression system
...
- Week 20: Full platform complete

Result: Overengineered, 20 weeks for 2-week fix
```

### After PM Philosophy: LEAN

**AI Agent Planning:**
```
User: "Fix the session hooks"

AI: *Checks PM Philosophy: LEAN*

AI: "LEAN philosophy detected - eliminate waste, MVP focus

Micro-MVP (2 weeks):
- Week 1: Update session-start.py to load context
- Week 2: Update session-end.py to save learnings
- Test with real usage
- Validate: Does this solve the problem?

If yes: Expand
If no: Pivot or stop

Total investment: $7,500
Risk: Minimal"

Result: Appropriately scoped, fast validation
```

---

## Recommendations

### For AIPM Dogfooding Project

**Recommended:** LEAN
```bash
apm project update --pm-philosophy=lean
```

**Why:**
- Uncertain if full platform needed
- Want fast validation (2 weeks)
- Limited initial budget
- Can expand later if validated

### For Enterprise Customers

**Recommended:** PMBOK or AIPM_HYBRID
```bash
apm init "Enterprise System" --pm-philosophy=pmbok
```

**Why:**
- Compliance requirements
- Need audit trail
- Fixed scope/budget
- Formal processes required

### For Product Development

**Recommended:** AGILE
```bash
apm init "SaaS Product" --pm-philosophy=agile
```

**Why:**
- Iterative delivery
- User feedback driven
- Changing requirements
- Sprint-based workflow

---

## Testing the Impact

### Experiment (Recommended)

**Test: Does PM Philosophy actually constrain AI behavior?**

```bash
# Create test project with LEAN
apm init "Test Project" --pm-philosophy=lean

# Ask AI to plan a feature
apm work-item create "User Authentication" --type=feature

# Observe: Does AI suggest Micro-MVP or comprehensive plan?

Expected with LEAN:
- AI suggests: "2-week basic auth (email/password)"
- Defers: OAuth, 2FA, SSO to later phases
- Minimal docs: README only

# Compare: Create another project with PMBOK
apm init "Test Project 2" --pm-philosophy=pmbok

# Same feature request
Expected with PMBOK:
- AI suggests: "Comprehensive auth system"
- Includes: All auth methods, complete specs, ADRs
- Full docs: Requirements, design, test plans
```

**This would validate if philosophy actually guides behavior or is just metadata.**

---

## Summary

**Added:** `ProjectManagementPhilosophy` enum with 4 values

**Purpose:** Constrain AI agent behavior to prevent overengineering

**Values:**
- LEAN: Minimal viable, validate fast
- AGILE: Iterative, time-boxed
- PMBOK: Comprehensive, structured
- AIPM_HYBRID: Balanced default

**Recommendation:** Set AIPM dogfooding to LEAN immediately

**Next Test:** See if this actually prevents AI from creating 200,000 words of specs when 2-week fix is enough

---

**Status:** ✅ Enum added and validated
**Next Action:** Test with real project to validate behavioral impact
**Expected Impact:** Prevents overengineering, maintains focus, validates assumptions
