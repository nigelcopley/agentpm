# Web Interface Coverage Analysis
## All Models and Fields - What's Surfaced vs What's Missing

**Date:** 2025-10-12
**Purpose:** Ensure all database models and fields are accessible via web interface
**Current Web Framework:** Flask

---

## Database Tables (20 tables)

### Currently Surfaced in Web Interface ✅

1. **projects** - ✅ PARTIAL
   - Route: `/projects`
   - Shows: name, description, work_item count, task count, agent count
   - Missing: tech_stack, pm_philosophy, created_at, metadata

2. **work_items** - ✅ GOOD
   - Routes: `/work-items`, `/work-item/<id>`
   - Shows: name, type, status, priority, description, tasks, progress
   - Missing: phase, business_context, ownership, scope, artifacts

3. **tasks** - ✅ GOOD
   - Routes: `/tasks`, `/task/<id>`
   - Shows: name, type, status, effort, priority, dependencies, blockers
   - Missing: assigned_to (agent), code_files, patterns

4. **work_item_summaries** - ✅ EXISTS
   - Route: `/work-item/<id>/summaries`
   - Shows: session history, temporal context
   - Coverage: Good

### Partially Surfaced (Need Enhancement) ⚠️

5. **agents** - ⚠️ MINIMAL
   - Referenced in project list (count only)
   - Missing: Full agent list view, agent detail, capabilities, tools, examples

6. **rules** - ⚠️ MINIMAL
   - Referenced in project list (count only)
   - Missing: Rules list, rule detail, enforcement levels

7. **task_dependencies** - ⚠️ PARTIAL
   - Shown in task detail
   - Missing: Dependency graph visualization, critical path

8. **task_blockers** - ⚠️ PARTIAL
   - Shown in task detail
   - Missing: Blockers dashboard, resolution tracking

### NOT Surfaced (Need to Add) ❌

9. **sessions** - ❌ NOT SURFACED
   - Model exists: SessionTool, LLM model, duration, metadata
   - Need: Sessions list, session detail, timeline view, provider analytics

10. **contexts** - ❌ NOT SURFACED
    - Model exists: 6W data, confidence scoring, freshness
    - Need: Context viewer, confidence dashboard, staleness alerts

11. **evidence_sources** - ❌ NOT SURFACED
    - Model exists: URL, excerpt, confidence, source_type
    - Need: Evidence list, source verification, confidence tracking

12. **document_references** - ❌ NOT SURFACED
    - Model exists: file_path, document_type, title, format
    - Need: Document browser, search interface, lifecycle tracking

13. **ideas** - ❌ NOT SURFACED
    - Model exists (CLI works: `apm idea list`)
    - Need: Ideas dashboard, voting interface, workflow transitions

14. **events** - ❌ NOT SURFACED
    - Model exists: event types, workflow transitions, audit trail
    - Need: Audit log viewer, timeline, event search

15. **session_events** - ❌ NOT SURFACED
    - Links sessions to events
    - Need: Session activity log

16. **agent_examples** - ❌ NOT SURFACED
    - Agent usage examples
    - Need: Examples browser, agent documentation

17. **agent_relationships** - ❌ NOT SURFACED
    - Agent hierarchies and collaborations
    - Need: Agent relationship diagram

18. **agent_tools** - ❌ NOT SURFACED
    - Tools available to agents
    - Need: Tool capability matrix

19. **work_item_dependencies** - ❌ NOT SURFACED
    - Work item level dependencies
    - Need: Portfolio dependency view

20. **schema_migrations** - ❌ NOT SURFACED
    - Migration history
    - Need: Schema version viewer, migration log

---

## Coverage Matrix

| Table | Web Coverage | Missing Fields/Views | Priority |
|-------|--------------|---------------------|----------|
| projects | 40% | pm_philosophy, tech_stack, metadata | 🔴 High |
| work_items | 70% | phase, ownership, scope, artifacts | 🟡 Medium |
| tasks | 75% | assigned_to, code_files, patterns | 🟡 Medium |
| work_item_summaries | 90% | (good coverage) | 🟢 Low |
| agents | 20% | Full agent CRUD, capabilities, SOPs | 🔴 High |
| rules | 20% | Full rules CRUD, enforcement tracking | 🟡 Medium |
| task_dependencies | 50% | Graph visualization, critical path | 🟡 Medium |
| task_blockers | 50% | Blockers dashboard, resolution workflow | 🟡 Medium |
| sessions | 0% | Everything | 🔴 HIGH |
| contexts | 0% | Everything | 🔴 HIGH |
| evidence_sources | 0% | Everything | 🟡 Medium |
| document_references | 0% | Everything | 🟡 Medium |
| ideas | 0% | Everything (CLI exists) | 🟢 Low |
| events | 0% | Everything | 🟢 Low |
| session_events | 0% | Everything | 🟢 Low |
| agent_* tables | 0% | Everything | 🟢 Low |
| work_item_dependencies | 0% | Everything | 🟢 Low |
| schema_migrations | 0% | Everything | 🟢 Low |

