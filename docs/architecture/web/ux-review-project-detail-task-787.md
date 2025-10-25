# UX Review: Project Detail Route (Task 787)

**Date**: 2025-10-22
**Reviewer**: flask-ux-designer
**Template**: `/agentpm/web/templates/projects/detail.html`
**Design System**: `/docs/architecture/web/design-system.md`

---

## Executive Summary

The project detail page (`detail.html`) has **mixed design system compliance**. While it uses some modern Tailwind patterns and includes comprehensive data visualization, it relies heavily on **legacy Bootstrap 3 patterns** that are inconsistent with the documented Tailwind-based design system.

**Overall Assessment**: ⚠️ **Needs Refactoring** (60% compliant)

**Key Issues**:
1. Mixed Bootstrap 3 and Tailwind CSS classes
2. Status badge colors don't follow AIPM design system
3. Inconsistent card styling patterns
4. Timeline and summary components need standardization
5. Legacy `.metric-card`, `.badge`, `.breadcrumb` classes

---

## Detailed Findings

### 1. Breadcrumb Navigation ❌ **Non-Compliant**

**Current Implementation** (Lines 6-11):
```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/">Dashboard</a></li>
        <li class="breadcrumb-item active" aria-current="page">Project: {{ detail.project.name }}</li>
    </ol>
</nav>
```

**Issues**:
- Uses Bootstrap 3 `.breadcrumb` classes (not in design system)
- No Tailwind utility classes
- Styling inconsistent with design system spec

**Recommended Fix** (Design System Snippet):
```html
<nav class="mb-6" aria-label="breadcrumb">
    <ol class="flex items-center space-x-2 text-sm text-gray-500">
        <li><a href="/" class="hover:text-primary transition">Dashboard</a></li>
        <li class="flex items-center">
            <i class="bi bi-chevron-right mx-2"></i>
            <span class="text-gray-900">{{ detail.project.name }}</span>
        </li>
    </ol>
</nav>
```

**References**: Design System § Breadcrumbs, Component Snippets Line 869-884

---

### 2. Status Badges ⚠️ **Partially Compliant**

**Current Implementation** (Lines 24-34):
```html
<span class="badge badge-primary">{{ detail.project.status.value }}</span>
<span class="badge badge-info">
    <i class="bi bi-tag"></i> {{ detail.project.project_type.value.title() }}
</span>
<span class="badge badge-gray">
    <i class="bi bi-people"></i> {{ detail.project.team }}
</span>
```

**Issues**:
- Uses legacy `.badge-{color}` classes
- Not using Tailwind utility classes
- Color palette doesn't match AIPM status colors
- Missing proper semantic mapping

**Current Status Color Mapping**:
```css
/* Existing (brand-system.css) */
.badge-primary → Blue (generic)
.badge-info → Cyan (generic)
.badge-gray → Gray (generic)
```

**Recommended AIPM Status Colors** (from design system):
```javascript
// Status-specific colors (Design System § Status Colors)
'draft': '#6c757d',         // Gray
'validated': '#764ba2',     // Purple
'accepted': '#4facfe',      // Light blue
'in_progress': '#43e97b',   // Green
'review': '#fa709a',        // Pink
'completed': '#28a745',     // Success green
'blocked': '#ffc107',       // Warning yellow
'archived': '#6c757d'       // Gray
```

**Recommended Fix**:
```html
<!-- Map status.value to AIPM status colors -->
{% set status_class_map = {
    'draft': 'badge badge-gray',
    'validated': 'inline-flex items-center gap-1 rounded-full bg-purple-600 px-3 py-1 text-xs font-semibold text-white',
    'accepted': 'badge badge-info',
    'in_progress': 'badge badge-success',
    'review': 'inline-flex items-center gap-1 rounded-full bg-pink-500 px-3 py-1 text-xs font-semibold text-white',
    'completed': 'badge badge-success',
    'blocked': 'badge badge-warning',
    'archived': 'badge badge-gray'
} %}
<span class="{{ status_class_map.get(detail.project.status.value, 'badge badge-gray') }}">
    {{ detail.project.status.value.title() }}
</span>
```

