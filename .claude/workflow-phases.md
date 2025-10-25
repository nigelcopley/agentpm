# APM (Agent Project Manager) Workflow Phases & Quality Gates

## 🎯 **WORKFLOW PHASES OVERVIEW**

APM (Agent Project Manager) follows a strict phase progression: **D1 → P1 → I1 → R1 → O1 → E1**

Each phase has:
- **Gate requirements** (must pass before advancing)
- **Specific commands** for common operations
- **Expected deliverables**
- **Quality checks**

---

## 📊 **PHASE PROGRESSION TABLE**

| Phase | Name | Gate Requirements | Primary Commands | Deliverables |
|-------|------|-------------------|------------------|--------------|
| **D1** | Discovery | business_context ≥50 chars<br>acceptance_criteria ≥3<br>risks ≥1<br>6W confidence ≥0.70 | `apm work-item show <id>`<br>`apm context show --work-item-id=<id>`<br>`apm idea analyze <id>` | Requirements defined<br>Context enriched<br>Risks identified |
| **P1** | Planning | Tasks created<br>Estimates complete<br>Dependencies mapped<br>Mitigations planned | `apm task create`<br>`apm task list --work-item-id=<id>`<br>`apm work-item add-dependency` | Implementation plan<br>Task breakdown<br>Dependencies mapped |
| **I1** | Implementation | Tests updated<br>Code complete<br>Docs updated<br>Migrations created | `apm task start <id>`<br>`apm context show --task-id=<id>`<br>`pytest tests/ -v --cov=agentpm` | Feature implemented<br>Tests passing<br>Documentation updated |
| **R1** | Review | AC verified<br>Tests pass (100%)<br>Quality checks pass<br>Code review approved | `pytest --cov-report=html`<br>`ruff check agentpm/`<br>`apm task approve <id>` | Quality validated<br>AC verified<br>Review approved |
| **O1** | Operations | Version bumped<br>Deployed<br>Health checks pass<br>Monitors active | `git tag v<version>`<br>`git push origin v<version>` | Deployed to production<br>Monitoring active<br>Health checks passing |
| **E1** | Evolution | Telemetry analyzed<br>Improvements identified<br>Feedback captured | `apm learnings list --recent`<br>`apm idea create` | Improvements backlog<br>Patterns documented<br>Technical debt cataloged |

---

## 🔍 **D1 DISCOVERY PHASE**

### **Purpose**
Transform raw requests into well-defined work items with acceptance criteria and risks.

### **Gate Requirements**
- ✅ Problem statement clear and scoped
- ✅ Value proposition documented
- ✅ Acceptance criteria ≥3 and testable
- ✅ Risks identified with mitigations
- ✅ Confidence score ≥0.70

### **Commands**
```bash
# Get work item details
apm work-item show <id>

# Get comprehensive context
apm context show --work-item-id=<id>

# Analyze idea comprehensively
apm idea analyze <id> --comprehensive

# Search related decisions and summaries
apm session history --search='relevant keywords'
apm summary list --search='relevant keywords'

# Validate D1 gate
apm work-item validate <id>

# Progress to next phase
apm work-item next <id>
```

### **Sub-Agents to Delegate To**
- `intent-triage` — Classify request type and complexity
- `context-assembler` — Gather relevant project context
- `problem-framer` — Define clear problem statement
- `value-articulator` — Document why this work matters
- `ac-writer` — Generate testable acceptance criteria
- `risk-notary` — Identify risks and mitigations
- `definition-gate-check` — Validate D1 gate criteria

---

## 📋 **P1 PLANNING PHASE**

### **Purpose**
Create implementation plan with tasks, estimates, and dependencies.

### **Gate Requirements**
- ✅ Tasks created for all required types
- ✅ Effort estimates complete
- ✅ Dependencies mapped
- ✅ Risk mitigations planned
- ✅ Time-boxing compliance verified

### **Commands**
```bash
# Create tasks for work item
apm task create 'Task Name' --type=implementation --effort=4

# List tasks for work item
apm task list --work-item-id=<id>

# Add dependencies
apm work-item add-dependency <id> --depends-on=<id>

# View dependency graph
apm work-item list-dependencies <id>

# Validate P1 gate
apm work-item validate <id>
```

