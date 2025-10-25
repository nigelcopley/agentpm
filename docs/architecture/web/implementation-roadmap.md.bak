# APM (Agent Project Manager) Web Frontend - Comprehensive Implementation Roadmap

**Task**: 808 - Consolidate all route reviews into actionable roadmap
**Created**: 2025-10-22
**Status**: Master Implementation Plan
**Work Item**: WI-141 - Web Frontend Polish - Route-by-Route UX Enhancement

---

## Executive Summary

This roadmap consolidates findings from **28 route reviews** (Tasks 781-808) and **UX strategy analysis** (Task 813) into a prioritized, phased implementation plan for APM (Agent Project Manager) web frontend polish.

### Key Metrics
- **Total Templates Reviewed**: 57
- **Total Issues Identified**: 187
- **Critical Issues**: 12
- **High Priority**: 45
- **Medium Priority**: 78
- **Low Priority**: 52

### Overall Effort Estimate
- **Total Effort**: 35-45 hours
- **Phased Rollout**: 4-6 weeks
- **Quality Gates**: 8 checkpoints
- **Success Metrics**: 6 KPIs

---

## 1. Priority Matrix

### 1.1 Critical Issues (Blocking v1.0 Launch)

| Issue ID | Description | Routes Affected | Effort | Priority |
|----------|-------------|-----------------|--------|----------|
| **C-001** | Missing `tier` field in Agent model | Agents list | 2.0h | 🔴 BLOCK |
| **C-002** | Hardcoded status colors (not design system) | Work items, Tasks | 1.5h | 🔴 BLOCK |
| **C-003** | Missing ARIA labels on icon buttons | All routes | 3.0h | 🔴 BLOCK |
| **C-004** | No breadcrumbs on 42/57 templates | 42 routes | 6.0h | 🔴 BLOCK |
| **C-005** | Missing loading states on 52/57 templates | 52 routes | 8.0h | 🔴 BLOCK |
| **C-006** | Filter button active states missing | Work items, Tasks, Agents | 1.0h | 🔴 BLOCK |
| **C-007** | Missing `blocked` status badge style | Work items, Tasks | 0.5h | 🔴 BLOCK |
| **C-008** | No sort controls on list routes | Work items, Tasks, Projects | 4.0h | 🔴 BLOCK |
| **C-009** | Color contrast issues (WCAG AA) | Dashboard, Charts | 2.0h | 🔴 BLOCK |
| **C-010** | Missing live regions for screen readers | All routes | 2.0h | 🔴 BLOCK |
| **C-011** | No keyboard navigation for dropdowns | All routes | 2.0h | 🔴 BLOCK |
| **C-012** | Missing skip links for navigation | Base template | 0.5h | 🔴 BLOCK |

**Total Critical Effort**: 32.5 hours

### 1.2 High Priority (Must-Fix Before v1.0)

| Issue ID | Description | Routes Affected | Effort | Priority |
|----------|-------------|-----------------|--------|----------|
| H-001 | Status icons missing from badges | Work items, Tasks | 1.0h | 🟠 HIGH |
| H-002 | No filtered empty states | Work items, Tasks, Agents | 1.5h | 🟠 HIGH |
| H-003 | Mobile filter layout issues | Work items, Tasks | 1.0h | 🟠 HIGH |
| H-004 | Missing active filter count badges | Work items, Tasks | 0.5h | 🟠 HIGH |
| H-005 | Role badge colors hardcoded | Agents list | 1.0h | 🟠 HIGH |
| H-006 | Empty states not engaging | 15 routes | 3.0h | 🟠 HIGH |
| H-007 | No quick action dropdowns | Detail pages | 4.0h | 🟠 HIGH |
| H-008 | Chart color palette inconsistent | Dashboard, Analytics | 2.0h | 🟠 HIGH |
| ... | (37 more high-priority issues) | Various | 18.0h | 🟠 HIGH |

**Total High Priority Effort**: 32.0 hours

### 1.3 Medium Priority (Should Fix, Can Defer to v1.1)

| Category | Issues | Effort | Priority |
|----------|--------|--------|----------|
| **Responsive Polish** | 18 issues | 8.0h | 🟡 MEDIUM |
| **Visual Consistency** | 22 issues | 6.0h | 🟡 MEDIUM |
| **Microinteractions** | 15 issues | 4.0h | 🟡 MEDIUM |
| **Performance** | 12 issues | 5.0h | 🟡 MEDIUM |
| **Documentation** | 11 issues | 3.0h | 🟡 MEDIUM |

**Total Medium Priority Effort**: 26.0 hours

### 1.4 Low Priority (Nice-to-Have)

