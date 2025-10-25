# Task #792: Project Settings - Quick Fix Guide

**Priority**: High (Blocking Design System Compliance)
**Estimated Total Effort**: 2-4 hours
**Files to Update**: 4 templates + CSS definitions

---

## 🎯 Critical Fixes (Must Do)

### 1. Replace Bootstrap 5 with Tailwind CSS (2 hours)

**Problem**: All templates use Bootstrap 5 classes instead of Tailwind CSS design system.

**Files**:
- `agentpm/web/templates/project_settings.html`
- `agentpm/web/templates/partials/project_name_field.html`
- `agentpm/web/templates/partials/project_description_field.html`
- `agentpm/web/templates/partials/project_tech_stack_field.html`

**Conversion Map**:
```
Bootstrap 5 → Tailwind CSS (Design System)
================================
card shadow-sm → card
card-header bg-gradient → card-header
card-body → card-body space-y-4
mb-4 → space-y-4 (or mb-4 if standalone)
form-label fw-bold → form-label
form-control → form-input
form-text text-muted → form-text
btn btn-sm btn-success → btn btn-primary btn-sm
btn btn-sm btn-secondary → btn btn-secondary btn-sm
badge badge-success → badge badge-success (same, but needs Tailwind def)
d-flex align-items-center → flex items-center
me-2 → mr-2 (Tailwind spacing)
```

**Example Fix** (project_name_field.html):

```html
<!-- BEFORE -->
<input type="text"
       name="name"
       value="{{ project.name }}"
       class="form-control {% if error %}is-invalid{% endif %}"
       required
       maxlength="200"
       autofocus>
{% if error %}
  <div class="invalid-feedback d-block">{{ error }}</div>
{% endif %}
<div class="mt-2">
  <button type="submit" class="btn btn-sm btn-success">
    <i class="bi bi-check"></i> Save
  </button>
  <button type="button" class="btn btn-sm btn-secondary">
    <i class="bi bi-x"></i> Cancel
  </button>
</div>

<!-- AFTER -->
<input type="text"
       name="name"
       value="{{ project.name }}"
       class="form-input {% if error %}border-error{% endif %}"
       required
       maxlength="200"
       autofocus>
{% if error %}
  <p class="form-text text-error">{{ error }}</p>
{% endif %}
<div class="flex items-center gap-3 mt-4">
  <button type="submit" class="btn btn-primary btn-sm">
    <i class="bi bi-check mr-2"></i>Save
  </button>
  <button type="button" class="btn btn-secondary btn-sm">
    <i class="bi bi-x mr-2"></i>Cancel
  </button>
</div>
```

---

### 2. Add Loading States to Save Buttons (30 minutes)

**Problem**: No visual feedback during HTMX save operations.

**Pattern** (Alpine.js + HTMX):

```html
<button
  x-data="{ loading: false }"
  @htmx:before-request="loading = true"
  @htmx:after-request="loading = false"
  :disabled="loading"
  type="submit"
  class="btn btn-primary btn-sm">
  <span x-show="!loading">
    <i class="bi bi-check mr-2"></i>Save
  </span>
  <span x-show="loading" class="flex items-center">
    <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
    Saving...
  </span>
</button>
```

**Apply to**:
- Project name save button
- Description save button
- Tech stack save button

---

## 🔧 Recommended Enhancements (Should Do)

### 3. Client-Side Validation (1 hour)

**Problem**: Only server-side validation; no immediate feedback.

**Pattern** (Alpine.js form wrapper):