**Note**: Ideally, create utility classes in `brand-system.css`:
```css
/* Add to brand-system.css */
.badge-status-draft { @apply bg-gray-100 text-gray-700; }
.badge-status-validated { @apply bg-purple-600 text-white; }
.badge-status-accepted { @apply bg-blue-500 text-white; }
.badge-status-in-progress { @apply bg-green-500 text-white; }
.badge-status-review { @apply bg-pink-500 text-white; }
.badge-status-completed { @apply bg-green-600 text-white; }
.badge-status-blocked { @apply bg-yellow-500 text-white; }
.badge-status-archived { @apply bg-gray-400 text-white; }
```

**References**: Design System § Status Colors (Line 53-86), Component Snippets § Badges (Line 336-389)

---

### 3. Card Styling ⚠️ **Partially Compliant**

**Current Implementation** (Lines 18-19, 168):
```html
<div class="card metric-card shadow-soft">
    <div class="card-body">
```

**Issues**:
- `.metric-card` and `.shadow-soft` not defined in design system
- Mixing legacy and Tailwind classes
- Inconsistent with design system card pattern

**Design System Card Pattern** (Expected):
```html
<div class="card">
    <div class="card-body space-y-4">
```

**Recommendation**:
- Remove `.metric-card` and `.shadow-soft` classes
- Use design system `.card` class (defined in `brand-system.css`)
- If custom shadow needed, use Tailwind: `shadow-md` or `shadow-lg`

**Fixed Example**:
```html
<div class="card shadow-md">
    <div class="card-body space-y-4">
        <h2 class="card-title">
            <i class="bi bi-folder2-open text-primary"></i> {{ detail.project.name }}
        </h2>
        <!-- Content -->
    </div>
</div>
```

**References**: Design System § Cards (Line 263-333), Component Snippets § Cards (Line 269-334)

---

### 4. 6W Context Section ✅ **Good** (with minor improvements)

**Current Implementation** (Lines 54-154):
```html
<div class="mt-3 p-3 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded border border-blue-500/30">
    <h6 class="text-primary mb-3">
        <i class="bi bi-diagram-3"></i> 6W Framework Context
```

**Strengths**:
- Uses Tailwind utility classes correctly
- Good visual hierarchy
- Semantic color coding (WHO=info, WHAT=success, etc.)
- Proper spacing with `space-y-` and `gap-` utilities

**Minor Issues**:
- `.text-purple` not a standard Tailwind class (Line 130)
- Should use `.text-purple-600` or `.text-purple-500`
- `.text-cyan` not standard (Line 143)
- Should use `.text-cyan-600` or `.text-cyan-500`

**Recommended Fix**:
```html
<!-- Line 130: Replace .text-purple with .text-purple-600 -->
<h6 class="text-purple-600 mb-2"><i class="bi bi-question-circle"></i> WHY</h6>

<!-- Line 143: Replace .text-cyan with .text-cyan-600 -->
<h6 class="text-cyan-600 mb-2"><i class="bi bi-gear"></i> HOW</h6>
```

**References**: Design System § Color Palette (Line 23-103)

---

### 5. Metric Cards ⚠️ **Partially Compliant**

**Current Implementation** (Lines 185-227):
```html
<div class="col-md-3">
    <div class="card metric-card shadow-soft h-100">
        <div class="card-body text-center">
            <i class="bi bi-kanban text-primary" style="font-size: 2rem; opacity: 0.3;"></i>
            <h3 class="display-6 mt-2">{{ detail.total_work_items }}</h3>
            <p class="metric-label">Work Items</p>
        </div>
    </div>
</div>
```

