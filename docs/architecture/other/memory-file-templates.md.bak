# Memory File Templates Specification

## Overview

This document defines the specific templates and formats for each of the 7 memory files in the Claude Memory System. Each template provides a consistent structure for extracting, formatting, and presenting APM (Agent Project Manager) database content to Claude.

## Template Structure

Each memory file follows this standard structure:
```markdown
# [TITLE] - [SUBTITLE]

## Overview
[Brief description of the system/component]

## [MAIN CONTENT SECTIONS]
[Structured data from database]

## Last Updated
- **Date**: [timestamp]
- **Source**: [database tables]
- **Version**: [file version]
- **Checksum**: [content hash]

## Related Files
- [Links to related memory files]
```

## 1. RULES.md Template

### Source Data
- `rules` table (project-specific rules)
- `agentpm/core/rules/config/rules_catalog.yaml` (catalog rules)
- Rule categories and enforcement levels

### Template Structure
```markdown
# APM (Agent Project Manager) Governance Rules

## Overview
Comprehensive governance rules system with 245 rules across 9 categories, enforcing development standards, workflow processes, and quality gates.

## Rule Categories
| Category | Code | Count | Description |
|----------|------|-------|-------------|
| Development Principles | DP | 55 | Core development practices and time-boxing |
| Workflow Rules | WR | 35 | Process and state transition rules |
| Code Quality | CQ | 40 | Code standards and quality requirements |
| Documentation | DOC | 25 | Documentation standards and requirements |
| Workflow & Process | WF | 20 | Process management and workflow rules |
| Technology Constraints | TC | 15 | Technology-specific limitations |
| Operations | OPS | 20 | Deployment and operational requirements |
| Governance | GOV | 15 | Project governance and compliance |
| Testing Requirements | TEST | 20 | Testing standards and coverage requirements |

## Presets
| Preset | Rules | Target User | Philosophy |
|--------|-------|-------------|------------|
| **Minimal** | 15 | Solo dev, prototype | Breadth over depth - one per category |
| **Standard** | 71 | Small team, MVP | Balanced - 2-3 per category |
| **Professional** | 220 | Production team | Deep security/testing/quality |
| **Enterprise** | 245 | Large org, compliance | Complete governance |

## Active Rules (Project-Specific)
[Generated from database rules table]

### Development Principles (DP)
[Rules with DP category, showing rule_id, name, description, enforcement_level, config]

### Workflow Rules (WR)
[Rules with WR category]

### Code Quality (CQ)
[Rules with CQ category]

### Documentation (DOC)
[Rules with DOC category]

### Workflow & Process (WF)
[Rules with WF category]

### Technology Constraints (TC)
[Rules with TC category]

### Operations (OPS)
[Rules with OPS category]

### Governance (GOV)
[Rules with GOV category]

### Testing Requirements (TEST)
[Rules with TEST category]

## Enforcement Levels
- **BLOCK**: Hard constraint - operation fails if rule violated
- **LIMIT**: Soft constraint - warning but operation succeeds
- **GUIDE**: Suggestion - informational only
- **ENHANCE**: Context enrichment - adds intelligence, no enforcement

## Time-Boxing Rules
- **IMPLEMENTATION**: ≤4h (STRICT - DP-001)
- **TESTING**: ≤6h (DP-002)
- **DESIGN**: ≤8h (DP-003)
- **DOCUMENTATION**: ≤6h (DP-004)

## Last Updated
- **Date**: [current timestamp]
- **Source**: rules table, rules_catalog.yaml
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [PRINCIPLES.md](./PRINCIPLES.md) - Development principles pyramid
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
```

## 2. PRINCIPLES.md Template

### Source Data
- `agentpm/core/database/enums/development_principles.py`
- Principle definitions and priority hierarchy

