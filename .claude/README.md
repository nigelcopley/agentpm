# APM (Agent Project Manager) Claude Integration Guide

## 🎯 **OVERVIEW**

This `.claude/` directory contains comprehensive guidance for AI agents working with APM (Agent Project Manager). It consolidates all rules, workflows, and agent guidance into a structured format that enables intelligent, context-aware development.

---

## 📁 **DIRECTORY STRUCTURE**

```
.claude/
├── README.md                           # This file - overview and navigation
├── aipm-v2-rules.md                   # Core APM (Agent Project Manager) rules and comprehensive framework
├── workflow-phases.md                 # D1→P1→I1→R1→O1→E1 workflow phases and quality gates
├── agent-specialization-guide.md      # Multi-agent architecture and specialization
├── context-system-guide.md            # Hierarchical context assembly and quality scoring
├── quick-reference.md                 # Essential commands and quick start guide
├── issue-tracking-guide.md            # Mandatory issue tracking and resolution
├── agents/                            # Individual agent definitions and SOPs
│   ├── master-orchestrator.md         # Main orchestrator for routing work
│   ├── orchestrators/                 # Phase-specific orchestrators
│   ├── sub-agents/                    # Single-responsibility agents
│   └── utilities/                     # Utility agents and tools
├── hooks/                             # Session hooks and automation
├── analysis/                          # Analysis reports and findings
└── commands/                          # Command-specific guidance
```

---

## 🚀 **QUICK START**

### **For New Chat Sessions:**
1. **Read**: `.claude/quick-reference.md` - Essential commands and rules
2. **Understand**: `.claude/aipm-v2-rules.md` - Core framework principles
3. **Follow**: `.claude/workflow-phases.md` - Phase progression and quality gates
4. **Use**: `.claude/context-system-guide.md` - Context assembly and quality scoring

### **For Issue Resolution:**
1. **Read**: `.claude/issue-tracking-guide.md` - Mandatory issue tracking
2. **Create**: AIPM idea for every issue encountered
3. **Analyze**: Use comprehensive analysis pipeline
4. **Resolve**: Follow systematic resolution workflow

### **For Agent Specialization:**
1. **Read**: `.claude/agent-specialization-guide.md` - Multi-agent architecture
2. **Select**: Appropriate agent based on work type and context
3. **Delegate**: Use specialist agents for domain-specific work
4. **Document**: Record agent usage and effectiveness

---

## 🎯 **CORE PRINCIPLES**

### **1. Context-First Approach**
- **ALWAYS** start with context assembly: `apm context show --work-item-id=all`
- **ALWAYS** check context quality (RED/YELLOW/GREEN indicators)
- **ALWAYS** validate dependencies before starting work
- **ALWAYS** follow established patterns and decisions

### **2. Quality Gates Enforcement**
- **IMPLEMENTATION tasks max 4 hours** (STRICT enforcement)
- **FEATURE requires**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT requires**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX requires**: ANALYSIS + BUGFIX + TESTING
- **ALWAYS** validate before state transitions

### **3. Evidence-Based Development**
- **ALWAYS** record decisions with evidence: `apm session add-decision`
- **ALWAYS** document rationale and business value
- **ALWAYS** track confidence scores and risk assessments
- **ALWAYS** capture patterns and learnings

### **4. Multi-Agent Architecture**
- **ALWAYS** use appropriate agent specialization
- **ALWAYS** delegate to specialist agents for domain work
- **ALWAYS** document agent usage and effectiveness
- **ALWAYS** follow phase-based orchestration

### **5. Issue Tracking (MANDATORY)**
- **ALWAYS** create AIPM idea for every issue/error
- **ALWAYS** run comprehensive analysis on issues
- **ALWAYS** document resolution approach and testing
- **ALWAYS** capture patterns for prevention

---

## 📊 **SUCCESS METRICS**

### **Context Quality**
- **Target**: >80% GREEN context quality scores
- **Command**: `apm context show --work-item-id=all`
- **Indicator**: Context confidence >0.8

### **Workflow Compliance**
- **Target**: 100% adherence to quality gates
- **Command**: `apm work-item validate <id>`
- **Indicator**: All required tasks present, no time-box violations

### **Evidence Tracking**
- **Target**: All decisions recorded with evidence
- **Command**: `apm session history --search="decision"`
- **Indicator**: Comprehensive decision documentation

### **Agent Usage**
- **Target**: Appropriate agents used >85% of the time
- **Command**: `apm session history --search="agent"`
- **Indicator**: Specialist agents used for domain work