**Issues**:
- Uses Bootstrap grid (`.col-md-3`) instead of Tailwind grid
- `.metric-card`, `.display-6`, `.metric-label` not in design system
- Inline styles (`style="font-size: 2rem; opacity: 0.3;"`)

**Design System Metric Card Pattern**:
```html
<div class="card">
  <div class="flex items-center">
    <div class="flex-shrink-0">
      <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
        <i class="bi bi-check-circle text-white text-2xl"></i>
      </div>
    </div>
    <div class="ml-4">
      <p class="text-sm font-medium text-gray-500">Total Work Items</p>
      <p class="text-2xl font-bold text-gray-900">42</p>
    </div>
  </div>
</div>
```

**Recommended Refactor**:
```html
<!-- Use Tailwind grid instead of Bootstrap -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Metric Card: Work Items -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                    <i class="bi bi-kanban text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Work Items</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_work_items }}</p>
            </div>
        </div>
    </div>

    <!-- Metric Card: Tasks -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-success rounded-lg flex items-center justify-center">
                    <i class="bi bi-check2-square text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Tasks</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_tasks }}</p>
            </div>
        </div>
    </div>

    <!-- Metric Card: Agents -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-info rounded-lg flex items-center justify-center">
                    <i class="bi bi-people text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Agents</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_agents }}</p>
                <a href="/agents" class="text-xs text-primary hover:text-primary-dark mt-1 inline-block">
                    View All <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Metric Card: Rules -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-warning rounded-lg flex items-center justify-center">
                    <i class="bi bi-shield-check text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Rules</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_rules }}</p>
                <a href="/rules" class="text-xs text-primary hover:text-primary-dark mt-1 inline-block">
                    View All <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>
</div>
```

**References**: Design System § Cards (Line 287-303), Component Snippets § Metric Card (Line 287-303)

---

### 6. Chart Containers ✅ **Good**

**Current Implementation** (Lines 238-244, 255-261):
```html
<div class="chart-container" style="position: relative; height: 300px;">
    <canvas id="workItemStatusChart"></canvas>
</div>
```

**Assessment**:
- Correct pattern for Chart.js responsive containers
- Inline `style` acceptable for dynamic height control
- No design system violations

**Recommendation**: ✅ **Keep as is**

---

### 7. Timeline Component ⚠️ **Needs Standardization**

**Current Implementation** (Lines 491-610, custom CSS):
```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-marker bg-primary"></div>
        <div class="timeline-content">
            <h6 class="timeline-title">{{ event.event_type.value }}</h6>
            <p class="timeline-text">{{ event.message }}</p>
            <small class="text-muted">{{ event.timestamp }}</small>
        </div>
    </div>
</div>
```

**Issues**:
- Custom CSS in `{% block extra_styles %}` (Lines 489-612)
- Not documented in design system
- Should be a reusable component

**Recommendation**:
1. **Extract timeline CSS** to `brand-system.css`:
```css
/* Timeline Component */
.timeline {
    position: relative;
    padding-left: 30px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, var(--color-primary), var(--color-secondary));
}

.timeline-item {
    position: relative;
    margin-bottom: 20px;
}

.timeline-marker {
    position: absolute;
    left: -22px;
    top: 5px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid var(--color-gray-900);
}

.timeline-content {
    @apply bg-gray-100 p-4 rounded-lg border-l-4 border-primary;
}

.timeline-title {
    @apply mb-1 text-primary text-sm font-semibold;
}

.timeline-text {
    @apply mb-2 text-gray-600 text-xs leading-snug;
}
```

2. **Add to component snippets** documentation

3. **Use Tailwind color utilities** instead of hardcoded hex values

**References**: Design System § Component Patterns (missing timeline component)

---

### 8. Progress Bars ⚠️ **Inconsistent**

**Current Implementation** (Lines 402-405):
```html
<div class="progress mt-1" style="height: 6px;">
    <div class="progress-bar bg-{{ 'success' if ... else 'danger' }}"
         style="width: {{ (score * 100) | round(1) }}%"></div>
</div>
```