```html
<!-- Name Field with Real-Time Validation -->
<form x-data="{
  formData: { name: '{{ project.name }}' },
  errors: {},
  validate() {
    this.errors = {};
    if (!this.formData.name) {
      this.errors.name = 'Name is required';
    } else if (this.formData.name.length > 200) {
      this.errors.name = 'Maximum 200 characters';
    }
    return Object.keys(this.errors).length === 0;
  }
}"
  @submit.prevent="if (validate()) $el.submit()"
  hx-post="/project/{{ project.id }}/update-name"
  hx-target="#project-name-container"
  hx-swap="innerHTML">

  <input
    type="text"
    name="name"
    x-model="formData.name"
    @input="validate()"
    :class="errors.name ? 'form-input border-error' : 'form-input'"
    required
    maxlength="200"
    autofocus>

  <p x-show="errors.name"
     x-text="errors.name"
     x-transition
     class="form-text text-error"></p>

  <!-- Save button with loading state... -->
</form>
```

**Validation Rules**:
- **Name**: Required, 1-200 chars
- **Description**: Optional, max 1000 chars
- **Tech Stack**: Optional, max 500 chars

---

### 4. Accessibility Focus Rings (15 minutes)

**Problem**: Edit buttons lack visible focus states.

**Fix** (add to all edit buttons):

```html
<button class="btn btn-sm btn-link p-0 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        hx-get="/project/{{ project.id }}/settings/name?edit=true"
        hx-target="#project-name-container"
        hx-swap="innerHTML"
        title="Edit project name"
        aria-label="Edit project name">
  <i class="bi bi-pencil text-primary"></i>
</button>
```

**Changes**:
- Add `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`
- Add `aria-label` for screen readers
- Ensure keyboard navigation works (Tab to button, Enter to activate)

---

## 📋 Full File Updates

### File 1: `project_settings.html`

**Key Changes**:
1. Replace Bootstrap grid classes with Tailwind
2. Update card components
3. Fix breadcrumb pattern
4. Update badge classes

**Example Section** (Basic Information):

```html
<!-- Basic Information Section -->
<div class="space-y-6">
  <h5 class="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">
    Basic Information
  </h5>

  <!-- Project Name -->
  <div class="space-y-2">
    <label class="form-label">
      Project Name
      <span class="text-error">*</span>
    </label>
    <div id="project-name-container">
      {% include 'partials/project_name_field.html' with context %}
    </div>
    <p class="form-text">The display name for your project (1-200 characters)</p>
  </div>

  <!-- Description -->
  <div class="space-y-2">
    <label class="form-label">Description</label>
    <div id="project-description-container">
      {% include 'partials/project_description_field.html' with context %}
    </div>
    <p class="form-text">Brief description of the project's purpose (max 1000 characters)</p>
  </div>
</div>
```

---

### File 2: `project_name_field.html`

**Complete Updated Version**:

```html
{% if edit_mode %}
  <!-- Edit Mode: Input + Save/Cancel with Loading State -->
  <form x-data="{
    formData: { name: '{{ project.name }}' },
    errors: {},
    loading: false,
    validate() {
      this.errors = {};
      if (!this.formData.name) {
        this.errors.name = 'Name is required';
      } else if (this.formData.name.length > 200) {
        this.errors.name = 'Maximum 200 characters';
      }
      return Object.keys(this.errors).length === 0;
    }
  }"
    @submit.prevent="if (validate()) $el.submit()"
    @htmx:before-request="loading = true"
    @htmx:after-request="loading = false"
    hx-post="/project/{{ project.id }}/update-name"
    hx-target="#project-name-container"
    hx-swap="innerHTML">

    <input
      type="text"
      name="name"
      x-model="formData.name"
      @input="validate()"
      :class="errors.name ? 'form-input border-error' : 'form-input'"
      required
      maxlength="200"
      autofocus>

    <p x-show="errors.name"
       x-text="errors.name"
       x-transition
       class="form-text text-error"></p>

    {% if error %}
      <p class="form-text text-error">{{ error }}</p>
    {% endif %}

    <div class="flex items-center gap-3 mt-4">
      <button
        type="submit"
        :disabled="loading"
        class="btn btn-primary btn-sm">
        <span x-show="!loading">
          <i class="bi bi-check mr-2"></i>Save
        </span>
        <span x-show="loading" class="flex items-center">
          <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
          Saving...
        </span>
      </button>

      <button
        type="button"
        :disabled="loading"
        hx-get="/project/{{ project.id }}/settings/name"
        hx-target="#project-name-container"
        hx-swap="innerHTML"
        class="btn btn-secondary btn-sm">
        <i class="bi bi-x mr-2"></i>Cancel
      </button>
    </div>
  </form>

{% else %}
  <!-- Display Mode: Value + Edit Button -->
  <div class="flex items-center gap-2">
    <span id="project-name-display" class="text-base text-gray-900">
      {{ project.name }}
    </span>
    <button
      class="btn btn-sm btn-link p-0 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
      hx-get="/project/{{ project.id }}/settings/name?edit=true"
      hx-target="#project-name-container"
      hx-swap="innerHTML"
      title="Edit project name"
      aria-label="Edit project name">
      <i class="bi bi-pencil text-primary"></i>
    </button>
  </div>
{% endif %}
```

