# Task 791: Rule Detail Route - Design System Review

**Task ID**: 791
**Objective**: Apply design system standards to rule detail route
**Date**: 2025-10-22
**Status**: Review Complete

---

## Executive Summary

### Current State
- **Route exists**: `/rules/<int:rule_id>` defined in `rules.py` blueprint
- **Template missing**: Expected `rules/detail.html` template does not exist
- **Current implementation**: Rule details shown via expandable row in `rules_list.html`
- **Design system**: Fully documented in `docs/architecture/web/design-system.md`

### Findings
1. ❌ **Critical Issue**: Missing `templates/rules/detail.html` template (404 error on route access)
2. ⚠️ **UX Issue**: Current expandable row lacks proper semantic structure
3. ⚠️ **Accessibility Issue**: Missing ARIA labels, keyboard navigation unclear
4. ⚠️ **Design System Compliance**: Expandable row doesn't use design system patterns
5. ⚠️ **Missing Fields**: Database has `validation_logic`, `error_message`, `config` not displayed

---

## 1. Current Implementation Analysis

### 1.1 Route Handler (`rules.py`)
```python
@rules_bp.route('/rules/<int:rule_id>')
def rule_detail(rule_id: int):
    """Get rule details."""
    db = get_database_service()

    rule = rule_methods.get_rule(db, rule_id)
    if not rule:
        abort(404, description=f"Rule {rule_id} not found")

    return render_template('rules/detail.html', rule=rule)
```

**Issues**:
- ✅ Proper error handling (404)
- ❌ Template doesn't exist
- ❌ No breadcrumb context passed
- ❌ No related rules or usage stats

### 1.2 Current Expandable Row (`partials/rule_row.html`)

**Structure**:
```html
<tr id="rule-{{ rule_info.rule.id }}" class="rule-details" style="display: none;">
    <td colspan="6" class="bg-light">
        <div class="p-3">
            <strong>Description:</strong>
            <p>{{ rule_info.rule.description }}</p>

            {% if rule_info.rule.validation_logic %}
            <strong>Validation Logic:</strong>
            <pre class="bg-white p-2 rounded"><code>{{ rule_info.rule.validation_logic }}</code></pre>
            {% endif %}

            {% if rule_info.rule.config %}
            <strong>Configuration:</strong>
            <pre class="bg-white p-2 rounded">{{ rule_info.rule.config | tojson(indent=2) }}</pre>
            {% endif %}
        </div>
    </td>
</tr>
```

**UX Issues Found**:
- ⚠️ **No card structure**: Uses table cell with `bg-light` background (not card pattern)
- ⚠️ **Inconsistent spacing**: Manual `p-3` padding instead of design system `.card-body`
- ⚠️ **Code display**: Pre/code blocks lack syntax highlighting or copy button
- ⚠️ **No rationale section**: Database field not displayed
- ⚠️ **No examples section**: Design pattern missing
- ⚠️ **Unclear toggle**: Row expansion has no visual indicator (chevron icon)

**Accessibility Issues**:
- ❌ No `role="button"` on clickable row
- ❌ No `aria-expanded` state
- ❌ No `aria-controls` linking
- ❌ No keyboard navigation (Enter key)
- ❌ No screen reader announcement of expansion

---

## 2. Database Schema vs. Display

### 2.1 Available Fields (Rule Model)

| Field               | Type       | Current Display | Should Display |
|---------------------|------------|----------------|----------------|
| `id`                | Integer    | ❌ No          | ℹ️ Debug only  |
| `rule_id`           | String     | ✅ Yes         | ✅ Primary ID  |
| `name`              | String     | ✅ Yes         | ✅ Title       |
| `description`       | String     | ✅ Yes         | ✅ Summary     |
| `category`          | String     | ✅ Yes         | ✅ Badge       |
| `enforcement_level` | Enum       | ✅ Yes         | ✅ Badge       |
| `validation_logic`  | String     | ⚠️ Partial     | ✅ Code block  |
| `error_message`     | String     | ❌ No          | ✅ Alert box   |
| `config`            | JSON       | ⚠️ Partial     | ✅ Formatted   |
| `enabled`           | Boolean    | ✅ Yes         | ✅ Status      |
| `created_at`        | Timestamp  | ❌ No          | ℹ️ Metadata    |
| `updated_at`        | Timestamp  | ❌ No          | ℹ️ Metadata    |