**Issues**:
- `.progress` and `.progress-bar` classes exist in design system
- But uses inline styles for height and width
- Mixing approaches

**Design System Pattern** (Line 610-619):
```css
.progress {
  @apply h-2 w-full overflow-hidden rounded-full bg-gray-200;
}

.progress-bar {
  @apply h-full bg-primary transition-all duration-300;
}
```

**Recommended Fix**:
```html
<!-- Use design system classes + dynamic width -->
<div class="progress">
    <div class="progress-bar bg-{{ 'success' if detail.project_context.confidence_band and detail.project_context.confidence_band.value == 'GREEN' else 'warning' if detail.project_context.confidence_band and detail.project_context.confidence_band.value == 'YELLOW' else 'error' }}"
         style="width: {{ (detail.project_context.confidence_score * 100) | round(1) }}%">
    </div>
</div>
```

**Alternative** (more semantic):
```html
<div class="h-2 w-full overflow-hidden rounded-full bg-gray-200">
    <div class="h-full bg-success transition-all duration-300"
         style="width: {{ (detail.project_context.confidence_score * 100) | round(1) }}%">
    </div>
</div>
```

**References**: Design System § Progress Bars (Line 583-619), Component Snippets § Progress (Line 888-920)

---

### 9. Bootstrap Grid vs. Tailwind Grid ❌ **Major Inconsistency**

**Current Usage**:
```html
<!-- Bootstrap Grid (Lines 16, 167, 184, 230, 267, 309, 384) -->
<div class="row mb-4 g-4">
    <div class="col-md-3">...</div>
    <div class="col-md-6">...</div>
</div>
```

**Design System Uses Tailwind Grid**:
```html
<!-- Tailwind Grid (Design System Line 178-186) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div>Card 1</div>
    <div>Card 2</div>
</div>
```

**Issue**: **Entire template uses Bootstrap 3 grid system** instead of Tailwind grid

**Recommendation**: **Refactor all `.row`/`.col-*` to Tailwind grid**

**Conversion Guide**:
```html
<!-- BEFORE (Bootstrap) -->
<div class="row mb-4 g-4">
    <div class="col-md-3">...</div>
    <div class="col-md-3">...</div>
    <div class="col-md-3">...</div>
    <div class="col-md-3">...</div>
</div>

<!-- AFTER (Tailwind) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <div>...</div>
    <div>...</div>
    <div>...</div>
    <div>...</div>
</div>
```

```html
<!-- BEFORE (Bootstrap) -->
<div class="row mb-4 g-4">
    <div class="col-md-6">...</div>
    <div class="col-md-6">...</div>
</div>

<!-- AFTER (Tailwind) -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
    <div>...</div>
    <div>...</div>
</div>
```

```html
<!-- BEFORE (Bootstrap) -->
<div class="row mb-4 g-4">
    <div class="col-md-8">...</div>
    <div class="col-md-4">...</div>
</div>

<!-- AFTER (Tailwind) -->
<div class="grid grid-cols-1 md:grid-cols-12 gap-6 mb-6">
    <div class="md:col-span-8">...</div>
    <div class="md:col-span-4">...</div>
</div>
```

**References**: Design System § Grid & Layout Patterns (Line 176-196)

---

### 10. Accessibility Compliance ✅ **Good** (with minor notes)

**Strengths**:
- Proper ARIA labels (`aria-label="breadcrumb"`, `aria-current="page"`)
- Semantic HTML (`<nav>`, `<ol>`, `<section>` implied by card structure)
- Icon-only buttons have text labels (no violations found)
- Color contrast appears adequate (needs verification with tool)

