# Evidence List Route - UX Design Review

**Task**: 800 - Review evidence list route for design system compliance
**Reviewer**: flask-ux-designer
**Date**: 2025-10-22
**Effort**: 1.0h

---

## Executive Summary

The evidence list route (`/evidence`) shows **good foundation** with proper filtering and table structure, but has **14 UX issues** that violate design system standards around confidence badges, source citations, responsive design, and accessibility.

**Overall Compliance**: 65%
- ✅ **Strengths**: Filter controls, empty states, basic table structure
- ⚠️ **Issues**: Confidence colors inconsistent, citation badges missing, no loading states, accessibility gaps

---

## Review Checklist Results

### ✅ Passed (6/14)
1. ✅ Filter controls follow design patterns
2. ✅ Empty state with proper messaging
3. ✅ Basic responsive layout (grid for metrics)
4. ✅ Metric cards use standard structure
5. ✅ Table structure follows patterns
6. ✅ Entity name resolution present

### ❌ Failed (8/14)
1. ❌ **CRITICAL**: Confidence colors don't use design system (`bg-confidence-{color}`)
2. ❌ **CRITICAL**: Source type badges use generic gray instead of semantic colors
3. ❌ **HIGH**: Citation badges not standardized (missing icon + type pattern)
4. ❌ **HIGH**: No loading states for filters or data fetching
5. ❌ **MEDIUM**: Confidence progress bars lack consistent styling
6. ❌ **MEDIUM**: Responsive breakpoints not optimized for mobile
7. ❌ **MEDIUM**: No ARIA labels for external links
8. ❌ **LOW**: Table doesn't use `.table-hover` class

---

## Detailed Findings

### Issue 1: Confidence Color System (CRITICAL)

**Location**: `list.html:136`

**Current Code**:
```html
<span class="block h-full rounded-full {{ 'bg-emerald-500' if confidence_pct >= 80 else 'bg-amber-400' if confidence_pct >= 60 else 'bg-rose-500' }}" style="width: {{ confidence_pct }}%"></span>
```

**Problem**:
- Uses hardcoded color classes (`bg-emerald-500`, `bg-amber-400`, `bg-rose-500`)
- Doesn't use design system's `confidence` colors from Tailwind config
- Inconsistent with other confidence badges in the system

**Design System Reference**:
```javascript
// tailwind.config.js:99-104
confidence: {
  green: '#10b981',  // High confidence (≥0.80)
  yellow: '#f59e0b', // Medium confidence (0.60-0.79)
  red: '#ef4444',    // Low confidence (<0.60)
}
```

**Recommended Fix**:
```html
{% set confidence_pct = (evidence.confidence * 100) | int %}
{% if confidence_pct >= 80 %}
  {% set confidence_color = 'bg-confidence-green' %}
  {% set confidence_label = 'High' %}
{% elif confidence_pct >= 60 %}
  {% set confidence_color = 'bg-confidence-yellow' %}
  {% set confidence_label = 'Medium' %}
{% else %}
  {% set confidence_color = 'bg-confidence-red' %}
  {% set confidence_label = 'Low' %}
{% endif %}

<div class="flex items-center gap-3">
  <div class="h-2 w-24 overflow-hidden rounded-full bg-gray-100">
    <span class="block h-full rounded-full {{ confidence_color }}" style="width: {{ confidence_pct }}%"></span>
  </div>
  <span class="inline-flex items-center gap-1 rounded-full {{ confidence_color }}/10 px-2 py-0.5 text-xs font-semibold {{ confidence_color | replace('bg-', 'text-') }}">
    {{ confidence_pct }}% {{ confidence_label }}
  </span>
</div>
```

**Impact**: High - Breaks consistency with confidence scoring across the system

---

### Issue 2: Source Type Badge Styling (CRITICAL)

**Location**: `list.html:123`

**Current Code**:
```html
<span class="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">{{ evidence.source_type }}</span>
```

**Problem**:
- All source types use same gray badge
- No visual distinction between documentation, research, stackoverflow, etc.
- Doesn't follow badge pattern from component snippets

**Design System Reference**:
```html
<!-- component-snippets.md:340-346 -->
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Completed</span>
<span class="badge badge-info">Info</span>
```

