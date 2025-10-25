# Responsive Design Testing Checklist - APM (Agent Project Manager)

**Purpose**: Manual testing checklist for verifying responsive design across all breakpoints
**Related Document**: `responsive-design-audit-report.md`
**Last Updated**: 2025-10-22

---

## Testing Setup

### Required Devices

**Mobile** (Required):
- [ ] iPhone SE (375×667 - smallest modern iPhone)
- [ ] iPhone 14 Pro (393×852 - standard iPhone)
- [ ] Samsung Galaxy S21 (360×800 - standard Android)
- [ ] Pixel 7 (412×915 - large Android)

**Tablet** (Recommended):
- [ ] iPad (768×1024 - standard tablet)
- [ ] iPad Pro 11" (834×1194 - large tablet)

**Desktop** (Required):
- [ ] 1280×800 (minimum desktop)
- [ ] 1920×1080 (standard desktop)
- [ ] 2560×1440 (large desktop)

### Browser Requirements

**Mobile**:
- [ ] Safari (iOS)
- [ ] Chrome (Android)

**Desktop**:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (macOS)
- [ ] Edge (latest)

### Testing Tools

**Chrome DevTools**:
- [ ] Device toolbar (Cmd/Ctrl + Shift + M)
- [ ] Responsive mode with custom viewport
- [ ] Network throttling (3G/4G simulation)

**Browser Extensions**:
- [ ] axe DevTools (accessibility)
- [ ] Lighthouse (performance + accessibility)

---

## 1. Global Layout Tests

### All Breakpoints (320px, 375px, 414px, 768px, 1024px, 1280px, 1920px)

#### Base Layout
- [ ] No horizontal scroll on any page
- [ ] All content visible without zooming
- [ ] Margins/padding appropriate for screen size
- [ ] Container max-width respected (max-w-7xl)

#### Header
- [ ] Logo visible and not distorted
- [ ] Navigation accessible (mobile menu on <768px)
- [ ] Search input functional
- [ ] User menu accessible
- [ ] WebSocket status indicator visible (on >640px)

#### Footer (if present)
- [ ] Footer content visible
- [ ] Links accessible and properly sized

---

## 2. Route-Specific Tests

### 2.1 Dashboard (`/`)

#### Mobile (320px-767px)
- [ ] **Metric cards**: Stack vertically (1 column)
- [ ] **Card padding**: Not cramped (comfortable spacing)
- [ ] **Icons**: Visible and not cut off
- [ ] **Recent work items**: Full-width cards, readable
- [ ] **Recent tasks**: Full-width cards, readable
- [ ] **Quick actions grid**: 1 column, cards tappable
- [ ] **No horizontal scroll**: Entire page

**320px Specific**:
- [ ] Metric card numbers not truncated
- [ ] Icon sizes appropriate (not too large)

#### Tablet (768px-1023px)
- [ ] **Metric cards**: 2 columns
- [ ] **Quick actions**: 2 columns
- [ ] **Recent items**: 2 columns or comfortable list

#### Desktop (1024px+)
- [ ] **Metric cards**: 4 columns
- [ ] **Quick actions**: 4 columns
- [ ] **All elements**: Visible without scroll
- [ ] **Sidebar**: Visible (if applicable)

---

### 2.2 Work Items List (`/work-items`)

#### Mobile (320px-767px)
- [ ] **Search bar**: Full-width, functional
- [ ] **Filters**: Accessible (collapsible or stacked)
  - [ ] Status filter accessible
  - [ ] Type filter accessible
  - [ ] Priority filter accessible
  - [ ] Clear filters button visible
- [ ] **Work item cards**: Stack vertically (1 column)
- [ ] **Card content**: Readable, not cramped
  - [ ] Title visible, not truncated
  - [ ] Status badge visible
  - [ ] Priority badge visible
  - [ ] Progress bar visible
  - [ ] Task counts visible
- [ ] **Action buttons**: Min 44×44px, tappable
- [ ] **No horizontal scroll**: Entire list

