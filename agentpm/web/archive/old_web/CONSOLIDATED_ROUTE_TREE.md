# APM (Agent Project Manager) Consolidated Route Tree

## "Less is More" Approach - Single Comprehensive Views

This design consolidates multiple nested routes into single, comprehensive views that show all related information in one place.

---

## Consolidated Route Structure

```
APM (Agent Project Manager) Web Application Routes (Consolidated - Read-Only)
├── / (Dashboard Blueprint)
│   ├── GET  /                    # Dashboard home
│   ├── GET  /dashboard           # Main dashboard
│   └── GET  /overview            # System overview
│
├── /ideas (Ideas Blueprint)
│   ├── GET  /ideas/                    # Ideas list
│   └── GET  /ideas/<id>                # Idea detail (includes elements, context, etc.)
│
├── /work-items (Work Items Blueprint)
│   ├── GET  /work-items/                    # Work items list
│   ├── GET  /work-items/<id>                # Work item detail (includes tasks list, dependencies, context, summaries)
│   └── GET  /work-items/<id>/tasks/<id>     # Task detail (includes task dependencies, context, etc.)
│
├── /context (Context Blueprint)
│   ├── GET  /context/                    # Context overview (includes all context types)
│   ├── GET  /context/documents           # Documents list
│   ├── GET  /context/evidence            # Evidence list
│   ├── GET  /context/events              # Events list
│   └── GET  /context/sessions            # Sessions list
│
├── /agents (Agents Blueprint)
│   ├── GET  /agents/                    # Agents list
│   └── GET  /agents/<id>                # Agent detail (includes all agent info)
│
├── /rules (Rules Blueprint)
│   ├── GET  /rules/                    # Rules list
│   └── GET  /rules/<id>                # Rule detail (includes all rule info)
│
├── /system (System Blueprint)
│   ├── GET  /system/health             # System health check
│   ├── GET  /system/database           # Database metrics
│   ├── GET  /system/context-files      # Context files list
│   ├── GET  /system/logs               # System logs
│   ├── GET  /system/metrics            # System metrics
│   └── GET  /system/settings           # System settings
│
└── /search (Search Blueprint)
    ├── GET  /search/                   # Search results
    └── GET  /search/history            # Search history
```

## Key Consolidation Changes

### ✅ **Work Items - Consolidated with Task Details:**
**Before (8 routes):**
- `/work-items/` - List
- `/work-items/<id>` - Detail
- `/work-items/<id>/tasks` - Tasks list
- `/work-items/<id>/tasks/<id>` - Task detail
- `/work-items/<id>/dependencies` - Dependencies
- `/work-items/<id>/context` - Context
- `/work-items/<id>/summaries` - Summaries

**After (3 routes):**
- `/work-items/` - List
- `/work-items/<id>` - **Comprehensive detail view** (includes tasks list, dependencies, context, summaries in tabs/sections)
- `/work-items/<id>/tasks/<id>` - **Task detail view** (includes task dependencies, context, etc.)

### ✅ **Ideas - Single Comprehensive View:**
**Before (4 routes):**
- `/ideas/` - List
- `/ideas/<id>` - Detail
- `/ideas/<id>/elements` - Elements list
- `/ideas/<id>/elements/<id>` - Element detail

**After (2 routes):**
- `/ideas/` - List
- `/ideas/<id>` - **Comprehensive detail view** (includes elements, context, etc. in tabs/sections)

### ✅ **Context - Simplified Structure:**
**Before (9 routes):**
- `/context/` - Overview
- `/context/documents/` - Documents list
- `/context/documents/<id>` - Document detail
- `/context/evidence/` - Evidence list
- `/context/evidence/<id>` - Evidence detail
- `/context/events/` - Events list
- `/context/events/<id>` - Event detail
- `/context/sessions/` - Sessions list
- `/context/sessions/<id>` - Session detail

