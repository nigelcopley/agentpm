# Analytics Route - Quick Fix Guide (Task 798)

**Goal**: Transform static analytics page into interactive Chart.js dashboard
**Time**: 2 hours for critical fixes
**Files**: `agentpm/web/templates/projects/analytics.html`

---

## 1. Add Chart.js (5 minutes)

**Location**: Top of `analytics.html` (after `{% extends %}`)

```html
{% extends "layouts/modern_base.html" %}

{% block title %}{{ view.project.name }} - Analytics{% endblock %}

{# ADD THIS BLOCK #}
{% block extra_css %}
<!-- Chart.js Library (CDN) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
<!-- AIPM Chart Theme -->
<script src="{{ url_for('static', filename='js/chart-theme.js') }}"></script>
{% endblock %}
```

---

## 2. Replace Session Activity (30 minutes)

**Find Lines 60-83** (current plain text list)

**Replace With**:

```html
<div class="mt-6">
  {% if view.sessions_over_time.get('dates') %}
  <div class="chart-container" style="position: relative; height: 300px;">
    <canvas id="sessionActivityChart"></canvas>
  </div>
  {% else %}
  <!-- Empty State -->
  <div class="text-center py-12">
    <i class="bi bi-graph-up text-gray-400 text-6xl mb-4"></i>
    <h3 class="text-lg font-medium text-gray-900 mb-2">No session data yet</h3>
    <p class="text-gray-600 mb-4">Session analytics will appear once activity is logged.</p>
    <button class="btn btn-primary" onclick="location.reload()">
      <i class="bi bi-arrow-clockwise mr-2"></i>
      Refresh Data
    </button>
  </div>
  {% endif %}
</div>
```

---

## 3. Replace Task Flow (30 minutes)

**Find Lines 106-122** (current plain text list)

**Replace With**:

```html
<div class="mt-6">
  {% if view.tasks_over_time.get('dates') %}
  <div class="chart-container" style="position: relative; height: 300px;">
    <canvas id="taskFlowChart"></canvas>
  </div>
  {% else %}
  <!-- Empty State -->
  <div class="text-center py-12">
    <i class="bi bi-kanban text-gray-400 text-6xl mb-4"></i>
    <h3 class="text-lg font-medium text-gray-900 mb-2">No task metrics yet</h3>
    <p class="text-gray-600 mb-4">Task flow data will appear once tasks are created.</p>
  </div>
  {% endif %}
</div>
```

---

## 4. Add Chart JavaScript (45 minutes)

**Location**: Bottom of `analytics.html` (after `{% endblock content %}`)

