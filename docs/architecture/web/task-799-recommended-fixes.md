# Task 799: Ideas Route - Recommended Fixes

**Date**: 2025-10-22
**Status**: Ready for Implementation
**Priority**: High (Launch-Critical)
**Effort**: 7.0 hours (required fixes only)

---

## Overview

This document provides **copy-paste ready code** for the critical fixes identified in the UX review. All fixes use the APM (Agent Project Manager) Design System (Tailwind CSS 3.4.14 + Alpine.js 3.14.1).

---

## Fix 1: Convert Metric Cards to Tailwind (Priority 1)

**File**: `/agentpm/web/templates/ideas/list.html`
**Lines**: 16-36
**Effort**: 30 minutes

### Before (Bootstrap)
```html
<div class="row mb-4 g-4">
    <div class="col-md-3">
        <div class="card metric-card shadow-royal card-lift">
            <div class="card-body text-center">
                <i class="bi bi-lightbulb text-warning icon-pulse" style="font-size: 2.5rem; opacity: 0.4;"></i>
                <h3 class="display-4 text-warning mt-3">{{ total_ideas }}</h3>
                <p class="metric-label">Total Ideas</p>
            </div>
        </div>
    </div>

    {% for status, count in status_distribution.items() %}
    <div class="col-md-3">
        <div class="card metric-card card-lift">
            <div class="card-body text-center">
                <h4>{{ count }}</h4>
                <p class="text-muted"><span class="badge badge-gray">{{ status }}</span></p>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
```

### After (Tailwind)
```html
<!-- Summary Metrics -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
    <!-- Total Ideas Card -->
    <div class="card text-center hover:shadow-lg transition-shadow">
        <i class="bi bi-lightbulb text-warning text-4xl opacity-40 mb-3"></i>
        <h3 class="text-4xl font-bold text-warning mb-2">{{ total_ideas }}</h3>
        <p class="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Ideas</p>
    </div>

    <!-- Status Distribution Cards -->
    {% for status, count in status_distribution.items() %}
    <div class="card text-center hover:shadow-lg transition-shadow">
        <h4 class="text-3xl font-bold text-gray-900 mb-2">{{ count }}</h4>
        <span class="badge badge-gray">{{ status }}</span>
    </div>
    {% endfor %}
</div>
```

---

## Fix 2: Convert Filter Buttons to Tailwind (Priority 1)

**File**: `/agentpm/web/templates/ideas/list.html`
**Lines**: 60-93
**Effort**: 30 minutes

### Before (Bootstrap)
```html
<div class="row mb-3">
    <div class="col-md-8">
        <div class="btn-group" role="group" aria-label="Status filter">
            <a href="/ideas" class="btn btn-sm {% if not current_status_filter %}btn-primary{% else %}btn-outline-primary{% endif %}">
                All
            </a>
            <a href="/ideas?status=idea" class="btn btn-sm {% if current_status_filter == 'idea' %}btn-primary{% else %}btn-outline-primary{% endif %}">
                Ideas
            </a>
            <!-- More buttons... -->
        </div>
    </div>
    <div class="col-md-4 text-end">
        <div class="btn-group" role="group" aria-label="Sort">
            <a href="/ideas?sort=votes" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-star"></i> Votes
            </a>
            <a href="/ideas?sort=created_at" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-clock"></i> Newest
            </a>
        </div>
    </div>
</div>
```