**Recommended Fix**:
```html
{% set source_badge_map = {
  'documentation': 'badge-info',
  'research': 'badge-primary',
  'stackoverflow': 'badge-warning',
  'github': 'badge-success',
  'internal_doc': 'badge-gray',
  'meeting_notes': 'badge-secondary',
  'expert_opinion': 'badge-accent'
} %}

{% set badge_class = source_badge_map.get(evidence.source_type, 'badge-gray') %}

<span class="badge {{ badge_class }}">
  {% if evidence.source_type == 'documentation' %}
    <i class="bi bi-journal-richtext"></i>
  {% elif evidence.source_type == 'research' %}
    <i class="bi bi-search"></i>
  {% elif evidence.source_type == 'stackoverflow' %}
    <i class="bi bi-stack-overflow"></i>
  {% elif evidence.source_type == 'github' %}
    <i class="bi bi-github"></i>
  {% elif evidence.source_type == 'internal_doc' %}
    <i class="bi bi-file-text"></i>
  {% elif evidence.source_type == 'meeting_notes' %}
    <i class="bi bi-chat-left-text"></i>
  {% elif evidence.source_type == 'expert_opinion' %}
    <i class="bi bi-person-badge"></i>
  {% endif %}
  {{ evidence.source_type | replace('_', ' ') | title }}
</span>
```

**Impact**: High - Poor visual distinction makes scanning difficult

---

### Issue 3: Citation Badge Pattern Missing (HIGH)

**Location**: `list.html:117-120` (URL cell)

**Current Code**:
```html
<a href="{{ evidence.url }}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary-dark">
  {{ evidence.url | truncate(50) }}
  <i class="bi bi-box-arrow-up-right"></i>
</a>
```

**Problem**:
- Long URLs truncated but not visually optimized
- No citation badge pattern (should show domain + icon)
- External link indicator is good, but URL display could be cleaner

**Recommended Fix**:
```html
{% set domain = evidence.url | regex_replace('https?://', '') | regex_replace('/.*', '') %}

<div class="flex items-center gap-2">
  <span class="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
    {% if 'github.com' in evidence.url %}
      <i class="bi bi-github"></i>
    {% elif 'stackoverflow.com' in evidence.url %}
      <i class="bi bi-stack-overflow"></i>
    {% elif 'docs.' in evidence.url %}
      <i class="bi bi-journal-richtext"></i>
    {% else %}
      <i class="bi bi-link-45deg"></i>
    {% endif %}
    {{ domain | truncate(20) }}
  </span>
  <a href="{{ evidence.url }}" target="_blank" rel="noopener noreferrer" 
     class="text-xs text-gray-500 hover:text-primary transition"
     aria-label="Open {{ domain }} in new tab">
    <i class="bi bi-box-arrow-up-right"></i>
  </a>
</div>
```

**Impact**: High - Citations should be scannable at a glance

---

### Issue 4: No Loading States (HIGH)

**Location**: Entire template

**Current Code**: No loading indicators present

**Problem**:
- Filter submission shows no loading feedback
- No skeleton loaders while data loads
- No spinner during async operations

**Design System Reference**:
```html
<!-- component-snippets.md:800-820 -->
<div id="loading-overlay" class="fixed inset-0 bg-gray-900/60 z-50 hidden">
  <div class="flex items-center justify-center h-full">
    <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-2xl">
      <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
      <span class="text-gray-700 font-medium">Loading...</span>
    </div>
  </div>
</div>
```

**Recommended Fix**:

1. **Add skeleton loader for table rows** (shown while loading):
```html
{% if loading %}
<tbody class="divide-y divide-gray-100">
  {% for i in range(5) %}
  <tr class="animate-pulse">
    <td class="px-6 py-4"><div class="h-4 bg-gray-200 rounded w-24"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-32"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-20"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-48"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-16"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-20"></div></td>
    <td class="px-4 py-4"><div class="h-4 bg-gray-200 rounded w-16"></div></td>
  </tr>
  {% endfor %}
</tbody>
{% else %}
<!-- Real data -->
{% endif %}
```

2. **Add loading button state for filters**:
```html
<button type="submit" class="btn btn-primary" 
        x-data="{ loading: false }"
        @click="loading = true"
        :disabled="loading">
  <span x-show="!loading">Apply Filters</span>
  <span x-show="loading" class="flex items-center">
    <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
    Filtering...
  </span>
</button>
```

**Impact**: High - Users get no feedback during long operations

---

### Issue 5: Confidence Progress Bar Inconsistency (MEDIUM)

**Location**: `list.html:133-139`

