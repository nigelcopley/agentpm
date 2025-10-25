# Universal Agent Rules - Quick Reference

**For**: All APM (Agent Project Manager) Agents
**Status**: MANDATORY - No Exceptions
**Enforcement**: R1 Gate (Blocking)

---

## 🚨 Before Completing ANY Work

### ✅ Required Actions

1. **Create Summary**
2. **Add Document References** (if you created/modified files)
3. **Validate Checklist**

**If ANY action skipped**: Work is INCOMPLETE and will be BLOCKED at R1 gate.

---

## 📝 Rule 1: Summary Creation

### When to Create
- **After** completing work on ANY entity
- **Before** marking task/work item complete
- **Every time** you do meaningful work

### Command Template
```bash
apm summary create \
  --entity-type=<TYPE> \
  --entity-id=<ID> \
  --summary-type=<SUMMARY_TYPE> \
  --content="<CONTENT>"
```

### Quick Reference Table

| Entity Type | Summary Type | Example Content |
|-------------|--------------|-----------------|
| **work_item** | work_item_progress | "Created 8 tasks, mapped dependencies, estimated 32h total" |
| **work_item** | work_item_milestone | "D1 gate passed, ready for planning phase" |
| **work_item** | work_item_decision | "Decided on PostgreSQL for JSONB support" |
| **task** | task_completion | "Implemented OAuth2 flow, added 12 tests, all passing" |
| **task** | task_progress | "50% complete, API integration done, UI pending" |
| **task** | task_technical_notes | "Used AsyncIO pattern from arch/patterns.md" |
| **project** | project_status_report | "Phase 2 complete, 85% test coverage, on schedule" |
| **project** | session_progress | "Fixed 3 blockers, advanced 2 work items to planning" |
| **session** | session_handover | "Paused at code review, next: address reviewer feedback" |

### Content Guidelines
- **Include**: What was done, decisions made, next steps
- **Length**: ≤500 words (be concise)
- **Style**: Clear, factual, actionable
- **Avoid**: Vague statements, speculation, unnecessary details

---

## 📄 Rule 2: Document References

### When to Add References

**Creating Documents**:
```bash
apm document add \
  --entity-type=<work_item|task> \
  --entity-id=<ID> \
  --file-path="<PATH>" \
  --document-type=<TYPE> \
  --title="<TITLE>"
```

**Modifying Documents**:
```bash
apm document update <DOC_ID> \
  --content-hash=$(sha256sum <PATH> | cut -d' ' -f1)
```

### Document Types Reference

| Category | Document Types | Examples |
|----------|----------------|----------|
| **Requirements** | requirements, user_story, use_case | PRD, user stories, use cases |
| **Architecture** | architecture, design, adr | Architecture docs, ADRs, design specs |
| **Implementation** | specification, api_doc, technical_specification | API docs, technical specs |
| **Testing** | test_plan | Test plans, test strategies |
| **Operations** | runbook, migration_guide | Runbooks, deployment guides |
| **Documentation** | user_guide, admin_guide, troubleshooting | User docs, admin guides |

### What Qualifies as a Document
- ✅ .md files (markdown docs)
- ✅ .yaml/.json files (config, specs)
- ✅ .txt files (notes, plans)
- ✅ Design diagrams (.drawio, .png with annotations)
- ✅ Architecture decision records
- ❌ Code files (.py, .js) - tracked differently
- ❌ Test files - tracked differently
- ❌ Temporary files

---

## ✅ Validation Checklist

### Before Marking Work Complete

```markdown
- [ ] Summary created for entity I worked on
- [ ] Summary type matches entity type
- [ ] Summary includes: what was done, decisions made, next steps
- [ ] Document references added for ALL files I created
- [ ] Document references updated for ALL files I modified
- [ ] Content hashes updated for modified documents
- [ ] All references link to correct entity (work_item or task)
```

**If ANY checkbox is unchecked**: Work is NOT complete.

---

## 🎯 Common Scenarios

### Scenario 1: Created Architecture Document
```bash
# 1. Create the document (using Write tool)
# 2. Add reference
apm document add \
  --entity-type=work_item \
  --entity-id=123 \
  --file-path="docs/architecture/oauth2-design.md" \
  --document-type=design \
  --title="OAuth2 Authentication Design"

# 3. Create summary
apm summary create \
  --entity-type=work_item \
  --entity-id=123 \
  --summary-type=work_item_progress \
  --content="Created OAuth2 design doc covering flow, security, error handling"
```

