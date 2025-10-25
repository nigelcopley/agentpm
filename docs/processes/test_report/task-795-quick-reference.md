# Task 795: Documents UX Review - Quick Reference Card

**For**: Developers implementing fixes
**Date**: 2025-10-22

---

## 🎯 Priority Matrix

| Priority | Issue | Fix Time | Impact |
|----------|-------|----------|--------|
| 🔴 P1 | Table classes missing | 5 min | High |
| 🔴 P1 | ARIA labels missing | 10 min | High |
| 🔴 P1 | File type badges | 30 min | Medium |
| 🟡 P2 | Search functionality | 60 min | High |
| 🟡 P2 | Empty state | 30 min | Medium |
| 🟡 P2 | Loading states | 30 min | Low |
| 🟡 P2 | Mobile cards | 60 min | High |
| 🟡 P2 | Sidebar integration | 30 min | Medium |
| 🟢 P3 | Sort controls | 30 min | Medium |
| 🟢 P3 | Tooltips | 15 min | Low |
| 🟢 P3 | Bulk actions | 60 min | Low |
| 🟢 P3 | Pagination | 45 min | Medium |

**Total**: 7.0 hours (phased implementation recommended)

---

## 🚀 Quick Wins (< 30 min each)

### 1. Fix Table Classes (5 min)
**File**: `templates/documents/list.html` (line 94)

**Before**:
```html
<table class="min-w-full divide-y divide-gray-100 text-left text-sm text-gray-700">
```

**After**:
```html
<table class="table table-hover">
```

✅ **Impact**: Consistent styling, hover states

---

### 2. Add ARIA Labels (10 min)
**File**: `templates/documents/list.html` (lines 152-159)

**Before**:
```html
<a href="/documents/{{ doc.id }}" class="btn btn-primary">
  <i class="bi bi-eye"></i> View
</a>
```

**After**:
```html
<a href="/documents/{{ doc.id }}"
   class="btn btn-primary"
   aria-label="View document {{ doc.title or 'ID ' ~ doc.id }}">
  <i class="bi bi-eye" aria-hidden="true"></i> View
</a>
```

✅ **Impact**: Screen reader accessibility

---

### 3. Add Tooltips (15 min)
**File**: `templates/documents/list.html` (line 121)

**Before**:
```html
<code class="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600">
  {{ doc.file_path | truncate(60) }}
</code>
```

**After**:
```html
<code class="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600 cursor-help"
      title="{{ doc.file_path }}">
  {{ doc.file_path | truncate(60) }}
</code>
```

✅ **Impact**: Users see full paths on hover

---

## 📋 Copy-Paste Code Blocks

### File Type Badge Macro
**Create**: `templates/components/layout/document_helpers.html`

```html
{% macro file_type_badge(format, document_type) %}
  {% set icon_map = {
    'markdown': 'bi-markdown',
    'yaml': 'bi-file-earmark-code',
    'json': 'bi-braces',
    'pdf': 'bi-file-pdf',
    'html': 'bi-filetype-html'
  } %}
  {% set color_map = {
    'markdown': 'bg-blue-100 text-blue-700',
    'yaml': 'bg-purple-100 text-purple-700',
    'json': 'bg-amber-100 text-amber-700',
    'pdf': 'bg-red-100 text-red-700',
    'html': 'bg-green-100 text-green-700'
  } %}
  <span class="inline-flex items-center gap-2 rounded-full {{ color_map.get(format, 'bg-gray-100 text-gray-600') }} px-3 py-1 text-xs font-semibold">
    <i class="{{ icon_map.get(format, 'bi-file-earmark') }}"></i>
    {{ format.upper() if format else 'UNKNOWN' }}
  </span>
{% endmacro %}
```

**Usage** (replace lines 134-145):
```html
{% import 'components/layout/document_helpers.html' as helpers %}
{{ helpers.file_type_badge(doc.format, doc.document_type) }}
```

---

### Search Input Section
**Insert after line 35** in `templates/documents/list.html`

```html
<section class="mb-6 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
  <form method="GET" action="/documents" class="flex gap-3">
    <div class="flex-1 relative">
      <label for="search" class="sr-only">Search documents</label>
      <input type="search" id="search" name="q"
             value="{{ request.args.get('q', '') }}"
             class="form-input pl-10"
             placeholder="Search by title, description, or file path..."
             aria-label="Search documents">
      <i class="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
    </div>
    <button type="submit" class="btn btn-primary">
      <i class="bi bi-search mr-2"></i> Search
    </button>
    {% if request.args.get('q') %}
    <a href="/documents" class="btn btn-secondary">
      <i class="bi bi-x mr-2"></i> Clear
    </a>
    {% endif %}
  </form>
</section>
```

**Backend** (add to `research.py:347`):
```python
search_query = request.args.get('q')
# Pass to database method (requires method update)
```

---

### Loading Overlay
**Wrap content** (line 5) in `templates/documents/list.html`

```html
{% block content %}
<div x-data="{ loading: false }" x-init="loading = true; setTimeout(() => loading = false, 100)">
  <div x-show="loading" x-transition.opacity
       class="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="flex flex-col items-center gap-3">
      <i class="bi bi-arrow-repeat animate-spin text-4xl text-primary"></i>
      <p class="text-sm text-gray-600 font-medium">Loading documents...</p>
    </div>
  </div>

  <div x-show="!loading" x-transition>
    <!-- Existing content here -->
  </div>
</div>
{% endblock %}
```

---

