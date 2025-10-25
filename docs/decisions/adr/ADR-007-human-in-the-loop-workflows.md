# ADR-007: Human-in-the-Loop Workflows

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Define when human review/approval is required vs. AI-only automation

---

## Context

### The Automation vs. Control Dilemma

AIPM enables AI agents to work autonomously on complex projects, but **not all decisions should be automated**:

**High-Risk Decisions:**
- Architecture choices affecting entire system
- Security-critical implementations
- Data schema changes in production
- External API integrations
- Cost-impacting infrastructure decisions
- Regulatory/compliance-affecting changes

**Current Problem:**

```
Scenario: AI agent decides to use MongoDB instead of PostgreSQL
├─ Agent reasoning: "MongoDB better for this use case"
├─ Creates migration plan
├─ Begins implementation
└─ Problem: No human reviewed this critical decision ❌

Result:
- 2 weeks of work on MongoDB implementation
- Discover: Doesn't meet compliance requirements
- Must revert to PostgreSQL
- Wasted effort, missed deadlines

What should have happened:
- Agent proposes MongoDB decision
- Flags for human review (architecture impact)
- Human reviews evidence, approves/rejects
- Only then: Implementation proceeds
```

### Requirements

1. **Risk-Based Gating**: Automatic detection of high-risk decisions
2. **Human Review Workflow**: Clear process for human approval
3. **Non-Blocking for Low Risk**: Don't slow down routine work
4. **Audit Trail**: Track human decisions and rationale
5. **Escalation Path**: Route to appropriate human reviewer
6. **Timeout Handling**: What happens if human doesn't respond

---

## Decision

We will implement a **Risk-Based Human Review System** with:

