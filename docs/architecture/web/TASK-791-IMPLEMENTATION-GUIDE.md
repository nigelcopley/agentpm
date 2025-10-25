# Task 791: Rule Detail Implementation Guide

**Quick Reference**: Design system-compliant implementation for rule detail page

---

## 1. Create Missing Template

**File**: `agentpm/web/templates/rules/detail.html`

```html
{% extends "layouts/modern_base.html" %}

{% block title %}{{ rule.rule_id }}: {{ rule.name }} - Rules - APM (Agent Project Manager){% endblock %}

{% block breadcrumb %}
<nav aria-label="breadcrumb" class="mb-6">
  <ol class="flex items-center space-x-2 text-sm text-gray-500">
    <li><a href="/" class="hover:text-primary">Dashboard</a></li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <a href="/rules" class="hover:text-primary">Rules</a>
    </li>
    <li class="flex items-center">
      <i class="bi bi-chevron-right mx-2"></i>
      <span class="text-gray-900">{{ rule.rule_id }}</span>
    </li>
  </ol>
</nav>
{% endblock %}

{% block content %}
<!-- Header Card -->
<div class="card mb-6">
  <div class="card-header">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ rule.rule_id }}: {{ rule.name }}</h1>
        <p class="text-sm text-gray-600 mt-1">
          <span class="badge badge-gray">{{ rule.category }}</span>
        </p>
      </div>
      <div class="flex items-center gap-3">
        <span class="badge enforcement-{{ rule.enforcement_level }}">
          {% if rule.enforcement_level == 'BLOCK' %}
            <i class="bi bi-shield-lock"></i>
          {% elif rule.enforcement_level == 'LIMIT' %}
            <i class="bi bi-exclamation-circle"></i>
          {% elif rule.enforcement_level == 'GUIDE' %}
            <i class="bi bi-info-circle"></i>
          {% else %}
            <i class="bi bi-stars"></i>
          {% endif %}
          {{ rule.enforcement_level }}
        </span>

        <!-- Toggle Switch -->
        <div x-data="{ enabled: {{ 'true' if rule.enabled else 'false' }} }" class="flex items-center gap-2">
          <button
            @click="enabled = !enabled"
            :class="enabled ? 'bg-success' : 'bg-gray-300'"
            :aria-label="enabled ? 'Disable rule' : 'Enable rule'"
            hx-post="/rules/{{ rule.id }}/actions/toggle"
            hx-swap="none"
            hx-on::after-request="showToast('Rule toggled', 'success')"
            class="relative inline-flex h-6 w-12 items-center rounded-full transition">
            <span
              :class="enabled ? 'translate-x-6' : 'translate-x-1'"
              class="inline-block h-4 w-4 transform rounded-full bg-white transition">
            </span>
          </button>
          <span class="text-sm text-gray-600" x-text="enabled ? 'Enabled' : 'Disabled'"></span>
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

<!-- Enforcement Impact Card -->
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Enforcement Impact</h2>
  </div>
  <div class="card-body">
    {% if rule.enforcement_level == 'BLOCK' %}
      <div class="alert alert-error">
        <div class="flex items-start gap-3">
          <i class="bi bi-shield-lock text-2xl flex-shrink-0"></i>
          <div>
            <strong class="block mb-1">BLOCK Level</strong>
            <p class="text-sm">Prevents invalid workflow transitions (raises error)</p>
          </div>
        </div>
      </div>
    {% elif rule.enforcement_level == 'LIMIT' %}
      <div class="alert alert-warning">
        <div class="flex items-start gap-3">
          <i class="bi bi-exclamation-circle text-2xl flex-shrink-0"></i>
          <div>
            <strong class="block mb-1">LIMIT Level</strong>
            <p class="text-sm">Shows warnings but allows transitions</p>
          </div>
        </div>
      </div>
    {% elif rule.enforcement_level == 'GUIDE' %}
      <div class="alert alert-info">
        <div class="flex items-start gap-3">
          <i class="bi bi-info-circle text-2xl flex-shrink-0"></i>
          <div>
            <strong class="block mb-1">GUIDE Level</strong>
            <p class="text-sm">Informational guidance only</p>
          </div>
        </div>
      </div>
    {% else %}
      <div class="alert alert-gray">
        <div class="flex items-start gap-3">
          <i class="bi bi-stars text-2xl flex-shrink-0"></i>
          <div>
            <strong class="block mb-1">ENHANCE Level</strong>
            <p class="text-sm">Enriches AI context silently</p>
          </div>
        </div>
      </div>
    {% endif %}

    {% if rule.error_message %}
    <div class="mt-4 pt-4 border-t border-gray-200">
      <h3 class="text-sm font-medium text-gray-700 mb-2">Error Message</h3>
      <p class="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{{ rule.error_message }}</p>
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
        <pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto font-mono text-sm text-gray-800">{{ rule.config | tojson(indent=2) }}</pre>
        <button
          @click="
            navigator.clipboard.writeText('{{ rule.config | tojson(indent=2) | safe }}');
            copied = true;
            setTimeout(() => copied = false, 2000);
            showToast('Configuration copied!', 'success');
          "
          class="btn btn-sm btn-secondary absolute top-2 right-2"
          aria-label="Copy configuration">
          <i class="bi bi-clipboard" x-show="!copied"></i>
          <i class="bi bi-check" x-show="copied" x-cloak></i>
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
        <pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto font-mono text-sm text-gray-800">{{ rule.validation_logic }}</pre>
        <button
          @click="
            navigator.clipboard.writeText('{{ rule.validation_logic | safe }}');
            copied = true;
            setTimeout(() => copied = false, 2000);
            showToast('Validation logic copied!', 'success');
          "
          class="btn btn-sm btn-secondary absolute top-2 right-2"
          aria-label="Copy validation logic">
          <i class="bi bi-clipboard" x-show="!copied"></i>
          <i class="bi bi-check" x-show="copied" x-cloak></i>
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
    <dl class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Rule ID</dt>
        <dd class="text-base font-mono text-gray-900">{{ rule.rule_id }}</dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Name</dt>
        <dd class="text-base font-mono text-gray-900">{{ rule.name }}</dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Category</dt>
        <dd><span class="badge badge-gray">{{ rule.category }}</span></dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Status</dt>
        <dd>
          {% if rule.enabled %}
            <span class="badge badge-success">
              <i class="bi bi-check-circle"></i>
              Enabled
            </span>
          {% else %}
            <span class="badge badge-gray">
              <i class="bi bi-x-circle"></i>
              Disabled
            </span>
          {% endif %}
        </dd>
      </div>
      {% if rule.created_at %}
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Created</dt>
        <dd class="text-sm text-gray-600">{{ rule.created_at.strftime('%Y-%m-%d %H:%M') }}</dd>
      </div>
      {% endif %}
      {% if rule.updated_at %}
      <div>
        <dt class="text-sm font-medium text-gray-500 mb-1">Last Updated</dt>
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

{% block extra_scripts %}
<script>
// Alpine.js x-cloak style (hide elements until Alpine initializes)
document.addEventListener('alpine:init', () => {
  // Add any Alpine-specific initialization here
});
</script>
{% endblock %}
```

