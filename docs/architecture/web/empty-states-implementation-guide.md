# Empty States Implementation Guide

**Date**: 2025-10-22
**Task**: WI-35, Task 801
**Related**: `empty-states-audit.md`
**Status**: Ready for Implementation

---

## Quick Start

### 1. Create the Macro

Save this file to `/agentpm/web/templates/macros/empty_state.html`:

```jinja2
{#
  Empty State Macro

  Renders a consistent empty state component with icon, heading, description, and optional CTA.

  Usage:
    {% from 'macros/empty_state.html' import render as empty_state %}

    {{ empty_state(
        icon='clipboard-check',
        heading='No work items found',
        description='Work items track features, bugs, and improvements. Create one to start planning.',
        cta_text='Create Work Item',
        cta_url='/work-items/create'
    ) }}

  Parameters:
    - icon (str): Bootstrap Icons name (without 'bi-' prefix) - default: 'inbox'
    - heading (str): Main heading text - default: 'No items found'
    - description (str): Explanatory text below heading - default: ''
    - cta_text (str, optional): Call-to-action button text - default: None
    - cta_url (str, optional): Call-to-action button URL - default: None
    - cta_icon (str, optional): Icon for CTA button - default: 'plus'
    - size (str): Size variant ('normal' or 'compact') - default: 'normal'
#}

{% macro render(
    icon='inbox',
    heading='No items found',
    description='',
    cta_text=None,
    cta_url=None,
    cta_icon='plus',
    size='normal'
) %}

{% set py_class = 'py-12' if size == 'normal' else 'py-8' %}
{% set icon_size = 'text-5xl' if size == 'normal' else 'text-4xl' %}
{% set icon_bg_size = 'w-24 h-24' if size == 'normal' else 'w-20 h-20' %}

<div class="text-center {{ py_class }}">
    <!-- Icon Container -->
    <div class="{{ icon_bg_size }} mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
        <i class="bi bi-{{ icon }} text-gray-400 {{ icon_size }}" aria-hidden="true"></i>
    </div>

    <!-- Heading -->
    <h3 class="text-lg font-medium text-gray-900 mb-2">{{ heading }}</h3>

    <!-- Description -->
    {% if description %}
    <p class="text-gray-500 mb-6">{{ description }}</p>
    {% endif %}

    <!-- Call to Action -->
    {% if cta_text and cta_url %}
    <a href="{{ cta_url }}" class="btn btn-primary">
        <i class="bi bi-{{ cta_icon }} mr-2"></i>
        {{ cta_text }}
    </a>
    {% endif %}
</div>

{% endmacro %}


{#
  Compact Empty State Macro

  Renders a minimal empty state for secondary views (inside tables, cards, etc.)

  Usage:
    {% from 'macros/empty_state.html' import compact as empty_state_compact %}

    {{ empty_state_compact(
        icon='info-circle',
        message='No agents configured for this project.',
        cta_text='Generate Agents',
        cta_url='/agents/generate'
    ) }}
#}

{% macro compact(
    icon='info-circle',
    message='No items found',
    cta_text=None,
    cta_url=None
) %}

<div class="px-6 py-12 text-center text-sm text-gray-500">
    <i class="bi bi-{{ icon }} text-lg text-gray-400" aria-hidden="true"></i>
    <p class="mt-2">{{ message }}</p>

    {% if cta_text and cta_url %}
    <a href="{{ cta_url }}" class="mt-4 inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition hover:bg-primary/20">
        <i class="bi bi-plus"></i>
        {{ cta_text }}
    </a>
    {% endif %}
</div>

{% endmacro %}


{#
  Filter-Aware Empty State

  Shows different message when filters are active vs no data exists.

  Usage:
    {% from 'macros/empty_state.html' import filter_aware %}

    {{ filter_aware(
        icon='search',
        no_results_heading='No results found',
        no_results_description='Try adjusting your search terms or filters.',
        no_data_heading='No work items yet',
        no_data_description='Create your first work item to get started.',
        has_filters=active_filters|length > 0,
        clear_filters_url='/work-items',
        cta_text='Create Work Item',
        cta_url='/work-items/create'
    ) }}
#}

{% macro filter_aware(
    icon='search',
    no_results_heading='No results found',
    no_results_description='Try adjusting your filters.',
    no_data_heading='No items yet',
    no_data_description='Get started by creating your first item.',
    has_filters=False,
    clear_filters_url=None,
    cta_text=None,
    cta_url=None
) %}

<div class="text-center py-12">
    <div class="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
        <i class="bi bi-{{ icon }} text-gray-400 text-5xl" aria-hidden="true"></i>
    </div>

    {% if has_filters %}
        <!-- Filtered State -->
        <h3 class="text-lg font-medium text-gray-900 mb-2">{{ no_results_heading }}</h3>
        <p class="text-gray-500 mb-6">{{ no_results_description }}</p>

        {% if clear_filters_url %}
        <a href="{{ clear_filters_url }}" class="btn btn-secondary">
            <i class="bi bi-x-circle mr-2"></i>
            Clear Filters
        </a>
        {% endif %}
    {% else %}
        <!-- Empty State -->
        <h3 class="text-lg font-medium text-gray-900 mb-2">{{ no_data_heading }}</h3>
        <p class="text-gray-500 mb-6">{{ no_data_description }}</p>

        {% if cta_text and cta_url %}
        <a href="{{ cta_url }}" class="btn btn-primary">
            <i class="bi bi-plus mr-2"></i>
            {{ cta_text }}
        </a>
        {% endif %}
    {% endif %}
</div>

{% endmacro %}
```

