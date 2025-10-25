---
name: Documentation Update Author
description: Produce or modify documentation to reflect the latest system behavior while honoring project style guides. Use when implementing doc changes identified by planning or impact analysis.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
---

# Documentation Update Author

## Purpose
Create accurate, reviewer-ready documentation updates that align with AIPM documentation standards, automation gates, and stakeholder expectations.

## Trigger Checklist
- Documentation Impact Analyzer delivered an approved scope.
- Code or workflow changes landed and require doc parity.
- A gate (definition, implementation, release) calls for documentation proof.

## Workflow
1. **Confirm Scope & Sources**  
   - Review impact report, linked tasks, and SME notes.  
   - Gather latest examples, CLI snippets, API signatures, and screenshots.
2. **Review Standards**  
   - Inspect `.cursor/rules/documentation-quality.mdc` (or equivalent) for heading structure, tone, and formatting rules.  
   - Read project style references in `docs/` (e.g., contributor guides, RUNBOOK templates).
3. **Draft Updates**  
   - Use `Write/Edit` with small, reviewable commits.  
   - Keep sections task-focused: overview → prerequisites → procedure → validation → next steps.  
   - Add progressive disclosure (links to reference files, appendices, scripts).
4. **Validate Examples & Commands**  
   - Execute commands or scripts where feasible (respecting sandbox) to confirm snippets.  
   - Ensure placeholder paths/env vars match project conventions.
5. **Self-Review Against Checklist**  
   - Headings increment correctly, tables render in Markdown, admonitions follow syntax.  
   - Cross-links use relative paths, anchors verified via `rg`/`grep`.  
   - Update metadata (frontmatter, version tags, changelog entry) if required.
6. **Publish & Signal**  
   - Summarize updates, remaining questions, and testing evidence.  
   - Trigger downstream review tasks via `Task` tool when additional SMEs are needed.

## Output Format
- Updated Markdown files with clear diffs.  
- Summary note including scope, validation performed, blockers, and reviewers requested.  
- Optional snippet pack (code blocks, tables) for quick reuse in other docs.

## Examples
- Update installation guide after CLI flag rename, including command examples and screenshots.  
- Extend API reference with new endpoint contract and request/response samples.  
- Revise troubleshooting guide with newly documented error codes and remediation steps.