### After (Tailwind)
```html
<!-- Filters and Sorting -->
<div class="flex flex-col md:flex-row md:justify-between gap-4 mb-6">
    <!-- Status Filters -->
    <div class="flex flex-wrap gap-2" role="group" aria-label="Status filter">
        <a href="/ideas"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if not current_status_filter %}
                    border-primary bg-primary text-white
                  {% else %}
                    border-gray-300 bg-white text-gray-700 hover:bg-gray-50
                  {% endif %}"
           {% if not current_status_filter %}aria-current="true"{% endif %}>
            All
        </a>

        <a href="/ideas?status=idea"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if current_status_filter == 'idea' %}
                    border-primary bg-primary text-white
                  {% else %}
                    border-gray-300 bg-white text-gray-700 hover:bg-gray-50
                  {% endif %}"
           {% if current_status_filter == 'idea' %}aria-current="true"{% endif %}>
            <i class="bi bi-lightbulb"></i>
            Ideas
        </a>

        <a href="/ideas?status=research"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if current_status_filter == 'research' %}
                    border-primary bg-primary text-white
                  {% else %}
                    border-gray-300 bg-white text-gray-700 hover:bg-gray-50
                  {% endif %}"
           {% if current_status_filter == 'research' %}aria-current="true"{% endif %}>
            <i class="bi bi-search"></i>
            Research
        </a>

        <a href="/ideas?status=proposed"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if current_status_filter == 'proposed' %}
                    border-primary bg-primary text-white
                  {% else %}
                    border-gray-300 bg-white text-gray-700 hover:bg-gray-50
                  {% endif %}"
           {% if current_status_filter == 'proposed' %}aria-current="true"{% endif %}>
            <i class="bi bi-check-circle"></i>
            Proposed
        </a>

        <a href="/ideas?status=converted"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if current_status_filter == 'converted' %}
                    border-success bg-success text-white
                  {% else %}
                    border-success bg-white text-success hover:bg-success/10
                  {% endif %}"
           {% if current_status_filter == 'converted' %}aria-current="true"{% endif %}>
            <i class="bi bi-box-arrow-up-right"></i>
            Converted
        </a>

        <a href="/ideas?status=rejected"
           class="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition
                  {% if current_status_filter == 'rejected' %}
                    border-error bg-error text-white
                  {% else %}
                    border-error bg-white text-error hover:bg-error/10
                  {% endif %}"
           {% if current_status_filter == 'rejected' %}aria-current="true"{% endif %}>
            <i class="bi bi-x-circle"></i>
            Rejected
        </a>
    </div>

    <!-- Sort Buttons -->
    <div class="flex gap-2" role="group" aria-label="Sort options">
        <a href="/ideas?sort=votes{% if current_status_filter %}&status={{ current_status_filter }}{% endif %}"
           class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
           {% if current_sort == 'votes' %}aria-current="true"{% endif %}>
            <i class="bi bi-star"></i>
            Votes
        </a>

        <a href="/ideas?sort=created_at{% if current_status_filter %}&status={{ current_status_filter }}{% endif %}"
           class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
           {% if current_sort == 'created_at' %}aria-current="true"{% endif %}>
            <i class="bi bi-clock"></i>
            Newest
        </a>
    </div>
</div>
```

---

## Fix 3: Convert Idea List Items to Tailwind (Priority 1)

**File**: `/agentpm/web/templates/ideas/list.html`
**Lines**: 96-176
**Effort**: 45 minutes

### Before (Bootstrap)
```html
<div class="card metric-card shadow-royal">
    <div class="card-body">
        <h5 class="card-title">
            Ideas <span class="text-muted">({{ ideas|length }})</span>
        </h5>

        {% if ideas %}
        <div class="list-group">
            {% for idea in ideas %}
            <a href="/ideas/{{ idea.id }}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">
                            <i class="bi bi-lightbulb-fill text-warning"></i>
                            {{ idea.title }}
                        </h6>
                        {% if idea.description %}
                        <p class="mb-1 text-muted small">{{ idea.description[:150] }}...</p>
                        {% endif %}
                        {% if idea.tags %}
                        <div class="mt-2">
                            {% for tag in idea.tags %}
                            <span class="badge badge-gray text-dark">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <div class="text-end ms-3">
                        <div class="mb-2">
                            <span class="badge badge-warning">
                                <i class="bi bi-star-fill"></i> {{ idea.votes or 0 }}
                            </span>
                        </div>
                        <div>
                            {% if idea.status == 'converted' %}
                            <span class="badge badge-success">{{ idea.status }}</span>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</div>
```