---

## Priority: What to Surface First

### 🔴 CRITICAL (Needed for Micro-MVP)

**1. Sessions Table - Full Coverage**

Why critical: Core of Micro-MVP is session context persistence

```python
# New routes needed:
@entities_bp.route('/sessions')
def sessions_list():
    """All sessions with provider, duration, work items"""

@entities_bp.route('/session/<session_id>')
def session_detail(session_id):
    """Session details: metadata, learnings, git commits"""

@entities_bp.route('/sessions/timeline')
def sessions_timeline():
    """Visual timeline of all sessions"""
```

**Fields to show:**
- session_id, tool_name (provider), llm_model
- start_time, end_time, duration_minutes
- work_items_touched, tasks_completed
- decisions_made, git_commits
- session_summary, next_session
- developer_name, status

**2. Contexts Table - Full Coverage**

Why critical: Validates context assembly is working

```python
@entities_bp.route('/contexts')
def contexts_list():
    """All contexts with confidence scores"""

@entities_bp.route('/context/<context_id>')
def context_detail(context_id):
    """Context 6W data, confidence breakdown, freshness"""

@entities_bp.route('/work-item/<id>/context')
def work_item_context(id):
    """Hierarchical context for work item"""
```

**Fields to show:**
- entity_type, entity_id (link to project/work_item/task)
- six_w_data (Who, What, When, Where, Why, How)
- confidence_score, confidence_band (RED/YELLOW/GREEN)
- confidence_factors (breakdown)
- created_at, updated_at (freshness)

**3. Project Detail - Enhanced**

Add missing critical fields:

```python
@entities_bp.route('/project/<id>')  # NEW ROUTE
def project_detail(id):
    """Complete project view"""
```

**Add fields:**
- pm_philosophy (LEAN/AGILE/PMBOK/AIPM_HYBRID)
- tech_stack (languages, frameworks)
- created_at, updated_at
- metadata (configuration)

---

### 🟡 IMPORTANT (Phase 2 - After Micro-MVP)

**4. Agents Table**
```python
@entities_bp.route('/agents')
@entities_bp.route('/agent/<id>')
```

**5. Document References**
```python
@entities_bp.route('/documents')
@entities_bp.route('/document/<id>')
```

**6. Evidence Sources**
```python
@entities_bp.route('/evidence')
@entities_bp.route('/evidence/<id>')
```

**7. Rules**
```python
@entities_bp.route('/rules')
@entities_bp.route('/rule/<id>')
```

---

### 🟢 NICE-TO-HAVE (Phase 3)

8. Ideas browser
9. Events/audit log
10. Agent relationships
11. Schema migrations viewer

---

## Recommended Implementation Plan

### Week 1 (Micro-MVP): Sessions & Contexts

**Day 1-2: Sessions Routes**
```python
# agentpm/web/routes/sessions.py (NEW FILE)

from flask import Blueprint, render_template
sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/sessions')
def sessions_list():
    """
    List all sessions with key metrics.

    Shows:
    - Session ID, provider (Claude/Cursor/Aider)
    - Start/end time, duration
    - Work items touched
    - Decisions made
    """
    db = get_database_service()
    sessions = db.execute("SELECT * FROM sessions ORDER BY start_time DESC").fetchall()

    return render_template('sessions_list.html', sessions=sessions)

@sessions_bp.route('/session/<session_id>')
def session_detail(session_id):
    """
    Session detail view.

    Shows:
    - Complete metadata (decisions, patterns, status)
    - Git commits made
    - Files modified
    - Next session context
    """
    db = get_database_service()
    session = db.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,)
    ).fetchone()

    if not session:
        abort(404)

    # Parse metadata JSON
    import json
    metadata = json.loads(session['metadata']) if session['metadata'] else {}

    return render_template('session_detail.html', session=session, metadata=metadata)

@sessions_bp.route('/sessions/timeline')
def sessions_timeline():
    """Visual timeline of all sessions (Chart.js)"""
    # Group sessions by date, show activity over time
```