### **Required Task Types by Work Item Type**
- **FEATURE**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX**: ANALYSIS + BUGFIX + TESTING
- **RESEARCH**: RESEARCH + ANALYSIS + DOCUMENTATION
- **DOCUMENTATION**: RESEARCH + DOCUMENTATION + REVIEW

### **Time-Boxing Limits**
- **IMPLEMENTATION**: Max 4 hours (STRICT)
- **DESIGN**: Max 8 hours
- **TESTING**: Max 6 hours
- **DOCUMENTATION**: Max 6 hours
- **ANALYSIS**: Max 8 hours
- **RESEARCH**: Max 12 hours

---

## 🔧 **I1 IMPLEMENTATION PHASE**

### **Purpose**
Implement features following established patterns and quality standards.

### **Gate Requirements**
- ✅ Tests updated and passing
- ✅ Code complete and functional
- ✅ Documentation updated
- ✅ Database migrations created (if needed)
- ✅ Quality gates validated

### **Commands**
```bash
# Start task
apm task start <id>

# Get task context
apm context show --task-id=<id>

# Run tests with coverage
pytest tests/ -v --cov=agentpm

# Record implementation decisions
apm session add-decision "Decision rationale" --rationale="Supporting evidence and context"

# Complete task with evidence
apm task complete <id> --evidence='Implementation details'
```

### **Implementation Standards**
- Follow DatabaseService pattern for new services
- Use three-layer architecture (Models → Adapters → Methods)
- Provide actionable error messages for agents
- Use Rich formatting for CLI output
- Record decisions with evidence
- Maintain >90% test coverage

---

## 🔍 **R1 REVIEW PHASE**

### **Purpose**
Validate quality, verify acceptance criteria, and approve for deployment.

### **Gate Requirements**
- ✅ All acceptance criteria verified
- ✅ Tests pass (100% pass rate)
- ✅ Quality checks pass
- ✅ Code review approved
- ✅ Documentation complete

### **Commands**
```bash
# Run full test suite with coverage report
pytest tests/ -v --cov=agentpm --cov-report=html

# Run linter
ruff check agentpm/

# Check code formatting
black --check agentpm/

# Validate work item quality
apm work-item validate <id>

# Approve task (different agent required)
apm task approve <id>

# Request changes with reason
apm task request-changes <id> --reason='Specific issue'
```

### **Quality Standards**
- **Test Coverage**: ≥90% required
- **Code Quality**: No linting errors
- **Documentation**: Complete and accurate
- **Acceptance Criteria**: All verified
- **Security**: No vulnerabilities

---

## 🚀 **O1 OPERATIONS PHASE**

### **Purpose**
Deploy to production and ensure operational readiness.

### **Gate Requirements**
- ✅ Version bumped appropriately
- ✅ Deployed to production
- ✅ Health checks passing
- ✅ Monitoring active
- ✅ Rollback plan ready

### **Commands**
```bash
# Create version tag
git tag v<version>

# Deploy to production
git push origin v<version>

# Record deployment learning
apm session add-decision "Deployment completed" --rationale="Deployment notes and lessons learned"
apm summary create --entity-type=work_item --entity-id=<id> --summary-type=deployment --text="Deployment details and outcomes"

# Validate O1 gate
apm work-item validate <id>
```

### **Operational Requirements**
- Version management
- Deployment automation
- Health monitoring
- Performance tracking
- Error logging
- Rollback procedures

---

## 📈 **E1 EVOLUTION PHASE**

### **Purpose**
Analyze telemetry, identify improvements, and plan next iterations.

### **Gate Requirements**
- ✅ Telemetry analyzed
- ✅ Improvements identified
- ✅ Feedback captured
- ✅ Patterns documented
- ✅ Technical debt cataloged

