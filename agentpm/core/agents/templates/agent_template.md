---
name: [agent-name]
description: [Brief description of agent purpose and responsibilities]
tier: [1|2|3]
type: [specialist|orchestrator|utility|generic]
tools: [tool1, tool2, tool3]
---

# [Agent Name]

**Persona**: [Agent Persona Description]
**Tier**: [1|2|3] - [Sub-Agent|Specialist|Orchestrator]

## Core Responsibilities

- [Specific responsibility 1]
- [Specific responsibility 2]
- [Specific responsibility 3]
- [Additional responsibilities as needed]

## Agent Type & Pattern

**Type**: [specialist|orchestrator|utility|generic]
**Implementation Pattern**: [Description of how this agent works and its role in the system]

## Project Rules Compliance

This agent follows all project rules defined in the project governance system. Key applicable rules:

- **[Rule ID]**: [Brief description of how this rule applies]
- **[Rule ID]**: [Brief description of how this rule applies]
- **[Rule ID]**: [Brief description of how this rule applies]

## Quality Standards

### Testing Requirements
- [Agent-specific testing requirements]
- [Coverage requirements]
- [Test types and approaches]

### Code Quality
- [Agent-specific code quality requirements]
- [Patterns and conventions to follow]
- [Architecture principles to apply]

### Documentation
- [Agent-specific documentation requirements]
- [Documentation standards to follow]
- [Examples and usage patterns]

### Context Awareness
- [Context loading requirements]
- [Dependency understanding needs]
- [System-wide impact considerations]
- [Confidence level requirements]

## Workflow Integration

### State Transitions
- Accept tasks via `apm task accept <id> --agent [agent-name]`
- Begin work via `apm task start <id>`
- Submit for review via `apm task submit-review <id>`
- [Additional workflow steps specific to this agent]

### Collaboration Patterns
- [Agent-specific collaboration requirements]
- [Review and feedback processes]
- [Escalation and communication patterns]

## Tools & Capabilities

### Primary Tools
- [List of primary tools this agent uses]
- [Tool-specific usage patterns]
- [Capability descriptions]

### MCP Server Usage
- **[Server Name]**: [Usage pattern and purpose]
- **[Server Name]**: [Usage pattern and purpose]
- [Additional MCP server usage as needed]

## Success Criteria

[Clear, measurable success criteria for this agent]
- [Specific criterion 1]
- [Specific criterion 2]
- [Additional criteria as needed]

## Escalation Protocol

### When to Escalate
- [Specific escalation triggers for this agent]
- [Blocking conditions]
- [Ambiguity or conflict situations]

### Escalation Path
1. [First escalation step]
2. [Second escalation step]
3. [Additional steps as needed]
4. [Final resolution approach]

## [Agent-Specific Section]

[Add any agent-specific sections as needed, such as:]
- [Specialised processes]
- [Unique capabilities]
- [Domain-specific requirements]
- [Integration patterns]

---
*Generated from database agent record. Last updated: [timestamp]*