**Day 3-4: Contexts Routes**
```python
# agentpm/web/routes/contexts.py (NEW FILE)

@contexts_bp.route('/contexts')
def contexts_list():
    """
    List all contexts with confidence scoring.

    Shows:
    - Entity (project/work_item/task)
    - Confidence band (RED/YELLOW/GREEN)
    - Freshness (days since update)
    - 6W completeness
    """

@contexts_bp.route('/context/<context_id>')
def context_detail(context_id):
    """
    Context detail with 6W data.

    Shows:
    - Who, What, When, Where, Why, How
    - Confidence breakdown
    - Plugin facts
    - Amalgamations
    """

@contexts_bp.route('/work-item/<id>/context')
def work_item_context_view(id):
    """
    Hierarchical context view for work item.

    Shows:
    - Project context (inherited)
    - Work item context (specific)
    - Task contexts (all tasks)
    - Merged view
    """
```

**Day 5: Templates**
```html
<!-- templates/sessions_list.html -->
<!-- templates/session_detail.html -->
<!-- templates/contexts_list.html -->
<!-- templates/context_detail.html -->
```

---

### Week 2 (Micro-MVP): Project Enhancement

**Enhance project detail view:**

```python
# agentpm/web/routes/entities.py (UPDATE EXISTING)

@entities_bp.route('/project/<int:project_id>')  # ADD THIS ROUTE
def project_detail(project_id):
    """
    Complete project detail view.

    Shows ALL project fields:
    - Basic: name, description, status
    - NEW: pm_philosophy (LEAN/AGILE/etc.)
    - NEW: tech_stack (languages, frameworks)
    - NEW: created_at, updated_at
    - NEW: metadata (config)
    - Stats: work items, tasks, agents, rules
    - Charts: Progress over time, type distribution
    """
    db = get_database_service()
    project = project_methods.get_project(db, project_id)

    if not project:
        abort(404)

    # Get all related data
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    agents = agent_methods.list_agents(db, project_id=project_id)
    rules = rule_methods.list_rules(db, project_id=project_id)
    sessions = db.execute(
        "SELECT * FROM sessions WHERE project_id = ? ORDER BY start_time DESC LIMIT 10",
        (project_id,)
    ).fetchall()

    return render_template(
        'project_detail.html',
        project=project,
        work_items=work_items,
        agents=agents,
        rules=rules,
        recent_sessions=sessions
    )
```

---

### Phase 2 (After Micro-MVP): Remaining Tables

**Priority order:**

**Week 3-4: Agent System**
- agents (full CRUD)
- agent_examples
- agent_tools
- agent_relationships

**Week 5-6: Knowledge Management**
- document_references (full browser)
- evidence_sources (verification dashboard)
- ideas (voting, transitions)

**Week 7-8: Audit & Events**
- events (audit log)
- session_events (activity tracking)
- work_item_dependencies (portfolio view)

---

## Specific Fields Missing from Current Views

### Projects Table

**Currently shown:**
- name, description (basic info)
- Counts: work_items, tasks, agents, rules

**Missing fields:**
```python
# Need to add to project detail view:
- pm_philosophy: ProjectManagementPhilosophy  # NEW from enum updates!
- project_type: ProjectType  # greenfield, brownfield, etc.
- tech_stack: JSON  # Languages, frameworks detected
- metadata: JSON  # Configuration
- created_at, updated_at: timestamps
- status: ProjectStatus  # initiated, active, etc.
```

### Work Items Table

**Currently shown:**
- name, type, status, priority, description
- Tasks list, progress percentage

**Missing fields:**
```python
# Need to add to work item detail:
- phase: Phase  # D1, P1, I1, R1, O1, E1
- business_context: str  # Why this matters
- ownership: JSON  # RACI matrix
- scope: JSON  # in_scope, out_of_scope
- artifacts: JSON  # code_paths, docs_paths
- dependencies: List[int]  # Work item dependencies
```

### Tasks Table

**Currently shown:**
- name, type, status, effort, priority
- Dependencies, blockers

**Missing fields:**
```python
# Need to add to task detail:
- assigned_to: str  # Agent ID
- code_files: JSON  # Files involved
- patterns_to_follow: JSON  # Code patterns
- implementation_notes: str  # Details
- acceptance_criteria: str  # Success criteria
- git_branch: str  # Associated branch
- pr_url: str  # Pull request link
```

---

## Recommended Micro-MVP Web Updates

### Must-Have (Week 1-2)

**1. Add Sessions Dashboard**
```
Route: /sessions
Shows: All sessions, filterable by provider/status
Purpose: Validate session tracking is working
```

**2. Add Contexts Viewer**
```
Route: /contexts
Shows: All contexts with confidence scoring
Purpose: Validate context assembly is working
```