---

## 2. Update Route Handler (Optional Enhancement)

**File**: `agentpm/web/blueprints/rules.py`

**Current**:
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

**Enhanced** (with related rules and breadcrumbs):
```python
@rules_bp.route('/rules/<int:rule_id>')
def rule_detail(rule_id: int):
    """Get rule details with related rules."""
    db = get_database_service()

    rule = rule_methods.get_rule(db, rule_id)
    if not rule:
        abort(404, description=f"Rule {rule_id} not found")

    # Get related rules in same category (optional)
    related_rules = [
        r for r in rule_methods.list_rules(db)
        if r.category == rule.category and r.id != rule.id
    ][:5]  # Limit to 5 related rules

    return render_template(
        'rules/detail.html',
        rule=rule,
        related_rules=related_rules if related_rules else None
    )
```

---

## 3. Enhanced Expandable Row (Alternative Approach)

**File**: `agentpm/web/templates/partials/rule_row.html`

**Current** (minimal):
```html
<tr id="rule-{{ rule_info.rule.id }}" class="rule-details" style="display: none;">
    <td colspan="6" class="bg-light">
        <div class="p-3">
            <strong>Description:</strong>
            <p>{{ rule_info.rule.description }}</p>
        </div>
    </td>
</tr>
```

**Enhanced** (design system compliant):
```html
{# Rule Row - Clickable with keyboard support #}
<tr id="rule-row-{{ rule_info.rule.id }}"
    class="rule-row hover:bg-gray-50 cursor-pointer transition"
    data-enforcement="{{ rule_info.rule.enforcement_level }}"
    data-category="{{ rule_info.rule.category }}"
    role="button"
    tabindex="0"
    aria-expanded="false"
    aria-controls="rule-detail-{{ rule_info.rule.id }}"
    @click="toggleRuleDetails('{{ rule_info.rule.id }}')"
    @keydown.enter="toggleRuleDetails('{{ rule_info.rule.id }}')"
    @keydown.space.prevent="toggleRuleDetails('{{ rule_info.rule.id }}')">

    <td>
      <div class="flex items-center gap-2">
        <i class="bi bi-chevron-right transition transform rule-chevron-{{ rule_info.rule.id }}"
           aria-hidden="true"></i>
        <strong class="font-mono">{{ rule_info.rule.rule_id }}</strong>
      </div>
    </td>
    <td><span class="badge badge-gray">{{ rule_info.rule.category }}</span></td>
    <td class="font-medium text-gray-900">{{ rule_info.rule.name }}</td>
    <td>
        <span class="badge enforcement-{{ rule_info.rule.enforcement_level }}">
            {% if rule_info.rule.enforcement_level == 'BLOCK' %}
              <i class="bi bi-shield-lock"></i>
            {% elif rule_info.rule.enforcement_level == 'LIMIT' %}
              <i class="bi bi-exclamation-circle"></i>
            {% elif rule_info.rule.enforcement_level == 'GUIDE' %}
              <i class="bi bi-info-circle"></i>
            {% else %}
              <i class="bi bi-stars"></i>
            {% endif %}
            {{ rule_info.rule.enforcement_level }}
        </span>
    </td>
    <td>
        <div class="form-check form-switch" @click.stop @keydown.stop>
            <input class="form-check-input"
                   type="checkbox"
                   id="rule-toggle-{{ rule_info.rule.id }}"
                   {% if rule_info.rule.enabled %}checked{% endif %}
                   hx-post="/rules/{{ rule_info.rule.id }}/actions/toggle"
                   hx-target="#rule-row-{{ rule_info.rule.id }}"
                   hx-swap="outerHTML"
                   hx-trigger="change"
                   aria-label="Toggle rule {{ rule_info.rule.rule_id }}">
            <label class="form-check-label" for="rule-toggle-{{ rule_info.rule.id }}">
                {% if rule_info.rule.enabled %}
                    <span class="text-success fw-bold">ON</span>
                {% else %}
                    <span class="text-muted">OFF</span>
                {% endif %}
            </label>
        </div>
    </td>
</tr>

{# Expandable Detail Row - Now uses proper card structure #}
<tr id="rule-detail-{{ rule_info.rule.id }}"
    class="rule-details"
    style="display: none;"
    aria-hidden="true">
    <td colspan="6" class="bg-gray-50 p-0">
        <div class="card mb-0 border-0 rounded-0">
            <div class="card-body space-y-4">
                {# Description #}
                <div>
                    <h4 class="text-lg font-medium text-gray-800 mb-2">Description</h4>
                    <p class="text-base text-gray-700">{{ rule_info.rule.description }}</p>
                </div>

                {# Enforcement Impact #}
                {% if rule_info.rule.enforcement_level == 'BLOCK' %}
                  <div class="alert alert-error">
                    <div class="flex items-center gap-2">
                      <i class="bi bi-shield-lock"></i>
                      <span class="text-sm">Prevents invalid workflow transitions (raises error)</span>
                    </div>
                  </div>
                {% elif rule_info.rule.enforcement_level == 'LIMIT' %}
                  <div class="alert alert-warning">
                    <div class="flex items-center gap-2">
                      <i class="bi bi-exclamation-circle"></i>
                      <span class="text-sm">Shows warnings but allows transitions</span>
                    </div>
                  </div>
                {% elif rule_info.rule.enforcement_level == 'GUIDE' %}
                  <div class="alert alert-info">
                    <div class="flex items-center gap-2">
                      <i class="bi bi-info-circle"></i>
                      <span class="text-sm">Informational guidance only</span>
                    </div>
                  </div>
                {% else %}
                  <div class="alert alert-gray">
                    <div class="flex items-center gap-2">
                      <i class="bi bi-stars"></i>
                      <span class="text-sm">Enriches AI context silently</span>
                    </div>
                  </div>
                {% endif %}

                {# Validation Logic #}
                {% if rule_info.rule.validation_logic %}
                <div>
                    <h4 class="text-lg font-medium text-gray-800 mb-2">Validation Logic</h4>
                    <pre class="bg-gray-100 rounded-lg p-3 overflow-x-auto"><code class="font-mono text-sm text-gray-800">{{ rule_info.rule.validation_logic }}</code></pre>
                </div>
                {% endif %}

                {# Configuration #}
                {% if rule_info.rule.config %}
                <div>
                    <h4 class="text-lg font-medium text-gray-800 mb-2">Configuration</h4>
                    <pre class="bg-gray-100 rounded-lg p-3 overflow-x-auto"><code class="font-mono text-sm text-gray-800">{{ rule_info.rule.config | tojson(indent=2) }}</code></pre>
                </div>
                {% endif %}

                {# Link to detail page #}
                <div class="pt-3 border-t border-gray-200">
                    <a href="/rules/{{ rule_info.rule.id }}"
                       class="btn btn-sm btn-primary"
                       @click.stop>
                        <i class="bi bi-arrow-right mr-1"></i>
                        View Full Details
                    </a>
                </div>
            </div>
        </div>
    </td>
</tr>
```