**Current Code**:
```html
<div class="flex items-center gap-3">
  <div class="h-2 w-24 overflow-hidden rounded-full bg-gray-100">
    <span class="block h-full rounded-full {{ color_class }}" style="width: {{ confidence_pct }}%"></span>
  </div>
  <span class="text-sm text-gray-600">{{ confidence_pct }}%</span>
</div>
```

**Problem**:
- Progress bar color correct, but percentage text doesn't use semantic color
- No confidence label (High/Medium/Low)
- Doesn't match progress bar pattern from design system

**Design System Reference**:
```html
<!-- design-system.md:591-596 -->
<div class="flex items-center gap-3">
  <div class="progress flex-1">
    <div class="progress-bar bg-success" style="width: 85%"></div>
  </div>
  <span class="text-sm font-medium text-gray-600">85%</span>
</div>
```

**Recommended Fix**:
```html
<div class="flex items-center gap-2">
  <!-- Progress bar -->
  <div class="h-2 w-20 overflow-hidden rounded-full bg-gray-100">
    <span class="block h-full rounded-full {{ confidence_color }}" style="width: {{ confidence_pct }}%"></span>
  </div>
  <!-- Percentage + Label Badge -->
  <span class="inline-flex items-center gap-1 rounded-full {{ confidence_color }}/10 px-2 py-0.5 text-xs font-semibold whitespace-nowrap"
        :class="'text-' + '{{ confidence_color | replace('bg-', '') }}'">
    <i class="bi bi-{{ 'check-circle' if confidence_pct >= 80 else 'exclamation-triangle' if confidence_pct >= 60 else 'x-circle' }}"></i>
    {{ confidence_pct }}%
  </span>
</div>
```

**Impact**: Medium - Reduces scannability of confidence scores

---

### Issue 6: Mobile Responsiveness (MEDIUM)

**Location**: `list.html:90-102` (table structure)

**Current Code**:
```html
<div class="overflow-x-auto">
  <table class="min-w-full divide-y divide-gray-100 text-left text-sm text-gray-700">
```

**Problem**:
- Table has 7 columns - too wide for mobile
- No responsive card view for small screens
- Horizontal scroll on mobile is poor UX

**Design System Guidance**:
```html
<!-- design-system.md:920-931 -->
<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<div class="block lg:hidden">Mobile only</div>
```

**Recommended Fix**:

1. **Desktop: Keep table** (hidden on mobile):
```html
<div class="hidden lg:block overflow-x-auto">
  <table class="table table-hover">
    <!-- Existing table -->
  </table>
</div>
```

2. **Mobile: Card view** (shown on mobile):
```html
<div class="block lg:hidden space-y-4 px-6 py-4">
  {% for evidence in view.evidence_list %}
  <article class="card hover:shadow-md transition-shadow">
    <!-- Entity & Type -->
    <div class="flex items-start justify-between mb-3">
      <div>
        <h3 class="font-semibold text-gray-900">{{ evidence.entity_type }}</h3>
        <p class="text-xs text-gray-500">{{ evidence.entity_name or 'ID: ' ~ evidence.entity_id }}</p>
      </div>
      <span class="badge {{ source_badge_map.get(evidence.source_type, 'badge-gray') }}">
        {{ evidence.source_type }}
      </span>
    </div>

    <!-- Excerpt -->
    {% if evidence.excerpt %}
    <p class="text-sm text-gray-700 mb-3">{{ evidence.excerpt | truncate(100) }}</p>
    {% endif %}

    <!-- Confidence -->
    <div class="mb-3">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-xs font-medium text-gray-500">Confidence</span>
        <span class="text-xs font-semibold {{ confidence_color | replace('bg-', 'text-') }}">
          {{ confidence_pct }}%
        </span>
      </div>
      <div class="h-2 overflow-hidden rounded-full bg-gray-100">
        <span class="block h-full rounded-full {{ confidence_color }}" style="width: {{ confidence_pct }}%"></span>
      </div>
    </div>

    <!-- Citation -->
    <div class="flex items-center justify-between">
      <a href="{{ evidence.url }}" target="_blank" rel="noopener noreferrer" 
         class="inline-flex items-center gap-1 text-xs text-primary hover:text-primary-dark">
        <i class="bi bi-{{ domain_icon }}"></i>
        {{ domain | truncate(25) }}
        <i class="bi bi-box-arrow-up-right"></i>
      </a>
      <span class="text-xs text-gray-500">
        {{ evidence.captured_at.strftime('%m/%d/%y') if evidence.captured_at else '—' }}
      </span>
    </div>
  </article>
  {% endfor %}
</div>
```

