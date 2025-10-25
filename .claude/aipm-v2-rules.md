# APM (Agent Project Manager) Comprehensive Rules & Guidelines

## 🎯 **MISSION: AI Project Manager for AI Agents**

APM (Agent Project Manager) is a comprehensive AI Project Manager designed specifically to enable AI coding agents to operate effectively across the entire product development lifecycle. Every component must serve this mission of providing intelligent, context-aware guidance to AI agents.

---

## 🚀 **MULTI-AGENT ANALYSIS PIPELINE**

### **ALWAYS Use For:**
- New feature requests
- Idea evaluation
- Problem analysis
- Technology decisions
- Architecture choices
- Business strategy questions

### **Commands to Use:**
```bash
apm idea create "Description" --type=feature
apm idea analyze <idea_id> --comprehensive
```

### **Agents to Leverage:**
- Current State Analysis Agent
- Market Research Agent
- Competitive Analysis Agent
- Impact Assessment Agent
- Value Proposition Agent
- Risk Analysis Agent
- Technical Feasibility Agent
- Resource Requirements Agent

---

## 🎯 **CONTEXTUAL PRINCIPLE MATRIX**

### **ALWAYS Apply Based on Context:**
- **Startup Context**: LEAN principles, YAGNI, KISS, rapid iteration
- **Enterprise Context**: PMBOK principles, SOLID, design patterns, risk management
- **Bugfix Context**: Make it work, safety first, minimal change
- **Research Context**: Design patterns, innovation, experimentation
- **Production Context**: Safety first, minimal change, rapid resolution

### **Commands to Use:**
```bash
apm session add-decision "Principle applied: [specific principle]" --rationale="Context and reasoning"
```

