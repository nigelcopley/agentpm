# Tooltip Usage Guide

**Component**: Alpine.js Tooltip Directive
**Version**: 1.0.0
**Status**: Ready for Implementation

---

## Quick Start

### 1. Include Tooltip Assets

**Add to `layouts/modern_base.html`**:

```html
<!-- In <head> section -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/tooltips.css') }}">

<!-- Before </body> (after Alpine.js) -->
<script src="{{ url_for('static', filename='js/components/tooltip.js') }}"></script>
```

### 2. Basic Usage

```html
<button x-tooltip="'Tooltip text'">Hover me</button>
```

---

## Positioning

### Top (Default)
```html
<button x-tooltip="'Top tooltip'">Hover me</button>
```

### Bottom
```html
<button x-tooltip.bottom="'Bottom tooltip'">Hover me</button>
```

### Left
```html
<button x-tooltip.left="'Left tooltip'">Hover me</button>
```

### Right
```html
<button x-tooltip.right="'Right tooltip'">Hover me</button>
```

---

## Advanced Patterns

### Custom Delay
```html
<!-- 500ms delay -->
<button x-tooltip.delay.500="'Slow tooltip'">Hover me</button>

<!-- 1000ms delay -->
<button x-tooltip.delay.1000="'Very slow'">Hover me</button>
```

### Multiline Tooltips
```html
<button x-tooltip.multiline="'Line 1\nLine 2\nLine 3'">
  Info
</button>
```

### Combined Modifiers
```html
<button x-tooltip.bottom.delay.500.multiline="'Bottom tooltip\nWith delay\nAnd multiple lines'">
  Complex tooltip
</button>
```

---

## Common Use Cases

### 1. Icon Button with Tooltip

```html
<!-- Edit button -->
<button
  class="btn btn-sm btn-secondary"
  x-tooltip="'Edit work item'"
  aria-label="Edit work item">
  <i class="bi bi-pencil"></i>
</button>

<!-- Delete button -->
<button
  class="btn btn-sm btn-error"
  x-tooltip.bottom="'Delete permanently (cannot be undone)'"
  aria-label="Delete work item">
  <i class="bi bi-trash"></i>
</button>

<!-- View button -->
<a
  href="/view"
  class="btn btn-sm btn-secondary"
  x-tooltip="'View details'"
  aria-label="View details">
  <i class="bi bi-eye"></i>
</a>
```

### 2. Form Field Help Icon

```html
<div class="form-group">
  <label for="business_context" class="form-label">
    Business Context
    <span
      x-tooltip.right="'Explain why this work matters to the business. Minimum 50 characters required for D1 gate validation.'"
      class="tooltip-help-icon">
      <i class="bi bi-info-circle"></i>
    </span>
  </label>
  <textarea id="business_context" name="business_context" class="form-input" rows="3"></textarea>
  <p class="form-text">Explain the business value (≥50 chars)</p>
</div>
```

### 3. Truncated Text with Tooltip

```html
<h3
  class="text-lg font-semibold text-gray-900 truncate-with-tooltip"
  x-tooltip.bottom="'{{ work_item.name }}'">
  {{ work_item.name }}
</h3>
```

### 4. Status Badge with Explanation

```html
<span
  class="badge badge-warning"
  x-tooltip.bottom="'Work is in progress by the assigned agent'">
  <i class="bi bi-arrow-repeat"></i>
  In Progress
</span>
```

### 5. Disabled Button with Reason

```html
<button
  class="btn btn-primary"
  disabled
  x-tooltip="'Cannot proceed: Missing required fields'">
  Submit
</button>
```

### 6. Complex Table Cell

```html
<td>
  <span
    x-tooltip.bottom.multiline="'Priority: {{ work_item.priority }}\nEstimate: {{ work_item.effort_hours }}h\nStatus: {{ work_item.status }}'"
    class="cursor-help">
    {{ work_item.name|truncate(30) }}
  </span>
</td>
```

---

## Accessibility Requirements

### Always Include ARIA Labels

**Icon buttons MUST have `aria-label`**:
```html
<!-- ✅ GOOD -->
<button
  x-tooltip="'Edit'"
  aria-label="Edit work item">
  <i class="bi bi-pencil"></i>
</button>

<!-- ❌ BAD (no aria-label) -->
<button x-tooltip="'Edit'">
  <i class="bi bi-pencil"></i>
</button>
```

### Keyboard Navigation

Tooltips automatically:
- ✅ Show on `focus` event (keyboard navigation)
- ✅ Hide on `blur` event (keyboard leave)
- ✅ Close on `Escape` key
- ✅ Work with Tab navigation

**No additional code needed** - handled by directive.

### Screen Reader Support