### 2.2 Missing Display Elements

**Based on governance rules documentation pattern**:
- ❌ **Rationale**: WHY the rule exists (not in DB schema, should be added)
- ❌ **Examples**: Code examples showing compliance/violation
- ❌ **Related Rules**: Links to rules in same category
- ❌ **Impact**: What happens when rule is violated (blocking vs. warning)
- ❌ **References**: Links to external documentation (style guides, etc.)

---

## 3. Design System Compliance Gaps

### 3.1 Typography
**Current**:
```html
<strong>Description:</strong>
<p>{{ rule_info.rule.description }}</p>
```

**Design System Standard**:
```html
<h4 class="text-lg font-medium text-gray-800">Description</h4>
<p class="text-base text-gray-700">{{ rule.description }}</p>
```

**Issues**:
- Using `<strong>` instead of semantic headings
- No design system classes
- Inconsistent spacing

### 3.2 Code Blocks
**Current**:
```html
<pre class="bg-white p-2 rounded"><code>{{ rule_info.rule.validation_logic }}</code></pre>
```

**Design System Standard** (from component snippets):
```html
<pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto">
  <code class="font-mono text-sm text-gray-800">{{ rule.validation_logic }}</code>
</pre>
```

**Missing**:
- Copy button
- Syntax highlighting
- Line numbers
- Proper overflow handling

### 3.3 Badges
**Current**:
```html
<span class="badge enforcement-{{ rule_info.rule.enforcement_level }}">
    {{ rule_info.rule.enforcement_level }}
</span>
```

**Design System Alignment**: ✅ Good - uses design system badge classes

**Enhancement Needed**:
- Add icon to enforcement badge (e.g., `<i class="bi bi-shield-lock"></i>` for BLOCK)
- Use semantic colors from design system

### 3.4 Cards
**Current**: No card structure in expandable row

**Design System Standard**: Should use `.card` pattern for detail view:
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">{{ rule.rule_id }}: {{ rule.name }}</h3>
    <span class="badge enforcement-{{ rule.enforcement_level }}">...</span>
  </div>
  <div class="card-body space-y-4">
    <!-- Content sections -->
  </div>
