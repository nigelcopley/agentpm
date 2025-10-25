# Task 784: Recommended Code Fixes

**Quick Reference for Implementation**

---

## Fix 1: Badge Classes (CRITICAL)

**Location**: Line 194-195

**Replace**:
```html
<span class="badge badge-{{ task.type.value|lower }}">{{ task.type.value.replace('_', ' ').title() }}</span>
<span class="badge badge-{{ task.status.value|lower|replace('_', '-') }}">{{ task.status.value.replace('_', ' ').title() }}</span>
```

**With**:
```jinja2
{# Status Badge - Semantic Color Mapping #}
{% set status_badge_map = {
    'proposed': 'badge-gray',
    'validated': 'badge-info',
    'accepted': 'badge-primary',
    'in_progress': 'badge-warning',
    'review': 'badge-info',
    'completed': 'badge-success',
    'blocked': 'badge-error',
    'cancelled': 'badge-gray'
} %}

{# Type Badge - Semantic Color Mapping #}
{% set type_badge_map = {
    'design': 'badge-primary',
    'implementation': 'badge-info',
    'testing': 'badge-warning',
    'documentation': 'badge-gray',
    'analysis': 'badge-info',
    'deployment': 'badge-success',
    'bugfix': 'badge-error'
} %}

<span class="badge {{ type_badge_map.get(task.type.value, 'badge-gray') }}">
    {{ task.type.value.replace('_', ' ').title() }}
</span>
<span class="badge {{ status_badge_map.get(task.status.value, 'badge-gray') }}">
    {{ task.status.value.replace('_', ' ').title() }}
</span>
```

---

## Fix 2: Replace Inline SVGs with Bootstrap Icons

**Location**: Multiple (lines 15-17, 21-23, 104-106, 167-169, 219-221, etc.)

### Search Icon (Line 104-106)
**Replace**:
```html
<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
</svg>
```

**With**:
```html
<i class="bi bi-search text-gray-400"></i>
```

### Export Button (Line 15-17)
**Replace**:
```html
<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
</svg>
```

**With**:
```html
<i class="bi bi-download mr-2"></i>
```

### New Task Button (Line 21-23)
**Replace**:
```html
<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
</svg>
```

**With**:
```html
<i class="bi bi-plus mr-2"></i>
```

### Metric Card Icons (Lines 36-38, 52-54, 68-70, 84-86)
**Replace**:
```html
<svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" clip-rule="evenodd"></path>
</svg>
```

**With**:
```html
{# Total Tasks #}
<i class="bi bi-clipboard-check text-white text-xl"></i>

{# In Progress #}
<i class="bi bi-clock text-white text-xl"></i>

{# Completed #}
<i class="bi bi-check-circle text-white text-xl"></i>

{# Blocked #}
<i class="bi bi-exclamation-triangle text-white text-xl"></i>
```

### Status Indicators (Lines 167-169, 173-175, 179-181)
**Replace**:
```html
<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
</svg>
```

**With**:
```html
{# Completed #}
<i class="bi bi-check-circle text-white"></i>

{# In Progress #}
<i class="bi bi-clock text-white"></i>

{# Blocked #}
<i class="bi bi-exclamation-triangle text-white"></i>
```

### Edit Button Icon (Line 219-221)
**Replace**:
```html
<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
</svg>
```

**With**:
```html
<i class="bi bi-pencil"></i>
```

### Pagination Arrows (Lines 237-239, 245-247)
**Replace**:
```html
<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
</svg>
```

**With**:
```html
<i class="bi bi-chevron-left"></i>

{# Next button #}
<i class="bi bi-chevron-right"></i>
```

### Empty State Icon (Line 258-260)
**Replace**:
```html
<svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
</svg>
```

**With**:
```html
<i class="bi bi-inbox text-gray-400 text-6xl mb-4 block"></i>
```

---

## Fix 3: Add Accessibility Attributes

### Search Input (Line 108-113)
**Replace**:
```html
<input
    type="text"
    class="form-input pl-10"
    placeholder="Search tasks..."
    id="tasks-search">
```

**With**:
```html
<label for="tasks-search" class="sr-only">Search tasks</label>
<input
    type="text"
    class="form-input pl-10"
    placeholder="Search tasks..."
    id="tasks-search"
    aria-label="Search tasks">
```

### Icon-Only Edit Button (Line 218-222)
**Replace**:
```html
<button class="btn btn-sm btn-secondary" onclick="editTask({{ task.id }})">
    <i class="bi bi-pencil"></i>
</button>
```

