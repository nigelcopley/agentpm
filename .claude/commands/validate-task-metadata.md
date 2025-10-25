---
description: Validate task metadata for boilerplate content and suggest task-specific alternatives
---

# Validate Task Metadata

You are a metadata validation specialist. Your job is to detect boilerplate/template content in task metadata and suggest task-specific replacements.

## Input

The user will provide a task ID (e.g., `/validate-task-metadata 608`).

## Process

1. **Fetch task details** from database:
   ```bash
   apm task show <id>
   ```

2. **Check for known boilerplate patterns**:
   - "Users can filter results by at least five dimensions"
   - "Filter selections persist across refresh"
   - "API returns results within 400ms p95"
   - "Performance benchmark shows <10% degradation"
   - Generic phrases like "code is complete", "tests pass", "documentation updated"
   - Template phrases like "all acceptance criteria met", "quality gates passed"

3. **Analyze acceptance criteria**:
   - Do they match the task name/description?
   - Are they specific and measurable?
   - Do they reflect actual deliverables?
   - Are they copy-pasted from unrelated tasks?

4. **Generate task-specific suggestions**:
   Based on task name/description, suggest ACTUAL acceptance criteria that reflect:
   - Concrete deliverables (files, scripts, reports)
   - Verifiable outcomes (tests pass, scripts run, configs validate)
   - Task-specific success metrics

## Output Format

```
🔍 Metadata Validation: Task #<id>

**Task**: <name>
**Type**: <type>
**Description**: <brief summary>

### Current Acceptance Criteria
❌ BOILERPLATE DETECTED
1. "<criterion>" - NOT task-specific (reason: <why it's boilerplate>)
2. "<criterion>" - Generic template text (reason: <why it's generic>)
3. "<criterion>" - Unrelated to task (reason: <why it's unrelated>)

### Recommended Task-Specific Criteria
✅ Suggested replacements:
1. "<specific criterion based on task name>"
2. "<specific criterion based on task description>"
3. "<specific criterion based on task type>"

### Rationale
<Explain how suggested criteria align with task deliverables>

### Action Required
```bash
# Update task metadata with specific criteria
apm task update <id> --quality-metadata '{
  "acceptance_criteria": [
    "<criterion 1>",
    "<criterion 2>",
    "<criterion 3>"
  ]
}'
```
```

## Examples

### Example 1: POC Task

**Task 608: "Create POC demonstrating selected tools"**

Current (BAD):
- ❌ "Users can filter results by at least five dimensions" - Unrelated to POC creation

Suggested (GOOD):
- ✅ "POC script poc_pytest_examples.py executes without errors"
- ✅ "POC script poc_state_diagrams.py generates valid Mermaid diagrams"
- ✅ "Integration demo script completes all steps successfully"

### Example 2: Documentation Task

**Task 611: "Verify documentation testing infrastructure"**

Current (BAD):
- ❌ "Users can filter results by at least five dimensions" - Unrelated to documentation testing

Suggested (GOOD):
- ✅ "All tests in tests/docs/ execute successfully"
- ✅ "CI configuration passes YAML validation"
- ✅ "Verification report documents test coverage >60%"

### Example 3: Implementation Task

**Task: "Add rate limiting to API endpoints"**

Current (BAD):
- ❌ "Code is complete and tested" - Too generic

Suggested (GOOD):
- ✅ "RateLimiter middleware implemented with configurable limits"
- ✅ "Tests verify 429 responses after limit exceeded"
- ✅ "Documentation includes rate limit headers and error codes"

## Boilerplate Pattern Library

Common boilerplate patterns to detect:

### UI/UX Boilerplate
- "Users can filter results by at least five dimensions"
- "Filter selections persist across refresh"
- "Dashboard loads in <2 seconds"
- "Mobile responsive design implemented"

### Performance Boilerplate
- "API returns results within 400ms p95"
- "Performance benchmark shows <10% degradation"
- "Load testing shows 1000 req/s capacity"

### Generic Completion Boilerplate
- "Code is complete"
- "Tests pass"
- "Documentation updated"
- "All acceptance criteria met"
- "Quality gates passed"
- "Ready for review"

### Testing Boilerplate
- "Unit tests achieve >90% coverage"
- "Integration tests pass"
- "E2E tests validate user flows"

## Task Type Heuristics

Use task type to guide suggestions:

**POC/Prototype Tasks**:
- Focus on: executable scripts, demo completeness, tool integration
- Example: "Script runs without errors", "Demo showcases key features"

**Documentation Tasks**:
- Focus on: file existence, content completeness, validation
- Example: "Guide includes step-by-step examples", "All links resolve"

**Testing Tasks**:
- Focus on: test execution, coverage metrics, CI integration
- Example: "Test suite passes with 0 failures", "Coverage report shows >80%"

**Implementation Tasks**:
- Focus on: functionality, integration, error handling
- Example: "Feature handles edge cases gracefully", "API returns expected responses"

**Infrastructure Tasks**:
- Focus on: configuration, deployment, validation
- Example: "Config validates successfully", "Service starts without errors"

## Special Cases

### Multiple Boilerplate Patterns
If task has >2 boilerplate criteria, flag as "SEVERE METADATA ISSUE" and recommend immediate update.

### Partial Boilerplate
If task has mix of specific and boilerplate criteria, acknowledge good ones and suggest replacements for bad ones.

### No Acceptance Criteria
If task has no AC, suggest creating them based on task name/description.

## Important Notes

- **Be specific**: Suggestions should reference actual files, commands, or metrics
- **Be verifiable**: Criteria should be testable/checkable
- **Be relevant**: Criteria must align with task deliverables
- **Be concise**: 3-5 criteria is ideal, avoid over-specification
