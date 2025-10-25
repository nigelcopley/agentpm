# Agent Detail Page - Quick Reference Card

**Quick Start**: Copy-paste ready template for agent detail page

---

## 1. Create Template File

**Location**: `agentpm/web/templates/agents/detail.html`

**Minimal Working Version** (150 lines):

```html
{% extends "layouts/modern_base.html" %}

{% block title %}{{ agent.display_name }} - APM (Agent Project Manager){% endblock %}

{% block content %}
<!-- Breadcrumb -->
<nav class="mb-6">
  <ol class="flex items-center space-x-2 text-sm text-gray-500">
    <li><a href="/" class="hover:text-primary">Dashboard</a></li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <a href="/agents" class="hover:text-primary">Agents</a>
    </li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <span class="text-gray-900">{{ agent.display_name }}</span>
    </li>
  </ol>
</nav>

<!-- Header -->
<section class="mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
  <div>
    <h1 class="text-3xl font-semibold text-gray-900">{{ agent.display_name }}</h1>
    <p class="mt-2 text-sm text-gray-500">{{ agent.role }}</p>
  </div>
  <div class="flex items-center gap-2">
    {% if agent.is_active %}
    <span class="badge badge-success">
      <i class="bi bi-check-circle"></i>
      Active
    </span>
    {% else %}
    <span class="badge badge-gray">
      <i class="bi bi-archive"></i>
      Inactive
    </span>
    {% endif %}

    <a href="/agents/{{ agent.id }}/edit" class="btn btn-secondary">
      <i class="bi bi-pencil"></i>
      Edit
    </a>
  </div>
</section>

<!-- Metrics -->
<section class="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
  <article class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
    <header class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
      <i class="bi bi-journal-check text-primary"></i>
      Total Tasks
    </header>
    <p class="mt-3 text-3xl font-semibold text-gray-900">{{ total_tasks }}</p>
  </article>

  <article class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
    <header class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
      <i class="bi bi-activity text-emerald-600"></i>
      Active Tasks
    </header>
    <p class="mt-3 text-3xl font-semibold text-gray-900">{{ active_tasks }}</p>
  </article>

  <article class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
    <header class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
      <i class="bi bi-check-circle text-success"></i>
      Completed
    </header>
    <p class="mt-3 text-3xl font-semibold text-gray-900">{{ completed_tasks }}</p>
  </article>

  <article class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
    <header class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
      <i class="bi bi-clock-history text-amber-600"></i>
      Last Used
    </header>
    <p class="mt-3 text-3xl font-semibold text-gray-900">
      {% if agent.last_used_at %}
        {{ (now - agent.last_used_at).days }}d
      {% else %}
        Never
      {% endif %}
    </p>
  </article>
</section>

<!-- Agent Details -->
<section class="mb-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
  <header class="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
    <i class="bi bi-info-circle text-primary"></i>
    Agent Details
  </header>

  <div class="space-y-4">
    {% if agent.description %}
    <div>
      <label class="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</label>
      <p class="mt-1 text-sm text-gray-700">{{ agent.description }}</p>
    </div>
    {% endif %}

    {% if agent.capabilities %}
    <div>
      <label class="text-xs font-semibold uppercase tracking-wide text-gray-500">Capabilities</label>
      <div class="mt-2 flex flex-wrap gap-2">
        {% for capability in agent.capabilities %}
        <span class="inline-flex items-center gap-1 rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-700">
          <i class="bi bi-check2"></i>
          {{ capability }}
        </span>
        {% endfor %}
      </div>
    </div>
    {% endif %}

    <div class="grid gap-4 md:grid-cols-2 border-t border-gray-100 pt-4">
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-gray-500">Created</label>
        <p class="mt-1 text-xs text-gray-600">
          <i class="bi bi-calendar text-gray-400"></i>
          {{ agent.created_at.strftime('%Y-%m-%d %H:%M') if agent.created_at else 'N/A' }}
        </p>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-gray-500">Last Updated</label>
        <p class="mt-1 text-xs text-gray-600">
          <i class="bi bi-calendar text-gray-400"></i>
          {{ agent.updated_at.strftime('%Y-%m-%d %H:%M') if agent.updated_at else 'N/A' }}
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Assigned Tasks -->
<section class="mb-8 rounded-2xl border border-gray-200 bg-white shadow-sm">
  <header class="flex items-center justify-between border-b border-gray-100 px-6 py-4">
    <div class="text-sm font-semibold uppercase tracking-wide text-gray-500">
      Assigned Tasks ({{ assigned_tasks | length }})
    </div>
  </header>

  {% if assigned_tasks %}
  <div class="overflow-x-auto">
    <table class="table table-hover">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Status</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for task in assigned_tasks %}
        <tr>
          <td class="font-mono text-sm text-gray-600">#{{ task.id }}</td>
          <td class="font-medium text-gray-900">{{ task.name }}</td>
          <td><span class="badge badge-primary">{{ task.status.value }}</span></td>
          <td class="text-xs text-gray-500">{{ task.created_at.strftime('%Y-%m-%d') }}</td>
          <td>
            <a href="/tasks/{{ task.id }}" class="btn btn-sm btn-secondary">
              <i class="bi bi-eye"></i>
              View
            </a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="px-6 py-12 text-center text-sm text-gray-500">
    <i class="bi bi-inbox text-lg text-gray-400"></i>
    <p class="mt-2">No tasks assigned to this agent yet.</p>
  </div>
  {% endif %}
</section>
{% endblock %}
```