**With**:
```html
<button class="btn btn-sm btn-secondary"
        onclick="editTask({{ task.id }})"
        aria-label="Edit task {{ task.name|truncate(50) }}">
    <i class="bi bi-pencil"></i>
</button>
```

### Filter Count Live Region (Line 232)
**Replace**:
```html
<div class="text-sm text-gray-700">
    Showing <span class="visible-count">{{ tasks|length }}</span> of {{ metrics.total_tasks or 0 }} tasks
</div>
```

**With**:
```html
<div class="text-sm text-gray-700">
    Showing <span class="visible-count" aria-live="polite" aria-atomic="true">{{ tasks|length }}</span> of {{ metrics.total_tasks or 0 }} tasks
</div>
```

---

## Fix 4: Add Progress Indicators

**Location**: After line 203 (inside task details)

**Add**:
```jinja2
<!-- Progress Bar for In-Progress Tasks -->
{% if task.status.value == 'in_progress' %}
<div class="mt-2 flex items-center gap-3">
    <div class="progress flex-1">
        {% set progress = task.progress_percentage|default(0) %}
        <div class="progress-bar bg-warning" style="width: {{ progress }}%"></div>
    </div>
    <span class="text-xs font-medium text-gray-600">{{ progress }}%</span>
</div>
{% endif %}
```

---

## Fix 5: Add Card Hover States

**Location**: Line 156

**Replace**:
```html
<div class="task-row card"
     data-task-id="{{ task.id }}"
     data-type="{{ task.type.value }}"
     data-status="{{ task.status.value }}"
     data-work-item-id="{{ task.work_item_id }}">
```

**With**:
```html
<div class="task-row card hover:shadow-lg transition-shadow cursor-pointer"
     onclick="window.location='/tasks/{{ task.id }}'"
     data-task-id="{{ task.id }}"
     data-type="{{ task.type.value }}"
     data-status="{{ task.status.value }}"
     data-work-item-id="{{ task.work_item_id }}">
```

---

## Fix 6: Improve Filter Layout for Mobile

**Location**: Line 99-149

**Replace entire filter section**:
```jinja2
<!-- Filters and Search -->
<div class="card mb-6">
    <div class="flex flex-col gap-4">
        <!-- Search (Full Width on Mobile) -->
        <div class="w-full lg:max-w-md">
            <label for="tasks-search" class="sr-only">Search tasks</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="bi bi-search text-gray-400"></i>
                </div>
                <input
                    type="text"
                    class="form-input pl-10 w-full"
                    placeholder="Search tasks..."
                    id="tasks-search"
                    aria-label="Search tasks">
            </div>
        </div>

        <!-- Filter Controls (Stack on Mobile, Row on Desktop) -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 flex-wrap">
            <!-- Status Filter -->
            <div class="flex items-center gap-2 w-full sm:w-auto">
                <label for="status-filter" class="text-sm font-medium text-gray-700 whitespace-nowrap">Status:</label>
                <select class="form-select flex-1 sm:flex-none sm:w-40" id="status-filter">
                    <option value="">All Status</option>
                    <option value="proposed">Proposed</option>
                    <option value="validated">Validated</option>
                    <option value="accepted">Accepted</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">Review</option>
                    <option value="completed">Completed</option>
                    <option value="blocked">Blocked</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>

            <!-- Type Filter -->
            <div class="flex items-center gap-2 w-full sm:w-auto">
                <label for="type-filter" class="text-sm font-medium text-gray-700 whitespace-nowrap">Type:</label>
                <select class="form-select flex-1 sm:flex-none sm:w-44" id="type-filter">
                    <option value="">All Types</option>
                    <option value="design">Design</option>
                    <option value="implementation">Implementation</option>
                    <option value="testing">Testing</option>
                    <option value="documentation">Documentation</option>
                    <option value="analysis">Analysis</option>
                    <option value="deployment">Deployment</option>
                    <option value="bugfix">Bug Fix</option>
                </select>
            </div>

            <!-- Clear Filters -->
            <button class="btn btn-sm btn-secondary w-full sm:w-auto" onclick="clearFilters()">
                <i class="bi bi-x-circle mr-2"></i>
                Clear Filters
            </button>
        </div>
    </div>
</div>
```

---

## Fix 7: Add Loading Overlay

**Location**: After line 5 (start of content block)

**Add**:
```jinja2
<!-- Loading Overlay -->
<div id="tasks-loading" class="hidden fixed inset-0 bg-gray-900/60 z-50">
    <div class="flex items-center justify-center h-full">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-2xl">
            <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
            <span class="text-gray-700 font-medium">Loading tasks...</span>
        </div>
    </div>
</div>
```

**Location**: In extra_js block (after line 362)