**Filter Issues** (Current):
- [ ] ⚠️ 3 dropdowns + button = overflow? (document if yes)
- [ ] Proposed fix: Collapsible filter panel needed?

#### Tablet (768px-1023px)
- [ ] **Work item cards**: 2 columns
- [ ] **Filters**: Horizontal layout, no overflow
- [ ] **All content**: Comfortable spacing

#### Desktop (1024px+)
- [ ] **Work item cards**: 3 columns (xl: 4 columns at 1280px+)
- [ ] **Filters**: All inline, no overflow
- [ ] **Sidebar**: Visible (if enabled)

---

### 2.3 Work Item Detail (`/work-items/<id>`)

#### Mobile (320px-767px)
- [ ] **Header**: Title + badges stack properly
- [ ] **Tabs**: Horizontal scroll if needed, or stack
- [ ] **Action buttons**: Min 44×44px
  - [ ] Edit button tappable
  - [ ] Status buttons tappable
  - [ ] Delete button (if present) tappable
- [ ] **Content sections**: Full-width, readable
- [ ] **Task list**: Cards stack vertically
- [ ] **No horizontal scroll**: Entire page

#### Tablet (768px-1023px)
- [ ] **Tabs**: All visible without scroll (if <6 tabs)
- [ ] **Content**: 2-column layout (if applicable)

#### Desktop (1024px+)
- [ ] **All content**: Visible without scroll
- [ ] **Tabs**: All visible
- [ ] **Sidebar**: Related items visible (if applicable)

---

### 2.4 Tasks List (`/tasks`)

#### Mobile (320px-767px)
- [ ] **Search bar**: Full-width, functional
- [ ] **Filters**: Accessible (collapsible or stacked)
  - [ ] Status filter accessible
  - [ ] Type filter accessible
  - [ ] Clear filters button visible
- [ ] **Task items**: Stack vertically, full-width
- [ ] **Task cards**: Readable, not cramped
  - [ ] Task name visible
  - [ ] Status indicator visible
  - [ ] Type badge visible
  - [ ] Work item link visible
  - [ ] Effort hours visible
- [ ] **Action buttons**: Min 44×44px
- [ ] **No horizontal scroll**: Entire list

#### Tablet (768px-1023px)
- [ ] **Task cards**: 2 columns or comfortable list
- [ ] **Filters**: Horizontal layout, no overflow

#### Desktop (1024px+)
- [ ] **Task cards**: 3 columns or optimized list
- [ ] **Filters**: All inline, no overflow

---

### 2.5 Agents List (`/agents`)

#### Mobile (320px-767px)
- [ ] **🔴 CRITICAL**: Table has mobile card alternative
  - [ ] If table: Horizontal scroll present (document)
  - [ ] If cards: Cards stack vertically
  - [ ] Agent name visible
  - [ ] Role visible
  - [ ] Active status visible
  - [ ] Task counts visible
- [ ] **Filter buttons**: No overflow, properly wrapped
- [ ] **"Generate Agents" button**: Min 44×44px
- [ ] **No horizontal scroll**: Entire page (except table if not fixed)

**Current Issue**:
- [ ] ❌ 7-column table causes horizontal scroll (verify)
- [ ] Proposed fix: Mobile card view needed

#### Tablet (768px-1023px)
- [ ] **Table**: All columns visible, or comfortable card grid
- [ ] **Filters**: Properly laid out

#### Desktop (1024px+)
- [ ] **Table**: All 7 columns visible, no scroll
- [ ] **Filters**: All inline, properly spaced

---

### 2.6 Search Results (`/search`)

#### Mobile (320px-767px)
- [ ] **Search form**: Stacks vertically
  - [ ] Search input full-width
  - [ ] Entity type dropdown full-width
  - [ ] Search button full-width
- [ ] **Result cards**: Full-width, readable
  - [ ] Title visible, highlighted terms clear
  - [ ] Snippet visible
  - [ ] Metadata visible (entity type, date, status)
  - [ ] "View" button min 44×44px
