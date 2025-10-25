# APM (Agent Project Manager) Design System - Quick Start Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-21

---

## What You Need to Know (5 Minutes)

The APM (Agent Project Manager) design system is built on **Tailwind CSS** with **Alpine.js** for interactivity. This guide gets you productive in 5 minutes.

---

## File Locations

| File | Purpose |
|------|---------|
| `/docs/architecture/web/design-system.md` | Complete design system documentation (1,216 lines) |
| `/docs/architecture/web/component-snippets.md` | Copy-paste ready components (936 lines) |
| `/tailwind.config.js` | Extended Tailwind configuration (AIPM colors, fonts) |
| `/agentpm/web/static/css/brand-system.css` | Custom CSS (gradients, animations) |
| `/agentpm/web/templates/layouts/modern_base.html` | Base template with Alpine.js |

---

## Core Technologies

### Tailwind CSS 3.4.14
Utility-first CSS framework - use classes instead of writing CSS.

**Example**:
```html
<!-- OLD WAY (Custom CSS) -->
<style>.my-button { padding: 1rem; background: blue; }</style>
<button class="my-button">Click</button>

<!-- NEW WAY (Tailwind) -->
<button class="px-4 py-2 bg-primary text-white rounded-md">Click</button>
```

### Alpine.js 3.14.1
Lightweight JavaScript framework for interactivity (15KB).

**Example**:
```html
<!-- Dropdown without Alpine.js -->
<button onclick="toggleDropdown()">Menu</button>
<div id="dropdown">...</div>
<script>function toggleDropdown() { ... }</script>

<!-- With Alpine.js -->
<div x-data="{ open: false }">
  <button @click="open = !open">Menu</button>
  <div x-show="open">...</div>
</div>
```

### Bootstrap Icons 1.11.1
Icon system (already loaded in base template).

**Example**:
```html
<i class="bi bi-check-circle text-success"></i>
<i class="bi bi-x-circle text-error"></i>
```

---

## Color System (Quick Reference)

Use these Tailwind classes for consistent colors:

| Color | Class | Use Case | Example |
|-------|-------|----------|---------|
| Primary (Blue) | `bg-primary` `text-primary` | CTAs, links, focus | `<button class="bg-primary text-white">` |
| Success (Green) | `bg-success` `text-success` | Completed, positive | `<span class="badge badge-success">` |
| Warning (Yellow) | `bg-warning` `text-warning` | In-progress, caution | `<span class="badge badge-warning">` |
| Error (Red) | `bg-error` `text-error` | Errors, blocked | `<span class="badge badge-error">` |
| Info (Cyan) | `bg-info` `text-info` | Informational | `<span class="badge badge-info">` |
| Gray-50 | `bg-gray-50` | Page background | `<body class="bg-gray-50">` |
| White | `bg-white` | Cards, modals | `<div class="card bg-white">` |

### AIPM-Specific Colors

| Color | Class | Use Case |
|-------|-------|----------|
| Confidence High | `bg-confidence-green` | Confidence ≥0.80 |
| Confidence Med | `bg-confidence-yellow` | Confidence 0.60-0.79 |
| Confidence Low | `bg-confidence-red` | Confidence <0.60 |
| Phase D1 | `bg-phase-d1` | Discovery phase |
| Phase P1 | `bg-phase-p1` | Planning phase |
| Phase I1 | `bg-phase-i1` | Implementation |

**Full palette**: See `tailwind.config.js` (extended from 5 shades to 9 shades per color).

---

## Component Quick Reference

### Buttons

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-error">Danger</button>
```

### Forms

```html
<div class="space-y-2">
  <label class="form-label">Name</label>
  <input type="text" class="form-input" placeholder="Enter name...">
  <p class="form-text">Help text</p>
</div>
```

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    Content
  </div>
</div>
```

### Badges

```html
<span class="badge badge-success">Completed</span>
<span class="badge badge-warning">In Progress</span>
<span class="badge badge-error">Blocked</span>
```

### Alerts

