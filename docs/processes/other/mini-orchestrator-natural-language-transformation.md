# Mini-Orchestrator Natural Language Transformation

**Date**: 2025-10-17
**Objective**: Convert structured `delegate ->` syntax to natural language Task tool invocation
**Files to Create**: 6 mini-orchestrator files in `.claude/agents/orchestrators/`

---

## Transformation Pattern

### FROM (Current - Structured Syntax):
```markdown
delegate -> intent-triage
input: {request: "raw user request"}
expect: {work_type, domain, complexity, priority}
```

### TO (Natural Language + Task Tool):
```markdown
Use the **intent-triage** subagent to classify this request.

Invoke the Task tool with:
- **subagent_type**: "intent-triage"
- **description**: "Classify user request for phase routing"
- **prompt**: """
  Analyze this request and determine:
  - Work type (feature, bugfix, research, refactoring, etc.)
  - Domain (backend, frontend, infrastructure, database)
  - Complexity score (0.0-1.0)
  - Recommended priority

  Request: [paste user request]
  Project context: [paste tech stack and rules]
  """

The subagent will return structured classification as YAML.
```

---

## Files to Create

| File | Phase | Gate | Sub-Agents |
|------|-------|------|------------|
| `definition-orch.md` | D1 Discovery | why_value + AC≥3 + risks | 7 agents |
| `planning-orch.md` | P1 Planning | steps↔AC + estimates + deps | 6 agents |
| `implementation-orch.md` | I1 Implementation | tests + docs + migrations | 6 agents |
| `review-test-orch.md` | R1 Review | AC pass + tests green + security | 5 agents |
| `release-ops-orch.md` | O1 Operations | version + changelog + rollback | 6 agents |
| `evolution-orch.md` | E1 Evolution | metrics + outcomes + priority | 6 agents |

---

## Transformation Rules

### 1. Delegation Language
- **Replace**: "delegate ->" with "Use the **[agent-name]** subagent to [action]"
- **Add**: "Invoke the Task tool with:" (explicit tool invocation)
- **Specify**: subagent_type, description, and detailed prompt

### 2. Input Specification
- **Replace**: `input: {field1, field2}` with detailed prompt instructions
- **Add**: Context requirements (paste project context, rules, etc.)
- **Format**: Multi-line string with clear instructions

### 3. Output Expectation
- **Replace**: `expect: {output1, output2}` with "The subagent will return [format]"
- **Specify**: Output format (YAML, JSON, structured text)
- **Add**: What to do with the output (store, validate, pass to next agent)

### 4. Control Flow
- **Add**: Explicit "If PASS:" and "If FAIL:" branches
- **Specify**: What happens on success vs failure
- **Include**: Escalation paths and retry logic

### 5. Quality Gates
- **Add**: Explicit gate validation steps
- **Specify**: Pass/fail criteria with checklist format
- **Include**: What to do if gate fails (retry, escalate, enrich context)

---

## Example Transformation

### Original (from script):
```markdown
## Delegation Pattern
```
request.raw → intent-triage → context-assembler → problem-framer
  ↓
value-articulator + ac-writer + risk-notary (parallel)
  ↓
definition.gate-check (D1 validation)
  ↓
workitem.ready (next phase)
```
```

### Transformed:
```markdown
## Delegation Pattern

### Step 1: Intent Triage
Use the **intent-triage** subagent to classify the incoming request.

Invoke the Task tool:
```
Task(
  subagent_type="intent-triage",
  description="Classify user request for phase routing",
  prompt="""
  Analyze this request and determine:
  - Work type (feature, bugfix, research, refactoring, etc.)
  - Domain (backend, frontend, infrastructure, database)
  - Complexity score (0.0-1.0)
  - Recommended priority

  Request: [paste user request]
  Project context: [paste tech stack from database]
  """
)
```

The subagent will return:
```yaml
work_type: "feature"
domain: "backend"
complexity: 0.7
priority: "high"
confidence: 0.85
```

### Step 2: Context Assembly
Use the **context-assembler** subagent to gather relevant project context.

Invoke the Task tool:
```
Task(
  subagent_type="context-assembler",
  description="Gather project context for requirements definition",
  prompt="""
  Assemble context for this request:
  - Project rules (from database)
  - Relevant codebase areas (from intent classification)
  - Similar past work items (from history)
  - Framework patterns (from plugins)

  Work type: [from step 1]
  Domain: [from step 1]
  """
)
```

The subagent will return structured context (paths, rules, patterns).

### Step 3: Problem Framing
Use the **problem-framer** subagent to frame the problem with constraints.

[Continue pattern...]

### Step 6: Gate Validation
Use the **definition-gate-check** subagent to validate D1 criteria.

Invoke the Task tool:
```
Task(
  subagent_type="definition-gate-check",
  description="Validate Definition phase completion (D1)",
  prompt="""
  Validate that all D1 criteria are met:
  ✅ why_value present (business + user value)
  ✅ AC count ≥ 3
  ✅ risks identified (with mitigation strategies)
  ✅ problem framed (with constraints)

  Work item ID: [from database]
  """
)
```

The subagent will return:
```yaml
gate: D1
status: PASS | FAIL
missing_criteria: []  # or list of failures
confidence: 0.90
```

**If PASS**: Proceed to PlanningOrch with `workitem.ready` artifact
**If FAIL**: Enrich context via DiscoveryOrch, then retry validation
```