**After (5 routes):**
- `/context/` - **Comprehensive overview** (includes all context types in sections)
- `/context/documents/` - Documents list
- `/context/evidence/` - Evidence list
- `/context/events/` - Events list
- `/context/sessions/` - Sessions list

### ✅ **Agents - Single Comprehensive View:**
**Before (3 routes):**
- `/agents/` - List
- `/agents/<id>` - Detail
- `/agents/generate` - Generate form

**After (2 routes):**
- `/agents/` - List
- `/agents/<id>` - **Comprehensive detail view** (includes generation info, etc.)

### ✅ **Rules - Single Comprehensive View:**
**Before (2 routes):**
- `/rules/` - List
- `/rules/<id>` - Detail

**After (2 routes):**
- `/rules/` - List
- `/rules/<id>` - **Comprehensive detail view** (includes all rule info)

### ✅ **System - Simplified Structure:**
**Before (8 routes):**
- `/system/health` - Health check
- `/system/database` - Database metrics
- `/system/context-files/` - Files list
- `/system/context-files/preview/<path>` - File preview
- `/system/context-files/download/<path>` - File download
- `/system/logs/` - Logs
- `/system/metrics/` - Metrics
- `/system/settings/` - Settings

**After (6 routes):**
- `/system/health` - Health check
- `/system/database` - Database metrics
- `/system/context-files/` - **Files list with preview/download inline**
- `/system/logs/` - Logs
- `/system/metrics/` - Metrics
- `/system/settings/` - Settings

### ✅ **Search - Simplified Structure:**
**Before (3 routes):**
- `/search/` - Search results
- `/search/suggestions` - Suggestions
- `/search/history` - History

**After (2 routes):**
- `/search/` - **Search results with suggestions inline**
- `/search/history` - History

## Final Route Statistics (Consolidated)

### By Blueprint
- **Dashboard**: 3 routes
- **Ideas**: 2 routes
- **Work Items**: 3 routes
- **Context**: 5 routes
- **Agents**: 2 routes
- **Rules**: 2 routes
- **System**: 6 routes
- **Search**: 2 routes

### By HTTP Method
- **GET**: 25 routes (all routes are read-only)

### Total Routes: 25 (vs 40 in previous version)

## Benefits of Consolidation

### ✅ **User Experience:**
1. **Single Source of Truth** - All related information in one view
2. **Reduced Navigation** - No need to click through multiple pages
3. **Better Context** - See relationships between data
4. **Faster Workflow** - Less page loads and navigation

### ✅ **Development:**
1. **Fewer Routes** - 24 vs 40 routes (40% reduction)
2. **Simpler Navigation** - Less complex routing logic
3. **Easier Maintenance** - Fewer templates and route handlers
4. **Better Performance** - Fewer HTTP requests

### ✅ **Template Design:**
1. **Tabbed Interfaces** - Use tabs/sections within detail views
2. **Accordion Layouts** - Collapsible sections for different data types
3. **Sidebar Navigation** - Quick jump to different sections
4. **Responsive Design** - Better mobile experience

## Implementation Strategy

### Phase 1 (Essential Views - 13 routes)
- Dashboard (3 routes)
- Ideas (2 routes)
- Work Items (3 routes)
- Agents (2 routes)
- Rules (2 routes)
- System health/database (2 routes)

### Phase 2 (Detailed Views - 12 routes)
- Context (5 routes)
- System files/logs/metrics (4 routes)
- Search (2 routes)
- System settings (1 route)

## Next Steps

1. **Design Comprehensive Templates** - Create tabbed/sectioned detail views
2. **Implement Consolidated Routes** - Update blueprint structure
3. **Update Navigation** - Simplify navigation to match consolidated structure
4. **Test All Views** - Ensure all consolidated views work properly
5. **Add Interactivity Later** - When ready, add actions within consolidated views

---

**Note**: This consolidated approach follows the "less is more" principle, providing a cleaner, more efficient user experience while reducing complexity for both users and developers.
