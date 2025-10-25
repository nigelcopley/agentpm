# Idea 48 Design – Structured Idea Breakdown

**Agent:** Solution Architect / Ops Engineer / QA Designer

## How will it be implemented?
1. **Schema & Migration**: Add a `parts` JSON column to `ideas`; write migration to backfill legacy ideas with empty structures.
2. **Model & Adapter Updates**: Extend `Idea` Pydantic model, adapter, and CRUD methods to read/write structured parts.
3. **CLI Experience**: Introduce commands (`apm idea add-part`, `apm idea show --parts`, etc.) with prompts for each question (what/why/who/how/impacts/when).
4. **Lifecycle Enforcement**: Validate that transitions (idea→research→design→proposal→accepted) require corresponding parts to be filled.
5. **Conversion Pipeline**: Map idea parts to work item metadata, auto-create tasks from `design.proposed_tasks`, attach all doc references.
6. **Documentation & QA**: Provide usage docs, update tests to cover structured parts + conversion.

## What else will it impact?
- Idea model serialization, CLI commands, and conversion pipeline.
- Migration tooling must handle pre-existing ideas gracefully.
- Workflow validators and UI need to display structured parts.

## Proposed Tasks (post-conversion)
1. Design idea parts schema & migration (`design`).
2. Implement idea part CLI commands (`implementation`).
3. Enhance idea→work-item conversion pipeline (`implementation`).
4. QA end-to-end conversion & update documentation (`testing`).

## Unknowns / Risks
- Balancing detail vs usability in CLI/UX.
- Agent assignment visibility (should we surface per part?).
- Ensuring conversion remains idempotent and traceable.

## References
- docs/ideas/idea-48/discovery.md
- docs/ideas/idea-48/research.md
- docs/ideas/idea-48/proposal.md

