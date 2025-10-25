# APM (Agent Project Manager) Route Tree View

## Comprehensive Route Structure Overview

This document shows the complete tree structure of the proposed routes, organized by blueprint and hierarchy.

```
APM (Agent Project Manager) Web Application Routes
├── / (Dashboard Blueprint)
│   ├── GET  /                    # Dashboard home
│   ├── GET  /dashboard           # Main dashboard
│   └── GET  /overview            # System overview
│
├── /ideas (Ideas Blueprint)
│   ├── GET     /ideas/                    # Ideas list
│   ├── GET     /ideas/<id>                # Idea detail
│   ├── PUT     /ideas/<id>                # Update idea
│   ├── DELETE  /ideas/<id>                # Delete idea
│   ├── POST    /ideas/<id>/actions/vote   # Vote on idea
│   ├── POST    /ideas/<id>/actions/transition # Transition idea
│   ├── POST    /ideas/<id>/actions/convert # Convert to work item
│   │
│   └── /ideas/<id>/elements (Idea Elements)
│       ├── GET     /ideas/<id>/elements           # List elements
│       ├── GET     /ideas/<id>/elements/<id>      # Element detail
│       ├── PUT     /ideas/<id>/elements/<id>      # Update element
│       └── DELETE  /ideas/<id>/elements/<id>      # Delete element
│
├── /work-items (Work Items Blueprint)
│   ├── GET     /work-items/                    # Work items list
│   ├── GET     /work-items/<id>                # Work item detail
│   ├── PUT     /work-items/<id>                # Update work item
│   ├── DELETE  /work-items/<id>                # Delete work item
│   ├── POST    /work-items/<id>/actions/start   # Start work item
│   ├── POST    /work-items/<id>/actions/complete # Complete work item
│   ├── POST    /work-items/<id>/actions/block   # Block work item
│   ├── POST    /work-items/<id>/actions/unblock # Unblock work item
│   │
│   ├── /work-items/<id>/tasks (Work Item Tasks)
│   │   ├── GET     /work-items/<id>/tasks           # List tasks
│   │   ├── GET     /work-items/<id>/tasks/<id>      # Task detail
│   │   ├── PUT     /work-items/<id>/tasks/<id>      # Update task
│   │   ├── DELETE  /work-items/<id>/tasks/<id>      # Delete task
│   │   ├── POST    /work-items/<id>/tasks/<id>/actions/assign   # Assign task
│   │   ├── POST    /work-items/<id>/tasks/<id>/actions/start    # Start task
│   │   ├── POST    /work-items/<id>/tasks/<id>/actions/complete # Complete task
│   │   ├── POST    /work-items/<id>/tasks/<id>/actions/block    # Block task
│   │   └── POST    /work-items/<id>/tasks/<id>/actions/unblock  # Unblock task
│   │
│   ├── /work-items/<id>/dependencies
│   │   ├── GET     /work-items/<id>/dependencies           # List dependencies
│   │   ├── POST    /work-items/<id>/dependencies           # Add dependency
│   │   └── DELETE  /work-items/<id>/dependencies/<id>      # Remove dependency
│   │
│   ├── /work-items/<id>/context
│   │   ├── GET     /work-items/<id>/context        # View context
│   │   └── POST    /work-items/<id>/context        # Refresh context
│   │
│   └── GET     /work-items/<id>/summaries          # Work item summaries
│
├── /context (Context Blueprint)
│   ├── GET  /context/                    # Context overview
│   │
│   ├── /context/documents
│   │   ├── GET     /context/documents/                    # Documents list
│   │   ├── GET     /context/documents/<id>                # Document detail
│   │   ├── PUT     /context/documents/<id>                # Update document
│   │   ├── DELETE  /context/documents/<id>                # Delete document
│   │   ├── POST    /context/documents/<id>/actions/refresh # Refresh document
│   │   └── GET     /context/documents/<id>/actions/download # Download document
│   │
│   ├── /context/evidence
│   │   ├── GET     /context/evidence/                    # Evidence list
│   │   ├── GET     /context/evidence/<id>                # Evidence detail
│   │   ├── PUT     /context/evidence/<id>                # Update evidence
│   │   ├── DELETE  /context/evidence/<id>                # Delete evidence
│   │   ├── POST    /context/evidence/<id>/actions/validate # Validate evidence
│   │   └── POST    /context/evidence/<id>/actions/verify  # Verify evidence
│   │
│   ├── /context/events
│   │   ├── GET     /context/events/                    # Events list
│   │   ├── GET     /context/events/<id>                # Event detail
│   │   ├── PUT     /context/events/<id>                # Update event
│   │   └── DELETE  /context/events/<id>                # Delete event
│   │
│   └── /context/sessions
│       ├── GET     /context/sessions/                    # Sessions list
│       ├── GET     /context/sessions/<id>                # Session detail
│       ├── PUT     /context/sessions/<id>                # Update session
│       ├── DELETE  /context/sessions/<id>                # Delete session
│       └── GET     /context/sessions/timeline            # Sessions timeline
│
├── /agents (Agents Blueprint)
│   ├── GET     /agents/                    # Agents list
│   ├── GET     /agents/<id>                # Agent detail
│   ├── PUT     /agents/<id>                # Update agent
│   ├── DELETE  /agents/<id>                # Delete agent
│   ├── POST    /agents/<id>/actions/toggle # Toggle agent status
│   ├── POST    /agents/<id>/actions/activate   # Activate agent
│   ├── POST    /agents/<id>/actions/deactivate # Deactivate agent
│   ├── POST    /agents/<id>/actions/assign     # Assign agent
│   ├── POST    /agents/<id>/actions/unassign   # Unassign agent
│   ├── GET     /agents/generate            # Generate agents form
│   ├── POST    /agents/actions/generate    # Generate agents
│   ├── POST    /agents/actions/import      # Import agents
│   └── GET     /agents/actions/export      # Export agents
│
├── /rules (Rules Blueprint)
│   ├── GET     /rules/                    # Rules list
│   ├── GET     /rules/<id>                # Rule detail
│   ├── PUT     /rules/<id>                # Update rule
│   ├── DELETE  /rules/<id>                # Delete rule
│   ├── POST    /rules/<id>/actions/toggle # Toggle rule status
│   ├── POST    /rules/<id>/actions/activate   # Activate rule
│   ├── POST    /rules/<id>/actions/deactivate # Deactivate rule
│   ├── POST    /rules/<id>/actions/test       # Test rule
│   ├── POST    /rules/<id>/actions/validate   # Validate rule
│   ├── POST    /rules/actions/import      # Import rules
│   └── GET     /rules/actions/export      # Export rules
│
├── /system (System Blueprint)
│   ├── GET     /system/health             # System health check
│   ├── GET     /system/database           # Database metrics
│   ├── POST    /system/database/backup    # Create database backup
│   ├── POST    /system/database/restore   # Restore database
│   ├── GET     /system/workflow           # Workflow visualization
│   ├── POST    /system/workflow/validate  # Validate workflow
│   ├── GET     /system/context-files      # Context files list
│   ├── GET     /system/context-files/preview/<path>  # File preview
│   ├── GET     /system/context-files/download/<path> # File download
│   ├── POST    /system/context-files/upload           # File upload
│   ├── DELETE  /system/context-files/<path>           # File delete
│   ├── GET     /system/logs               # System logs
│   ├── GET     /system/logs/<type>        # Logs by type
│   ├── GET     /system/metrics            # System metrics
│   ├── GET     /system/settings           # System settings
│   └── PUT     /system/settings           # Update settings
│
├── /api (API Blueprint)
│   ├── GET  /api/ideas                    # Ideas API
│   ├── GET  /api/ideas/<id>               # Idea detail API
│   ├── GET  /api/work-items               # Work items API
│   ├── GET  /api/work-items/<id>          # Work item detail API
│   ├── GET  /api/work-items/<id>/tasks    # Work item tasks API
│   ├── GET  /api/context/documents        # Context documents API
│   ├── GET  /api/context/evidence         # Context evidence API
│   ├── GET  /api/context/events           # Context events API
│   ├── GET  /api/context/sessions         # Context sessions API
│   ├── GET  /api/agents                   # Agents API
│   ├── GET  /api/agents/<id>              # Agent detail API
│   ├── GET  /api/rules                    # Rules API
│   └── GET  /api/rules/<id>               # Rule detail API
│
└── /search (Search Blueprint)
    ├── GET     /search/                   # Search results
    ├── GET     /search/api                # Search API
    ├── GET     /search/suggestions        # Search suggestions
    ├── GET     /search/history            # Search history
    └── DELETE  /search/history            # Clear search history
```