### After (Tailwind)
```html
<div class="card">
    <h5 class="text-xl font-semibold text-gray-900 mb-4">
        Ideas <span class="text-gray-500 font-normal">({{ ideas|length }})</span>
    </h5>

    {% if ideas %}
    <!-- Ideas List -->
    <div class="space-y-3">
        {% for idea in ideas %}
        <a href="/ideas/{{ idea.id }}"
           class="block rounded-lg border border-gray-100 bg-white p-4 transition
                  hover:shadow-lg hover:border-primary/20
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">

            <div class="flex flex-col md:flex-row md:justify-between gap-4">
                <!-- Left: Title, Description, Tags -->
                <div class="flex-grow space-y-2">
                    <h6 class="text-base font-semibold text-gray-900 flex items-center gap-2">
                        <i class="bi bi-lightbulb-fill text-warning"></i>
                        {{ idea.title }}
                    </h6>

                    {% if idea.description %}
                    <p class="text-sm text-gray-600 line-clamp-2">
                        {{ idea.description[:150] }}{% if idea.description|length > 150 %}...{% endif %}
                    </p>
                    {% endif %}

                    {% if idea.tags %}
                    <div class="flex flex-wrap gap-2">
                        {% for tag in idea.tags %}
                        <span class="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                            #{{ tag }}
                        </span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>

                <!-- Right: Votes, Status, Metadata -->
                <div class="flex flex-row md:flex-col gap-3 md:gap-2 items-start md:items-end">
                    <!-- Vote Count -->
                    <div>
                        <span class="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">
                            <i class="bi bi-star-fill"></i>
                            {{ idea.votes or 0 }}
                        </span>
                    </div>

                    <!-- Status Badge -->
                    <div>
                        {% if idea.status == 'converted' %}
                        <span class="badge badge-success" role="status" aria-label="Status: converted">
                            <i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>
                            converted
                        </span>
                        {% elif idea.status == 'rejected' %}
                        <span class="badge badge-error" role="status" aria-label="Status: rejected">
                            <i class="bi bi-x-circle" aria-hidden="true"></i>
                            rejected
                        </span>
                        {% elif idea.status == 'proposed' %}
                        <span class="badge badge-primary" role="status" aria-label="Status: proposed">
                            <i class="bi bi-check-circle" aria-hidden="true"></i>
                            proposed
                        </span>
                        {% elif idea.status == 'research' %}
                        <span class="badge badge-info" role="status" aria-label="Status: research">
                            <i class="bi bi-search" aria-hidden="true"></i>
                            research
                        </span>
                        {% else %}
                        <span class="badge badge-gray" role="status" aria-label="Status: {{ idea.status }}">
                            <i class="bi bi-lightbulb" aria-hidden="true"></i>
                            {{ idea.status }}
                        </span>
                        {% endif %}
                    </div>

                    <!-- Metadata -->
                    <div class="flex flex-col items-end text-xs text-gray-500 space-y-1">
                        <span>{{ idea.source.replace('_', ' ') }}</span>
                        {% if idea.created_at %}
                        <span>{{ idea.created_at.strftime('%Y-%m-%d') }}</span>
                        {% endif %}
                    </div>
                </div>
            </div>
        </a>
        {% endfor %}
    </div>
    {% endif %}
</div>
```

---

## Fix 4: Improve Empty State (Priority 1)

**File**: `/agentpm/web/templates/ideas/list.html`
**Lines**: 164-172
**Effort**: 15 minutes

### Before (Bootstrap Alert)
```html
<div class="alert alert-info" role="alert">
    <i class="bi bi-info-circle"></i> No ideas match your filters.
    {% if current_status_filter or current_tag_filter %}
    <br><a href="/ideas" class="alert-link">Clear filters</a>
    {% else %}
    <br>Use <code>apm idea create "Title"</code> to capture ideas.
    {% endif %}
</div>
```