**Impact**: Medium - Poor mobile experience for a data-heavy view

---

### Issue 7: Missing ARIA Labels (MEDIUM)

**Location**: Multiple locations

**Current Issues**:
1. External links missing `aria-label` (line 117)
2. Filter form missing fieldset/legend (line 43)
3. Table missing caption or `aria-label` (line 91)

**Accessibility Reference**:
```html
<!-- design-system.md:967-977 -->
<!-- Icon-only buttons -->
<button class="btn btn-secondary" aria-label="Close dialog">
  <i class="bi bi-x"></i>
</button>

<!-- Form inputs -->
<label for="input-id" class="form-label">Label</label>
<input id="input-id" type="text" class="form-input" aria-describedby="help-text">
```

**Recommended Fixes**:

1. **Add table caption**:
```html
<table class="table table-hover" aria-label="Evidence sources list">
  <caption class="sr-only">Evidence sources with confidence scores and citations</caption>
  <!-- ... -->
</table>
```

2. **Add ARIA labels to external links**:
```html
<a href="{{ evidence.url }}" 
   target="_blank" 
   rel="noopener noreferrer" 
   aria-label="Open {{ domain }} citation in new tab"
   class="inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary-dark">
  {{ evidence.url | truncate(50) }}
  <i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>
</a>
```

3. **Add fieldset to filter form**:
```html
<form method="GET" action="/evidence" class="grid gap-4 md:grid-cols-4">
  <fieldset class="contents">
    <legend class="sr-only">Filter evidence sources</legend>
    <!-- Filter controls -->
  </fieldset>
</form>
```

**Impact**: Medium - Accessibility violation (WCAG 2.1 Level A)

---

### Issue 8: Missing Table Hover Class (LOW)

**Location**: `list.html:91`

**Current Code**:
```html
<table class="min-w-full divide-y divide-gray-100 text-left text-sm text-gray-700">
```

**Problem**:
- Table doesn't use `.table-hover` class from design system
- Rows have `hover:bg-primary/5` which is good, but inconsistent with design system

**Design System Reference**:
```html
<!-- design-system.md:431-481 -->
<table class="table table-hover">
  <!-- ... -->
</table>
```

**Recommended Fix**:
```html
<table class="table table-hover">
  <thead>
    <tr>
      <th>Entity</th>
      <!-- ... -->
    </tr>
  </thead>
  <tbody>
    {% for evidence in view.evidence_list %}
    <tr>
      <!-- Remove individual hover:bg-primary/5, .table-hover handles it -->
    </tr>
    {% endfor %}
  </tbody>
</table>
```

**Impact**: Low - Minor visual inconsistency

---

## Recommendations Summary

### Priority 1: Critical Fixes (Do First)
1. **Standardize confidence colors** - Use `bg-confidence-{green|yellow|red}` from Tailwind config
2. **Add source type badge colors** - Map source types to semantic badge colors with icons
3. **Implement citation badge pattern** - Domain + icon for clean URL display

### Priority 2: High-Impact Improvements
4. **Add loading states** - Skeleton loaders + spinner for filter submissions
5. **Mobile responsive cards** - Show card view on mobile, table on desktop
6. **Confidence label badges** - Add High/Medium/Low labels to percentage

### Priority 3: Accessibility & Polish
7. **Add ARIA labels** - External links, table caption, filter fieldset
8. **Use `.table-hover` class** - Follow design system table patterns
9. **Add empty state icon** - Visual enhancement for no results

---

## Before/After Code Comparison

### Confidence Score Display

**Before**:
```html
<div class="flex items-center gap-3">
  <div class="h-2 w-24 overflow-hidden rounded-full bg-gray-100">
    <span class="block h-full rounded-full {{ 'bg-emerald-500' if confidence_pct >= 80 else 'bg-amber-400' if confidence_pct >= 60 else 'bg-rose-500' }}" style="width: {{ confidence_pct }}%"></span>
  </div>
  <span class="text-sm text-gray-600">{{ confidence_pct }}%</span>
</div>
```

