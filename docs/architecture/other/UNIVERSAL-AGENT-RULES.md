# Universal Agent Rules - MANDATORY FOR ALL AGENTS

**Version**: 1.0
**Date**: 2025-10-17
**Status**: REQUIRED - All agents MUST follow these rules

---

## 🚨 **MANDATORY RULES** (Every Agent, Every Time)

### **Rule 1: Summary Obligation** (MUST)

**Every agent that works on ANY entity MUST create a summary.**

```bash
# After working on a project
apm summary create --entity-type=project --entity-id=<id> \
  --summary-type=session_progress \
  --text="What was accomplished, decisions made, next steps"

# After working on a work item
apm summary create --entity-type=work_item --entity-id=<id> \
  --summary-type=work_item_progress \
  --text="Progress update, blockers resolved, next tasks"

# After working on a task
apm summary create --entity-type=task --entity-id=<id> \
  --summary-type=task_completion \
  --text="What was implemented, tests added, issues encountered"

# After working on an idea
apm summary create --entity-type=idea --entity-id=<id> \
  --summary-type=session \
  --text="Research findings, validation results, next steps"
```

**Summary Types by Entity**:
- **Project**: project_milestone, project_status_report, project_strategic_review
- **Session**: session_handover, session_progress, session_decision_log
- **Work Item**: work_item_progress, work_item_milestone, work_item_decision
- **Task**: task_completion, task_progress, task_technical_notes
- **Idea**: session (legacy support)

**Non-Negotiable**:
- ✅ Create summary BEFORE completing work
- ✅ Include: What was done, decisions made, next steps
- ✅ Keep summaries concise (≤500 words)
- ✅ Use appropriate summary_type for entity

---

### **Rule 2: Document Reference Obligation** (MUST)

**Every agent that creates OR touches a document MUST update document references.**

**When Creating Documents**:
```bash
# After creating any document (.md, .pdf, .yaml, etc.)
apm document add \
  --entity-type=work_item \
  --entity-id=<id> \
  --file-path="docs/architecture/oauth2-design.md" \
  --document-type=design \
  --title="OAuth2 Architecture Design"
```

**When Modifying Documents**:
```bash
# After editing an existing document
apm document update <doc-id> \
  --content-hash=$(sha256sum docs/path/file.md | cut -d' ' -f1)
```

**Document Types**:
- **Requirements**: requirements, user_story, use_case
- **Architecture**: architecture, design, adr
- **Implementation**: specification, api_doc, technical_specification
- **Testing**: test_plan
- **Operations**: runbook, migration_guide
- **Documentation**: user_guide, admin_guide, troubleshooting

**Non-Negotiable**:
- ✅ Add reference IMMEDIATELY after creating file
- ✅ Update hash when modifying file
- ✅ Link to correct entity (work_item, task, idea)
- ✅ Use accurate document_type

---

## 📋 **Enforcement**

### **How to Verify Compliance**

**Before Completing Task**:
```bash
# Check if summary was created
apm summary list --entity-type=task --entity-id=<id>
# Must show at least 1 summary

# Check if document references were added
apm document list --entity-type=work_item --entity-id=<id>
# Must show all created/modified documents
```

**Quality Gates Check These Rules**:
- **R1 Gate** (Review): Validates summaries exist
- **R1 Gate** (Review): Validates document references complete
- **E1 Gate** (Evolution): Requires complete summary for handover

---

## 🎯 **Integration with Agent Workflows**

### **Standard Agent Workflow Template**

```markdown
## Agent Workflow (Standard Pattern)

1. **Receive task assignment**
2. **Load context**: Query database for task/work item/project context
3. **Execute work**: [agent-specific work]
4. **Create summary**: `apm summary create ...` (MANDATORY)
5. **Add document references**: `apm document add ...` (if documents created)
6. **Update task status**: `apm task next <id>`
7. **Return results** to orchestrator
```

### **Examples by Agent Type**

**Generic Agent** (documentation-writer):
```
1. Use Write tool to create docs/user-guides/feature-x.md
2. MUST: apm document add --file-path="docs/user-guides/feature-x.md"
3. MUST: apm summary create --entity-type=task --content="Created user guide for feature X"
```

