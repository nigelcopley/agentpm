# APM (Agent Project Manager) Frontend Polish - Implementation Checklist

**Purpose**: Track progress on all 187 issues across 6 phases
**Format**: Interactive checklist for developers

---

## Phase 1: Foundation (Week 1) - 12 hours

### Component Library (4 hours)
- [ ] Create `components/breadcrumbs.html` (30 min)
  - [ ] `render(items)` macro
  - [ ] Home icon + chevron separators
  - [ ] Active page styling (no link)
  - [ ] Test with 1/2/3/4 level hierarchies
- [ ] Create `components/skeleton.html` (1 hour)
  - [ ] `card()` macro
  - [ ] `table(rows=5)` macro
  - [ ] `list(items=3)` macro
  - [ ] `metric()` macro
  - [ ] Test all variants
- [ ] Create `components/quick_actions.html` (1 hour)
  - [ ] `dropdown(actions, label)` macro
  - [ ] Keyboard navigation (arrow keys, Esc)
  - [ ] Divider support
  - [ ] Danger action styling
  - [ ] Test with 2/3/5 action sets
- [ ] Create `components/badge.html` (1 hour)
  - [ ] `status_badge(status)` macro
  - [ ] `role_badge(role)` macro
  - [ ] `tier_badge(tier)` macro
  - [ ] `priority_badge(priority)` macro
  - [ ] Icon + text layout
  - [ ] Test all status/role/tier combinations
- [ ] Create `components/empty_state.html` (30 min)
  - [ ] `render(icon, heading, message, cta)` macro
  - [ ] Large icon (text-6xl)
  - [ ] Heading + subtitle structure
  - [ ] Primary CTA button
  - [ ] Secondary help link
- [ ] Create `components/loading_spinner.html` (15 min)
  - [ ] Inline spinner variant
  - [ ] Full-page overlay variant
  - [ ] Test with HTMX triggers
- [ ] Create `components/toast.html` (15 min)
  - [ ] Success variant
  - [ ] Error variant
  - [ ] Warning variant
  - [ ] Info variant

### Design System Updates (2 hours)
- [ ] Update `tailwind.config.js` (1 hour)
  - [ ] Add `colors.status.*` (8 status colors)
  - [ ] Add `colors.confidence.*` (green/yellow/red)
  - [ ] Add `colors.phase.*` (d1/p1/i1/r1/o1/e1)
  - [ ] Add `colors.metric.*` (primary/active/assigned/info)
  - [ ] Add `colors.role.*` (orchestrator/specialist/sub-agent)
  - [ ] Test color palette in browser
- [ ] Update `brand-system.css` (1 hour)
  - [ ] Add `.btn.active` styles
  - [ ] Add `[data-filter-type].active` styles
  - [ ] Add focus-visible global styles
  - [ ] Add skip-link styles
  - [ ] Test button active states

### Base Template Accessibility (3 hours)
- [ ] Update `modern_base.html` (2 hours)
  - [ ] Add skip link (sr-only, focus:not-sr-only)
  - [ ] Add `role="status" aria-live="polite"` to loading overlay
  - [ ] Add main content `id="main-content"`
  - [ ] Add page title announcement (sr-only h1)
  - [ ] Test with screen reader (NVDA/VoiceOver)
- [ ] Global ARIA labels (1 hour)
  - [ ] Find all icon-only buttons (42 instances)
  - [ ] Add `aria-label` to each
  - [ ] Add `aria-hidden="true"` to icon SVGs
  - [ ] Test keyboard navigation (Tab order)

### Database Migration (2 hours)
- [ ] Create `migrations/add_agent_tier.sql` (30 min)
  - [ ] Add `tier INTEGER DEFAULT 3` to agents table
  - [ ] Populate tier: 1 for `*-orch`, 2 for `*-specialist`, 3 for others
  - [ ] Test migration on dev database
- [ ] Update `Agent` model (30 min)
  - [ ] Add `tier: int = 3` field
  - [ ] Update adapter `to_model()` method
  - [ ] Update adapter `to_row()` method
- [ ] Update `AgentInfo` view model (30 min)
  - [ ] Add `tier: int` field
  - [ ] Update blueprint to include tier
- [ ] Test tier display (30 min)
  - [ ] Verify tier badges show correct tier
  - [ ] Verify tier filtering works