### **Issue Resolution**
- **Target**: Every issue has corresponding AIPM idea
- **Command**: `apm idea list --type=bugfix`
- **Indicator**: Systematic issue tracking and resolution

---

## 🔧 **ESSENTIAL COMMANDS**

### **Session Start**
```bash
apm status                                    # Project dashboard
apm work-item list                           # Current work items
apm context show --work-item-id=all          # Comprehensive context
```

### **Work Item Management**
```bash
apm work-item create "Name" --type feature   # Create work item
apm work-item show <id>                      # Show details
apm work-item validate <id>                  # Validate quality gates
apm work-item add-dependency <id> --depends-on <id>  # Add dependency
```

### **Task Management**
```bash
apm task create "Name" --type implementation --effort 4  # Create task
apm task start <id>                         # Start task
apm task complete <id>                      # Complete task
apm context show --task-id=<id>             # Get task context
```

### **Decision Recording**
```bash
apm session add-decision "Decision text" --rationale "Reasoning"  # Record decision
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=learning --text "Content"  # Create summary
apm document add --entity-type=work_item --entity-id=<id> --file-path="path" --document-type=pattern  # Add document
```

### **Issue Tracking**
```bash
apm idea create "Issue: Description" --type=bugfix  # Create issue idea
apm idea analyze <id> --comprehensive               # Analyze issue
apm work-item create "Fix: Description" --type=bugfix  # Create fix work item
```

---

## 🚨 **CRITICAL RULES**

### **NEVER Skip These:**
- ❌ **Context Assembly** - Always get context before work
- ❌ **Quality Gates** - Always validate before transitions
- ❌ **Evidence Recording** - Always record decisions with evidence
- ❌ **Issue Tracking** - Always create AIPM ideas for issues
- ❌ **Time-Boxing** - Never exceed 4h for IMPLEMENTATION tasks
- ❌ **Dependencies** - Always check dependencies before starting

### **ALWAYS Do These:**
- ✅ **Start with Context** - Get comprehensive context first
- ✅ **Follow Quality Gates** - Enforce professional standards
- ✅ **Record Decisions** - Document all decisions with evidence
- ✅ **Use Specialist Agents** - Delegate to appropriate agents
- ✅ **Track Issues** - Create AIPM ideas for all issues
- ✅ **Validate Work** - Check quality before completion

---

## 📚 **DETAILED GUIDES**

### **Core Framework**
- **`.claude/aipm-v2-rules.md`** - Comprehensive APM (Agent Project Manager) rules and framework
- **`.claude/workflow-phases.md`** - D1→P1→I1→R1→O1→E1 workflow phases
- **`.claude/context-system-guide.md`** - Hierarchical context assembly

### **Agent Architecture**
- **`.claude/agent-specialization-guide.md`** - Multi-agent architecture
- **`.claude/agents/`** - Individual agent definitions and SOPs

### **Operational Guides**
- **`.claude/quick-reference.md`** - Essential commands and quick start
- **`.claude/issue-tracking-guide.md`** - Mandatory issue tracking

---

## 🎯 **INTEGRATION POINTS**

### **With APM (Agent Project Manager) System**
- **Database-Driven**: All state from database, not files
- **Quality Gates**: Automatic enforcement of workflow requirements
- **Context Assembly**: Hierarchical context with quality scoring
- **Multi-Agent Pipeline**: Comprehensive idea assessment
- **Evidence-Based**: Decision tracking with confidence scoring

### **With Claude Agents**
- **Agent Specialization**: Domain-specific expertise and tools
- **Phase Orchestration**: Workflow-based agent coordination
- **Context Delivery**: Structured, actionable context for agents
- **Quality Enforcement**: Prevents agents from skipping essential steps

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **Monitor Effectiveness**
```bash
apm context show --work-item-id=all          # Context quality
apm session history --search="decision"      # Decision tracking
apm session history --search="agent"         # Agent usage
apm idea list --type=bugfix                  # Issue tracking
```

### **Optimize Performance**
- **Context Quality**: Maintain >80% GREEN scores
- **Workflow Compliance**: 100% quality gate adherence
- **Agent Usage**: >85% appropriate agent selection
- **Issue Resolution**: Systematic tracking and resolution
- **Learning Capture**: >90% of insights documented

---

**Remember: This comprehensive framework ensures consistent, high-quality development by providing intelligent, context-aware guidance to AI agents across the entire product development lifecycle.**