---

### File 3: `project_description_field.html`

**Key Updates**:
- Same pattern as name field
- Validation: max 1000 chars
- Loading state on save button
- Tailwind classes throughout

```html
{% if edit_mode %}
  <form x-data="{
    formData: { description: '{{ project.description or '' }}' },
    errors: {},
    loading: false,
    validate() {
      this.errors = {};
      if (this.formData.description.length > 1000) {
        this.errors.description = 'Maximum 1000 characters';
      }
      return Object.keys(this.errors).length === 0;
    }
  }"
    @submit.prevent="if (validate()) $el.submit()"
    @htmx:before-request="loading = true"
    @htmx:after-request="loading = false"
    hx-post="/project/{{ project.id }}/update-description"
    hx-target="#project-description-container"
    hx-swap="innerHTML">

    <textarea
      name="description"
      x-model="formData.description"
      @input="validate()"
      :class="errors.description ? 'form-textarea border-error' : 'form-textarea'"
      rows="4"
      maxlength="1000"
      autofocus>{{ project.description or '' }}</textarea>

    <p x-show="errors.description"
       x-text="errors.description"
       x-transition
       class="form-text text-error"></p>

    {% if error %}
      <p class="form-text text-error">{{ error }}</p>
    {% endif %}

    <div class="flex items-center gap-3 mt-4">
      <button type="submit" :disabled="loading" class="btn btn-primary btn-sm">
        <span x-show="!loading">
          <i class="bi bi-check mr-2"></i>Save
        </span>
        <span x-show="loading" class="flex items-center">
          <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
          Saving...
        </span>
      </button>
      <button type="button" :disabled="loading"
              hx-get="/project/{{ project.id }}/settings/description"
              hx-target="#project-description-container"
              hx-swap="innerHTML"
              class="btn btn-secondary btn-sm">
        <i class="bi bi-x mr-2"></i>Cancel
      </button>
    </div>
  </form>

{% else %}
  <div class="flex items-start gap-2">
    <p id="project-description-display" class="text-base text-gray-700">
      {% if project.description %}
        {{ project.description }}
      {% else %}
        <em class="text-gray-400">No description set</em>
      {% endif %}
    </p>
    <button
      class="btn btn-sm btn-link p-0 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
      hx-get="/project/{{ project.id }}/settings/description?edit=true"
      hx-target="#project-description-container"
      hx-swap="innerHTML"
      title="Edit description"
      aria-label="Edit project description">
      <i class="bi bi-pencil text-primary"></i>
    </button>
  </div>
{% endif %}
```

---

### File 4: `project_tech_stack_field.html`

**Key Updates**:
- Same loading state pattern
- Validation: max 500 chars
- Badge styling with Tailwind