### After (Centered Empty State)
```html
{% else %}
<!-- Empty State -->
<div class="text-center py-16 px-4">
    <i class="bi bi-inbox text-gray-400 text-6xl mb-4"></i>
    <h3 class="text-lg font-medium text-gray-900 mb-2">No ideas found</h3>

    {% if current_status_filter or current_tag_filter %}
        <p class="text-gray-600 mb-4">
            No ideas match your current filters. Try adjusting your criteria.
        </p>
        <a href="/ideas" class="btn btn-primary">
            <i class="bi bi-x-circle mr-2"></i>
            Clear All Filters
        </a>
    {% else %}
        <p class="text-gray-600 mb-6 max-w-md mx-auto">
            Start capturing ideas using the AIPM CLI. Ideas flow through research, proposal, and conversion to work items.
        </p>

        <!-- CLI Command Example -->
        <div class="inline-flex items-center gap-3 rounded-lg bg-gray-100 px-4 py-3 font-mono text-sm text-gray-700">
            <i class="bi bi-terminal text-gray-500"></i>
            <code>apm idea create "My brilliant idea"</code>
        </div>

        <!-- Workflow Diagram -->
        <div class="mt-8 flex justify-center items-center gap-2 text-sm">
            <span class="badge badge-gray">idea</span>
            <i class="bi bi-arrow-right text-gray-400"></i>
            <span class="badge badge-info">research</span>
            <i class="bi bi-arrow-right text-gray-400"></i>
            <span class="badge badge-primary">proposed</span>
            <i class="bi bi-arrow-right text-gray-400"></i>
            <span class="badge badge-success">converted</span>
        </div>
    {% endif %}
</div>
{% endif %}
```

---

## Fix 5: Add Loading Overlay (Priority 1)

**File**: `/agentpm/web/templates/ideas/list.html`
**Location**: Add to `{% block content %}` (before closing)
**Effort**: 15 minutes

### Add Before `{% endblock %}`
```html
<!-- Loading Overlay -->
<div id="loading-overlay" class="fixed inset-0 bg-gray-900/60 z-50 hidden">
    <div class="flex items-center justify-center h-full">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-2xl">
            <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
            <span class="text-gray-700 font-medium">Updating...</span>
        </div>
    </div>
</div>
```

### Update JavaScript (Lines 207-232)
```javascript
{% block extra_scripts %}
<script>
// Global loading helpers
function showLoading() {
    document.getElementById('loading-overlay')?.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay')?.classList.add('hidden');
}

// Vote interaction with loading state
document.addEventListener('DOMContentLoaded', function() {
    let voteTimeout;

    document.body.addEventListener('click', function(e) {
        if (e.target.closest('[data-idea-vote]')) {
            e.preventDefault();

            // Debounce rapid clicks
            clearTimeout(voteTimeout);

            voteTimeout = setTimeout(() => {
                const btn = e.target.closest('[data-idea-vote]');
                const ideaId = btn.dataset.ideaId;
                const direction = btn.dataset.direction;

                showLoading();

                fetch(`/idea/${ideaId}/vote`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({direction})
                })
                .then(r => {
                    if (!r.ok) throw new Error('Vote failed');
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        // Update vote count in UI
                        const voteElement = document.querySelector(`[data-votes-for="${ideaId}"]`);
                        if (voteElement) {
                            voteElement.textContent = data.votes;
                        }
                        // Show success toast (if toast system available)
                        if (typeof showToast === 'function') {
                            showToast('Vote recorded!', 'success', 2000);
                        }
                    }
                })
                .catch(error => {
                    console.error('Vote error:', error);
                    if (typeof showToast === 'function') {
                        showToast('Failed to vote. Please try again.', 'error');
                    }
                })
                .finally(() => {
                    hideLoading();
                });
            }, 300);
        }
    });
});
</script>
{% endblock %}
```

---

## Fix 6: Fix Vote Button in Detail View (Priority 1)

**File**: `/agentpm/web/templates/idea_detail.html`
**Lines**: 44-52
**Effort**: 10 minutes

### Before
```html
<div class="mt-2">
    <button class="btn btn-warning btn-sm" data-idea-vote data-idea-id="{{ idea.id }}" data-direction="up">
        <i class="bi bi-star-fill"></i> Upvote
    </button>
    <span class="badge badge-gray text-dark ms-2" data-votes-for="{{ idea.id }}">
        {{ idea.votes or 0 }} votes
    </span>
</div>
```

