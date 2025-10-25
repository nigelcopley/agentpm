# APM (Agent Project Manager) Route Standardization Plan

## Current Issues Identified

### 1. **Dual Route Systems**
- **Problem**: Two parallel route systems (`/blueprints/` and `/routes/`)
- **Impact**: Confusion, maintenance overhead, inconsistent behavior
- **Solution**: Consolidate to single system using `/blueprints/`

### 2. **Inconsistent URL Patterns**
- **Problem**: Mixed singular/plural patterns
  - `/work-item/123` vs `/work-items`
  - `/task/123` vs `/tasks`
  - `/idea/123` vs `/ideas`
- **Impact**: Poor UX, confusing navigation
- **Solution**: Standardize on plural for collections, singular for individual resources

### 3. **Inconsistent Action Patterns**
- **Problem**: Mixed action URL patterns
  - `/work-items/123/actions/start` vs `/work-items/123/start`
- **Impact**: Inconsistent API design
- **Solution**: Standardize on `/actions/` prefix for all actions

### 4. **Navigation Mismatch**
- **Problem**: Header navigation links don't match actual routes
- **Impact**: Broken navigation, poor UX
- **Solution**: Align navigation with standardized routes

## Proposed Route Structure

### **Core Principles**
1. **RESTful Design**: Follow REST conventions
2. **Consistent Naming**: Plural for collections, singular for individual resources
3. **Hierarchical Structure**: Logical parent-child relationships
4. **Action Prefixes**: All actions use `/actions/` prefix
5. **Resource Grouping**: Related resources grouped under logical paths

### **Standardized Route Structure**

#### **Dashboard & Overview**
```
GET  /                           # Dashboard home (redirects to first project)
GET  /dashboard                  # Main dashboard
GET  /overview                   # System overview
```

#### **Projects**
```
GET     /projects                # Projects list
GET     /projects/{id}           # Project detail
GET     /projects/{id}/edit      # Project edit form
PUT     /projects/{id}           # Update project
GET     /projects/{id}/settings  # Project settings
GET     /projects/{id}/analytics # Project analytics
GET     /projects/{id}/context   # Project context
POST    /projects/{id}/actions/update    # Update project action
```

#### **Work Items**
```
GET     /work-items              # Work items list
GET     /work-items/{id}         # Work item detail
GET     /work-items/{id}/edit    # Work item edit form
PUT     /work-items/{id}         # Update work item
GET     /work-items/{id}/tasks   # Work item tasks
GET     /work-items/{id}/context # Work item context
GET     /work-items/{id}/summaries # Work item summaries
POST    /work-items/{id}/actions/start    # Start work item
POST    /work-items/{id}/actions/complete # Complete work item
POST    /work-items/{id}/actions/block    # Block work item
```

#### **Tasks**
```
GET     /tasks                   # Tasks list
GET     /tasks/{id}              # Task detail
GET     /tasks/{id}/edit         # Task edit form
PUT     /tasks/{id}              # Update task
GET     /tasks/{id}/dependencies # Task dependencies
GET     /tasks/{id}/blockers     # Task blockers
POST    /tasks/{id}/actions/assign   # Assign task
POST    /tasks/{id}/actions/start    # Start task
POST    /tasks/{id}/actions/complete # Complete task
POST    /tasks/{id}/actions/block    # Block task
```

#### **Agents**
```
GET     /agents                  # Agents list
GET     /agents/{id}             # Agent detail
GET     /agents/{id}/edit        # Agent edit form
PUT     /agents/{id}             # Update agent
GET     /agents/generate         # Generate agents form
POST    /agents/actions/generate # Generate agents action
POST    /agents/{id}/actions/toggle # Toggle agent status
```

#### **Rules**
```
GET     /rules                   # Rules list
GET     /rules/{id}              # Rule detail
GET     /rules/{id}/edit         # Rule edit form
PUT     /rules/{id}              # Update rule
POST    /rules/{id}/actions/toggle # Toggle rule status
```

#### **Ideas**
```
GET     /ideas                   # Ideas list
GET     /ideas/{id}              # Idea detail
GET     /ideas/{id}/edit         # Idea edit form
PUT     /ideas/{id}              # Update idea
GET     /ideas/{id}/convert-form # Convert idea form
POST    /ideas/{id}/actions/vote # Vote on idea
POST    /ideas/{id}/actions/transition # Transition idea
POST    /ideas/{id}/actions/convert # Convert idea to work item
```