---

## 2. Icon Reference

### Recommended Icons by Route

| Route | Bootstrap Icon | Semantic Meaning |
|-------|----------------|------------------|
| Work Items | `clipboard-check` | Task tracking/completion |
| Tasks | `list-task` | Task list/checklist |
| Projects | `briefcase` | Project/work organization |
| Ideas | `lightbulb` | Brainstorming/creativity |
| Agents | `people` | Team/collaboration |
| Rules | `shield-check` | Governance/protection |
| Documents | `file-text` | Documentation |
| Evidence | `database` | Data/evidence storage |
| Sessions | `clock-history` | Time-based history |
| Contexts | `diagram-3` | Context/relationships |
| Search | `search` | Search functionality |
| No Project | `folder-x` | Missing folder/project |

### All Available Icons

See: https://icons.getbootstrap.com/

**Common Categories**:
- **Actions**: `plus`, `trash`, `pencil`, `download`, `upload`
- **Status**: `check-circle`, `x-circle`, `exclamation-triangle`, `info-circle`
- **Objects**: `inbox`, `archive`, `bookmark`, `calendar`, `envelope`
- **Navigation**: `arrow-left`, `arrow-right`, `chevron-down`, `house`

---

## 3. Usage Examples

### Example 1: Work Items List (Basic)

**File**: `agentpm/web/templates/work-items/list.html`

**Replace this**:
```jinja2
{% else %}
<div class="text-center py-12">
    <div class="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
        </svg>
    </div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">No work items found</h3>
    <p class="text-gray-500 mb-6">Get started by creating your first work item.</p>
    <a href="/work-items/create" class="btn btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Create Work Item
    </a>
</div>
{% endif %}
```

**With this**:
```jinja2
{% from 'macros/empty_state.html' import render as empty_state %}

{% else %}
{{ empty_state(
    icon='clipboard-check',
    heading='No work items found',
    description='Work items track features, bugs, and improvements. Create one to start planning.',
    cta_text='Create Work Item',
    cta_url='/work-items/create'
) }}
{% endif %}
```

**Lines of Code**: 18 → 10 (44% reduction)

---

### Example 2: Ideas List (Filter-Aware)

**File**: `agentpm/web/templates/ideas/list.html`

**Replace this**:
```jinja2
{% else %}
<div class="alert alert-info" role="alert">
    <i class="bi bi-info-circle"></i> No ideas match your filters.
    {% if current_status_filter or current_tag_filter %}
    <br><a href="/ideas" class="alert-link">Clear filters</a>
    {% else %}
    <br>Use <code>apm idea create "Title"</code> to capture ideas.
    {% endif %}
</div>
{% endif %}
```

**With this**:
```jinja2
{% from 'macros/empty_state.html' import filter_aware %}

{% else %}
{{ filter_aware(
    icon='lightbulb',
    no_results_heading='No ideas match your filters',
    no_results_description='Try adjusting your status or tag filters to see more results.',
    no_data_heading='No ideas yet',
    no_data_description='Ideas flow from brainstorming to research to conversion. Use <code>apm idea create "Title"</code> to capture your first idea.',
    has_filters=(current_status_filter or current_tag_filter),
    clear_filters_url='/ideas',
    cta_text='Create Idea (CLI)',
    cta_url='#'
) }}
{% endif %}
```

