# New Route Structure Design

## Design Principles

### 1. RESTful Resource-Based URLs
- Use consistent resource naming (always plural for collections)
- Follow standard HTTP methods (GET, POST, PUT, DELETE)
- Use nested resources for related entities
- Implement proper status codes

### 2. Clear Separation of Concerns
- One blueprint per domain/resource type
- Separate API and web routes
- Isolate test/development routes
- Clear boundaries between functionalities

### 3. Consistent Naming Patterns
- Always use plural for collections: `/projects`, `/work-items`, `/tasks`
- Use singular for individual resources: `/projects/1`, `/work-items/5`
- Use kebab-case for multi-word resources: `/work-items`, `/context-files`
- Use actions for non-CRUD operations: `/work-items/5/actions/start`

### 4. Logical Grouping
- Group related functionality together
- Minimize cross-blueprint dependencies
- Clear hierarchy and organization

## New Blueprint Structure

### 1. Dashboard Blueprint (`dashboard.py`)
**Purpose**: Main dashboard and overview pages
```
/                           - Main dashboard
/dashboard                  - Dashboard (explicit)
/overview                   - Project overview
```

### 2. Projects Blueprint (`projects.py`)
**Purpose**: Project management and CRUD operations
```
/projects                   - List all projects
/projects/<id>              - Get project details
/projects/<id>/edit         - Edit project form
/projects/<id>/settings     - Project settings
/projects/<id>/analytics    - Project analytics
/projects/<id>/context      - Project context (6W)
/projects/<id>/actions/update - Update project (PUT)
```

### 3. Work Items Blueprint (`work_items.py`)
**Purpose**: Work item management and operations
```
/work-items                 - List all work items
/work-items/<id>            - Get work item details
/work-items/<id>/edit       - Edit work item form
/work-items/<id>/summaries  - Work item summaries timeline
/work-items/<id>/context    - Work item context
/work-items/<id>/tasks      - Tasks for this work item
/work-items/<id>/actions/start    - Start work item
/work-items/<id>/actions/complete - Complete work item
/work-items/<id>/actions/block    - Block work item
```

### 4. Tasks Blueprint (`tasks.py`)
**Purpose**: Task management and operations
```
/tasks                      - List all tasks
/tasks/<id>                 - Get task details
/tasks/<id>/edit            - Edit task form
/tasks/<id>/dependencies    - Task dependencies
/tasks/<id>/blockers        - Task blockers
/tasks/<id>/actions/assign  - Assign task
/tasks/<id>/actions/start   - Start task
/tasks/<id>/actions/complete - Complete task
/tasks/<id>/actions/block   - Block task
```

### 5. Agents Blueprint (`agents.py`)
**Purpose**: Agent management and operations
```
/agents                     - List all agents
/agents/<id>                - Get agent details
/agents/<id>/edit           - Edit agent form
/agents/generate            - Generate agents form
/agents/actions/generate    - Generate agents (POST)
/agents/<id>/actions/toggle - Toggle agent status
```

### 6. Rules Blueprint (`rules.py`)
**Purpose**: Rules management and operations
```
/rules                      - List all rules
/rules/<id>                 - Get rule details
/rules/<id>/edit            - Edit rule form
/rules/<id>/actions/toggle  - Toggle rule enforcement
```

### 7. Ideas Blueprint (`ideas.py`)
**Purpose**: Ideas management and lifecycle
```
/ideas                      - List all ideas
/ideas/<id>                 - Get idea details
/ideas/<id>/edit            - Edit idea form
/ideas/<id>/actions/vote    - Vote on idea
/ideas/<id>/actions/transition - Transition idea status
/ideas/<id>/actions/convert - Convert to work item
```

### 8. Sessions Blueprint (`sessions.py`)
**Purpose**: Session management and timeline
```
/sessions                   - List all sessions
/sessions/<id>              - Get session details
/sessions/timeline          - Sessions timeline view
```

### 9. Research Blueprint (`research.py`)
**Purpose**: Research, evidence, and documentation
```
/evidence                   - Evidence sources list
/events                     - Events timeline
/documents                  - Document references list
/context-files              - Context files browser
/context-files/<path>       - Context file preview
/context-files/<path>/download - Download context file
```

### 10. Contexts Blueprint (`contexts.py`)
**Purpose**: Context management and 6W framework
```
/contexts                   - List all contexts
/contexts/<id>              - Get context details
/contexts/<id>/edit         - Edit context form
/contexts/<id>/actions/refresh - Refresh context
```

### 11. System Blueprint (`system.py`)
**Purpose**: System administration and monitoring
```
/system                     - System overview
/system/database            - Database metrics
/system/workflow            - Workflow visualization
/system/health              - Health check (JSON)
```

### 12. Search Blueprint (`search.py`)
**Purpose**: Search functionality
```
/search                     - Search results page
/api/search                 - Search API endpoint
```

### 13. API Blueprint (`api.py`)
**Purpose**: RESTful API endpoints
```
/api/v1/projects            - Projects API
/api/v1/work-items          - Work items API
/api/v1/tasks               - Tasks API
/api/v1/agents              - Agents API
/api/v1/rules               - Rules API
/api/v1/ideas               - Ideas API
/api/v1/sessions            - Sessions API
/api/v1/contexts            - Contexts API
```