## Route Statistics

### By Blueprint
- **Dashboard**: 3 routes
- **Ideas**: 11 routes (4 main + 7 elements)
- **Work Items**: 25 routes (8 main + 17 nested)
- **Context**: 20 routes (1 main + 19 nested)
- **Agents**: 12 routes
- **Rules**: 12 routes
- **System**: 16 routes
- **API**: 14 routes
- **Search**: 5 routes

### By HTTP Method
- **GET**: 45 routes (view/list operations)
- **POST**: 25 routes (actions and creation)
- **PUT**: 12 routes (update operations)
- **DELETE**: 8 routes (delete operations)

### Total Routes: 118

## Key Design Principles Applied

1. **RESTful Design**: Each resource has standard CRUD operations
2. **Hierarchical Structure**: Logical parent-child relationships
3. **Action Prefixes**: Non-REST operations use `/actions/` prefix
4. **Consistent Naming**: Plural for collections, singular for individual resources
5. **No Duplicates**: Single route per action (eliminated edit/update redundancy)

## Next Steps

1. **Map to System Capabilities**: Align these routes with actual APM (Agent Project Manager) functionality
2. **Prioritize Implementation**: Identify which routes are essential vs. nice-to-have
3. **Template Mapping**: Ensure all routes have corresponding templates
4. **Database Integration**: Connect routes to actual database operations
5. **Testing Strategy**: Create test coverage for all routes

---

**Note**: This is a comprehensive route structure that may exceed current system capabilities. The next step is to align these routes with the actual APM (Agent Project Manager) system features and database schema.
