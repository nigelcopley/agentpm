# APM (Agent Project Manager) Agent Specialization Guide

## 🎯 **AGENT SPECIALIZATION OVERVIEW**

APM (Agent Project Manager) uses a multi-agent architecture with specialized agents for different domains and contexts. Each agent has specific capabilities, tools, and expertise areas.

---

## 🤖 **PHASE ORCHESTRATORS (MAIN WORKFLOW)**

### **Definition Orchestrator** (`definition-orch`)
**Purpose**: Transform raw requests into well-defined work items
**When to Use**: D1 Discovery phase
**Delegates To**: intent-triage, context-assembler, problem-framer, value-articulator, ac-writer, risk-notary

```bash
# Get definition context
apm context show --agent=definition-orch --work-item-id=<id>
```

### **Planning Orchestrator** (`planning-orch`)
**Purpose**: Create implementation plans with tasks and dependencies
**When to Use**: P1 Planning phase
**Delegates To**: planner, estimator, dependency-mapper, mitigation-planner

```bash
# Get planning context
apm context show --agent=planning-orch --work-item-id=<id>
```

### **Implementation Orchestrator** (`implementation-orch`)
**Purpose**: Implement features following established patterns
**When to Use**: I1 Implementation phase
**Delegates To**: code-implementer, test-implementer, doc-toucher

```bash
# Get implementation context
apm context show --agent=implementation-orch --task-id=<id>
```

### **Review Orchestrator** (`review-test-orch`)
**Purpose**: Validate quality and approve for deployment
**When to Use**: R1 Review phase
**Delegates To**: reviewer, test-runner, quality-gatekeeper

```bash
# Get review context
apm context show --agent=review-test-orch --task-id=<id>
```

### **Release Operations Orchestrator** (`release-ops-orch`)
**Purpose**: Deploy to production and ensure operational readiness
**When to Use**: O1 Operations phase
**Delegates To**: deploy-orchestrator, health-verifier, versioner

```bash
# Get operations context
apm context show --agent=release-ops-orch --work-item-id=<id>
```

### **Evolution Orchestrator** (`evolution-orch`)
**Purpose**: Analyze telemetry and plan improvements
**When to Use**: E1 Evolution phase
**Delegates To**: signal-harvester, insight-synthesizer, backlog-curator

```bash
# Get evolution context
apm context show --agent=evolution-orch --work-item-id=<id>
```

---

## 🔧 **SPECIALIST AGENTS (DOMAIN EXPERTISE)**

### **Python/CLI Developer** (`aipm-python-cli-developer`)
**Purpose**: Python development, CLI commands, APM (Agent Project Manager) codebase
**When to Use**: Implementing Python code, CLI commands, core services
**Expertise**: Python, Click, Rich, Pydantic, database patterns

```bash
# Get Python development context
apm context show --agent=aipm-python-cli-developer --task-id=<id>
```

### **Database Developer** (`aipm-database-developer`)
**Purpose**: Database operations, schema changes, migrations
**When to Use**: Database design, migrations, data operations
**Expertise**: SQLite, migrations, three-layer architecture

```bash
# Get database context
apm context show --agent=aipm-database-developer --task-id=<id>
```

### **Testing Specialist** (`aipm-testing-specialist`)
**Purpose**: Test creation, coverage analysis, quality validation
**When to Use**: Writing tests, coverage analysis, quality gates
**Expertise**: pytest, coverage, TDD, integration testing

```bash
# Get testing context
apm context show --agent=aipm-testing-specialist --task-id=<id>
```

### **Documentation Specialist** (`aipm-documentation-specialist`)
**Purpose**: User guides, API docs, developer documentation
**When to Use**: Creating documentation, user guides, API docs
**Expertise**: Markdown, technical writing, user experience

```bash
# Get documentation context
apm context show --agent=aipm-documentation-specialist --task-id=<id>
```

### **Quality Validator** (`aipm-quality-validator`)
**Purpose**: Gate checks, compliance validation, quality assurance
**When to Use**: Quality gate validation, compliance checks
**Expertise**: Quality gates, workflow validation, standards compliance

```bash
# Get quality validation context
apm context show --agent=aipm-quality-validator --work-item-id=<id>
```

---

## 🎯 **SUB-AGENTS (SINGLE RESPONSIBILITY)**

### **Context Assembly** (MANDATORY at session start)
**Agent**: `context-delivery`
**Purpose**: Assemble project context from database
**When**: Every session start, before any work

```bash
# Get comprehensive context
apm context show --work-item-id=all
```

### **Other Sub-Agents**
- `intent-triage`: Analyze user intent
- `ac-writer`: Write acceptance criteria
- `test-runner`: Execute test suites
- `quality-gatekeeper`: Validate quality gates
- `code-implementer`: Implement code patterns
- `evidence-writer`: Record decisions with evidence
- `pattern-applier`: Apply established patterns
- `risk-notary`: Identify and assess risks

---

## 🎨 **CONTEXT-SPECIFIC AGENT SELECTION**

### **Startup Context**
**Primary Agents**: Rapid Prototyper, Implementation Orchestrator
**Principles**: LEAN, YAGNI, KISS, rapid iteration
**Focus**: Speed, minimal viable product, quick feedback

```bash
# Startup context commands
apm context show --agent=rapid-prototyper --task-id=<id>
apm learnings record --type=decision --content="LEAN principle applied: [specific principle]"
```

### **Enterprise Context**
**Primary Agents**: Enterprise Architect, Quality Validator
**Principles**: PMBOK, SOLID, design patterns, risk management
**Focus**: Compliance, scalability, maintainability, governance