### Template Structure
```markdown
# Development Principles Pyramid

## Overview
The Pyramid of Software Development Principles provides a hierarchical framework for decision-making, with lower numbers indicating higher priority.

## 12-Tier Hierarchy

### Foundation Layer (Priority 1)
**1. Make it Work**
- **Definition**: Functionality first, optimization second
- **When to Apply**: Always - foundation of all development
- **Examples**: Get basic feature working before optimizing

### Core Principles (Priorities 2-6)
**2. YAGNI (You Aren't Gonna Need It)**
- **Definition**: Don't build what you don't need yet
- **When to Apply**: When considering future features
- **Examples**: Avoid over-engineering, build only current requirements

**3. Principle of Least Surprise**
- **Definition**: Code should behave as expected
- **When to Apply**: API design, user interface design
- **Examples**: Consistent naming, predictable behavior

**4. KISS (Keep It Simple, Stupid)**
- **Definition**: Simplicity is the ultimate sophistication
- **When to Apply**: When complexity is growing
- **Examples**: Choose simple solutions over complex ones

**5. Be Consistent**
- **Definition**: Follow established patterns and conventions
- **When to Apply**: Throughout codebase and processes
- **Examples**: Consistent naming, formatting, architecture

**6. DRY (Don't Repeat Yourself)**
- **Definition**: Avoid code duplication
- **When to Apply**: When you find repeated code
- **Examples**: Extract common functionality, use abstractions

### Quality Principles (Priorities 7-8)
**7. Clean Code**
- **Definition**: Code should be readable and maintainable
- **When to Apply**: During code review and refactoring
- **Examples**: Clear variable names, small functions, good comments

**8. SOLID Principles**
- **Definition**: Five object-oriented design principles
- **When to Apply**: Object-oriented design decisions
- **Examples**: Single responsibility, open/closed principle

### Advanced Principles (Priorities 9-12)
**9. Design Patterns**
- **Definition**: Proven solutions to common problems
- **When to Apply**: When solving recurring design problems
- **Examples**: Factory pattern, Observer pattern, MVC

**10. Agile Practices**
- **Definition**: Iterative development and collaboration
- **When to Apply**: Project management and team processes
- **Examples**: Sprints, retrospectives, continuous integration

**11. Boy Scout Rule**
- **Definition**: Leave code better than you found it
- **When to Apply**: During maintenance and bug fixes
- **Examples**: Refactor while fixing, improve documentation

**12. Make it Fast**
- **Definition**: Optimize for performance when needed
- **When to Apply**: After functionality is working
- **Examples**: Performance profiling, algorithm optimization

## Additional Principles

### AHA Rule of Three
- **Definition**: Extract abstraction after third occurrence
- **When to Apply**: When you see repeated code patterns
- **Examples**: Don't abstract too early, wait for pattern to emerge

### Single Source of Truth
- **Definition**: Each piece of data should have one authoritative source
- **When to Apply**: Data management and configuration
- **Examples**: Centralized configuration, single database

### Build vs Buy vs Reuse
- **Definition**: Evaluate options before implementing
- **When to Apply**: When adding new functionality
- **Examples**: Use existing libraries, evaluate third-party solutions

## Priority Decision Matrix
| Situation | Primary Principle | Secondary Principle |
|-----------|------------------|-------------------|
| New Feature | Make it Work | YAGNI |
| Code Review | Clean Code | Be Consistent |
| Performance Issue | Make it Fast | Make it Work |
| Duplicate Code | DRY | Clean Code |
| Complex Problem | KISS | Design Patterns |

## Last Updated
- **Date**: [current timestamp]
- **Source**: development_principles.py enum
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [RULES.md](./RULES.md) - Governance rules enforcement
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
```

## 3. WORKFLOW.md Template

### Source Data
- `agentpm/core/workflow/` directory
- Workflow phase definitions and quality gates
- Work item types and required tasks