### 14. Development Blueprint (`dev.py`)
**Purpose**: Development and testing routes (only in development)
```
/dev/test-toasts            - Test toast notifications
/dev/test-interactions      - Test interactions
/dev/test-route/<type>      - Test route endpoints
```

## URL Pattern Standards

### Collection URLs (List/Index)
```
GET /projects               - List all projects
GET /work-items             - List all work items
GET /tasks                  - List all tasks
GET /agents                 - List all agents
GET /rules                  - List all rules
GET /ideas                  - List all ideas
GET /sessions               - List all sessions
GET /contexts               - List all contexts
```

### Resource URLs (Individual Items)
```
GET /projects/<id>          - Get specific project
GET /work-items/<id>        - Get specific work item
GET /tasks/<id>             - Get specific task
GET /agents/<id>            - Get specific agent
GET /rules/<id>             - Get specific rule
GET /ideas/<id>             - Get specific idea
GET /sessions/<id>          - Get specific session
GET /contexts/<id>          - Get specific context
```

### Form URLs (Edit/Create)
```
GET /projects/<id>/edit     - Edit project form
GET /work-items/<id>/edit   - Edit work item form
GET /tasks/<id>/edit        - Edit task form
GET /agents/<id>/edit       - Edit agent form
GET /rules/<id>/edit        - Edit rule form
GET /ideas/<id>/edit        - Edit idea form
GET /contexts/<id>/edit     - Edit context form
```

### Action URLs (Non-CRUD Operations)
```
POST /work-items/<id>/actions/start     - Start work item
POST /work-items/<id>/actions/complete  - Complete work item
POST /work-items/<id>/actions/block     - Block work item
POST /tasks/<id>/actions/assign         - Assign task
POST /tasks/<id>/actions/start          - Start task
POST /tasks/<id>/actions/complete       - Complete task
POST /tasks/<id>/actions/block          - Block task
POST /agents/<id>/actions/toggle        - Toggle agent
POST /rules/<id>/actions/toggle         - Toggle rule
POST /ideas/<id>/actions/vote           - Vote on idea
POST /ideas/<id>/actions/transition     - Transition idea
POST /ideas/<id>/actions/convert        - Convert idea
POST /contexts/<id>/actions/refresh     - Refresh context
```

### Nested Resource URLs
```
GET /work-items/<id>/tasks              - Tasks for work item
GET /work-items/<id>/summaries          - Summaries for work item
GET /work-items/<id>/context            - Context for work item
GET /tasks/<id>/dependencies            - Dependencies for task
GET /tasks/<id>/blockers                - Blockers for task
GET /projects/<id>/work-items           - Work items for project
GET /projects/<id>/context              - Context for project
GET /projects/<id>/analytics            - Analytics for project
```

## HTTP Method Standards

### GET Requests
- Retrieve data (list, detail, forms)
- No side effects
- Cacheable

### POST Requests
- Create new resources
- Execute actions
- Non-idempotent operations

### PUT Requests
- Update existing resources
- Idempotent operations
- Replace resource data

### DELETE Requests
- Remove resources
- Idempotent operations

## Migration Strategy

### Phase 1: Create New Blueprints
1. Create new blueprint files with proper structure
2. Implement new routes alongside existing ones
3. Add feature flags to switch between old/new routes

### Phase 2: Update Templates
1. Update navigation templates to use new routes
2. Update internal links in templates
3. Update form actions

### Phase 3: Redirect Old Routes
1. Add redirect routes from old URLs to new URLs
2. Implement proper HTTP redirects (301/302)
3. Update external references

### Phase 4: Remove Old Routes
1. Remove old route implementations
2. Clean up unused blueprint code
3. Update documentation

## Benefits of New Structure

### 1. Consistency
- All routes follow the same patterns
- Predictable URL structure
- Easy to remember and use

### 2. Maintainability
- Clear separation of concerns
- Easy to locate and modify code
- Reduced coupling between modules

### 3. Scalability
- Easy to add new resources
- Clear patterns for new features
- Better organization as system grows

### 4. Developer Experience
- Intuitive route structure
- Easy to understand and navigate
- Better debugging and testing

### 5. User Experience
- Consistent navigation patterns
- Predictable URLs
- Better bookmarking and sharing

## Implementation Notes

### Blueprint Registration
```python
# In app.py
from .blueprints import (
    dashboard_bp, projects_bp, work_items_bp, tasks_bp,
    agents_bp, rules_bp, ideas_bp, sessions_bp,
    research_bp, contexts_bp, system_bp, search_bp,
    api_bp, dev_bp
)

app.register_blueprint(dashboard_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(work_items_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(agents_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(ideas_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(research_bp)
app.register_blueprint(contexts_bp)
app.register_blueprint(system_bp)
app.register_blueprint(search_bp)
app.register_blueprint(api_bp, url_prefix='/api/v1')
app.register_blueprint(dev_bp, url_prefix='/dev')  # Only in development
```

### Error Handling
- Consistent error responses
- Proper HTTP status codes
- User-friendly error messages

### Testing Strategy
- Unit tests for each blueprint
- Integration tests for route interactions
- End-to-end tests for user workflows

This design provides a solid foundation for a maintainable, scalable, and user-friendly route structure.