```bash
# Enterprise context commands
apm context show --agent=enterprise-architect --task-id=<id>
apm learnings record --type=decision --content="PMBOK principle applied: [specific principle]"
```

### **Bugfix Context**
**Primary Agents**: Production Specialist, Root Cause Analyst
**Principles**: Make it work, safety first, minimal change
**Focus**: Rapid resolution, minimal risk, production stability

```bash
# Bugfix context commands
apm context show --agent=production-specialist --task-id=<id>
apm learnings record --type=decision --content="Rapid resolution principle applied: [specific principle]"
```

### **Research Context**
**Primary Agents**: Research Engineer, Deep Research Agent
**Principles**: Design patterns, innovation, experimentation
**Focus**: Exploration, proof of concept, technical feasibility

```bash
# Research context commands
apm context show --agent=research-engineer --task-id=<id>
apm learnings record --type=decision --content="Experimentation principle applied: [specific principle]"
```

---

## 🔄 **AGENT DELEGATION PATTERNS**

### **When to Delegate to Claude Agents**

APM (Agent Project Manager) uses a multi-agent architecture. Delegate work to specialist agents for:

#### **Phase Orchestrators (Main Workflow)**
- **D1 Discovery**: Use `definition-orch` for requirements gathering
- **P1 Planning**: Use `planning-orch` for task decomposition
- **I1 Implementation**: Use `implementation-orch` for feature development
- **R1 Review**: Use `review-test-orch` for quality validation
- **O1 Operations**: Use `release-ops-orch` for deployment
- **E1 Evolution**: Use `evolution-orch` for continuous improvement

#### **Specialist Agents (Domain Expertise)**
- **Python/CLI development**: Use `aipm-python-cli-developer`
- **Database operations**: Use `aipm-database-developer`
- **Testing**: Use `aipm-testing-specialist`
- **Documentation**: Use `aipm-documentation-specialist`
- **Quality validation**: Use `aipm-quality-validator`

#### **Sub-Agents (Single Responsibility)**
- **Context Assembly**: Use `context-delivery` (MANDATORY)
- **Intent Analysis**: Use `intent-triage`
- **Acceptance Criteria**: Use `ac-writer`
- **Test Execution**: Use `test-runner`
- **Quality Gates**: Use `quality-gatekeeper`

### **Delegation Pattern**

**DO NOT implement directly. Instead:**

1. Identify the work type (discovery, planning, implementation, review, etc.)
2. Select appropriate agent from table above
3. Document the delegation in commit or task notes
4. Let the agent handle the specialized work

---

## 📊 **AGENT SELECTION CRITERIA**

### **Work Type Selection**
- **Implementation**: Use Implementation Orchestrator + Python/CLI Developer
- **Testing**: Use Testing Specialist + Review Orchestrator
- **Documentation**: Use Documentation Specialist
- **Database**: Use Database Developer
- **Quality**: Use Quality Validator
- **Research**: Use Research Engineer

### **Complexity Selection**
- **Simple**: Use sub-agents directly
- **Medium**: Use specialist agents
- **Complex**: Use orchestrators with delegation

### **Time Constraints**
- **Urgent**: Use Rapid Prototyper or Production Specialist
- **Flexible**: Use appropriate orchestrator with full delegation

### **Quality Requirements**
- **Basic**: Use Implementation Orchestrator
- **Enterprise**: Use Enterprise Architect + Quality Validator

---

## 🎯 **AGENT INTEGRATION COMMANDS**

### **Context Assembly (MANDATORY)**
```bash
# Get comprehensive context for any work
apm context show --work-item-id=all
apm context show --task-id=<id>
apm context show --agent=<specialized_agent> --task-id=<id>
```

### **Agent Selection**
```bash
# List available agents
apm agents list

# Get agent-specific context
apm context show --agent=<agent_name> --task-id=<id>

# Record agent usage
apm session add-decision "Agent specialization applied: [agent name]" --rationale="Work type and context for agent selection"
```

### **Delegation Documentation**
```bash
# Record delegation decision
apm session add-decision "Delegated to [agent] for [reason]" --rationale="Context and rationale for delegation"

# Record agent effectiveness
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=learning --text="Agent [name] effectiveness: [results]"
```

---

## 🚨 **AGENT USAGE RULES**

### **MANDATORY Usage**
- **Context Assembly**: Always use `context-delivery` at session start
- **Phase Orchestration**: Use appropriate orchestrator for each phase
- **Specialist Delegation**: Use specialist agents for domain-specific work
- **Documentation**: Record all agent usage and effectiveness

### **PROHIBITED Actions**
- ❌ Never implement directly when specialist agents available
- ❌ Never skip context assembly
- ❌ Never bypass agent delegation
- ❌ Never use wrong agent for work type

### **BEST PRACTICES**
- ✅ Always start with context assembly
- ✅ Select agent based on work type and complexity
- ✅ Document delegation decisions
- ✅ Record agent effectiveness
- ✅ Use appropriate agent for project context

---

## 📈 **AGENT EFFECTIVENESS METRICS**

### **Success Indicators**
- **Context Quality**: >80% GREEN context quality scores
- **Agent Usage**: Appropriate agents used >85% of the time
- **Delegation Accuracy**: Correct agent selected >90% of the time
- **Work Quality**: High-quality deliverables from specialist agents
- **Time Efficiency**: Faster completion with specialist agents

### **Monitoring Commands**
```bash
# Check agent usage patterns
apm session history --search="agent"

# Monitor context quality
apm context show --work-item-id=all

# Track agent effectiveness
apm summary list --search="agent effectiveness"
```

---

**Remember: Agent specialization ensures high-quality, efficient work by leveraging domain expertise and established patterns. Always use the appropriate agent for the work type and context.**