**Updated JavaScript** (in `rules_list.html`):
```javascript
function toggleRuleDetails(ruleId) {
    const detailRow = document.getElementById(`rule-detail-${ruleId}`);
    const mainRow = document.getElementById(`rule-row-${ruleId}`);
    const chevron = mainRow.querySelector(`.rule-chevron-${ruleId}`);

    if (detailRow.style.display === 'none') {
        // Expand
        detailRow.style.display = '';
        detailRow.setAttribute('aria-hidden', 'false');
        mainRow.setAttribute('aria-expanded', 'true');
        chevron.classList.add('rotate-90');
    } else {
        // Collapse
        detailRow.style.display = 'none';
        detailRow.setAttribute('aria-hidden', 'true');
        mainRow.setAttribute('aria-expanded', 'false');
        chevron.classList.remove('rotate-90');
    }
}
```

---

## 4. CSS Additions (if needed)

**File**: `agentpm/web/static/css/brand-system.css`

```css
/* Alpine.js x-cloak support */
[x-cloak] {
    display: none !important;
}

/* Chevron rotation animation */
.transform {
    transition: transform 0.2s ease;
}

.rotate-90 {
    transform: rotate(90deg);
}

/* Enforcement level badges with icons */
.badge.enforcement-BLOCK {
    background-color: #dc3545;
    color: white;
}

.badge.enforcement-LIMIT {
    background-color: #ffc107;
    color: #212529;
}

.badge.enforcement-GUIDE {
    background-color: #0d6efd;
    color: white;
}

.badge.enforcement-ENHANCE {
    background-color: #6c757d;
    color: white;
}

/* Alert variants (if not already in design system) */
.alert-error {
    border-color: #f5c2c7;
    background-color: #f8d7da;
    color: #842029;
}

.alert-warning {
    border-color: #ffecb5;
    background-color: #fff3cd;
    color: #664d03;
}

.alert-info {
    border-color: #b6d4fe;
    background-color: #cfe2ff;
    color: #084298;
}

.alert-gray {
    border-color: #dee2e6;
    background-color: #f8f9fa;
    color: #495057;
}
```