**Sub-Agent** (code-implementer):
```
1. Implement code changes
2. MUST: apm summary create --entity-type=task --content="Implemented OAuth2 flow, added 3 endpoints, 12 tests"
3. Return: Implementation complete
```

**Mini-Orchestrator** (planning-orch):
```
1. Delegate to: decomposer, estimator, dependency-mapper
2. Collect results
3. MUST: apm summary create --entity-type=work_item --content="Created 8 tasks, mapped 3 dependencies, estimated 32h total"
4. Return: plan.snapshot artifact
```

---

## 🔍 **Validation Checklist**

**Every agent MUST answer YES to**:

- [ ] Did I create a summary for the entity I worked on?
- [ ] Did I add document references for any files I created?
- [ ] Did I update document references for any files I modified?
- [ ] Is my summary type appropriate for the entity?
- [ ] Did I include: what was done, decisions made, next steps?

**If ANY answer is NO**: Work is INCOMPLETE

---

## 🚀 **CLI Command Reference**

### **Summary Commands**
```bash
# Create
apm summary create --entity-type=<type> --entity-id=<id> \
  --summary-type=<type> --content="<text>"

# List
apm summary list --entity-type=<type> --entity-id=<id>

# Show
apm summary show <id>

# Search
apm summary search "<query>"

# Delete (rare)
apm summary delete <id>
```

### **Document Commands**
```bash
# Add
apm document add --entity-type=<type> --entity-id=<id> \
  --file-path="<path>" --document-type=<type>

# List
apm document list --entity-type=<type> --entity-id=<id>

# Show
apm document show <id>

# Update
apm document update <id> --content-hash=<hash>

# Delete
apm document delete <id>
```

---

## 📖 **Rationale**

### **Why Summaries are Mandatory**

1. **Context Continuity**: Next agent/session needs to know what was done
2. **Audit Trail**: Complete history of all work
3. **Learning**: Patterns and decisions captured for reuse
4. **Handover**: Seamless transition between agents/sessions
5. **Analytics**: Track velocity, quality, completion

### **Why Document References are Mandatory**

1. **Traceability**: Know which documents belong to which work
2. **Change Detection**: Content hash tracks modifications
3. **Context Assembly**: Documents included in agent context
4. **Quality Gates**: Verify documentation completeness
5. **Search**: Find relevant documents by entity

---

## ⚠️ **Common Mistakes to Avoid**

**DON'T**:
- ❌ Skip summary because "nothing important happened"
- ❌ Skip document reference because "it's just a small change"
- ❌ Create summary AFTER completing work (do it BEFORE)
- ❌ Use wrong summary_type (check entity type)
- ❌ Forget to update hash when modifying documents

**DO**:
- ✅ Create summary even for failed attempts
- ✅ Reference all documents, no matter how small
- ✅ Create summary as final step before completion
- ✅ Use correct entity_type and summary_type mapping
- ✅ Update hash every time file changes

---

## 🎓 **Integration with Quality Gates**

### **Gate Validation Checks**

**P1 Gate** (Planning → Implementation):
- Checks: Planning summary exists

**I1 Gate** (Implementation → Review):
- Checks: Implementation summary exists
- Checks: All code files have document references

**R1 Gate** (Review → Operations):
- Checks: Review summary exists
- Checks: Test results documented

**O1 Gate** (Operations → Evolution):
- Checks: Deployment summary exists
- Checks: Runbook document referenced

**E1 Gate** (Evolution):
- Checks: Analysis summary with metrics
- Checks: Improvement recommendations documented

---

## 📚 **This Document Must Be**

1. **Included** in every agent SOP (reference or embed)
2. **Enforced** by quality gates (automated validation)
3. **Tested** in every agent workflow (CI/CD)
4. **Updated** when summary/document schemas change

**Location for Agent Reference**:
```markdown
## Universal Rules

Before completing any work, you MUST:
1. Create summary: See docs/agents/UNIVERSAL-AGENT-RULES.md#Rule-1
2. Add document references: See docs/agents/UNIVERSAL-AGENT-RULES.md#Rule-2
```

---

**Status**: APPROVED and READY for integration into all agent definitions
**Next**: Embed these rules in every agent .md file