### **Commands**
```bash
# Review recent decisions and summaries
apm session history --search="recent"
apm summary list --recent

# Record patterns discovered
apm session add-decision "Pattern discovered: [pattern description]" --rationale="Usage guidance and when to apply"
apm document add --entity-type=work_item --entity-id=<id> --file-path="docs/patterns/[pattern-name].md" --document-type=pattern

# Create improvement ideas
apm idea create 'Improvement idea' --type=enhancement

# Analyze idea for feasibility
apm idea analyze <id> --comprehensive

# Create improvement work item
apm work-item create 'Improvement' --type=enhancement
```

### **Evolution Activities**
- Performance analysis
- User feedback review
- Technical debt assessment
- Pattern recognition
- Improvement planning
- Knowledge capture

---

## 🚨 **QUALITY GATE VALIDATION**

### **Gate Validation Process**

**Before advancing phases, ALWAYS validate gates:**

```bash
# Check if work item is ready to advance
apm work-item validate <id>

# View validation results and missing requirements
apm work-item show <id>
```

### **CI Gates (Automated Validation)**

APM (Agent Project Manager) enforces these quality gates automatically:

#### CI-001: Agent Validation
- Valid agent assigned to work item/task
- Agent has required capabilities
- Agent is active and available

**Check**: `apm agents list`

#### CI-002: Context Quality
- Context confidence ≥ 0.70
- 6W context complete (WHO, WHAT, WHEN, WHERE, WHY, HOW)
- Evidence sources documented

**Check**: `apm context show --work-item-id=<id>`

#### CI-004: Testing Quality
- Test coverage ≥ 90%
- All tests passing (100% pass rate)
- AAA pattern (Arrange-Act-Assert) followed
- Project-relative imports only

**Check**: `pytest tests/ -v --cov=agentpm`

#### CI-006: Documentation Standards
- Description ≥ 50 chars
- Business context defined
- No placeholder text (TODO, TBD, FIXME)
- Technical decisions documented

**Check**: `apm work-item validate <id>`

---

## ⚠️ **COMMON ISSUES & SOLUTIONS**

### **Gate Validation Failed**

**Symptoms**: `apm work-item validate <id>` fails

**Diagnostic**:
```bash
apm work-item show <id>
apm work-item validate <id>
```

**Recovery**:
- Check missing criteria in validation output
- Complete missing requirements
- Re-validate before advancing

### **Test Failure**

**Symptoms**: pytest returns non-zero exit code

**Diagnostic**:
```bash
pytest tests/ -v --tb=short
```

**Recovery**:
- Fix failing tests
- Ensure ≥90% coverage
- Re-run tests: `pytest tests/ -v --cov=agentpm`

### **Context Confidence Low**

**Symptoms**: Context confidence < 0.70

**Diagnostic**:
```bash
apm context show --task-id=<id>
```

**Recovery**:
- Enrich context with evidence
- Add sources and references
- Document decision rationale
- Re-check confidence

### **Task Time-Box Exceeded**

**Symptoms**: Implementation task > 4 hours effort

**Diagnostic**:
```bash
apm task show <id>
```

**Recovery**:
- Break task into smaller units (≤4h each)
- Create subtasks: `apm task create 'Subtask' --effort=3`
- Map dependencies between subtasks

---

## 🎯 **SUCCESS INDICATORS**

### **Phase Completion Criteria**
- **D1**: Clear requirements, acceptance criteria, risk assessment
- **P1**: Complete task breakdown, dependencies mapped, estimates done
- **I1**: Feature implemented, tests passing, documentation updated
- **R1**: Quality validated, acceptance criteria verified, approved
- **O1**: Deployed to production, monitoring active, health checks passing
- **E1**: Telemetry analyzed, improvements identified, patterns documented

### **Quality Metrics**
- **Context Quality**: >80% GREEN context quality scores
- **Test Coverage**: ≥90% maintained
- **Time-Boxing**: All tasks within limits
- **Dependency Management**: No circular dependencies
- **Evidence Tracking**: All decisions recorded with evidence

---

**Remember: Each phase must be completed with quality gates passed before advancing to the next phase. This ensures consistent, high-quality development throughout the entire lifecycle.**
