# APM (Agent Project Manager) Design System

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Tech Stack**: Tailwind CSS 3.4.14 + Alpine.js 3.14.1 + HTMX (planned)

---

## Overview

This design system defines the visual language, component patterns, and interaction guidelines for the APM (Agent Project Manager) web frontend. Built on **Tailwind CSS** with **Alpine.js** for lightweight interactivity, it ensures consistency, accessibility, and maintainability across all templates.

### Core Principles

1. **Utility-First**: Leverage Tailwind's utility classes for rapid, consistent styling
2. **Component-Based**: Reusable patterns defined in Tailwind config and documented here
3. **Accessible**: WCAG 2.1 AA compliance for all interactive elements
4. **Responsive**: Mobile-first design with breakpoint-aware components
5. **Performance**: Minimal custom CSS, maximize Tailwind's purge benefits

---

## Color Palette

### Brand Colors (Extended in Tailwind Config)

```javascript
// tailwind.config.js - colors.primary
primary: {
  50:  '#eef2ff',  // Lightest - backgrounds
  100: '#e0e7ff',
  200: '#c7d2fe',
  300: '#a5b4fc',
  400: '#818cf8',
  500: '#6366f1',  // Base brand color (default)
  600: '#4f46e5',  // Hover states
  700: '#4338ca',
  800: '#3730a3',
  900: '#312e81',  // Darkest - text on light
}

secondary: {
  500: '#8b5cf6',  // Purple accent
  600: '#7c3aed',
}

accent: {
  500: '#ec4899',  // Pink accent
}
```

### Status Colors

```javascript
success: {
  50:  '#ecfdf5',  // Background
  100: '#d1fae5',  // Light background
  500: '#10b981',  // Base (badges, buttons)
  600: '#059669',  // Hover
  700: '#047857',  // Dark text
}

warning: {
  50:  '#fffbeb',
  100: '#fef3c7',
  500: '#f59e0b',  // Base
  600: '#d97706',
  700: '#b45309',
}

danger/error: {
  50:  '#fef2f2',
  100: '#fee2e2',
  500: '#ef4444',  // Base
  600: '#dc2626',
  700: '#b91c1c',
}

info: {
  50:  '#eff6ff',
  100: '#dbeafe',
  500: '#3b82f6',  // Base
  600: '#2563eb',
  700: '#1d4ed8',
}
```

### Neutrals (Tailwind Gray Scale)

```javascript
gray: {
  50:  '#f9fafb',  // Page background
  100: '#f3f4f6',  // Card borders, hover states
  200: '#e5e7eb',  // Dividers
  300: '#d1d5db',  // Input borders
  400: '#9ca3af',  // Placeholder text
  500: '#6b7280',  // Secondary text
  600: '#4b5563',  // Body text (muted)
  700: '#374151',  // Dark text
  800: '#1f2937',  // Headings
  900: '#111827',  // Primary headings
}
```

### Semantic Color Usage

| Color       | Use Case                            | Tailwind Class                |
|-------------|-------------------------------------|-------------------------------|
| Primary     | CTAs, links, focus rings            | `bg-primary`, `text-primary`  |
| Success     | Completed tasks, positive feedback  | `bg-success`, `text-success`  |
| Warning     | In-progress, cautions               | `bg-warning`, `text-warning`  |
| Danger      | Errors, blocked tasks, deletions    | `bg-error`, `text-error`      |
| Info        | Informational badges, tooltips      | `bg-info`, `text-info`        |
| Gray-50     | Page background                     | `bg-gray-50`                  |
| Gray-100    | Card backgrounds, table rows        | `bg-gray-100`                 |
| White       | Cards, modals, dropdowns            | `bg-white`                    |

---

## Typography

### Font Families (Defined in Tailwind Config)

```javascript
fontFamily: {
  sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
  mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
}
```

### Type Scale (Tailwind Utility Classes)

