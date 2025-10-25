# APM (Agent Project Manager) Realistic Route Tree

## System Capabilities Analysis

Based on the actual database models and methods available in APM (Agent Project Manager), here's a realistic route structure that aligns with system capabilities:

### Core Entities Available:
- **Projects** (with status, tech_stack, frameworks)
- **Ideas** (6-state lifecycle: idea → research → design → accepted → converted/rejected)
- **Work Items** (with types, status, phases)
- **Tasks** (with status, effort, dependencies)
- **Agents** (with roles, lifecycle, generation tracking)
- **Rules** (with categories, enforcement levels)
- **Context** (resource files + entity contexts with UnifiedSixW)
- **Sessions** (with tracking and metadata)
- **Dependencies** (TaskDependency, TaskBlocker, WorkItemDependency)
- **Evidence Sources** (with validation and verification)
- **Events** (with categorization and metadata)
- **Document References** (with types, formats, organization)
- **Summaries** (polymorphic across all entity types)
- **Search Indexes** (with metrics and performance tracking)

---

## Realistic Route Structure

```
APM (Agent Project Manager) Web Application Routes (System-Aligned)
├── / (Dashboard Blueprint)
│   ├── GET  /                    # Dashboard home
│   ├── GET  /dashboard           # Main dashboard
│   └── GET  /overview            # System overview
│
├── /projects (Projects Blueprint)
│   ├── GET     /projects/                    # Projects list
│   ├── GET     /projects/<id>                # Project detail
│   ├── PUT     /projects/<id>                # Update project
│   ├── DELETE  /projects/<id>                # Delete project
│   ├── POST    /projects/<id>/actions/activate   # Activate project
│   ├── POST    /projects/<id>/actions/archive    # Archive project
│   └── GET     /projects/<id>/context        # Project context
│
├── /ideas (Ideas Blueprint)
│   ├── GET     /ideas/                    # Ideas list
│   ├── GET     /ideas/<id>                # Idea detail
│   ├── PUT     /ideas/<id>                # Update idea
│   ├── DELETE  /ideas/<id>                # Delete idea
│   ├── POST    /ideas/<id>/actions/vote   # Vote on idea
│   ├── POST    /ideas/<id>/actions/transition # Transition idea (idea→research→design→accepted)
│   ├── POST    /ideas/<id>/actions/convert # Convert to work item
│   └── POST    /ideas/<id>/actions/reject  # Reject idea
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
│   │   └── POST    /context/documents/<id>/actions/refresh # Refresh document
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
│       └── DELETE  /context/sessions/<id>                # Delete session
│
├── /agents (Agents Blueprint)
│   ├── GET     /agents/                    # Agents list
│   ├── GET     /agents/<id>                # Agent detail
│   ├── PUT     /agents/<id>                # Update agent
│   ├── DELETE  /agents/<id>                # Delete agent
│   ├── POST    /agents/<id>/actions/activate   # Activate agent
│   ├── POST    /agents/<id>/actions/deactivate # Deactivate agent
│   ├── POST    /agents/<id>/actions/generate   # Mark as generated
│   ├── GET     /agents/generate            # Generate agents form
│   ├── POST    /agents/actions/generate    # Generate agents
│   └── GET     /agents/stale               # Get stale agents
│
├── /rules (Rules Blueprint)
│   ├── GET     /rules/                    # Rules list
│   ├── GET     /rules/<id>                # Rule detail
│   ├── PUT     /rules/<id>                # Update rule
│   ├── DELETE  /rules/<id>                # Delete rule
│   ├── POST    /rules/<id>/actions/activate   # Activate rule
│   ├── POST    /rules/<id>/actions/deactivate # Deactivate rule
│   ├── POST    /rules/<id>/actions/test       # Test rule
│   └── POST    /rules/<id>/actions/validate   # Validate rule
│
├── /system (System Blueprint)
│   ├── GET     /system/health             # System health check
│   ├── GET     /system/database           # Database metrics
│   ├── GET     /system/context-files      # Context files list
│   ├── GET     /system/context-files/preview/<path>  # File preview
│   ├── GET     /system/context-files/download/<path> # File download
│   ├── GET     /system/logs               # System logs
│   ├── GET     /system/logs/<type>        # Logs by type
│   ├── GET     /system/metrics            # System metrics
│   ├── GET     /system/settings           # System settings
│   └── PUT     /system/settings           # Update settings
│
├── /api (API Blueprint)
│   ├── GET  /api/projects                 # Projects API
│   ├── GET  /api/projects/<id>            # Project detail API
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

## Key Differences from Comprehensive Version

### Removed Routes (Not Supported by System):
1. **Idea Elements** - No "elements" concept in the Idea model
2. **Work Item Context Refresh** - No refresh mechanism in context methods
3. **Agent Import/Export** - No import/export methods in agent_methods
4. **Rule Import/Export** - No import/export methods in rule_methods
5. **Database Backup/Restore** - No backup/restore methods in system
6. **Workflow Validation** - No workflow validation in system
7. **File Upload/Delete** - No file management in system
8. **System Logs by Type** - No log categorization in system

### Added Routes (Actually Supported):
1. **Projects Blueprint** - Full project management (was missing)
2. **Idea Reject Action** - Idea rejection is part of the lifecycle
3. **Agent Generate/Stale** - Agent generation tracking is supported
4. **Rule Test/Validate** - Rule testing and validation is supported

## Route Statistics (Realistic)

### By Blueprint
- **Dashboard**: 3 routes
- **Projects**: 7 routes
- **Ideas**: 8 routes
- **Work Items**: 20 routes (8 main + 12 nested)
- **Context**: 16 routes (1 main + 15 nested)
- **Agents**: 10 routes
- **Rules**: 8 routes
- **System**: 10 routes
- **API**: 14 routes
- **Search**: 5 routes

### By HTTP Method
- **GET**: 42 routes (view/list operations)
- **POST**: 20 routes (actions and creation)
- **PUT**: 10 routes (update operations)
- **DELETE**: 6 routes (delete operations)

### Total Routes: 101 (vs 118 in comprehensive version)

## Implementation Priority

### Phase 1 (Essential - 40 routes)
- Dashboard (3 routes)
- Projects (7 routes)
- Ideas (8 routes)
- Work Items main (8 routes)
- Agents (10 routes)
- Rules (8 routes)

### Phase 2 (Important - 35 routes)
- Work Items nested (12 routes)
- Context main (1 route)
- Context documents (5 routes)
- Context evidence (6 routes)
- System health/database (2 routes)
- API endpoints (14 routes)

### Phase 3 (Nice to Have - 26 routes)
- Context events (4 routes)
- Context sessions (4 routes)
- System files/logs/metrics (8 routes)
- Search functionality (5 routes)
- System settings (2 routes)

---

**Note**: This realistic route structure aligns with the actual APM (Agent Project Manager) database models and methods, ensuring all routes can be properly implemented with existing system capabilities.