```html
<div class="alert alert-success">
  <i class="bi bi-check-circle mr-2"></i>
  <span>Success message</span>
</div>
```

**More components**: See `/docs/architecture/web/component-snippets.md` (20+ copy-paste ready patterns).

---

## Common Patterns

### 1. Responsive Grid

```html
<!-- 1 column mobile, 2 tablet, 4 desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
  <div class="card">Card 4</div>
</div>
```

### 2. Modal (Alpine.js)

```html
<div x-data="{ open: false }">
  <button @click="open = true" class="btn btn-primary">Open Modal</button>

  <div x-show="open" class="fixed inset-0 bg-gray-900/60 z-50 flex items-center justify-center">
    <div @click.away="open = false" class="bg-white rounded-xl p-6 max-w-2xl w-full">
      <h2 class="text-2xl font-bold mb-4">Modal Title</h2>
      <p class="text-gray-700 mb-6">Modal content...</p>
      <button @click="open = false" class="btn btn-secondary">Close</button>
    </div>
  </div>
</div>
```

### 3. Toast Notification (JavaScript)

```html
<script>
// Function already available in modern_base.html
showToast('Work item created!', 'success');
showToast('Failed to save', 'error');
showToast('Processing...', 'info');
</script>
```

### 4. Dropdown Menu (Alpine.js)

```html
<div x-data="{ open: false }" class="relative">
  <button @click="open = !open" @click.away="open = false" class="btn btn-secondary">
    Actions <i class="bi bi-chevron-down ml-2"></i>
  </button>

  <div x-show="open" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border">
    <a href="#" class="block px-4 py-2 hover:bg-gray-50">Edit</a>
    <a href="#" class="block px-4 py-2 hover:bg-gray-50">Delete</a>
  </div>
</div>
```

---

## Alpine.js Cheat Sheet

| Directive | Purpose | Example |
|-----------|---------|---------|
| `x-data` | Component state | `x-data="{ open: false }"` |
| `x-show` | Toggle visibility | `x-show="open"` |
| `@click` | Click handler | `@click="open = true"` |
| `@click.away` | Click outside | `@click.away="open = false"` |
| `x-model` | Two-way binding | `x-model="formData.name"` |
| `x-transition` | Smooth transitions | `x-show="open" x-transition` |
| `:class` | Dynamic classes | `:class="{ 'bg-primary': active }"` |
| `x-text` | Dynamic text | `x-text="count"` |

**Learn more**: https://alpinejs.dev/start-here

---

## Tailwind Spacing Reference

Tailwind uses a numeric scale for spacing (padding, margin, gap):

| Class | Value | Use Case |
|-------|-------|----------|
| `p-1` `m-1` | 0.25rem (4px) | Tight spacing |
| `p-2` `m-2` | 0.5rem (8px) | Small gaps |
| `p-3` `m-3` | 0.75rem (12px) | Default gap |
| `p-4` `m-4` | 1rem (16px) | Card padding |
| `p-6` `m-6` | 1.5rem (24px) | Section padding |
| `p-8` `m-8` | 2rem (32px) | Page padding |

**Directional**:
- `px-4` = Horizontal padding (left + right)
- `py-2` = Vertical padding (top + bottom)
- `pt-6` = Padding top only
- `mb-4` = Margin bottom only

**Gaps**:
- `gap-3` = Gap between grid/flex children
- `space-y-4` = Vertical spacing between children

---

## Accessibility Checklist

Every component must:
- [ ] Have visible focus states (Tailwind adds automatically)
- [ ] Support keyboard navigation (Tab, Enter, Escape)
- [ ] Include ARIA labels for icon-only buttons
- [ ] Meet WCAG 2.1 AA color contrast (4.5:1 for text)
- [ ] Work with screen readers

**Example (Accessible Button)**:
```html
<!-- Icon-only button needs aria-label -->
<button class="btn btn-secondary" aria-label="Close dialog">
  <i class="bi bi-x"></i>
</button>

<!-- Button with text is already accessible -->
<button class="btn btn-primary">
  <i class="bi bi-plus mr-2"></i>
  Create
</button>
```

