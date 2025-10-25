# APM (Agent Project Manager) Context System Guide

## 🎯 **CONTEXT SYSTEM OVERVIEW**

APM (Agent Project Manager) provides hierarchical context assembly that delivers intelligent, context-aware guidance to AI agents across the entire product development lifecycle.

---

## 🏗️ **HIERARCHICAL CONTEXT STRUCTURE**

### **Context Hierarchy**
```
Project Context (Base)
├── Tech stack detection via plugins
├── Framework rules and patterns
├── Code amalgamations
├── Project standards and principles
└── Business context and market intelligence

Work Item Context (Middle)
├── Scope and requirements (6W framework)
├── Acceptance criteria
├── Dependencies and blockers
├── Quality gates and workflow enforcement
└── Business value and strategic alignment

Task Context (Top)
├── Specific implementation details
├── Time-boxing constraints (4h max for IMPLEMENTATION)
├── Agent guidance and SOPs
├── Success criteria and quality requirements
└── Evidence-based decision tracking
```

---

## 🔍 **CONTEXT ASSEMBLY COMMANDS**

### **Primary Context Commands**
```bash
# Get comprehensive project context
apm context show --work-item-id=all

# Get specific work item context
apm context show --work-item-id=<work_item_id>

# Get specific task context
apm context show --task-id=<task_id>

# Get agent-specific context
apm context show --agent=<specialized_agent> --task-id=<task_id>

# Refresh stale context
apm context refresh --work-item-id=<work_item_id>
```

### **Context Quality Indicators**
```bash
# Check context quality (RED/YELLOW/GREEN)
apm context show --work-item-id=<id>
# Look for: Context Quality: GREEN (0.85 confidence)
```

---

## 📊 **CONTEXT QUALITY SCORING**

### **Quality Levels**
- **RED** (<0.6 confidence): Insufficient context - request additional information
- **YELLOW** (0.6-0.8 confidence): Adequate context - proceed with caution
- **GREEN** (>0.8 confidence): Excellent context - proceed with confidence

### **Quality Factors**
- **Completeness**: All required context elements present
- **Freshness**: Context is up-to-date and relevant
- **Accuracy**: Context reflects current state
- **Relevance**: Context is appropriate for the task
- **Evidence**: Context is supported by evidence

### **Quality Messages**
```python
# Context quality guidance for agents
def get_context_quality_message(quality: ContextQuality) -> str:
    messages = {
        ContextQuality.RED: (
            "⚠️  Context quality is RED - insufficient information. "
            "Request additional project details or clarification."
        ),
        ContextQuality.YELLOW: (
            "⚠️  Context quality is YELLOW - adequate information. "
            "Proceed with caution, may need additional context."
        ),
        ContextQuality.GREEN: (
            "✅ Context quality is GREEN - excellent information. "
            "Proceed with confidence."
        )
    }
    return messages[quality]
```

---

## 🎯 **CONTEXT TYPES & ASSEMBLY**

### **Project Context**
**Purpose**: Base context for all work
**Includes**:
- Technology stack and frameworks
- Project standards and principles
- Code patterns and amalgamations
- Business context and market intelligence
- Plugin-detected framework rules

**Commands**:
```bash
# Get project context
apm context show --work-item-id=all
apm status
```

### **Work Item Context**
**Purpose**: Scope and requirements context
**Includes**:
- 6W framework (WHO, WHAT, WHEN, WHERE, WHY, HOW)
- Acceptance criteria and requirements
- Dependencies and blockers
- Quality gates and workflow enforcement
- Business value and strategic alignment

**Commands**:
```bash
# Get work item context
apm context show --work-item-id=<work_item_id>
apm work-item show <work_item_id>
apm work-item list-dependencies <work_item_id>
```

### **Task Context**
**Purpose**: Implementation-specific context
**Includes**:
- Specific implementation details
- Time-boxing constraints and limits
- Agent guidance and SOPs
- Success criteria and quality requirements
- Evidence-based decision tracking

**Commands**:
```bash
# Get task context
apm context show --task-id=<task_id>
apm task show <task_id>
apm task list-dependencies <task_id>
```

### **Agent Context**
**Purpose**: Specialized agent guidance
**Includes**:
- Agent-specific capabilities and tools
- Domain expertise and patterns
- Specialized workflows and procedures
- Context-appropriate principles
- Agent-specific quality requirements

**Commands**:
```bash
# Get agent-specific context
apm context show --agent=<specialized_agent> --task-id=<task_id>
apm agents list
```

---

## 🔧 **CONTEXT ASSEMBLY PROCESS**

### **Step 1: Project Context Discovery**
```bash
# Check project status and tech stack
apm status
apm context show --work-item-id=all
```

### **Step 2: Work Item Context Assembly**
```bash
# Get work item details and dependencies
apm work-item show <work_item_id>
apm work-item list-dependencies <work_item_id>
apm context show --work-item-id=<work_item_id>
```

### **Step 3: Task Context Assembly**
```bash
# Get task details and constraints
apm task show <task_id>
apm context show --task-id=<task_id>
```

### **Step 4: Agent Context Selection**
```bash
# Select appropriate agent and get specialized context
apm context show --agent=<specialized_agent> --task-id=<task_id>
```

### **Step 5: Context Quality Validation**
```bash
# Check context quality and confidence
apm context show --task-id=<task_id>
# Look for quality indicators and confidence scores
```

---

## 🎨 **CONTEXT-FIRST APPROACH**