### After
```html
<div class="mt-3 flex items-center gap-3">
    <button class="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-amber-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            data-idea-vote
            data-idea-id="{{ idea.id }}"
            data-direction="up"
            aria-label="Upvote idea: {{ idea.title }}">
        <i class="bi bi-star-fill" aria-hidden="true"></i>
        Upvote
    </button>

    <span class="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700"
          data-votes-for="{{ idea.id }}"
          role="status"
          aria-live="polite">
        {{ idea.votes or 0 }} votes
    </span>
</div>
```

---

## Fix 7: Fix Status Badges in Detail View (Priority 1)

**File**: `/agentpm/web/templates/idea_detail.html`
**Lines**: 34-42
**Effort**: 10 minutes

### Before
```html
{% if idea.status == 'converted' %}
<span class="badge badge-success fs-5">{{ idea.status }}</span>
{% elif idea.status == 'rejected' %}
<span class="badge badge-error fs-5">{{ idea.status }}</span>
{% elif idea.status == 'proposed' %}
<span class="badge badge-primary fs-5">{{ idea.status }}</span>
{% else %}
<span class="badge badge-gray fs-5">{{ idea.status }}</span>
{% endif %}
```

### After
```html
{% if idea.status == 'converted' %}
<span class="badge badge-success text-base" role="status" aria-label="Status: converted">
    <i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>
    converted
</span>
{% elif idea.status == 'rejected' %}
<span class="badge badge-error text-base" role="status" aria-label="Status: rejected">
    <i class="bi bi-x-circle" aria-hidden="true"></i>
    rejected
</span>
{% elif idea.status == 'proposed' %}
<span class="badge badge-primary text-base" role="status" aria-label="Status: proposed">
    <i class="bi bi-check-circle" aria-hidden="true"></i>
    proposed
</span>
{% elif idea.status == 'research' %}
<span class="badge badge-info text-base" role="status" aria-label="Status: research">
    <i class="bi bi-search" aria-hidden="true"></i>
    research
</span>
{% else %}
<span class="badge badge-gray text-base" role="status" aria-label="Status: {{ idea.status }}">
    <i class="bi bi-lightbulb" aria-hidden="true"></i>
    {{ idea.status }}
</span>
{% endif %}
```

---

## Fix 8: Add Loading State to Detail View (Priority 1)

**File**: `/agentpm/web/templates/idea_detail.html`
**Location**: Before `{% endblock %}`
**Effort**: 10 minutes

### Add Before `{% endblock %}`
```html
<!-- Loading Overlay -->
<div id="loading-overlay" class="fixed inset-0 bg-gray-900/60 z-50 hidden">
    <div class="flex items-center justify-center h-full">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-2xl">
            <i class="bi bi-arrow-repeat animate-spin text-2xl text-primary"></i>
            <span class="text-gray-700 font-medium">Processing...</span>
        </div>
    </div>
</div>
```