1. **Risk Scoring**: Automatically classify decisions by risk level
2. **Review Requirements**: Define what requires human approval
3. **Review Workflow**: Request → Review → Approve/Reject → Proceed
4. **Reviewer Routing**: Assign to appropriate human based on domain
5. **SLA Management**: Timeouts and escalation for stalled reviews

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AI Agent Work Flow                         │
│                                                         │
│  Agent makes decision                                   │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────┐                                  │
│  │  Risk Scoring    │                                  │
│  │  Algorithm       │                                  │
│  └────────┬─────────┘                                  │
│           │                                             │
│    ┌──────┴───────┐                                    │
│    │              │                                     │
│  Low Risk      High Risk                               │
│    │              │                                     │
│    ▼              ▼                                     │
│  Auto-      ┌─────────────────┐                        │
│  Approve    │  Human Review   │                        │
│    │        │  Required       │                        │
│    │        └────────┬────────┘                        │
│    │                 │                                  │
│    │          ┌──────┴──────┐                          │
│    │          │             │                          │
│    │      Approved    Rejected                         │
│    │          │             │                          │
│    └──────────┴─────────────┘                          │
│               │                                         │
│               ▼                                         │
│         Implementation                                  │
│          Proceeds                                       │
└─────────────────────────────────────────────────────────┘
```

### Risk Scoring Algorithm

```python
class DecisionRiskScorer:
    """
    Calculate risk score for decisions to determine if human review needed.

    Risk factors:
    - Impact scope (file, module, system, architecture)
    - Reversibility (easy, moderate, difficult, irreversible)
    - Cost implications (none, low, medium, high)
    - Security impact (none, low, medium, critical)
    - Compliance impact (none, low, high)
    - Confidence level (high confidence = lower risk)
    """

    def score_decision(self, decision: Decision) -> RiskScore:
        """
        Calculate risk score (0.0-1.0).

        0.0-0.3: Low risk (auto-approve)
        0.3-0.7: Medium risk (optional review)
        0.7-1.0: High risk (mandatory review)
        """

        # Factor 1: Impact Scope (40% weight)
        scope_score = self._score_impact_scope(decision)

        # Factor 2: Reversibility (25% weight)
        reversibility_score = self._score_reversibility(decision)

        # Factor 3: Cost Impact (15% weight)
        cost_score = self._score_cost_impact(decision)

        # Factor 4: Security Impact (15% weight)
        security_score = self._score_security_impact(decision)

        # Factor 5: Compliance Impact (5% weight)
        compliance_score = self._score_compliance_impact(decision)

        # Weighted average
        risk_score = (
            scope_score * 0.40 +
            reversibility_score * 0.25 +
            cost_score * 0.15 +
            security_score * 0.15 +
            compliance_score * 0.05
        )

        # Adjust based on confidence (low confidence = higher risk)
        if decision.confidence < 0.6:
            risk_score *= 1.2  # Increase risk by 20%

        risk_score = min(risk_score, 1.0)  # Cap at 1.0

        return RiskScore(
            overall=risk_score,
            factors={
                "scope": scope_score,
                "reversibility": reversibility_score,
                "cost": cost_score,
                "security": security_score,
                "compliance": compliance_score
            },
            requires_review=risk_score >= 0.7,
            review_level=self._determine_review_level(risk_score)
        )

    def _score_impact_scope(self, decision: Decision) -> float:
        """
        How much of the system is affected?

        0.0-0.25: Single file
        0.25-0.50: Single module/component
        0.50-0.75: Multiple modules
        0.75-1.0: System-wide/architectural
        """

        keywords = {
            "architecture": 1.0,
            "system-wide": 0.9,
            "database schema": 0.85,
            "api contract": 0.8,
            "multi-module": 0.6,
            "module": 0.4,
            "file": 0.2
        }

        decision_text = f"{decision.title} {decision.decision} {decision.rationale}".lower()

        for keyword, score in keywords.items():
            if keyword in decision_text:
                return score

        return 0.3  # Default: moderate scope

    def _score_reversibility(self, decision: Decision) -> float:
        """
        How hard to reverse this decision?

        0.0-0.25: Trivial to reverse
        0.25-0.50: Easy to reverse
        0.50-0.75: Difficult to reverse
        0.75-1.0: Irreversible or very costly
        """

        irreversible_keywords = [
            "database migration",
            "production schema",
            "external api commitment",
            "vendor lock-in",
            "architectural pattern"
        ]

        decision_text = f"{decision.title} {decision.decision}".lower()

        for keyword in irreversible_keywords:
            if keyword in decision_text:
                return 0.8  # High cost to reverse

        # Check if decision mentions "easy to change" or "reversible"
        if "reversible" in decision_text or "easy to change" in decision_text:
            return 0.2

        return 0.5  # Default: moderately reversible

    def _score_cost_impact(self, decision: Decision) -> float:
        """
        What's the cost impact?

        0.0: No cost impact
        0.3: Low cost (<$100/month)
        0.6: Medium cost ($100-1000/month)
        1.0: High cost (>$1000/month)
        """

        cost_keywords = {
            "infrastructure": 0.7,
            "database scaling": 0.8,
            "third-party service": 0.6,
            "api calls": 0.5,
            "storage": 0.4
        }

        decision_text = decision.rationale.lower()

        for keyword, score in cost_keywords.items():
            if keyword in decision_text:
                return score

        return 0.2  # Default: low cost impact

    def _score_security_impact(self, decision: Decision) -> float:
        """
        Security implications?

        0.0: No security impact
        0.5: Low security relevance
        0.8: Moderate security impact
        1.0: Critical security decision
        """

        security_keywords = [
            "authentication",
            "authorization",
            "encryption",
            "credentials",
            "api keys",
            "access control",
            "security"
        ]

        decision_text = f"{decision.title} {decision.decision}".lower()

        for keyword in security_keywords:
            if keyword in decision_text:
                return 0.9  # High security impact

        return 0.1  # Default: minimal security impact

    def _determine_review_level(self, risk_score: float) -> str:
        """
        Who should review?

        0.0-0.3: No review needed (AI auto-approve)
        0.3-0.7: Peer review (another AI agent or junior dev)
        0.7-0.9: Senior review (senior dev, tech lead)
        0.9-1.0: Executive review (CTO, architect)
        """

        if risk_score < 0.3:
            return "auto-approve"
        elif risk_score < 0.7:
            return "peer"
        elif risk_score < 0.9:
            return "senior"
        else:
            return "executive"
