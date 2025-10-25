# Junie Playbook for APM (Agent Project Manager)

Purpose: This guide translates JetBrains Junie capabilities into concrete, safe, and high‑leverage actions specifically for the agentpm component of this monorepo.

Reference: JetBrains Junie Getting Started
- https://www.jetbrains.com/help/junie/get-started-with-junie.html

Related guidelines in this repo:
- .junie/guidelines.md (project-wide rules and workflow)
- aipm-v2/.junie/guidelines.md (agent development rules for APM (Agent Project Manager))

Important repository policy:
- Do not ever touch teh db directly, always use apm commands. No direct SQLite access under any circumstances.

---

## What Junie can do in agentpm (Quick Wins)

These are safe, minimal, Anti‑Accumulation compliant tasks Junie can run or prepare for you today:

1) Template and Rules Consistency
- Inspect JSON templates under agentpm/templates/json/ for schema drift.
- Cross-check rules/config.json against task templates for missing or unused rule IDs.
- Produce a diff-ready, minimal patch to fix mismatches (rename IDs, add missing required keys, remove stale fields) with clear docstrings in tests.

2) Testing Improvements (no behavior change)
- Add/extend pytest tests in aipm-v2/tests/ to validate template schemas (only if missing), keeping tests fast and deterministic.
- Improve assertion messages to pinpoint exact file/field on failure.

3) Context Detection Planning
- Review existing context templates (contexts/six_w.json, projects/tech_stack.json) and propose a single source of truth structure.
- Draft a minimal Pydantic model proposal (in docs first) for detected frameworks and tech stack to be used by services.

4) Documentation Enhancements
- Add clarifying comments/docstrings where tests or services are unclear.
- Create focused HOWTO docs for recurring developer tasks (e.g., updating a template safely, adding a new rule), linking to this playbook.

5) Guardrail Enforcement
- Identify and remove duplicated or obsolete files that conflict with SSOT (upon maintainer approval).
- Add lightweight checks (in tests) to prevent future drift once the schema test is accepted.

---

## Concrete Junie Workflows (step-by-step)

Workflow A: Template Schema Sanity Pass
- Goal: Ensure all agentpm templates follow a consistent schema.
- Steps:
  1. Use project search to list JSON under:
     - agentpm/templates/json/tasks/
     - agentpm/templates/json/work_items/
     - agentpm/templates/json/session_events/
     - agentpm/templates/json/rules/
  2. Compare required keys across files and note inconsistencies.
  3. Prepare a minimal test plan (pytest) to enforce required keys/types.
  4. Draft a minimal patch (docs and/or tests only at first) that introduces validation without changing runtime behavior.

Workflow B: Rules Config Cross-Reference
- Goal: Align rules/config.json with actual usage within task templates.
- Steps:
  1. Extract all rule IDs referenced in templates.
  2. Verify each appears in rules/config.json with expected metadata.
  3. Propose a minimal patch: either add missing config entries or remove unused rules, favoring deletion of dead rules (Anti‑Accumulation).

Workflow C: Context Model SSOT Proposal
- Goal: Define a single, authoritative schema for detected frameworks/tech stack.
- Steps:
  1. Review contexts/six_w.json and projects/tech_stack.json.
  2. Produce a short Pydantic-style schema proposal in a doc (no code changes yet) that services can adopt.
  3. Plan for a future refactor to align existing templates and services to this SSOT.

---

## Ready-to-use Junie Prompts within this Repo

Use these prompts with Junie to drive targeted, minimal changes:

- "List all JSON templates in agentpm and report any missing required keys (id/title/description/tags/dependencies) with file paths. Propose the smallest patch to fix them without changing behavior."
- "Cross-reference rule IDs used in agentpm/templates/json/tasks/*.json against agentpm/templates/json/rules/config.json and output a table of missing/extra IDs with a minimal, delete-first remediation plan."
- "Draft a pytest file under aipm-v2/tests/templates/ that validates the schema for all task templates and prints precise failure messages. Do not modify runtime code; tests only."
- "Review contexts/six_w.json and projects/tech_stack.json and propose a single Pydantic model (in docs) to serve as SSOT. Provide a migration note describing any field renames."
- "Identify duplicated or obsolete documents in aipm-v2/docs that can be safely deleted or consolidated, referencing SSOT." 

---

## Safety and Compliance Checklist for Junie Actions

Before making any change, ensure:
- Replace, don’t add: Prefer refactoring or removal over adding new artifacts.
- Delete, don’t archive: Do not create _old/_backup folders; rely on git history.
- Consolidate, don’t duplicate: Check for existing docs/tests before adding.
- SSOT: Every field and rule has exactly one authoritative definition.
- No DB access: All database operations must go through approved apm commands (but for this playbook, prefer docs/tests-only changes).
- Tests first: Any code changes must include pytest tests; for doc-only changes, plan the tests in the next PR.

---

## Where to Put Changes

- Documentation: aipm-v2/docs/ (this playbook is an example)
- Tests: aipm-v2/tests/
- Templates/Rules: agentpm/templates/json/
- Agent Guidelines: aipm-v2/.junie/guidelines.md

Avoid scattering similar content across multiple locations—link to SSOT documents.

---

## Next Actions (suggested sequence)

1) Run a non-invasive audit:
   - Identify schema drift in templates and rule ID mismatches.
   - Report findings in a short doc under aipm-v2/docs/ (no code changes yet).
2) Add a single pytest file for schema validation in aipm-v2/tests/ (in a follow-up PR).
3) Apply the smallest possible patch to fix any mismatches in templates/rules.
4) Propose the SSOT Pydantic model for context data and plan consolidation.

---

## What can be removed or consolidated?

To honor Anti‑Accumulation, please indicate if we should remove or merge any of the following if this playbook supersedes them:
- Overlapping guidance in other aipm-v2/docs/* strategy documents
- Redundant rule descriptions spread across multiple files
- Any obsolete templates under agentpm/templates/json/ no longer referenced by tests or services

Reply with the files you approve for deletion, and Junie will prepare a minimal, safe cleanup patch.


---

## Related existing tests (do not duplicate)

When extending validation, prefer adding to or refining these existing tests instead of creating new files:
- aipm-v2/tests/templates/test_json_templates.py
- aipm-v2/tests/core/agents/test_workflow_enforcement.py
- aipm-v2/tests/cli/test_template_commands.py

These already cover template structure, workflow enforcement, and CLI template listing; add focused assertions there to keep a single source of truth.

## Running tests for agentpm only

To avoid failures from unrelated modules (e.g., root Makefile targets that reference a missing aipm-cli), run tests within the aipm-v2 module:
- cd aipm-v2 && pytest -q
- Optionally run a single file or test for faster iteration, for example:
  - cd aipm-v2 && pytest -q tests/templates/test_json_templates.py

Note: The top-level Makefile includes targets for aipm-cli that may fail until the CLI is restored or guarded. Prefer invoking pytest directly inside aipm-v2 for now.