```html
{% if edit_mode %}
  <form x-data="{
    formData: { tech_stack: '{{ project.tech_stack | join(\", \") if project.tech_stack else \"\" }}' },
    errors: {},
    loading: false,
    validate() {
      this.errors = {};
      if (this.formData.tech_stack.length > 500) {
        this.errors.tech_stack = 'Maximum 500 characters';
      }
      return Object.keys(this.errors).length === 0;
    }
  }"
    @submit.prevent="if (validate()) $el.submit()"
    @htmx:before-request="loading = true"
    @htmx:after-request="loading = false"
    hx-post="/project/{{ project.id }}/update-tech-stack"
    hx-target="#project-tech-stack-container"
    hx-swap="innerHTML">

    <textarea
      name="tech_stack"
      x-model="formData.tech_stack"
      @input="validate()"
      :class="errors.tech_stack ? 'form-textarea border-error' : 'form-textarea'"
      rows="3"
      maxlength="500"
      autofocus>{{ project.tech_stack | join(', ') if project.tech_stack else '' }}</textarea>

    <p x-show="errors.tech_stack"
       x-text="errors.tech_stack"
       x-transition
       class="form-text text-error"></p>

    {% if error %}
      <p class="form-text text-error">{{ error }}</p>
    {% endif %}

    <div class="flex items-center gap-3 mt-4">
      <button type="submit" :disabled="loading" class="btn btn-primary btn-sm">
        <span x-show="!loading">
          <i class="bi bi-check mr-2"></i>Save
        </span>
        <span x-show="loading" class="flex items-center">
          <i class="bi bi-arrow-repeat animate-spin mr-2"></i>
          Saving...
        </span>
      </button>
      <button type="button" :disabled="loading"
              hx-get="/project/{{ project.id }}/settings/tech-stack"
              hx-target="#project-tech-stack-container"
              hx-swap="innerHTML"
              class="btn btn-secondary btn-sm">
        <i class="bi bi-x mr-2"></i>Cancel
      </button>
    </div>
  </form>

{% else %}
  <div class="flex items-start gap-2">
    <div id="project-tech-stack-display">
      {% if project.tech_stack %}
        <div class="flex flex-wrap gap-2">
          {% for tech in project.tech_stack %}
            <span class="badge badge-info">{{ tech }}</span>
          {% endfor %}
        </div>
      {% else %}
        <em class="text-gray-400">No technologies specified</em>
      {% endif %}
    </div>
    <button
      class="btn btn-sm btn-link p-0 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
      hx-get="/project/{{ project.id }}/settings/tech-stack?edit=true"
      hx-target="#project-tech-stack-container"
      hx-swap="innerHTML"
      title="Edit technology stack"
      aria-label="Edit technology stack">
      <i class="bi bi-pencil text-primary"></i>
    </button>
  </div>
{% endif %}
```

---

## ✅ Testing Checklist

After implementing fixes, verify:

### Functionality
- [ ] Name field saves correctly
- [ ] Description field saves correctly
- [ ] Tech stack saves correctly
- [ ] Cancel buttons restore original values
- [ ] Server validation still works
- [ ] Toast notifications appear on save

### UX
- [ ] Loading spinners appear during save
- [ ] Buttons disable during save (prevent double-submit)
- [ ] Client-side validation shows errors immediately
- [ ] Error messages clear when user fixes input

### Accessibility
- [ ] Tab navigation works (Tab through fields, buttons)
- [ ] Enter key submits forms
- [ ] Escape key cancels edit mode
- [ ] Focus rings visible on all interactive elements
- [ ] Screen reader announces errors

### Visual
- [ ] Consistent with design system (Tailwind classes)
- [ ] Badges styled correctly
- [ ] Spacing matches other pages
- [ ] Responsive on mobile (375px width)
- [ ] Icons aligned properly

---

## 🚀 Implementation Order

1. **Start with one field** (e.g., project name) to establish pattern
2. **Test thoroughly** before copying to other fields
3. **Apply same pattern** to description and tech stack
4. **Update main template** (project_settings.html)
5. **Final testing** across all fields

**Estimated Time**: 2-3 hours for all fixes

---

**Author**: flask-ux-designer
**Date**: 2025-10-22
**Task**: #792 - Project Settings UX Review