---

### Example 3: Agents List (Compact, Inline)

**File**: `agentpm/web/templates/agents/list.html`

**Replace this**:
```jinja2
{% else %}
<div class="px-6 py-12 text-center text-sm text-gray-500">
    <i class="bi bi-info-circle text-lg text-gray-400"></i>
    <p class="mt-2">No agents configured for this project.</p>
    <button class="mt-4 inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition hover:bg-primary/20"
            hx-get="/agents/generate-form"
            hx-target="#generate-modal-content"
            onclick="openAgentModal()">
      <i class="bi bi-magic"></i>
      Generate Agents Now
    </button>
</div>
{% endif %}
```

**With this** (note: keep button attributes for HTMX):
```jinja2
{% from 'macros/empty_state.html' import compact as empty_state_compact %}

{% else %}
<div class="px-6 py-12 text-center text-sm text-gray-500">
    <i class="bi bi-people text-lg text-gray-400" aria-hidden="true"></i>
    <p class="mt-2">No agents configured for this project.</p>
    <button class="mt-4 inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition hover:bg-primary/20"
            hx-get="/agents/generate-form"
            hx-target="#generate-modal-content"
            onclick="openAgentModal()">
      <i class="bi bi-magic"></i>
      Generate Agents Now
    </button>
</div>
{% endif %}
```

**Note**: For complex CTAs (HTMX, modal triggers), keep custom markup but use macro for icon + message structure.

---

### Example 4: Rules List (New Empty State)

**File**: `agentpm/web/templates/rules_list.html`

**Replace this**:
```jinja2
{% else %}
<div class="alert alert-info" role="alert">
    No rules configured for this project.
</div>
{% endif %}
```

**With this**:
```jinja2
{% from 'macros/empty_state.html' import render as empty_state %}

{% else %}
{{ empty_state(
    icon='shield-check',
    heading='No rules loaded',
    description='Rules are loaded from the database. Run <code>apm init</code> to populate default rules, or check the documentation for custom rule creation.',
    cta_text='View Documentation',
    cta_url='/docs/rules'
) }}
{% endif %}
```

---

### Example 5: Evidence List (Enhanced)

**File**: `agentpm/web/templates/evidence/list.html`

**Replace this**:
```jinja2
{% else %}
<div class="px-6 py-12 text-center text-sm text-gray-500">
    <i class="bi bi-info-circle text-lg text-gray-400"></i>
    <p class="mt-2">No evidence sources found. Adjust filters or ingest new evidence via the workflow.</p>
</div>
{% endif %}
```

**With this**:
```jinja2
{% from 'macros/empty_state.html' import compact as empty_state_compact %}

{% else %}
{{ empty_state_compact(
    icon='database',
    message='No evidence sources found. Adjust filters or ingest new evidence via <code>apm evidence add</code>.'
) }}
{% endif %}
```

---

## 4. Migration Checklist

For each route being migrated, complete these steps:

### Pre-Migration
- [ ] Identify current empty state pattern (A, B, C, or D)
- [ ] Note icon used (if any)
- [ ] Note CTA text and URL
- [ ] Check if filter-aware logic exists

### During Migration
- [ ] Import macro at top of template: `{% from 'macros/empty_state.html' import render as empty_state %}`
- [ ] Replace empty state HTML with macro call
- [ ] Choose appropriate icon from Bootstrap Icons
- [ ] Update description text (add value prop if needed)
- [ ] Test CTA link works correctly
- [ ] Add ARIA attributes (`aria-hidden="true"` on icon) - **Already in macro**

### Post-Migration
- [ ] Visual QA (compare before/after screenshots)
- [ ] Test on mobile (375px), tablet (768px), desktop (1440px)
- [ ] Test keyboard navigation (Tab to CTA, Enter to activate)
- [ ] Test with filters active (if filter-aware)
- [ ] Update test snapshots (if visual regression tests exist)

---

## 5. Route-Specific Migration Plan

### Priority 1: Pattern A Routes (High Impact, Easy)