```

### Human Review Workflow

```python
@dataclass
class HumanReviewRequest:
    """
    Request for human review of AI decision.
    """

    # Identification
    id: str  # UUID
    decision_id: str
    work_item_id: int
    task_id: Optional[int]

    # Risk context
    risk_score: float
    risk_factors: Dict[str, float]
    review_level: Literal["peer", "senior", "executive"]

    # Decision summary
    decision_summary: str  # ≤200 words
    why_review_needed: str
    potential_impact: str
    alternatives: List[str]

    # Review workflow
    requested_at: datetime
    requested_by: str  # Agent ID
    assigned_to: Optional[str]  # Human reviewer
    sla_deadline: datetime  # When decision becomes stale
    urgency: Literal["low", "medium", "high", "critical"]

    # Resolution
    status: Literal["pending", "under_review", "approved", "rejected", "escalated"]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    follow_up_required: bool

class HumanReviewService:
    """
    Manages human review workflow.
    """

    def request_review(
        self,
        decision: Decision,
        risk_score: RiskScore,
        urgency: str = "medium"
    ) -> HumanReviewRequest:
        """
        Create human review request.

        Steps:
        1. Calculate SLA deadline based on urgency
        2. Route to appropriate reviewer (based on review_level)
        3. Create notification (email, Slack, CLI alert)
        4. Track in database
        5. Return review request

        SLA Deadlines:
        - Critical: 4 hours
        - High: 24 hours
        - Medium: 3 days
        - Low: 1 week
        """

        # Calculate deadline
        sla_hours = {
            "critical": 4,
            "high": 24,
            "medium": 72,
            "low": 168
        }
        deadline = datetime.now() + timedelta(hours=sla_hours[urgency])

        # Create review request
        review = HumanReviewRequest(
            id=generate_uuid(),
            decision_id=decision.id,
            work_item_id=decision.work_item_id,
            risk_score=risk_score.overall,
            risk_factors=risk_score.factors,
            review_level=risk_score.review_level,
            decision_summary=self._summarize_decision(decision),
            why_review_needed=self._explain_risk(risk_score),
            potential_impact=self._analyze_impact(decision),
            alternatives=decision.alternatives_considered,
            requested_at=datetime.now(),
            requested_by=decision.made_by,
            assigned_to=self._route_reviewer(risk_score.review_level),
            sla_deadline=deadline,
            urgency=urgency,
            status="pending"
        )

        db.add(review)
        db.commit()

        # Send notification
        self._notify_reviewer(review)

        return review

    def approve_decision(
        self,
        review_id: str,
        reviewer: str,
        notes: Optional[str] = None
    ) -> Decision:
        """
        Human approves decision.

        Steps:
        1. Update review status
        2. Update decision status to 'accepted'
        3. Record human approval in audit trail
        4. Notify agent to proceed
        5. Return approved decision
        """

        review = db.query(HumanReviewRequest).get(review_id)
        review.status = "approved"
        review.reviewed_by = reviewer
        review.reviewed_at = datetime.now()
        review.review_notes = notes

        # Update decision
        decision = db.query(Decision).get(review.decision_id)
        decision.status = "accepted"
        decision.reviewed_by = reviewer

        # Audit trail
        audit_log.record(
            actor=reviewer,
            actor_type="human",
            action="APPROVE_DECISION",
            entity_type="decision",
            entity_id=decision.id,
            context={
                "review_id": review_id,
                "risk_score": review.risk_score,
                "review_notes": notes
            }
        )

        db.commit()

        # Notify agent
        event_bus.publish("decision.approved", decision)

        return decision

    def reject_decision(
        self,
        review_id: str,
        reviewer: str,
        reason: str,
        alternative_suggested: Optional[str] = None
    ) -> Decision:
        """
        Human rejects decision.

        Steps:
        1. Update review status
        2. Update decision status to 'rejected'
        3. Record rejection rationale
        4. Notify agent with feedback
        5. Optionally suggest alternative
        """

        review = db.query(HumanReviewRequest).get(review_id)
        review.status = "rejected"
        review.reviewed_by = reviewer
        review.reviewed_at = datetime.now()
        review.review_notes = reason

        decision = db.query(Decision).get(review.decision_id)
        decision.status = "rejected"

        # Create learning from rejection
        learning = Learning(
            work_item_id=decision.work_item_id,
            learning_type="constraint",
            content=f"Rejected approach: {decision.decision}",
            rationale=reason,
            agent_id="human-reviewer",
            confidence=1.0  # Human decision = high confidence
        )
        db.add(learning)

        # If alternative suggested, create new decision
        if alternative_suggested:
            new_decision = Decision(
                work_item_id=decision.work_item_id,
                title=f"{decision.title} (Revised)",
                decision=alternative_suggested,
                rationale=f"Based on human review: {reason}",
                made_by=reviewer,
                confidence=0.9,
                status="proposed"
            )
            db.add(new_decision)

        db.commit()

        # Notify agent
        event_bus.publish("decision.rejected", {
            "decision": decision,
            "reason": reason,
            "alternative": alternative_suggested
        })

        return decision