### Template Structure
```markdown
# APM (Agent Project Manager) Workflow System

## Overview
Quality-gated workflow system with 6 phases, enforcing professional standards and preventing agents from bypassing essential steps.

## 6-Phase Workflow

### D1: Discovery
- **Purpose**: Define user needs, validate market fit, gather requirements
- **Status**: draft
- **Required Tasks**: analysis, research, design
- **Gate Requirements**: Business context (≥50 chars), acceptance criteria (≥3), risks (≥1)

### P1: Plan
- **Purpose**: Create technical design, break down work, plan dependencies
- **Status**: ready
- **Required Tasks**: design, planning
- **Gate Requirements**: Technical design complete, dependencies identified

### I1: Implementation
- **Purpose**: Implement feature, write tests, document code
- **Status**: active
- **Required Tasks**: implementation, testing, documentation
- **Gate Requirements**: Code complete, tests passing, documentation done

### R1: Review
- **Purpose**: Quality validation, acceptance criteria verification
- **Status**: review
- **Required Tasks**: review, testing
- **Gate Requirements**: All acceptance criteria met, quality review passed

### O1: Operations
- **Purpose**: Deploy successfully, monitor performance
- **Status**: done
- **Required Tasks**: deployment, monitoring
- **Gate Requirements**: Deployment successful, monitoring active

### E1: Evolution
- **Purpose**: Historical tracking, learning capture
- **Status**: archived
- **Required Tasks**: documentation, learning
- **Gate Requirements**: Lessons learned captured, documentation complete

## Work Item Types & Required Tasks

### FEATURE (New functionality)
**Required Tasks**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **Design**: Architecture and technical design (≤8h)
- **Implementation**: Code changes (≤4h STRICT)
- **Testing**: Test coverage (≤6h)
- **Documentation**: Docs and guides (≤6h)

### ENHANCEMENT (Improvements)
**Required Tasks**: DESIGN + IMPLEMENTATION + TESTING
- **Design**: Improvement design (≤8h)
- **Implementation**: Code changes (≤4h STRICT)
- **Testing**: Test coverage (≤6h)

### BUGFIX (Bug fixes)
**Required Tasks**: ANALYSIS + BUGFIX + TESTING
- **Analysis**: Root cause analysis (≤4h)
- **Bugfix**: Fix implementation (≤4h)
- **Testing**: Test coverage (≤6h)

### RESEARCH (Investigation)
**Required Tasks**: ANALYSIS + DOCUMENTATION
- **Analysis**: Investigation and research (≤6h)
- **Documentation**: Findings documentation (≤6h)

### PLANNING (Planning work)
**Forbidden Tasks**: IMPLEMENTATION
- **Allowed**: analysis, design, documentation, research

## Quality Gates (CI Gates)

### CI-001: Agent Validation
- **Requirement**: Valid, active agent assigned before task start
- **Enforcement**: Block task → ACTIVE if agent invalid
- **Checks**: Agent assigned, exists in registry, is active

### CI-002: Context Quality
- **Requirement**: Context confidence >70% before task start
- **Enforcement**: Block task → ACTIVE if context quality low
- **Checks**: 6W completeness ≥70%, no stale contexts, required fields present

### CI-004: Testing Quality
- **Requirement**: Tests passing before review, acceptance criteria met before completion
- **Enforcement**: Block task → REVIEW/DONE if tests fail
- **Checks**: Tests passing, acceptance criteria met, coverage >90%

### CI-005: Acceptance Criteria
- **Requirement**: All acceptance criteria met before completion
- **Enforcement**: Block work item → DONE if criteria not met
- **Checks**: All criteria validated, evidence provided

## Time-Boxing Limits (STRICT)

| Task Type | Max Hours | Enforcement | Rationale |
|-----------|-----------|-------------|-----------|
| **IMPLEMENTATION** | 4h | BLOCK | Prevents scope creep |
| **TESTING** | 6h | BLOCK | Scoped test effort |
| **DESIGN** | 8h | BLOCK | Prevents analysis paralysis |
| **DOCUMENTATION** | 6h | BLOCK | Reasonable documentation scope |
| **ANALYSIS** | 6h | LIMIT | Investigation scope |
| **RESEARCH** | 8h | LIMIT | Research scope |

## State Transitions

### Work Item States
- **draft** → **ready** → **active** → **review** → **done** → **archived**
- **draft** → **cancelled** (at any time)

### Task States
- **draft** → **ready** → **active** → **review** → **done**
- **draft** → **cancelled** (at any time)

## Workflow Enforcement

### Quality Gate Validation
- **Phase Gates**: Must complete phase requirements before advancement
- **State Gates**: Must meet state requirements before transition
- **Time Gates**: Must respect time-boxing limits
- **Dependency Gates**: Must resolve dependencies before start

### Agent Workflow Enforcement
- **Prevent Skipping**: Agents cannot bypass required steps
- **Quality Enforcement**: Professional standards enforced throughout
- **Evidence Tracking**: All decisions recorded with evidence
- **Learning Capture**: Patterns and insights continuously documented

## Last Updated
- **Date**: [current timestamp]
- **Source**: workflow service, phase validators, quality gates
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [RULES.md](./RULES.md) - Governance rules enforcement
- [PRINCIPLES.md](./PRINCIPLES.md) - Development principles
- [AGENTS.md](./AGENTS.md) - Agent system and capabilities
```

## 4. AGENTS.md Template

### Source Data
- `agents` table (project agents)
- `agentpm/core/agents/` directory
- Agent definitions, capabilities, and SOPs