```html
<!-- Headings -->
<h1 class="text-3xl font-bold text-gray-900">Page Title (2.25rem)</h1>
<h2 class="text-2xl font-semibold text-gray-900">Section Heading (1.875rem)</h2>
<h3 class="text-xl font-semibold text-gray-800">Subsection (1.5rem)</h3>
<h4 class="text-lg font-medium text-gray-800">Card Title (1.25rem)</h4>
<h5 class="text-base font-medium text-gray-700">Small Heading (1.125rem)</h5>

<!-- Body Text -->
<p class="text-base text-gray-700">Body text (1rem / 16px)</p>
<p class="text-sm text-gray-600">Secondary text (0.875rem / 14px)</p>
<p class="text-xs text-gray-500">Caption, metadata (0.75rem / 12px)</p>

<!-- Code -->
<code class="font-mono text-sm text-danger bg-gray-100 px-1 py-0.5 rounded">inline code</code>
```

### Font Weights

- **300 (light)**: Reserved for large display text
- **400 (normal)**: Body text, paragraphs
- **500 (medium)**: Labels, secondary headings
- **600 (semibold)**: Primary headings, buttons
- **700 (bold)**: Page titles, emphasis

---

## Spacing & Layout

### Spacing Scale (Tailwind Default)

Use consistent spacing via Tailwind's default scale:

| Size | Value  | Use Case                           |
|------|--------|------------------------------------|
| 1    | 0.25rem| Tight spacing (icons, badges)      |
| 2    | 0.5rem | Small gaps (inline elements)       |
| 3    | 0.75rem| Default gap between elements       |
| 4    | 1rem   | Card padding, section spacing      |
| 6    | 1.5rem | Large padding, section margins     |
| 8    | 2rem   | Page padding, major sections       |
| 12   | 3rem   | Hero sections, large spacing       |

### Grid & Layout Patterns

```html
<!-- Responsive Grid (1 col mobile, 2 col tablet, 4 col desktop) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
  <div>Card 4</div>
</div>

<!-- Container -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <!-- Content -->
</div>

<!-- Flexbox Centering -->
<div class="flex items-center justify-center h-screen">
  <div>Centered Content</div>
</div>
```

---

## Component Patterns

### 1. Buttons

```html
<!-- Primary Button -->
<button class="btn btn-primary">
  <svg class="w-4 h-4 mr-2">...</svg>
  Primary Action
</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">
  Secondary Action
</button>

<!-- Success Button -->
<button class="btn btn-success">
  <i class="bi bi-check-circle mr-2"></i>
  Approve
</button>

<!-- Danger Button -->
<button class="btn btn-error">
  <i class="bi bi-trash mr-2"></i>
  Delete
</button>

<!-- Button Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- Disabled State -->
<button class="btn btn-primary" disabled>
  Disabled
</button>
```

**Tailwind Classes Defined**:
```css
/* In brand-system.css or Tailwind config */
.btn {
  @apply inline-flex items-center justify-center gap-2 rounded-md border border-transparent px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60;
}

.btn-primary {
  @apply bg-primary text-white hover:bg-primary-dark;
}

.btn-secondary {
  @apply border border-gray-300 bg-white text-gray-700 hover:bg-gray-50;
}

.btn-sm {
  @apply px-3 py-1.5 text-xs;
}

.btn-lg {
  @apply px-6 py-3 text-base;
}
```

### 2. Cards

```html
<!-- Basic Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Subtitle or metadata</p>
  </div>
  <div class="card-body space-y-4">
    <!-- Card content -->
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>

<!-- Metric Card (Dashboard) -->
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

<!-- Hover Effect Card -->
<div class="card hover:shadow-lg transition-shadow cursor-pointer">
  <!-- Content -->
</div>
```

**Tailwind Classes Defined**:
```css
.card {
  @apply mb-6 rounded-xl border border-gray-100 bg-white p-6 shadow-sm;
}

.card-header {
  @apply mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-4;
}

.card-title {
  @apply text-xl font-semibold text-gray-900;
}

.card-subtitle {
  @apply mt-1 text-sm text-gray-500;
}

.card-footer {
  @apply mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 pt-4;
}
```

### 3. Badges

```html
<!-- Status Badges -->
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Completed</span>
<span class="badge badge-warning">In Progress</span>
<span class="badge badge-error">Blocked</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-gray">Draft</span>

<!-- Badge with Icon -->
<span class="badge badge-success">
  <i class="bi bi-check-circle"></i>
  Approved
</span>

<!-- Badge Sizes (Custom) -->
<span class="inline-flex items-center gap-1 rounded-full bg-primary px-2 py-0.5 text-xs font-semibold text-white">
  Small Badge
</span>
```