### Update JavaScript (Lines 196-271)
```javascript
{% block extra_scripts %}
<script>
// Global loading helpers
function showLoading() {
    document.getElementById('loading-overlay')?.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay')?.classList.add('hidden');
}

// Idea transitions with loading
document.addEventListener('DOMContentLoaded', function() {
    // Transition buttons
    document.body.addEventListener('click', function(e) {
        if (e.target.closest('[data-idea-transition]')) {
            const btn = e.target.closest('[data-idea-transition]');
            const ideaId = btn.dataset.ideaId;
            const newStatus = btn.dataset.newStatus;

            if (confirm(`Transition to ${newStatus}?`)) {
                showLoading();

                fetch(`/idea/${ideaId}/transition`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_status: newStatus})
                })
                .then(r => {
                    if (!r.ok) throw new Error('Transition failed');
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Transition error:', error);
                    alert('Failed to transition. Please try again.');
                })
                .finally(() => {
                    hideLoading();
                });
            }
        }
    });

    // Reject button with loading
    document.body.addEventListener('click', function(e) {
        if (e.target.closest('[data-idea-reject]')) {
            const btn = e.target.closest('[data-idea-reject]');
            const ideaId = btn.dataset.ideaId;
            const reason = prompt('Rejection reason:');

            if (reason) {
                showLoading();

                fetch(`/idea/${ideaId}/transition`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        new_status: 'rejected',
                        reason: reason
                    })
                })
                .then(r => {
                    if (!r.ok) throw new Error('Rejection failed');
                    return r.json();
                })
                .then(data => {
                    if (data.success) {
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Rejection error:', error);
                    alert('Failed to reject. Please try again.');
                })
                .finally(() => {
                    hideLoading();
                });
            }
        }
    });

    // Vote buttons with loading
    document.body.addEventListener('click', function(e) {
        if (e.target.closest('[data-idea-vote]')) {
            const btn = e.target.closest('[data-idea-vote]');
            const ideaId = btn.dataset.ideaId;
            const direction = btn.dataset.direction;

            showLoading();

            fetch(`/idea/${ideaId}/vote`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({direction})
            })
            .then(r => {
                if (!r.ok) throw new Error('Vote failed');
                return r.json();
            })
            .then(data => {
                if (data.success) {
                    const voteElement = document.querySelector(`[data-votes-for="${ideaId}"]`);
                    if (voteElement) {
                        voteElement.textContent = data.votes + ' votes';
                    }
                }
            })
            .catch(error => {
                console.error('Vote error:', error);
                alert('Failed to vote. Please try again.');
            })
            .finally(() => {
                hideLoading();
            });
        }
    });
});
</script>
{% endblock %}
```

---

## Implementation Checklist

### Phase 1: Critical Fixes (4 hours)
- [ ] **Fix 1**: Convert metric cards (30 min)
- [ ] **Fix 2**: Convert filter buttons (30 min)
- [ ] **Fix 3**: Convert idea list items (45 min)
- [ ] **Fix 4**: Improve empty state (15 min)
- [ ] **Fix 5**: Add loading overlay to list (15 min)
- [ ] **Fix 6**: Fix vote button in detail (10 min)
- [ ] **Fix 7**: Fix status badges in detail (10 min)
- [ ] **Fix 8**: Add loading to detail view (10 min)

### Phase 2: Testing (1 hour)
- [ ] Visual regression testing (mobile + desktop)
- [ ] Keyboard navigation testing
- [ ] Screen reader testing (NVDA/JAWS)
- [ ] Color contrast verification
- [ ] Performance testing (Lighthouse)

### Phase 3: Documentation (30 min)
- [ ] Update component usage docs
- [ ] Add accessibility notes
- [ ] Document new patterns

---

## Verification Steps

1. **Visual Check**:
   ```bash
   # Start dev server
   cd /Users/nigelcopley/.project_manager/aipm-v2
   python -m agentpm.web.app

   # Open in browser
   open http://localhost:5000/ideas
   ```

2. **Responsive Check**:
   - Resize browser to 375px (mobile)
   - Resize to 768px (tablet)
   - Resize to 1920px (desktop)
   - Verify all layouts work correctly

3. **Accessibility Check**:
   ```bash
   # Use axe DevTools browser extension
   # Or run Lighthouse audit in Chrome DevTools
   ```

4. **Keyboard Navigation**:
   - Tab through all interactive elements
   - Verify focus-visible styles appear
   - Test Enter/Space on buttons
   - Test Escape on modals (if implemented)

---

## Before/After Screenshots

*Screenshots to be captured after implementation*

**Checklist**:
- [ ] Ideas list - mobile view
- [ ] Ideas list - desktop view
- [ ] Filter buttons - active state
- [ ] Idea card hover state
- [ ] Empty state
- [ ] Loading overlay
- [ ] Vote button focus state

---

**Document Version**: 1.0
**Last Updated**: 2025-10-22
**Ready for Implementation**: Yes
**Estimated Total Time**: 7 hours