```

### Review Triggers (Risk-Based)

```yaml
Auto-Approve (Risk < 0.3):
  Examples:
    - Code formatting decisions
    - Variable naming
    - Test case additions
    - Documentation updates
    - Refactoring within module

  Process:
    - AI agent decides
    - Auto-approved immediately
    - No human review
    - Audit trail recorded

Peer Review (Risk 0.3-0.7):
  Examples:
    - New feature implementation approach
    - Performance optimization strategy
    - Testing strategy selection
    - Module-level architecture

  Process:
    - AI agent decides
    - Flagged for peer review (another agent or junior dev)
    - 3-day SLA
    - Work can proceed if no response (with warning)

Senior Review (Risk 0.7-0.9):
  Examples:
    - Database schema changes
    - API contract changes
    - Security implementation
    - Integration with external systems

  Process:
    - AI agent proposes
    - Requires senior dev/tech lead approval
    - 24-hour SLA
    - Work BLOCKED until approved
    - Escalates if no response

Executive Review (Risk 0.9-1.0):
  Examples:
    - Architecture paradigm changes
    - Technology stack changes (new database, framework)
    - Major security decisions
    - Compliance-affecting changes

  Process:
    - AI agent proposes
    - Requires CTO/architect approval
    - 4-hour SLA for critical, 24-hour for high
    - Work BLOCKED until approved
    - Auto-escalates to CEO if needed
```

### CLI Commands

```bash
# List pending reviews
apm review list

# Output:
# 🔍 Pending Reviews (3):
#
# 1. [CRITICAL] Database Technology Change (WI-5, Task-42)
#    Decision: Switch from PostgreSQL to MongoDB
#    Risk Score: 0.95 (architecture impact, high cost)
#    Requested: 2 hours ago by aipm-database-developer
#    SLA: 2 hours remaining
#    Assigned to: tech-lead@company.com
#
# 2. [HIGH] Security Implementation (WI-8, Task-67)
#    Decision: Use OAuth2 with external provider
#    Risk Score: 0.82 (security, external dependency)
#    Requested: 1 day ago by aipm-python-cli-developer
#    SLA: 23 hours remaining
#    Assigned to: security-team@company.com

# Review decision
apm review show <review-id>

# Output: Full decision details, evidence, risk analysis

# Approve decision
apm review approve <review-id> \
  --notes "Approved. MongoDB justified for this use case."

# Reject decision
apm review reject <review-id> \
  --reason "PostgreSQL required for ACID compliance" \
  --alternative "Keep PostgreSQL, use JSONB for flexibility"

# Escalate review
apm review escalate <review-id> \
  --to="cto@company.com" \
  --reason="Tech lead unavailable, decision blocking critical path"
```

### Human Review Dashboard

```python
def generate_review_dashboard() -> ReviewDashboard:
    """
    Dashboard for human reviewers.
    """

    pending = db.query(HumanReviewRequest).filter(
        HumanReviewRequest.status.in_(["pending", "under_review"])
    ).all()

    # Group by urgency
    critical = [r for r in pending if r.urgency == "critical"]
    high = [r for r in pending if r.urgency == "high"]
    medium = [r for r in pending if r.urgency == "medium"]

    # SLA tracking
    overdue = [r for r in pending if datetime.now() > r.sla_deadline]
    due_soon = [
        r for r in pending
        if r.sla_deadline - datetime.now() < timedelta(hours=4)
    ]

    return ReviewDashboard(
        total_pending=len(pending),
        critical_count=len(critical),
        high_count=len(high),
        overdue_count=len(overdue),
        due_soon_count=len(due_soon),
        avg_review_time=calculate_avg_review_time(),
        reviews_this_week=count_reviews_this_week()
    )
