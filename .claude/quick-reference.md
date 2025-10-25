# APM (Agent Project Manager) Quick Reference Guide

## 🚀 **START HERE - New Chat Session**

```bash
# 1. Check project status
apm status

# 2. List current work items
apm work-item list

# 3. Get context for current work
apm context show --work-item-id=all
```

## 🎯 **ESSENTIAL COMMANDS**

### **Work Item Management**
```bash
apm work-item create "Name" --type feature          # Create work item
apm work-item show <id>                             # Show details
apm work-item add-dependency <id> --depends-on <id> # Add dependency
apm work-item list-dependencies <id>                # Show dependencies
apm work-item validate <id>                         # Validate quality gates
```

### **Task Management**
```bash
apm task create "Name" --type implementation --effort 4  # Create task
apm task list                                          # List tasks
apm task start <id>                                    # Start task
apm task complete <id>                                 # Complete task
```

### **Context & Learning**
```bash
apm context show --task-id=<id>                       # Get task context
apm context show --work-item-id=<id>                  # Get work item context
apm session add-decision "Decision text" --rationale "Reasoning"  # Record decision
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=learning --text "Content"  # Create summary
```

## ⚠️ **CRITICAL RULES**

- **IMPLEMENTATION tasks max 4 hours** (enforced)
- **FEATURE requires**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT requires**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX requires**: ANALYSIS + BUGFIX + TESTING
- **Always check dependencies** before starting work
- **Always get context first** before making changes

## 🔍 **CONTEXT-FIRST APPROACH**

1. **Get context**: `apm context show --task-id=<id>`
2. **Check quality**: Look for RED/YELLOW/GREEN indicators
3. **Review dependencies**: `apm work-item list-dependencies <id>`
4. **Follow patterns**: Use established code patterns
5. **Record decisions**: `apm session add-decision` for all decisions

## 🚨 **ERROR RECOVERY**

```bash
# If something goes wrong:
apm status                                    # Check system status
apm work-item validate <id>                   # Validate work item
apm work-item list-dependencies <id>          # Check dependencies
apm context show --task-id=<id>               # Get full context
```

## 📊 **SUCCESS INDICATORS**

- ✅ Context quality: GREEN (>0.8 confidence)
- ✅ All required tasks present for work item type
- ✅ No time-box violations
- ✅ Dependencies properly sequenced
- ✅ All decisions recorded with evidence

## 🎯 **APM (Agent Project Manager) MISSION**

**Comprehensive AI Project Manager** that provides intelligent, context-aware guidance across the entire product development lifecycle. Every component serves the mission of enabling AI agents to make informed, strategic decisions.

---

**Remember: Always start with context, follow quality gates, and record decisions with evidence.**