### Template Structure
```markdown
# APM (Agent Project Manager) Agent System

## Overview
Comprehensive agent system with 100+ specialized AI assistants, organized by tiers and categories, each with specific roles, capabilities, and Standard Operating Procedures.

## Agent Tiers

### Tier 1: Sub-Agents (Specialized Tasks)
- **Purpose**: Handle specific, focused tasks
- **Examples**: code-analyzer, test-runner, documentation-writer
- **Characteristics**: Narrow scope, high expertise in specific domain

### Tier 2: Specialists (Domain Experts)
- **Purpose**: Manage complex domain-specific work
- **Examples**: backend-architect, frontend-specialist, devops-engineer
- **Characteristics**: Broad domain knowledge, can coordinate sub-agents

### Tier 3: Orchestrators (Workflow Coordination)
- **Purpose**: Coordinate complex workflows and multiple agents
- **Examples**: master-orchestrator, definition-orch, implementation-orch
- **Characteristics**: High-level coordination, workflow management

## Agent Categories

### Orchestrator
- **Purpose**: High-level workflow coordination
- **Examples**: master-orchestrator, definition-orch, implementation-orch
- **Capabilities**: Workflow management, agent coordination, decision making

### Sub-Agent
- **Purpose**: Specific task execution
- **Examples**: code-analyzer, test-runner, documentation-writer
- **Capabilities**: Focused task execution, specialized expertise

### Specialist
- **Purpose**: Domain expertise and complex problem solving
- **Examples**: backend-architect, frontend-specialist, security-engineer
- **Capabilities**: Domain knowledge, architectural decisions, mentoring

### Utility
- **Purpose**: Supporting functions and tools
- **Examples**: audit-logger, evidence-writer, workflow-updater
- **Capabilities**: Logging, documentation, system maintenance

### Generic
- **Purpose**: General-purpose assistance
- **Examples**: python-expert, technical-writer, reviewer
- **Capabilities**: General expertise, flexible application

## Active Agents (Project-Specific)

### Orchestrators
[Generated from database agents table with tier=3]

| Role | Display Name | Description | Capabilities |
|------|--------------|-------------|--------------|
| [role] | [display_name] | [description] | [capabilities] |

### Specialists
[Generated from database agents table with tier=2]

| Role | Display Name | Description | Capabilities |
|------|--------------|-------------|--------------|
| [role] | [display_name] | [description] | [capabilities] |

### Sub-Agents
[Generated from database agents table with tier=1]

| Role | Display Name | Description | Capabilities |
|------|--------------|-------------|--------------|
| [role] | [display_name] | [description] | [capabilities] |

### Utilities
[Generated from database agents table with category=utility]

| Role | Display Name | Description | Capabilities |
|------|--------------|-------------|--------------|
| [role] | [display_name] | [description] | [capabilities] |

## Agent Selection Criteria

### By Work Type
- **Implementation**: python-implementer, code-implementer, backend-architect
- **Testing**: test-implementer, test-runner, quality-engineer
- **Design**: system-architect, backend-architect, frontend-architect
- **Documentation**: technical-writer, documentation-writer, doc-toucher
- **Analysis**: code-analyzer, requirements-analyst, root-cause-analyst

### By Domain
- **Backend**: backend-architect, python-expert, database-developer
- **Frontend**: frontend-architect, react-specialist, ui-designer
- **DevOps**: devops-architect, deployment-specialist, infrastructure-engineer
- **Security**: security-engineer, threat-screener, compliance-specialist
- **Quality**: quality-engineer, test-specialist, code-reviewer

### By Complexity
- **Simple Tasks**: sub-agents (tier 1)
- **Complex Problems**: specialists (tier 2)
- **Workflow Coordination**: orchestrators (tier 3)

## Agent Capabilities Matrix

| Capability | Orchestrator | Specialist | Sub-Agent | Utility |
|------------|--------------|------------|-----------|---------|
| Workflow Management | ✅ | ⚠️ | ❌ | ❌ |
| Domain Expertise | ⚠️ | ✅ | ✅ | ❌ |
| Task Execution | ⚠️ | ✅ | ✅ | ✅ |
| Decision Making | ✅ | ✅ | ❌ | ❌ |
| Agent Coordination | ✅ | ⚠️ | ❌ | ❌ |
| System Maintenance | ❌ | ⚠️ | ❌ | ✅ |

## Standard Operating Procedures (SOPs)

### Agent SOP Structure
Each agent has a detailed SOP covering:
- **Role Definition**: Clear purpose and responsibilities
- **Capabilities**: Specific skills and tools
- **Workflow**: How to approach tasks
- **Quality Standards**: Expected output quality
- **Integration**: How to work with other agents

### Example SOP: Python Implementer
```markdown
# Python Implementer Agent SOP

## Role
Implement Python code following APM (Agent Project Manager) patterns and quality standards.

## Capabilities
- Python development
- APM (Agent Project Manager) service patterns
- Database integration
- Testing implementation
- Code review

## Workflow
1. Analyze requirements
2. Follow DatabaseService pattern
3. Implement three-layer architecture
4. Write comprehensive tests
5. Document code and decisions

## Quality Standards
- >90% test coverage
- Type hints required
- Comprehensive docstrings
- Actionable error messages
- Rich CLI formatting
```

## Agent Assignment Rules

### Automatic Assignment
- **By Task Type**: Implementation tasks → implementer agents
- **By Domain**: Backend tasks → backend specialists
- **By Complexity**: Simple tasks → sub-agents, complex → specialists

### Manual Assignment
- **Expertise Required**: Specific domain knowledge needed
- **Workflow Coordination**: Orchestrator needed for complex workflows
- **Quality Assurance**: Specialist needed for critical components

## Agent Performance Metrics

### Usage Tracking
- **Last Used**: When agent was last assigned to a task
- **Task Count**: Number of tasks completed
- **Success Rate**: Percentage of successful task completions
- **Quality Score**: Average quality of agent output

### Performance Optimization
- **Agent Selection**: Choose best agent for task type and complexity
- **Workload Distribution**: Balance work across available agents
- **Capability Matching**: Match agent capabilities to task requirements
- **Continuous Improvement**: Update agent SOPs based on performance

## Last Updated
- **Date**: [current timestamp]
- **Source**: agents table, agent definitions
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
- [CONTEXT.md](./CONTEXT.md) - Context assembly system
- [PROJECT.md](./PROJECT.md) - Project context and information
```