### Quality Gate 1 (End of Phase 1)
- [ ] All component macros functional
- [ ] Tailwind color system working
- [ ] Base template passes accessibility audit
- [ ] Database migration successful
- [ ] **Approval**: Flask UX Designer + Quality Validator

---

## Phase 2: High-Traffic Routes (Week 2) - 12 hours

### Dashboard (2 hours)
- [ ] Add breadcrumbs (15 min)
  - [ ] `breadcrumbs = [{'name': project.name, 'url': f'/projects/{project.id}'}]`
- [ ] Add loading skeletons for metrics (1 hour)
  - [ ] Wrap metrics in Alpine.js loading state
  - [ ] Show 4 skeleton cards while loading
  - [ ] Fade in real metrics after 500ms
- [ ] Fix chart color palette (30 min)
  - [ ] Update Chart.js config to use design system colors
  - [ ] Test all chart types (bar, line, doughnut)
- [ ] Add loading state for charts (15 min)
  - [ ] Show spinner while chart data loads

### Work Items List (2 hours)
- [ ] Add breadcrumbs (15 min)
  - [ ] `breadcrumbs = [{'name': 'Work Items', 'url': None}]`
- [ ] Add skeleton loader (30 min)
  - [ ] Show 6 skeleton cards while loading
  - [ ] Fade in real work items
- [ ] Add sort controls (1 hour)
  - [ ] Sort dropdown (updated_at, created_at, priority, status, progress)
  - [ ] Sort direction toggle button
  - [ ] Update `smart-filters.js` to support sorting
  - [ ] Add data attributes to work item rows
- [ ] Fix mobile filter layout (15 min)
  - [ ] Stack filters vertically on mobile
  - [ ] Full-width selects on mobile

### Work Item Detail (1.5 hours)
- [ ] Add breadcrumbs (15 min)
  - [ ] `['Work Items', f'WI-{id}']`
- [ ] Add quick action dropdown (1 hour)
  - [ ] Edit, Duplicate, Archive, Delete actions
  - [ ] Keyboard navigation
- [ ] Add loading state for form submission (15 min)
  - [ ] Button spinner on submit

### Tasks List (2 hours)
- [ ] Add breadcrumbs (15 min)
- [ ] Add skeleton loader (30 min)
- [ ] Add sort controls (1 hour)
- [ ] Fix mobile filter layout (15 min)

### Task Detail (1.5 hours)
- [ ] Add breadcrumbs (30 min)
  - [ ] `['Work Items', f'WI-{wi_id}', 'Tasks', f'Task-{id}']`
- [ ] Add quick action dropdown (1 hour)

### Status Icons in Badges (1 hour)
- [ ] Update `work_item_card.html` (30 min)
  - [ ] Add icon logic to status badges
  - [ ] Test all status values
- [ ] Update `task_card.html` (30 min)
  - [ ] Add icon logic to status badges

### Enhanced Empty States (1.5 hours)
- [ ] Work items empty state (30 min)
- [ ] Tasks empty state (30 min)
- [ ] Filtered empty state (30 min)

### Quality Gate 2 (End of Phase 2)
- [ ] All high-traffic routes have breadcrumbs
- [ ] All high-traffic routes have loading states
- [ ] Sort controls functional
- [ ] Quick actions on detail pages
- [ ] Accessibility audit: 0 critical issues
- [ ] **Approval**: Quality Validator + Product Owner

---

## Phase 3: System Routes (Week 3) - 10 hours

### Agents List (2 hours)
- [ ] Add breadcrumbs (15 min)
- [ ] Add skeleton loader (30 min)
- [ ] Add sort controls (30 min)
- [ ] Fix role badge colors (30 min)
  - [ ] Map role suffix to color (orch=purple, specialist=blue, etc.)
- [ ] Add filter button active states (15 min)

### Agents Detail (1 hour)
- [ ] Add breadcrumbs (15 min)
- [ ] Add quick action dropdown (45 min)

### Rules List (2 hours)
- [ ] Add breadcrumbs (15 min)
- [ ] Add skeleton loader (30 min)
- [ ] Add sort controls (30 min)
- [ ] Enhanced empty state (30 min)
- [ ] Filter button active states (15 min)