### **ALWAYS Start with Context**
1. **Get Hierarchical Context**: `apm context show --task-id=<id>`
2. **Review Quality Indicators**: Check RED/YELLOW/GREEN status
3. **Understand Dependencies**: Check work item and task dependencies
4. **Follow Established Patterns**: Use existing code patterns and decisions
5. **Record New Decisions**: Use `apm session add-decision` for all decisions

### **Context Quality Checklist**
- [ ] Project context loaded (tech stack, frameworks, patterns)
- [ ] Work item context complete (scope, requirements, dependencies)
- [ ] Task context available (implementation details, constraints)
- [ ] Agent context selected (appropriate specialization)
- [ ] Context quality GREEN (>0.8 confidence)
- [ ] Dependencies verified and resolved
- [ ] Quality gates validated

---

## 🚨 **CONTEXT TROUBLESHOOTING**

### **Low Context Quality (RED/YELLOW)**

**Symptoms**: Context confidence < 0.8
**Diagnostic**:
```bash
apm context show --task-id=<id>
apm context show --work-item-id=<id>
```

**Recovery**:
- Enrich context with additional evidence
- Add missing sources and references
- Document decision rationale
- Refresh stale context: `apm context refresh --work-item-id=<id>`
- Re-check confidence score

### **Missing Context Elements**

**Symptoms**: Incomplete context information
**Diagnostic**:
```bash
apm work-item show <id>
apm task show <id>
apm context show --work-item-id=<id>
```

**Recovery**:
- Complete missing work item details
- Add required task metadata
- Update acceptance criteria
- Document business context
- Add evidence and sources

### **Stale Context**

**Symptoms**: Context doesn't reflect current state
**Diagnostic**:
```bash
apm context show --work-item-id=<id>
# Check freshness indicators
```

**Recovery**:
- Refresh context: `apm context refresh --work-item-id=<id>`
- Update work item status
- Sync task progress
- Re-assemble context

---

## 📈 **CONTEXT OPTIMIZATION**

### **Context Assembly Best Practices**
- **Start Early**: Get context before starting any work
- **Refresh Regularly**: Update context as work progresses
- **Validate Quality**: Ensure GREEN context quality before proceeding
- **Use Appropriate Agents**: Select context based on work type
- **Document Decisions**: Record all context-based decisions

### **Performance Optimization**
- **Context Caching**: Reuse context when appropriate
- **Incremental Updates**: Only refresh changed elements
- **Selective Assembly**: Get only needed context types
- **Agent Specialization**: Use agent-specific context when available

### **Context Monitoring**
```bash
# Monitor context quality trends
apm context show --work-item-id=all

# Track context usage patterns
apm learnings list --type=context-usage --recent

# Monitor context effectiveness
apm learnings list --type=learning --search="context effectiveness"
```

---

## 🎯 **CONTEXT INTEGRATION POINTS**

### **Key Integration Points**
1. **Context Retrieval**: `apm context show --task-id=<id>` - Complete hierarchical context
2. **Work Item Management**: `apm work-item list` - Current work items and dependencies
3. **Task Management**: `apm task create` - With validation and quality gates
4. **Dependency Management**: `apm work-item add-dependency` - Work item sequencing
5. **Quality Gates**: Automatic enforcement of workflow requirements
6. **Evidence Tracking**: `apm learnings record` - Decision tracking with evidence
7. **Multi-Agent Pipeline**: Comprehensive idea assessment before development
8. **Contextual Principles**: Dynamic principle selection based on project context

### **Context Usage Patterns**
```bash
# Session start pattern
apm status
apm work-item list
apm context show --work-item-id=all

# Work item start pattern
apm work-item show <id>
apm context show --work-item-id=<id>
apm work-item validate <id>

# Task start pattern
apm task show <id>
apm context show --task-id=<id>
apm task start <id>

# Agent delegation pattern
apm context show --agent=<specialized_agent> --task-id=<id>
```

---

## 📊 **CONTEXT SUCCESS METRICS**

### **Context Quality Metrics**
- **Context Quality**: >80% GREEN context quality scores
- **Context Freshness**: <5s context delivery time
- **Context Completeness**: All required elements present
- **Context Accuracy**: Reflects current state accurately
- **Context Relevance**: Appropriate for task type

### **Context Usage Metrics**
- **Context Retrieval**: Context retrieved before all work
- **Context Validation**: Quality checked before proceeding
- **Context Refresh**: Stale context refreshed appropriately
- **Agent Selection**: Appropriate agents used based on context
- **Decision Recording**: All context-based decisions documented

### **Monitoring Commands**
```bash
# Check context quality distribution
apm context show --work-item-id=all

# Monitor context usage patterns
apm session history --search="context"

# Track context effectiveness
apm summary list --search="context"
```

---

## 🎯 **CONTEXT SYSTEM INTEGRATION**

### **With Multi-Agent Analysis Pipeline**
- Context provides input for comprehensive idea analysis
- Agent selection based on context and work type
- Evidence-based decisions recorded in context

### **With Quality Gates**
- Context validates quality gate requirements
- Workflow enforcement based on context state
- Dependencies managed through context assembly

### **With Learning System**
- Context decisions recorded as learnings
- Patterns captured from context usage
- Continuous improvement based on context effectiveness

---

**Remember: Context is the foundation of intelligent agent operation. Always start with comprehensive context assembly and maintain high context quality throughout the development lifecycle.**