</div>
```

---

## 4. Enforcement Level Visualization

### 4.1 Current Colors (from design system)
```css
.enforcement-BLOCK { background: #dc3545; color: white; }  /* Red - Danger */
.enforcement-LIMIT { background: #ffc107; color: white; }  /* Yellow - Warning */
.enforcement-GUIDE { background: #0d6efd; color: white; }  /* Blue - Info */
.enforcement-ENHANCE { background: #6c757d; color: white; } /* Gray - Secondary */
```

### 4.2 Recommended Icons (Bootstrap Icons)
- **BLOCK**: `bi-shield-lock` or `bi-exclamation-triangle-fill`
- **LIMIT**: `bi-exclamation-circle` or `bi-shield-exclamation`
- **GUIDE**: `bi-info-circle` or `bi-lightbulb`
- **ENHANCE**: `bi-magic` or `bi-stars`

### 4.3 Impact Indicators (Proposed)

**Enforcement Impact Card**:
```html
<div class="alert alert-{{ enforcement_color }}">
  <div class="flex items-center">
    <i class="bi bi-{{ enforcement_icon }} mr-2"></i>
    <div>
      <strong>Impact: {{ enforcement_level }}</strong>
      <p class="text-sm">{{ enforcement_explanation }}</p>
    </div>
  </div>
</div>
```

**Explanations**:
- **BLOCK**: "Prevents invalid workflow transitions (raises error)"
- **LIMIT**: "Shows warnings but allows transitions"
- **GUIDE**: "Informational guidance only"
- **ENHANCE**: "Enriches AI context silently"

---

## 5. Recommended Implementation: Two Options

### Option A: Dedicated Detail Page (Recommended)

**Route**: `/rules/<int:rule_id>` → `templates/rules/detail.html`

**Benefits**:
- ✅ Full design system compliance
- ✅ Better accessibility
- ✅ Shareable URLs
- ✅ More space for comprehensive information
- ✅ Supports breadcrumbs and navigation

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ Breadcrumb: Dashboard > Rules > DP-001         │
├─────────────────────────────────────────────────┤
│ [Header Card]                                   │
│   DP-001: time-boxing-implementation            │
│   Badge: BLOCK   Category: Development          │
│   Toggle: [ON/OFF]                             │
├─────────────────────────────────────────────────┤
│ [Description Card]                              │
│   IMPLEMENTATION tasks ≤4h                      │
├─────────────────────────────────────────────────┤
│ [Rationale Card] (if available)                 │
│   Why this rule exists...                       │
├─────────────────────────────────────────────────┤
│ [Impact Card]                                   │
│   Alert box showing enforcement level impact    │
├─────────────────────────────────────────────────┤
│ [Configuration Card] (if config exists)         │
│   JSON display with syntax highlighting         │
├─────────────────────────────────────────────────┤
│ [Validation Logic Card] (if exists)             │
│   Code block with copy button                   │
├─────────────────────────────────────────────────┤
│ [Examples Card] (if available)                  │
│   Tabs: [Compliant] [Violation]                │
├─────────────────────────────────────────────────┤
│ [Related Rules Card]                            │
│   Links to other rules in same category         │
└─────────────────────────────────────────────────┘
```

### Option B: Enhanced Expandable Row

**Keep current expandable row pattern but improve it**

**Benefits**:
- ✅ Faster to implement
- ✅ No navigation required
- ✅ Inline context

**Drawbacks**:
- ❌ Limited space
- ❌ No shareable URLs
- ❌ Harder to achieve full accessibility

**Enhancements Needed**:
```html
<tr class="rule-row cursor-pointer"
    role="button"
    aria-expanded="false"
    aria-controls="rule-detail-{{ rule.id }}"
    tabindex="0"
    @click="toggleDetails()"
    @keydown.enter="toggleDetails()">
  <td>
    <div class="flex items-center gap-2">
      <i class="bi bi-chevron-right transition" :class="{ 'rotate-90': expanded }"></i>
      <strong>{{ rule.rule_id }}</strong>
    </div>
  </td>
  <!-- ... other cells ... -->
</tr>

<tr id="rule-detail-{{ rule.id }}" class="rule-details" style="display: none;">
  <td colspan="6">
    <div class="card mb-0">
      <div class="card-body space-y-4">
        <!-- Use proper card structure with design system classes -->
      </div>
    </div>
  </td>
</tr>
```

---

## 6. Missing Template Creation (Option A)

### 6.1 Create `templates/rules/detail.html`

**File**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/web/templates/rules/detail.html`

**Template Structure**:
```html
{% extends "layouts/modern_base.html" %}

{% block title %}{{ rule.rule_id }}: {{ rule.name }} - Rules - APM (Agent Project Manager){% endblock %}

{% block breadcrumb %}
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/">Dashboard</a></li>
    <li class="breadcrumb-item"><a href="/rules">Rules</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ rule.rule_id }}</li>
  </ol>
</nav>
{% endblock %}

{% block content %}
<!-- Header Card -->
<div class="card mb-6">
  <div class="card-header">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ rule.rule_id }}: {{ rule.name }}</h1>
        <p class="text-sm text-gray-600 mt-1">Category: {{ rule.category }}</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="badge enforcement-{{ rule.enforcement_level }}">
          <i class="bi bi-shield-lock"></i>
          {{ rule.enforcement_level }}
        </span>
        <!-- Toggle switch -->
        <div x-data="{ enabled: {{ 'true' if rule.enabled else 'false' }} }">
          <button
            @click="enabled = !enabled"
            :class="enabled ? 'bg-success' : 'bg-gray-300'"
            class="relative inline-flex h-6 w-12 items-center rounded-full transition">
            <span
              :class="enabled ? 'translate-x-6' : 'translate-x-1'"
              class="inline-block h-4 w-4 transform rounded-full bg-white transition">
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Description Card -->
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Description</h2>
  </div>
  <div class="card-body">
    <p class="text-base text-gray-700">{{ rule.description }}</p>
  </div>