```

---

## Consequences

### Positive

1. **Risk Mitigation**
   - High-risk decisions reviewed by humans
   - Prevents costly mistakes
   - Architecture quality maintained

2. **Appropriate Automation**
   - Low-risk work fully automated
   - No unnecessary bottlenecks
   - Fast development for routine tasks

3. **Clear Accountability**
   - Human decisions explicitly recorded
   - Audit trail for compliance
   - Can answer "who approved this?"

4. **Learning from Humans**
   - Rejected decisions become constraints
   - AI learns from human feedback
   - Quality improves over time

5. **Confidence Calibration**
   - Low-confidence AI decisions flagged
   - Humans validate uncertain choices
   - System learns confidence thresholds

### Negative

1. **Human Bottleneck**
   - High-risk work blocked on human availability
   - SLA pressure on reviewers
   - Could slow down development

2. **Review Fatigue**
   - Too many review requests
   - Reviewers may rubber-stamp
   - Quality degrades

3. **Complexity**
   - Adds review workflow to system
   - Notification systems needed
   - SLA tracking overhead

4. **False Positives**
   - Risk scoring may be wrong
   - Low-risk flagged as high-risk
   - Wasted reviewer time

### Mitigation Strategies

1. **Optimize Review Volume**
   - Tune risk thresholds (start conservative, relax over time)
   - Batch similar reviews
   - AI learns from approvals (auto-approve similar decisions)

2. **Prevent Review Fatigue**
   - Clear, concise review requests (≤200 words)
   - Include evidence and analysis
   - Recommend approval/rejection (AI suggestion)
   - Track reviewer metrics (prevent overload)

3. **SLA Management**
   - Automatic escalation
   - Backup reviewers
   - Holiday/vacation coverage
   - Critical path prioritization

4. **Risk Scoring Calibration**
   - A/B test risk scoring accuracy
   - Human feedback on risk scores
   - Tune weights based on outcomes
   - Allow manual override

---

## Implementation Plan

### Phase 1: Risk Scoring (Week 1)

```yaml
Tasks:
  - Implement DecisionRiskScorer
  - Define risk factors and weights
  - Test scoring algorithm
  - Calibrate thresholds

Deliverables:
  - agentpm/core/risk/scorer.py
  - Risk scoring tests-BAK
  - Calibration report

Success Criteria:
  - Risk scores 0.0-1.0
  - Accuracy >80% (human validation)
  - Clear factor explanations
```

### Phase 2: Review Workflow (Week 2)

```yaml
Tasks:
  - Implement HumanReviewService
  - Create review request model
  - Build approval/rejection logic
  - SLA tracking

Deliverables:
  - agentpm/core/review/service.py
  - Database models
  - CLI: apm review list/show/approve/reject

Success Criteria:
  - Review workflow works
  - SLAs tracked accurately
  - Notifications sent
```

### Phase 3: Integration (Week 3)

```yaml
Tasks:
  - Integrate with decision system
  - Add risk scoring to all decisions
  - Auto-flag high-risk decisions
  - Agent workflow integration

Deliverables:
  - Decision system integration
  - Agent blocking on high-risk
  - Review dashboard

Success Criteria:
  - High-risk decisions auto-flagged
  - Agents wait for approval
  - Dashboard shows pending reviews
```

### Phase 4: Notifications & UI (Week 4)

```yaml
Tasks:
  - Email notifications
  - Slack integration
  - CLI alerts
  - Web dashboard (optional)

Deliverables:
  - Notification system
  - Slack webhooks
  - Review dashboard (CLI/web)

Success Criteria:
  - Reviewers notified immediately
  - SLA reminders work
  - Easy to review from any device
```

---

## Usage Examples

### Example 1: Auto-Approved Low-Risk Decision

```python
# AI agent decides: "Use black for code formatting"
decision = Decision(
    title="Code Formatting Tool Selection",
    decision="Use black for Python code formatting",
    rationale="Consistent, opinionated, widely adopted",
    confidence=0.95,
    made_by="aipm-python-cli-developer"
)