### Rules Detail (1 hour)
- [ ] Add breadcrumbs (15 min)
- [ ] Add quick action dropdown (45 min)

### Projects Routes (2 hours)
- [ ] Projects list: Breadcrumbs, skeleton, empty state (1 hour)
- [ ] Project detail: Breadcrumbs, quick actions (30 min)
- [ ] Project context: Breadcrumbs (15 min)
- [ ] Project settings: Breadcrumbs, form validation (15 min)

### Database Metrics (1 hour)
- [ ] Add breadcrumbs (15 min)
- [ ] Fix chart color palette (30 min)
- [ ] Add loading states for charts (15 min)

### Workflow Visualization (1 hour)
- [ ] Add breadcrumbs (15 min)
- [ ] Add interactive state feedback (30 min)
- [ ] Add loading state (15 min)

### Quality Gate 3 (End of Phase 3)
- [ ] All system routes consistent with high-traffic
- [ ] Role badge colors semantic
- [ ] Chart colors standardized
- [ ] **Approval**: Flask UX Designer

---

## Phase 4: Content Routes (Week 4) - 8 hours

### Contexts (1.5 hours)
- [ ] List: Breadcrumbs, skeleton, empty state (1 hour)
- [ ] Detail: Breadcrumbs, quick actions (30 min)

### Documents (1 hour)
- [ ] List: Breadcrumbs, skeleton, empty state (1 hour)

### Evidence (1 hour)
- [ ] List: Breadcrumbs, skeleton, empty state (1 hour)

### Sessions (1.5 hours)
- [ ] List: Breadcrumbs, skeleton (1 hour)
- [ ] Detail: Breadcrumbs, quick actions (30 min)

### Ideas (1.5 hours)
- [ ] List: Breadcrumbs, skeleton (1 hour)
- [ ] Detail: Breadcrumbs, quick actions (30 min)

### Other Content Routes (1.5 hours)
- [ ] Events: Breadcrumbs, skeleton (30 min)
- [ ] Quality Gates: Breadcrumbs (30 min)
- [ ] Search Results: Breadcrumbs, loading state (30 min)

### Quality Gate 4 (End of Phase 4)
- [ ] All content routes have breadcrumbs
- [ ] All content routes have loading states
- [ ] All detail pages have quick actions
- [ ] Empty states engaging
- [ ] **Approval**: Flask UX Designer

---

## Phase 5: QA & Polish (Week 5) - 8 hours

### Accessibility Audit (3 hours)
- [ ] WCAG 1.3.1 Info & Relationships (45 min)
  - [ ] Verify semantic HTML on all routes
  - [ ] Check form label associations
  - [ ] Test heading hierarchy
- [ ] WCAG 1.4.3 Contrast (Minimum) (45 min)
  - [ ] Test all text/background combinations
  - [ ] Fix any contrast < 4.5:1
- [ ] WCAG 2.1.1 Keyboard (45 min)
  - [ ] Test Tab navigation on all routes
  - [ ] Test Enter/Space on all interactive elements
  - [ ] Test Esc to close modals/dropdowns
- [ ] WCAG 2.4.1 Bypass Blocks (15 min)
  - [ ] Verify skip link works
- [ ] WCAG 2.4.7 Focus Visible (30 min)
  - [ ] Test focus ring on all interactive elements
- [ ] WCAG 4.1.2 Name, Role, Value (30 min)
  - [ ] Verify ARIA labels on all icon buttons
  - [ ] Test screen reader announcements

### Screen Reader Testing (2 hours)
- [ ] NVDA (Windows) - 1 hour
  - [ ] Test 5 representative routes
  - [ ] Verify live region announcements
  - [ ] Test form error announcements
- [ ] VoiceOver (macOS) - 1 hour
  - [ ] Test 5 representative routes
  - [ ] Verify rotor navigation
  - [ ] Test landmark navigation

### Cross-Browser Testing (2 hours)
- [ ] Chrome (30 min)
  - [ ] Test all routes
  - [ ] Verify Tailwind styles
- [ ] Firefox (30 min)
  - [ ] Test all routes
  - [ ] Check custom CSS compatibility
- [ ] Safari (30 min)
  - [ ] Test all routes
  - [ ] Check Alpine.js reactivity
- [ ] Mobile Safari (iOS) (30 min)
  - [ ] Test responsive layouts
  - [ ] Check touch targets (44x44px minimum)