---

## Responsive Design Tips

### Mobile-First Approach

Tailwind is **mobile-first**, meaning base classes apply to mobile, and you add breakpoints for larger screens.

```html
<!-- Bad (Desktop-first) -->
<div class="w-1/2 md:w-full">Content</div>

<!-- Good (Mobile-first) -->
<div class="w-full md:w-1/2">Content</div>
```

### Breakpoints

| Breakpoint | Min Width | Example |
|------------|-----------|---------|
| (default) | 0px | `text-sm` |
| `sm:` | 640px | `sm:text-base` |
| `md:` | 768px | `md:text-lg` |
| `lg:` | 1024px | `lg:text-xl` |
| `xl:` | 1280px | `xl:text-2xl` |

**Example**:
```html
<!-- Text size changes at breakpoints -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">
  Responsive Heading
</h1>

<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">Desktop only</div>

<!-- Grid: 1 col mobile, 2 tablet, 4 desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <!-- Cards -->
</div>
```

---

## Workflow: Adding a New Component

1. **Search component-snippets.md** for similar pattern
2. **Copy snippet** to your template
3. **Customize content** (replace placeholders)
4. **Test in browser** (check mobile + desktop)
5. **Test accessibility** (Tab navigation, screen reader)
6. **Commit** with clear message

**Example**:
```bash
# 1. Edit template
vim agentpm/web/templates/work-items/detail.html

# 2. Add component (from snippets.md)
# <div class="card">...</div>

# 3. Test locally
python -m agentpm.web.app

# 4. Verify responsive
# Resize browser to 375px (mobile), 768px (tablet), 1024px (desktop)

# 5. Commit
git add agentpm/web/templates/work-items/detail.html
git commit -m "feat: add metric cards to work item detail page"
```

---

## Common Questions

### Q: When do I use custom CSS vs. Tailwind?

**A**: Prefer Tailwind classes. Only use custom CSS for:
- Complex animations (keyframes)
- Global resets
- Vendor-specific prefixes

### Q: How do I customize colors?

**A**: Edit `tailwind.config.js` under `theme.extend.colors`. Colors are already set up for AIPM (primary, success, error, etc.).

### Q: Can I use HTMX?

**A**: Not yet implemented, but planned. Use Alpine.js for now (see snippets.md for patterns).

### Q: Where are the icons from?

**A**: Bootstrap Icons (https://icons.getbootstrap.com/). Already loaded in base template.

**Usage**:
```html
<i class="bi bi-check-circle"></i>  <!-- Checkmark -->
<i class="bi bi-x-circle"></i>       <!-- X mark -->
<i class="bi bi-trash"></i>          <!-- Delete -->
<i class="bi bi-pencil"></i>         <!-- Edit -->
```

### Q: How do I rebuild Tailwind CSS?

**A**: Tailwind is configured with JIT (Just-In-Time) mode. Changes are reflected automatically during development.

If needed:
```bash
# Rebuild CSS (if using build process)
npx tailwindcss -i ./agentpm/web/static/css/input.css -o ./agentpm/web/static/css/brand-system.css --watch
```

---

## Next Steps

1. **Read design-system.md** (30 min) - Comprehensive guide
2. **Browse component-snippets.md** (15 min) - 20+ ready-to-use patterns
3. **Try Alpine.js tutorial** (20 min) - https://alpinejs.dev/start-here
4. **Review existing templates** - See dashboard_modern.html for examples

---

## Resources

- **Tailwind Docs**: https://tailwindcss.com/docs
- **Alpine.js Docs**: https://alpinejs.dev/
- **Bootstrap Icons**: https://icons.getbootstrap.com/
- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **AIPM Design System**: `/docs/architecture/web/design-system.md`
- **Component Snippets**: `/docs/architecture/web/component-snippets.md`

---

**Questions?** Refer to the design system documentation or ask in #web-dev channel.

**Last Updated**: 2025-10-21
**Maintained by**: APM (Agent Project Manager) Team
