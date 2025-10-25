# Navigation Code Examples & Implementation Guide

**Date**: 2025-10-22
**Related**: navigation-consistency-audit.md
**Purpose**: Production-ready code examples for navigation standardization

---

## Table of Contents

1. [Standard Breadcrumbs Component](#1-standard-breadcrumbs-component)
2. [Navigation Macros](#2-navigation-macros)
3. [Sidebar Navigation](#3-sidebar-navigation)
4. [Tabs Component](#4-tabs-component)
5. [Mobile Navigation](#5-mobile-navigation)
6. [Accessibility Enhancements](#6-accessibility-enhancements)
7. [Implementation Checklist](#7-implementation-checklist)

---

## 1. Standard Breadcrumbs Component

### File: `components/navigation/breadcrumbs.html`

```html
{#
  Standard Breadcrumbs Navigation Component

  USAGE:
    {% include 'components/navigation/breadcrumbs.html' %}

  REQUIRED CONTEXT:
    - breadcrumbs: List[dict] with 'name' and optional 'url'

  EXAMPLE:
    breadcrumbs = [
        {'name': 'Work Items', 'url': '/work-items'},
        {'name': 'WI-123', 'url': None}  # Current page (no URL)
    ]

  ACCESSIBILITY:
    - WCAG 2.1 AA compliant
    - aria-label on nav for screen readers
    - aria-current on last item
    - Keyboard navigable (Tab, Enter)
#}
{% if breadcrumbs and breadcrumbs|length > 0 %}
<nav aria-label="Breadcrumb" class="mb-6">
  <ol class="flex items-center flex-wrap gap-2 text-sm text-gray-500">
    <!-- Home (Always first) -->
    <li>
      <a href="/"
         class="flex items-center gap-1 hover:text-primary transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded"
         title="Dashboard">
        <i class="bi bi-house-door"></i>
        <span class="sr-only">Dashboard</span>
      </a>
    </li>

    <!-- Breadcrumb Items -->
    {% for breadcrumb in breadcrumbs %}
    <li class="flex items-center gap-2">
      <!-- Separator -->
      <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
      </svg>

      <!-- Link or Current Page -->
      {% if breadcrumb.url %}
      <a href="{{ breadcrumb.url }}"
         class="hover:text-primary transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded truncate max-w-xs"
         title="{{ breadcrumb.name }}">
        {{ breadcrumb.name }}
      </a>
      {% else %}
      <span class="text-gray-900 font-medium truncate max-w-xs" aria-current="page">
        {{ breadcrumb.name }}
      </span>
      {% endif %}
    </li>
    {% endfor %}
  </ol>
</nav>
{% endif %}
```

### Usage in Templates

**In Route Handler** (Python):
```python
from flask import render_template

@app.route('/work-items/<int:id>')
def work_item_detail(id):
    work_item = get_work_item(id)

    breadcrumbs = [
        {'name': 'Work Items', 'url': '/work-items'},
        {'name': f'WI-{work_item.id}: {work_item.name[:30]}', 'url': None}
    ]

    return render_template(
        'work-items/detail.html',
        work_item=work_item,
        breadcrumbs=breadcrumbs
    )
```

**In Template** (Jinja2):
```html
{% extends "layouts/modern_base.html" %}

{# Breadcrumbs are automatically rendered by modern_base.html #}
{# No need to include manually - just pass breadcrumbs in context #}

{% block content %}
  <!-- Your page content -->
{% endblock %}
```

### Migration from Old Pattern

**BEFORE** (Legacy Bootstrap breadcrumbs):
```html
{% block breadcrumb %}
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/">Dashboard</a></li>
    <li class="breadcrumb-item"><a href="/work-items">Work Items</a></li>
    <li class="breadcrumb-item active" aria-current="page">WI-123</li>
  </ol>
</nav>
{% endblock %}
```

**AFTER** (New Tailwind breadcrumbs):
```python
# In route handler - pass breadcrumbs as context variable
breadcrumbs = [
    {'name': 'Work Items', 'url': '/work-items'},
    {'name': 'WI-123', 'url': None}
]
```

**Template changes**:
```html
{# DELETE the entire {% block breadcrumb %} block #}
{# Breadcrumbs are automatically rendered by modern_base.html #}
```

---

## 2. Navigation Macros

### File: `macros/navigation.html`

```jinja2
{#
  Navigation Macros for Active State Detection and Rendering

  USAGE:
    {% from 'macros/navigation.html' import nav_link, mobile_nav_link, is_active_path %}
#}

{#
  Check if path is active (for highlighting)

  USAGE:
    {% if is_active_path('/work-items', request.path) %}active{% endif %}
#}
{% macro is_active_path(href, current_path) -%}
  {{ (href == '/' and current_path == '/') or (href != '/' and current_path.startswith(href)) }}
{%- endmacro %}

{#
  Desktop Navigation Link (Pill Style)

  USAGE:
    {{ nav_link('/work-items', 'Work Items', icon='list-task', current_path=request.path) }}
#}
{% macro nav_link(href, label, icon=None, current_path='') -%}
  {% set active = is_active_path(href, current_path) %}
  <a href="{{ href }}"
     class="rounded-full px-3 py-1.5 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
            {{ 'bg-white text-primary shadow-sm' if active else 'text-gray-600 hover:text-primary' }}"
     {{ 'aria-current="page"' if active else '' }}>
    <span class="flex items-center gap-2">
      {% if icon %}
      <i class="bi bi-{{ icon }}" aria-hidden="true"></i>
      {% endif %}
      {{ label }}
    </span>
  </a>
{%- endmacro %}

{#
  Mobile Navigation Link (Block Style)

  USAGE:
    {{ mobile_nav_link('/work-items', 'Work Items', icon='list-task', current_path=request.path) }}
#}
{% macro mobile_nav_link(href, label, icon=None, current_path='') -%}
  {% set active = is_active_path(href, current_path) %}
  <a href="{{ href }}"
     class="flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
            {{ 'bg-primary/10 text-primary' if active else 'text-gray-700 hover:bg-gray-50 hover:text-primary' }}"
     {{ 'aria-current="page"' if active else '' }}>
    <span class="flex items-center gap-2">
      {% if icon %}
      <i class="bi bi-{{ icon }}" aria-hidden="true"></i>
      {% endif %}
      {{ label }}
    </span>
    {% if active %}
    <span class="h-2 w-2 rounded-full bg-primary" aria-hidden="true"></span>
    {% endif %}
  </a>
{%- endmacro %}

{#
  Sidebar Navigation Link

  USAGE:
    {{ sidebar_nav_link('/work-items', 'Work Items', icon='list-task', count=42, current_path=request.path) }}
#}
{% macro sidebar_nav_link(href, label, icon=None, count=None, current_path='') -%}
  {% set active = is_active_path(href, current_path) %}
  <a href="{{ href }}"
     class="flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
            {{ 'bg-primary/10 text-primary' if active else 'text-gray-700 hover:bg-gray-50 hover:text-primary' }}"
     {{ 'aria-current="page"' if active else '' }}>
    <span class="flex items-center gap-2">
      {% if icon %}
      <i class="bi bi-{{ icon }}" aria-hidden="true"></i>
      {% endif %}
      {{ label }}
    </span>
    {% if count is not none %}
    <span class="rounded-full px-2 py-0.5 text-xs font-semibold
                 {{ 'bg-primary/20 text-primary' if active else 'bg-gray-200 text-gray-600' }}">
      {{ count }}
    </span>
    {% endif %}
  </a>
{%- endmacro %}
```

### Usage in Header

**BEFORE** (Duplicated logic):
```html
<a href="/work-items"
   class="rounded-full px-3 py-1.5 text-sm font-medium transition
          {{ 'bg-white text-primary shadow-sm' if current_path.startswith('/work-item') else 'text-gray-600 hover:text-primary' }}">
  Work Items
</a>
```

**AFTER** (Using macro):
```html
{% from 'macros/navigation.html' import nav_link %}

{{ nav_link('/work-items', 'Work Items', icon='list-task', current_path=request.path) }}
{{ nav_link('/tasks', 'Tasks', icon='check2-square', current_path=request.path) }}
{{ nav_link('/sessions', 'Sessions', icon='clock-history', current_path=request.path) }}
```

---

## 3. Sidebar Navigation

### File: `components/navigation/sidebar_section.html`

```html
{#
  Sidebar Section Component

  USAGE:
    {% include 'components/navigation/sidebar_section.html' with context %}

  REQUIRED CONTEXT:
    - section_title: str
    - section_items: List[dict] with 'url', 'label', 'icon' (optional), 'count' (optional)

  EXAMPLE:
    section_title = "Quick Actions"
    section_items = [
        {'url': '/work-items/create', 'label': 'New Work Item', 'icon': 'plus'},
        {'url': '/tasks/create', 'label': 'New Task', 'icon': 'check2-square'},
    ]
#}
{% from 'macros/navigation.html' import sidebar_nav_link %}

<div class="mb-6">
  <!-- Section Title -->
  <h3 class="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
    {{ section_title }}
  </h3>

  <!-- Navigation Items -->
  <nav class="space-y-1" aria-label="{{ section_title }}">
    {% for item in section_items %}
    {{ sidebar_nav_link(
         item.url,
         item.label,
         icon=item.icon if item.icon else None,
         count=item.count if item.count is defined else None,
         current_path=request.path
       ) }}
    {% endfor %}
  </nav>
</div>
```

### Usage Example

**In Sidebar Template** (`components/layout/sidebar_work_items.html`):
```html
<aside class="w-64 border-r border-gray-200 bg-white overflow-y-auto">
  <div class="p-4 space-y-6">
    <!-- Section 1: Filters -->
    {% set filter_items = [
        {'url': '/work-items?status=active', 'label': 'Active', 'icon': 'circle-fill', 'count': 12},
        {'url': '/work-items?status=blocked', 'label': 'Blocked', 'icon': 'exclamation-circle', 'count': 3},
        {'url': '/work-items?status=done', 'label': 'Done', 'icon': 'check-circle', 'count': 42}
    ] %}
    {% include 'components/navigation/sidebar_section.html' with context
       section_title='Status',
       section_items=filter_items %}

    <!-- Section 2: Quick Actions -->
    {% set action_items = [
        {'url': '/work-items/create', 'label': 'New Work Item', 'icon': 'plus'},
        {'url': '/work-items/import', 'label': 'Import', 'icon': 'upload'}
    ] %}
    {% include 'components/navigation/sidebar_section.html' with context
       section_title='Actions',
       section_items=action_items %}
  </div>
</aside>
```

---

## 4. Tabs Component

### File: `components/navigation/tabs.html`

```html
{#
  Tabs Navigation Component (Alpine.js)

  USAGE:
    {% include 'components/navigation/tabs.html' %}
    {# Then define tab content in {% block tab_<id> %} #}

  REQUIRED CONTEXT:
    - tabs: List[dict] with 'id', 'label', 'icon' (optional), 'count' (optional)
    - default_tab: str (ID of default active tab)

  EXAMPLE:
    tabs = [
        {'id': 'overview', 'label': 'Overview', 'icon': 'info-circle'},
        {'id': 'tasks', 'label': 'Tasks', 'icon': 'check2-square', 'count': 12},
        {'id': 'history', 'label': 'History', 'icon': 'clock-history'}
    ]
    default_tab = 'overview'
#}
<div x-data="{ activeTab: '{{ default_tab }}' }" class="mb-6">
  <!-- Tab Headers -->
  <div class="border-b border-gray-200">
    <nav class="-mb-px flex gap-6 overflow-x-auto" aria-label="Tabs" role="tablist">
      {% for tab in tabs %}
      <button
        @click="activeTab = '{{ tab.id }}'"
        :class="activeTab === '{{ tab.id }}' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'"
        :aria-selected="(activeTab === '{{ tab.id }}').toString()"
        class="flex items-center gap-2 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        role="tab"
        type="button">
        {% if tab.icon %}
        <i class="bi bi-{{ tab.icon }}" aria-hidden="true"></i>
        {% endif %}
        <span>{{ tab.label }}</span>
        {% if tab.count is defined %}
        <span class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="activeTab === '{{ tab.id }}' ? 'bg-primary/20 text-primary' : 'bg-gray-200 text-gray-600'">
          {{ tab.count }}
        </span>
        {% endif %}
      </button>
      {% endfor %}
    </nav>
  </div>

  <!-- Tab Panels -->
  <div class="mt-6">
    {% for tab in tabs %}
    <div x-show="activeTab === '{{ tab.id }}'"
         x-transition
         role="tabpanel"
         :aria-hidden="(activeTab !== '{{ tab.id }}').toString()">
      {% block tab_content %}
      <!-- Override this block in parent template -->
      <div id="tab-{{ tab.id }}">
        <p class="text-gray-500">Content for {{ tab.label }}</p>
      </div>
      {% endblock %}
    </div>
    {% endfor %}
  </div>
</div>
```

### Usage in Detail Page

```html
{% extends "layouts/modern_base.html" %}

{% block content %}
<h1>Work Item #{{ work_item.id }}</h1>

<!-- Tabs -->
{% set tabs = [
    {'id': 'overview', 'label': 'Overview', 'icon': 'info-circle'},
    {'id': 'tasks', 'label': 'Tasks', 'icon': 'check2-square', 'count': work_item.tasks_count},
    {'id': 'history', 'label': 'History', 'icon': 'clock-history'}
] %}
{% set default_tab = 'overview' %}

<div x-data="{ activeTab: '{{ default_tab }}' }">
  <!-- Tab Headers -->
  <div class="border-b border-gray-200">
    <nav class="-mb-px flex gap-6" role="tablist">
      {% for tab in tabs %}
      <button @click="activeTab = '{{ tab.id }}'"
              :class="activeTab === '{{ tab.id }}' ? 'border-primary text-primary' : 'border-transparent text-gray-500'"
              class="flex items-center gap-2 border-b-2 py-4 px-1 text-sm font-medium transition">
        <i class="bi bi-{{ tab.icon }}"></i>
        {{ tab.label }}
        {% if tab.count is defined %}
        <span class="rounded-full px-2 py-0.5 text-xs" :class="activeTab === '{{ tab.id }}' ? 'bg-primary/20 text-primary' : 'bg-gray-200'">
          {{ tab.count }}
        </span>
        {% endif %}
      </button>
      {% endfor %}
    </nav>
  </div>

  <!-- Tab Content -->
  <div class="mt-6">
    <!-- Overview Tab -->
    <div x-show="activeTab === 'overview'" x-transition>
      <h2>Overview</h2>
      <p>{{ work_item.description }}</p>
    </div>

    <!-- Tasks Tab -->
    <div x-show="activeTab === 'tasks'" x-transition>
      <h2>Tasks ({{ work_item.tasks_count }})</h2>
      <!-- Tasks list -->
    </div>

    <!-- History Tab -->
    <div x-show="activeTab === 'history'" x-transition>
      <h2>History</h2>
      <!-- Timeline -->
    </div>
  </div>
</div>
{% endblock %}
```

---

## 5. Mobile Navigation

### Enhanced Mobile Menu with Active Indicator

**File**: `components/layout/header.html` (Update existing mobile menu)

```html
<!-- Mobile Menu (Enhanced) -->
<nav
  x-cloak
  x-show="mobileOpen"
  x-transition
  @click.away="mobileOpen = false"
  class="border-t border-gray-200 bg-white md:hidden">

  <div class="space-y-2 px-4 py-4">
    {% from 'macros/navigation.html' import mobile_nav_link %}

    {{ mobile_nav_link('/', 'Home', icon='house-door', current_path=request.path) }}
    {{ mobile_nav_link('/work-items', 'Work Items', icon='list-task', current_path=request.path) }}
    {{ mobile_nav_link('/tasks', 'Tasks', icon='check2-square', current_path=request.path) }}
    {{ mobile_nav_link('/sessions', 'Sessions', icon='clock-history', current_path=request.path) }}
    {{ mobile_nav_link('/ideas', 'Ideas', icon='lightbulb', current_path=request.path) }}
    {{ mobile_nav_link('/contexts', 'Contexts', icon='folder2', current_path=request.path) }}
    {{ mobile_nav_link('/documents', 'Documents', icon='journal-text', current_path=request.path) }}

    <!-- Quick Actions (Bottom of menu) -->
    <div class="border-t border-gray-200 pt-4 mt-4">
      <a href="/work-items/create" class="btn btn-primary w-full">
        <i class="bi bi-plus mr-2"></i>
        New Work Item
      </a>
    </div>
  </div>
</nav>
```

### Swipe-to-Close (Optional Enhancement)

**Install Alpine.js Gesture Plugin**:
```html
<!-- Add to modern_base.html before Alpine.js -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/gesture@3.14.1/dist/cdn.min.js"></script>
```

**Update Mobile Menu**:
```html
<nav
  x-show="mobileOpen"
  x-transition
  @swipe.left="mobileOpen = false"
  @click.away="mobileOpen = false"
  class="...">
  <!-- Menu content -->
</nav>
```

---

## 6. Accessibility Enhancements

### 6.1 Skip-to-Content Link

**Add to `layouts/modern_base.html`** (BEFORE header):

```html
<!DOCTYPE html>
<html lang="en">
<head>...</head>
<body class="h-full min-h-screen bg-gray-50 text-gray-900">

<!-- Skip-to-Content Link (WCAG 2.1 AA) -->
<a href="#main-content"
   class="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded focus:shadow-lg">
  Skip to main content
</a>

<!-- Header -->
{% include 'components/layout/header.html' %}

<!-- Main Content -->
<main id="main-content" class="flex-1 overflow-y-auto" tabindex="-1">
  <!-- ... -->
</main>
```

**Styling** (in `brand-system.css`):
```css
/* Skip-to-content link - only visible on focus */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.focus\:not-sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: 0.5rem 1rem;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

---

### 6.2 ARIA Labels for Icon Buttons

**User Menu Button** (in `header.html`):
```html
<button
  type="button"
  aria-label="Open user menu"
  aria-haspopup="menu"
  :aria-expanded="open.toString()"
  class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
  @click="open = !open">
  <i class="bi bi-person-fill" aria-hidden="true"></i>
</button>
```

**Mobile Menu Button** (in `header.html`):
```html
<button
  type="button"
  aria-label="Open navigation menu"
  aria-haspopup="menu"
  :aria-expanded="mobileOpen.toString()"
  class="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 shadow-sm transition hover:border-primary/40 hover:text-primary md:hidden focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
  @click="mobileOpen = !mobileOpen">
  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
  </svg>
  <span class="sr-only">Menu</span>
</button>
```

**Documents Button** (in `header.html`):
```html
<a
  href="/documents"
  aria-label="View documents"
  class="hidden rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-600 shadow-sm transition hover:border-primary/30 hover:text-primary sm:inline-flex focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
  title="Documents">
  <i class="bi bi-journal-text" aria-hidden="true"></i>
</a>
```

---

### 6.3 Focus Trap for Modals

**Install Alpine.js Focus Plugin**:
```html
<!-- Add to modern_base.html before Alpine.js -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.14.1/dist/cdn.min.js"></script>
```

**Update Modal Component**:
```html
<div x-data="{ open: false }">
  <!-- Trigger -->
  <button @click="open = true" class="btn btn-primary">Open Modal</button>

  <!-- Modal Overlay -->
  <div
    x-show="open"
    x-transition.opacity
    @keydown.escape.window="open = false"
    class="fixed inset-0 bg-gray-900/60 z-50 flex items-center justify-center p-4">

    <!-- Modal Content (with focus trap) -->
    <div
      @click.stop
      x-trap.inert.noscroll="open"
      x-transition
      class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">

      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 id="modal-title" class="text-2xl font-bold text-gray-900">Modal Title</h2>
        <button @click="open = false" aria-label="Close modal" class="text-gray-400 hover:text-gray-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <!-- Content -->
      </div>

      <!-- Modal Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
        <button @click="open = false" class="btn btn-secondary">Cancel</button>
        <button class="btn btn-primary">Confirm</button>
      </div>
    </div>
  </div>
</div>
```

**Explanation of `x-trap.inert.noscroll`**:
- `x-trap`: Traps focus within modal (Tab cycles through modal elements only)
- `.inert`: Makes background content inert (not clickable/focusable)
- `.noscroll`: Prevents background scrolling while modal is open

---

### 6.4 Keyboard Shortcuts

**Global Keyboard Handler** (in `modern_base.html`):
```html
<script>
// Keyboard shortcuts
document.addEventListener('keydown', (event) => {
  // Ignore if user is typing in input/textarea
  if (event.target.matches('input, textarea, select')) {
    return;
  }

  // ⌘K / Ctrl+K - Focus search
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    const searchInput = document.querySelector('input[name="global-search"]') ||
                        document.querySelector('input[type="search"]');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  // N - New work item (only if not in input)
  if (event.key.toLowerCase() === 'n' && !event.ctrlKey && !event.metaKey) {
    event.preventDefault();
    window.location.href = '/work-items/create';
  }

  // E - Export (only if on list page)
  if (event.key.toLowerCase() === 'e' && !event.ctrlKey && !event.metaKey) {
    const exportBtn = document.querySelector('[onclick*="export"]');
    if (exportBtn) {
      event.preventDefault();
      exportBtn.click();
    }
  }

  // ? - Show keyboard shortcuts help
  if (event.key === '?') {
    event.preventDefault();
    showKeyboardShortcuts();
  }
});

function showKeyboardShortcuts() {
  const shortcuts = [
    { key: '⌘K / Ctrl+K', action: 'Focus global search' },
    { key: 'N', action: 'Create new work item' },
    { key: 'E', action: 'Export current list' },
    { key: '?', action: 'Show this help' },
    { key: 'Esc', action: 'Close modals/dropdowns' }
  ];

  const html = `
    <div class="space-y-2">
      <h3 class="text-lg font-semibold mb-4">Keyboard Shortcuts</h3>
      ${shortcuts.map(s => `
        <div class="flex justify-between items-center">
          <kbd class="px-2 py-1 bg-gray-100 rounded text-sm font-mono">${s.key}</kbd>
          <span class="text-gray-600">${s.action}</span>
        </div>
      `).join('')}
    </div>
  `;

  // Show in modal (implementation depends on modal system)
  console.info('Keyboard shortcuts:', shortcuts);
}
</script>
```

---

## 7. Implementation Checklist

### Phase 1: Critical Fixes (HIGH Priority)

- [ ] **Create navigation components** (1 hour)
  - [ ] Create `components/navigation/breadcrumbs.html`
  - [ ] Create `macros/navigation.html`
  - [ ] Test breadcrumbs rendering with sample data

- [ ] **Standardize existing breadcrumbs** (2 hours)
  - [ ] Update `layouts/modern_base.html` to include new breadcrumbs component
  - [ ] Migrate `tasks/detail.html` to use context variable (remove block override)
  - [ ] Migrate `projects/detail.html` to use context variable
  - [ ] Migrate `rules_list.html` to use context variable
  - [ ] Test all migrated pages

- [ ] **Add missing breadcrumbs** (1 hour)
  - [ ] Add breadcrumbs to `work-items/list.html`
  - [ ] Add breadcrumbs to `tasks/list.html`
  - [ ] Add breadcrumbs to `contexts/list.html`
  - [ ] Add breadcrumbs to `ideas/list.html`
  - [ ] Add breadcrumbs to `documents/list.html`

- [ ] **Accessibility fixes** (1 hour)
  - [ ] Add skip-to-content link to `modern_base.html`
  - [ ] Add `aria-label="Breadcrumb"` to breadcrumbs nav
  - [ ] Add ARIA labels to all icon-only buttons in header
  - [ ] Test with screen reader (VoiceOver/NVDA)

**Total Phase 1**: ~5 hours

### Phase 2: Enhancements (MEDIUM Priority)

- [ ] **Refactor header navigation** (1 hour)
  - [ ] Import navigation macros in `header.html`
  - [ ] Replace desktop nav links with `nav_link` macro
  - [ ] Replace mobile nav links with `mobile_nav_link` macro
  - [ ] Test active state highlighting

- [ ] **Add mobile nav enhancements** (0.5 hours)
  - [ ] Add active indicator dots to mobile nav
  - [ ] Add quick action button at bottom of mobile menu
  - [ ] Test on real mobile device

- [ ] **Create sidebar components** (2 hours)
  - [ ] Create `components/navigation/sidebar_section.html`
  - [ ] Update existing sidebar templates to use component
  - [ ] Enable sidebar on work item detail page
  - [ ] Enable sidebar on task detail page

**Total Phase 2**: ~3.5 hours

### Phase 3: Advanced Features (LOW Priority)

- [ ] **Tabs component** (2 hours)
  - [ ] Create `components/navigation/tabs.html`
  - [ ] Implement tabs on work item detail page
  - [ ] Implement tabs on project detail page
  - [ ] Test tab navigation and transitions

- [ ] **Keyboard enhancements** (2 hours)
  - [ ] Install Alpine.js Focus plugin
  - [ ] Add focus trap to modals
  - [ ] Implement global keyboard shortcuts (N, E, ?)
  - [ ] Create keyboard shortcuts help modal

- [ ] **Swipe gestures** (1 hour)
  - [ ] Install Alpine.js Gesture plugin
  - [ ] Add swipe-to-close to mobile menu
  - [ ] Test on touch devices

**Total Phase 3**: ~5 hours

---

### Testing Checklist

**Manual Testing**:
- [ ] Breadcrumbs appear on all list pages
- [ ] Breadcrumbs appear on all detail pages
- [ ] Active page highlighted in desktop nav
- [ ] Active page highlighted in mobile nav
- [ ] Mobile menu opens/closes smoothly
- [ ] Skip-to-content link appears on Tab key press
- [ ] All icon buttons have ARIA labels

**Keyboard Navigation Testing**:
- [ ] Tab key navigates through all interactive elements
- [ ] Enter key activates links/buttons
- [ ] Escape key closes modals/dropdowns
- [ ] ⌘K focuses search
- [ ] Focus visible on all elements

**Screen Reader Testing** (VoiceOver/NVDA):
- [ ] Breadcrumbs announced correctly
- [ ] Navigation landmarks recognized
- [ ] Skip-to-content link works
- [ ] Icon-only buttons announced with labels
- [ ] Modal focus trap works

**Mobile Testing**:
- [ ] Mobile menu accessible on small screens
- [ ] Active page indicator visible
- [ ] Touch targets at least 44x44px
- [ ] Swipe-to-close works (if implemented)

**Browser Testing**:
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + iOS)
- [ ] Firefox
- [ ] Edge

---

## Summary

This guide provides production-ready code for:

1. ✅ **Standard breadcrumbs component** (Tailwind-based, accessible)
2. ✅ **Navigation macros** (DRY active state logic)
3. ✅ **Sidebar navigation** (reusable section component)
4. ✅ **Tabs component** (Alpine.js-based)
5. ✅ **Mobile navigation enhancements** (active indicators, quick actions)
6. ✅ **Accessibility fixes** (skip link, ARIA labels, focus trap)

**Total Implementation Time**: ~13.5 hours (split across 3 phases)

**Next Steps**:
1. Start with Phase 1 (critical fixes) - 5 hours
2. Test thoroughly with keyboard and screen reader
3. Move to Phase 2 (enhancements) - 3.5 hours
4. Phase 3 is optional but recommended - 5 hours

---

**Document Version**: 1.0
**Last Updated**: 2025-10-22
**Related**: navigation-consistency-audit.md