### Scenario 2: Implemented Code (No Documents)
```bash
# 1. Implement code (using Edit/Write tools)
# 2. Create summary (no document references needed for code)
apm summary create \
  --entity-type=task \
  --entity-id=456 \
  --summary-type=task_completion \
  --content="Implemented OAuth2 service, added 12 tests, integrated with user model"
```

### Scenario 3: Modified Existing Document
```bash
# 1. Modify document (using Edit tool)
# 2. Get document ID
apm document list --entity-type=work_item --entity-id=123

# 3. Update reference with new hash
apm document update 789 \
  --content-hash=$(sha256sum docs/architecture/oauth2-design.md | cut -d' ' -f1)

# 4. Create summary
apm summary create \
  --entity-type=work_item \
  --entity-id=123 \
  --summary-type=work_item_progress \
  --content="Updated OAuth2 design with token refresh flow and error scenarios"
```

### Scenario 4: Research Phase (Multiple Documents)
```bash
# 1. Create research findings document
# 2. Add reference
apm document add \
  --entity-type=work_item \
  --entity-id=123 \
  --file-path="docs/research/oauth2-providers-analysis.md" \
  --document-type=requirements \
  --title="OAuth2 Provider Comparison"

# 3. Create summary with findings
apm summary create \
  --entity-type=work_item \
  --entity-id=123 \
  --summary-type=work_item_progress \
  --content="Analyzed 5 OAuth2 providers, recommend Google/GitHub for MVP, Auth0 for enterprise"
```

---

## 🚫 Common Mistakes

### ❌ DON'T
- Skip summary because "nothing important happened"
- Skip document reference because "it's just a small change"
- Create summary AFTER marking work complete
- Use wrong summary_type for entity
- Forget to update hash when modifying documents
- Leave summary content vague or incomplete

### ✅ DO
- Create summary even for failed attempts (capture learnings)
- Reference all documents, no matter how small
- Create summary as FINAL step BEFORE completion
- Match summary_type to entity_type
- Update hash EVERY time file changes
- Include specific accomplishments and next steps

---

## 🔍 Verification Commands

### Check Summary Exists
```bash
# For work item
apm summary list --entity-type=work_item --entity-id=123

# For task
apm summary list --entity-type=task --entity-id=456

# Should show at least 1 summary
```

### Check Document References
```bash
# For work item
apm document list --entity-type=work_item --entity-id=123

# For task
apm document list --entity-type=task --entity-id=456

# Should show all created/modified documents
```

### View Summary Details
```bash
apm summary show <SUMMARY_ID>
```

### View Document Details
```bash
apm document show <DOC_ID>
```

---

## 🛡️ Enforcement

### R1 Gate Validation
**Before work can advance from REVIEW phase**:

1. ✅ Summary exists for entity
2. ✅ Summary type matches entity type
3. ✅ Summary content includes required elements
4. ✅ Document references complete for all created files
5. ✅ Document references updated for all modified files

**If ANY validation fails**: Work is BLOCKED.

### Gate Response
```
❌ R1 Gate FAILED

Missing Requirements:
- Summary not found for task 456
- Document reference missing for: docs/design/feature-x.md
- Summary content missing 'next steps' section

Action Required: Complete Universal Rules obligations before resubmitting
```

---

## 📚 Complete Documentation

**Full Details**: `docs/agents/UNIVERSAL-AGENT-RULES.md`
**Update Report**: `docs/agents/AGENT-UNIVERSAL-RULES-UPDATE-REPORT.md`
**Summary System**: `docs/components/summaries/summary-contract-specification.md`
**Document System**: `docs/components/document/README.md`

---

## 🆘 Need Help?

### Questions
1. Check complete documentation (see above)
2. Review example scenarios in this guide
3. Look at other agent implementations
4. Verify gate requirements in workflow docs

### Issues
1. Summary creation failing → Check entity_type and entity_id are valid
2. Document add failing → Verify file_path exists and is correct
3. Validation failing → Use verification commands to debug
4. Gate blocking → Check all checklist items completed

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Status**: MANDATORY FOR ALL AGENTS
**Next Review**: As needed
