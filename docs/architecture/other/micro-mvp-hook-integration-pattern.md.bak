# Micro-MVP: Hook Integration Pattern for Session Context Persistence

**Work Item**: WI-63 - Micro-MVP: Session Context Persistence  
**Task**: #392 - Micro-MVP Design: Hook Integration Pattern  
**Status**: In Progress  
**Designer**: aipm-codebase-navigator  

## 🎯 **Problem Statement**

Claude Code sessions lose context between sessions, requiring manual re-explanation of project state, current work, and context every time. This creates friction in the AI agent workflow and reduces productivity.

## 🎯 **Desired Outcome**

Context automatically loads on session start and learnings automatically save on session end, eliminating manual context re-explanation between Claude Code sessions.

## 🏗️ **Current Architecture Analysis**

### **Existing Hook System**
- **Location**: `agentpm/hooks/implementations/`
- **Current Hooks**: session-start.py, session-end.py, user-prompt-submit.py
- **Performance**: SessionStart ~180ms, SessionEnd ~220ms
- **Integration**: Already integrated with database session management

### **Existing Context System**
- **Location**: `agentpm/core/context/`
- **Components**: ContextAssemblyService, ContextService, SixWMerger
- **Performance**: <200ms context assembly target
- **Features**: Hierarchical 6W merging, plugin intelligence, agent SOP injection

### **Existing Session Management**
- **Location**: `agentpm/core/sessions/`
- **Components**: EventBus, Session models, database persistence
- **Features**: Event-driven tracking, session metadata capture

## 🔧 **Design Solution**

### **Core Integration Pattern**

The solution leverages existing infrastructure with minimal changes:

```
Claude Code Session Lifecycle:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Session Start │───▶│  Context Load    │───▶│  Work Session   │
│   (Hook)        │    │  (Enhanced)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Session End   │◀───│  Context Save    │◀───│  Work Session   │
│   (Hook)        │    │  (Enhanced)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Enhanced Session-Start Hook**

**Current**: Loads basic context from NEXT-SESSION.md  
**Enhanced**: Loads rich hierarchical context using ContextAssemblyService

```python
# Enhanced session-start.py pattern
def load_rich_context():
    """Load comprehensive context for session start"""
    
    # 1. Get current active work items/tasks
    active_work_items = get_active_work_items()
    active_tasks = get_active_tasks()
    
    # 2. Assemble context for each active entity
    contexts = []
    for task_id in active_tasks:
        context_payload = context_assembly_service.assemble_task_context(task_id)
        contexts.append(context_payload)
    
    # 3. Format for Claude consumption
    formatted_context = format_context_for_claude(contexts)
    
    # 4. Inject into Claude's initial prompt
    inject_context_to_claude(formatted_context)
```

### **Enhanced Session-End Hook**

**Current**: Generates NEXT-SESSION.md handover  
**Enhanced**: Saves rich context snapshots for next session

```python
# Enhanced session-end.py pattern
def save_rich_context():
    """Save comprehensive context for next session"""
    
    # 1. Capture current session state
    session_metadata = capture_session_metadata()
    
    # 2. Save context snapshots for active entities
    for task_id in active_tasks:
        context_payload = context_assembly_service.assemble_task_context(task_id)
        save_context_snapshot(task_id, context_payload)
    
    # 3. Generate enhanced handover document
    generate_enhanced_handover(session_metadata, context_snapshots)
    
    # 4. Update session in database
    update_session_metadata(session_metadata)
```

## 🔄 **Integration Points**

### **1. Context Assembly Service Integration**

**File**: `agentpm/hooks/implementations/session-start.py`  
**Change**: Import and use ContextAssemblyService

```python
from agentpm.core.context.assembly_service import ContextAssemblyService


def get_rich_context():
    """Get rich context using assembly service"""
    context_service = ContextAssemblyService(db, project_path)

    # Get active tasks
    active_tasks = get_active_tasks_from_db()

    # Assemble context for each task
    contexts = []
    for task_id in active_tasks:
        try:
            context = context_service.assemble_task_context(task_id)
            contexts.append(context)
        except Exception as e:
            # Graceful degradation - continue with basic context
            logger.warning(f"Failed to assemble context for task {task_id}: {e}")

    return contexts
```

### **2. Session Management Integration**

**File**: `agentpm/hooks/implementations/session-end.py`  
**Change**: Enhanced metadata capture

```python
def capture_enhanced_session_metadata():
    """Capture rich session metadata"""
    metadata = {
        'work_items_touched': get_work_items_touched(),
        'tasks_completed': get_tasks_completed(),
        'context_snapshots': save_context_snapshots(),
        'session_summary': generate_session_summary(),
        'next_session_priorities': get_next_priorities()
    }
    return metadata