**3. Add PM Philosophy to Project**
```
Route: /project/<id> (new route)
Shows: PM philosophy, tech stack, full project details
Purpose: Show AI constraint system is working
```

### Should-Have (Phase 2)

**4. Agents Dashboard**
```
Route: /agents
Shows: All agents, capabilities, assignments
```

**5. Documents Browser**
```
Route: /documents
Shows: All documents, searchable, filterable
```

**6. Evidence Tracker**
```
Route: /evidence
Shows: Evidence sources, verification status
```

---

## Quick Win: Add Missing Fields to Existing Views

### Update Project List (5 minutes)

```python
# agentpm/web/routes/entities.py line ~80

projects_data.append(
    ProjectListItem(
        project=project,
        total_work_items=total_work_items,
        total_tasks=total_tasks,
        total_agents=total_agents,
        total_rules=total_rules,
        pm_philosophy=project.pm_philosophy,  # ADD THIS
        tech_stack=project.tech_stack  # ADD THIS
    )
)
```

### Update Work Item Detail (10 minutes)

```python
# Show phase and business context
detail = WorkItemDetail(
    work_item=work_item,
    project_name=project_name,
    tasks=tasks,
    task_status_dist=task_status_dist,
    progress_percent=round(progress_percent, 1),
    time_boxing_compliant=time_boxing_compliant,
    phase=work_item.phase,  # ADD THIS
    business_context=work_item.business_context  # ADD THIS
)
```

### Update Task Detail (10 minutes)

```python
# Show assigned agent
detail = TaskDetail(
    task=task,
    work_item_name=work_item_name,
    project_name=project_name,
    dependencies=dependencies,
    dependents=dependents,
    blockers=blockers,
    time_boxing_compliant=time_boxing_compliant,
    max_hours=max_hours,
    assigned_agent=task.assigned_to  # ADD THIS
)
```

---

## Implementation Strategy

### Option A: Add All Missing Tables (Full Coverage)

**Effort:** 2-3 weeks
**Routes to create:** 15+ new routes
**Templates to create:** 20+ new templates
**Benefit:** Complete web interface

**Cons:**
- Delays Micro-MVP (session hooks)
- Violates LEAN philosophy (build before validating need)

### Option B: Add Only Sessions & Contexts (Micro-MVP Focus)

**Effort:** 2-3 days
**Routes to create:** 4 new routes (sessions list/detail, contexts list/detail)
**Templates to create:** 4 new templates
**Benefit:** Validates Micro-MVP is working

**Pros:**
- Focused on Micro-MVP validation
- Quick to implement
- Can expand later if valuable

### Option C: Quick Wins + Micro-MVP Essentials

**Effort:** 3-4 days
**Routes to create:** 5 routes
**Updates:** Enhance existing 3 routes
**Benefit:** Best balance

**What to do:**
1. Add sessions routes (2 routes, critical)
2. Add contexts routes (2 routes, critical)
3. Add project detail route (1 route, enhances existing)
4. Update existing routes to show missing fields (quick wins)

---

## My Recommendation

**Do Option C: Quick Wins + Micro-MVP Essentials (3-4 days)**

**Week 1 (Alongside hook implementation):**

**Day 1:** Add PM Philosophy and Tech Stack to existing project views
- Update `projects_list.html` template
- Show: PM Philosophy badge, Tech Stack tags
- Effort: 2 hours

**Day 2:** Create Sessions routes
- `/sessions` list view
- `/session/<id>` detail view
- Effort: 4 hours

**Day 3:** Create Contexts routes
- `/contexts` list view
- `/context/<id>` detail view
- Effort: 4 hours

**Day 4:** Create Project Detail route
- `/project/<id>` with all fields
- Complete project dashboard
- Effort: 4 hours

**Day 5:** Polish and test
- Styling, navigation
- Test all new routes
- Effort: 2 hours

**Total: 3-4 days of work (can be done parallel with hooks)**

---

## Defer to Later

**Don't build yet:**
- Ideas web interface (CLI works fine for now)
- Evidence browser (no evidence captured yet)
- Document search (document store not implemented)
- Events/audit log (nice-to-have)
- Agent dashboards (agents working, admin UI not critical)

**Build these AFTER Micro-MVP validates**

---

## Summary

**Current Coverage:** 30-40% of models/fields
**Critical Gap:** Sessions and Contexts (0% covered)
**Recommendation:** 3-4 days to add essential views
**Defer:** Advanced features until Micro-MVP proven

**Want me to implement the Micro-MVP web routes (Sessions + Contexts + Project detail)?**