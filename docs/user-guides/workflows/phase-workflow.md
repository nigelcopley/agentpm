# Phase Workflow

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](cli-reference/commands.md) | [Next →](workflows/ideas-workflow.md)

**Complete Phase-Based Development Lifecycle** | Version 2.0 | Real Examples from fullstack-ecommerce

APM uses a **6-phase workflow** to structure development work from discovery through evolution. This guide walks through each phase with real examples.

---

## Table of Contents

1. [Phase Overview](#phase-overview)
2. [Phase Lifecycle](#phase-lifecycle)
3. [D1: Discovery Phase](#d1-discovery-phase)
4. [P1: Planning Phase](#p1-planning-phase)
5. [I1: Implementation Phase](#i1-implementation-phase)
6. [R1: Review Phase](#r1-review-phase)
7. [O1: Operations Phase](#o1-operations-phase)
8. [E1: Evolution Phase](#e1-evolution-phase)
9. [Phase Commands Reference](#phase-commands-reference)
10. [Common Workflows](#common-workflows)

---

## Phase Overview

### Integration with Ideas

Work items can originate from ideas through a seamless conversion process:

```
Ideas (Exploration) → Work Items (Execution)
     ↓                        ↓
idea → research → design → accepted → converted → D1 → P1 → I1 → R1 → O1 → E1
```

**Phase Alignment**:
- Idea `research` → Work Item `D1_DISCOVERY`
- Idea `design` → Work Item `P1_PLAN`  
- Idea `accepted` → Work Item `P1_PLAN` (ready for implementation)

**Benefits**:
- ✅ **Smooth transition** from exploration to execution
- ✅ **No duplication** of research/design work
- ✅ **Full traceability** from brainstorm to delivery
- ✅ **Context preservation** - idea metadata carried forward

### The 6-Phase Model

```
D1 → P1 → I1 → R1 → O1 → E1
 ↓     ↓     ↓     ↓     ↓     ↓
Discovery → Planning → Implementation → Review → Operations → Evolution
```

| Phase | Code | Name | Purpose | Duration |
|-------|------|------|---------|----------|
| **D1** | `d1_discovery` | Discovery | Define needs, validate market fit | 1-2 weeks |
| **P1** | `p1_plan` | Planning | Create detailed plans, estimates | 1 week |
| **I1** | `i1_implementation` | Implementation | Build the solution | 2-4 weeks |
| **R1** | `r1_review` | Review | Test, validate quality | 1-2 weeks |
| **O1** | `o1_operations` | Operations | Deploy and monitor | 1 week |
| **E1** | `e1_evolution` | Evolution | Learn, adapt, improve | Ongoing |

### Why Phases?

**Benefits**:
✅ **Structured Progress**: Clear milestones and checkpoints
✅ **Quality Gates**: Ensure completeness before advancing
✅ **Risk Management**: Catch issues early in the lifecycle
✅ **Visibility**: Stakeholders understand current progress
✅ **Predictability**: Consistent workflow across all work items

**Key Principles**:
1. **Sequential**: Phases must be completed in order
2. **Gated**: Each phase has entry/exit criteria
3. **Validated**: Quality checks before advancing
4. **Traceable**: Full audit trail of phase progression

---

## Phase Lifecycle

### State Diagram

```
┌─────────┐
│  NULL   │ Initial state (not started)
└────┬────┘
     │ phase-advance
     ↓
┌─────────────┐
│ D1_DISCOVERY│ Define needs, validate fit
└─────┬───────┘
      │ phase-advance (validated)
      ↓
┌──────────┐
│  P1_PLAN │ Create detailed plans
└─────┬────┘
      │ phase-advance (validated)
      ↓
┌─────────────────────┐
│ I1_IMPLEMENTATION   │ Build the solution
└─────┬───────────────┘
      │ phase-advance (validated)
      ↓
┌───────────┐
│ R1_REVIEW │ Test and validate
└─────┬─────┘
      │ phase-advance (validated)
      ↓
┌────────────────┐
│ O1_OPERATIONS  │ Deploy and monitor
└─────┬──────────┘
      │ phase-advance (validated)
      ↓
┌───────────────┐
│ E1_EVOLUTION  │ Learn and improve
└───────────────┘
```

### Phase Commands

```bash
# Check current phase status
apm work-item phase-status <id>

# Validate ready to advance
apm work-item phase-validate <id>

# Advance to next phase
apm work-item phase-advance <id>
```

---

## D1: Discovery Phase

### Purpose

**Define user needs, validate market fit, gather requirements, assess technical feasibility**

**Key Questions**:
- Who are the users?
- What problem are we solving?
- Why is this valuable?
- Is this technically feasible?
- What are the risks?

### Typical Activities

Create tasks as needed to achieve D1 phase goals. Common task types for this phase:

- `analysis` - Analyze problem space and requirements
- `research` - Research technical approaches and solutions
- `design` - Initial system design and architecture

**Note**: Phase gates validate outcomes (requirements clear? risks identified?), not task types.

### Entry Criteria

✅ Work item created with basic description
✅ Business context defined (6W framework)
✅ Priority assigned

### Exit Criteria

✅ Requirements clearly defined
✅ Business value articulated
✅ Technical feasibility validated
✅ Risks identified and assessed
✅ Acceptance criteria drafted

### Real Example

**Work Item**: Product Catalog API (ID: 1)

**Starting State**:
```bash
apm work-item phase-status 1
```

**Output**:
```
Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL (not started)
Next Phase: D1_DISCOVERY

Phase Sequence for FEATURE:
  D1_DISCOVERY (future)
  P1_PLAN (future)
  I1_IMPLEMENTATION (future)
  R1_REVIEW (future)
  O1_OPERATIONS (future)
  E1_EVOLUTION (future)

Next Phase (D1_DISCOVERY) Requirements:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Available Actions:
  apm work-item phase-validate 1  # Check if ready to advance
  apm work-item phase-advance 1   # Advance to next phase
```

**Advancing to D1**:
```bash
apm work-item phase-advance 1
```

**Output**:
```
Advancing Work Item #1: Product Catalog API
Current Phase: NULL
Current Status: draft

Advancing: NULL → D1_DISCOVERY

Validating phase gate requirements...
✅ Phase gate validation PASSED

✅ Phase advanced successfully

Phase: NULL → D1_DISCOVERY
Status: draft → draft

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Typical activities:
  • Create implementation plan
  • Analyze requirements and risks
  • Design initial architecture

Next Steps:
  apm work-item phase-status 1  # View phase requirements
  apm task list --work-item-id=1  # View tasks
  apm work-item phase-advance 1   # Advance when ready
```

### D1 Activities

1. **User Research**
   - Identify target users
   - Understand user needs and pain points
   - Define user personas

2. **Requirements Analysis**
   - Gather functional requirements
   - Identify non-functional requirements (performance, security, etc.)
   - Define acceptance criteria

3. **Technical Feasibility**
   - Assess technical approaches
   - Identify technology constraints
   - Evaluate third-party dependencies

4. **Risk Assessment**
   - Identify technical risks
   - Identify business risks
   - Plan risk mitigation strategies

5. **Initial Design**
   - Create high-level architecture
   - Define system boundaries
   - Identify integration points

### D1 Deliverables

- Requirements document
- User personas
- Acceptance criteria (≥3 items)
- Risk register
- High-level architecture diagram
- Technical feasibility report

---

## P1: Planning Phase

### Purpose

**Create detailed plans, estimates, dependencies, and mitigation strategies**

**Key Questions**:
- How will we build this?
- What tasks are required?
- How long will it take?
- What are the dependencies?
- What could go wrong?

### Typical Activities

Create tasks to develop your implementation plan. Common task types:

- `planning` - Create detailed project plan
- `design` - Detailed system design

**P1 Gate Focus**: Do you have a plan with estimates and dependencies mapped?

### Entry Criteria

✅ D1 phase completed
✅ Requirements validated
✅ Business value confirmed
✅ Technical feasibility proven

### Exit Criteria

✅ Detailed implementation plan
✅ All tasks defined with estimates
✅ Dependencies mapped
✅ Resource allocation confirmed
✅ Risk mitigation plans in place

### P1 Activities

1. **Task Decomposition**
   - Break work into tasks (≤8h each)
   - Define task dependencies
   - Identify critical path

2. **Effort Estimation**
   - Estimate each task
   - Add buffer for uncertainty
   - Validate estimates with team

3. **Dependency Mapping**
   - Identify task dependencies
   - Identify external dependencies
   - Create dependency graph

4. **Resource Planning**
   - Assign agents to tasks
   - Identify skill gaps
   - Plan for resource constraints

5. **Risk Mitigation**
   - Create mitigation plans for each risk
   - Define fallback strategies
   - Assign risk owners

### P1 Deliverables

- Detailed task list with estimates
- Dependency graph
- Resource allocation plan
- Risk mitigation plan
- Timeline/schedule
- Detailed design documents

---

## I1: Implementation Phase

### Purpose

**Build the solution according to plans and designs**

**Key Questions**:
- Are we building the right thing?
- Are tests being written?
- Is documentation being updated?
- Are migrations handled?

### Typical Activities

Build and test your solution. Common task types:

- `implementation` - Write production code
- `testing` - Write tests (target >90% coverage)
- `documentation` - Update docs as you code

**I1 Gate Focus**: Is code complete and tested? Documentation updated?

### Entry Criteria

✅ P1 phase completed
✅ Detailed plans approved
✅ Resources allocated
✅ Design finalized

### Exit Criteria

✅ All implementation tasks completed
✅ Test coverage >90%
✅ Code reviewed
✅ Documentation updated
✅ Migrations created (if applicable)

### I1 Activities

1. **Code Implementation**
   - Write production code
   - Follow coding standards
   - Implement error handling

2. **Test Development**
   - Write unit tests
   - Write integration tests
   - Achieve >90% coverage

3. **Documentation**
   - Update API documentation
   - Write usage examples
   - Update architecture docs

4. **Database Migrations**
   - Create migration scripts
   - Test migrations
   - Document migration steps

5. **Code Review**
   - Submit for peer review
   - Address review feedback
   - Ensure code quality

### I1 Deliverables

- Production code
- Comprehensive test suite (>90% coverage)
- Updated documentation
- Database migrations (if applicable)
- Code review signoffs

---

## R1: Review Phase

### Purpose

**Test, validate, and ensure quality before deployment**

**Key Questions**:
- Do all tests pass?
- Are acceptance criteria met?
- Are there security vulnerabilities?
- Is performance acceptable?

### Typical Activities

Validate quality before deployment. Common task types:

- `testing` - Execute test suite
- `review` - Code and quality review
- `security` - Security scans

**R1 Gate Focus**: Do all tests pass? Acceptance criteria met?

### Entry Criteria

✅ I1 phase completed
✅ All implementation tasks done
✅ Test coverage >90%
✅ Documentation updated

### Exit Criteria

✅ All tests passing
✅ Acceptance criteria validated
✅ Security scan passed
✅ Performance benchmarks met
✅ Code quality standards met

### R1 Activities

1. **Test Execution**
   - Run full test suite
   - Run integration tests
   - Run end-to-end tests

2. **Acceptance Validation**
   - Verify each acceptance criterion
   - Demonstrate functionality
   - Get stakeholder approval

3. **Security Review**
   - Run security scans
   - Check for vulnerabilities
   - Validate access controls

4. **Performance Testing**
   - Run performance benchmarks
   - Identify bottlenecks
   - Optimize if needed

5. **Quality Validation**
   - Static code analysis
   - Code coverage check
   - Documentation review

### R1 Deliverables

- Test execution report
- Acceptance validation report
- Security scan results
- Performance benchmark results
- Quality metrics report

---

## O1: Operations Phase

### Purpose

**Deploy to production and monitor in live environment**

**Key Questions**:
- Is deployment automated?
- Are rollback procedures ready?
- Are monitoring tools configured?
- Is the system healthy in production?

### Typical Activities

Deploy and monitor in production. Common task types:

- `deployment` - Deploy to production
- `monitoring` - Set up monitoring and alerts
- `operations` - Configure health checks

**O1 Gate Focus**: Is deployment successful? Monitoring configured?

### Entry Criteria

✅ R1 phase completed
✅ All quality gates passed
✅ Deployment plan approved
✅ Rollback plan ready

### Exit Criteria

✅ Successfully deployed to production
✅ Monitoring configured
✅ Health checks passing
✅ No critical issues in production
✅ Rollback tested

### O1 Activities

1. **Deployment**
   - Execute deployment plan
   - Verify deployment success
   - Run smoke tests

2. **Monitoring Setup**
   - Configure application monitoring
   - Set up error tracking
   - Create dashboards

3. **Health Verification**
   - Check system health
   - Verify all services running
   - Test critical paths

4. **Rollback Testing**
   - Test rollback procedures
   - Verify rollback works
   - Document rollback steps

5. **Operational Handoff**
   - Train operations team
   - Document operational procedures
   - Set up on-call rotation

### O1 Deliverables

- Deployment confirmation
- Monitoring dashboards
- Health check reports
- Rollback procedures
- Operational runbooks

---

## E1: Evolution Phase

### Purpose

**Learn from production, adapt, and continuously improve**

**Key Questions**:
- How is the system performing in production?
- What issues are users encountering?
- What can we improve?
- What did we learn?

### Typical Activities

Learn and improve from production data. Common task types:

- `analysis` - Analyze production metrics
- `documentation` - Document learnings
- `planning` - Plan next iteration

**E1 Gate Focus**: Have you captured learnings? Next improvements identified?

### Entry Criteria

✅ O1 phase completed
✅ System running in production
✅ Metrics being collected
✅ Minimum observation period passed (e.g., 2 weeks)

### Exit Criteria

✅ Production metrics analyzed
✅ Issues documented
✅ Improvements prioritized
✅ Learnings captured
✅ Next iteration planned

### E1 Activities

1. **Metrics Analysis**
   - Review performance metrics
   - Analyze user behavior
   - Track error rates

2. **Issue Tracking**
   - Collect user feedback
   - Document production issues
   - Prioritize fixes

3. **Continuous Improvement**
   - Identify optimization opportunities
   - Plan technical debt reduction
   - Schedule refactoring

4. **Learning Capture**
   - Document what worked well
   - Document what didn't work
   - Share learnings with team

5. **Next Iteration Planning**
   - Plan improvements for next iteration
   - Create new work items for enhancements
   - Update product backlog

### E1 Deliverables

- Production metrics report
- Issue tracker backlog
- Improvement proposals
- Lessons learned document
- Next iteration plan

---

## Phase Commands Reference

### Check Current Phase

```bash
apm work-item phase-status <id>
```

**Shows**:
- Current phase
- Current status
- Next phase
- Phase sequence
- Available actions

**Real Example**:
```bash
apm work-item phase-status 1
```

---

### Validate Phase Readiness

```bash
apm work-item phase-validate <id>
```

**Checks**:
- Phase gate requirements
- Required tasks present
- Quality standards met
- Dependencies satisfied

**Example**:
```bash
apm work-item phase-validate 1
```

---

### Advance to Next Phase

```bash
apm work-item phase-advance <id>
```

**Validates and advances to next phase**

**Real Example**:
```bash
apm work-item phase-advance 1
```

**Real Output**:
```
Advancing Work Item #1: Product Catalog API
Current Phase: NULL → D1_DISCOVERY

✅ Phase gate validation PASSED
✅ Phase advanced successfully

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements
```

---

## Common Workflows

### Idea-to-Work-Item Conversion Workflow

**Step 1: Create and Develop Idea**
```bash
# Create idea
apm idea create "Add product search functionality"

# Research phase
apm idea transition 5 research
apm idea update 5 --description "Research shows need for full-text search with filters"

# Design phase  
apm idea transition 5 design
apm idea update 5 --description "Design: Elasticsearch integration with faceted search"

# Accept idea
apm idea transition 5 accepted
```

**Step 2: Convert to Work Item**
```bash
# Convert with auto-phase detection (starts in P1_PLAN)
apm idea convert 5 --type=feature --priority=2

# Or skip planning if design already complete
apm idea convert 5 --start-phase=I1_IMPLEMENTATION
```

**Step 3: Continue with Work Item Phases**
```bash
# Work item starts in appropriate phase
apm work-item show 12  # Shows origin: Idea #5

# Continue with normal phase progression
apm work-item phase-advance 12  # P1 → I1
# ... implementation work ...
apm work-item phase-advance 12  # I1 → R1
# ... testing and review ...
```

### Complete Feature Workflow

**Step 1: Create Feature (D1)**
```bash
# Create work item
apm work-item create "Product Catalog API" --type=feature --priority=1 \
  --business-context "Enable product discovery for 1000+ SKUs"

# Advance to D1
apm work-item phase-advance 1

# Create discovery tasks
apm task create "Requirements Analysis" --work-item-id=1 --type=analysis --effort=4
apm task create "Technical Feasibility Study" --work-item-id=1 --type=research --effort=3
apm task create "Initial Architecture Design" --work-item-id=1 --type=design --effort=3
```

**Step 2: Plan Feature (P1)**
```bash
# Complete D1 tasks (work on them)
# ...

# Advance to P1
apm work-item phase-advance 1

# Create planning tasks
apm task create "Detailed Implementation Plan" --work-item-id=1 --type=planning --effort=3
apm task create "API Design Specification" --work-item-id=1 --type=design --effort=4
```

**Step 3: Implement Feature (I1)**
```bash
# Complete P1 tasks
# ...

# Advance to I1
apm work-item phase-advance 1

# Create implementation tasks
apm task create "Implement Product API" --work-item-id=1 --type=implementation --effort=4
apm task create "Write API Tests" --work-item-id=1 --type=testing --effort=3
apm task create "Document API" --work-item-id=1 --type=documentation --effort=2
```

**Step 4: Review Feature (R1)**
```bash
# Complete I1 tasks
# ...

# Advance to R1
apm work-item phase-advance 1

# Create review tasks
apm task create "Execute Test Suite" --work-item-id=1 --type=testing --effort=2
apm task create "Code Review" --work-item-id=1 --type=review --effort=2
```

**Step 5: Deploy Feature (O1)**
```bash
# Complete R1 tasks
# ...

# Advance to O1
apm work-item phase-advance 1

# Create operations tasks
apm task create "Deploy to Production" --work-item-id=1 --type=deployment --effort=3
apm task create "Configure Monitoring" --work-item-id=1 --type=monitoring --effort=2
```

**Step 6: Evolve Feature (E1)**
```bash
# Complete O1 tasks
# ...

# Advance to E1
apm work-item phase-advance 1

# Create evolution tasks
apm task create "Analyze Production Metrics" --work-item-id=1 --type=analysis --effort=2
apm task create "Document Learnings" --work-item-id=1 --type=documentation --effort=1
```

---

### Quick Feature (Skip Early Phases)

For well-understood features, you can start at later phases:

```bash
# Create work item starting at I1
apm work-item create "Simple Bug Fix" --type=bugfix --phase=i1_implementation

# Create required tasks
apm task create "Fix Bug" --work-item-id=<id> --type=bugfix --effort=2
apm task create "Test Fix" --work-item-id=<id> --type=testing --effort=1

# Advance through remaining phases
apm work-item phase-advance <id>  # I1 → R1
apm work-item phase-advance <id>  # R1 → O1
apm work-item phase-advance <id>  # O1 → E1
```

---

## Phase Best Practices

### General

1. **Don't Skip Phases**: Each phase adds value and reduces risk
2. **Validate Thoroughly**: Use `phase-validate` before advancing
3. **Document Everything**: Capture decisions and learnings
4. **Iterate**: Phases can repeat if rework is needed

### D1 Discovery

- Start with user needs, not technical solutions
- Validate business value before investing in design
- Identify risks early when they're cheaper to address
- Get stakeholder buy-in on requirements

### P1 Planning

- Break tasks to ≤8h for better estimates
- Map dependencies to identify critical path
- Add buffer for uncertainty (20-30%)
- Review plans with team before committing

### I1 Implementation

- Write tests FIRST (TDD approach)
- Keep tasks ≤4h for implementation
- Update docs as you code, not after
- Commit frequently with clear messages

### R1 Review

- Automate testing where possible
- Get independent code reviews
- Don't skip security scans
- Validate acceptance criteria with stakeholders

### O1 Operations

- Test rollback BEFORE deploying
- Set up monitoring BEFORE deploying
- Deploy during low-traffic windows
- Have on-call support ready

### E1 Evolution

- Give system time to stabilize (≥2 weeks)
- Track both quantitative and qualitative feedback
- Prioritize technical debt reduction
- Share learnings across teams

---

## Phase Metrics

### Tracking Phase Progress

```bash
# Check phase distribution
apm work-item list --phase=d1_discovery
apm work-item list --phase=i1_implementation
apm work-item list --phase=r1_review

# Check phase duration (via session history)
apm work-item show-history <id>
```

### Key Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| Phase Cycle Time | Time from phase start to completion | <1 week per phase |
| Phase Rework Rate | % of work items that regress to earlier phase | <10% |
| Phase Gate Pass Rate | % of validations that pass on first attempt | >80% |
| Phase Distribution | % of work items in each phase | Balanced pipeline |

---

## See Also

- [Getting Started Guide](01-getting-started.md) - Learn the basics
- [Quick Reference Card](02-quick-reference.md) - Common workflows
- [CLI Command Reference](03-cli-commands.md) - Complete command docs
- [Troubleshooting Guide](05-troubleshooting.md) - Solutions to common issues

---

**Generated**: 2025-10-17
**APM Version**: 2.0
**Real Examples**: All examples from live walkthrough of fullstack-ecommerce project

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Phase Workflow](cli-reference/commands.md)
- [➡️ Next: Ideas Workflow](workflows/ideas-workflow.md)

---