### **Principles to Apply:**
- Make it Work (Foundation)
- YAGNI (You Aren't Gonna Need It)
- KISS (Keep It Simple, Stupid)
- SOLID principles
- Design patterns
- Quality engineering
- Risk management
- Market validation
- Customer focus
- ROI optimization

---

## 📊 **EVIDENCE-BASED DEVELOPMENT**

### **ALWAYS Record:**
- All decisions with supporting evidence
- Business value and impact
- Confidence scores
- Risk assessments
- Alternative considerations
- Implementation rationale

### **Commands to Use:**
```bash
apm session add-decision "Decision with evidence and business value" --rationale="Supporting evidence and confidence level"
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=decision --text="Decision details with evidence"
```

### **Evidence Types to Include:**
- Market research data
- Technical analysis
- User feedback
- Performance metrics
- Cost analysis
- Risk assessment
- Competitive analysis
- Technical feasibility studies

---

## 🏗️ **WORK ITEM DEPENDENCY MANAGEMENT**

### **ALWAYS Check:**
- Work item dependencies before starting work
- Task dependencies within work items
- Circular dependency prevention
- Critical path analysis
- Resource availability
- Timeline constraints

### **Commands to Use:**
```bash
apm work-item list-dependencies <work_item_id>
apm work-item add-dependency <id> --depends-on <id>
apm task list-dependencies <task_id>
```

### **Dependency Types to Manage:**
- Hard dependencies (blocks start)
- Soft dependencies (warns only)
- Resource dependencies
- Technical dependencies
- Business dependencies
- Timeline dependencies

---

## 🎯 **QUALITY GATES & WORKFLOW ENFORCEMENT**

### **ALWAYS Enforce:**
- Required task types for work item types
- Time-boxing limits (IMPLEMENTATION max 4h)
- Quality metadata completion
- Dependency resolution
- Blocker resolution
- Acceptance criteria validation

### **Commands to Use:**
```bash
apm work-item validate <work_item_id>
apm task list --type=implementation
apm work-item list-dependencies <work_item_id>
```

### **Quality Gate Types:**
- **FEATURE**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX**: ANALYSIS + BUGFIX + TESTING
- **RESEARCH**: RESEARCH + ANALYSIS + DOCUMENTATION
- **DOCUMENTATION**: RESEARCH + DOCUMENTATION + REVIEW

---

## 🔍 **CONTEXT ASSEMBLY**

### **ALWAYS Get:**
- Hierarchical context (Project → Work Item → Task)
- Quality indicators (RED/YELLOW/GREEN)
- Sub-agent analysis
- Confidence scores
- Freshness indicators
- Agent-specific context

### **Commands to Use:**
```bash
apm context show --task-id=<task_id>
apm context show --work-item-id=<work_item_id>
apm context show --work-item-id=all
apm context refresh --work-item-id=<work_item_id>
```

### **Context Types to Assemble:**
- Project context (tech stack, frameworks, patterns)
- Work item context (scope, requirements, dependencies)
- Task context (implementation details, constraints)
- Agent context (specialization, capabilities)
- Temporal context (session continuity, recent changes)

---

## 🤖 **AGENT SPECIALIZATION**

### **ALWAYS Use Appropriate Agents:**
- **Rapid Prototyper**: MVP work, time-critical development
- **Enterprise Architect**: Large systems, compliance requirements
- **Production Specialist**: Bug fixes, incident response
- **Quality Engineer**: Testing, documentation, compliance
- **DevOps Specialist**: Infrastructure, deployment, monitoring
- **Research Engineer**: Technology evaluation, proof of concept

### **Commands to Use:**
```bash
apm context show --agent=<specialized_agent> --task-id=<task_id>
```

### **Agent Selection Criteria:**
- Project context (startup vs enterprise)
- Work type (implementation vs research)
- Complexity level (simple vs complex)
- Time constraints (urgent vs flexible)
- Quality requirements (basic vs enterprise)

---

## 📚 **LEARNING & PATTERN CAPTURE**

### **ALWAYS Capture:**
- Implementation patterns
- Design decisions
- Problem solutions
- Best practices
- Lessons learned
- Anti-patterns to avoid

### **Commands to Use:**
```bash
apm session add-decision "Pattern discovered: [pattern description]" --rationale="Usage guidance and when to apply"
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=learning --text="Key learnings and insights"
apm document add --entity-type=work_item --entity-id=<id> --file-path="docs/patterns/[pattern-name].md" --document-type=pattern
```

### **Learning Types to Capture:**
- **Patterns**: Reusable solutions and approaches
- **Decisions**: Architectural and design decisions
- **Learnings**: Insights and lessons learned
- **Discoveries**: New findings and realizations
- **Anti-patterns**: What not to do and why

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **ALWAYS Monitor:**
- Context quality scores
- Workflow compliance rates
- Time-boxing adherence
- Dependency management effectiveness
- Evidence tracking completeness
- Learning capture rates

### **Commands to Use:**
```bash
apm session history --search="recent"
apm summary list --recent
apm work-item validate <work_item_id>
apm context show --work-item-id=all
```

### **Improvement Areas:**
- Context assembly speed and quality
- Principle application accuracy
- Agent specialization effectiveness
- Quality gate compliance
- Learning capture completeness
- Evidence tracking quality

---

## ⚠️ **MANDATORY USAGE RULES**

### **For EVERY User Request:**
- **Context Assembly**: Get hierarchical context
- **Quality Gate Check**: Validate work items and tasks
- **Dependency Check**: Verify dependencies and sequencing
- **Evidence Recording**: Record decisions with evidence
- **Pattern Recognition**: Check for existing patterns
- **Time-Boxing Verification**: Ensure compliance with limits
- **Learning Capture**: Document insights and patterns
- **Agent Specialization**: Use appropriate agent context
- **Principle Application**: Apply contextual principles
- **Continuous Improvement**: Monitor and optimize

### **For EVERY Work Item:**
- **Proper Structure**: Create required tasks based on type
- **Dependency Management**: Set up proper sequencing
- **Quality Gates**: Enforce professional standards
- **Evidence Tracking**: Record all decisions with evidence
- **Learning Capture**: Document patterns and learnings
- **Context Assembly**: Provide comprehensive context
- **Agent Specialization**: Use appropriate agents
- **Principle Application**: Apply right principles for context
- **Continuous Improvement**: Monitor effectiveness
- **Comprehensive Integration**: Use all framework components

---

## 🎯 **SUCCESS METRICS**

### **Claude is Using APM (Agent Project Manager) Comprehensively When:**
- **Multi-Agent Analysis**: Used for all new ideas and features
- **Contextual Principles**: Applied based on project context
- **Evidence-Based Development**: All decisions recorded with evidence
- **Work Item Dependencies**: Properly managed and sequenced
- **Quality Gates**: Enforced consistently across all work
- **Context Assembly**: Hierarchical context always available
- **Agent Specialization**: Appropriate agents used for work type
- **Learning Capture**: Patterns and insights continuously documented
- **Continuous Improvement**: System effectiveness monitored and optimized
- **Comprehensive Integration**: All components working together

### **Quantitative Metrics:**
- **Context Quality**: >80% GREEN context quality scores
- **Workflow Compliance**: 100% adherence to quality gates
- **Time-Boxing**: All tasks within time limits
- **Dependency Management**: No circular dependencies
- **Evidence Tracking**: All decisions recorded with evidence
- **Learning Capture**: >90% of insights documented
- **Agent Usage**: Appropriate agents used >85% of the time
- **Principle Application**: Contextual principles applied >90% of the time
- **Multi-Agent Analysis**: Used for >95% of new ideas
- **Continuous Improvement**: >10% improvement quarterly

---

**Remember: This comprehensive framework ensures Claude leverages EVERY aspect of APM (Agent Project Manager) for maximum value and consistent, high-quality development.**

---

## 📜 **UNIVERSAL AGENT RULES**

See [.claude/UNIVERSAL-AGENT-RULES.md](.claude/UNIVERSAL-AGENT-RULES.md) for the mandatory rules that all agents MUST follow.