**Tailwind Classes Defined**:
```css
.badge {
  @apply inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide;
}

.badge-primary {
  @apply bg-primary text-white;
}

.badge-success {
  @apply bg-success text-white;
}

.badge-warning {
  @apply bg-warning text-white;
}

.badge-error {
  @apply bg-error text-white;
}

.badge-gray {
  @apply bg-gray-100 text-gray-700;
}
```

### 4. Forms

```html
<!-- Form Group -->
<div class="form-group space-y-2">
  <label for="input-id" class="form-label">
    Label Text
    <span class="text-error">*</span>
  </label>
  <input
    type="text"
    id="input-id"
    name="field_name"
    class="form-input"
    placeholder="Enter value..."
    required>
  <p class="form-text">Helpful hint or validation message</p>
</div>

<!-- Select -->
<select class="form-select">
  <option>Option 1</option>
  <option>Option 2</option>
</select>

<!-- Textarea -->
<textarea class="form-textarea" rows="4" placeholder="Description..."></textarea>

<!-- Checkbox -->
<div class="flex items-center gap-2">
  <input type="checkbox" id="check" class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary">
  <label for="check" class="text-sm text-gray-700">Checkbox label</label>
</div>

<!-- Error State -->
<input type="text" class="form-input border-error focus:ring-error" aria-invalid="true">
<p class="form-text text-error">Error message here</p>
```

**Tailwind Classes Defined**:
```css
.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-input, .form-select, .form-textarea {
  @apply block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 placeholder:text-gray-400;
}

.form-text {
  @apply text-xs text-gray-500;
}
```

### 5. Tables

```html
<div class="table-responsive">
  <table class="table table-hover">
    <thead>
      <tr>
        <th>Name</th>
        <th>Status</th>
        <th>Priority</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr class="hover:bg-gray-50 cursor-pointer">
        <td class="font-medium text-gray-900">Work Item #1</td>
        <td>
          <span class="badge badge-success">Completed</span>
        </td>
        <td>
          <span class="text-sm text-gray-600">High</span>
        </td>
        <td>
          <button class="btn btn-sm btn-secondary">View</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Tailwind Classes Defined**:
```css
.table {
  @apply min-w-full divide-y divide-gray-200 text-left text-sm;
}

.table thead {
  @apply bg-gray-50 text-xs font-semibold uppercase tracking-wide text-gray-500;
}

.table th, .table td {
  @apply px-4 py-3;
}

.table tbody tr {
  @apply border-b border-gray-100;
}

.table-hover tbody tr:hover {
  @apply bg-gray-50 transition;
}
```

### 6. Alerts

```html
<!-- Success Alert -->
<div class="alert alert-success">
  <div class="flex items-center">
    <i class="bi bi-check-circle mr-2"></i>
    <span>Operation completed successfully!</span>
  </div>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
  <div class="flex items-center">
    <i class="bi bi-exclamation-triangle mr-2"></i>
    <span>An error occurred. Please try again.</span>
  </div>
</div>

<!-- Warning Alert -->
<div class="alert alert-warning">
  <div class="flex items-center">
    <i class="bi bi-exclamation-circle mr-2"></i>
    <span>Warning: This action cannot be undone.</span>
  </div>
</div>
```

**Tailwind Classes Defined**:
```css
.alert {
  @apply flex items-center justify-between gap-2 rounded-xl border bg-white p-3 shadow-sm;
}

.alert-success {
  @apply border-emerald-200 bg-emerald-50 text-emerald-700;
}

.alert-error {
  @apply border-rose-200 bg-rose-50 text-rose-700;
}

.alert-warning {
  @apply border-amber-200 bg-amber-50 text-amber-700;
}

.alert-info {
  @apply border-sky-200 bg-sky-50 text-sky-700;
}
```

### 7. Toast Notifications

```html
<!-- Toast Container (in base layout) -->
<div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2"></div>

