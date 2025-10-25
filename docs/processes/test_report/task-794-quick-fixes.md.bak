# Task 794: Quick Fixes Summary

**Priority**: High
**Effort**: ~30 minutes total
**Impact**: Design system compliance + accessibility

---

## Fix #1: Confidence Colors (5 min)

**File**: `/agentpm/web/templates/contexts/list.html`
**Lines**: 126-127, 130-131

**Find**:
```html
'bg-success' if context.confidence_band == 'green' else 'bg-warning' if context.confidence_band == 'yellow' else 'bg-error'
```

**Replace with**:
```html
'bg-confidence-green' if context.confidence_band == 'green' else 'bg-confidence-yellow' if context.confidence_band == 'yellow' else 'bg-confidence-red'
```

**Do this for**:
- Progress bar background (line 126)
- Badge background (line 130)
- Badge text color (line 130)

---

## Fix #2: ARIA Labels for Progress Bars (3 min)

**File**: `/agentpm/web/templates/contexts/list.html`
**Line**: 125

**Find**:
```html
<div class="h-2 w-24 overflow-hidden rounded-full bg-gray-100">
```

**Replace with**:
```html
<div class="h-2 w-24 overflow-hidden rounded-full bg-gray-100" role="progressbar" aria-valuenow="{{ (context.confidence_score * 100)|round }}" aria-valuemin="0" aria-valuemax="100" aria-label="Confidence score">
```

---

## Fix #3: Badge Color Consistency (10 min)

**File**: `/agentpm/web/templates/contexts/list.html`
**Lines**: 27, 38

**Find (line 27)**:
```html
<span class="badge badge-{{ band if band in ['green','yellow','red'] else 'gray' }} capitalize">{{ band }}</span>
```

**Replace with**:
```html
<span class="inline-flex items-center gap-1 rounded-full {{ 'bg-confidence-green text-white' if band == 'green' else 'bg-confidence-yellow text-white' if band == 'yellow' else 'bg-confidence-red text-white' if band == 'red' else 'bg-gray-100 text-gray-700' }} px-3 py-1 text-xs font-semibold uppercase">
  <i class="bi {{ 'bi-check-circle' if band == 'green' else 'bi-exclamation-triangle' if band == 'yellow' else 'bi-x-circle' if band == 'red' else 'bi-circle' }}"></i>
  {{ band.title() if band else 'Unknown' }}
</span>
```

---

## Fix #4: Filter Form Responsive Grid (2 min)

**File**: `/agentpm/web/templates/contexts/list.html`
**Line**: 54

**Find**:
```html
<form method="GET" class="grid gap-4 md:grid-cols-3">
```

**Replace with**:
```html
<form method="GET" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
```

---

## Fix #5: Empty State Icon Accessibility (2 min)

**File**: `/agentpm/web/templates/contexts/list.html`
**Line**: 161

**Find**:
```html
<svg class="h-12 w-12 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
```

**Replace with**:
```html
<svg class="h-12 w-12 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" role="img" aria-label="No contexts available">
    <title>No contexts available</title>
```

---

## Testing Checklist

After applying fixes:

- [ ] View `/contexts` page in browser
- [ ] Inspect confidence badges (should be green/yellow/red, not generic success/warning/error)
- [ ] Test keyboard navigation (Tab key)
- [ ] Test screen reader (VoiceOver on Mac: Cmd+F5)
- [ ] Resize browser to mobile width (375px) - filter form should stack properly
- [ ] Check browser console for errors

---

## Validation

Run these commands to verify changes:

```bash
# Check for old color references
grep -r "bg-success\|bg-warning\|bg-error" agentpm/web/templates/contexts/

# Should only find detail.html (uses different pattern)
# list.html should now use bg-confidence-*

# Check for missing ARIA labels
grep -r "role=\"progressbar\"" agentpm/web/templates/contexts/

# Should find at least one match in list.html
```

---

**Total Time**: ~22 minutes
**Files Changed**: 1 (`list.html`)
**Lines Changed**: ~10 lines

**Impact**:
- ✅ Design system compliant
- ✅ WCAG AA accessible
- ✅ Consistent visual language