```html
{% block extra_scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Load AIPM theme
  const chartTheme = window.AIPM_CHART_THEME;
  const palette = chartTheme?.palette || {};
  const textColor = palette.textLight || '#e2e8f0';
  const gridColor = palette.midnight || '#2d3748';
  const borderColor = palette.navy || '#1a1d29';
  const tickColor = palette.slate || '#94a3b8';

  // ============================================
  // 1. SESSION ACTIVITY CHART (Line Chart)
  // ============================================
  {% if view.sessions_over_time.get('dates') %}
  const sessionCtx = document.getElementById('sessionActivityChart').getContext('2d');
  const sessionLabels = {{ view.sessions_over_time.get('dates', []) | tojson }};
  const sessionData = {{ view.sessions_over_time.get('sessions', []) | tojson }};
  const durationData = {{ view.sessions_over_time.get('duration', []) | tojson }};

  new Chart(sessionCtx, {
    type: 'line',
    data: {
      labels: sessionLabels,
      datasets: [
        {
          label: 'Sessions',
          data: sessionData,
          borderColor: palette.primary || '#667eea',
          backgroundColor: chartTheme.withAlpha(palette.primary || '#667eea', 0.1),
          tension: 0.4,
          fill: true,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Duration (min)',
          data: durationData,
          borderColor: palette.green || '#43e97b',
          backgroundColor: chartTheme.withAlpha(palette.green || '#43e97b', 0.1),
          tension: 0.4,
          fill: true,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: textColor,
            padding: 10,
            usePointStyle: true,
            font: { size: 12 }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: palette.primary,
          borderWidth: 1,
          callbacks: {
            title: function(context) {
              return `Date: ${context[0].label}`;
            },
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          position: 'left',
          title: {
            display: true,
            text: 'Sessions',
            color: textColor,
            font: { size: 12, weight: 'bold' }
          },
          ticks: {
            color: tickColor,
            stepSize: 1
          },
          grid: {
            color: gridColor,
            drawBorder: false
          }
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          title: {
            display: true,
            text: 'Duration (min)',
            color: textColor,
            font: { size: 12, weight: 'bold' }
          },
          ticks: {
            color: tickColor
          },
          grid: {
            drawOnChartArea: false
          }
        },
        x: {
          ticks: {
            color: tickColor,
            maxRotation: 45,
            minRotation: 0
          },
          grid: {
            color: gridColor,
            drawBorder: false
          }
        }
      }
    }
  });
  {% endif %}

  // ============================================
  // 2. TASK FLOW CHART (Bar Chart)
  // ============================================
  {% if view.tasks_over_time.get('dates') %}
  const taskCtx = document.getElementById('taskFlowChart').getContext('2d');
  const taskLabels = {{ view.tasks_over_time.get('dates', []) | tojson }};
  const tasksCreated = {{ view.tasks_over_time.get('created', []) | tojson }};
  const tasksCompleted = {{ view.tasks_over_time.get('completed', []) | tojson }};

  new Chart(taskCtx, {
    type: 'bar',
    data: {
      labels: taskLabels,
      datasets: [
        {
          label: 'Created',
          data: tasksCreated,
          backgroundColor: palette.primary || '#667eea',
          borderColor: borderColor,
          borderWidth: 1
        },
        {
          label: 'Completed',
          data: tasksCompleted,
          backgroundColor: palette.success || '#28a745',
          borderColor: borderColor,
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: textColor,
            padding: 10,
            usePointStyle: true,
            font: { size: 12 }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: palette.primary,
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          stacked: false,
          title: {
            display: true,
            text: 'Task Count',
            color: textColor,
            font: { size: 12, weight: 'bold' }
          },
          ticks: {
            color: tickColor,
            stepSize: 1
          },
          grid: {
            color: gridColor,
            drawBorder: false
          }
        },
        x: {
          stacked: false,
          ticks: {
            color: tickColor,
            maxRotation: 45,
            minRotation: 0
          },
          grid: {
            color: gridColor,
            drawBorder: false
          }
        }
      }
    }
  });
  {% endif %}
});
</script>
{% endblock %}
```

---

## 5. Enhance Metric Cards (20 minutes)

**Find Lines 27-46** (metric cards section)

**Replace With**:

```html
<section class="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
  <!-- Time Boxing Card -->
  <article class="card">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div class="w-12 h-12 rounded-lg flex items-center justify-center
                    {% if view.time_boxing_compliance >= 90 %}bg-success/10{% elif view.time_boxing_compliance >= 70 %}bg-warning/10{% else %}bg-error/10{% endif %}">
          <i class="bi bi-stopwatch text-2xl
                     {% if view.time_boxing_compliance >= 90 %}text-success{% elif view.time_boxing_compliance >= 70 %}text-warning{% else %}text-error{% endif %}"></i>
        </div>
      </div>
      <div class="ml-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Time Boxing</p>
        <p class="text-2xl font-bold text-gray-900">{{ '%.1f'|format(view.time_boxing_compliance) }}%</p>
      </div>
    </div>
    <p class="mt-3 text-xs text-gray-500">Tasks inside expected effort bands</p>
  </article>

  <!-- Task Success Card -->
  <article class="card">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div class="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
          <i class="bi bi-check-circle text-success text-2xl"></i>
        </div>
      </div>
      <div class="ml-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Task Success</p>
        <p class="text-2xl font-bold text-gray-900">{{ '%.1f'|format(view.task_success_rate) }}%</p>
      </div>
    </div>
    <p class="mt-3 text-xs text-gray-500">Completed tasks vs. total assigned</p>
  </article>

  <!-- Avg Task Duration Card -->
  <article class="card">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
          <i class="bi bi-clock text-primary text-2xl"></i>
        </div>
      </div>
      <div class="ml-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Avg Duration</p>
        <p class="text-2xl font-bold text-gray-900">{{ '%.1f'|format(view.average_task_duration) }}h</p>
      </div>
    </div>
    <p class="mt-3 text-xs text-gray-500">Based on completed task lifecycle</p>
  </article>

  <!-- Agent Utilization Card -->
  <article class="card">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div class="w-12 h-12 bg-info/10 rounded-lg flex items-center justify-center">
          <i class="bi bi-robot text-info text-2xl"></i>
        </div>
      </div>
      <div class="ml-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Agent Util</p>
        <p class="text-2xl font-bold text-gray-900">{{ '%.1f'|format(view.agent_utilization) }}%</p>
      </div>
    </div>
    <p class="mt-3 text-xs text-gray-500">Pending richer analytics</p>
  </article>
</section>
```

