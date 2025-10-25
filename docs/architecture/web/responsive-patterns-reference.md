# Responsive Design Patterns - Quick Reference

**Purpose**: Copy-paste patterns for implementing responsive designs in APM (Agent Project Manager)
**Related**: `design-system.md`, `responsive-design-audit-report.md`
**Last Updated**: 2025-10-22

---

## Pattern Index

1. [Mobile Filter Panel](#1-mobile-filter-panel)
2. [Mobile Table Alternative](#2-mobile-table-alternative)
3. [Responsive Metrics Grid](#3-responsive-metrics-grid)
4. [Responsive Card Grid](#4-responsive-card-grid)
5. [Touch-Friendly Buttons](#5-touch-friendly-buttons)
6. [Responsive Search Form](#6-responsive-search-form)
7. [Stacked vs. Inline Actions](#7-stacked-vs-inline-actions)
8. [Responsive Navigation](#8-responsive-navigation)

---

## 1. Mobile Filter Panel

**Use Case**: Routes with 3+ filter dropdowns (work items, tasks, agents)

**Problem**: Multiple inline filters overflow on mobile screens

**Solution**: Collapsible filter panel with Alpine.js

### Implementation

```html
<div x-data="{
  filtersOpen: false,
  activeFilters: 0,
  statusFilter: '',
  typeFilter: '',
  priorityFilter: '',

  updateFilters() {
    this.activeFilters = [this.statusFilter, this.typeFilter, this.priorityFilter]
      .filter(f => f !== '').length;
    this.applyFilters();
  },

  applyFilters() {
    // Your filter logic here (e.g., hide/show rows)
    const rows = document.querySelectorAll('.filterable-row');
    rows.forEach(row => {
      let visible = true;

      if (this.statusFilter && row.dataset.status !== this.statusFilter) {
        visible = false;
      }
      if (this.typeFilter && row.dataset.type !== this.typeFilter) {
        visible = false;
      }
      if (this.priorityFilter && row.dataset.priority !== this.priorityFilter) {
        visible = false;
      }

      row.style.display = visible ? '' : 'none';
    });
  },

  clearFilters() {
    this.statusFilter = '';
    this.typeFilter = '';
    this.priorityFilter = '';
    this.activeFilters = 0;
    this.applyFilters();
  }
}">

  <!-- Mobile Filter Button (visible only on mobile) -->
  <button
    type="button"
    class="btn btn-secondary w-full lg:hidden"
    @click="filtersOpen = !filtersOpen">
    <i class="bi bi-funnel"></i>
    Filters
    <span
      x-show="activeFilters > 0"
      x-transition
      class="badge badge-primary ml-2"
      x-text="activeFilters"></span>
    <i
      class="bi bi-chevron-down ml-auto transition-transform"
      :class="{ 'rotate-180': filtersOpen }"></i>
  </button>

  <!-- Mobile Filter Panel (collapsible) -->
  <div
    x-show="filtersOpen"
    x-transition:enter="transition ease-out duration-200"
    x-transition:enter-start="opacity-0 -translate-y-4"
    x-transition:enter-end="opacity-100 translate-y-0"
    x-transition:leave="transition ease-in duration-150"
    x-transition:leave-start="opacity-100 translate-y-0"
    x-transition:leave-end="opacity-0 -translate-y-4"
    class="mt-4 space-y-3 lg:hidden">

    <!-- Status Filter -->
    <div>
      <label class="form-label">Status</label>
      <select
        class="form-select"
        x-model="statusFilter"
        @change="updateFilters">
        <option value="">All Status</option>
        <option value="draft">Draft</option>
        <option value="ready">Ready</option>
        <option value="active">Active</option>
        <option value="review">Review</option>
        <option value="blocked">Blocked</option>
        <option value="done">Done</option>
      </select>
    </div>

    <!-- Type Filter -->
    <div>
      <label class="form-label">Type</label>
      <select
        class="form-select"
        x-model="typeFilter"
        @change="updateFilters">
        <option value="">All Types</option>
        <option value="feature">Feature</option>
        <option value="enhancement">Enhancement</option>
        <option value="bugfix">Bug Fix</option>
        <option value="research">Research</option>
      </select>
    </div>

    <!-- Priority Filter -->
    <div>
      <label class="form-label">Priority</label>
      <select
        class="form-select"
        x-model="priorityFilter"
        @change="updateFilters">
        <option value="">All Priorities</option>
        <option value="1">Critical (P1)</option>
        <option value="2">High (P2)</option>
        <option value="3">Medium (P3)</option>
        <option value="4">Low (P4)</option>
      </select>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2">
      <button
        type="button"
        class="btn btn-primary flex-1"
        @click="filtersOpen = false">
        <i class="bi bi-check"></i>
        Apply Filters
      </button>
      <button
        type="button"
        class="btn btn-secondary"
        @click="clearFilters">
        <i class="bi bi-x"></i>
        Clear
      </button>
    </div>
  </div>

  <!-- Desktop Inline Filters (hidden on mobile) -->
  <div class="hidden lg:flex items-center gap-4">
    <!-- Status Filter -->
    <div class="flex items-center gap-2">
      <label class="text-sm font-medium text-gray-700">Status:</label>
      <select
        class="form-select"
        x-model="statusFilter"
        @change="updateFilters">
        <option value="">All Status</option>
        <option value="draft">Draft</option>
        <option value="ready">Ready</option>
        <option value="active">Active</option>
        <option value="review">Review</option>
        <option value="blocked">Blocked</option>
        <option value="done">Done</option>
      </select>
    </div>

    <!-- Type Filter -->
    <div class="flex items-center gap-2">
      <label class="text-sm font-medium text-gray-700">Type:</label>
      <select
        class="form-select"
        x-model="typeFilter"
        @change="updateFilters">
        <option value="">All Types</option>
        <option value="feature">Feature</option>
        <option value="enhancement">Enhancement</option>
        <option value="bugfix">Bug Fix</option>
        <option value="research">Research</option>
      </select>
    </div>

    <!-- Priority Filter -->
    <div class="flex items-center gap-2">
      <label class="text-sm font-medium text-gray-700">Priority:</label>
      <select
        class="form-select"
        x-model="priorityFilter"
        @change="updateFilters">
        <option value="">All Priorities</option>
        <option value="1">Critical (P1)</option>
        <option value="2">High (P2)</option>
        <option value="3">Medium (P3)</option>
        <option value="4">Low (P4)</option>
      </select>
    </div>

    <!-- Clear Filters Button -->
    <button
      type="button"
      class="btn btn-sm btn-secondary"
      @click="clearFilters">
      Clear Filters
    </button>
  </div>
</div>
```

### Styling Tips

```css
/* Ensure dropdowns are full-width on mobile */
@media (max-width: 1023px) {
  .form-select {
    width: 100%;
  }
}

/* Smooth transitions for filter panel */
[x-cloak] {
  display: none !important;
}
```

---

## 2. Mobile Table Alternative

**Use Case**: Tables with 5+ columns (agents, contexts, evidence, sessions)

**Problem**: Wide tables cause horizontal scroll on mobile

**Solution**: Card view for mobile, table view for desktop

### Implementation

```html
<!-- Mobile Card View (< md breakpoint) -->
<div class="md:hidden space-y-3">
  {% for item in items %}
  <div class="card hover:shadow-lg transition-shadow">
    <!-- Card Header: Primary info -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex-1">
        <h3 class="font-semibold text-gray-900">
          <a href="{{ item.url }}" class="hover:text-primary">
            {{ item.name }}
          </a>
        </h3>
        <p class="text-sm text-gray-600">{{ item.role or item.type }}</p>
      </div>
      <span class="badge badge-{{ item.status_color }}">
        {{ item.status }}
      </span>
    </div>

    <!-- Card Body: Secondary info in 2-column grid -->
    <div class="grid grid-cols-2 gap-3 text-sm text-gray-600 mb-3">
      <div>
        <span class="font-medium">Tier:</span>
        <span>{{ item.tier }}</span>
      </div>
      <div>
        <span class="font-medium">Last Used:</span>
        <span>{{ item.last_used }}</span>
      </div>
      <div>
        <span class="font-medium">Assigned:</span>
        <span>{{ item.assigned_tasks }}</span>
      </div>
      <div>
        <span class="font-medium">Active:</span>
        <span>{{ item.active_tasks }}</span>
      </div>
    </div>

    <!-- Card Footer: Actions -->
    <div class="flex items-center justify-end gap-2 pt-3 border-t border-gray-100">
      <a href="{{ item.url }}" class="btn btn-sm btn-secondary">
        View
      </a>
      <button class="btn btn-sm btn-secondary" onclick="editItem({{ item.id }})">
        <i class="bi bi-pencil"></i>
      </button>
    </div>
  </div>
  {% endfor %}
</div>

<!-- Desktop Table View (≥ md breakpoint) -->
<div class="hidden md:block overflow-x-auto">
  <table class="min-w-full divide-y divide-gray-100 text-left text-sm text-gray-700">
    <thead class="bg-gray-50 text-xs font-semibold uppercase tracking-wide text-gray-500">
      <tr>
        <th class="px-6 py-3">Name</th>
        <th class="px-4 py-3">Role</th>
        <th class="px-4 py-3">Tier</th>
        <th class="px-4 py-3">Last Used</th>
        <th class="px-4 py-3">Assigned Tasks</th>
        <th class="px-4 py-3">Active Tasks</th>
        <th class="px-4 py-3 text-right">Status</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-100">
      {% for item in items %}
      <tr class="hover:bg-gray-50 transition">
        <td class="px-6 py-3 font-medium text-gray-900">
          <a href="{{ item.url }}" class="hover:text-primary">{{ item.name }}</a>
        </td>
        <td class="px-4 py-3">
          <span class="badge badge-sky">{{ item.role }}</span>
        </td>
        <td class="px-4 py-3">{{ item.tier }}</td>
        <td class="px-4 py-3">{{ item.last_used }}</td>
        <td class="px-4 py-3">{{ item.assigned_tasks }}</td>
        <td class="px-4 py-3">{{ item.active_tasks }}</td>
        <td class="px-4 py-3 text-right">
          <span class="badge badge-{{ item.status_color }}">{{ item.status }}</span>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

### Variation: Expandable Mobile Cards

```html
<div class="md:hidden space-y-3" x-data="{ expandedId: null }">
  {% for item in items %}
  <div class="card">
    <!-- Summary (always visible) -->
    <div
      class="flex items-center justify-between cursor-pointer"
      @click="expandedId = expandedId === {{ item.id }} ? null : {{ item.id }}">
      <div>
        <h3 class="font-semibold text-gray-900">{{ item.name }}</h3>
        <p class="text-sm text-gray-600">{{ item.role }}</p>
      </div>
      <i
        class="bi bi-chevron-down transition-transform"
        :class="{ 'rotate-180': expandedId === {{ item.id }} }"></i>
    </div>

    <!-- Details (expandable) -->
    <div
      x-show="expandedId === {{ item.id }}"
      x-transition
      class="mt-3 pt-3 border-t border-gray-100">
      <div class="grid grid-cols-2 gap-3 text-sm text-gray-600">
        <!-- All details here -->
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

---

## 3. Responsive Metrics Grid

**Use Case**: Dashboard metric cards, statistics

**Pattern**: 1 col mobile → 2 col tablet → 4 col desktop

### Implementation

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
  {% for label, value, icon, color in metrics %}
  <div class="card">
    <div class="flex items-center">
      <!-- Icon (scales with breakpoint) -->
      <div class="flex-shrink-0">
        <div class="w-10 h-10 sm:w-12 sm:h-12 bg-{{ color }} rounded-lg flex items-center justify-center">
          <i class="bi bi-{{ icon }} text-white text-lg sm:text-xl"></i>
        </div>
      </div>

      <!-- Content (responsive spacing) -->
      <div class="ml-3 sm:ml-4">
        <p class="text-xs sm:text-sm font-medium text-gray-500">{{ label }}</p>
        <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ value }}</p>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

### Variation: Vertical Layout on Mobile

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
  <div class="card">
    <!-- Mobile: Vertical stack -->
    <div class="flex flex-col sm:flex-row items-center sm:items-start gap-3">
      <!-- Icon -->
      <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
        <i class="bi bi-check-circle text-white text-xl"></i>
      </div>

      <!-- Content -->
      <div class="text-center sm:text-left">
        <p class="text-sm font-medium text-gray-500">Total Work Items</p>
        <p class="text-2xl font-bold text-gray-900">42</p>
      </div>
    </div>
  </div>
</div>
```

---

## 4. Responsive Card Grid

**Use Case**: Work item cards, task cards, idea cards

**Pattern**: 1 col mobile → 2 col tablet → 3 col desktop → 4 col large

### Implementation

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
  {% for item in items %}
  <div class="card hover:shadow-lg transition-shadow">
    <!-- Card content -->
    <div class="card-header">
      <h3 class="card-title">{{ item.name }}</h3>
      <p class="card-subtitle">{{ item.type }}</p>
    </div>

    <div class="card-body">
      <p class="text-sm text-gray-700">{{ item.description[:100] }}...</p>
    </div>

    <div class="card-footer">
      <a href="{{ item.url }}" class="btn btn-sm btn-secondary">View</a>
    </div>
  </div>
  {% endfor %}
</div>
```

### Tips

- Use `gap-4 md:gap-6` for responsive gaps
- Always include hover effect for cards: `hover:shadow-lg transition-shadow`
- Consider `aspect-ratio` for consistent card heights

---

## 5. Touch-Friendly Buttons

**Use Case**: All interactive elements on mobile

**Requirement**: WCAG 2.1 AA minimum 44×44px

### Implementation

```html
<!-- Standard Button (meets requirement) -->
<button class="btn btn-primary">
  <i class="bi bi-plus mr-2"></i>
  Create
</button>
<!-- Default: px-4 py-2 ≈ 48px height ✓ -->

<!-- Small Button (needs enforcement) -->
<button class="btn btn-sm btn-secondary min-w-[44px] min-h-[44px]">
  <i class="bi bi-pencil"></i>
</button>

<!-- Icon-Only Button (always enforce) -->
<button
  class="flex items-center justify-center w-11 h-11 rounded-lg border border-gray-200 bg-white text-gray-600 hover:text-primary"
  aria-label="Edit">
  <i class="bi bi-pencil"></i>
</button>
<!-- w-11 h-11 = 44px ✓ -->

<!-- Link as Button (ensure touch area) -->
<a href="/edit" class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-4 py-2 rounded-lg bg-primary text-white">
  Edit
</a>
```

### Design System Addition

Add to `brand-system.css`:

```css
/* Ensure small buttons meet touch target requirements */
.btn-sm {
  @apply min-w-[44px] min-h-[44px];
}

/* Icon-only buttons must meet minimum size */
.btn-icon {
  @apply flex items-center justify-center w-11 h-11 rounded-lg;
}
```

---

## 6. Responsive Search Form

**Use Case**: Global search, list filters with search

**Pattern**: Stacked mobile → Horizontal tablet+

### Implementation

```html
<form method="GET" action="/search" class="flex flex-col sm:flex-row gap-3 sm:gap-4">
  <!-- Search Input (full-width mobile, flex-1 desktop) -->
  <div class="flex-1">
    <div class="relative">
      <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-gray-400">
        <i class="bi bi-search"></i>
      </span>
      <input
        type="search"
        name="q"
        placeholder="Search..."
        class="form-input pl-10 w-full"
        autocomplete="off"
      />
    </div>
  </div>

  <!-- Filter Dropdown (full-width mobile, auto desktop) -->
  <select name="entity_type" class="form-select w-full sm:w-auto">
    <option value="">All Types</option>
    <option value="work_item">Work Items</option>
    <option value="task">Tasks</option>
    <option value="idea">Ideas</option>
  </select>

  <!-- Search Button (full-width mobile, auto desktop) -->
  <button type="submit" class="btn btn-primary w-full sm:w-auto">
    <i class="bi bi-search mr-2"></i>
    Search
  </button>
</form>
```

### Variation: With Advanced Filters

```html
<div x-data="{ advancedOpen: false }">
  <form class="flex flex-col sm:flex-row gap-3 sm:gap-4">
    <!-- Search Input -->
    <div class="flex-1">
      <input type="search" class="form-input w-full" placeholder="Search..." />
    </div>

    <!-- Quick Filters -->
    <select class="form-select w-full sm:w-auto">
      <option value="">All Types</option>
    </select>

    <!-- Search + Advanced Toggle -->
    <div class="flex gap-2">
      <button type="submit" class="btn btn-primary flex-1 sm:flex-none">
        <i class="bi bi-search mr-2"></i>
        Search
      </button>
      <button
        type="button"
        class="btn btn-secondary"
        @click="advancedOpen = !advancedOpen">
        <i class="bi bi-sliders"></i>
        <span class="hidden sm:inline ml-2">Advanced</span>
      </button>
    </div>
  </form>

  <!-- Advanced Filters Panel -->
  <div x-show="advancedOpen" x-transition class="mt-4 card">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Advanced filter inputs -->
    </div>
  </div>
</div>
```

---

## 7. Stacked vs. Inline Actions

**Use Case**: Card footers, form buttons, action bars

**Pattern**: Stack on mobile, inline on desktop

### Implementation

```html
<!-- Card Footer Actions -->
<div class="card-footer">
  <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-2 sm:gap-3">
    <!-- Primary Actions (left side) -->
    <div class="flex gap-2">
      <a href="/view" class="btn btn-sm btn-secondary flex-1 sm:flex-none">
        View Details
      </a>
      <button class="btn btn-sm btn-primary flex-1 sm:flex-none">
        Start Work
      </button>
    </div>

    <!-- Secondary Actions (right side) -->
    <div class="flex gap-1 justify-end">
      <button class="btn btn-sm btn-secondary" aria-label="Edit">
        <i class="bi bi-pencil"></i>
      </button>
      <button class="btn btn-sm btn-secondary" aria-label="Duplicate">
        <i class="bi bi-files"></i>
      </button>
      <button class="btn btn-sm btn-error" aria-label="Delete">
        <i class="bi bi-trash"></i>
      </button>
    </div>
  </div>
</div>

<!-- Form Actions -->
<div class="flex flex-col-reverse sm:flex-row justify-end gap-3 mt-6">
  <button type="button" class="btn btn-secondary w-full sm:w-auto">
    Cancel
  </button>
  <button type="submit" class="btn btn-primary w-full sm:w-auto">
    <i class="bi bi-check mr-2"></i>
    Save
  </button>
</div>
<!-- Note: flex-col-reverse on mobile = primary button on top -->
```

### Tips

- Use `flex-1 sm:flex-none` to make buttons full-width on mobile
- Use `flex-col-reverse` for forms (primary button on top on mobile)
- Always group related actions together

---

## 8. Responsive Navigation

**Use Case**: Header navigation, tab navigation

**Pattern**: Mobile menu → Inline tabs

### Implementation (Tabs)

```html
<div x-data="{ activeTab: 'overview' }">
  <!-- Mobile: Dropdown Tabs -->
  <div class="md:hidden mb-4">
    <select
      class="form-select w-full"
      x-model="activeTab"
      @change="$el.blur()">
      <option value="overview">Overview</option>
      <option value="tasks">Tasks</option>
      <option value="history">History</option>
      <option value="comments">Comments</option>
    </select>
  </div>

  <!-- Desktop: Horizontal Tabs -->
  <div class="hidden md:flex border-b border-gray-200 mb-6">
    <button
      type="button"
      @click="activeTab = 'overview'"
      :class="activeTab === 'overview' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      Overview
    </button>
    <button
      type="button"
      @click="activeTab = 'tasks'"
      :class="activeTab === 'tasks' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      Tasks
    </button>
    <button
      type="button"
      @click="activeTab = 'history'"
      :class="activeTab === 'history' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      History
    </button>
    <button
      type="button"
      @click="activeTab = 'comments'"
      :class="activeTab === 'comments' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      Comments
    </button>
  </div>

  <!-- Tab Content (same for both) -->
  <div>
    <div x-show="activeTab === 'overview'" x-transition>
      <!-- Overview content -->
    </div>
    <div x-show="activeTab === 'tasks'" x-transition>
      <!-- Tasks content -->
    </div>
    <div x-show="activeTab === 'history'" x-transition>
      <!-- History content -->
    </div>
    <div x-show="activeTab === 'comments'" x-transition>
      <!-- Comments content -->
    </div>
  </div>
</div>
```

### Variation: Scrollable Tabs

```html
<!-- Desktop: Scrollable horizontal tabs (if many tabs) -->
<div class="hidden md:flex overflow-x-auto border-b border-gray-200 mb-6 scrollbar-hide">
  <div class="flex gap-1 min-w-max">
    <button class="px-4 py-2 border-b-2 border-primary text-primary font-medium whitespace-nowrap">
      Tab 1
    </button>
    <button class="px-4 py-2 border-b-2 border-transparent text-gray-500 hover:text-gray-700 font-medium whitespace-nowrap">
      Tab 2
    </button>
    <!-- More tabs... -->
  </div>
</div>

<style>
/* Hide scrollbar but keep functionality */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
```

---

## General Best Practices

### 1. Mobile-First Approach

Always start with mobile styles, then enhance for larger screens:

```html
<!-- ✓ GOOD: Mobile first -->
<div class="p-4 md:p-6 lg:p-8">

<!-- ✗ BAD: Desktop first (requires overrides) -->
<div class="p-8 md:p-6 sm:p-4">
```

### 2. Consistent Breakpoints

Stick to Tailwind's standard breakpoints:

```javascript
sm: 640px   // Mobile landscape
md: 768px   // Tablet
lg: 1024px  // Desktop
xl: 1280px  // Large desktop
2xl: 1536px // Extra large (rarely needed)
```

### 3. Touch Target Sizes

Always ensure interactive elements are ≥44×44px:

```html
<!-- All buttons -->
<button class="btn min-w-[44px] min-h-[44px]">

<!-- Links with padding -->
<a href="#" class="inline-block py-3 px-4">

<!-- Icon buttons -->
<button class="w-11 h-11">
```

### 4. Text Sizing

Scale text appropriately:

```html
<!-- Headings -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">

<!-- Body text (usually stays same size) -->
<p class="text-base">

<!-- Small text -->
<p class="text-xs sm:text-sm">
```

### 5. Spacing

Use responsive spacing:

```html
<!-- Gaps -->
<div class="gap-4 md:gap-6">

<!-- Padding -->
<div class="p-4 sm:p-6 lg:p-8">

<!-- Margins -->
<div class="mb-4 md:mb-6 lg:mb-8">
```

---

## Testing Checklist

Before considering a responsive implementation complete:

- [ ] Tested at 320px (smallest mobile)
- [ ] Tested at 375px (standard mobile)
- [ ] Tested at 768px (tablet)
- [ ] Tested at 1024px (desktop)
- [ ] Tested at 1920px (large desktop)
- [ ] No horizontal scroll on any breakpoint
- [ ] All touch targets ≥44×44px
- [ ] Text readable without zooming
- [ ] Forms usable on mobile
- [ ] Tables have mobile alternative (if >4 columns)
- [ ] Alpine.js interactions work on mobile

---

**Document Version**: 1.0
**Last Updated**: 2025-10-22
**Maintained By**: AIPM UX Team