<!-- JavaScript to show toast -->
<script>
function showToast(message, type = 'info', duration = 5000) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');

  const typeClasses = {
    'success': 'alert-success',
    'error': 'alert-error',
    'warning': 'alert-warning',
    'info': 'alert-info'
  };

  toast.className = `alert ${typeClasses[type]} transform transition-all duration-300 translate-x-full`;
  toast.innerHTML = `
    <div class="flex items-center justify-between">
      <span>${message}</span>
      <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-current opacity-70 hover:opacity-100">
        <i class="bi bi-x text-xl"></i>
      </button>
    </div>
  `;

  container.appendChild(toast);

  // Animate in
  setTimeout(() => toast.classList.remove('translate-x-full'), 100);

  // Auto remove
  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add('translate-x-full');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

// Usage
showToast('Work item created successfully!', 'success');
showToast('Failed to save changes', 'error');
</script>
```

### 8. Progress Bars

```html
<!-- Basic Progress -->
<div class="progress">
  <div class="progress-bar" style="width: 65%"></div>
</div>

<!-- With Label -->
<div class="flex items-center gap-3">
  <div class="progress flex-1">
    <div class="progress-bar bg-success" style="width: 85%"></div>
  </div>
  <span class="text-sm font-medium text-gray-600">85%</span>
</div>

<!-- Color Variants -->
<div class="progress">
  <div class="progress-bar bg-success" style="width: 90%"></div>
</div>
<div class="progress">
  <div class="progress-bar bg-warning" style="width: 50%"></div>
</div>
<div class="progress">
  <div class="progress-bar bg-error" style="width: 25%"></div>
</div>
```

**Tailwind Classes Defined**:
```css
.progress {
  @apply h-2 w-full overflow-hidden rounded-full bg-gray-200;
}

.progress-bar {
  @apply h-full bg-primary transition-all duration-300;
}
```

---

## Alpine.js Component Patterns

### 1. Dropdown Menu

```html
<div x-data="{ open: false }" class="relative">
  <!-- Trigger -->
  <button
    @click="open = !open"
    @click.away="open = false"
    class="btn btn-secondary">
    <span>Actions</span>
    <i class="bi bi-chevron-down ml-2" :class="{ 'rotate-180': open }"></i>
  </button>

  <!-- Dropdown -->
  <div
    x-show="open"
    x-transition
    class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Edit</a>
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Duplicate</a>
    <a href="#" class="block px-4 py-2 text-sm text-error hover:bg-gray-50">Delete</a>
  </div>
</div>
```

### 2. Modal Dialog

```html
<div x-data="{ open: false }">
  <!-- Trigger -->
  <button @click="open = true" class="btn btn-primary">
    <i class="bi bi-plus mr-2"></i>
    Create New
  </button>

  <!-- Modal Overlay -->
  <div
    x-show="open"
    x-transition.opacity
    class="fixed inset-0 bg-gray-900/60 z-50 flex items-center justify-center p-4">

    <!-- Modal Content -->
    <div
      @click.away="open = false"
      x-transition
      class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[600px] overflow-y-auto">

      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold text-gray-900">Modal Title</h2>
        <button @click="open = false" class="text-gray-400 hover:text-gray-600">
          <i class="bi bi-x text-2xl"></i>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <p class="text-gray-700">Modal content goes here...</p>
      </div>

      <!-- Modal Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
        <button @click="open = false" class="btn btn-secondary">Cancel</button>
        <button class="btn btn-primary">Save</button>
      </div>
    </div>
  </div>
</div>
```

### 3. Tabs

```html
<div x-data="{ activeTab: 'overview' }">
  <!-- Tab Headers -->
  <div class="flex gap-4 border-b border-gray-200 mb-6">
    <button
      @click="activeTab = 'overview'"
      :class="activeTab === 'overview' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      Overview
    </button>
    <button
      @click="activeTab = 'tasks'"
      :class="activeTab === 'tasks' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      Tasks
    </button>
    <button
      @click="activeTab = 'history'"
      :class="activeTab === 'history' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
      class="px-4 py-2 border-b-2 font-medium transition">
      History
    </button>
  </div>

  <!-- Tab Content -->
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
  </div>