---

## 6. Testing Checklist

After implementation, verify:

### Visual Testing
- [ ] Charts render on page load (no JavaScript errors)
- [ ] Session Activity chart shows dual Y-axes (sessions + duration)
- [ ] Task Flow chart shows side-by-side bars (created vs completed)
- [ ] Empty states display when no data
- [ ] Metric cards show colored icons

### Interaction Testing
- [ ] Hover over chart points shows tooltips
- [ ] Click legend to toggle dataset visibility
- [ ] Charts responsive on mobile (resize browser to 375px)
- [ ] Charts responsive on tablet (768px)
- [ ] Charts responsive on desktop (1920px)

### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Accessibility Testing
- [ ] Keyboard navigation (Tab through elements)
- [ ] Color contrast meets 4.5:1 ratio (use DevTools)
- [ ] Screen reader announces chart data (NVDA/VoiceOver)

---

## 7. Common Issues & Fixes

### Issue: "AIPM_CHART_THEME is not defined"
**Fix**: Ensure `chart-theme.js` is loaded BEFORE chart initialization
```html
{% block extra_css %}
<script src="{{ url_for('static', filename='js/chart-theme.js') }}"></script>
{% endblock %}
```

### Issue: Charts not rendering (blank canvas)
**Fix**: Check browser console for errors. Common causes:
1. Data array empty (use `{% if view.sessions_over_time.get('dates') %}`)
2. Canvas ID mismatch (`sessionActivityChart` vs `sessionChart`)
3. Chart.js not loaded (check Network tab in DevTools)

### Issue: Charts look broken on mobile
**Fix**: Set `maintainAspectRatio: false` in chart options
```javascript
options: {
  responsive: true,
  maintainAspectRatio: false, // <-- Critical for responsive height
  // ...
}
```

### Issue: Colors don't match design system
**Fix**: Use `palette` from `AIPM_CHART_THEME`, not hard-coded hex values
```javascript
// ❌ Wrong
borderColor: '#667eea'

// ✅ Correct
borderColor: palette.primary || '#667eea'
```

---

## 8. Performance Tips

1. **Lazy Load Chart.js**: Only load on analytics route (already done via `{% block extra_css %}`)
2. **Limit Data Points**: Keep datasets <100 points for smooth rendering
3. **Cache chart-theme.js**: Flask will serve from cache after first load
4. **Defer Script Execution**: Use `defer` attribute if needed

---

## 9. Next Steps After Critical Fixes

**Phase 2 Enhancements** (1 hour):
1. Add time period selector (7 days, 30 days, 90 days)
2. Implement loading states (skeleton loaders)
3. Add data table alternative (accessibility)

**Phase 3 Polish** (30 minutes):
1. CSV export button
2. Real-time updates (WebSocket)
3. Chart animation refinements

---

## 10. File Locations Reference

- **Template**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/web/templates/projects/analytics.html`
- **Chart Theme**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/web/static/js/chart-theme.js`
- **Design System**: `/Users/nigelcopley/.project_manager/aipm-v2/docs/architecture/web/design-system.md`
- **Component Snippets**: `/Users/nigelcopley/.project_manager/aipm-v2/docs/architecture/web/component-snippets.md`

---

**Total Effort**: 2 hours (critical fixes only)
**Success Criteria**: Charts render, empty states work, colors match design system
**Review Document**: `ANALYTICS_UX_REVIEW.md` (full details)