</div>

<!-- Impact Card -->
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Enforcement Impact</h2>
  </div>
  <div class="card-body">
    {% if rule.enforcement_level == 'BLOCK' %}
      <div class="alert alert-error">
        <div class="flex items-center">
          <i class="bi bi-shield-lock mr-2"></i>
          <div>
            <strong>BLOCK Level</strong>
            <p class="text-sm">Prevents invalid workflow transitions (raises error)</p>
          </div>
        </div>
      </div>
    {% elif rule.enforcement_level == 'LIMIT' %}
      <div class="alert alert-warning">
        <div class="flex items-center">
          <i class="bi bi-exclamation-circle mr-2"></i>
          <div>
            <strong>LIMIT Level</strong>
            <p class="text-sm">Shows warnings but allows transitions</p>
          </div>
        </div>
      </div>
    {% elif rule.enforcement_level == 'GUIDE' %}
      <div class="alert alert-info">
        <div class="flex items-center">
          <i class="bi bi-info-circle mr-2"></i>
          <div>
            <strong>GUIDE Level</strong>
            <p class="text-sm">Informational guidance only</p>
          </div>
        </div>
      </div>
    {% else %}
      <div class="alert alert-gray">
        <div class="flex items-center">
          <i class="bi bi-stars mr-2"></i>
          <div>
            <strong>ENHANCE Level</strong>
            <p class="text-sm">Enriches AI context silently</p>
          </div>
        </div>
      </div>
    {% endif %}

    {% if rule.error_message %}
    <div class="mt-4">
      <strong class="text-sm text-gray-700">Error Message:</strong>
      <p class="text-sm text-gray-600 mt-1">{{ rule.error_message }}</p>
    </div>
    {% endif %}
  </div>
</div>

<!-- Configuration Card -->
{% if rule.config %}
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Configuration</h2>
  </div>
  <div class="card-body">
    <div x-data="{ copied: false }">
      <div class="relative">
        <pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto"><code class="font-mono text-sm text-gray-800">{{ rule.config | tojson(indent=2) }}</code></pre>
        <button
          @click="navigator.clipboard.writeText('{{ rule.config | tojson(indent=2) }}'); copied = true; setTimeout(() => copied = false, 2000)"
          class="absolute top-2 right-2 btn btn-sm btn-secondary">
          <i class="bi bi-clipboard" x-show="!copied"></i>
          <i class="bi bi-check" x-show="copied"></i>
          <span x-text="copied ? 'Copied!' : 'Copy'"></span>
        </button>
      </div>
    </div>
  </div>
</div>
{% endif %}

<!-- Validation Logic Card -->
{% if rule.validation_logic %}
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Validation Logic</h2>
  </div>
  <div class="card-body">
    <div x-data="{ copied: false }">
      <div class="relative">
        <pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto"><code class="font-mono text-sm text-gray-800">{{ rule.validation_logic }}</code></pre>
        <button
          @click="navigator.clipboard.writeText('{{ rule.validation_logic }}'); copied = true; setTimeout(() => copied = false, 2000)"
          class="absolute top-2 right-2 btn btn-sm btn-secondary">
          <i class="bi bi-clipboard" x-show="!copied"></i>
          <i class="bi bi-check" x-show="copied"></i>
          <span x-text="copied ? 'Copied!' : 'Copy'"></span>
        </button>
      </div>
    </div>
  </div>