</div>
```

### 4. Accordion

```html
<div x-data="{ openItem: null }">
  <!-- Accordion Item 1 -->
  <div class="border-b border-gray-200">
    <button
      @click="openItem = openItem === 1 ? null : 1"
      class="w-full flex items-center justify-between py-4 text-left hover:text-primary transition">
      <span class="font-medium">Accordion Item 1</span>
      <i class="bi bi-chevron-down transition-transform" :class="{ 'rotate-180': openItem === 1 }"></i>
    </button>
    <div x-show="openItem === 1" x-collapse class="pb-4">
      <p class="text-gray-600">Content for item 1...</p>
    </div>
  </div>

  <!-- Accordion Item 2 -->
  <div class="border-b border-gray-200">
    <button
      @click="openItem = openItem === 2 ? null : 2"
      class="w-full flex items-center justify-between py-4 text-left hover:text-primary transition">
      <span class="font-medium">Accordion Item 2</span>
      <i class="bi bi-chevron-down transition-transform" :class="{ 'rotate-180': openItem === 2 }"></i>
    </button>
    <div x-show="openItem === 2" x-collapse class="pb-4">
      <p class="text-gray-600">Content for item 2...</p>
    </div>
  </div>
</div>
```

### 5. Toggle Switch

```html
<div x-data="{ enabled: false }" class="flex items-center gap-3">
  <label class="text-sm font-medium text-gray-700">Enable Feature</label>

  <!-- Toggle Button -->
  <button
    @click="enabled = !enabled"
    :class="enabled ? 'bg-success' : 'bg-gray-300'"
    class="relative inline-flex h-6 w-12 items-center rounded-full transition">
    <span
      :class="enabled ? 'translate-x-6' : 'translate-x-1'"
      class="inline-block h-4 w-4 transform rounded-full bg-white transition">
    </span>
  </button>

  <span class="text-sm text-gray-600" x-text="enabled ? 'Enabled' : 'Disabled'"></span>
</div>
```

### 6. Form Validation (Client-Side)

```html
<form x-data="{
  formData: { name: '', email: '' },
  errors: {},
  validate() {
    this.errors = {};
    if (!this.formData.name) this.errors.name = 'Name is required';
    if (!this.formData.email) this.errors.email = 'Email is required';
    else if (!this.formData.email.includes('@')) this.errors.email = 'Invalid email';
    return Object.keys(this.errors).length === 0;
  }
}" @submit.prevent="if (validate()) $el.submit()">

  <!-- Name Field -->
  <div class="form-group space-y-2">
    <label class="form-label">Name</label>
    <input
      type="text"
      x-model="formData.name"
      :class="errors.name ? 'form-input border-error' : 'form-input'"
      placeholder="Enter name">
    <p x-show="errors.name" x-text="errors.name" class="form-text text-error"></p>
  </div>

  <!-- Email Field -->
  <div class="form-group space-y-2">
    <label class="form-label">Email</label>
    <input
      type="email"
      x-model="formData.email"
      :class="errors.email ? 'form-input border-error' : 'form-input'"
      placeholder="Enter email">
    <p x-show="errors.email" x-text="errors.email" class="form-text text-error"></p>
  </div>

  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

---

## HTMX Integration Patterns (Planned)

HTMX is planned for dynamic server interactions. Here are the recommended patterns:

### 1. Dynamic Form Submission

```html
<form
  hx-post="/api/work-items"
  hx-trigger="submit"
  hx-target="#result"
  hx-indicator="#spinner">

  <input type="text" name="name" class="form-input" placeholder="Work Item Name">

  <button type="submit" class="btn btn-primary">
    <span id="spinner" class="htmx-indicator">
      <i class="bi bi-arrow-repeat animate-spin"></i>
    </span>
    Create
  </button>
</form>

<div id="result"></div>
```

### 2. Load-on-Scroll (Infinite Scroll)

```html
<div id="work-items-list">
  <!-- Initial items -->
</div>

<div
  hx-get="/api/work-items?page=2"
  hx-trigger="revealed"
  hx-swap="afterend"
  class="text-center py-4">
  <i class="bi bi-arrow-repeat animate-spin"></i>
  Loading more...
</div>
```

### 3. Live Search

```html
<input
  type="search"
  name="q"
  hx-get="/api/search"
  hx-trigger="keyup changed delay:500ms"
  hx-target="#search-results"
  hx-indicator="#search-spinner"
  class="form-input"
  placeholder="Search...">

<div id="search-spinner" class="htmx-indicator">
  <i class="bi bi-arrow-repeat animate-spin"></i>
</div>

<div id="search-results"></div>
```