Tooltips use `aria-describedby` to link to trigger:
```html
<!-- Rendered HTML -->
<button aria-describedby="tooltip-abc123">
  Hover me
  <div id="tooltip-abc123" role="tooltip" aria-hidden="false">
    Tooltip text
  </div>
</button>
```

### Focus Visible

Trigger elements automatically get focus ring:
```css
[x-tooltip]:focus-visible {
  outline: 2px solid #6366f1; /* primary color */
  outline-offset: 2px;
}
```

---

## Styling Customization

### Override Tooltip Colors

```css
/* In your custom CSS */
.tooltip-content {
  background-color: #4f46e5; /* primary color */
  color: #ffffff;
}

.tooltip-content::before {
  border-top-color: #4f46e5; /* match background */
}
```

### Larger Tooltips

```css
.tooltip-content.tooltip-large {
  max-width: 400px;
  font-size: 1rem;
  padding: 0.75rem 1rem;
}
```

Usage:
```html
<button
  x-tooltip.multiline="'Large tooltip content'"
  x-tooltip:class="'tooltip-large'">
  Info
</button>
```

---

## Mobile Considerations

### Touch Support

Tooltips work on touch devices:
- **Tap**: Shows tooltip
- **Tap again**: Hides tooltip
- **Tap elsewhere**: Auto-hides

### Responsive Sizes

Mobile tooltips are automatically smaller:
```css
@media (max-width: 640px) {
  .tooltip-content {
    max-width: 200px;
    font-size: 0.8125rem; /* 13px */
  }
}
```

---

## Performance Considerations

### Lazy Creation

Tooltips are **created on demand** (first hover/focus):
- ❌ Not created at page load
- ✅ Created when needed
- ✅ Cleaned up when element removed

### Debouncing

Tooltips have built-in delay (default 300ms):
- Prevents flashing on quick hover
- Reduces DOM manipulations
- Improves perceived performance

---

## Testing Checklist

### Manual Testing

- [ ] **Mouse hover**: Tooltip appears after delay
- [ ] **Keyboard focus**: Tab to element, tooltip shows
- [ ] **Keyboard navigation**: Escape closes tooltip
- [ ] **Touch device**: Tap shows tooltip, tap again hides
- [ ] **Screen reader**: ARIA labels read correctly
- [ ] **Mobile**: Tooltip positions correctly (no overflow)
- [ ] **Long text**: Multiline tooltip wraps properly
- [ ] **Viewport edge**: Tooltip flips position if needed

### Accessibility Testing

- [ ] **Color contrast**: ≥4.5:1 ratio (white on gray-800)
- [ ] **Keyboard only**: All tooltips reachable via Tab
- [ ] **Screen reader**: VoiceOver/NVDA reads `aria-label` and tooltip
- [ ] **Focus visible**: Clear focus ring on trigger
- [ ] **Reduced motion**: No animations if `prefers-reduced-motion`
- [ ] **High contrast mode**: Tooltip visible with border

---

## Common Patterns by Route

### Work Items List (`work-items/list.html`)

```html
<!-- Card actions -->
<div class="flex gap-2">
  <button
    class="btn btn-sm btn-secondary"
    x-tooltip="'Edit work item'"
    aria-label="Edit work item"
    onclick="editWorkItem({{ work_item.id }})">
    <i class="bi bi-pencil"></i>
  </button>

  <button
    class="btn btn-sm btn-secondary"
    x-tooltip="'Duplicate work item'"
    aria-label="Duplicate work item"
    onclick="duplicateWorkItem({{ work_item.id }})">
    <i class="bi bi-copy"></i>
  </button>

  <button
    class="btn btn-sm btn-error"
    x-tooltip.bottom="'Delete permanently'"
    aria-label="Delete work item"
    onclick="deleteWorkItem({{ work_item.id }})">
    <i class="bi bi-trash"></i>
  </button>
</div>
```

### Forms (`work-items/form.html`)

```html
<!-- Business Context field -->
<div class="form-group">
  <label for="business_context" class="form-label">
    Business Context
    <span
      x-tooltip.right.multiline="'Why this work matters:\n• Business value\n• User impact\n• Strategic alignment\n\nRequired: ≥50 characters for D1 gate'"
      class="tooltip-help-icon">
      <i class="bi bi-info-circle"></i>
    </span>
  </label>
  <textarea id="business_context" name="business_context" class="form-input" rows="3"></textarea>
</div>

<!-- Priority field -->
<div class="form-group">
  <label for="priority" class="form-label">
    Priority
    <span
      x-tooltip.right.multiline="'Priority levels:\n• P1: Critical (urgent, high impact)\n• P2: High (important, near-term)\n• P3: Medium (normal priority)\n• P4: Low (can defer)\n• P5: Very Low (nice-to-have)'"
      class="tooltip-help-icon">
      <i class="bi bi-info-circle"></i>
    </span>
  </label>
  <select id="priority" name="priority" class="form-select">
    <!-- options -->
  </select>
</div>
```