---

## 5. Testing Checklist

### Manual Testing
- [ ] Navigate to `/rules` page
- [ ] Click on a rule row to expand details
- [ ] Verify chevron icon rotates
- [ ] Press Enter/Space on focused row (keyboard navigation)
- [ ] Click "View Full Details" link
- [ ] Verify `/rules/<id>` page loads
- [ ] Verify all sections render (Description, Impact, Config, Validation, Metadata)
- [ ] Test copy buttons (click "Copy" on config/validation)
- [ ] Test toggle switch (ON/OFF)
- [ ] Test breadcrumb navigation (Dashboard > Rules > DP-001)
- [ ] Test "Back to Rules" button
- [ ] Resize browser to mobile width (verify responsive layout)

### Accessibility Testing (macOS)
```bash
# Enable VoiceOver
Cmd + F5

# Navigate with keyboard
Tab (next element)
Shift + Tab (previous element)
Enter (activate button/link)
Space (activate button)

# Screen reader should announce:
- "DP-001: time-boxing-implementation, button, collapsed"
- "Expand to show details" (on chevron hover)
- "BLOCK enforcement level" (on badge)
- "Copy configuration, button" (on copy button)
```

### Browser DevTools Testing
1. Open DevTools (Cmd+Option+I)
2. Check Console for errors
3. Network tab: verify HTMX requests (toggle switch)
4. Accessibility tab: run Lighthouse audit
5. Responsive design mode: test mobile/tablet breakpoints

---

## 6. Quick Reference: Design System Classes Used