```

### **3. Context Formatting for Claude**

**New Component**: Context formatter for Claude consumption

```python
def format_context_for_claude(contexts: List[ContextPayload]) -> str:
    """Format context payloads for Claude consumption"""
    
    formatted = []
    formatted.append("🤖 **AIPM Session Context**")
    formatted.append("")
    
    for context in contexts:
        # Project context
        formatted.append(f"## 📁 Project: {context.project['name']}")
        formatted.append(f"**Tech Stack**: {', '.join(context.project.get('tech_stack', []))}")
        formatted.append("")
        
        # Work item context
        if context.work_item:
            formatted.append(f"## 📋 Work Item: {context.work_item['name']}")
            formatted.append(f"**Status**: {context.work_item['status']}")
            formatted.append(f"**Description**: {context.work_item['description']}")
            formatted.append("")
        
        # Task context
        if context.task:
            formatted.append(f"## 🎯 Current Task: {context.task['name']}")
            formatted.append(f"**Status**: {context.task['status']}")
            formatted.append(f"**Assigned**: {context.task['assigned_to']}")
            formatted.append(f"**Effort**: {context.task['effort_hours']}h")
            formatted.append("")
        
        # 6W Context
        if context.merged_6w:
            formatted.append("## 📊 Context (6W Framework)")
            formatted.append(f"**WHO**: {', '.join(context.merged_6w.end_users or [])}")
            formatted.append(f"**WHAT**: {context.merged_6w.functional_requirements[0] if context.merged_6w.functional_requirements else 'N/A'}")
            formatted.append(f"**WHY**: {context.merged_6w.business_value or 'N/A'}")
            formatted.append("")
        
        # Agent SOP
        if context.agent_sop:
            formatted.append("## 📋 Agent SOP")
            formatted.append(context.agent_sop[:500] + "..." if len(context.agent_sop) > 500 else context.agent_sop)
            formatted.append("")
    
    return "\n".join(formatted)
```

## 📊 **Performance Considerations**

### **Target Performance**
- **Session Start**: <300ms (current 180ms + 120ms context assembly)
- **Session End**: <350ms (current 220ms + 130ms context saving)
- **Total Overhead**: <650ms per session (acceptable for daily usage)

### **Optimization Strategies**
1. **Lazy Loading**: Only assemble context for active tasks
2. **Caching**: Cache context snapshots between sessions
3. **Graceful Degradation**: Fall back to basic context if assembly fails
4. **Background Processing**: Save context snapshots asynchronously

## 🔒 **Error Handling & Graceful Degradation**

### **Failure Scenarios**
1. **Context Assembly Fails**: Fall back to basic NEXT-SESSION.md
2. **Database Unavailable**: Use file-based context only
3. **Plugin System Fails**: Skip plugin facts, continue with basic context
4. **Session Management Fails**: Continue with file-based handover

### **Graceful Degradation Pattern**
```python
def load_context_with_fallback():
    """Load context with graceful degradation"""
    try:
        # Try rich context first
        return load_rich_context()
    except ContextAssemblyError:
        logger.warning("Context assembly failed, falling back to basic context")
        return load_basic_context()
    except DatabaseError:
        logger.warning("Database unavailable, using file-based context")
        return load_file_context()
    except Exception as e:
        logger.error(f"Unexpected error: {e}, using minimal context")
        return load_minimal_context()
```

## 🧪 **Testing Strategy**

### **Unit Tests**
- Context assembly integration
- Error handling scenarios
- Performance benchmarks
- Format validation

### **Integration Tests**
- End-to-end session lifecycle
- Hook execution with real database
- Context persistence and retrieval
- Graceful degradation scenarios

### **Performance Tests**
- Session start/end timing
- Context assembly performance
- Memory usage during context loading
- Database query optimization

## 📋 **Implementation Plan**

### **Phase 1: Core Integration (2-3 hours)**
1. **Enhance session-start.py** (1h)
   - Import ContextAssemblyService
   - Add rich context loading
   - Implement graceful degradation

2. **Enhance session-end.py** (1h)
   - Add context snapshot saving
   - Enhanced metadata capture
   - Improved handover generation

3. **Add context formatter** (1h)
   - Format context for Claude consumption
   - Handle multiple active tasks
   - Optimize for Claude's context window

### **Phase 2: Testing & Validation (2-3 hours)**
1. **Unit tests** (1h)
2. **Integration tests** (1h)
3. **Performance validation** (1h)

### **Phase 3: Documentation & Deployment (1 hour)**
1. **Update documentation** (30min)
2. **Deploy and validate** (30min)

## 🎯 **Success Metrics**

### **Primary Metrics**
- **Zero manual context re-explanation** needed between sessions
- **<5 second context load time** for session start
- **100% session continuity** (no lost context)

### **Secondary Metrics**
- **<300ms session start overhead** (vs current 180ms)
- **<350ms session end overhead** (vs current 220ms)
- **95% graceful degradation** success rate
- **Zero critical failures** in production

## 🔄 **Future Enhancements**

### **Phase 2 Improvements**
- **Context Caching**: Cache assembled contexts between sessions
- **Smart Context Selection**: Only load relevant context based on user intent
- **Context Compression**: Optimize context size for Claude's limits

### **Phase 3 Advanced Features**
- **Context Versioning**: Track context changes over time
- **Context Analytics**: Analyze context usage patterns
- **Context Personalization**: Adapt context based on user preferences

## 📚 **Dependencies**

### **Internal Dependencies**
- ✅ ContextAssemblyService (existing)
- ✅ Session Management System (existing)
- ✅ Database Service (existing)
- ✅ Hook System (existing)

### **External Dependencies**
- ✅ Claude Code (existing integration)
- ✅ Python 3.11+ (existing)
- ✅ SQLite (existing)

## 🚀 **Deployment Strategy**

### **Rollout Plan**
1. **Development Testing**: Test in development environment
2. **Staging Validation**: Validate with real project data
3. **Gradual Rollout**: Deploy to subset of users first
4. **Full Deployment**: Roll out to all users after validation

### **Rollback Plan**
- Keep existing hook implementations as backup
- Database changes are additive (no breaking changes)
- Can revert to basic context loading if needed

---

**Design Status**: ✅ Complete  
**Next Step**: Begin implementation of enhanced session-start.py  
**Estimated Implementation Time**: 2-3 hours  
**Risk Level**: Low (leverages existing infrastructure)