- [ ] **Pagination**: Buttons not cramped
  - [ ] Previous/Next buttons min 44×44px
  - [ ] Page numbers tappable
- [ ] **No horizontal scroll**: Entire page

#### Tablet (768px-1023px)
- [ ] **Search form**: Horizontal layout (input + dropdown + button)
- [ ] **Result cards**: Full-width or 2 columns
- [ ] **Pagination**: Full desktop layout

#### Desktop (1024px+)
- [ ] **Search form**: Horizontal with max-width
- [ ] **Result cards**: Optimized layout
- [ ] **Pagination**: All page numbers visible

---

## 3. Component-Specific Tests

### 3.1 Work Item Card Component

#### Mobile (320px-767px)
- [ ] **Card header**: Title + badges stack or wrap properly
- [ ] **Progress bar**: Full-width, visible
- [ ] **Task status grid**: 4 columns fit comfortably
  - [ ] If cramped: Should be 2×2 grid (document)
- [ ] **Action buttons**: Footer buttons not cramped
  - [ ] "View Details" button min 44×44px
  - [ ] Icon buttons min 44×44px
- [ ] **Metadata**: Icons + text visible, not truncated

**Current Issue**:
- [ ] ⚠️ 4-column task grid cramped on 320px? (verify)
- [ ] Proposed fix: 2×2 grid on mobile

#### Tablet (768px-1023px)
- [ ] **Card layout**: Optimal, all elements visible
- [ ] **4-column task grid**: Comfortable spacing

#### Desktop (1024px+)
- [ ] **Hover effects**: Card lifts on hover (transform)
- [ ] **All elements**: Visible, well-spaced

---

### 3.2 Header Component

#### Mobile (320px-767px)
- [ ] **Logo**: Icon visible, text hidden (`hidden sm:block`)
- [ ] **Desktop search**: Hidden (`hidden md:flex`)
- [ ] **Mobile search**: Visible in separate row (`md:hidden`)
- [ ] **Mobile menu button**: Visible, min 44×44px
- [ ] **Mobile menu**: Opens on tap, full navigation visible
  - [ ] Home link
  - [ ] Work Items link
  - [ ] Tasks link
  - [ ] Sessions link
  - [ ] Ideas link
  - [ ] Contexts link
  - [ ] Documents link
- [ ] **User menu**: Dropdown accessible on tap

#### Tablet (768px-1023px)
- [ ] **Logo**: Icon + text visible
- [ ] **Search**: In header (not separate row)
- [ ] **Navigation**: Pill-style tabs visible
- [ ] **Mobile menu**: Hidden

#### Desktop (1024px+)
- [ ] **Full header**: All elements visible
- [ ] **Search**: Keyboard shortcut (Cmd/Ctrl+K) works
- [ ] **Navigation**: All tabs visible, active state correct

---

### 3.3 Forms (Work Item/Task Create/Edit)

#### Mobile (320px-767px)
- [ ] **Form inputs**: Full-width
- [ ] **Labels**: Visible above inputs
- [ ] **Input fields**: Min height for touch (py-2 ≈ 42px)
- [ ] **Dropdowns**: Full-width, tappable
- [ ] **Text areas**: Full-width, adequate height
- [ ] **Submit button**: Full-width or min 44×44px
- [ ] **Cancel button**: Full-width or min 44×44px
- [ ] **Validation errors**: Visible, readable

#### Tablet (768px-1023px)
- [ ] **Form layout**: 1-2 columns (as appropriate)
- [ ] **Buttons**: Side-by-side (if space allows)

#### Desktop (1024px+)
- [ ] **Form layout**: Optimized multi-column (if applicable)
- [ ] **Buttons**: Right-aligned or centered

---

## 4. Interaction Tests

### 4.1 Touch Targets (Mobile Only)

**Requirement**: Minimum 44×44px for all interactive elements (WCAG 2.1 AA)