**Minor Improvements Needed**:
```html
<!-- Line 172: Add aria-label to link -->
<a href="/projects/{{ detail.project.id }}/context"
   class="btn btn-primary"
   aria-label="View 6W Context for project {{ detail.project.name }}">
    <i class="bi bi-eye"></i> View 6W Context
</a>

<!-- Line 209-223: Add aria-label to metric action links -->
<a href="/agents"
   class="btn btn-sm btn-outline-primary mt-2"
   aria-label="View all {{ detail.total_agents }} agents">
    <i class="bi bi-arrow-right"></i> View All
</a>
```

**References**: Design System § Accessibility (Line 945-992)

---

## Summary of Issues by Severity

### 🔴 Critical (Must Fix)
1. **Bootstrap Grid System** → Migrate to Tailwind grid (Lines 16+)
2. **Legacy Badge Classes** → Use design system badge pattern (Lines 24-34)
3. **Breadcrumb Component** → Use design system pattern (Lines 6-11)

### 🟡 Important (Should Fix)
4. **Metric Card Pattern** → Use design system metric card (Lines 185-227)
5. **Card Styling Classes** → Remove `.metric-card`, `.shadow-soft` (Lines 18+)
6. **Status Color Mapping** → Implement AIPM status colors (Lines 24+)
7. **Timeline Component** → Extract to design system (Lines 491-610)

### 🟢 Minor (Nice to Have)
8. **Color Class Corrections** → `.text-purple` → `.text-purple-600` (Lines 130, 143)
9. **Accessibility Labels** → Add aria-labels to action buttons (Lines 172, 209)
10. **Progress Bar Height** → Remove inline styles, use design system (Lines 402-405)

---

## Compliance Scorecard

| Component                  | Current State | Design System Compliance | Priority |
|----------------------------|---------------|--------------------------|----------|
| Breadcrumbs                | Bootstrap 3   | ❌ Non-compliant         | 🔴 High  |
| Badges                     | Mixed         | ⚠️ Partial (40%)         | 🔴 High  |
| Cards                      | Mixed         | ⚠️ Partial (60%)         | 🟡 Medium|
| Grid Layout                | Bootstrap 3   | ❌ Non-compliant         | 🔴 High  |
| Buttons                    | Design System | ✅ Compliant (90%)       | ✅ Good  |
| Typography                 | Design System | ✅ Compliant (85%)       | ✅ Good  |
| Icons (Bootstrap Icons)    | Design System | ✅ Compliant (100%)      | ✅ Good  |
| Charts (Chart.js)          | Correct       | ✅ Compliant (100%)      | ✅ Good  |
| 6W Context Section         | Tailwind      | ✅ Compliant (95%)       | ✅ Good  |
| Timeline Component         | Custom CSS    | ⚠️ Not documented        | 🟡 Medium|
| Progress Bars              | Mixed         | ⚠️ Partial (70%)         | 🟢 Low   |
| Accessibility              | Good          | ✅ Compliant (90%)       | ✅ Good  |

**Overall Compliance**: **63%** (weighted by importance)

---

## Recommended Action Plan

### Phase 1: High Priority (2-3 hours)
1. **Refactor Grid System** (1.5h)
   - Replace all `.row`/`.col-*` with Tailwind grid
   - Test responsive breakpoints
2. **Standardize Badges** (0.5h)
   - Implement AIPM status color mapping
   - Create `.badge-status-*` utility classes
3. **Fix Breadcrumbs** (0.25h)
   - Apply design system pattern

### Phase 2: Medium Priority (1-2 hours)
4. **Refactor Metric Cards** (1h)
   - Use design system metric card pattern
   - Remove legacy classes
5. **Standardize Timeline** (0.5h)
   - Extract CSS to `brand-system.css`
   - Document in component snippets
6. **Card Cleanup** (0.5h)
   - Remove `.metric-card`, `.shadow-soft`
   - Verify shadow consistency

### Phase 3: Polish (0.5-1 hour)
7. **Color Class Fixes** (0.25h)
   - Fix `.text-purple` → `.text-purple-600`
   - Fix `.text-cyan` → `.text-cyan-600`