## 5. CONTEXT.md Template

### Source Data
- `contexts` table (project contexts)
- Context service and assembly logic
- UnifiedSixW framework definitions

### Template Structure
```markdown
# APM (Agent Project Manager) Context System

## Overview
Hierarchical context assembly system providing comprehensive project, work item, and task context through the UnifiedSixW framework with confidence scoring and quality indicators.

## UnifiedSixW Framework

The UnifiedSixW framework provides consistent structure across all context levels (Project/WorkItem/Task) with the same fields but different granularity.

### WHO - People and Roles
**Scales**: @cto → @team → @alice
- **Project Level**: @cto, @team, @stakeholders
- **WorkItem Level**: @team, @tech-lead, @designer
- **Task Level**: @alice, @bob, @agent-python-dev

### WHAT - Requirements
**Scales**: system → component → function
- **Project Level**: System requirements, business goals
- **WorkItem Level**: Component requirements, feature scope
- **Task Level**: Function requirements, specific acceptance criteria

### WHERE - Technical Context
**Scales**: infrastructure → services → files
- **Project Level**: Infrastructure, all services, cloud platform
- **WorkItem Level**: Specific services, microservices, modules
- **Task Level**: Files, functions, specific code locations

### WHEN - Timeline
**Scales**: quarters → weeks → days
- **Project Level**: Quarters, major milestones
- **WorkItem Level**: Weeks, sprint goals
- **Task Level**: Days, hours, immediate dependencies

### WHY - Value Proposition
**Scales**: business → feature → technical
- **Project Level**: Business value, market impact
- **WorkItem Level**: Feature value, user benefit
- **Task Level**: Technical necessity, debt reduction

### HOW - Approach
**Scales**: architecture → patterns → implementation
- **Project Level**: Architecture, system patterns
- **WorkItem Level**: Design patterns, component patterns
- **Task Level**: Implementation details, algorithms

## Context Types

### Entity Contexts
- **project_context**: Project-level 6W information
- **work_item_context**: Work item-level 6W information
- **task_context**: Task-level 6W information

### Rich Context Types
- **business_pillars_context**: Business strategy and pillars
- **market_research_context**: Market analysis and research
- **competitive_analysis_context**: Competitive landscape
- **quality_gates_context**: Quality requirements and gates
- **stakeholder_context**: Stakeholder information and needs
- **technical_context**: Technical architecture and constraints
- **implementation_context**: Implementation details and patterns

### Ideas Integration
- **idea_context**: Idea analysis and evaluation
- **idea_to_work_item_mapping**: Idea to work item relationships

## Confidence Scoring

### Confidence Bands
- **RED**: <0.6 confidence - insufficient context
- **YELLOW**: 0.6-0.8 confidence - adequate context
- **GREEN**: >0.8 confidence - excellent context

### Confidence Factors
- **6W Completeness**: Percentage of 6W fields populated
- **Freshness**: How recent the context information is
- **Source Quality**: Reliability of context sources
- **Validation**: Whether context has been validated

### Context Quality Messages
- **RED**: "⚠️ Context quality is RED - insufficient information. Request additional project details or clarification."
- **YELLOW**: "⚠️ Context quality is YELLOW - adequate information. Proceed with caution, may need additional context."
- **GREEN**: "✅ Context quality is GREEN - excellent information. Proceed with confidence."

## Active Contexts (Project-Specific)

### Project Contexts
[Generated from contexts table with context_type=project_context]

| Context ID | Entity ID | Confidence | 6W Completeness | Last Updated |
|------------|-----------|------------|-----------------|--------------|
| [id] | [entity_id] | [confidence] | [completeness] | [timestamp] |

### Work Item Contexts
[Generated from contexts table with context_type=work_item_context]

| Context ID | Entity ID | Confidence | 6W Completeness | Last Updated |
|------------|-----------|------------|-----------------|--------------|
| [id] | [entity_id] | [confidence] | [completeness] | [timestamp] |

### Task Contexts
[Generated from contexts table with context_type=task_context]

| Context ID | Entity ID | Confidence | 6W Completeness | Last Updated |
|------------|-----------|------------|-----------------|--------------|
| [id] | [entity_id] | [confidence] | [completeness] | [timestamp] |

## Context Assembly Process

### Hierarchical Assembly
1. **Project Context**: Base context from project information
2. **Work Item Context**: Work item-specific context
3. **Task Context**: Task-specific implementation context
4. **Agent Context**: Agent-specific guidance and capabilities

### Context Quality Indicators
- **Confidence Score**: 0.0-1.0 numerical score
- **Confidence Band**: RED/YELLOW/GREEN visual indicator
- **Freshness**: Time since last update
- **Completeness**: Percentage of required fields populated

### Context Delivery
- **Automatic**: Context provided without agent requests
- **Structured**: Clear, organized format for agent consumption
- **Actionable**: Includes guidance and next actions
- **Comprehensive**: All relevant information included

## Context Usage Patterns

### Agent Context Consumption
- **Context-First Approach**: Always get context before work
- **Quality Assessment**: Check confidence indicators
- **Pattern Recognition**: Use existing patterns and decisions
- **Evidence Recording**: Record new decisions with evidence

### Context Update Triggers
- **Database Changes**: Context updated when underlying data changes
- **Work Item Changes**: Context refreshed when work items change
- **Task Changes**: Context updated when tasks progress
- **Manual Refresh**: On-demand context updates

## Context Validation

### Quality Checks
- **Completeness**: All required 6W fields present
- **Accuracy**: Context matches current database state
- **Freshness**: Context is not stale (>90 days)
- **Consistency**: Context is internally consistent

### Validation Rules
- **6W Completeness**: ≥70% for YELLOW, ≥80% for GREEN
- **Freshness**: <30 days for GREEN, <90 days for YELLOW
- **Source Validation**: Context sources are reliable
- **Cross-Validation**: Context is consistent across levels

## Last Updated
- **Date**: [current timestamp]
- **Source**: contexts table, context service
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [PROJECT.md](./PROJECT.md) - Project context and information
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
- [AGENTS.md](./AGENTS.md) - Agent system and capabilities
```