#### Buttons
- [ ] **Primary buttons**: ≥44×44px
- [ ] **Secondary buttons**: ≥44×44px
- [ ] **Small buttons** (`.btn-sm`): ≥44×44px (verify)
- [ ] **Icon-only buttons**: ≥44×44px (verify)
- [ ] **Pagination buttons**: ≥44×44px
- [ ] **Filter buttons**: ≥44×44px

#### Links
- [ ] **Card titles**: Tappable area ≥44×44px (or full card tappable)
- [ ] **Navigation links**: ≥44×44px
- [ ] **Breadcrumb links**: ≥44×44px

#### Form Elements
- [ ] **Checkboxes**: Tap area ≥44×44px (including label)
- [ ] **Radio buttons**: Tap area ≥44×44px (including label)
- [ ] **Dropdowns**: ≥44×44px height

**Testing Method**: Use browser DevTools to measure elements:
1. Inspect element
2. Check computed width × height
3. Verify ≥44px for both dimensions

---

### 4.2 Scroll Behavior

#### Mobile
- [ ] **Vertical scroll**: Smooth, no jank
- [ ] **No horizontal scroll**: On any page (critical)
- [ ] **Scroll position**: Preserved when navigating back
- [ ] **Sticky header**: Stays at top (if applicable)

#### Desktop
- [ ] **Vertical scroll**: Smooth
- [ ] **Horizontal scroll**: Only on intended elements (tables with overflow)
- [ ] **Sticky elements**: Function correctly

---

### 4.3 Alpine.js Interactions

#### Mobile
- [ ] **Mobile menu**: Opens/closes smoothly (Alpine.js `x-show`, `x-transition`)
- [ ] **Dropdowns**: Open/close on tap (including `@click.away`)
- [ ] **Modals**: Open/close, overlay visible
- [ ] **Filter panels**: Expand/collapse (if implemented)

#### Desktop
- [ ] **Dropdowns**: Open on click, close on click-away
- [ ] **Modals**: Open/close, keyboard ESC works
- [ ] **Tooltips**: Show on hover (if implemented)

---

## 5. Accessibility Tests (WCAG 2.1 AA)

### 5.1 Color Contrast

**Requirement**: 4.5:1 for normal text, 3:1 for large text

- [ ] **Body text** (Gray-700 on white): ≥4.5:1 (6.5:1 ✓)
- [ ] **Headings** (Gray-900 on white): ≥4.5:1 (13.5:1 ✓)
- [ ] **Secondary text** (Gray-500 on white): ≥4.5:1 (verify ~4.6:1)
- [ ] **Badges**: All colors meet WCAG AA
- [ ] **Links**: Default color meets contrast requirement
- [ ] **Button text**: Meets contrast on all button variants

**Testing Tool**: Use browser DevTools Accessibility panel or axe DevTools

---

### 5.2 Keyboard Navigation

- [ ] **Tab order**: Logical, follows visual order
- [ ] **Focus visible**: All interactive elements have visible focus state
- [ ] **Skip links**: Present (if applicable)
- [ ] **Modals**: Focus trapped inside modal when open
- [ ] **Dropdowns**: Accessible via keyboard (arrow keys, ESC)
- [ ] **Search**: Cmd/Ctrl+K focuses search input

---

### 5.3 Screen Reader (Optional - Advanced)

**Tools**: VoiceOver (macOS/iOS), NVDA (Windows), TalkBack (Android)

- [ ] **Page title**: Announced correctly
- [ ] **Headings**: Proper hierarchy (h1 → h2 → h3)
- [ ] **Form labels**: Associated with inputs (for/id)
- [ ] **ARIA labels**: Icon-only buttons have `aria-label`
- [ ] **Live regions**: Dynamic content updates announced (if applicable)

---

## 6. Performance Tests

### 6.1 Page Load

**Target**: First Contentful Paint <2s on 3G

- [ ] **Dashboard**: Loads in <2s
- [ ] **Work Items List**: Loads in <2s
- [ ] **Tasks List**: Loads in <2s
- [ ] **Agents List**: Loads in <2s