### 4. Toggle Actions (Enable/Disable)

```html
<button
  hx-post="/api/work-items/{{ item.id }}/toggle"
  hx-trigger="click"
  hx-swap="none"
  hx-on::after-request="showToast('Status updated', 'success')"
  class="btn btn-sm btn-secondary">
  {{ 'Disable' if item.enabled else 'Enable' }}
</button>
```

---

## Responsive Design

### Breakpoints (Tailwind Default)

| Breakpoint | Min Width | Max Width | Use Case         |
|------------|-----------|-----------|------------------|
| `sm:`      | 640px     | -         | Mobile landscape |
| `md:`      | 768px     | -         | Tablet           |
| `lg:`      | 1024px    | -         | Desktop          |
| `xl:`      | 1280px    | -         | Large desktop    |
| `2xl:`     | 1536px    | -         | Extra large      |

### Mobile-First Approach

```html
<!-- Stack on mobile, 2 columns on tablet, 4 columns on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
  <div>Card 4</div>
</div>

<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<div class="block lg:hidden">Mobile only</div>

<!-- Responsive text sizes -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">Responsive Heading</h1>
```

---

## Accessibility (WCAG 2.1 AA)

### Focus States

All interactive elements must have visible focus states:

```css
/* Tailwind automatically adds focus-visible styles */
.btn:focus-visible {
  @apply outline-none ring-2 ring-primary ring-offset-2;
}
```

### Color Contrast

- **Text on White**: Minimum 4.5:1 contrast
  - Gray-700+ for body text (6.5:1)
  - Gray-900 for headings (13.5:1)
- **Buttons**: Use defined semantic colors (all meet WCAG AA)

### ARIA Labels

```html
<!-- Icon-only buttons -->
<button class="btn btn-secondary" aria-label="Close dialog">
  <i class="bi bi-x"></i>
</button>

<!-- Form inputs -->
<label for="input-id" class="form-label">Label</label>
<input id="input-id" type="text" class="form-input" aria-describedby="help-text">
<p id="help-text" class="form-text">Help text</p>

<!-- Loading states -->
<div role="status" aria-live="polite">
  <span class="sr-only">Loading...</span>
  <i class="bi bi-arrow-repeat animate-spin"></i>
</div>
```

### Keyboard Navigation

- All interactive elements reachable via Tab
- Enter/Space to activate buttons
- Escape to close modals/dropdowns
- Arrow keys for dropdowns/tabs

---

## Performance Best Practices

### 1. Tailwind Purge

Ensure `tailwind.config.js` includes all template paths:

```javascript
module.exports = {
  content: [
    "./agentpm/web/templates/**/*.{html,js}",
    "./agentpm/web/static/js/**/*.js",
  ],
  // ...
}
```

### 2. Minimize Custom CSS

Prefer Tailwind utilities over custom CSS files. Only use `brand-system.css` for:
- Complex animations
- Global resets
- Component base classes

### 3. Alpine.js Best Practices

- Use `x-cloak` to hide elements until Alpine initializes
- Prefer `@click.away` over manual document listeners
- Use `x-transition` for smooth animations

### 4. Image Optimization

```html
<!-- Lazy loading -->
<img src="..." alt="..." loading="lazy" class="w-full h-auto">

<!-- Responsive images -->
<img
  srcset="image-480w.jpg 480w, image-800w.jpg 800w"
  sizes="(max-width: 768px) 100vw, 50vw"
  src="image-800w.jpg"
  alt="..."
  class="w-full h-auto">
```

---

## Icon System

### Bootstrap Icons (Primary)

```html
<!-- Usage -->
<i class="bi bi-check-circle text-success"></i>
<i class="bi bi-x-circle text-error"></i>
<i class="bi bi-exclamation-triangle text-warning"></i>
<i class="bi bi-info-circle text-info"></i>

<!-- Sizes -->
<i class="bi bi-check text-sm"></i>   <!-- 14px -->
<i class="bi bi-check text-base"></i> <!-- 16px -->
<i class="bi bi-check text-lg"></i>   <!-- 18px -->
<i class="bi bi-check text-xl"></i>   <!-- 20px -->
<i class="bi bi-check text-2xl"></i>  <!-- 24px -->
```

