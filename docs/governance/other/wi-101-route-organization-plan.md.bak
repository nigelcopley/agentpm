# APM (Agent Project Manager) Route Organization Plan

## Current Issues

The current route organization has several problems:

1. **Scattered Logic**: Related functionality is spread across multiple files
2. **Inconsistent Naming**: Some routes use singular, others plural
3. **Mixed Responsibilities**: Files contain unrelated functionality
4. **Hard to Find**: Routes are not logically grouped
5. **Template Mismatch**: Routes don't align with template structure

## Current Route Structure

```
agentpm/web/routes/
├── configuration.py    # Rules, agents, project settings (mixed concerns)
├── contexts.py         # Context management
├── entities.py         # Work items, tasks, projects (mixed concerns)
├── ideas.py           # Idea management
├── main.py            # Dashboard, project context, tests
├── projects.py        # Project detail, analytics
├── research.py        # Evidence, events, documents
├── sessions.py        # Session management
└── system.py          # Health, database, workflow, files
```

## Proposed Route Organization

### 1. Core Entity Routes
```
agentpm/web/routes/
├── work_items.py      # All work item routes
├── tasks.py           # All task routes  
├── projects.py        # All project routes
├── ideas.py           # All idea routes
└── sessions.py        # All session routes
```

### 2. Supporting Routes
```
agentpm/web/routes/
├── contexts.py        # Context management
├── documents.py       # Document management
├── evidence.py        # Evidence and research
└── analytics.py       # Analytics and reporting
```

### 3. System Routes
```
agentpm/web/routes/
├── dashboard.py       # Main dashboard
├── configuration.py   # Settings and configuration
├── system.py          # Health, database, workflow
└── admin.py           # Administrative functions
```

## Detailed Route Mapping

### Work Items (`work_items.py`)
```python
# List and overview
@work_items_bp.route('/work-items')
@work_items_bp.route('/work-items/<int:work_item_id>')

# CRUD operations
@work_items_bp.route('/work-item/create')
@work_items_bp.route('/work-item/<int:work_item_id>/edit')
@work_items_bp.route('/work-item/<int:work_item_id>/delete', methods=['POST'])

# Work item specific
@work_items_bp.route('/work-item/<int:work_item_id>/tasks')
@work_items_bp.route('/work-item/<int:work_item_id>/context')
@work_items_bp.route('/work-item/<int:work_item_id>/summaries')
@work_items_bp.route('/work-item/<int:work_item_id>/dependencies')

# Actions
@work_items_bp.route('/work-item/<int:work_item_id>/start', methods=['POST'])
@work_items_bp.route('/work-item/<int:work_item_id>/complete', methods=['POST'])
@work_items_bp.route('/work-item/<int:work_item_id>/cancel', methods=['POST'])
```

### Tasks (`tasks.py`)
```python
# List and overview
@tasks_bp.route('/tasks')
@tasks_bp.route('/task/<int:task_id>')

# CRUD operations
@tasks_bp.route('/task/create')
@tasks_bp.route('/task/<int:task_id>/edit')
@tasks_bp.route('/task/<int:task_id>/delete', methods=['POST'])

# Task specific
@tasks_bp.route('/task/<int:task_id>/dependencies')
@tasks_bp.route('/task/<int:task_id>/blockers')

# Actions
@tasks_bp.route('/task/<int:task_id>/start', methods=['POST'])
@tasks_bp.route('/task/<int:task_id>/complete', methods=['POST'])
@tasks_bp.route('/task/<int:task_id>/block', methods=['POST'])
```

### Projects (`projects.py`)
```python
# List and overview
@projects_bp.route('/projects')
@projects_bp.route('/project/<int:project_id>')

# CRUD operations
@projects_bp.route('/project/create')
@projects_bp.route('/project/<int:project_id>/edit')
@projects_bp.route('/project/<int:project_id>/delete', methods=['POST'])

# Project specific
@projects_bp.route('/project/<int:project_id>/work-items')
@projects_bp.route('/project/<int:project_id>/tasks')
@projects_bp.route('/project/<int:project_id>/context')
@projects_bp.route('/project/<int:project_id>/analytics')
@projects_bp.route('/project/<int:project_id>/settings')

# Actions
@projects_bp.route('/project/<int:project_id>/activate', methods=['POST'])
@projects_bp.route('/project/<int:project_id>/archive', methods=['POST'])
```

### Dashboard (`dashboard.py`)
```python
# Main dashboard
@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')

# Quick actions
@dashboard_bp.route('/quick-create/work-item')
@dashboard_bp.route('/quick-create/task')
@dashboard_bp.route('/quick-create/project')

# Search and navigation
@dashboard_bp.route('/search')
@dashboard_bp.route('/recent')
@dashboard_bp.route('/favorites')
```

### Configuration (`configuration.py`)
```python
# Rules management
@config_bp.route('/rules')
@config_bp.route('/rule/<int:rule_id>')
@config_bp.route('/rule/<int:rule_id>/toggle', methods=['POST'])

# Agents management
@config_bp.route('/agents')
@config_bp.route('/agent/<int:agent_id>')
@config_bp.route('/agent/<int:agent_id>/toggle', methods=['POST'])
@config_bp.route('/agents/generate', methods=['POST'])

# System settings
@config_bp.route('/settings')
@config_bp.route('/settings/update', methods=['POST'])
```

## Route Naming Conventions

### Consistent Patterns
- **List views**: `/entities` (plural)
- **Detail views**: `/entity/<id>` (singular)
- **Create forms**: `/entity/create`
- **Edit forms**: `/entity/<id>/edit`
- **Actions**: `/entity/<id>/action` (POST methods)
- **Sub-resources**: `/entity/<id>/sub-entity`

### HTTP Methods
- **GET**: View, list, form display
- **POST**: Create, update, delete, actions
- **PUT/PATCH**: Partial updates (if needed)

## Template Alignment

Routes should align with template structure:

```
Routes                    → Templates
/work-items              → work-items/list.html
/work-item/123           → work-items/detail.html
/work-item/create        → work-items/form.html
/work-item/123/edit      → work-items/form.html

/tasks                   → tasks/list.html
/task/456                → tasks/detail.html
/task/create             → tasks/form.html
/task/456/edit           → tasks/form.html

/projects                → projects/list.html
/project/789             → projects/detail.html
/project/create          → projects/form.html
/project/789/edit        → projects/form.html
```

## Migration Strategy

### Phase 1: Create New Route Files
1. Create new route files with proper organization
2. Move routes from existing files to new structure
3. Update imports and blueprints

### Phase 2: Update Templates
1. Ensure all templates exist in new structure
2. Update template references in routes
3. Test all routes work correctly

### Phase 3: Clean Up
1. Remove old route files
2. Update any remaining references
3. Update documentation

## Benefits

1. **Logical Grouping**: Related functionality together
2. **Easy Navigation**: Clear file structure
3. **Consistent Naming**: Predictable URL patterns
4. **Template Alignment**: Routes match template structure
5. **Maintainability**: Easier to find and modify code
6. **Scalability**: Easy to add new routes in right place

## Implementation Priority

1. **High Priority**: Work items, tasks, projects (core entities)
2. **Medium Priority**: Dashboard, configuration
3. **Low Priority**: Analytics, admin functions

This organization will make the codebase much more maintainable and easier to navigate.