#### **Sessions**
```
GET     /sessions                # Sessions list
GET     /sessions/{id}           # Session detail
GET     /sessions/timeline       # Sessions timeline
```

#### **Research**
```
GET     /research/documents      # Documents list
GET     /research/evidence       # Evidence sources
GET     /research/events         # Events timeline
```

#### **Contexts**
```
GET     /contexts                # Contexts list
GET     /contexts/{id}           # Context detail
POST    /contexts/{id}/actions/refresh # Refresh context
```

#### **System**
```
GET     /system/health           # System health
GET     /system/database         # Database metrics
GET     /system/workflow         # Workflow visualization
GET     /system/context-files    # Context files list
GET     /system/context-files/preview/{path} # Context file preview
GET     /system/context-files/download/{path} # Context file download
```

#### **Search & API**
```
GET     /search                  # Search results
GET     /api/search              # Search API
GET     /api/projects            # Projects API
GET     /api/work-items          # Work items API
GET     /api/tasks               # Tasks API
GET     /api/agents              # Agents API
GET     /api/rules               # Rules API
GET     /api/ideas               # Ideas API
GET     /api/sessions            # Sessions API
GET     /api/contexts            # Contexts API
```

#### **Development (Dev Only)**
```
GET     /dev/test-toasts         # Test toasts
POST    /dev/test-toast/{type}   # Trigger test toast
GET     /dev/test/interactions   # Test interactions
```

## Implementation Plan

### Phase 1: Route Consolidation
1. **Audit Current Routes**: Document all existing routes
2. **Create New Blueprint Structure**: Implement standardized routes
3. **Update Route Handlers**: Migrate logic to new structure
4. **Test Route Functionality**: Ensure all routes work correctly

### Phase 2: Navigation Update
1. **Update Header Navigation**: Align with new route structure
2. **Update Sidebar Navigation**: Ensure consistency
3. **Update Breadcrumbs**: Use new route patterns
4. **Update Internal Links**: Fix all internal references

### Phase 3: Legacy Support
1. **Create Redirect Routes**: Maintain backward compatibility
2. **Update Documentation**: Reflect new route structure
3. **Deprecation Notices**: Mark old routes as deprecated

### Phase 4: Testing & Validation
1. **Route Testing**: Test all new routes
2. **Navigation Testing**: Verify navigation works correctly
3. **User Testing**: Validate UX improvements
4. **Performance Testing**: Ensure no performance regression

## Benefits of Standardization

### **User Experience**
- **Predictable URLs**: Users can guess URLs based on patterns
- **Consistent Navigation**: All navigation follows same patterns
- **Better Breadcrumbs**: Clear hierarchical navigation
- **Improved Search**: More intuitive search results

### **Developer Experience**
- **Easier Maintenance**: Single route system to maintain
- **Consistent Patterns**: Predictable route structure
- **Better Testing**: Standardized route testing
- **Clear Documentation**: Self-documenting route structure

### **System Benefits**
- **Reduced Complexity**: Single route system
- **Better Performance**: Optimized route handling
- **Easier Debugging**: Clear route patterns
- **Future-Proof**: Scalable route structure

## Migration Strategy

### **Backward Compatibility**
- Keep existing routes working during transition
- Use redirects for old routes
- Gradual migration of internal links
- Clear deprecation timeline

### **Testing Strategy**
- Comprehensive route testing
- Navigation flow testing
- User acceptance testing
- Performance benchmarking

### **Rollout Plan**
1. **Development**: Implement new routes alongside old ones
2. **Staging**: Test new routes in staging environment
3. **Production**: Deploy with redirects for old routes
4. **Cleanup**: Remove old routes after migration period

## Success Metrics

### **Technical Metrics**
- Route response times
- Navigation success rates
- Error rates
- Code maintainability scores

### **User Experience Metrics**
- Navigation completion rates
- User satisfaction scores
- Support ticket reduction
- Feature adoption rates

### **Business Metrics**
- User engagement
- Feature usage
- Development velocity
- Maintenance costs

---

**Next Steps**: Begin implementation of Phase 1 - Route Consolidation