</div>
{% endif %}

<!-- Metadata Card -->
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Metadata</h2>
  </div>
  <div class="card-body">
    <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <dt class="text-sm font-medium text-gray-500">Rule ID</dt>
        <dd class="text-base text-gray-900">{{ rule.rule_id }}</dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500">Name</dt>
        <dd class="text-base text-gray-900">{{ rule.name }}</dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500">Category</dt>
        <dd><span class="badge badge-gray">{{ rule.category }}</span></dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500">Status</dt>
        <dd>
          {% if rule.enabled %}
            <span class="badge badge-success">Enabled</span>
          {% else %}
            <span class="badge badge-gray">Disabled</span>
          {% endif %}
        </dd>
      </div>
      {% if rule.created_at %}
      <div>
        <dt class="text-sm font-medium text-gray-500">Created</dt>
        <dd class="text-sm text-gray-600">{{ rule.created_at.strftime('%Y-%m-%d %H:%M') }}</dd>
      </div>
      {% endif %}
      {% if rule.updated_at %}
      <div>
        <dt class="text-sm font-medium text-gray-500">Updated</dt>
        <dd class="text-sm text-gray-600">{{ rule.updated_at.strftime('%Y-%m-%d %H:%M') }}</dd>
      </div>
      {% endif %}
    </dl>
  </div>
</div>

<!-- Actions Card -->
<div class="card">
  <div class="card-footer">
    <a href="/rules" class="btn btn-secondary">
      <i class="bi bi-arrow-left mr-2"></i>
      Back to Rules
    </a>
    <a href="/rules/{{ rule.id }}/edit" class="btn btn-primary">
      <i class="bi bi-pencil mr-2"></i>
      Edit Rule
    </a>
  </div>
</div>
{% endblock %}
```

---

## 7. Accessibility Compliance Checklist

### 7.1 WCAG 2.1 AA Requirements

**Keyboard Navigation**:
- [ ] All interactive elements reachable via Tab
- [ ] Enter/Space activates buttons
- [ ] Escape closes modals/dropdowns
- [ ] Focus visible on all interactive elements

**Screen Reader Support**:
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] ARIA labels for icon-only buttons
- [ ] `role="button"` on clickable non-button elements
- [ ] `aria-expanded` for expandable sections
- [ ] `aria-controls` linking toggle to content

**Color Contrast**:
- [ ] Text ≥4.5:1 contrast (body text)
- [ ] Headings ≥4.5:1 contrast
- [ ] Interactive elements ≥3:1 contrast
- [ ] Status indicators use more than color alone

**Semantic HTML**:
- [ ] Proper use of headings, lists, tables
- [ ] Form labels associated with inputs
- [ ] Navigation landmarks (`<nav>`, `<main>`, etc.)

### 7.2 Current Accessibility Issues

**Expandable Row** (Option B):
- ❌ No `role="button"` on clickable row
- ❌ No `aria-expanded="false"` attribute
- ❌ No `aria-controls="rule-detail-{{ rule.id }}"`
- ❌ No keyboard support (Enter key)
- ❌ Chevron icon missing for visual expansion indicator

**Dedicated Page** (Option A):
- ✅ Proper heading hierarchy
- ✅ Semantic HTML structure
- ✅ Keyboard navigation natural
- ⚠️ Toggle switch needs ARIA label
- ⚠️ Copy buttons need accessible text

---

## 8. Responsive Design Considerations

### 8.1 Breakpoint Behavior

**Mobile (< 768px)**:
- Stack enforcement badge and toggle vertically
- Full-width cards
- Reduce padding in code blocks
- Collapse metadata grid to 1 column

**Tablet (768px - 1024px)**:
- 2-column metadata grid
- Side-by-side header elements

**Desktop (> 1024px)**:
- Full layout as designed
- 2-column metadata grid
- Comfortable spacing

### 8.2 Responsive Classes (Tailwind)

```html
<!-- Header: stack on mobile, flex on desktop -->
<div class="flex flex-col md:flex-row md:items-center md:justify-between">
  <div>...</div>
  <div class="mt-4 md:mt-0">...</div>