## 6. PROJECT.md Template

### Source Data
- `projects` table (project information)
- Project service and metadata
- Business context and technical stack

### Template Structure
```markdown
# APM (Agent Project Manager) Project Context

## Overview
Current project information, business context, technical stack, and development status for APM (Agent Project Manager) system.

## Project Information

### Basic Details
- **Name**: [project name]
- **Description**: [project description]
- **Path**: [project filesystem path]
- **Status**: [project status]
- **Created**: [creation timestamp]
- **Updated**: [last update timestamp]

### Business Context
- **Business Domain**: [business domain]
- **Business Description**: [business description]
- **Project Type**: [project type]
- **Team**: [team name]

### Technical Stack
- **Tech Stack**: [detected technologies]
- **Frameworks**: [detected frameworks]
- **Languages**: [primary languages]
- **Tools**: [development tools]

## Project Lifecycle

### Current Status: [status]
- **Lifecycle Stage**: [initiated/active/on_hold/completed/archived]
- **Development Phase**: [current phase]
- **Next Milestone**: [next milestone]

### Status Transitions
- **initiated** → **active**: Project setup complete, development started
- **active** → **on_hold**: Development paused, resources reallocated
- **active** → **completed**: All objectives met, project finished
- **completed** → **archived**: Project archived, historical record

## Work Items Summary

### Work Item Distribution
| Type | Count | Status Distribution |
|------|-------|-------------------|
| Feature | [count] | [status breakdown] |
| Enhancement | [count] | [status breakdown] |
| Bugfix | [count] | [status breakdown] |
| Research | [count] | [status breakdown] |
| Planning | [count] | [status breakdown] |
| Refactoring | [count] | [status breakdown] |

### Task Summary
| Type | Count | Total Hours | Status Distribution |
|------|-------|-------------|-------------------|
| Implementation | [count] | [hours] | [status breakdown] |
| Testing | [count] | [hours] | [status breakdown] |
| Design | [count] | [hours] | [status breakdown] |
| Documentation | [count] | [hours] | [status breakdown] |
| Analysis | [count] | [hours] | [status breakdown] |

## Quality Metrics

### Time-Boxing Compliance
- **Compliant Tasks**: [count]/[total] ([percentage]%)
- **Violations**: [count] violations
- **Most Common Violation**: [violation type]

### Test Coverage
- **Overall Coverage**: [percentage]%
- **Target Coverage**: >90%
- **Coverage Status**: [meeting/not meeting] target

### Workflow Compliance
- **Quality Gates**: [percentage]% compliance
- **Required Tasks**: [percentage]% present
- **State Transitions**: [percentage]% valid

## Active Work

### Current Work Items
[Generated from active work items]

| ID | Name | Type | Status | Priority |
|----|------|------|--------|----------|
| [id] | [name] | [type] | [status] | [priority] |

### Current Tasks
[Generated from active tasks]

| ID | Name | Type | Status | Effort | Assigned |
|----|------|------|--------|--------|----------|
| [id] | [name] | [type] | [status] | [effort] | [agent] |

## Project Configuration

### Rules Configuration
- **Active Rules**: [count] rules enabled
- **Preset**: [preset name]
- **Enforcement Level**: [enforcement level]

### Agent Configuration
- **Active Agents**: [count] agents
- **Agent Tiers**: [tier distribution]
- **Agent Categories**: [category distribution]

### Context Configuration
- **Context Types**: [context type count]
- **Confidence Threshold**: [threshold]
- **Update Frequency**: [frequency]

## Development Environment

### Database
- **Database Path**: [database path]
- **Schema Version**: [schema version]
- **Migration Status**: [migration status]

### Plugins
- **Active Plugins**: [plugin list]
- **Plugin Status**: [plugin status]

### CLI
- **CLI Version**: [version]
- **Command Count**: [command count]
- **Performance**: [performance metrics]

## Business Value

### Objectives
- **Primary Objective**: [primary objective]
- **Success Metrics**: [success metrics]
- **Target Timeline**: [timeline]

### Stakeholders
- **Primary Stakeholders**: [stakeholder list]
- **Decision Makers**: [decision maker list]
- **End Users**: [end user list]

### Constraints
- **Technical Constraints**: [technical constraints]
- **Business Constraints**: [business constraints]
- **Timeline Constraints**: [timeline constraints]

## Last Updated
- **Date**: [current timestamp]
- **Source**: projects table, project service
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [CONTEXT.md](./CONTEXT.md) - Context assembly system
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
- [AGENTS.md](./AGENTS.md) - Agent system and capabilities
- [RULES.md](./RULES.md) - Governance rules enforcement
```