**Testing**: Chrome DevTools Network tab, throttle to "Slow 3G"

---

### 6.2 Layout Shift (CLS)

**Target**: Cumulative Layout Shift <0.1

- [ ] **No shift**: Metric cards load without shift
- [ ] **No flash**: Alpine.js elements use `x-cloak` (no FOUC)
- [ ] **Images**: Have width/height attributes (if applicable)

**Testing**: Lighthouse report, check CLS score

---

### 6.3 JavaScript Errors

- [ ] **No console errors**: On page load
- [ ] **No console errors**: On interactions (clicks, form submits)
- [ ] **Alpine.js**: Initializes correctly (check `x-data` scopes)

---

## 7. Browser-Specific Tests

### 7.1 Safari (iOS)

**Known Issues**:
- [ ] **Input zoom**: Check if inputs <16px font-size cause zoom on focus
- [ ] **Alpine.js**: Verify `x-cloak` prevents flash
- [ ] **Sticky header**: Works correctly (Safari has issues with position:sticky)

**Fix**: Add to all form inputs:
```css
/* Prevent iOS zoom on input focus */
input, select, textarea {
  font-size: 16px;
}
```

---

### 7.2 Chrome (Android)

- [ ] **Touch events**: Tap, swipe work correctly
- [ ] **Virtual keyboard**: Doesn't obscure inputs
- [ ] **Scroll performance**: Smooth, no jank

---

### 7.3 Desktop Browsers

- [ ] **Chrome**: All features work
- [ ] **Firefox**: All features work (check Alpine.js compatibility)
- [ ] **Safari (macOS)**: All features work
- [ ] **Edge**: All features work

---

## 8. Documentation & Reporting

### Test Results Template

For each route tested, document:

```markdown
### Route: /work-items

**Breakpoint: 320px (Mobile)**
- ✅ Search bar full-width
- ❌ Filters overflow (3 dropdowns + button)
- ✅ Work item cards stack vertically
- ⚠️ Action buttons slightly cramped (40px height, need 44px)

**Issues Found**:
1. Filter overflow on mobile (320px-640px)
   - Severity: HIGH
   - Proposed fix: Collapsible filter panel
   - Effort: 1.5 hours

2. Touch target size (action buttons)
   - Severity: MEDIUM (accessibility)
   - Proposed fix: Add `min-h-[44px]` to `.btn-sm`
   - Effort: 0.5 hours

**Breakpoint: 768px (Tablet)**
- ✅ All tests passed

**Breakpoint: 1024px (Desktop)**
- ✅ All tests passed
```

---

### Issue Priority

**🔴 HIGH** (Blocking):
- Horizontal scroll on any page
- Content not accessible (hidden/cut off)
- Touch targets <40px (severe accessibility issue)

**🟡 MEDIUM** (Important):
- Touch targets 40-43px (borderline accessibility)
- Filter overflow (usability issue)
- Layout cramping (poor UX)

**🟢 LOW** (Nice to have):
- Padding optimization
- Icon size adjustments
- Spacing tweaks

---

## 9. Sign-Off

### Tester Information

- **Tester Name**: ___________________
- **Date**: ___________________
- **Testing Duration**: ___________________

### Device Coverage

- [ ] Tested on ≥2 mobile devices
- [ ] Tested on ≥1 tablet device
- [ ] Tested on ≥3 desktop viewports
- [ ] Tested on ≥3 desktop browsers

### Overall Assessment

- **Responsive Design Score**: _____ / 100
- **Critical Issues Found**: _____
- **Medium Issues Found**: _____
- **Low Issues Found**: _____

### Recommendations

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

### Approval

- [ ] **Approved**: All critical and medium issues resolved
- [ ] **Conditional**: Approved with known low-priority issues documented
- [ ] **Rejected**: Critical issues remain, requires rework

**Signature**: ___________________
**Date**: ___________________

---

**Document Version**: 1.0
**Last Updated**: 2025-10-22
**Related**: `responsive-design-audit-report.md`