### Dashboard (`dashboard.html`)

```html
<!-- Metric card with explanation -->
<div class="card" x-tooltip.bottom="'Total number of work items across all projects'">
  <div class="card-body text-center">
    <i class="bi bi-kanban text-primary text-2xl"></i>
    <h3 class="text-3xl font-bold mt-2">{{ metrics.total_work_items }}</h3>
    <p class="text-sm text-gray-600">Total Work Items</p>
  </div>
</div>
```

### Context Files (`context_files_list.html`)

```html
<!-- File actions -->
<a
  href="{{ url_for('context_file_preview', filepath=file.path) }}"
  class="btn btn-sm btn-secondary"
  x-tooltip="'View file details and preview'"
  aria-label="View file details">
  <i class="bi bi-eye"></i>
</a>

<a
  href="{{ url_for('download_context_file', filepath=file.path) }}"
  class="btn btn-sm btn-secondary"
  x-tooltip="'Download full file'"
  aria-label="Download file"
  download>
  <i class="bi bi-download"></i>
</a>
```

---

## Migration Guide

### Step 1: Update Base Template

```html
<!-- layouts/modern_base.html -->
<head>
  <!-- Existing CSS -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/components/tooltips.css') }}">
</head>
<body>
  <!-- Existing content -->

  <!-- Before Alpine.js -->
  <script src="{{ url_for('static', filename='js/components/tooltip.js') }}"></script>
</body>
```

### Step 2: Update Icon Buttons

**Find all icon buttons without text**:
```bash
grep -r "bi bi-" templates/ | grep -v "aria-label" | grep -v "x-tooltip"
```

**Update each match**:
```html
<!-- BEFORE -->
<button class="btn btn-sm btn-secondary">
  <i class="bi bi-pencil"></i>
</button>

<!-- AFTER -->
<button
  class="btn btn-sm btn-secondary"
  x-tooltip="'Edit'"
  aria-label="Edit">
  <i class="bi bi-pencil"></i>
</button>
```

### Step 3: Add Form Help Icons

**Pattern**:
```html
<label for="field" class="form-label">
  Field Name
  <span x-tooltip.right="'Help text'" class="tooltip-help-icon">
    <i class="bi bi-info-circle"></i>
  </span>
</label>
```

### Step 4: Test and Validate

```bash
# Start development server
apm web start

# Test routes:
# 1. /work-items (icon buttons)
# 2. /work-items/create (form help icons)
# 3. /dashboard (metric cards)
# 4. /context (file actions)
```

---

## Troubleshooting

### Tooltip Not Showing

**Check**:
1. ✅ Alpine.js loaded (`window.Alpine` exists)
2. ✅ Tooltip directive registered (console log: "Tooltip directive registered")
3. ✅ CSS file loaded (check DevTools Network tab)
4. ✅ Expression is valid (`x-tooltip="'text'"` not `x-tooltip="text"`)

### Tooltip Position Wrong

**Solution**:
```html
<!-- Explicitly set position -->
<button x-tooltip.bottom="'Tooltip'">Button</button>
```

### Tooltip Overflows Viewport

**Automatic**: Directive adjusts position if tooltip overflows.

**Manual override**:
```css
.tooltip-content {
  max-width: 200px; /* Smaller on mobile */
}
```

### Tooltip Not Accessible

**Ensure**:
- Icon buttons have `aria-label`
- Tooltip has `role="tooltip"`
- Trigger has `aria-describedby`

---

## FAQ

**Q: Can I use HTML in tooltips?**
A: No. Use plain text only. For complex content, use a modal or popover.

**Q: How do I change the default delay?**
A: Use `.delay.{ms}` modifier: `x-tooltip.delay.500="'text'"`

**Q: Do tooltips work on disabled buttons?**
A: Yes, but wrap the button: `<span x-tooltip="'...">` `<button disabled>` `</button>` `</span>`

**Q: Can I use dynamic content?**
A: Yes: `x-tooltip="workItem.name"` (no quotes for variables)

**Q: How do I test accessibility?**
A: Use Chrome DevTools Lighthouse, axe DevTools, or VoiceOver/NVDA.

---

## References

- **Design System**: `docs/architecture/web/design-system.md`
- **Audit Report**: `docs/architecture/web/tooltip-audit-report.md`
- **Alpine.js Docs**: https://alpinejs.dev/directives/
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/Understanding/content-on-hover-or-focus

---

**Last Updated**: 2025-10-22
**Version**: 1.0.0
**Maintained By**: flask-ux-designer agent
