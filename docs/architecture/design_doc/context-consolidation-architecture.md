# Context Consolidation Architecture Design

**Work Item**: WI-167 - Consolidate Context Storage Fields  
**Type**: FEATURE  
**Status**: DESIGN  
**Created**: 2025-01-27  
**Author**: AI Assistant  

---

## 🎯 Overview

Currently, context is stored in multiple places across the AgentPM system, creating fragmentation and inconsistency. This design consolidates all context storage into a unified Context model as the single source of truth.

### Current Fragmentation

1. **WorkItem.business_context** (Optional field) - Legacy business context storage
2. **Context.six_w** (UnifiedSixW structure) - Structured 6W framework data
3. **Context.context_data** (Optional field) - Rich context data dictionary
4. **UnifiedContextService.context_payload** - Comprehensive hierarchical context

### Proposed Solution

- **Deprecate** WorkItem.business_context field
- **Standardise** on Context model as single source of truth
- **Use** Context.context_data field for all context storage
- **Update** blueprints and templates to use Context model consistently
- **Create** migration to move existing business_context data to Context records

---

## 📋 Current State Analysis

### 1. WorkItem.business_context Usage

**Location**: `agentpm/core/database/models/work_item.py:70`
```python
business_context: Optional[str] = None
```

**Current Usage**:
- **CLI Commands**: `create`, `update`, `show`, `next`, `convert`
- **Web Templates**: `detail.html`, `edit.html`, `form.html`, `create.html`
- **Web Blueprints**: `detail.py`, `dashboard.py`
- **Context Service**: `service.py:129` - includes in work item context

**Data Format**: Plain text string (markdown supported in templates)

### 2. Context.six_w Usage

**Location**: `agentpm/core/database/models/context.py:243`
```python
six_w: Optional[UnifiedSixW] = None
```

**Current Usage**:
- **Structured Data**: 14 fields across 6W dimensions (who/what/when/where/why/how)
- **Confidence Scoring**: Integrated with confidence_score and confidence_band
- **Entity Relationships**: Linked via entity_type + entity_id
- **Template Rendering**: Serialised to dict for display

**Data Format**: UnifiedSixW dataclass with structured fields

### 3. Context.context_data Usage

**Location**: `agentpm/core/database/models/context.py:251`
```python
context_data: Optional[dict] = None
```

**Current Usage**:
- **Rich Context**: Business pillars, market research, competitive analysis
- **Template Rendering**: JSON serialised for display
- **CLI Commands**: `rich.py` for context management
- **Web Interface**: Context creation and editing forms

**Data Format**: JSON dictionary with flexible structure

### 4. UnifiedContextService.context_payload Usage

**Location**: `agentpm/core/context/unified_service.py:88`
```python
@dataclass
class ContextPayload:
```

**Current Usage**:
- **Hierarchical Assembly**: Combines entity + six_w + supporting data
- **Agent Consumption**: Primary output for AI agents
- **Performance Optimised**: Query optimisation with JOINs
- **Type Safety**: Pydantic models with validation

**Data Format**: Comprehensive dataclass with all context types

---

## 🏗️ Proposed Architecture

### 1. Unified Context Model

**Single Source of Truth**: Context model with context_data field

```python
class Context(BaseModel):
    # ... existing fields ...
    
    # Unified context storage
    context_data: Optional[dict] = None
    
    # Deprecated: Keep for backward compatibility during migration
    six_w: Optional[UnifiedSixW] = None  # Will be moved to context_data
```

### 2. Context Data Structure

**Standardised Format**:
```python
context_data = {
    "business_context": "Plain text business rationale",
    "six_w": {
        "who": {"end_users": [], "implementers": [], "reviewers": []},
        "what": {"functional_requirements": [], "technical_constraints": [], "acceptance_criteria": []},
        "where": {"affected_services": [], "repositories": [], "deployment_targets": []},
        "when": {"deadline": "2025-02-01", "dependencies_timeline": []},
        "why": {"business_value": "Improve user experience", "risk_if_delayed": "Competitive disadvantage"},
        "how": {"suggested_approach": "Implement in phases", "existing_patterns": []}
    },
    "rich_context": {
        "business_pillars": {},
        "market_research": {},
        "competitive_analysis": {}
    }
}
```

### 3. Migration Strategy

**Phase 1: Data Migration**
1. Create migration script to move WorkItem.business_context → Context.context_data
2. Update existing Context.six_w → Context.context_data["six_w"]
3. Preserve all existing data with backward compatibility

**Phase 2: Code Updates**
1. Update all CLI commands to use Context model
2. Update web templates and blueprints
3. Update context services and assemblers

**Phase 3: Cleanup**
1. Deprecate WorkItem.business_context field
2. Remove six_w field from Context model
3. Update documentation and tests

---

## 🔄 Implementation Plan

### Task 1: Design Context Consolidation Architecture ✅
- [x] Analyse current context storage fragmentation
- [x] Design unified Context model structure
- [x] Plan migration strategy
- [x] Document architecture decisions

### Task 2: Implement Context Consolidation
- [ ] Create database migration for data consolidation
- [ ] Update Context model to support unified storage
- [ ] Implement migration utilities
- [ ] Update context services

### Task 3: Test Context Consolidation
- [ ] Test data migration accuracy
- [ ] Verify context consistency across system
- [ ] Test backward compatibility
- [ ] Performance testing

### Task 4: Document Context Consolidation
- [ ] Update templates to use unified Context model
- [ ] Update blueprints for context handling
- [ ] Update CLI commands
- [ ] Update documentation

---

## 📊 Benefits

### 1. Single Source of Truth
- **Consistency**: All context data in one place
- **Maintainability**: Easier to update and debug
- **Reliability**: No data synchronisation issues

### 2. Better Organisation
- **Structured Storage**: Hierarchical context data
- **Flexible Schema**: Support for any context type
- **Rich Metadata**: Confidence scoring and timestamps

### 3. Unified API
- **Consistent Access**: Same methods for all context types
- **Type Safety**: Pydantic validation throughout
- **Performance**: Optimised queries and caching

### 4. Easier Maintenance
- **Single Model**: One place to update context logic
- **Clear Dependencies**: Obvious data flow
- **Better Testing**: Centralised test coverage

---

## ⚠️ Risks & Mitigation

### Risk 1: Data Loss During Migration
**Mitigation**: 
- Comprehensive backup before migration
- Rollback plan with data restoration
- Validation checks after migration

### Risk 2: Breaking Changes
**Mitigation**:
- Backward compatibility during transition
- Gradual rollout with feature flags
- Comprehensive testing

### Risk 3: Performance Impact
**Mitigation**:
- Performance testing before deployment
- Query optimisation
- Caching strategies

---

## 🎯 Success Criteria

1. **Data Integrity**: All existing context data preserved
2. **Functionality**: All features work with unified model
3. **Performance**: No degradation in context assembly speed
4. **Maintainability**: Single source of truth established
5. **Documentation**: All templates and blueprints updated

---

## 📚 References

- [WorkItem Model](agentpm/core/database/models/work_item.py)
- [Context Model](agentpm/core/database/models/context.py)
- [UnifiedContextService](agentpm/core/context/unified_service.py)
- [Context Service](agentpm/core/context/service.py)
- [Context Assembly Service](agentpm/core/context/assembly_service.py)
