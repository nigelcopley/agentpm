---
name: Knowledge Base Synchronizer
description: Sync product and operational knowledge across documentation, runbooks, and context packages. Use after significant changes when internal/external knowledge sources must stay aligned.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Task
---

# Knowledge Base Synchronizer

## Purpose
Keep knowledge artifacts coherent by propagating key updates across guides, FAQs, runbooks, and context bundles used by agents and humans.

## Trigger Checklist
- Major feature or policy shipped with multi-surface documentation.  
- Incident or RCA generated new operational insights.  
- Stakeholders report conflicting guidance between docs, playbooks, and knowledge packs.

## Workflow
1. **Inventory Sources & Targets**  
   - Enumerate authoritative docs (reference guides, tutorials, runbooks, release notes, ACs).  
   - Identify downstream consumers: knowledge packs, onboarding decks, support macros.
2. **Extract Canonical Facts**  
   - Pull critical updates (behaviors, limits, toggles, mitigations) from primary sources.  
   - Validate against implementation evidence (code, config, monitoring dashboards).
3. **Propagate Updates**  
   - Edit or file tasks for each target asset, ensuring phrasing and examples remain consistent.  
   - Update metadata (version tags, last-reviewed timestamps, ownership) where applicable.
4. **Coordinate With Agents & Processes**  
   - Notify relevant specialist agents (doc-toucher, technical-writer, context-delivery) via `Task` to perform deep edits if required.  
   - Ensure context bundles referenced by orchestration workflows include the refreshed docs.
5. **Verification & Audit Trail**  
   - Produce summary of updated assets, outstanding items, and review owners.  
   - Link to changelog entries or evidence logs for traceability.

## Output Format
- Synchronization log listing each asset touched, action taken, and next reviewer.  
- Optional dependency graph highlighting upstream/downstream relationships.  
   - Example columns: `Source`, `Dependent Asset`, `Status`, `Notes`.

## Examples
- Align product docs, support KB, and sales playbook after a pricing change.  
- Propagate incident learnings into on-call runbooks, FAQ entries, and monitoring guides.  
- Sync internal architecture reference with public developer documentation following API deprecation.
