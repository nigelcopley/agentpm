# Loading States Quick Reference

**Work Item**: WI-141
**Date**: 2025-10-22

---

## Quick Usage Guide

### 1. Import Skeleton Loaders

```jinja
{% from "components/skeleton_loaders.html" import
    card_skeleton,
    work_item_card_skeleton,
    task_row_skeleton,
    list_skeleton,
    grid_skeleton,
    loading_button,
    spinner
%}
```

---

## Common Patterns

### Pattern 1: Page with Skeleton Loading

```jinja
<div x-data="{ loading: true }" x-init="setTimeout(() => loading = false, 500)">
  <!-- Skeleton State -->
  <div x-show="loading">
    {{ list_skeleton(items=5) }}
  </div>

  <!-- Content State -->
  <div x-show="!loading" x-transition>
    {% for item in items %}
      {{ item_card(item) }}
    {% endfor %}
  </div>
</div>
```

### Pattern 2: Button Loading State

```html
<button x-data="{ loading: false }"
        @click="loading = true; await action(); loading = false"
        :disabled="loading"
        class="btn btn-primary">
  <span x-show="!loading">Submit</span>
  <span x-show="loading" class="flex items-center space-x-2">
    <span class="spinner spinner-sm"></span>
    <span>Submitting...</span>
  </span>
</button>
```

### Pattern 3: Form with Loading Overlay

```html
<form x-data="{ loading: false }"
      @submit.prevent="loading = true; await submitForm(); loading = false"
      class="relative">

  <!-- Loading Overlay -->
  <div x-show="loading" class="loading-overlay">
    <span class="spinner spinner-md"></span>
    <span>Processing...</span>
  </div>

  <!-- Form Fields -->
  <input type="text" name="name" class="form-input">
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Pattern 4: HTMX Request (Automatic)

```html
<!-- Global loading overlay appears automatically -->
<button hx-post="/api/action" hx-swap="outerHTML">
  Submit
</button>
```

---

## Available Skeleton Components

| Component | Usage | Best For |
|-----------|-------|----------|
| `card_skeleton()` | Generic card | Standard cards |
| `metric_card_skeleton()` | Metric cards | Dashboard metrics |
| `work_item_card_skeleton()` | Work item cards | Work item grids |
| `task_row_skeleton()` | Task rows | Task lists |
| `list_skeleton(items=5)` | List view | List pages |
| `grid_skeleton(cols=3, rows=2)` | Grid layout | Card grids |
| `table_skeleton(rows=5)` | Tables | Data tables |
| `detail_page_skeleton()` | Full pages | Detail pages |

---

## Spinner Sizes

```html
<span class="spinner spinner-sm"></span>  <!-- 16px -->
<span class="spinner spinner-md"></span>  <!-- 24px -->
<span class="spinner spinner-lg"></span>  <!-- 32px -->
<span class="spinner spinner-xl"></span>  <!-- 48px -->
```

---

## JavaScript Utilities

### Manual Loading State

```javascript
// Button loading
LoadingStates.disableButton(button, 'Processing...');
// ... do work
LoadingStates.enableButton(button);

// Element skeleton
LoadingStates.showSkeleton(element, 'card'); // or 'list', 'table'

// Element spinner
LoadingStates.showSpinner(element);
```

### Alpine.js Store

```javascript
// Global loading
Alpine.store('loading').setGlobal(true);
Alpine.store('loading').setGlobal(false);

// Form loading
Alpine.store('loading').setForm('myForm', true);
const isLoading = Alpine.store('loading').isFormLoading('myForm');
```

---

## CSS Classes

| Class | Purpose |
|-------|---------|
| `.skeleton` | Base skeleton loader |
| `.spinner` | Rotating spinner |
| `.loading-overlay` | Full overlay with backdrop |
| `.btn.loading` | Button loading state |
| `.form-loading` | Form with overlay |
| `.is-loading` | Disable interactions |

---

## Routes with Loading States

| Route | Global Overlay | Skeletons Available |
|-------|----------------|---------------------|
| `/` | ✅ | N/A (server-rendered) |
| `/work-items` | ✅ | Grid, Card |
| `/work-items/:id` | ✅ | Detail, Card |
| `/tasks` | ✅ | List, Row |
| `/tasks/:id` | ✅ | Detail, Card |

---

## Testing

Access test page: `/test-loading-states` (if route added)

Or test manually:
```javascript
// Global overlay
Alpine.store('loading').setGlobal(true);
setTimeout(() => Alpine.store('loading').setGlobal(false), 2000);

// Button test
const btn = document.querySelector('#myButton');
LoadingStates.disableButton(btn, 'Loading...');
setTimeout(() => LoadingStates.enableButton(btn), 2000);
```

---

## Troubleshooting

### Overlay doesn't disappear
```javascript
// Manual reset
document.body.dispatchEvent(new Event('htmx:after-request'));
```

### Skeleton not animating
Check CSS import:
```html
<link rel="stylesheet" href=".../loading-states.css">
```

### Button stays disabled
Ensure `finally` block:
```javascript
try { ... } finally { loading = false; }
```

---

**Last Updated**: 2025-10-22
**Status**: Production Ready ✅
