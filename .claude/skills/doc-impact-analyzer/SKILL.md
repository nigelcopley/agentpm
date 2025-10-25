---
name: Documentation Impact Analyzer
description: Identify which documentation assets must change for a given feature, bugfix, or migration. Use when you need a scoped list of docs to update before starting documentation work or during post-implementation validation.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
---

# Documentation Impact Analyzer

## Purpose
Build a precise map of documentation surfaces affected by incoming code, configuration, or workflow changes so downstream doc work is planned, time-boxed, and aligned with project rules.

## Trigger Checklist
- New feature, migration, or policy change reached READY/ACTIVE.
- Code review surfaced doc drift risks.
- A release checklist or gate requires documentation confirmation.

## Workflow
1. **Collect Inputs**  
   - Read linked specs, work items, commit summaries, and test updates.  
   - Use `Read/Grep/Glob` to pull current doc snippets under `docs/`, `README.md`, `CHANGELOG.md`, runbooks, and knowledge-base folders.
2. **Classify Documentation Surfaces**  
   - Tag each impacted asset as reference, tutorial, how-to, release-notes, ops/runbook, or API.  
   - Note whether the change is an update, new document, retirement, or cross-link.
3. **Assess Gate & Rule Dependencies**  
   - Check for applicable rules such as `.cursor/rules/documentation-quality.mdc` or team-specific quality gates.  
   - Flag requirements for diagrams, screenshots, or versioned samples.
4. **Scope Work & Time Boxes**  
   - Estimate doc effort in hours using project limits (≤4h documentation tasks).  
   - Suggest follow-up Tasks using `Task` tool for each discrete deliverable.
5. **Surface Risks & Stakeholders**  
   - Identify SMEs, reviewers, and dependent teams.  
   - Record risks (e.g., missing product screenshots, pending API contracts).

## Output Format
- Summary paragraph covering change context.  
- Table with columns: `Path/Asset`, `Doc Type`, `Required Action`, `Owner/Reviewer`, `Notes`.  
- Recommended Tasks (bulleted or as `Task` invocations) with proposed time boxes.  
- Open questions or blockers (if any).

## Examples
- Feature launch touching API and UI surfaces → list reference docs, tutorial updates, release notes entry, support KB sync.  
- Database migration → flag runbooks, on-call playbooks, and architecture diagrams needing revision.  
- Policy change → capture handbook pages, compliance docs, and onboarding materials requiring edits.