## 7. IDEAS.md Template

### Source Data
- `ideas` table (project ideas)
- Ideas service and analysis pipeline
- Multi-agent analysis results

### Template Structure
```markdown
# APM (Agent Project Manager) Ideas System

## Overview
Multi-agent analysis pipeline for comprehensive idea evaluation, including market research, competitive analysis, impact assessment, and technical feasibility analysis.

## Multi-Agent Analysis Pipeline

### Current State Analysis Agent
- **Purpose**: Analyze current system state and capabilities
- **Output**: Current state assessment, gap analysis
- **Usage**: Baseline for idea evaluation

### Market Research Agent
- **Purpose**: Research market trends and opportunities
- **Output**: Market analysis, trend identification
- **Usage**: Market validation for ideas

### Competitive Analysis Agent
- **Purpose**: Analyze competitive landscape
- **Output**: Competitive positioning, differentiation
- **Usage**: Competitive advantage assessment

### Impact Assessment Agent
- **Purpose**: Evaluate business and technical impact
- **Output**: Impact analysis, risk assessment
- **Usage**: Value proposition evaluation

### Value Proposition Agent
- **Purpose**: Define and validate value proposition
- **Output**: Value proposition, target audience
- **Usage**: Business value assessment

### Risk Analysis Agent
- **Purpose**: Identify and assess risks
- **Output**: Risk register, mitigation strategies
- **Usage**: Risk management planning

### Technical Feasibility Agent
- **Purpose**: Assess technical implementation feasibility
- **Output**: Technical analysis, implementation plan
- **Usage**: Technical validation

### Resource Requirements Agent
- **Purpose**: Estimate resource needs
- **Output**: Resource estimates, timeline
- **Usage**: Planning and budgeting

## Idea Analysis Workflow

### 1. Idea Capture
- **Input**: Idea description, initial context
- **Process**: Structured idea capture
- **Output**: Initial idea record

### 2. Multi-Agent Analysis
- **Input**: Idea record
- **Process**: Parallel agent analysis
- **Output**: Comprehensive analysis results

### 3. Synthesis and Evaluation
- **Input**: Analysis results
- **Process**: Result synthesis, scoring
- **Output**: Evaluation report, recommendations

### 4. Work Item Creation
- **Input**: Approved ideas
- **Process**: Work item generation
- **Output**: Structured work items

## Active Ideas (Project-Specific)

### Recent Ideas
[Generated from ideas table]

| ID | Title | Type | Status | Priority | Analysis Status |
|----|-------|------|--------|----------|-----------------|
| [id] | [title] | [type] | [status] | [priority] | [analysis_status] |

### Analysis Results
[Generated from idea analysis results]

| Idea ID | Market Score | Technical Score | Business Score | Overall Score | Recommendation |
|---------|--------------|-----------------|----------------|---------------|----------------|
| [id] | [score] | [score] | [score] | [score] | [recommendation] |

## Idea Categories

### Feature Ideas
- **New Features**: New functionality requests
- **Enhancements**: Improvements to existing features
- **Integrations**: Third-party integrations

### Technical Ideas
- **Architecture**: System architecture improvements
- **Performance**: Performance optimization ideas
- **Security**: Security enhancement ideas

### Process Ideas
- **Workflow**: Workflow improvement ideas
- **Quality**: Quality process improvements
- **Automation**: Automation opportunities

### Business Ideas
- **Market**: Market expansion ideas
- **Product**: Product development ideas
- **Partnership**: Partnership opportunities

## Analysis Scoring

### Scoring Criteria
- **Market Potential**: 0-10 scale
- **Technical Feasibility**: 0-10 scale
- **Business Value**: 0-10 scale
- **Resource Requirements**: 0-10 scale (lower = better)
- **Risk Level**: 0-10 scale (lower = better)

### Overall Score Calculation
```
Overall Score = (Market + Technical + Business) / 3 - (Resources + Risk) / 2
```

### Score Interpretation
- **8-10**: Excellent - High priority implementation
- **6-8**: Good - Consider for implementation
- **4-6**: Fair - Evaluate carefully
- **2-4**: Poor - Low priority
- **0-2**: Reject - Not viable

## Idea to Work Item Mapping

### Conversion Process
1. **Idea Approval**: Idea meets minimum score threshold
2. **Work Item Creation**: Generate appropriate work item type
3. **Task Breakdown**: Create required tasks based on work item type
4. **Dependency Setup**: Establish dependencies and sequencing

### Work Item Type Selection
- **Feature Ideas** → FEATURE work items
- **Enhancement Ideas** → ENHANCEMENT work items
- **Technical Ideas** → REFACTORING work items
- **Research Ideas** → RESEARCH work items

## Analysis Templates

### Market Analysis Template
```markdown
## Market Analysis
- **Market Size**: [size estimate]
- **Growth Rate**: [growth rate]
- **Competition**: [competitive landscape]
- **Opportunity**: [market opportunity]
```

### Technical Analysis Template
```markdown
## Technical Analysis
- **Feasibility**: [feasibility assessment]
- **Complexity**: [complexity rating]
- **Dependencies**: [technical dependencies]
- **Timeline**: [implementation timeline]
```

### Business Analysis Template
```markdown
## Business Analysis
- **Value Proposition**: [value proposition]
- **Target Audience**: [target audience]
- **Revenue Impact**: [revenue impact]
- **Strategic Alignment**: [strategic alignment]
```

## Idea Management Commands

### CLI Commands
```bash
# Create new idea
apm idea create "Idea description" --type=feature