### Performance Optimization (1 hour)
- [ ] Run Lighthouse on 5 representative routes (30 min)
  - [ ] Dashboard
  - [ ] Work items list
  - [ ] Task detail
  - [ ] Agents list
  - [ ] Project detail
- [ ] Optimize low scores (30 min)
  - [ ] Lazy-load images
  - [ ] Defer non-critical JavaScript
  - [ ] Optimize Tailwind purge

### Quality Gate 5 (Accessibility)
- [ ] WCAG 2.1 AA compliance: 100%
- [ ] Screen reader testing passed
- [ ] Keyboard navigation: all routes functional
- [ ] **Approval**: Quality Validator + Accessibility Specialist

### Quality Gate 6 (Cross-Browser)
- [ ] Chrome: All routes functional
- [ ] Firefox: All routes functional
- [ ] Safari: All routes functional
- [ ] Mobile: All routes functional
- [ ] **Approval**: Testing Specialist

### Quality Gate 7 (Performance)
- [ ] Lighthouse Performance: ≥90
- [ ] Lighthouse Accessibility: 100
- [ ] First Contentful Paint: <1.0s
- [ ] Largest Contentful Paint: <2.5s
- [ ] **Approval**: Performance Engineer

---

## Phase 6: Documentation (Week 6) - 4 hours

### Design System Docs (1 hour)
- [ ] Update `design-system.md` (30 min)
  - [ ] Document new color extensions
  - [ ] Add component library section
- [ ] Update `component-snippets.md` (30 min)
  - [ ] Add breadcrumb examples
  - [ ] Add skeleton loader examples
  - [ ] Add quick action examples

### Component Usage Guide (1 hour)
- [ ] Create `component-usage-guide.md`
  - [ ] When to use breadcrumbs
  - [ ] When to use skeleton loaders
  - [ ] When to use quick actions
  - [ ] When to use empty states
  - [ ] Code examples for each

### Accessibility Patterns (1 hour)
- [ ] Create `accessibility-guide.md`
  - [ ] ARIA label best practices
  - [ ] Keyboard navigation patterns
  - [ ] Screen reader considerations
  - [ ] Focus management
  - [ ] Color contrast guidelines

### Developer Migration Guide (1 hour)
- [ ] Create `web-migration.md`
  - [ ] How to add breadcrumbs to a route
  - [ ] How to add loading states
  - [ ] How to add quick actions
  - [ ] How to use component macros
  - [ ] Before/after examples

### Quality Gate 8 (Documentation)
- [ ] Design system docs updated
- [ ] Component usage guide created
- [ ] Accessibility patterns documented
- [ ] Developer migration guide complete
- [ ] **Approval**: Documentation Specialist + Product Owner

---

## Post-Launch Monitoring (First 30 Days)

### Week 1 Post-Launch
- [ ] Monitor error rates (JavaScript, 500s)
- [ ] Track performance metrics (LCP, FCP, CLS)
- [ ] Collect accessibility feedback
- [ ] Monitor browser compatibility issues
- [ ] Review user engagement (page views, time on page)

### Week 2-4 Post-Launch
- [ ] Weekly UX feedback sessions
- [ ] Address any critical issues
- [ ] Document lessons learned
- [ ] Plan continuous improvement backlog

---

## Rollback Triggers (If Any of These Occur)

- [ ] Performance regression >20%
- [ ] Critical accessibility issue discovered
- [ ] Browser compatibility failure
- [ ] User-reported critical bug
- [ ] **Action**: Revert to previous version, hotfix, redeploy

---

## Summary Progress

**Phase 1**: [ ] 0/12 items complete (0%)
**Phase 2**: [ ] 0/18 items complete (0%)
**Phase 3**: [ ] 0/14 items complete (0%)
**Phase 4**: [ ] 0/10 items complete (0%)
**Phase 5**: [ ] 0/12 items complete (0%)
**Phase 6**: [ ] 0/8 items complete (0%)

**Overall Progress**: 0/74 items complete (0%)

**Estimated Completion**: Week of 2025-11-25

---

**Checklist Version**: 1.0
**Created**: 2025-10-22
**Last Updated**: 2025-10-22
**Format**: Markdown (compatible with GitHub, VS Code, Obsidian)