**Common Icons**:
- `bi-check-circle`: Success, completed
- `bi-x-circle`: Error, failed
- `bi-exclamation-triangle`: Warning
- `bi-info-circle`: Info
- `bi-plus`: Create, add
- `bi-trash`: Delete
- `bi-pencil`: Edit
- `bi-arrow-repeat`: Loading, refresh
- `bi-chevron-down`: Dropdown indicator

---

## Animation & Transitions

### Tailwind Transitions

```html
<!-- Basic transition -->
<button class="transition hover:bg-primary">Hover me</button>

<!-- All properties -->
<div class="transition-all duration-300 hover:scale-105">Scale on hover</div>

<!-- Specific properties -->
<div class="transition-shadow hover:shadow-lg">Shadow on hover</div>

<!-- Custom durations -->
<div class="transition duration-150">Fast (150ms)</div>
<div class="transition duration-300">Default (300ms)</div>
<div class="transition duration-500">Slow (500ms)</div>
```

### Alpine.js Transitions

```html
<!-- Fade -->
<div x-show="open" x-transition>
  Content fades in/out
</div>

<!-- Slide down -->
<div x-show="open" x-transition:enter="transition ease-out duration-300"
     x-transition:enter-start="opacity-0 transform -translate-y-4"
     x-transition:enter-end="opacity-100 transform translate-y-0">
  Slides down
</div>

<!-- Scale -->
<div x-show="open" x-transition:enter="transition ease-out duration-200"
     x-transition:enter-start="opacity-0 scale-95"
     x-transition:enter-end="opacity-100 scale-100">
  Scales up
</div>
```

### Loading Spinners

```html
<!-- Inline spinner -->
<i class="bi bi-arrow-repeat animate-spin"></i>

<!-- Full overlay -->
<div class="fixed inset-0 bg-gray-900/60 flex items-center justify-center">
  <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
    <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
    <span class="text-gray-700">Loading...</span>
  </div>
</div>
```

---

## Reference: Existing Patterns (WI-23 Dashboard)

Based on analysis of current templates, these patterns are already in use:

1. **Card-based layouts**: `.card`, `.card-header`, `.card-body`, `.card-footer`
2. **Status badges**: `.badge-success`, `.badge-warning`, `.badge-error`
3. **Metric cards**: Icon + label + value pattern
4. **Alpine.js dropdowns**: `x-data`, `x-show`, `@click.away`
5. **Toast notifications**: `showToast()` global function
6. **Loading overlays**: `#loading-overlay` with `showLoading()`/`hideLoading()`

### Migration Notes

- Current CSS uses custom properties (`--color-primary`, etc.) - maintain for compatibility
- Existing Bootstrap Icons integration - keep and expand
- Alpine.js 3.14.1 already loaded - ready for new components
- Toast system functional - document and standardize

---

## Quick Reference: Common Patterns

### Layout
```html
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Page content -->
</div>
```

### Card Grid
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div class="card">...</div>
</div>
```

### Form
```html
<form class="space-y-6">
  <div class="space-y-2">
    <label class="form-label">Label</label>
    <input type="text" class="form-input">
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Alert
```html
<div class="alert alert-success">
  <i class="bi bi-check-circle mr-2"></i>
  <span>Success message</span>
</div>
```

### Modal (Alpine.js)
```html
<div x-data="{ open: false }">
  <button @click="open = true" class="btn btn-primary">Open</button>
  <div x-show="open" class="fixed inset-0 z-50 bg-gray-900/60">
    <div @click.away="open = false" class="bg-white rounded-xl p-6 max-w-2xl mx-auto mt-20">
      <!-- Modal content -->
    </div>
  </div>
</div>
```

---

## Changelog

**v1.0.0** (2025-10-21):
- Initial design system documentation
- Defined color palette with Tailwind integration
- Documented 8 core component patterns
- Added Alpine.js interaction patterns
- Defined HTMX integration approach (planned)
- Accessibility guidelines (WCAG 2.1 AA)
- Responsive design patterns

---

**Maintained by**: APM (Agent Project Manager) Team
**Questions**: Refer to Tailwind CSS docs (https://tailwindcss.com/docs)
**Alpine.js**: https://alpinejs.dev/