### Enhanced Empty State
**Replace lines 170-177** in `templates/documents/list.html`

```html
<section class="mt-8 rounded-2xl border border-gray-200 bg-white p-16 text-center shadow-sm">
  <div class="flex flex-col items-center gap-4">
    <svg class="w-48 h-48 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
    <h2 class="text-2xl font-bold text-gray-900">No documents yet</h2>
    <p class="max-w-md text-gray-600">
      Documents track ADRs, design notes, test plans, and supporting documentation.
      Start by adding your first document reference.
    </p>
    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 max-w-2xl">
      <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">CLI Command</p>
      <code class="block bg-gray-900 text-green-400 px-4 py-3 rounded text-sm font-mono text-left">
        apm document add \<br>
        &nbsp;&nbsp;--entity-type=work_item \<br>
        &nbsp;&nbsp;--entity-id=123 \<br>
        &nbsp;&nbsp;--file-path="docs/design.md" \<br>
        &nbsp;&nbsp;--document-type=design
      </code>
    </div>
  </div>
</section>
```

---

### Mobile Card View
**Add after line 93** (desktop table) in `templates/documents/list.html`

```html
{# Desktop: Table View #}
<div class="hidden lg:block overflow-x-auto">
  <table class="table table-hover">
    <!-- Existing table -->
  </table>
</div>

{# Mobile: Card View #}
<div class="lg:hidden space-y-4">
  {% for doc in docs %}
  <article class="card">
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1">
        <h3 class="font-semibold text-gray-900">
          {{ doc.title or 'Untitled Document' }}
        </h3>
        <p class="text-xs text-gray-500 mt-1">
          {{ doc.entity_type.replace('_',' ').title() }} • {{ doc.entity_name }}
        </p>
      </div>
      {{ helpers.file_type_badge(doc.format, doc.document_type) }}
    </div>
    {% if doc.description %}
    <p class="text-sm text-gray-600 mb-3">{{ doc.description | truncate(80) }}</p>
    {% endif %}
    <div class="flex gap-2">
      <a href="/documents/{{ doc.id }}" class="btn btn-primary flex-1 justify-center">
        <i class="bi bi-eye mr-2"></i> View
      </a>
      <a href="/documents/download/{{ doc.id }}" class="btn btn-secondary flex-1 justify-center">
        <i class="bi bi-download mr-2"></i> Download
      </a>
    </div>
  </article>
  {% endfor %}
</div>
```

---

## 🧪 Testing Checklist

After each fix, test:

- [ ] **Desktop**: Chrome, Firefox, Safari
- [ ] **Mobile**: iOS Safari, Chrome Android (< 768px)
- [ ] **Screen Reader**: VoiceOver (Mac) or NVDA (Windows)
- [ ] **Keyboard**: Tab navigation, Enter to submit, Escape to close
- [ ] **Color Contrast**: Use browser DevTools Accessibility panel

---

## 📦 File Locations

```
aipm-v2/
├── agentpm/web/
│   ├── templates/
│   │   ├── documents/
│   │   │   └── list.html                    ← Primary file to edit
│   │   └── components/layout/
│   │       ├── sidebar_documents.html       ← Sidebar integration
│   │       └── document_helpers.html        ← NEW: Create macro file
│   ├── routes/
│   │   └── research.py                      ← Backend changes
│   └── static/css/
│       └── brand-system.css                 ← Ensure .table classes exist
└── docs/
    └── reviews/
        ├── task-795-documents-ux-review.md  ← Full detailed review
        └── task-795-quick-reference.md      ← This file
```

---

## 🔗 Related Documentation

- **Full Review**: `docs/reviews/task-795-documents-ux-review.md`
- **Design System**: `docs/architecture/web/design-system.md`
- **Component Snippets**: `docs/architecture/web/component-snippets.md`
- **Tailwind Docs**: https://tailwindcss.com/docs
- **Alpine.js Docs**: https://alpinejs.dev/

---

## ⚡ Implementation Order

### Day 1: Critical Fixes (2h)
1. Fix table classes (5 min)
2. Add ARIA labels (10 min)
3. Create file type badge macro (30 min)
4. Add tooltips (15 min)
5. Test accessibility (30 min)

### Day 2: High Priority (3h)
6. Implement search (60 min)
7. Enhance empty state (30 min)
8. Add loading states (30 min)
9. Create mobile card view (60 min)

### Day 3: Polish (2h)
10. Add sort controls (30 min)
11. Integrate sidebar (30 min)
12. Add pagination (45 min)
13. Final testing (15 min)

---

## 💡 Pro Tips

1. **Test as you go**: Don't implement all fixes then test
2. **Use design tokens**: Stick to Tailwind utility classes
3. **Mobile first**: Test on phone immediately
4. **Screen reader**: Download NVDA (free) or use VoiceOver
5. **Git commits**: One commit per fix for easy rollback

---

## ❓ Common Issues

**Q: Table styles not applying?**
A: Check `brand-system.css` includes `.table` class definition (see design system doc)

**Q: Alpine.js not working?**
A: Verify Alpine.js 3.14.1 loaded in base template (`<script defer src="...alpinejs"></script>`)

**Q: Icons missing?**
A: Bootstrap Icons 1.11.1 required (`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">`)

**Q: Search not working?**
A: Update `document_references.py` method to accept `search_query` parameter

---

**Quick Reference**: ✅ Complete
**Full Review**: See `task-795-documents-ux-review.md`
**Questions?**: Refer to design system documentation

---

*Last updated: 2025-10-22*