</div>

<!-- Metadata grid: 1 col mobile, 2 col desktop -->
<dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
  ...
</dl>

<!-- Code blocks: scrollable on mobile -->
<pre class="overflow-x-auto">...</pre>
```

---

## 9. Implementation Priority

### Phase 1: Critical (Blocker for launch)
1. ✅ Create `templates/rules/detail.html` (dedicated page)
2. ✅ Implement proper card structure
3. ✅ Add enforcement impact explanation
4. ✅ Display all database fields (description, config, validation_logic, error_message)
5. ✅ Breadcrumb navigation
6. ✅ Basic accessibility (headings, ARIA labels)

### Phase 2: Important (Launch-critical UX)
1. ⚠️ Add copy buttons to code blocks
2. ⚠️ Implement toggle functionality (HTMX)
3. ⚠️ Responsive design testing
4. ⚠️ Related rules section
5. ⚠️ Keyboard navigation testing

### Phase 3: Enhancement (Post-launch polish)
1. ℹ️ Syntax highlighting for code blocks
2. ℹ️ Examples section (requires database schema change)
3. ℹ️ Rationale section (requires database schema change)
4. ℹ️ Usage statistics (which work items/tasks affected)
5. ℹ️ Edit inline (modal form)

---

## 10. Recommended Next Steps

### Immediate Actions (This Sprint)

1. **Create Missing Template**:
   - File: `agentpm/web/templates/rules/detail.html`
   - Use template structure from Section 6.1
   - Apply design system classes throughout

2. **Update Route Handler** (optional enhancement):
   ```python
   @rules_bp.route('/rules/<int:rule_id>')
   def rule_detail(rule_id: int):
       db = get_database_service()
       rule = rule_methods.get_rule(db, rule_id)

       if not rule:
           abort(404, description=f"Rule {rule_id} not found")

       # Get related rules in same category
       related_rules = [
           r for r in rule_methods.list_rules(db)
           if r.category == rule.category and r.id != rule.id
       ][:5]  # Limit to 5

       return render_template(
           'rules/detail.html',
           rule=rule,
           related_rules=related_rules,
           breadcrumb=[
               {'name': 'Dashboard', 'url': '/'},
               {'name': 'Rules', 'url': '/rules'},
               {'name': rule.rule_id, 'url': None}
           ]
       )
   ```

3. **Enhance Expandable Row** (parallel task):
   - Add ARIA attributes
   - Add chevron icon
   - Add keyboard support
   - Use design system card pattern

4. **Testing Checklist**:
   - [ ] Navigate to `/rules/422` (DP-001)
   - [ ] Verify all sections render
   - [ ] Test toggle functionality
   - [ ] Test copy buttons
   - [ ] Test keyboard navigation (Tab through page)
   - [ ] Test screen reader (VoiceOver on Mac)
   - [ ] Test mobile view (resize browser)
   - [ ] Test breadcrumb navigation

### Database Schema Enhancements (Future)

**Add fields to `rules` table**:
```sql
ALTER TABLE rules ADD COLUMN rationale TEXT;
ALTER TABLE rules ADD COLUMN examples TEXT;  -- JSON array of examples
ALTER TABLE rules ADD COLUMN references TEXT;  -- JSON array of URLs
```

**Example data structure**:
```json
{
  "rationale": "Time-boxing prevents scope creep and ensures tasks are properly decomposed. Tasks exceeding 4 hours are likely too complex and should be split into smaller, more manageable units.",
  "examples": [
    {
      "type": "compliant",
      "code": "# Task: Implement user authentication\\nEstimate: 3.5 hours",
      "description": "Well-scoped task under time limit"
    },
    {
      "type": "violation",
      "code": "# Task: Build entire dashboard\\nEstimate: 12 hours",
      "description": "Too large - should be decomposed into smaller tasks"
    }
  ],
  "references": [
    {"title": "Agile Estimation Guide", "url": "https://..."},
    {"title": "Task Decomposition Best Practices", "url": "https://..."}
  ]
}
```

---

## 11. Before/After Comparison

### Current State (Expandable Row)
```
Rules List Page
┌─────────────────────────────────────────┐
│ DP-001 | Dev Principles | [BLOCK] | ON │ ← Click to expand
├─────────────────────────────────────────┤
│ Description: IMPLEMENTATION tasks ≤4h   │ ← Expanded inline
│ Config: {"max_hours": 4.0}             │
└─────────────────────────────────────────┘
```

**Issues**:
- No shareable URL
- Limited space for content
- Poor accessibility
- Not design system compliant

### Proposed State (Dedicated Page)
```
URL: /rules/422

