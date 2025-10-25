# APM (Agent Project Manager) Issue Tracking Guide

## 🚨 **MANDATORY: ALWAYS CREATE AIPM IDEAS FOR ISSUES**

**When encountering ANY issue, bug, or problem, Claude MUST create an AIPM idea to track and resolve it.**

---

## 🎯 **TRIGGER CONDITIONS**

### **ALWAYS Create AIPM Ideas When:**
- [ ] **Error Messages**: Any error, exception, or failure occurs
- [ ] **Bug Reports**: User reports a bug or issue
- [ ] **Performance Issues**: Slow performance, timeouts, or resource problems
- [ ] **Integration Problems**: API failures, connection issues, or external service problems
- [ ] **Test Failures**: Any test fails or coverage drops below 90%
- [ ] **Build Failures**: CI/CD pipeline failures or deployment issues
- [ ] **Security Issues**: Vulnerabilities, security warnings, or compliance violations
- [ ] **User Experience Issues**: UI/UX problems, accessibility issues, or usability concerns
- [ ] **Data Issues**: Data corruption, validation failures, or data quality problems
- [ ] **Configuration Issues**: Environment problems, missing dependencies, or setup issues
- [ ] **Documentation Issues**: Missing, outdated, or incorrect documentation
- [ ] **Code Quality Issues**: Linting errors, code smells, or maintainability problems

---

## 📝 **MANDATORY AIPM IDEA CREATION**

### **For EVERY Issue Encountered:**
```bash
# ALWAYS create AIPM idea for the issue
apm idea create "Issue: [Brief Description]" --type=bugfix

# ALWAYS include comprehensive issue details
apm idea update <idea_id> --description="
## Issue Description
[Detailed description of the issue]

## Error Details
[Exact error messages, stack traces, or symptoms]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment Details
- OS: [Operating system]
- Browser: [If applicable]
- Version: [Software version]
- Dependencies: [Relevant dependencies]

## Impact Assessment
- Severity: [Critical/High/Medium/Low]
- Affected Users: [Number or description]
- Business Impact: [Description of impact]

## Proposed Solution
[Initial thoughts on how to fix]

## Additional Context
[Any other relevant information]
"

# ALWAYS set appropriate priority based on severity
apm idea update <idea_id> --priority=critical  # For critical issues
apm idea update <idea_id> --priority=high      # For high severity
apm idea update <idea_id> --priority=medium    # For medium severity
apm idea update <idea_id> --priority=low       # For low severity
```

---

## 🔍 **ISSUE ANALYSIS WORKFLOW**

### **After Creating the AIPM Idea:**
```bash
# ALWAYS run comprehensive analysis on the issue
apm idea analyze <idea_id> --comprehensive

# ALWAYS check for similar known issues
apm session history --search="error keywords"
apm work-item list --type=bugfix --search="similar keywords"

# ALWAYS create work item for issue resolution
apm work-item create "Fix: [Issue Description]" --type=bugfix

# ALWAYS add required tasks for BUGFIX
apm task create "Analyze Issue" --type=analysis --effort=4
apm task create "Implement Fix" --type=bugfix --effort=4
apm task create "Test Fix" --type=testing --effort=3

# ALWAYS record issue analysis
apm session add-decision "Issue analysis and resolution approach" --rationale="Root cause analysis and fix strategy"
```

---

## 📊 **ISSUE CATEGORIZATION**

### **Issue Types and AIPM Idea Categories:**

#### **Critical Issues (Priority: Critical)**
```bash
# System crashes, data loss, security vulnerabilities
apm idea create "CRITICAL: [Issue Description]" --type=bugfix --priority=critical
```

#### **High Priority Issues (Priority: High)**
```bash
# Major functionality broken, performance degradation
apm idea create "HIGH: [Issue Description]" --type=bugfix --priority=high
```

#### **Medium Priority Issues (Priority: Medium)**
```bash
# Minor bugs, UI issues, non-critical problems
apm idea create "MEDIUM: [Issue Description]" --type=bugfix --priority=medium
```

