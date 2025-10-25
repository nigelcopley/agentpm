# Button & Form Quick Reference

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Status**: ✅ Production Ready

---

## Button Reference

### Basic Buttons

```html
<!-- Primary Action -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary Action -->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Success Action -->
<button class="btn btn-success">Save</button>

<!-- Warning Action -->
<button class="btn btn-warning">Pause</button>

<!-- Danger Action -->
<button class="btn btn-error">Delete</button>

<!-- Info Action -->
<button class="btn btn-info">Details</button>
```

### Button Sizes

```html
<!-- Small -->
<button class="btn btn-sm btn-primary">Small</button>

<!-- Default (no size class needed) -->
<button class="btn btn-primary">Default</button>

<!-- Large -->
<button class="btn btn-lg btn-primary">Large</button>
```

### Button Variants

```html
<!-- Outlined -->
<button class="btn btn-outline">Learn More</button>

<!-- Link Style -->
<button class="btn btn-link">Edit</button>

<!-- Close/Dismiss -->
<button class="btn btn-close" aria-label="Close">
  <i class="bi bi-x"></i>
</button>
```

### Button with Icons

```html
<!-- Icon Left -->
<button class="btn btn-primary">
  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
  </svg>
  Create New
</button>

<!-- Icon Right -->
<button class="btn btn-secondary">
  Next
  <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
  </svg>
</button>

<!-- Icon Only (must have aria-label) -->
<button class="btn btn-sm btn-secondary" aria-label="Edit">
  <i class="bi bi-pencil"></i>
</button>
```

### Button States

```html
<!-- Normal -->
<button class="btn btn-primary">Active</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>

<!-- Loading (JavaScript-controlled) -->
<button class="btn btn-primary" data-loading>
  <span class="inline-flex items-center">
    <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
    Loading...
  </span>
</button>
```

### Button Groups

```html
<!-- Horizontal Group -->
<div class="flex items-center gap-2">
  <button class="btn btn-secondary">Cancel</button>
  <button class="btn btn-primary">Save</button>
</div>

<!-- Vertical Stack -->
<div class="flex flex-col gap-2">
  <button class="btn btn-primary w-full">Edit</button>
  <button class="btn btn-secondary w-full">Duplicate</button>
  <button class="btn btn-error w-full">Delete</button>
</div>
```

---

## Form Reference

### Basic Input

```html
<div class="form-group">
  <label for="name" class="form-label">
    Name
    <span class="text-error">*</span>
  </label>
  <input
    type="text"
    id="name"
    name="name"
    class="form-input"
    placeholder="Enter your name"
    required
  >
  <p class="form-text">Your full legal name</p>
</div>
```

### Email Input

```html
<div class="form-group">
  <label for="email" class="form-label">Email Address</label>
  <input
    type="email"
    id="email"
    name="email"
    class="form-input"
    placeholder="you@example.com"
    required
  >
</div>
```

### Number Input

```html
<div class="form-group">
  <label for="age" class="form-label">Age</label>
  <input
    type="number"
    id="age"
    name="age"
    class="form-input"
    min="18"
    max="120"
    placeholder="25"
  >
</div>
```

### Select Dropdown

```html
<div class="form-group">
  <label for="status" class="form-label">Status</label>
  <select id="status" name="status" class="form-select">
    <option value="">-- Select Status --</option>
    <option value="draft">Draft</option>
    <option value="published">Published</option>
    <option value="archived">Archived</option>
  </select>
</div>
```

### Textarea

```html
<div class="form-group">
  <label for="description" class="form-label">Description</label>
  <textarea
    id="description"
    name="description"
    class="form-textarea"
    rows="4"
    placeholder="Provide a detailed description..."
  ></textarea>
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
    class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
  >
  <label for="agree" class="text-sm text-gray-700">
    I agree to the terms and conditions
  </label>
</div>
```

### Radio Buttons

```html
<div class="form-group">
  <label class="form-label">Priority</label>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-high"
        name="priority"
        value="high"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary"
      >
      <label for="priority-high" class="text-sm text-gray-700">High</label>
    </div>
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-medium"
        name="priority"
        value="medium"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary"
      >
      <label for="priority-medium" class="text-sm text-gray-700">Medium</label>
    </div>
    <div class="flex items-center gap-2">
      <input
        type="radio"
        id="priority-low"
        name="priority"
        value="low"
        class="w-4 h-4 text-primary border-gray-300 focus:ring-primary"
      >
      <label for="priority-low" class="text-sm text-gray-700">Low</label>
    </div>
  </div>
</div>
```

### Form with Validation

```html
<div class="form-group">
  <label for="email-validated" class="form-label">Email</label>
  <input
    type="email"
    id="email-validated"
    name="email"
    class="form-input border-error"
    placeholder="you@example.com"
    aria-describedby="email-error"
    aria-invalid="true"
  >
  <p id="email-error" class="form-text text-error">
    <i class="bi bi-exclamation-triangle mr-1"></i>
    Please enter a valid email address.
  </p>
</div>
```

### Form Layouts

#### Single Column (Mobile-First)

```html
<form class="space-y-6">
  <div class="form-group">...</div>
  <div class="form-group">...</div>
  <div class="flex justify-end gap-3">
    <button type="button" class="btn btn-secondary">Cancel</button>
    <button type="submit" class="btn btn-primary">Submit</button>
  </div>
</form>
```

