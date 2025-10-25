---
name: Documentation Quality Reviewer
description: Verify completed documentation updates for accuracy, style compliance, and gate readiness. Use when docs need QA before merge, release, or hand-off.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
---

# Documentation Quality Reviewer

## Purpose
Provide a structured quality check on documentation deliverables, ensuring they satisfy project gates, style expectations, and stakeholder acceptance criteria.

## Trigger Checklist
- Documentation changes are code-complete and awaiting review.
- Release or implementation gate requires documentation validation evidence.
- Support/Enablement teams request confirmation that guidance is accurate.

## Workflow
1. **Context Sync**  
   - Read associated impact report, PR, or change summary.  
   - Identify intended audience (internal, customer, ops) to tailor the review focus.
2. **Structural Validation**  
   - Ensure headings follow hierarchy, TOC renders logically, and sections map to reader journey.  
   - Check that admonitions, tables, diagrams, and callouts conform to Markdown syntax accepted by the publishing pipeline.
3. **Content Accuracy**  
   - Trace claims back to source code, API definitions, or CLI behavior.  
   - Spot-check commands or configuration snippets; flag any that cannot be verified.
4. **Style & Clarity**  
   - Compare tone, voice, and terminology against style guides (e.g., `documentation-quality.mdc`, internal doc standards).  
   - Highlight ambiguous instructions, missing prerequisites, or leaps in logic.
5. **Compliance & Metadata**  
   - Confirm changelog entries, version tags, and cross-links were updated.  
   - Verify references to gated assets (runbooks, diagrams) and ensure they exist.
6. **Feedback & Tasking**  
   - Provide actionable comments (what/why/where) with proposed fixes.  
   - Use `Task` tool for follow-up actions that exceed the reviewer’s scope.

## Output Format
- Review report summarizing pass/fail status, key findings, and confidence level.  
- Inline or section-referenced comments pointing to exact file locations.  
- Optional checklist completion (structure, accuracy, style, metadata).  
- Recommendation: approve, approve with edits, or request rework.

## Examples
- Pre-release audit of API reference to certify request/response fields.  
- QA review of onboarding tutorial to ensure new workflow steps are complete.  
- Validation of incident runbook revisions before on-call rotation changeover.