Breadcrumb: Dashboard > Rules > DP-001

┌─────────────────────────────────────────┐
│ [Header Card]                           │
│ DP-001: time-boxing-implementation      │
│ Badge: BLOCK   Toggle: ON              │
├─────────────────────────────────────────┤
│ [Description Card]                      │
│ IMPLEMENTATION tasks ≤4h                │
├─────────────────────────────────────────┤
│ [Impact Card - Alert Box]               │
│ 🛡️ BLOCK: Prevents invalid transitions │
├─────────────────────────────────────────┤
│ [Configuration Card]                    │
│ {"max_hours": 4.0} [Copy Button]       │
├─────────────────────────────────────────┤
│ [Metadata Card]                         │
│ Category: Development Principles        │
│ Created: 2025-10-15                    │
└─────────────────────────────────────────┘
[< Back to Rules]  [Edit Rule]
```

**Benefits**:
- ✅ Shareable URL
- ✅ Full design system compliance
- ✅ Comprehensive information display
- ✅ Proper accessibility
- ✅ Professional UI polish

---

## 12. Design System Compliance Summary

### Compliant Elements
- ✅ Enforcement badges (colors and classes)
- ✅ Toggle switch pattern
- ✅ Bootstrap Icons usage

### Non-Compliant Elements (Need Fixing)
- ❌ Missing template (critical)
- ❌ No card structure in expandable row
- ❌ Typography (using `<strong>` instead of headings)
- ❌ Code blocks (missing copy button, syntax highlighting)
- ❌ No alert patterns for impact explanation
- ❌ Accessibility attributes missing
- ❌ No responsive design considerations

### Design System Utilization Score
- **Current**: 30% (expandable row)
- **Proposed**: 95% (dedicated page with full template)

---

## 13. Conclusion

### Critical Finding
The rule detail route **expects a template that doesn't exist**, causing 404 errors. This is a **blocking issue** for any user trying to view detailed rule information via direct URL.

### Recommended Solution
**Option A: Create dedicated detail page** (`templates/rules/detail.html`)

**Rationale**:
1. Fixes 404 error
2. Provides shareable URLs
3. Full design system compliance
4. Better accessibility
5. More comprehensive information display
6. Supports future enhancements (examples, rationale, usage stats)

### Effort Estimate
- **Template creation**: 1.5 hours
- **Route enhancement**: 0.5 hours
- **Testing**: 0.5 hours
- **Total**: 2.5 hours (within 2.0h max for task)

### Success Criteria
- [ ] `/rules/<id>` returns 200 status (no 404)
- [ ] All rule fields displayed properly
- [ ] Design system classes used throughout
- [ ] WCAG 2.1 AA accessibility compliance
- [ ] Responsive design (mobile to desktop)
- [ ] Copy buttons functional
- [ ] Toggle switch functional (HTMX)
- [ ] Breadcrumb navigation working
- [ ] Related rules displayed (if applicable)

---

**Review Date**: 2025-10-22
**Reviewer**: flask-ux-designer agent
**Status**: Ready for implementation
**Next Task**: Create `templates/rules/detail.html` template
