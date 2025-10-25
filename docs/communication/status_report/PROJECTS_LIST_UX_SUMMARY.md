# Projects List Route UX Review - Executive Summary

**Task**: #786
**Date**: 2025-10-22
**Status**: ✅ REVIEW COMPLETE

---

## Quick Verdict

**Grade**: B- (66/100)
**Launch Readiness**: ⚠️ NEEDS FIXES (3 critical issues block launch)

---

## 3 Critical Fixes Required (1.5h)

### 1. Status Badge Mapping BROKEN ❌
**Problem**: `badge-active`, `badge-completed` classes don't exist.
**Fix**: Add template filter to map `project.status` → design system badge classes
**Code**:
```python
# agentpm/web/app.py
@app.template_filter('project_status_badge')
def project_status_badge_filter(status_value: str) -> str:
    mapping = {
        'active': 'badge-warning',
        'completed': 'badge-success',
        'on_hold': 'badge-gray',
        'archived': 'badge-gray',
    }
    return mapping.get(status_value.lower(), 'badge-gray')
```

### 2. No Card Hover Effects ❌
**Problem**: Cards feel non-interactive
**Fix**: Add `hover:shadow-lg transition-shadow` classes
**Code**:
```html
<a href="/projects/{{ project.id }}"
   class="card hover:shadow-lg transition-shadow duration-200 group">
```

### 3. Accessibility Gaps ❌
**Problem**: Missing ARIA labels, keyboard nav broken
**Fix**:
- Add `aria-label` to icon buttons
- Add `sr-only` label to search input
- Make entire card a link (not just title)

**Effort**: 30 min + 15 min + 45 min = **1.5 hours**

---

## 5 Medium Priority Issues (1.75h)

4. No loading states (30 min)
5. Limited filters (search only, no status filter) (1h)
6. No pagination (hardcoded "Page 1 of 1") (1h)
7. Inline SVGs instead of Bootstrap Icons (30 min)
8. No empty search results state (15 min)

---

## What Works Well ✅

- Clean card grid layout (responsive 1→2→3 columns)
- Good empty state design
- Clear "Create Project" CTA
- Search functionality works
- Design system classes used correctly (mostly)

---

## Files to Modify

1. `agentpm/web/templates/projects/list.html` - Main fixes
2. `agentpm/web/app.py` - Add template filter
3. `agentpm/web/routes/projects.py` - Pagination (optional)

---

## Detailed Review

📄 **Full Report**: `docs/architecture/web/ux-review-projects-list.md`

**Includes**:
- Before/after code examples
- Design system compliance audit
- Accessibility checklist
- Testing procedures
- Implementation priority order

---

## Recommendation

✅ **Fix critical issues (1.5h)** before v1.0 launch
⚠️ **Defer medium issues** to post-launch polish

**Next**: Assign to `aipm-python-cli-developer` for implementation.