| Route | File | Effort | Notes |
|-------|------|--------|-------|
| `/work-items` | `work-items/list.html:225-239` | 15 min | Replace SVG with `clipboard-check` |
| `/tasks` | `tasks/list.html:256-270` | 15 min | Replace SVG with `list-task` |
| `/projects` | `projects/list.html:229-243` | 15 min | Replace SVG with `briefcase` |
| `/search` (no results) | `search/results.html:189-209` | 20 min | Keep suggestions logic, use `filter_aware` macro |

**Subtotal**: 1 hour 5 minutes

---

### Priority 2: Pattern C Routes (Legacy Bootstrap)

| Route | File | Effort | Notes |
|-------|------|--------|-------|
| `/ideas` | `ideas/list.html:164-171` | 25 min | Use `filter_aware` macro for filter/no-data states |
| `/rules` | `rules_list.html:105-107` | 20 min | Add `shield-check` icon, update description |
| `/sessions` | `sessions/list.html:194-201` | 20 min | Use `filter_aware` for filter state |
| `/contexts` | `contexts/list.html:160-167` | 20 min | Keep CLI command in description, add `diagram-3` icon |

**Subtotal**: 1 hour 25 minutes

---

### Priority 3: Pattern B Routes (Compact)

| Route | File | Effort | Notes |
|-------|------|--------|-------|
| `/evidence` | `evidence/list.html:149-152` | 15 min | Use `compact` macro, upgrade icon to `database` |
| `/documents` | `documents/list.html:170-176` | 15 min | Keep CLI guidance, use `compact` macro |

**Subtotal**: 30 minutes

---

### Total Migration Effort: 3 hours

---

## 6. Testing Guide

### Manual Testing Checklist

For each migrated route:

1. **Visual Inspection**
   - [ ] Icon displays correctly (size, color, centering)
   - [ ] Heading is legible (text-lg, gray-900, centered)
   - [ ] Description is readable (text-gray-500, max-width reasonable)
   - [ ] CTA button styled correctly (btn btn-primary)
   - [ ] Spacing looks balanced (py-12 provides enough whitespace)

2. **Responsive Testing**
   - [ ] Mobile (375px): Icon/text stacks vertically, no overflow
   - [ ] Tablet (768px): Layout remains centered
   - [ ] Desktop (1440px): Content doesn't stretch too wide

3. **Keyboard Navigation**
   - [ ] Tab to CTA button (should have visible focus ring)
   - [ ] Enter on CTA activates link

4. **Screen Reader Testing** (if available)
   - [ ] Reads heading first
   - [ ] Reads description
   - [ ] Icon is skipped (aria-hidden="true")
   - [ ] CTA button text is clear

5. **Filter-Aware Testing** (if applicable)
   - [ ] With filters: Shows "No results found" + "Clear Filters" button
   - [ ] Without filters: Shows "No items yet" + "Create" button

---

### Automated Testing

**Visual Regression** (Playwright/Cypress):

```javascript
// Example Playwright test
test('work items empty state displays correctly', async ({ page }) => {
  // Navigate to empty work items page
  await page.goto('/work-items?status=archived'); // Ensure empty

  // Check empty state elements
  await expect(page.locator('h3')).toContainText('No work items found');
  await expect(page.locator('.bi-clipboard-check')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Create Work Item' })).toBeVisible();

  // Screenshot for visual regression
  await expect(page).toHaveScreenshot('work-items-empty-state.png');
});
```

**Accessibility Testing** (axe-core):

```javascript
test('work items empty state is accessible', async ({ page }) => {
  await page.goto('/work-items?status=archived');

  const results = await injectAxe(page);
  expect(results.violations).toHaveLength(0);

  // Check specific ARIA attributes
  const icon = page.locator('.bi-clipboard-check');
  await expect(icon).toHaveAttribute('aria-hidden', 'true');
});
```

---

## 7. Troubleshooting

### Issue: Macro not found

**Error**: `TemplateNotFound: macros/empty_state.html`

**Solution**:
- Ensure file is saved to `agentpm/web/templates/macros/empty_state.html`
- Check import path: `{% from 'macros/empty_state.html' import render as empty_state %}`
- Restart Flask dev server (may need to clear template cache)

---

### Issue: Icon not displaying

**Error**: Icon shows as square or missing

