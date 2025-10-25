# APM (Agent Project Manager) Component Snippets

**Version**: 1.0.0
**Last Updated**: 2025-10-21
**Purpose**: Copy-paste ready component patterns for rapid development

---

## Quick Start

This file contains production-ready component snippets using:
- **Tailwind CSS 3.4.14** - Utility classes
- **Alpine.js 3.14.1** - Lightweight interactivity
- **Bootstrap Icons 1.11.1** - Icon system

### Usage

1. Copy the snippet
2. Paste into your template
3. Customize content and classes
4. Test accessibility with keyboard navigation

---

## Table of Contents

1. [Buttons](#buttons)
2. [Forms](#forms)
3. [Cards](#cards)
4. [Badges & Pills](#badges--pills)
5. [Alerts & Notifications](#alerts--notifications)
6. [Modals & Dialogs](#modals--dialogs)
7. [Dropdowns & Menus](#dropdowns--menus)
8. [Tables](#tables)
9. [Tabs & Accordions](#tabs--accordions)
10. [Loading States](#loading-states)
11. [Empty States](#empty-states)
12. [Breadcrumbs](#breadcrumbs)

---

## Buttons

### Primary Button
```html
<button class="btn btn-primary">
  <i class="bi bi-plus mr-2"></i>
  Create New
</button>
```

### Secondary Button
```html
<button class="btn btn-secondary">
  Cancel
</button>
```

### Success Button
```html
<button class="btn btn-success">
  <i class="bi bi-check-circle mr-2"></i>
  Approve
</button>
```

### Danger Button
```html
<button class="btn btn-error">
  <i class="bi bi-trash mr-2"></i>
  Delete
</button>
```

### Button with Loading State (Alpine.js)
```html
<button
  x-data="{ loading: false }"
  @click="loading = true; setTimeout(() => loading = false, 2000)"
  :disabled="loading"
  class="btn btn-primary">
  <span x-show="!loading">Submit</span>
  <span x-show="loading" class="flex items-center">
    <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
    Processing...
  </span>
</button>
```

### Button Group
```html
<div class="inline-flex rounded-lg border border-gray-300">
  <button class="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border-r border-gray-300">
    <i class="bi bi-list"></i>
  </button>
  <button class="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border-r border-gray-300">
    <i class="bi bi-grid"></i>
  </button>
  <button class="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
    <i class="bi bi-calendar"></i>
  </button>
</div>
```

---

## Forms

### Basic Input Field
```html
<div class="space-y-2">
  <label for="name" class="form-label">
    Name
    <span class="text-error">*</span>
  </label>
  <input
    type="text"
    id="name"
    name="name"
    class="form-input"
    placeholder="Enter name..."
    required>
  <p class="form-text">Your full name as it appears on official documents</p>
</div>
```

### Select Dropdown
```html
<div class="space-y-2">
  <label for="status" class="form-label">Status</label>
  <select id="status" name="status" class="form-select">
    <option value="">-- Select Status --</option>
    <option value="draft">Draft</option>
    <option value="in_progress">In Progress</option>
    <option value="completed">Completed</option>
  </select>
</div>
```

### Textarea
```html
<div class="space-y-2">
  <label for="description" class="form-label">Description</label>
  <textarea
    id="description"
    name="description"
    rows="4"
    class="form-textarea"
    placeholder="Provide a detailed description..."></textarea>
  <p class="form-text">Minimum 50 characters</p>
</div>
```

### Checkbox
```html
<div class="flex items-center gap-2">
  <input
    type="checkbox"
    id="agree"
    name="agree"
    class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary">
  <label for="agree" class="text-sm text-gray-700">
    I agree to the terms and conditions
  </label>
</div>
```

### Radio Buttons
```html
<div class="space-y-3">
  <label class="form-label">Priority</label>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-high"
        name="priority"
        value="high"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary">
      <label for="priority-high" class="text-sm text-gray-700">High</label>
    </div>
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-medium"
        name="priority"
        value="medium"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary">
      <label for="priority-medium" class="text-sm text-gray-700">Medium</label>
    </div>
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-low"
        name="priority"
        value="low"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary">
      <label for="priority-low" class="text-sm text-gray-700">Low</label>
    </div>
  </div>
</div>
```

### Toggle Switch (Alpine.js)
```html
<div x-data="{ enabled: false }" class="flex items-center gap-3">
  <label class="text-sm font-medium text-gray-700">Enable Feature</label>
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

### Form with Validation (Alpine.js)
```html
<form x-data="{
  formData: { name: '', email: '' },
  errors: {},
  validate() {
    this.errors = {};
    if (!this.formData.name) this.errors.name = 'Name is required';
    if (!this.formData.email) this.errors.email = 'Email is required';
    else if (!this.formData.email.includes('@')) this.errors.email = 'Invalid email format';
    return Object.keys(this.errors).length === 0;
  },
  submit() {
    if (this.validate()) {
      // Form is valid - submit
      this.$el.submit();
    }
  }
}" @submit.prevent="submit()" class="space-y-6">

  <!-- Name Field -->
  <div class="space-y-2">
    <label class="form-label">Name</label>
    <input
      type="text"
      x-model="formData.name"
      :class="errors.name ? 'form-input border-error' : 'form-input'"
      placeholder="Enter name">
    <p x-show="errors.name" x-text="errors.name" class="form-text text-error"></p>
  </div>

  <!-- Email Field -->
  <div class="space-y-2">
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

## Cards

### Basic Card
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Optional subtitle or metadata</p>
  </div>
  <div class="card-body space-y-4">
    <p class="text-gray-700">Card content goes here...</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">Cancel</button>
    <button class="btn btn-primary">Save</button>
  </div>
</div>
```

### Metric Card (Dashboard)
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

### Card with Image
```html
<div class="card p-0">
  <img
    src="https://via.placeholder.com/400x200"
    alt="Card image"
    class="w-full h-48 object-cover rounded-t-xl">
  <div class="p-6">
    <h3 class="text-xl font-semibold text-gray-900 mb-2">Card Title</h3>
    <p class="text-gray-600 mb-4">Card description text goes here.</p>
    <button class="btn btn-primary w-full">Learn More</button>
  </div>
</div>
```

### Hover Card (Clickable)
```html
<a href="#" class="card hover:shadow-lg transition-shadow group">
  <div class="flex items-center justify-between">
    <div>
      <h3 class="text-lg font-semibold text-gray-900 group-hover:text-primary transition">
        Work Item #123
      </h3>
      <p class="text-sm text-gray-600">Status: In Progress</p>
    </div>
    <i class="bi bi-chevron-right text-gray-400 group-hover:text-primary transition"></i>
  </div>
</a>
```

---

## Badges & Pills

### Status Badges
```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Completed</span>
<span class="badge badge-warning">In Progress</span>
<span class="badge badge-error">Blocked</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-gray">Draft</span>
```

### Badge with Icon
```html
<span class="badge badge-success">
  <i class="bi bi-check-circle"></i>
  Approved
</span>
```

### Confidence Badge (AIPM-Specific)
```html
<!-- High Confidence -->
<span class="inline-flex items-center gap-1 rounded-full bg-confidence-green px-3 py-1 text-xs font-semibold text-white">
  <i class="bi bi-check-circle"></i>
  High (0.95)
</span>

<!-- Medium Confidence -->
<span class="inline-flex items-center gap-1 rounded-full bg-confidence-yellow px-3 py-1 text-xs font-semibold text-white">
  <i class="bi bi-exclamation-triangle"></i>
  Medium (0.72)
</span>

<!-- Low Confidence -->
<span class="inline-flex items-center gap-1 rounded-full bg-confidence-red px-3 py-1 text-xs font-semibold text-white">
  <i class="bi bi-x-circle"></i>
  Low (0.45)
</span>
```

### Phase Badge (AIPM-Specific)
```html
<span class="inline-flex items-center gap-1 rounded-full bg-phase-d1 px-3 py-1 text-xs font-semibold text-white">
  D1 Discovery
</span>
<span class="inline-flex items-center gap-1 rounded-full bg-phase-p1 px-3 py-1 text-xs font-semibold text-white">
  P1 Planning
</span>
<span class="inline-flex items-center gap-1 rounded-full bg-phase-i1 px-3 py-1 text-xs font-semibold text-white">
  I1 Implementation
</span>
```

---

## Alerts & Notifications

### Success Alert
```html
<div class="alert alert-success">
  <div class="flex items-center">
    <i class="bi bi-check-circle mr-2"></i>
    <span>Operation completed successfully!</span>
  </div>
</div>
```

### Error Alert
```html
<div class="alert alert-error">
  <div class="flex items-center">
    <i class="bi bi-exclamation-triangle mr-2"></i>
    <span>An error occurred. Please try again.</span>
  </div>
</div>
```

### Warning Alert
```html
<div class="alert alert-warning">
  <div class="flex items-center">
    <i class="bi bi-exclamation-circle mr-2"></i>
    <span>Warning: This action cannot be undone.</span>
  </div>
</div>
```

### Alert with Dismiss Button
```html
<div x-data="{ show: true }" x-show="show" x-transition class="alert alert-info">
  <div class="flex items-center justify-between w-full">
    <div class="flex items-center">
      <i class="bi bi-info-circle mr-2"></i>
      <span>This is an informational message.</span>
    </div>
    <button @click="show = false" class="ml-4 text-current opacity-70 hover:opacity-100">
      <i class="bi bi-x text-xl"></i>
    </button>
  </div>
</div>
```

### Toast Notification (JavaScript)
```html
<!-- Add to base template -->
<div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2"></div>

<!-- JavaScript function (already in modern_base.html) -->
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
  setTimeout(() => toast.classList.remove('translate-x-full'), 100);

  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add('translate-x-full');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

// Usage
showToast('Work item created!', 'success');
</script>
```

---

## Modals & Dialogs

### Basic Modal (Alpine.js)
```html
<div x-data="{ open: false }">
  <!-- Trigger Button -->
  <button @click="open = true" class="btn btn-primary">
    <i class="bi bi-plus mr-2"></i>
    Create New
  </button>

  <!-- Modal Overlay -->
  <div
    x-show="open"
    x-transition.opacity
    class="fixed inset-0 bg-gray-900/60 z-50 flex items-center justify-center p-4"
    @click="open = false">

    <!-- Modal Content -->
    <div
      @click.stop
      x-transition
      class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[600px] overflow-y-auto">

      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold text-gray-900">Modal Title</h2>
        <button @click="open = false" class="text-gray-400 hover:text-gray-600 transition">
          <i class="bi bi-x text-2xl"></i>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6 space-y-4">
        <p class="text-gray-700">Modal content goes here...</p>
        <!-- Form fields, etc. -->
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

### Confirmation Dialog
```html
<div x-data="{ open: false }">
  <button @click="open = true" class="btn btn-error">
    <i class="bi bi-trash mr-2"></i>
    Delete
  </button>

  <div
    x-show="open"
    x-transition.opacity
    class="fixed inset-0 bg-gray-900/60 z-50 flex items-center justify-center p-4"
    @click="open = false">

    <div @click.stop class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
      <div class="flex items-start gap-4 mb-4">
        <div class="flex-shrink-0 w-12 h-12 bg-error/10 rounded-full flex items-center justify-center">
          <i class="bi bi-exclamation-triangle text-error text-2xl"></i>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-1">Confirm Deletion</h3>
          <p class="text-sm text-gray-600">This action cannot be undone. Are you sure?</p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3">
        <button @click="open = false" class="btn btn-secondary">Cancel</button>
        <button @click="open = false" class="btn btn-error">Delete</button>
      </div>
    </div>
  </div>
</div>
```

---

## Dropdowns & Menus

### Dropdown Menu (Alpine.js)
```html
<div x-data="{ open: false }" class="relative">
  <!-- Trigger -->
  <button
    @click="open = !open"
    @click.away="open = false"
    class="btn btn-secondary">
    <span>Actions</span>
    <i class="bi bi-chevron-down ml-2 transition" :class="{ 'rotate-180': open }"></i>
  </button>

  <!-- Dropdown -->
  <div
    x-show="open"
    x-transition
    class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition">
      <i class="bi bi-pencil mr-2"></i>
      Edit
    </a>
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition">
      <i class="bi bi-copy mr-2"></i>
      Duplicate
    </a>
    <div class="border-t border-gray-200 my-1"></div>
    <a href="#" class="block px-4 py-2 text-sm text-error hover:bg-gray-50 transition">
      <i class="bi bi-trash mr-2"></i>
      Delete
    </a>
  </div>
</div>
```

### Context Menu (Right-Click)
```html
<div x-data="{ open: false, x: 0, y: 0 }">
  <!-- Target Element -->
  <div
    @contextmenu.prevent="
      x = $event.pageX;
      y = $event.pageY;
      open = true;
    "
    @click.away="open = false"
    class="p-4 bg-gray-100 rounded-lg cursor-pointer">
    Right-click me for context menu
  </div>

  <!-- Context Menu -->
  <div
    x-show="open"
    x-transition
    :style="`position: fixed; left: ${x}px; top: ${y}px;`"
    class="w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Copy</a>
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Paste</a>
    <a href="#" class="block px-4 py-2 text-sm text-error hover:bg-gray-50">Delete</a>
  </div>
</div>
```

---

## Tables

### Basic Table
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
      <tr>
        <td class="font-medium text-gray-900">Work Item #1</td>
        <td><span class="badge badge-success">Completed</span></td>
        <td><span class="text-sm text-gray-600">High</span></td>
        <td>
          <button class="btn btn-sm btn-secondary">View</button>
        </td>
      </tr>
      <tr>
        <td class="font-medium text-gray-900">Work Item #2</td>
        <td><span class="badge badge-warning">In Progress</span></td>
        <td><span class="text-sm text-gray-600">Medium</span></td>
        <td>
          <button class="btn btn-sm btn-secondary">View</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table with Row Selection (Alpine.js)
```html
<div x-data="{ selected: [] }">
  <table class="table">
    <thead>
      <tr>
        <th class="w-12">
          <input
            type="checkbox"
            @change="selected = $event.target.checked ? [1, 2, 3] : []"
            class="w-4 h-4">
        </th>
        <th>Name</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr :class="selected.includes(1) ? 'bg-primary/10' : ''">
        <td>
          <input
            type="checkbox"
            :checked="selected.includes(1)"
            @change="selected = $event.target.checked ? [...selected, 1] : selected.filter(id => id !== 1)"
            class="w-4 h-4">
        </td>
        <td>Work Item #1</td>
        <td><span class="badge badge-success">Completed</span></td>
      </tr>
      <!-- More rows... -->
    </tbody>
  </table>

  <div x-show="selected.length > 0" class="mt-4">
    <p class="text-sm text-gray-600">
      <span x-text="selected.length"></span> item(s) selected
    </p>
  </div>
</div>
```

---

## Tabs & Accordions

### Tabs (Alpine.js)
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
      <p class="text-gray-700">Overview content...</p>
    </div>
    <div x-show="activeTab === 'tasks'" x-transition>
      <p class="text-gray-700">Tasks content...</p>
    </div>
    <div x-show="activeTab === 'history'" x-transition>
      <p class="text-gray-700">History content...</p>
    </div>
  </div>
</div>
```

### Accordion (Alpine.js)
```html
<div x-data="{ openItem: null }">
  <!-- Accordion Item 1 -->
  <div class="border-b border-gray-200">
    <button
      @click="openItem = openItem === 1 ? null : 1"
      class="w-full flex items-center justify-between py-4 text-left hover:text-primary transition">
      <span class="font-medium text-gray-900">What is AIPM?</span>
      <i class="bi bi-chevron-down transition-transform" :class="{ 'rotate-180': openItem === 1 }"></i>
    </button>
    <div x-show="openItem === 1" x-collapse class="pb-4">
      <p class="text-gray-600">AIPM is an AI-powered project management system...</p>
    </div>
  </div>

  <!-- Accordion Item 2 -->
  <div class="border-b border-gray-200">
    <button
      @click="openItem = openItem === 2 ? null : 2"
      class="w-full flex items-center justify-between py-4 text-left hover:text-primary transition">
      <span class="font-medium text-gray-900">How do I get started?</span>
      <i class="bi bi-chevron-down transition-transform" :class="{ 'rotate-180': openItem === 2 }"></i>
    </button>
    <div x-show="openItem === 2" x-collapse class="pb-4">
      <p class="text-gray-600">Getting started is easy. Simply...</p>
    </div>
  </div>
</div>
```

---

## Loading States

### Inline Spinner
```html
<div class="flex items-center gap-2 text-gray-600">
  <i class="bi bi-arrow-repeat animate-spin"></i>
  <span>Loading...</span>
</div>
```

### Full Page Loading Overlay
```html
<!-- Add to base template -->
<div id="loading-overlay" class="fixed inset-0 bg-gray-900/60 z-50 hidden">
  <div class="flex items-center justify-center h-full">
    <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-2xl">
      <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
      <span class="text-gray-700 font-medium">Loading...</span>
    </div>
  </div>
</div>

<script>
function showLoading() {
  document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loading-overlay').classList.add('hidden');
}
</script>
```

### Skeleton Loader
```html
<div class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-5/6"></div>
</div>
```

---

## Empty States

### Basic Empty State
```html
<div class="text-center py-12">
  <i class="bi bi-inbox text-gray-400 text-6xl mb-4"></i>
  <h3 class="text-lg font-medium text-gray-900 mb-2">No work items yet</h3>
  <p class="text-gray-600 mb-4">Create your first work item to get started.</p>
  <button class="btn btn-primary">
    <i class="bi bi-plus mr-2"></i>
    Create Work Item
  </button>
</div>
```

### Empty State with Illustration
```html
<div class="text-center py-16 px-4">
  <svg class="w-48 h-48 mx-auto text-gray-300 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
  </svg>
  <h3 class="text-2xl font-bold text-gray-900 mb-2">Nothing to see here</h3>
  <p class="text-gray-600 max-w-md mx-auto mb-6">
    You haven't created any tasks yet. Start by creating your first task.
  </p>
  <button class="btn btn-primary btn-lg">
    <i class="bi bi-plus mr-2"></i>
    Create First Task
  </button>
</div>
```

---

## Breadcrumbs

### Basic Breadcrumbs
```html
<nav class="mb-6">
  <ol class="flex items-center space-x-2 text-sm text-gray-500">
    <li><a href="/" class="hover:text-primary">Dashboard</a></li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <a href="/work-items" class="hover:text-primary">Work Items</a>
    </li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <span class="text-gray-900">WI-123</span>
    </li>
  </ol>
</nav>
```

---

## Progress Bars

### Basic Progress
```html
<div class="space-y-2">
  <div class="flex items-center justify-between text-sm">
    <span class="text-gray-700">Completion</span>
    <span class="font-medium text-gray-900">65%</span>
  </div>
  <div class="progress">
    <div class="progress-bar" style="width: 65%"></div>
  </div>
</div>
```

### Colored Progress Bars
```html
<!-- Success (Green) -->
<div class="progress">
  <div class="progress-bar bg-success" style="width: 85%"></div>
</div>

<!-- Warning (Yellow) -->
<div class="progress">
  <div class="progress-bar bg-warning" style="width: 50%"></div>
</div>

<!-- Error (Red) -->
<div class="progress">
  <div class="progress-bar bg-error" style="width: 25%"></div>
</div>
```

---

## Copy-Paste Checklist

Before using a snippet:
- [ ] Replace placeholder content with real data
- [ ] Customize colors if needed (check Tailwind config)
- [ ] Add `aria-label` to icon-only buttons
- [ ] Test keyboard navigation (Tab, Enter, Escape)
- [ ] Verify color contrast (use browser DevTools)
- [ ] Check mobile responsiveness (resize browser)

---

**Last Updated**: 2025-10-21
**Maintained by**: APM (Agent Project Manager) Team