#### **Low Priority Issues (Priority: Low)**
```bash
# Cosmetic issues, minor improvements, nice-to-haves
apm idea create "LOW: [Issue Description]" --type=bugfix --priority=low
```

---

## 🎯 **ISSUE RESOLUTION TRACKING**

### **During Issue Resolution:**
```bash
# ALWAYS update idea with progress
apm idea update <idea_id> --status=in-progress

# ALWAYS record investigation findings
apm session add-decision "Investigation findings and root cause analysis" --rationale="Technical analysis and findings"

# ALWAYS document solution approach
apm session add-decision "Solution approach and implementation details" --rationale="Fix strategy and implementation plan"

# ALWAYS test the fix
apm task complete <task_id> --evidence="Fix tested and verified"

# ALWAYS update idea with resolution
apm idea update <idea_id> --status=resolved --resolution="Issue resolved with [solution details]"
```

---

## 📈 **ISSUE PATTERN RECOGNITION**

### **ALWAYS Look for Patterns:**
```bash
# ALWAYS check for recurring issues
apm session history --search="recurring issues"

# ALWAYS identify common root causes
apm session history --search="root causes"

# ALWAYS document issue patterns
apm session add-decision "Issue pattern: [pattern description]" --rationale="Prevention guidance and pattern recognition"

# ALWAYS create prevention strategies
apm session add-decision "Prevention strategy for [issue type]" --rationale="Proactive measures to prevent similar issues"
```

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **ALWAYS Learn from Issues:**
```bash
# ALWAYS analyze issue trends
apm session history --search="issue trends"

# ALWAYS identify improvement opportunities
apm session add-decision "Process improvement based on issue analysis" --rationale="Lessons learned and process enhancements"

# ALWAYS update prevention measures
apm session add-decision "Updated prevention measures for [issue category]" --rationale="Enhanced prevention strategies"
```

---

## ⚠️ **MANDATORY COMPLIANCE**

### **NEVER Skip Issue Tracking:**
- [ ] **NEVER** ignore errors or warnings
- [ ] **NEVER** fix issues without creating AIPM ideas
- [ ] **NEVER** skip issue analysis and documentation
- [ ] **NEVER** resolve issues without proper testing
- [ ] **NEVER** forget to record lessons learned

### **ALWAYS Do These Steps:**
1. **Create AIPM Idea** - For every issue encountered
2. **Analyze Issue** - Run comprehensive analysis
3. **Create Work Item** - Set up proper bugfix work item
4. **Document Solution** - Record investigation and solution
5. **Test Fix** - Verify the fix works
6. **Learn from Issue** - Capture patterns and prevention strategies

---

## 🎯 **SUCCESS INDICATORS**

### **Claude is Following Issue Tracking Rule When:**
- ✅ Every error/issue has a corresponding AIPM idea
- ✅ All issues are properly categorized and prioritized
- ✅ Issue analysis is comprehensive and documented
- ✅ Solutions are tested and verified
- ✅ Patterns are recognized and documented
- ✅ Prevention strategies are developed
- ✅ Lessons learned are captured
- ✅ Issue trends are analyzed
- ✅ Continuous improvement is applied

---

## 📋 **ISSUE TRACKING CHECKLIST**

### **For EVERY Issue:**
- [ ] **Create AIPM Idea** with detailed description
- [ ] **Set Priority** based on severity assessment
- [ ] **Run Analysis** using comprehensive analysis pipeline
- [ ] **Check Similar Issues** for patterns and existing solutions
- [ ] **Create Work Item** with proper bugfix structure
- [ ] **Add Required Tasks** (Analyze, Fix, Test)
- [ ] **Record Investigation** findings and root cause
- [ ] **Document Solution** approach and implementation
- [ ] **Test Fix** thoroughly before marking resolved
- [ ] **Update Idea** with resolution details
- [ ] **Capture Patterns** for future prevention
- [ ] **Learn and Improve** from the issue

---

**Remember: Every issue is an opportunity to learn, improve, and prevent future problems. Always create AIPM ideas to track, analyze, and resolve issues systematically.**