#### Two Column (Tablet+)

```html
<form class="space-y-6">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="form-group">...</div>
    <div class="form-group">...</div>
  </div>
  <div class="flex justify-end gap-3">
    <button type="button" class="btn btn-secondary">Cancel</button>
    <button type="submit" class="btn btn-primary">Submit</button>
  </div>
</form>
```

#### Sidebar Layout (Desktop)

```html
<form class="grid grid-cols-1 lg:grid-cols-3 gap-8">
  <!-- Main Content (2/3 width) -->
  <div class="lg:col-span-2 space-y-6">
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Main Form</h3>
      </div>
      <div class="card-body space-y-4">
        <div class="form-group">...</div>
        <div class="form-group">...</div>
      </div>
    </div>
  </div>

  <!-- Sidebar (1/3 width) -->
  <div class="space-y-6">
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Options</h3>
      </div>
      <div class="card-body space-y-4">
        <div class="form-group">...</div>
      </div>
    </div>

    <!-- Actions -->
    <div class="card">
      <div class="card-body space-y-3">
        <button type="submit" class="btn btn-primary w-full">Submit</button>
        <button type="button" class="btn btn-secondary w-full">Cancel</button>
      </div>
    </div>
  </div>
</form>
```

---

## Validation Message Patterns

### Success

```html
<p class="form-text text-success">
  <i class="bi bi-check-circle mr-1"></i>
  Looks good!
</p>
```

### Error

```html
<p class="form-text text-error">
  <i class="bi bi-exclamation-triangle mr-1"></i>
  This field is required.
</p>
```

### Warning

```html
<p class="form-text text-warning">
  <i class="bi bi-exclamation-circle mr-1"></i>
  This action cannot be undone.
</p>
```

### Info

```html
<p class="form-text text-info">
  <i class="bi bi-info-circle mr-1"></i>
  Maximum 200 characters.
</p>
```

---

## Accessibility Checklist

### Buttons
- ✅ Use semantic `<button>` element
- ✅ Include visible text or `aria-label` for icon-only buttons
- ✅ Don't disable keyboard navigation
- ✅ Ensure color contrast ≥ 4.5:1
- ✅ Focus states are clearly visible

### Forms
- ✅ Every input has an associated `<label>`
- ✅ Use `for` attribute to link label to input
- ✅ Mark required fields with `required` attribute
- ✅ Use `aria-describedby` for help text and errors
- ✅ Set `aria-invalid="true"` for invalid inputs
- ✅ Ensure placeholder text doesn't replace labels
- ✅ Group related inputs with `<fieldset>` and `<legend>`

---

## Common Patterns

### Search Form

```html
<form class="mb-6">
  <div class="relative">
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
      </svg>
    </div>
    <input
      type="search"
      class="form-input pl-10"
      placeholder="Search..."
    >
  </div>
</form>
```

### Filter Form

```html
<div class="card mb-6">
  <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
    <!-- Search -->
    <div class="flex-1 max-w-md">
      <input type="text" class="form-input" placeholder="Search...">
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-4">
      <select class="form-select">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>

      <button class="btn btn-sm btn-secondary">Clear Filters</button>
    </div>
  </div>
</div>
```

### Inline Edit

```html
<div x-data="{ editing: false }">
  <!-- View Mode -->
  <div x-show="!editing" class="flex items-center gap-2">
    <span class="text-lg font-medium">Current Value</span>
    <button @click="editing = true" class="btn btn-sm btn-link">
      <i class="bi bi-pencil"></i>
      Edit
    </button>
  </div>

  <!-- Edit Mode -->
  <form x-show="editing" @submit.prevent="editing = false" class="flex items-center gap-2">
    <input type="text" class="form-input" value="Current Value">
    <button type="submit" class="btn btn-sm btn-success">
      <i class="bi bi-check"></i>
      Save
    </button>
    <button type="button" @click="editing = false" class="btn btn-sm btn-secondary">
      <i class="bi bi-x"></i>
      Cancel
    </button>
  </form>
</div>
```

---

## CSS Classes Quick Reference

### Button Classes

| Class | Description |
|-------|-------------|
| `.btn` | Base button styles (required) |
| `.btn-primary` | Blue primary action |
| `.btn-secondary` | Gray secondary action |
| `.btn-success` | Green success action |
| `.btn-warning` | Amber warning action |
| `.btn-error` | Red danger/delete action |
| `.btn-info` | Cyan informational action |
| `.btn-outline` | Transparent with border |
| `.btn-link` | Link-style button |
| `.btn-close` | Close/dismiss button |
| `.btn-sm` | Small size |
| `.btn-lg` | Large size |

### Form Classes

| Class | Description |
|-------|-------------|
| `.form-group` | Form field container |
| `.form-label` | Input label |
| `.form-input` | Text input |
| `.form-select` | Dropdown select |
| `.form-textarea` | Multi-line textarea |
| `.form-text` | Help text / hint |

### Utility Classes

| Class | Description |
|-------|-------------|
| `.text-error` | Red error text |
| `.text-success` | Green success text |
| `.text-warning` | Amber warning text |
| `.text-info` | Cyan info text |
| `.border-error` | Red error border |
| `.border-success` | Green success border |

---

**Last Updated**: 2025-10-22
**Maintained by**: APM (Agent Project Manager) Team
**Questions**: See [design-system.md](./design-system.md) for full documentation
