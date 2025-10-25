# Idea 48 Research – Structured Idea Breakdown

**Agent:** Market Research Analyst / Technical Analyst

## Evidence Gathered
1. Atlassian Jira Product Discovery – structured fields (Problem, Impact, Confidence) and seamless conversion to Jira Software epics.
2. Linear – problem/solution templates, roadmap workflow, conversion into projects/sprints.
3. Azure DevOps – process templates requiring fields before state changes, backlog promotion.
4. ClickUp / Aha! – idea portals with scorecards, custom forms, automatic conversion with history.

## Competitive Landscape Highlights
- Leading PPM tools collect structured data per ideation stage.
- Enforce gating by requiring fields before state transitions.
- Maintain traceability when ideas become execution artifacts.

## Feasibility Insights
- JSON column for structured parts is compatible with our schema.
- CLI prompts/templates align with existing AIPM patterns.
- Need to handle migrations carefully for legacy ideas.

## Open Questions
- Where to store longer artefacts (repo docs vs `.aipm/context`).
- How to display structured parts in UI/CLI without burnout.
- Versioning strategy for parts updated after acceptance.