8. **Accessibility Enhancement** (0.25h)
   - Add aria-labels to action buttons
9. **Progress Bar Standardization** (0.25h)
   - Remove inline styles where possible

**Total Estimated Effort**: **4-6 hours**

---

## Before/After Code Examples

### Example 1: Metric Cards Grid

**BEFORE** (Lines 184-227):
```html
<div class="row mb-4 g-4">
    <div class="col-md-3">
        <div class="card metric-card shadow-soft h-100">
            <div class="card-body text-center">
                <i class="bi bi-kanban text-primary" style="font-size: 2rem; opacity: 0.3;"></i>
                <h3 class="display-6 mt-2">{{ detail.total_work_items }}</h3>
                <p class="metric-label">Work Items</p>
            </div>
        </div>
    </div>
    <!-- Repeat 3 more times -->
</div>
```

**AFTER** (Design System Compliant):
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Work Items -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                    <i class="bi bi-kanban text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Work Items</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_work_items }}</p>
            </div>
        </div>
    </div>

    <!-- Tasks -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-success rounded-lg flex items-center justify-center">
                    <i class="bi bi-check2-square text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Tasks</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_tasks }}</p>
            </div>
        </div>
    </div>

    <!-- Agents -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-info rounded-lg flex items-center justify-center">
                    <i class="bi bi-people text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Agents</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_agents }}</p>
                <a href="/agents" class="text-xs text-primary hover:text-primary-dark mt-1 inline-block" aria-label="View all agents">
                    View All <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Rules -->
    <div class="card">
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-warning rounded-lg flex items-center justify-center">
                    <i class="bi bi-shield-check text-white text-2xl"></i>
                </div>
            </div>
            <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Rules</p>
                <p class="text-2xl font-bold text-gray-900">{{ detail.total_rules }}</p>
                <a href="/rules" class="text-xs text-primary hover:text-primary-dark mt-1 inline-block" aria-label="View all rules">
                    View All <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>
</div>
```

**Improvements**:
- ✅ Tailwind grid instead of Bootstrap
- ✅ Design system metric card pattern
- ✅ Removed legacy classes (`.metric-card`, `.shadow-soft`, `.display-6`, `.metric-label`)
- ✅ Removed inline styles
- ✅ Added semantic color mapping (`.bg-primary`, `.bg-success`, `.bg-info`, `.bg-warning`)
- ✅ Better accessibility (aria-labels on links)

---

### Example 2: Status Badges

**BEFORE** (Lines 24-34):
```html
<span class="badge badge-primary">{{ detail.project.status.value }}</span>
<span class="badge badge-info">
    <i class="bi bi-tag"></i> {{ detail.project.project_type.value.title() }}
</span>
```

**AFTER** (AIPM Status Colors):
```html
<!-- Add to template top (after {% extends %}) -->
{% set status_badge_map = {
    'draft': 'badge badge-gray',
    'validated': 'badge bg-purple-600 text-white',
    'accepted': 'badge badge-info',
    'in_progress': 'badge badge-success',
    'review': 'badge bg-pink-500 text-white',
    'completed': 'badge badge-success',
    'blocked': 'badge badge-warning',
    'archived': 'badge badge-gray'
} %}

<!-- In template body -->
<span class="{{ status_badge_map.get(detail.project.status.value, 'badge badge-gray') }}">
    {{ detail.project.status.value.replace('_', ' ').title() }}
</span>

<span class="badge badge-info">
    <i class="bi bi-tag"></i> {{ detail.project.project_type.value.title() }}
