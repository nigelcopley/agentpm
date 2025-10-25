# APM (Agent Project Manager) Web Routes Analysis

## Current Route Structure

### Main Blueprint (`main.py`)
- `/` - Dashboard (project overview)
- `/project/<int:project_id>` - Project detail view
- `/project/<int:project_id>/context` - Project context view (6W framework)
- `/test-toasts` - Test route for toast notifications (dev only)
- `/test-toast/<toast_type>` - HTMX endpoint for test toasts
- `/test/interactions` - Test route for enhanced interactions (dev only)

### Entities Blueprint (`entities.py`)
- `/projects` - Projects list view
- `/work-items-debug` - Debug work items list view
- `/work-items` - Work items list view with smart filtering
- `/work-item/<int:work_item_id>` - Work item detail view
- `/work-item/<int:work_item_id>/summaries` - Work item summaries timeline
- `/tasks` - Tasks list view
- `/task/<int:task_id>` - Task detail view

### Projects Blueprint (`projects.py`)
- `/project/<int:project_id>` - Complete project detail view (enhanced)
- `/project/<int:project_id>/settings` - Project settings view
- `/project/<int:project_id>/analytics` - Project analytics view
- `/project/<int:project_id>/update` - Update project settings (POST)

### Configuration Blueprint (`configuration.py`)
- `/rules` - Rules list view
- `/rules/<int:rule_id>/toggle` - Toggle rule enforcement (POST/GET)
- `/agents` - Agents list view
- `/agents/<int:agent_id>/toggle` - Toggle agent status (POST)
- `/agents/generate-form` - Load agent generation modal (GET)
- `/agents/generate` - Generate agents from form (POST)
- `/project/<int:project_id>/settings` - Project settings page
- `/project/<int:project_id>/settings/name` - Project name field (GET)
- `/project/<int:project_id>/update-name` - Update project name (POST)
- `/project/<int:project_id>/settings/description` - Project description field (GET)
- `/project/<int:project_id>/update-description` - Update project description (POST)
- `/project/<int:project_id>/settings/tech-stack` - Project tech stack field (GET)
- `/project/<int:project_id>/update-tech-stack` - Update project tech stack (POST)

### System Blueprint (`system.py`)
- `/health` - Health check endpoint (JSON)
- `/system/database` - Database metrics dashboard
- `/workflow` - Workflow state machine visualization
- `/context-files` - Context files browser
- `/context-files/preview/<path:filepath>` - Preview context file
- `/context-files/download/<path:filepath>` - Download context file

### Search Blueprint (`search.py`)
- `/search` - Search results page
- `/api/search` - Search API endpoint (JSON)

### Ideas Blueprint (`ideas.py`)
- `/ideas` - Ideas list view with filtering
- `/idea/<int:idea_id>` - Idea detail view
- `/idea/<int:idea_id>/vote` - Vote on idea (POST)
- `/idea/<int:idea_id>/transition` - Transition idea lifecycle (POST)
- `/idea/<int:idea_id>/convert-form` - HTMX form for converting idea to work item
- `/idea/<int:idea_id>/convert` - Convert idea to work item (POST)

### Research Blueprint (`research.py`)
- `/evidence` - Evidence sources list view
- `/events` - Events audit log timeline view
- `/documents` - Document references list view

### Sessions Blueprint (`sessions.py`)
- `/sessions` - Sessions list view
- `/session/<session_id>` - Session detail view
- `/sessions/timeline` - Sessions timeline view

### Contexts Blueprint (`contexts.py`)
- `/contexts` - Contexts list view
- `/context/<int:context_id>` - Context detail view
- `/work-item/<int:work_item_id>/context` - Hierarchical context view for work item
- `/context/<int:context_id>/refresh` - Refresh context data (POST)

## Current UI Navigation Analysis

### Header Navigation (Desktop)
Currently exposed:
- Work Items (`/work-items`)
- Tasks (`/tasks`)
- Sessions (`/sessions`)
- Ideas (`/ideas`)

### Header Navigation (Mobile)
Currently exposed:
- Home (`/`)
- Work Items (`/work-items`)
- Tasks (`/tasks`)
- Sessions (`/sessions`)
- Ideas (`/ideas`)
- Contexts (`/contexts`)
- Documents (`/documents`)

### User Dropdown
Currently exposed:
- Project Settings (`/project/1/settings`)
- System Status (`/system/database`)
- Notifications (placeholder)

## Missing Endpoints in UI Navigation

### High Priority Missing Routes
1. **Projects** - `/projects` (projects list view)
2. **Rules** - `/rules` (rules management)
3. **Agents** - `/agents` (agents management)
4. **Evidence** - `/evidence` (evidence sources)
5. **Events** - `/events` (events timeline)
6. **Context Files** - `/context-files` (context files browser)
7. **Workflow** - `/workflow` (workflow visualization)

### Medium Priority Missing Routes
1. **Project Analytics** - `/project/<id>/analytics`
2. **Project Context** - `/project/<id>/context`
3. **Work Item Summaries** - `/work-item/<id>/summaries`
4. **Work Item Context** - `/work-item/<id>/context`
5. **Session Timeline** - `/sessions/timeline`

### Low Priority Missing Routes
1. **Health Check** - `/health` (API endpoint)
2. **Search API** - `/api/search` (API endpoint)
3. **Test Routes** - Various test endpoints (dev only)

## Recommendations

### 1. Fix User Dropdown Positioning
✅ **COMPLETED** - Fixed the user dropdown positioning by:
- Adding `z-50` class for proper z-index
- Using inline style for `max-width` to prevent Tailwind class conflicts
- Ensuring dropdown stays within viewport bounds

### 2. Add Missing Navigation Items
Add the following to the header navigation:

#### Desktop Navigation
- Add "Projects" link
- Add "Rules" link  
- Add "Agents" link
- Add "Research" dropdown with Evidence, Events, Documents
- Add "System" dropdown with Database, Workflow, Context Files

#### Mobile Navigation
- Add all missing routes to mobile menu
- Organize into logical groups

#### User Dropdown
- Add "Rules Management" link
- Add "Agents Management" link
- Add "Context Files" link
- Add "Workflow Visualization" link

### 3. Organize Navigation Structure
```
Header Navigation:
├── Work Items
├── Tasks  
├── Sessions
├── Ideas
├── Projects
├── Research ▼
│   ├── Evidence
│   ├── Events
│   └── Documents
├── Management ▼
│   ├── Rules
│   └── Agents
└── System ▼
    ├── Database
    ├── Workflow
    └── Context Files
```

### 4. User Dropdown Enhancements
```
User Dropdown:
├── Project Settings
├── System Status
├── Context Files
├── Workflow Visualization
├── Rules Management
├── Agents Management
└── Notifications
```

## Implementation Priority

1. **Immediate** - Fix user dropdown positioning ✅
2. **High Priority** - Add missing core navigation items
3. **Medium Priority** - Organize navigation with dropdowns
4. **Low Priority** - Add advanced features and API endpoints

## Notes

- All routes are properly implemented with comprehensive functionality
- Routes follow consistent patterns and use proper database methods
- Templates exist for most routes
- Some routes have both list and detail views
- API endpoints are available for AJAX functionality
- Test routes are available for development