# Run comprehensive analysis
apm idea analyze <idea_id> --comprehensive

# Convert to work item
apm idea convert <idea_id> --work-item-type=feature

# List ideas
apm idea list --status=active
```

## Last Updated
- **Date**: [current timestamp]
- **Source**: ideas table, ideas service
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [PROJECT.md](./PROJECT.md) - Project context and information
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
- [AGENTS.md](./AGENTS.md) - Agent system and capabilities
```

## Template Generation Process

### Database Extraction
Each template includes specific database queries to extract relevant data:

```python
# Example extraction for RULES.md
def extract_rules_data(project_id: int) -> Dict[str, Any]:
    """Extract rules data for memory file generation"""
    return {
        'project_rules': query_rules_table(project_id),
        'catalog_rules': load_rules_catalog(),
        'categories': get_rule_categories(),
        'presets': get_rule_presets()
    }
```

### Template Rendering
Templates use Jinja2-style syntax for dynamic content:

```python
# Example template rendering
def render_rules_template(data: Dict[str, Any]) -> str:
    """Render RULES.md template with data"""
    template = load_template('rules.md.j2')
    return template.render(**data)
```

### File Generation
Generated files include metadata and validation:

```python
# Example file generation
def generate_memory_file(filename: str, content: str) -> None:
    """Generate memory file with metadata"""
    filepath = Path('.claude') / filename
    filepath.write_text(content)
    update_file_metadata(filepath)
```

## Last Updated
- **Date**: [current timestamp]
- **Source**: Template specifications
- **Version**: 1.0
- **Checksum**: [content hash]

## Related Files
- [claude-memory-system-architecture.md](./claude-memory-system-architecture.md) - Overall system architecture
- [RULES.md](../.claude/RULES.md) - Generated rules memory file
- [PRINCIPLES.md](../.claude/PRINCIPLES.md) - Generated principles memory file
- [WORKFLOW.md](../.claude/WORKFLOW.md) - Generated workflow memory file
- [AGENTS.md](../.claude/AGENTS.md) - Generated agents memory file
- [CONTEXT.md](../.claude/CONTEXT.md) - Generated context memory file
- [PROJECT.md](../.claude/PROJECT.md) - Generated project memory file
- [IDEAS.md](../.claude/IDEAS.md) - Generated ideas memory file