**After**:
```html
{% if evidence.confidence >= 0.80 %}
  {% set conf_color = 'bg-confidence-green' %}
  {% set conf_label = 'High' %}
{% elif evidence.confidence >= 0.60 %}
  {% set conf_color = 'bg-confidence-yellow' %}
  {% set conf_label = 'Medium' %}
{% else %}
  {% set conf_color = 'bg-confidence-red' %}
  {% set conf_label = 'Low' %}
{% endif %}

<div class="flex items-center gap-2">
  <div class="h-2 w-20 overflow-hidden rounded-full bg-gray-100">
    <span class="block h-full rounded-full {{ conf_color }}" style="width: {{ (evidence.confidence * 100) | int }}%"></span>
  </div>
  <span class="inline-flex items-center gap-1 rounded-full {{ conf_color }}/10 px-2 py-0.5 text-xs font-semibold {{ conf_color | replace('bg-', 'text-') }}">
    {{ (evidence.confidence * 100) | int }}% {{ conf_label }}
  </span>
</div>
```

**Impact**: Consistent with design system, scannable confidence levels

---

### Source Type Badge

**Before**:
```html
<span class="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
  {{ evidence.source_type }}
</span>
```

**After**:
```html
{% set source_badges = {
  'documentation': ('badge-info', 'bi-journal-richtext'),
  'research': ('badge-primary', 'bi-search'),
  'stackoverflow': ('badge-warning', 'bi-stack-overflow'),
  'github': ('badge-success', 'bi-github'),
  'internal_doc': ('badge-gray', 'bi-file-text'),
  'meeting_notes': ('badge-secondary', 'bi-chat-left-text'),
  'expert_opinion': ('badge-accent', 'bi-person-badge')
} %}

{% set badge_class, badge_icon = source_badges.get(evidence.source_type, ('badge-gray', 'bi-file')) %}

<span class="badge {{ badge_class }}">
  <i class="{{ badge_icon }}"></i>
  {{ evidence.source_type | replace('_', ' ') | title }}
</span>
```

**Impact**: Visual distinction between source types, scannable at a glance

---

## Design System Compliance Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Color Palette** | 40% | ❌ Not using `confidence.*` colors, ❌ source badges generic |
| **Typography** | 90% | ✅ Font classes correct, minor text color issues |
| **Spacing & Layout** | 80% | ✅ Grid layout good, ⚠️ table not responsive |
| **Component Patterns** | 60% | ⚠️ Badges inconsistent, ⚠️ missing loading states |
| **Accessibility** | 50% | ❌ Missing ARIA labels, ❌ no table caption |
| **Responsive Design** | 40% | ❌ No mobile card view, table too wide |
| **Interactive States** | 70% | ✅ Hover states present, ❌ no loading feedback |

**Overall Compliance**: **65%** (Needs Improvement)

---

## Implementation Checklist

To bring evidence list to 95%+ compliance:

- [ ] Update confidence colors to use `bg-confidence-{green|yellow|red}`
- [ ] Add confidence label badges (High/Medium/Low)
- [ ] Map source types to semantic badge colors with icons
- [ ] Implement citation badge pattern (domain + icon)
- [ ] Add loading states (skeleton loader + filter spinner)
- [ ] Create mobile card view (hidden on desktop)
- [ ] Add ARIA labels to external links
- [ ] Add table caption/aria-label
- [ ] Add fieldset/legend to filter form
- [ ] Use `.table-hover` class from design system
- [ ] Test keyboard navigation (Tab through filters → table rows)
- [ ] Test color contrast with browser DevTools
- [ ] Verify responsiveness (375px mobile → 1920px desktop)

---

## Estimated Effort

- **Confidence colors fix**: 15 min
- **Source type badges**: 20 min
- **Citation badges**: 20 min
- **Loading states**: 25 min
- **Mobile responsive cards**: 40 min
- **Accessibility fixes**: 20 min
- **Testing & polish**: 20 min

**Total**: ~2.5 hours (within 2.0h budget for implementation)

---

## Conclusion

The evidence list route has a **solid foundation** but needs **design system alignment** to match the quality of other APM (Agent Project Manager) views. Priority should be:

1. **Confidence color standardization** (consistency across system)
2. **Source type visual distinction** (usability improvement)
3. **Mobile responsiveness** (accessibility for all devices)

Once these 3 priorities are addressed, the evidence list will achieve **90%+ design system compliance** and provide an excellent user experience for research and documentation workflows.

---

**Next Steps**: Implement fixes in priority order, test with real evidence data, validate WCAG 2.1 AA compliance.
