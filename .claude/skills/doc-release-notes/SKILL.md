---
name: Release Notes Curator
description: Assemble clear, audience-targeted release notes from the latest changes, highlighting features, fixes, risks, and doc links. Use during sprint reviews, pre-release windows, or whenever stakeholders need a change digest.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
---

# Release Notes Curator

## Purpose
Transform raw change artifacts (commits, merged tasks, doc updates) into concise release notes that product, engineering, and go-to-market teams can consume.

## Trigger Checklist
- Release cadence (weekly/monthly) approaching.  
- Implementation orchestrator requests stakeholder summary.  
- Support or customer success needs highlight reels for enablement.

## Workflow
1. **Gather Signals**  
   - Aggregate merged PRs, work items, and doc changes for the release span.  
   - Pull context from changelog entries, `docs/` updates, and AIPM work item metadata.
2. **Categorize Content**  
   - Group items into Features, Improvements, Fixes, Documentation, Ops/Infra, Known Issues.  
   - Identify user impact level (high, medium, low) and any adoption prerequisites.
3. **Draft Narrative**  
   - Lead with top customer-visible changes.  
   - Provide summary sentences plus optional deep links to detailed docs, runbooks, or tickets.  
   - Note rollout/enablement steps, flags, or migration guides.
4. **Compliance Checks**  
   - Ensure terminology aligns with branding and doc style guidelines.  
   - Confirm sensitive or internal-only information is handled per comms policy.  
   - Verify referenced documents exist and are current.
5. **Finalize & Tasking**  
   - Deliver Markdown-friendly release note section and, if needed, short-form copy for status updates.  
   - Create follow-up Tasks for missing screenshots, marketing blurbs, or customer communications.

## Output Format
- Markdown release note draft with dated header and categorized bullet lists.  
- Table of key changes (Column: Category, Summary, Impact, Link).  
- Optional TL;DR + callouts for adoption risks or required migrations.

## Examples
- Sprint release including new automation, bug fixes, and doc updates referencing guides.  
- Hotfix announcement summarizing incident resolution steps and updated runbooks.  
- Major release note bundling product features with links to onboarding tutorials and API reference sections.