**Solution**:
- Ensure Bootstrap Icons CSS is loaded in base template:
  ```html
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  ```
- Check icon name is correct (without `bi-` prefix in macro parameter)
- Verify icon exists: https://icons.getbootstrap.com/

---

### Issue: Layout breaks on mobile

**Symptom**: Text overflows, icon too large, layout not centered

**Solution**:
- Check `py-12` class is present (provides vertical spacing)
- Ensure parent container has no fixed width
- Test with actual device or Chrome DevTools mobile emulation
- Verify Tailwind CSS is loaded and purge config includes template paths

---

### Issue: CTA button not working

**Symptom**: Button displays but doesn't navigate

**Solution**:
- Check `cta_url` parameter is correct (absolute or relative path)
- Verify route exists in Flask app
- Test with `<a>` tag (macro uses link, not button)
- For HTMX/Alpine.js CTAs, keep custom markup (don't use macro CTA)

---

## 8. Performance Considerations

### Macro vs. Inline HTML

**Pros of Macro**:
- ✅ Consistency (one source of truth)
- ✅ Maintainability (change once, affects all)
- ✅ DRY (no code duplication)

**Cons of Macro**:
- ⚠️ Slight template rendering overhead (negligible in practice)
- ⚠️ Requires import statement in each template

**Verdict**: **Use macro**. Benefits far outweigh minor overhead.

---

### Template Caching

Jinja2 templates are cached by default in production. Empty states are rendered server-side, so no client-side performance impact.

**Best Practice**: Use macro for all standard empty states. Only use inline HTML for complex cases (modals, HTMX-heavy interactions).

---

## 9. Future Enhancements

### Phase 3 Ideas (Post-Migration)

1. **Animated Empty States**
   - Add CSS fade-in animation on page load
   - Use Alpine.js for smooth transitions when filters change

2. **Contextual Illustrations**
   - Replace icons with custom SVG illustrations (like Undraw.co)
   - Match illustration to empty state type (e.g., person holding clipboard for work items)

3. **Smart Suggestions**
   - Use backend logic to suggest related items ("You have 3 similar work items")
   - Show recent items in empty state ("Or view recently archived items")

4. **Onboarding Overlays**
   - First-time users get guided tour ("Let's create your first work item!")
   - Track onboarding progress in user session

5. **Empty State Analytics**
   - Track how often users see empty states
   - Measure CTA click-through rate
   - A/B test different messaging

---

## 10. Maintenance

### When to Update Macro

Update `macros/empty_state.html` when:
- Design system changes (new colors, spacing, or typography)
- Accessibility improvements needed (new ARIA patterns)
- New empty state variants required (e.g., "loading" state)

### When to Add Custom Empty State

Use custom HTML (not macro) when:
- Complex interactive elements needed (HTMX, Alpine.js)
- Unique layout required (e.g., multi-column empty state)
- A/B testing different designs

Always document custom implementations in this guide.

---

## 11. Acceptance Criteria

This implementation is complete when:

- [x] Macro file created (`macros/empty_state.html`)
- [ ] All Pattern A routes migrated (4 routes)
- [ ] All Pattern C routes migrated (4 routes)
- [ ] All Pattern B routes enhanced (2 routes)
- [ ] Visual QA passed (screenshots match design)
- [ ] Responsive testing passed (mobile, tablet, desktop)
- [ ] Accessibility testing passed (axe-core, keyboard nav)
- [ ] Documentation updated (this guide + design system)
- [ ] Team review completed

---

## 12. Rollout Plan

### Week 1: Foundation
- [ ] Create macro file
- [ ] Test macro in isolation (create test page)
- [ ] Migrate 2 Pattern A routes (work items, tasks)
- [ ] QA and iterate

### Week 2: Expansion
- [ ] Migrate remaining Pattern A routes (projects, search)
- [ ] Migrate 2 Pattern C routes (ideas, rules)
- [ ] QA and iterate

### Week 3: Completion
- [ ] Migrate remaining routes (sessions, contexts, evidence, documents)
- [ ] Full regression testing
- [ ] Documentation updates
- [ ] Team training (if needed)

**Total Timeline**: 3 weeks (15-20 hours of development)

---

**Author**: flask-ux-designer agent
**Last Updated**: 2025-10-22
**Status**: Ready for Implementation