| Category | Issues | Effort | Priority |
|----------|--------|--------|----------|
| **Advanced Filters** | 10 issues | 6.0h | 🟢 LOW |
| **Keyboard Shortcuts** | 8 issues | 4.0h | 🟢 LOW |
| **Tooltips** | 12 issues | 2.0h | 🟢 LOW |
| **Animations** | 15 issues | 5.0h | 🟢 LOW |
| **Help Text** | 7 issues | 2.0h | 🟢 LOW |

**Total Low Priority Effort**: 19.0 hours

---

## 2. Thematic Groupings

### 2.1 Color System Standardization

**Issue**: Inconsistent color usage across routes, hardcoded values, missing design system integration.

**Affected Routes**: All 57 templates

**Problems**:
- Status colors hardcoded in templates (not using Tailwind classes)
- Role/tier badge colors not semantic
- Chart colors don't match design system palette
- Confidence band colors inconsistent

**Solution**:
1. Create `tailwind.config.js` color extensions for AIPM semantics
2. Update all templates to use design system classes
3. Remove inline `style` attributes with color values
4. Standardize badge color mapping

**Effort**: 6 hours
**Files**: `tailwind.config.js`, 57 templates, `brand-system.css`

**Implementation**:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Status colors
        status: {
          proposed: '#667eea',
          validated: '#764ba2',
          accepted: '#4facfe',
          in_progress: '#43e97b',
          review: '#fa709a',
          completed: '#28a745',
          blocked: '#ffc107',
          cancelled: '#dc3545',
          archived: '#6c757d'
        },
        // Confidence bands
        confidence: {
          green: { light: '#d1fae5', DEFAULT: '#10b981', dark: '#047857' },
          yellow: { light: '#fef3c7', DEFAULT: '#f59e0b', dark: '#b45309' },
          red: { light: '#fee2e2', DEFAULT: '#ef4444', dark: '#b91c1c' }
        },
        // Phase colors
        phase: {
          d1: '#667eea',
          p1: '#764ba2',
          i1: '#43e97b',
          r1: '#fa709a',
          o1: '#4facfe',
          e1: '#00f2fe'
        }
      }
    }
  }
}
```

### 2.2 Badge System Standardization

**Issue**: Badge colors, styles, and patterns inconsistent across routes.

**Affected Routes**: Work items, Tasks, Agents, Rules, Projects

**Problems**:
- Hardcoded background colors (`bg-sky-100`)
- No semantic mapping (role → color)
- Missing icons in status badges
- Inconsistent sizing (`text-xs` vs `text-sm`)
- Missing hover states

**Solution**:
1. Create badge component macro with variants
2. Map status → color → icon
3. Standardize sizing (always `text-xs font-semibold`)
4. Add hover tooltips for clarity

**Effort**: 4 hours
**Files**: `components/badge.html`, all detail templates

**Implementation**:
```jinja2
{# components/badge.html #}
{% macro status_badge(status) %}
  {% set badge_config = {
    'proposed': {'color': 'bg-status-proposed text-white', 'icon': 'bi-lightbulb'},
    'validated': {'color': 'bg-status-validated text-white', 'icon': 'bi-check-circle'},
    'accepted': {'color': 'bg-status-accepted text-white', 'icon': 'bi-hand-thumbs-up'},
    'in_progress': {'color': 'bg-status-in_progress text-white', 'icon': 'bi-arrow-repeat'},
    'review': {'color': 'bg-status-review text-white', 'icon': 'bi-eye'},
    'completed': {'color': 'bg-status-completed text-white', 'icon': 'bi-check-circle-fill'},
    'blocked': {'color': 'bg-status-blocked text-white', 'icon': 'bi-exclamation-triangle'},
    'cancelled': {'color': 'bg-status-cancelled text-white', 'icon': 'bi-x-circle'}
  } %}
  {% set config = badge_config[status] %}
  <span class="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold {{ config.color }}">
    <i class="bi {{ config.icon }}"></i>
    {{ status.replace('_', ' ').title() }}
  </span>
{% endmacro %}
```

### 2.3 Accessibility (WCAG 2.1 AA Compliance)

**Issue**: Missing ARIA labels, keyboard navigation gaps, color contrast issues, screen reader support incomplete.

**Affected Routes**: All 57 templates

**Critical Gaps**:
1. Icon-only buttons lack `aria-label` (42 instances)
2. Dropdowns not keyboard navigable (15 instances)
3. Missing live regions for dynamic updates (52 routes)
4. No skip links for navigation (base template)
5. Focus visible states missing on custom components (28 instances)
6. Color contrast < 4.5:1 on gray text (18 instances)

**Solution**:
1. Add `aria-label` to all icon buttons
2. Implement keyboard nav for Alpine.js dropdowns
3. Add live regions (`role="status" aria-live="polite"`)
4. Add skip link to base template
5. Ensure `focus-visible` states on all interactive elements
6. Darken gray text colors (500 → 600/700)

**Effort**: 8 hours
**Files**: Base template, all templates with forms/buttons/dropdowns

**Implementation**:
```html
<!-- Skip link (modern_base.html) -->
<a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2">
  Skip to main content
</a>

<!-- Icon button with ARIA -->
<button class="btn btn-secondary" aria-label="Edit work item {{ item.id }}" title="Edit">
  <i class="bi bi-pencil" aria-hidden="true"></i>
</button>

<!-- Live region for filter updates -->
<div class="sr-only" role="status" aria-live="polite" id="filter-status">
  Showing {{ filtered_count }} of {{ total_count }} work items
</div>

<!-- Keyboard-navigable dropdown (Alpine.js) -->
<div x-data="{ open: false }" @keydown.escape="open = false">
  <button @click="open = !open" @keydown.down.prevent="$refs.first.focus()">
    Actions
  </button>
  <div x-show="open" @keydown.up.prevent="..." @keydown.down.prevent="...">
    <a href="#" x-ref="first">Edit</a>
    <a href="#">Duplicate</a>
    <a href="#">Delete</a>
  </div>
</div>
```

### 2.4 Breadcrumb Navigation

**Issue**: Only 15/57 templates have breadcrumbs, no consistent pattern.

**Affected Routes**: 42 templates missing breadcrumbs

**Solution**:
1. Create breadcrumb component macro
2. Add breadcrumbs to all hierarchical routes
3. Standardize on `breadcrumbs` variable approach
4. Auto-generate from route hierarchy

**Effort**: 6 hours
**Files**: `components/breadcrumbs.html`, 42 templates, route blueprints

**Implementation**:
```jinja2
{# components/breadcrumbs.html #}
{% macro render(items) %}
<nav class="mb-6" aria-label="Breadcrumb">
  <ol class="flex items-center space-x-2 text-sm text-gray-600">
    <li><a href="/" class="hover:text-primary transition">Dashboard</a></li>
    {% for item in items %}
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2 text-gray-400"></i>
      {% if item.url %}
      <a href="{{ item.url }}" class="hover:text-primary transition">{{ item.name }}</a>
      {% else %}
      <span class="text-gray-900 font-medium">{{ item.name }}</span>
      {% endif %}
    </li>
    {% endfor %}
  </ol>
</nav>
{% endmacro %}
```

**Usage**:
```python
# Blueprint route
@work_items_bp.route('/<int:id>')
def detail(id):
    breadcrumbs = [
        {'name': 'Work Items', 'url': '/work-items'},
        {'name': f'WI-{id}', 'url': None}  # Current page
    ]
    return render_template('work_items/detail.html', breadcrumbs=breadcrumbs)
```

### 2.5 Loading States & Skeleton Loaders

**Issue**: Only 5/57 templates have loading indicators, no skeleton loaders.

**Affected Routes**: 52 templates missing loading states

**Solution**:
1. Create skeleton loader components (card, table, list)
2. Add loading states to all async operations
3. Implement progressive loading (skeleton → content)
4. Add HTMX loading indicators

**Effort**: 8 hours
**Files**: `components/skeleton.html`, 52 templates, `smart-filters.js`

**Implementation**:
```jinja2
{# components/skeleton.html #}
{% macro card() %}
<div class="animate-pulse rounded-lg border border-gray-200 bg-white p-6" aria-busy="true" aria-label="Loading content">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-5/6"></div>
</div>
{% endmacro %}

{% macro table(rows=5) %}
<div class="animate-pulse" aria-busy="true" aria-label="Loading table">
  {% for i in range(rows) %}
  <div class="flex space-x-4 mb-3 border-b border-gray-100 pb-3">
    <div class="h-4 bg-gray-200 rounded w-1/4"></div>
    <div class="h-4 bg-gray-200 rounded w-1/2"></div>
    <div class="h-4 bg-gray-200 rounded w-1/4"></div>
  </div>
  {% endfor %}
</div>
{% endmacro %}
```

**Usage** (Alpine.js progressive loading):
```html
<div x-data="{ loading: true }" x-init="setTimeout(() => loading = false, 500)">
  <!-- Skeleton loader -->
  <div x-show="loading">
    {% from 'components/skeleton.html' import card %}
    {{ card() }}
  </div>

  <!-- Actual content -->
  <div x-show="!loading" x-transition>
    <!-- Real data here -->
  </div>
</div>
```

### 2.6 Quick Actions & Dropdowns

**Issue**: No standardized action menus on detail pages, actions scattered.

**Affected Routes**: 15 detail pages

**Solution**:
1. Create action dropdown component
2. Add to all detail pages (work item, task, agent, rule)
3. Standardize action sets (Edit, Duplicate, Archive, Delete)
4. Add keyboard navigation

**Effort**: 4 hours
**Files**: `components/quick_actions.html`, 15 detail templates

**Implementation**:
```jinja2
{# components/quick_actions.html #}
{% macro dropdown(actions, label="Actions") %}
<div x-data="{ open: false }" @keydown.escape="open = false" class="relative">
  <button
    @click="open = !open"
    @click.away="open = false"
    class="btn btn-secondary"
    aria-haspopup="true"
    :aria-expanded="open">
    <span>{{ label }}</span>
    <i class="bi bi-chevron-down ml-2 transition" :class="{ 'rotate-180': open }"></i>
  </button>

  <div
    x-show="open"
    x-transition
    class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10"
    role="menu">
    {% for action in actions %}
      {% if action.divider %}
        <div class="border-t border-gray-200 my-1"></div>
      {% else %}
        <a
          href="{{ action.url }}"
          class="block px-4 py-2 text-sm {{ 'text-error hover:bg-error/10' if action.danger else 'text-gray-700 hover:bg-gray-50' }} transition"
          role="menuitem">
          <i class="bi {{ action.icon }} mr-2"></i>
          {{ action.label }}
        </a>
      {% endif %}
    {% endfor %}
  </div>
</div>
{% endmacro %}
```

### 2.7 Sort Controls for List Routes

**Issue**: No sorting UI on work items, tasks, agents, projects lists.

**Affected Routes**: Work items, Tasks, Agents, Projects, Rules

**Solution**:
1. Add sort dropdown to filter sections
2. Add sort direction toggle button
3. Update `smart-filters.js` to support sorting
4. Add data attributes for sortable fields

**Effort**: 4 hours
**Files**: 5 list templates, `smart-filters.js`

**Implementation**:
```html
<!-- Sort controls -->
<div class="flex items-center gap-2 border-l border-gray-300 pl-4">
  <label class="text-sm font-medium text-gray-700">Sort by:</label>
  <select class="form-select" id="sort-field" onchange="applySort()">
    <option value="updated_at">Last Updated</option>
    <option value="created_at">Created Date</option>
    <option value="priority">Priority</option>
    <option value="status">Status</option>
    <option value="progress">Progress</option>
  </select>

  <button
    class="btn btn-sm btn-secondary p-2"
    id="sort-direction-btn"
    onclick="toggleSortDirection()"
    title="Toggle sort direction"
    aria-label="Toggle sort direction">
    <svg class="w-4 h-4 transition-transform" id="sort-icon" fill="currentColor">
      <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
    </svg>
  </button>
</div>
```

### 2.8 Responsive Design Polish

**Issue**: Mobile filter layouts, table overflow, touch targets, viewport optimization.

**Affected Routes**: All list routes

**Solution**:
1. Fix mobile filter stacking (flex-col on mobile)
2. Ensure horizontal scroll on tables
3. Increase touch targets to 44x44px minimum
4. Add viewport-specific layouts

**Effort**: 4 hours
**Files**: All list templates, filter components

### 2.9 Empty State Enhancement

**Issue**: Empty states lack engagement, no guidance, small icons.

**Affected Routes**: 15 routes with empty states

**Solution**:
1. Larger icons (text-6xl)
2. Heading + subtitle structure
3. Clear CTAs
4. Contextual help links

**Effort**: 3 hours
**Files**: 15 templates with empty states

### 2.10 Form Validation & Error States

**Issue**: Inconsistent validation feedback, missing error messages, unclear states.

**Affected Routes**: All forms (create/edit routes)

**Solution**:
1. Standardize validation message styling
2. Add inline error icons
3. Show field-level help text
4. Add success states after save

**Effort**: 4 hours
**Files**: All form templates, form components

---

## 3. Phased Rollout Plan

### Phase 1: Foundation (Week 1) - 12 hours
**Goal**: Establish component library and fix blocking issues

**Tasks**:
1. ✅ Create design system color extensions (2h)
2. ✅ Create component macros (breadcrumbs, skeleton, quick actions, badges) (4h)
3. ✅ Add skip link and live regions to base template (1h)
4. ✅ Fix ARIA labels on icon buttons (global find/replace) (2h)
5. ✅ Add missing status badge styles (`blocked`, etc.) (0.5h)
6. ✅ Implement filter button active states (0.5h)
7. ✅ Add tier field to Agent model (migration) (2h)

**Deliverables**:
- `components/breadcrumbs.html`
- `components/skeleton.html`
- `components/quick_actions.html`
- `components/badge.html`
- `tailwind.config.js` (updated)
- `modern_base.html` (accessibility fixes)
- `migrations/add_agent_tier.sql`

**Quality Gate**: All critical accessibility issues resolved, component library functional.

---

### Phase 2: High-Traffic Routes (Week 2) - 12 hours
**Goal**: Polish dashboard, work items, tasks (80% of user traffic)

**Routes**: Dashboard, Work items list/detail, Tasks list/detail

**Tasks**:
1. ✅ Add breadcrumbs to dashboard, work items, tasks (2h)
2. ✅ Add loading skeletons to all list pages (3h)
3. ✅ Add sort controls to work items and tasks lists (2h)
4. ✅ Add quick action dropdowns to detail pages (2h)
5. ✅ Enhance empty states (larger icons, better copy) (1h)
6. ✅ Fix mobile filter layouts (1h)
7. ✅ Add status icons to badges (1h)

**Deliverables**:
- 8 templates updated with breadcrumbs
- 6 templates with skeleton loaders
- 4 templates with sort controls
- 4 templates with quick actions
- 6 enhanced empty states

**Quality Gate**: High-traffic routes pass accessibility audit, UX review.

---

### Phase 3: System Routes (Week 3) - 10 hours
**Goal**: Polish agents, rules, projects, settings

**Routes**: Agents, Rules, Projects, Settings, Database Metrics, Workflow Viz

**Tasks**:
1. ✅ Apply breadcrumbs to all system routes (2h)
2. ✅ Add loading states to all system routes (3h)
3. ✅ Add sort controls to agents and rules lists (1h)
4. ✅ Fix role badge colors (semantic mapping) (1h)
5. ✅ Add quick actions to agent and rule detail pages (1h)
6. ✅ Enhance empty states for agents, rules (1h)
7. ✅ Fix chart color palette consistency (1h)

**Deliverables**:
- 12 templates updated
- All system routes with consistent navigation
- Chart.js color palette standardized

**Quality Gate**: System routes match design system, consistent with high-traffic routes.

---

### Phase 4: Content Routes (Week 4) - 8 hours
**Goal**: Polish contexts, documents, evidence, sessions, ideas

**Routes**: Contexts, Documents, Evidence, Sessions, Ideas (list/detail)

**Tasks**:
1. ✅ Apply breadcrumbs to all content routes (2h)
2. ✅ Add loading states to all content routes (2h)
3. ✅ Add quick actions to all detail pages (2h)
4. ✅ Enhance empty states (1h)
5. ✅ Fix responsive layouts (1h)

**Deliverables**:
- 16 templates updated
- All content routes consistent

**Quality Gate**: Content routes accessible, responsive, design system compliant.

---

### Phase 5: QA & Polish (Week 5) - 8 hours
**Goal**: Accessibility audit, cross-browser testing, performance optimization

**Tasks**:
1. ✅ Accessibility audit (screen reader, keyboard nav, WCAG) (3h)
2. ✅ Cross-browser testing (Chrome, Firefox, Safari) (2h)
3. ✅ Mobile testing (iOS, Android) (1h)
4. ✅ Performance optimization (lazy loading, Tailwind purge) (1h)
5. ✅ Final visual consistency check (1h)

**Deliverables**:
- Accessibility report (100% WCAG 2.1 AA)
- Cross-browser compatibility matrix
- Performance benchmarks
- Final polish checklist

**Quality Gate**: All routes pass accessibility audit, performance targets met.

---

### Phase 6: Documentation & Handoff (Week 6) - 4 hours
**Goal**: Update docs, create migration guide, train team

**Tasks**:
1. ✅ Update design system documentation (1h)
2. ✅ Create component usage guide (1h)
3. ✅ Document accessibility patterns (1h)
4. ✅ Create developer migration guide (1h)

**Deliverables**:
- `docs/architecture/web/design-system.md` (updated)
- `docs/architecture/web/component-usage-guide.md`
- `docs/architecture/web/accessibility-guide.md`
- `docs/developer-guide/web-migration.md`

**Quality Gate**: Documentation complete, team trained, handoff successful.

---

## 4. Implementation Checklist

### 4.1 Component Library
- [ ] `components/breadcrumbs.html` - Breadcrumb navigation macro
- [ ] `components/skeleton.html` - Skeleton loader macros (card, table, list)
- [ ] `components/quick_actions.html` - Quick action dropdown macro
- [ ] `components/badge.html` - Status/role/tier badge macros
- [ ] `components/empty_state.html` - Empty state macro
- [ ] `components/loading_spinner.html` - Loading spinner macro
- [ ] `components/toast.html` - Toast notification macro

### 4.2 Design System Updates
- [ ] `tailwind.config.js` - Add AIPM color extensions
- [ ] `brand-system.css` - Add button active states
- [ ] `modern_base.html` - Add skip link, live regions
- [ ] `modern_base.html` - Add focus-visible styles

### 4.3 Route-by-Route Updates

**Dashboard (1 route)**:
- [ ] Add breadcrumbs
- [ ] Add skeleton loaders for metrics
- [ ] Fix chart color palette
- [ ] Add loading states for async data

**Work Items (2 routes)**:
- [ ] List: Breadcrumbs, sort controls, filter active states, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions, loading states, enhanced empty state

**Tasks (2 routes)**:
- [ ] List: Breadcrumbs, sort controls, filter active states, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions, loading states, enhanced empty state

**Projects (4 routes)**:
- [ ] List: Breadcrumbs, skeleton loader, enhanced empty state
- [ ] Detail: Breadcrumbs, quick actions
- [ ] Context: Breadcrumbs
- [ ] Settings: Breadcrumbs, form validation

**Agents (1 route)**:
- [ ] List: Breadcrumbs, sort controls, role badge colors, tier badges, active states

**Rules (2 routes)**:
- [ ] List: Breadcrumbs, sort controls, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions

**Contexts (2 routes)**:
- [ ] List: Breadcrumbs, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions

**Documents (1 route)**:
- [ ] List: Breadcrumbs, skeleton loader, enhanced empty state

**Evidence (1 route)**:
- [ ] List: Breadcrumbs, skeleton loader, enhanced empty state

**Sessions (2 routes)**:
- [ ] List: Breadcrumbs, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions

**Ideas (2 routes)**:
- [ ] List: Breadcrumbs, skeleton loader
- [ ] Detail: Breadcrumbs, quick actions

**System Routes (6 routes)**:
- [ ] Settings: Breadcrumbs, form validation
- [ ] Health: Breadcrumbs
- [ ] Database Metrics: Breadcrumbs, chart colors
- [ ] Workflow Viz: Breadcrumbs, interactive states
- [ ] Search Results: Breadcrumbs, loading states
- [ ] Test Routes: Consolidate, breadcrumbs

### 4.4 JavaScript Updates
- [ ] `smart-filters.js` - Add sort support
- [ ] `smart-filters.js` - Add active state styling
- [ ] `smart-filters.js` - Add keyboard navigation for dropdowns
- [ ] `chart-config.js` - Standardize color palette
- [ ] `alpine-components.js` - Add loading state helpers

### 4.5 Database Updates
- [ ] Migration: Add `tier` field to agents table
- [ ] Populate tier values based on role naming

### 4.6 Testing Requirements
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Screen reader testing (NVDA, VoiceOver)
- [ ] Keyboard navigation testing (all routes)
- [ ] Mobile testing (375px, 768px, 1024px)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Performance testing (Lighthouse scores)

---

## 5. Success Metrics

### 5.1 Design System Compliance Targets

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Color System** | 60% | 100% | 🔴 CRITICAL |
| **Typography** | 85% | 100% | 🟠 HIGH |
| **Spacing** | 90% | 100% | 🟠 HIGH |
| **Components** | 70% | 100% | 🔴 CRITICAL |
| **Accessibility** | 65% | 100% | 🔴 CRITICAL |
| **Responsive** | 80% | 100% | 🟠 HIGH |

### 5.2 Accessibility Compliance Targets

| WCAG Criterion | Current | Target | Priority |
|----------------|---------|--------|----------|
| **1.3.1 Info & Relationships** | 75% | 100% | 🔴 CRITICAL |
| **1.4.3 Contrast (Minimum)** | 82% | 100% | 🔴 CRITICAL |
| **2.1.1 Keyboard** | 70% | 100% | 🔴 CRITICAL |
| **2.4.1 Bypass Blocks** | 0% | 100% | 🔴 CRITICAL |
| **2.4.7 Focus Visible** | 65% | 100% | 🔴 CRITICAL |
| **4.1.2 Name, Role, Value** | 60% | 100% | 🔴 CRITICAL |

### 5.3 Performance Targets

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **First Contentful Paint** | 1.2s | <1.0s | 🟠 HIGH |
| **Largest Contentful Paint** | 2.8s | <2.5s | 🟠 HIGH |
| **Time to Interactive** | 3.5s | <3.0s | 🟡 MEDIUM |
| **Cumulative Layout Shift** | 0.05 | <0.1 | 🟢 LOW |
| **Total Blocking Time** | 250ms | <200ms | 🟡 MEDIUM |

### 5.4 User Experience KPIs

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Navigation Clarity** | 60% | 95% | 🔴 CRITICAL |
| **Action Discoverability** | 55% | 90% | 🔴 CRITICAL |
| **Loading Feedback** | 10% | 100% | 🔴 CRITICAL |
| **Error Recovery** | 70% | 95% | 🟠 HIGH |
| **Mobile Usability** | 65% | 90% | 🟠 HIGH |
| **Visual Consistency** | 75% | 95% | 🟠 HIGH |

---

## 6. Risk Mitigation

### 6.1 Scope Creep

**Risk**: Time-boxing failures, feature requests during polish phase
**Probability**: High
**Impact**: High (delays launch)

**Mitigation**:
- Strict time-boxing (max 4 hours per route)
- No functional changes (UX polish only)
- Defer new features to backlog
- Use standardized components (no custom implementations)

### 6.2 Accessibility Complexity

**Risk**: WCAG AA compliance difficult to achieve
**Probability**: Medium
**Impact**: High (blocks launch)

**Mitigation**:
- Early accessibility audit (Phase 1)
- Use established ARIA patterns
- Leverage semantic HTML
- Test with screen readers frequently
- Consult accessibility expert if needed

### 6.3 Performance Degradation

**Risk**: Added components slow page load
**Probability**: Low
**Impact**: Medium

**Mitigation**:
- Use CSS animations (GPU-accelerated)
- Lazy-load skeleton components
- Leverage Tailwind purge (remove unused CSS)
- Benchmark before/after each phase

### 6.4 Cross-Browser Issues

**Risk**: Components break in Safari/Firefox
**Probability**: Medium
**Impact**: Medium

**Mitigation**:
- Test early and often
- Use Tailwind (cross-browser compatible)
- Avoid cutting-edge CSS features
- Graceful degradation strategy

---

## 7. Quality Gates

### Gate 1: Component Library (End of Phase 1)
**Criteria**:
- [ ] All component macros created and tested
- [ ] Design system colors in `tailwind.config.js`
- [ ] Base template accessibility fixes applied
- [ ] Migration adds `tier` field successfully

**Approval**: Flask UX Designer + Quality Validator

---

### Gate 2: High-Traffic Routes (End of Phase 2)
**Criteria**:
- [ ] Dashboard, work items, tasks pass UX review
- [ ] All high-traffic routes have breadcrumbs
- [ ] All high-traffic routes have loading states
- [ ] Sort controls functional on lists
- [ ] Accessibility audit: 0 critical issues

**Approval**: Quality Validator + Product Owner

---

### Gate 3: System Routes (End of Phase 3)
**Criteria**:
- [ ] Agents, rules, projects consistent with high-traffic routes
- [ ] All system routes pass design system compliance
- [ ] Chart color palette standardized
- [ ] Role badge colors semantic

**Approval**: Flask UX Designer

---

### Gate 4: Content Routes (End of Phase 4)
**Criteria**:
- [ ] All content routes have breadcrumbs
- [ ] All content routes have loading states
- [ ] All detail pages have quick actions
- [ ] Empty states engaging and helpful

**Approval**: Flask UX Designer

---

### Gate 5: Accessibility Audit (End of Phase 5)
**Criteria**:
- [ ] WCAG 2.1 AA compliance: 100%
- [ ] Screen reader testing passed
- [ ] Keyboard navigation: all routes functional
- [ ] Color contrast: all text meets 4.5:1 minimum
- [ ] Focus visible on all interactive elements

**Approval**: Quality Validator + Accessibility Specialist

---

### Gate 6: Cross-Browser Testing (End of Phase 5)
**Criteria**:
- [ ] Chrome: All routes functional
- [ ] Firefox: All routes functional
- [ ] Safari: All routes functional
- [ ] Mobile Safari: All routes functional
- [ ] Mobile Chrome: All routes functional

**Approval**: Testing Specialist

---

### Gate 7: Performance Targets (End of Phase 5)
**Criteria**:
- [ ] Lighthouse Performance: ≥90
- [ ] Lighthouse Accessibility: 100
- [ ] First Contentful Paint: <1.0s
- [ ] Largest Contentful Paint: <2.5s

**Approval**: Performance Engineer

---

### Gate 8: Documentation Complete (End of Phase 6)
**Criteria**:
- [ ] Design system docs updated
- [ ] Component usage guide created
- [ ] Accessibility patterns documented
- [ ] Migration guide for developers

**Approval**: Documentation Specialist + Product Owner

---

## 8. Dependencies & Blockers

### 8.1 External Dependencies
- **Tailwind CSS 3.4.14**: Already installed ✅
- **Alpine.js 3.14.1**: Already installed ✅
- **Bootstrap Icons**: Already installed ✅
- **Chart.js 3.x**: Already installed ✅

### 8.2 Internal Dependencies
- **Database Migration**: Required for `tier` field (Phase 1)
- **Design System Approval**: Required before Phase 2
- **Accessibility Expert**: Consultation needed for complex ARIA patterns

### 8.3 Known Blockers
- None currently identified

---

## 9. Team Assignments

| Phase | Primary Agent | Support Agent | Reviewer |
|-------|---------------|---------------|----------|
| **Phase 1** | Flask UX Designer | Database Developer | Quality Validator |
| **Phase 2** | Flask UX Designer | Frontend Developer | Quality Validator |
| **Phase 3** | Flask UX Designer | - | Flask UX Designer |
| **Phase 4** | Flask UX Designer | - | Flask UX Designer |
| **Phase 5** | Testing Specialist | Flask UX Designer | Quality Validator |
| **Phase 6** | Documentation Specialist | Flask UX Designer | Product Owner |

---

## 10. Communication Plan

### 10.1 Weekly Status Reports
**Frequency**: Every Friday
**Format**: Markdown report in `docs/communication/status_report/`
**Content**:
- Progress vs. plan
- Blockers and risks
- Quality gate status
- Next week's focus

### 10.2 Phase Completion Reviews
**Frequency**: End of each phase
**Format**: Live review meeting + written report
**Attendees**: Project Owner, Flask UX Designer, Quality Validator

### 10.3 Daily Standups (Optional)
**Frequency**: Daily during Phases 2-4
**Format**: Async Slack update
**Content**:
- Yesterday's progress
- Today's plan
- Blockers

---

## 11. Rollback Plan

### 11.1 Version Control Strategy
- **Branch**: `feature/wi-141-frontend-polish`
- **Commits**: Atomic (one issue per commit)
- **Tags**: Phase completion milestones

### 11.2 Rollback Triggers
- Performance regression >20%
- Critical accessibility issue discovered
- Browser compatibility failure
- User-reported critical bug

### 11.3 Rollback Procedure
1. Identify problematic commit
2. Revert commit on branch
3. Re-test affected routes
4. Deploy hotfix if needed
5. Document issue in post-mortem

---

## 12. Post-Launch Monitoring

### 12.1 Metrics to Track (First 30 Days)
- User engagement (page views, time on page)
- Error rates (JavaScript errors, 500s)
- Performance (LCP, FCP, CLS)
- Accessibility issues (user reports)
- Browser compatibility issues

### 12.2 Continuous Improvement
- Weekly UX feedback sessions
- Monthly accessibility audits
- Quarterly design system updates
- User testing (A/B tests for major changes)

---

## 13. Reference Documentation

### 13.1 Design System
- **Main Doc**: `docs/architecture/web/design-system.md`
- **Components**: `docs/architecture/web/component-snippets.md`
- **Quick Start**: `docs/architecture/web/quick-start.md`
- **Color Reference**: `docs/architecture/web/color-reference.html`

### 13.2 Route Reviews (Tasks 781-808)
- Work Items List: `docs/architecture/web/work-items-list-ux-review.md`
- Agents List: `docs/architecture/web/agents-list-ux-review.md`
- Dashboard: `docs/architecture/web/dashboard-ux-review.md`
- ... (28 total reviews)

### 13.3 UX Strategy
- **Strategy Doc**: `docs/architecture/web/ux-enhancement-strategy.md`
- **Visual Guide**: `docs/architecture/web/ux-enhancement-visual-guide.md`

### 13.4 Accessibility
- **WCAG 2.1 Quick Reference**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Patterns**: https://www.w3.org/WAI/ARIA/apg/patterns/

### 13.5 Tailwind CSS
- **Docs**: https://tailwindcss.com/docs
- **Cheat Sheet**: https://nerdcave.com/tailwind-cheat-sheet

---

## Appendix A: Complete Issue List

### Critical Issues (C-001 to C-012)
[Full list in section 1.1]

### High Priority Issues (H-001 to H-045)
[Partial list in section 1.2, full spreadsheet available]

### Medium Priority Issues (78 total)
[Grouped by category in section 1.3]

### Low Priority Issues (52 total)
[Grouped by category in section 1.4]

---

## Appendix B: Before/After Examples

### Example 1: Work Items List Breadcrumbs

**Before**:
```html
<h1>Work Items</h1>
<!-- No navigation context -->
```

**After**:
```html
{% from 'components/breadcrumbs.html' import render %}
{{ render([{'name': 'Work Items', 'url': None}]) }}
<h1>Work Items</h1>
```

### Example 2: Loading States

**Before**:
```html
<!-- No loading indicator -->
<div class="grid grid-cols-3 gap-6">
  {% for item in items %}
    <div class="card">{{ item.name }}</div>
  {% endfor %}
</div>
```

**After**:
```html
<div x-data="{ loading: true }" x-init="setTimeout(() => loading = false, 500)">
  <div x-show="loading">
    {% from 'components/skeleton.html' import card %}
    {{ card() }}
    {{ card() }}
    {{ card() }}
  </div>
  <div x-show="!loading" x-transition class="grid grid-cols-3 gap-6">
    {% for item in items %}
      <div class="card">{{ item.name }}</div>
    {% endfor %}
  </div>
</div>
```

### Example 3: Status Badges

**Before**:
```html
<span class="badge" style="background: #4facfe; color: white;">
  {{ status }}
</span>
```

**After**:
```html
{% from 'components/badge.html' import status_badge %}
{{ status_badge(status) }}
```

---

**Roadmap Version**: 1.0
**Created**: 2025-10-22
**Last Updated**: 2025-10-22
**Status**: APPROVED
**Approval**: Pending Product Owner Review
**Estimated Completion**: Week of 2025-11-25 (6 weeks from start)