---

## Structure for Each Orchestrator File

```markdown
# [Phase] Orchestrator

**Phase**: [Phase name]
**Gate**: [Gate ID] ([criteria])
**Artifact In**: [incoming artifact]
**Artifact Out**: [outgoing artifact]

---

## Purpose
[Phase-specific purpose from script description]

---

## Responsibilities
1. [List from script]
2. ...

---

## Delegation Pattern

### Step 0: Context Assembly (MANDATORY)
[Context delivery agent invocation]

### Step 1: [First Sub-Agent]
[Natural language + Task tool invocation]

### Step 2: [Second Sub-Agent]
[Natural language + Task tool invocation]

...

### Step N: Gate Validation
[Gate-check agent invocation with criteria]

---

## Quality Gate: [Gate ID]
- ✅ [Criterion 1]
- ✅ [Criterion 2]
- ...

**Pass Behavior**: [What happens on gate pass]
**Fail Behavior**: [What happens on gate fail]

---

## Tools
- **[tool-name]**: [Usage description]
- ...

---

## Escalation
[From script - when to escalate, retry logic]

---

## Prohibited Actions
- ❌ [Action 1 - from phase constraints]
- ❌ [Action 2]
- ❌ [Action 3]

---

## Example Flow
[Concrete example with sample inputs/outputs]
```

---

## Implementation Plan

1. **Create directory**: `.claude/agents/orchestrators/`
2. **Create 6 files**: One per orchestrator
3. **Apply transformation**: For each sub-agent delegation
4. **Add examples**: Concrete input/output samples
5. **Validate**: Check all sub-agents referenced exist

---

## Sub-Agent Count by Orchestrator

1. **Definition-Orch**: 7 sub-agents
   - intent-triage
   - context-assembler
   - problem-framer
   - value-articulator
   - ac-writer
   - risk-notary
   - definition-gate-check

2. **Planning-Orch**: 6 sub-agents
   - decomposer
   - estimator
   - dependency-mapper
   - mitigation-planner
   - backlog-curator
   - planning-gate-check

3. **Implementation-Orch**: 6 sub-agents
   - pattern-applier
   - code-implementer
   - test-implementer
   - migration-author
   - doc-toucher
   - implementation-gate-check

4. **Review-Test-Orch**: 5 sub-agents
   - static-analyzer
   - test-runner
   - threat-screener
   - ac-verifier
   - quality-gatekeeper

5. **Release-Ops-Orch**: 6 sub-agents
   - versioner
   - changelog-curator
   - deploy-orchestrator
   - health-verifier
   - operability-gatecheck
   - incident-scribe

6. **Evolution-Orch**: 6 sub-agents
   - signal-harvester
   - insight-synthesizer
   - debt-registrar
   - refactor-proposer
   - sunset-planner
   - evolution-gate-check

**Total**: 36 sub-agent delegations to transform

---

## Success Criteria

- ✅ All 6 orchestrator files created
- ✅ All 36 sub-agent delegations use natural language
- ✅ All delegations use Task tool invocation syntax
- ✅ All gate validations have explicit pass/fail logic
- ✅ All files include concrete examples
- ✅ All prohibited actions listed
- ✅ All escalation paths defined

---

**Status**: Ready for implementation
**Next**: Create orchestrator files with transformed delegation
