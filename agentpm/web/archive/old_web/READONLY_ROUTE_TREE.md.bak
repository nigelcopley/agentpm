# APM (Agent Project Manager) Read-Only Route Tree

## Current System State Analysis

Based on your feedback, the current system is:
- **Read-only views** (no full CRUD operations)
- **Minimal interactivity** (settings/config only)
- **No API endpoints** (not implemented yet)
- **Ideas need elements model** (to be added)

---

## Read-Only Route Structure

```
APM (Agent Project Manager) Web Application Routes (Read-Only)
├── / (Dashboard Blueprint)
│   ├── GET  /                    # Dashboard home
│   ├── GET  /dashboard           # Main dashboard
│   └── GET  /overview            # System overview
│
├── /ideas (Ideas Blueprint)
│   ├── GET  /ideas/                    # Ideas list
│   ├── GET  /ideas/<id>                # Idea detail
│   │
│   └── /ideas/<id>/elements (Idea Elements - TO BE ADDED)
│       ├── GET  /ideas/<id>/elements           # List elements
│       └── GET  /ideas/<id>/elements/<id>      # Element detail
│
├── /work-items (Work Items Blueprint)
│   ├── GET  /work-items/                    # Work items list
│   ├── GET  /work-items/<id>                # Work item detail
│   │
│   ├── /work-items/<id>/tasks (Work Item Tasks)
│   │   ├── GET  /work-items/<id>/tasks           # List tasks
│   │   └── GET  /work-items/<id>/tasks/<id>      # Task detail
│   │
│   ├── /work-items/<id>/dependencies
│   │   └── GET  /work-items/<id>/dependencies           # List dependencies
│   │
│   ├── /work-items/<id>/context
│   │   └── GET  /work-items/<id>/context        # View context
│   │
│   └── GET  /work-items/<id>/summaries          # Work item summaries
│
├── /context (Context Blueprint)
│   ├── GET  /context/                    # Context overview
│   │
│   ├── /context/documents
│   │   ├── GET  /context/documents/                    # Documents list
│   │   └── GET  /context/documents/<id>                # Document detail
│   │
│   ├── /context/evidence
│   │   ├── GET  /context/evidence/                    # Evidence list
│   │   └── GET  /context/evidence/<id>                # Evidence detail
│   │
│   ├── /context/events
│   │   ├── GET  /context/events/                    # Events list
│   │   └── GET  /context/events/<id>                # Event detail
│   │
│   └── /context/sessions
│       ├── GET  /context/sessions/                    # Sessions list
│       └── GET  /context/sessions/<id>                # Session detail
│
├── /agents (Agents Blueprint)
│   ├── GET  /agents/                    # Agents list
│   ├── GET  /agents/<id>                # Agent detail
│   └── GET  /agents/generate            # Generate agents form (read-only)
│
├── /rules (Rules Blueprint)
│   ├── GET  /rules/                    # Rules list
│   └── GET  /rules/<id>                # Rule detail
│
├── /system (System Blueprint)
│   ├── GET  /system/health             # System health check
│   ├── GET  /system/database           # Database metrics
│   ├── GET  /system/context-files      # Context files list
│   ├── GET  /system/context-files/preview/<path>  # File preview
│   ├── GET  /system/context-files/download/<path> # File download
│   ├── GET  /system/logs               # System logs
│   ├── GET  /system/metrics            # System metrics
│   └── GET  /system/settings           # System settings (read-only)
│
└── /search (Search Blueprint)
    ├── GET  /search/                   # Search results
    ├── GET  /search/suggestions        # Search suggestions
    └── GET  /search/history            # Search history
```

## Key Changes Made

### Removed (Not Currently Needed):
1. **All API endpoints** - No API methods implemented yet
2. **All action routes** - No interactivity needed at this stage
3. **All PUT/POST/DELETE routes** - Read-only system
4. **Import/Export functionality** - Not implemented
5. **File upload/delete** - Not implemented
6. **Database backup/restore** - Not implemented
7. **Workflow validation** - Not implemented

### Added (Missing from Previous):
1. **Ideas Elements** - Need to add elements model to ideas
2. **Projects Blueprint** - Was completely missing

### Kept (Essential Read-Only Views):
1. **All GET routes** - For viewing data
2. **System health/database** - For monitoring
3. **File preview/download** - For viewing context files
4. **Search functionality** - For finding information
5. **Settings view** - For configuration (read-only)

## Route Statistics (Read-Only)

### By Blueprint
- **Dashboard**: 3 routes
- **Ideas**: 4 routes (2 main + 2 elements)
- **Work Items**: 8 routes (2 main + 6 nested)
- **Context**: 9 routes (1 main + 8 nested)
- **Agents**: 3 routes
- **Rules**: 2 routes
- **System**: 8 routes
- **Search**: 3 routes

### By HTTP Method
- **GET**: 40 routes (all routes are read-only)

### Total Routes: 40 (vs 43 in previous version)

## Implementation Priority

### Phase 1 (Essential Views - 17 routes)
- Dashboard (3 routes)
- Ideas (4 routes)
- Work Items main (2 routes)
- Agents (3 routes)
- Rules (2 routes)
- System health/database (2 routes)
- Search (3 routes)

### Phase 2 (Detailed Views - 23 routes)
- Work Items nested (6 routes)
- Context main (1 route)
- Context documents (2 routes)
- Context evidence (2 routes)
- Context events (2 routes)
- Context sessions (2 routes)
- System files/logs/metrics (6 routes)
- System settings (1 route)

## Next Steps

1. **Add Ideas Elements Model** - Need to create the elements model for ideas
2. **Implement Read-Only Templates** - Create templates for all 40 routes
3. **Add Navigation** - Update navigation to match this simplified structure
4. **Test All Routes** - Ensure all routes work with existing database methods
5. **Add Interactivity Later** - When ready, add action routes and CRUD operations

---

**Note**: This read-only route structure reflects the current system state - a viewing and monitoring interface with minimal interactivity, focusing on displaying the rich data that APM (Agent Project Manager) already manages.