---

## 2. Update Backend Route

**File**: `agentpm/web/blueprints/agents.py`

**Replace** lines 122-131 with:

```python
from datetime import datetime, timezone

@agents_bp.route('/agents/<int:agent_id>')
def agent_detail(agent_id: int):
    """Get agent details with assigned tasks and metrics."""
    db = get_database_service()

    # Get agent
    agent = agent_methods.get_agent(db, agent_id)
    if not agent:
        abort(404, description=f"Agent {agent_id} not found")

    # Get assigned tasks
    from ...core.database.methods import tasks as task_methods
    assigned_tasks = task_methods.list_tasks(
        db,
        filters={'assigned_agent': agent.role},
        include_completed=True
    )

    # Calculate metrics
    total_tasks = len(assigned_tasks)
    active_tasks = sum(1 for t in assigned_tasks
                       if t.status.value in ['IN_PROGRESS', 'REVIEW'])
    completed_tasks = sum(1 for t in assigned_tasks
                          if t.status.value == 'COMPLETED')

    return render_template(
        'agents/detail.html',
        agent=agent,
        assigned_tasks=assigned_tasks,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        now=datetime.now(timezone.utc)
    )
```

---

## 3. Test

```bash
# Start Flask server
cd /Users/nigelcopley/.project_manager/aipm-v2
python -m agentpm.web.app

# Visit in browser
open http://localhost:5001/agents/1
```

**Expected Result**: Agent detail page loads with:
- Agent name and status badge
- 4 metrics cards
- Agent details (description, capabilities)
- Assigned tasks table (if any)

---

## 4. Common Issues

### Issue: Template Not Found
**Error**: `TemplateNotFound: agents/detail.html`
**Fix**: Ensure file exists at `agentpm/web/templates/agents/detail.html`

### Issue: Attribute Error (no last_used_at)
**Error**: `AttributeError: 'Agent' object has no attribute 'last_used_at'`
**Fix**: Run migration 0011 to add `last_used_at` column:
```bash
apm db migrate
```

### Issue: No Tasks Showing
**Error**: Tasks table shows "No tasks assigned"
**Cause**: `assigned_agent` field uses role string, not agent ID
**Fix**: Verify tasks have `assigned_agent` set to agent.role (e.g., "python-developer")

---

## 5. Enhancement Checklist

Once basic version works, add:
- [ ] Collapsible SOP section (Alpine.js)
- [ ] HTMX status toggle button
- [ ] Task filtering (All/Active/Completed)
- [ ] Status color mapping (badge-success, badge-warning, etc.)
- [ ] Tier badge (sub-agent, specialist, orchestrator)
- [ ] Last used timestamp formatting
- [ ] Project link in agent details

---

## 6. Design System Reference

**Colors**:
- Primary: `#6366f1` (blue-purple)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (amber)
- Error: `#ef4444` (red)
- Gray: `#6b7280` (neutral)

**Badge Classes**:
- `badge-primary` - Blue-purple
- `badge-success` - Green (active status)
- `badge-warning` - Amber (in-progress)
- `badge-error` - Red (blocked)
- `badge-gray` - Gray (inactive)
- `badge-info` - Blue (tier badges)

**Button Classes**:
- `btn-primary` - Primary actions
- `btn-secondary` - Secondary actions
- `btn-error` - Destructive actions
- `btn-sm` - Small button

**Card Classes**:
- `card` - Base card container
- `card-header` - Card header with border
- `card-body` - Card content area

---

## 7. File Tree

```
agentpm/web/
├── blueprints/
│   └── agents.py (UPDATE - enhance route handler)
└── templates/
    ├── layouts/
    │   └── modern_base.html (extends this)
    └── agents/
        ├── list.html (exists)
        └── detail.html (CREATE - new file)
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-10-22
**For**: APM (Agent Project Manager) Agent Detail Page Implementation