**Add**:
```javascript
// Loading overlay functions
function showTasksLoading() {
    document.getElementById('tasks-loading')?.classList.remove('hidden');
}

function hideTasksLoading() {
    document.getElementById('tasks-loading')?.classList.add('hidden');
}

// Update filterTasks to show loading
function filterTasks() {
    showTasksLoading();

    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const statusValue = statusFilter ? statusFilter.value : '';
    const typeValue = typeFilter ? typeFilter.value : '';

    const rows = document.querySelectorAll('.task-row');
    let visibleCount = 0;

    rows.forEach(row => {
        let visible = true;

        // Search filter
        if (searchQuery) {
            const text = row.textContent.toLowerCase();
            if (!text.includes(searchQuery)) {
                visible = false;
            }
        }

        // Status filter
        if (statusValue && row.getAttribute('data-status') !== statusValue) {
            visible = false;
        }

        // Type filter
        if (typeValue && row.getAttribute('data-type') !== typeValue) {
            visible = false;
        }

        row.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
    });

    // Update visible count
    const countElements = document.querySelectorAll('.visible-count');
    countElements.forEach(el => {
        el.textContent = visibleCount;
    });

    // Hide loading after short delay for smooth UX
    setTimeout(() => {
        hideTasksLoading();
    }, 200);
}

// Hide loading on page load
document.addEventListener('DOMContentLoaded', function() {
    hideTasksLoading();
    // ... rest of initialization ...
});
```

---

## Fix 8: Update Status Indicator Sizes

**Location**: Lines 164-186

**Replace**:
```html
<!-- Status Indicator -->
<div class="flex-shrink-0">
    {% if task.status.value == 'completed' %}
    <div class="w-6 h-6 bg-success rounded-full flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
        </svg>
    </div>
    {% elif task.status.value == 'in_progress' %}
    <div class="w-6 h-6 bg-warning rounded-full flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
        </svg>
    </div>
    {% elif task.status.value == 'blocked' %}
    <div class="w-6 h-6 bg-error rounded-full flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
        </svg>
    </div>
    {% else %}
    <div class="w-6 h-6 border-2 border-gray-300 rounded-full"></div>
    {% endif %}
</div>
```

**With**:
```html
<!-- Status Indicator (Design System Aligned) -->
<div class="flex-shrink-0">
    {% if task.status.value == 'completed' %}
    <div class="w-8 h-8 bg-success rounded-lg flex items-center justify-center">
        <i class="bi bi-check-circle text-white text-lg"></i>
    </div>
    {% elif task.status.value == 'in_progress' %}
    <div class="w-8 h-8 bg-warning rounded-lg flex items-center justify-center">
        <i class="bi bi-clock text-white text-lg"></i>
    </div>
    {% elif task.status.value == 'blocked' %}
    <div class="w-8 h-8 bg-error rounded-lg flex items-center justify-center">
        <i class="bi bi-exclamation-triangle text-white text-lg"></i>
    </div>
    {% elif task.status.value == 'review' %}
    <div class="w-8 h-8 bg-info rounded-lg flex items-center justify-center">
        <i class="bi bi-eye text-white text-lg"></i>
    </div>
    {% else %}
    <div class="w-8 h-8 border-2 border-gray-300 rounded-lg flex items-center justify-center">
        <i class="bi bi-circle text-gray-400"></i>
    </div>
    {% endif %}
</div>
```

---

## Testing Checklist

After applying fixes, test:

- [ ] All badges display correct colors (not grey)
- [ ] All icons use Bootstrap Icons (no broken SVGs)
- [ ] Screen reader announces search input label
- [ ] Screen reader announces filter count changes
- [ ] Icon-only buttons have accessible names
- [ ] Progress bars display for in-progress tasks
- [ ] Card hover effects work (shadow deepens on hover)
- [ ] Filter controls stack properly on mobile (< 640px)
- [ ] Loading overlay shows/hides during filtering
- [ ] Status indicators sized consistently (w-8 h-8)
- [ ] Empty state icon displays correctly
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Color contrast meets WCAG AA (use DevTools color picker)

---

## Quick Win Priority

**Apply these in order for fastest improvement:**

1. ✅ Fix badges (5 minutes) - Most visible issue
2. ✅ Replace common icons (10 minutes) - Search, buttons, pagination
3. ✅ Add ARIA labels (5 minutes) - Critical accessibility
4. ✅ Add hover states (2 minutes) - Instant UX improvement
5. ✅ Fix status indicators (10 minutes) - Visual consistency

**Total for quick wins**: ~30 minutes
**Impact**: Massive visual and accessibility improvement

---

**End of Fixes Guide**
