# Agent File Format Analysis & Redesign

## 🔍 **Current Issues Identified**

### 1. **Broken Rule Formatting**
- **Problem**: Lines 33-352 contain malformed rule entries with empty rule IDs (`****`)
- **Impact**: Rules are unreadable and non-functional
- **Root Cause**: Template generation process creating invalid markdown

### 2. **Massive Content Duplication**
- **Problem**: Entire project ruleset (75+ rules) embedded in every agent file
- **Impact**: 
  - Files are 400+ lines long (should be ~100 lines)
  - Maintenance nightmare - rules updated in 85+ places
  - Inconsistent rule descriptions across agents
- **Root Cause**: Poor separation of concerns between agent-specific and project-wide content

### 3. **Poor Structure & Organization**
- **Problem**: Mixing agent responsibilities with generic project rules
- **Impact**: Difficult to find agent-specific information
- **Root Cause**: No clear template structure or content boundaries

### 4. **Outdated References**
- **Problem**: References to "tests-BAK" directory and other outdated paths
- **Impact**: Confusion and incorrect guidance
- **Root Cause**: Template not updated after refactoring

### 5. **Inconsistent Formatting**
- **Problem**: Inconsistent rule formatting, missing rule IDs, malformed enforcement levels
- **Impact**: Rules cannot be parsed or validated
- **Root Cause**: Template generation logic errors

## 🎯 **Proposed Solution: New Agent Format**

### **Key Design Principles**

1. **Separation of Concerns**: Agent-specific content only, reference project rules
2. **Consistency**: Standardised structure across all agents
3. **Maintainability**: Easy to update and maintain
4. **Clarity**: Clear, focused content for each agent
5. **Extensibility**: Easy to add new sections as needed

### **New Format Structure**

```markdown
---
name: agent-name
description: Brief description
tier: 1|2|3
type: specialist|orchestrator|utility|generic
tools: [tool1, tool2, tool3]
---

# Agent Name

**Persona**: [Agent Persona]
**Tier**: [1|2|3] - [Sub-Agent|Specialist|Orchestrator]

## Core Responsibilities
- [Specific responsibility 1]
- [Specific responsibility 2]

## Agent Type & Pattern
**Type**: [specialist|orchestrator|utility|generic]
**Implementation Pattern**: [Description of how this agent works]

## Project Rules Compliance
This agent follows all project rules defined in the project governance system. 
Key applicable rules:
- [Rule ID]: [Brief description]
- [Rule ID]: [Brief description]

## Quality Standards
### Testing Requirements
- [Agent-specific testing requirements]

### Code Quality
- [Agent-specific code quality requirements]

### Documentation
- [Agent-specific documentation requirements]

## Workflow Integration
### State Transitions
- Accept tasks via `apm task accept <id> --agent [agent-name]`
- [Other workflow steps]

### Collaboration Patterns
- [Agent-specific collaboration requirements]

## Tools & Capabilities
### Primary Tools
- [List of primary tools]

### MCP Server Usage
- [MCP server usage patterns]

## Success Criteria
[Clear, measurable success criteria]

## Escalation Protocol
### When to Escalate
- [Specific escalation triggers]

### Escalation Path
1. [Escalation steps]

---
*Generated from database agent record. Last updated: [timestamp]*
```

## 📊 **Benefits of New Format**

### **Size Reduction**
- **Current**: 400+ lines per agent
- **New**: ~100 lines per agent
- **Reduction**: 75% smaller files

### **Maintainability**
- **Current**: Update rules in 85+ files
- **New**: Update rules in one place, reference in agents
- **Improvement**: 85x easier maintenance

### **Consistency**
- **Current**: Inconsistent formatting and content
- **New**: Standardised structure across all agents
- **Improvement**: 100% consistency

### **Clarity**
- **Current**: Mixed agent-specific and generic content
- **New**: Focused, agent-specific content only
- **Improvement**: Much clearer purpose and responsibilities

## 🔧 **Implementation Plan**

### **Phase 1: Template Creation**
- ✅ Create new agent template
- ✅ Create example agent-builder-new.md
- ✅ Document new format structure

### **Phase 2: Migration Strategy**
- [ ] Create migration script to convert existing agents
- [ ] Validate new format with sample agents
- [ ] Update agent generation process

### **Phase 3: Full Migration**
- [ ] Migrate all 85 agents to new format
- [ ] Update agent generation templates
- [ ] Validate all agents work correctly

### **Phase 4: Cleanup**
- [ ] Remove old format templates
- [ ] Update documentation
- [ ] Train team on new format

## 🚀 **Immediate Actions Required**

1. **Fix Current agent-builder.md**: Replace with new format
2. **Update Agent Generation Process**: Use new template
3. **Create Migration Script**: Convert existing agents
4. **Validate New Format**: Test with sample agents

## 📋 **Success Criteria**

- [ ] All agent files under 150 lines
- [ ] No embedded project rules in agent files
- [ ] Consistent formatting across all agents
- [ ] Easy to maintain and update
- [ ] Clear separation of concerns
- [ ] All agents pass validation

## 🔍 **Next Steps**

1. **Review and approve new format**
2. **Create migration script**
3. **Migrate agent-builder.md as proof of concept**
4. **Plan full migration of all 85 agents**
5. **Update agent generation process**

---

*This analysis provides a comprehensive review of the current agent file format issues and proposes a clean, maintainable solution.*