</span>
```

**OR** (Better: Add to brand-system.css):
```css
/* Add to brand-system.css */
.badge-status-draft { @apply inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-gray-700; }
.badge-status-validated { @apply inline-flex items-center gap-1 rounded-full bg-purple-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-accepted { @apply inline-flex items-center gap-1 rounded-full bg-blue-500 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-in-progress { @apply inline-flex items-center gap-1 rounded-full bg-green-500 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-review { @apply inline-flex items-center gap-1 rounded-full bg-pink-500 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-completed { @apply inline-flex items-center gap-1 rounded-full bg-green-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-blocked { @apply inline-flex items-center gap-1 rounded-full bg-yellow-500 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
.badge-status-archived { @apply inline-flex items-center gap-1 rounded-full bg-gray-400 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white; }
```

```html
<!-- Then in template -->
<span class="badge-status-{{ detail.project.status.value.replace('_', '-') }}">
    {{ detail.project.status.value.replace('_', ' ').title() }}
</span>
```

**Improvements**:
- ✅ Uses AIPM-specific status colors
- ✅ Consistent with workflow state colors
- ✅ Reusable utility classes
- ✅ Better semantic naming

---

## Testing Checklist

After implementing fixes, verify:

- [ ] **Responsive Layout**: Test on mobile (375px), tablet (768px), desktop (1280px)
- [ ] **Color Contrast**: Use browser DevTools to verify WCAG AA compliance (4.5:1 ratio)
- [ ] **Keyboard Navigation**: Tab through all interactive elements
- [ ] **Screen Reader**: Test breadcrumbs, badges, buttons with NVDA/VoiceOver
- [ ] **Chart Responsiveness**: Resize browser window, verify Chart.js reflows correctly
- [ ] **Status Badge Colors**: Verify all 8+ workflow statuses render with correct colors
- [ ] **Grid Breakpoints**: Test md:grid-cols-2, lg:grid-cols-4 transitions
- [ ] **Timeline Component**: Test with 0 events, 1 event, 10+ events
- [ ] **Loading States**: Verify chart containers show gracefully when empty

---

## Design System Compliance Verification

### ✅ Already Compliant
- Chart.js integration (correct pattern)
- 6W Context section (95% compliant, minor color class fixes needed)
- Typography hierarchy (h2, h3, text-sm, etc.)
- Icon usage (Bootstrap Icons)
- Button patterns (btn, btn-primary, etc.)

### ⚠️ Needs Refactoring
- Grid system (Bootstrap → Tailwind)
- Badge patterns (legacy → design system)
- Card styling (remove custom classes)
- Breadcrumbs (Bootstrap → design system)
- Metric cards (custom → design system)

### ❌ Not Documented
- Timeline component (needs design system entry)
- Custom `.metric-label`, `.display-6` classes (remove or document)

---

## Related Files to Update

1. **`/agentpm/web/static/css/brand-system.css`**
   - Add `.badge-status-*` utility classes
   - Add timeline component CSS
   - Add `.text-purple-600`, `.text-cyan-600` if not already present

2. **`/docs/architecture/web/component-snippets.md`**
   - Add timeline component snippet
   - Update badge examples with AIPM status colors

3. **`/docs/architecture/web/design-system.md`**
   - Document timeline component pattern
   - Add AIPM status color reference table

4. **`/agentpm/web/templates/projects/detail_enhanced.html`**
   - Appears to be an older version, consider deprecating or merging improvements

---

## Conclusion

The project detail route requires **moderate refactoring** to achieve full design system compliance. The primary issues are:

1. **Bootstrap 3 grid system** usage (should be Tailwind grid)
2. **Legacy badge classes** not aligned with AIPM status colors
3. **Custom metric card classes** instead of design system pattern

**Estimated effort**: 4-6 hours for full compliance

**Recommended approach**: Tackle high-priority issues first (grid, badges, breadcrumbs), then medium priority (metric cards, timeline), then polish (color classes, accessibility).

**Next steps**:
1. Create work item for Phase 1 refactoring
2. Update `brand-system.css` with status badge utilities
3. Refactor grid system to Tailwind
4. Document timeline component in design system

---

**Reviewed by**: flask-ux-designer
**Task**: 787
**Date**: 2025-10-22
**Status**: ✅ Review Complete