| Component          | Classes                                      | Purpose                   |
|--------------------|---------------------------------------------|---------------------------|
| **Card**           | `.card`, `.card-header`, `.card-body`, `.card-footer` | Container structure |
| **Typography**     | `.text-3xl`, `.font-bold`, `.text-gray-900` | Headings and text        |
| **Badges**         | `.badge`, `.enforcement-BLOCK`, `.badge-gray` | Status indicators      |
| **Alerts**         | `.alert`, `.alert-error`, `.alert-info`      | Enforcement explanations |
| **Buttons**        | `.btn`, `.btn-primary`, `.btn-secondary`     | Actions                  |
| **Code Blocks**    | `.font-mono`, `.bg-gray-100`, `.rounded-lg`  | Configuration display    |
| **Grid**           | `.grid`, `.grid-cols-1`, `.md:grid-cols-2`   | Responsive metadata      |
| **Spacing**        | `.mb-6`, `.gap-4`, `.space-y-4`              | Consistent spacing       |
| **Icons**          | `.bi`, `.bi-shield-lock`, `.bi-chevron-right` | Visual indicators       |

---

## 7. Common Issues & Solutions

### Issue: Copy button doesn't work
**Solution**: Ensure `navigator.clipboard` is available (requires HTTPS or localhost)
```javascript
// Fallback for non-HTTPS environments
if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
} else {
    // Fallback: create textarea and copy
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}
```

### Issue: HTMX toggle not working
**Solution**: Check HTMX is loaded in `modern_base.html`
```html
<!-- In <head> section -->
<script src="https://unpkg.com/htmx.org@1.9.6"></script>
```

### Issue: Alpine.js not initializing
**Solution**: Ensure Alpine.js is loaded and `x-data` is on correct element
```html
<!-- In <head> section -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Add x-cloak styles -->
<style>[x-cloak] { display: none !important; }</style>
```

### Issue: Chevron not rotating
**Solution**: Add CSS transition classes
```css
.transform { transition: transform 0.2s ease; }
.rotate-90 { transform: rotate(90deg); }
```

---

## 8. Future Enhancements (Post-Launch)

### Phase 1: Syntax Highlighting
```html
<!-- Use Prism.js or Highlight.js -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>

<pre><code class="language-python">{{ rule.validation_logic }}</code></pre>
```

### Phase 2: Examples Section
**Database Schema Change**:
```sql
ALTER TABLE rules ADD COLUMN examples TEXT;  -- JSON array
```

**Template Addition**:
```html
{% if rule.examples %}
<div class="card mb-6" x-data="{ activeExample: 'compliant' }">
  <div class="card-header">
    <h2 class="card-title">Examples</h2>
  </div>
  <div class="card-body">
    <!-- Tabs -->
    <div class="flex gap-4 border-b border-gray-200 mb-4">
      <button @click="activeExample = 'compliant'"
              :class="activeExample === 'compliant' ? 'border-primary text-primary' : 'border-transparent text-gray-500'"
              class="px-4 py-2 border-b-2 font-medium">
        ✅ Compliant
      </button>
      <button @click="activeExample = 'violation'"
              :class="activeExample === 'violation' ? 'border-primary text-primary' : 'border-transparent text-gray-500'"
              class="px-4 py-2 border-b-2 font-medium">
        ❌ Violation
      </button>
    </div>

    <!-- Content -->
    <div x-show="activeExample === 'compliant'" x-transition>
      <pre><code>{{ rule.examples.compliant }}</code></pre>
    </div>
    <div x-show="activeExample === 'violation'" x-transition>
      <pre><code>{{ rule.examples.violation }}</code></pre>
    </div>
  </div>
</div>
{% endif %}
```

### Phase 3: Related Rules
```html
{% if related_rules %}
<div class="card mb-6">
  <div class="card-header">
    <h2 class="card-title">Related Rules</h2>
  </div>
  <div class="card-body">
    <ul class="space-y-2">
      {% for related in related_rules %}
      <li>
        <a href="/rules/{{ related.id }}"
           class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
          <div>
            <strong class="font-mono">{{ related.rule_id }}</strong>
            <span class="text-gray-600 ml-2">{{ related.name }}</span>
          </div>
          <i class="bi bi-arrow-right text-gray-400"></i>
        </a>
      </li>
      {% endfor %}
    </ul>
  </div>
</div>
{% endif %}
```

---

**Implementation Guide Complete**
**Estimated Time**: 2.0 hours
**Priority**: High (fixes 404 error)
**Next Step**: Create `templates/rules/detail.html` file