# Risk scoring
risk = scorer.score_decision(decision)
# risk.overall = 0.15 (low risk: formatting is low impact)

# Auto-approved (no human needed)
decision.status = "accepted"
db.commit()

# Agent proceeds immediately
# No delay, no bottleneck
```

### Example 2: High-Risk Decision Requires Review

```python
# AI agent proposes: "Switch to MongoDB"
decision = Decision(
    title="Database Technology Change",
    decision="Migrate from PostgreSQL to MongoDB",
    rationale="Better for document-oriented data model",
    alternatives_considered=["Keep PostgreSQL with JSONB"],
    confidence=0.75,
    made_by="aipm-database-developer"
)

# Risk scoring
risk = scorer.score_decision(decision)
# risk.overall = 0.95 (very high risk: architecture change, high cost, difficult to reverse)

# Create review request
review = review_service.request_review(
    decision=decision,
    risk_score=risk,
    urgency="high"
)

# Notification sent to tech lead:
"""
🚨 HIGH-RISK Decision Requires Your Review

Decision: Migrate from PostgreSQL to MongoDB
Work Item: Multi-Tenant E-Commerce Platform
Risk Score: 0.95 (architecture, high cost, difficult to reverse)

Summary:
Agent proposes switching to MongoDB for better document handling.

Evidence:
- MongoDB flexible schema (3 sources, confidence 0.8)
- Performance benchmarks favor MongoDB (2 sources, confidence 0.7)

Concerns:
- Irreversible change (high migration cost)
- Team has PostgreSQL expertise
- ACID compliance requirements

Alternatives Considered:
- Keep PostgreSQL with JSONB (rejected by agent)

Your Decision Needed:
✅ Approve: Agent proceeds with MongoDB migration
❌ Reject: Agent stays with PostgreSQL
💬 Request More Info: Ask agent for additional analysis

SLA: Review within 24 hours
Review: https://aipm.app/reviews/rev_uuid_123
"""

# Tech lead reviews, rejects:
apm review reject rev_uuid_123 \
  --reason "ACID compliance required for transactions, PostgreSQL better fit" \
  --alternative "Use PostgreSQL JSONB for flexible fields"

# Agent receives:
# "❌ Decision rejected by tech-lead@company.com
#     Reason: ACID compliance required
#     Suggested: Use PostgreSQL JSONB
#     Next: Revise proposal or ask for clarification"
```

### Example 3: Escalation for Critical Decision

```python
# AI agent proposes: "Architectural redesign"
decision = Decision(
    title="Migrate to Microservices Architecture",
    decision="Split monolith into 15 microservices",
    rationale="Better scalability, team autonomy",
    confidence=0.65,  # Low confidence (big change)
    made_by="aipm-development-orchestrator"
)

# Risk scoring
risk = scorer.score_decision(decision)
# risk.overall = 0.98 (critical: entire architecture change)
# risk.review_level = "executive"

# Create review (critical urgency)
review = review_service.request_review(
    decision=decision,
    risk_score=risk,
    urgency="critical"  # 4-hour SLA
)

# Assigned to: CTO

# After 2 hours, no response → auto-escalate
if datetime.now() > review.requested_at + timedelta(hours=2):
    review_service.escalate_review(
        review_id=review.id,
        to="ceo@company.com",
        reason="SLA at risk, decision blocking critical path"
    )

# Ensures critical decisions never stuck
# But preserves human control
```

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Main specification
- **ADR-004**: Evidence Storage and Retrieval (evidence supports reviews)
- **ADR-005**: Multi-Provider Session Management (reviews across providers)
- **ADR-008**: Data Privacy and Security (sensitive decisions)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Risk-based review gating | Balance automation with control |
| 2025-10-12 | Multi-level review (peer/senior/exec) | Appropriate reviewer for risk level |
| 2025-10-12 | SLA-based escalation | Prevent stalled decisions |
| 2025-10-12 | Auto-approve <0.3 risk | Don't bottleneck low-risk work |
| 2025-10-12 | Learning from rejections | System improves from feedback |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype risk scoring
3. Test review workflow
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
