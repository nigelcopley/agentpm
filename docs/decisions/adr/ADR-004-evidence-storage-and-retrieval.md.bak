# ADR-004: Evidence Storage and Retrieval

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable traceable, evidence-based decision making with confidence scoring

---

## Context

### The Evidence Problem

Complex software development involves thousands of decisions:
- Architecture choices (microservices vs monolith)
- Technology selections (PostgreSQL vs MongoDB)
- Pattern adoptions (REST vs GraphQL)
- Implementation approaches (async vs sync)

**Current State: Decisions Without Evidence**
```
Decision Made: "Use PostgreSQL for database"
Rationale: "It's what we know"
Evidence: None
Confidence: Unknown
Sources: None

6 months later:
- Why PostgreSQL? "Someone decided that"
- What alternatives were considered? "Not sure"
- Can we switch to MongoDB? "Don't know the original reasoning"
- Who made this decision? "Can't remember"
```

**Result:**
- Decisions made on assumptions, not data
- No trace of alternatives considered
- Can't review or challenge decisions
- Knowledge lost when team members leave
- Repeated debates on settled questions

### Requirements for Enterprise Development

1. **Auditability**: Every decision traceable to evidence
2. **Confidence Scoring**: Know how certain we are
3. **Source Tracking**: Link to authoritative sources
4. **Evidence Verification**: Detect when evidence is outdated
5. **Compliance Ready**: Meet audit requirements (SOC 2, ISO 27001)

---

## Decision

We will implement an **Evidence-Based Decision System** with:

1. **Structured Evidence Storage**: Database-backed evidence entries
2. **Confidence Scoring**: Quantify certainty of decisions
3. **Source Classification**: Primary, secondary, internal sources
4. **Content Verification**: SHA256 hashing for integrity
5. **Temporal Tracking**: Capture when evidence was valid

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Evidence Database                       │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Decisions (What was decided)                        │ │
│  │  ├─ decision_id                                     │ │
│  │  ├─ work_item_id, task_id                          │ │
│  │  ├─ title, decision, rationale                      │ │
│  │  ├─ alternatives_considered: List[str]             │ │
│  │  ├─ made_by (agent/human), made_at                 │ │
│  │  ├─ confidence: float (0.0-1.0)                    │ │
│  │  └─ status: proposed | accepted | superseded       │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ Evidence Entries (Why we decided)                   │ │
│  │  ├─ evidence_id                                     │ │
│  │  ├─ decision_id (FK)                                │ │
│  │  ├─ source_url, source_type                        │ │
│  │  ├─ excerpt (≤25 words)                            │ │
│  │  ├─ captured_at, content_hash (SHA256)            │ │
│  │  ├─ confidence: float (source quality)             │ │
│  │  └─ relevance: float (to decision)                 │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ Sources (Where evidence came from)                  │ │
│  │  ├─ source_id                                       │ │
│  │  ├─ url, title, author                             │ │
│  │  ├─ source_type: primary | secondary | internal   │ │
│  │  ├─ credibility_score: float                       │ │
│  │  ├─ last_verified, verification_status             │ │
│  │  └─ access_method: web | API | local              │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────▼────┐    ┌───▼────┐    ┌───▼─────┐
    │ Capture │    │ Verify │    │  Query  │
    │         │    │        │    │         │
    │ • Web   │    │ • Hash │    │ • By    │
    │   fetch │    │   check│    │   decision│
    │ • API   │    │ • Link │    │ • By    │
    │   calls │    │   alive│    │   source│
    │ • Local │    │ • Conf.│    │ • By    │
    │   docs  │    │   score│    │   type  │
    └─────────┘    └────────┘    └─────────┘
```

### Evidence Data Model

```python
@dataclass
class Decision:
    """
    An architectural or implementation decision.

    Links to evidence that supports the decision.
    """

    # Identification
    id: str  # UUID
    work_item_id: int
    task_id: Optional[int]

    # Decision content
    title: str  # Short summary (≤50 words)
    decision: str  # What was decided
    rationale: str  # Why this decision was made
    alternatives_considered: List[str]  # What else was evaluated

    # Context
    context: str  # Circumstances that led to decision
    constraints: List[str]  # Limitations that influenced decision
    assumptions: List[str]  # Assumptions made

    # Metadata
    made_by: str  # Agent ID or human email
    made_at: datetime
    confidence: float  # 0.0-1.0 (aggregate from evidence)
    status: Literal["proposed", "accepted", "superseded"]

    # Relationships
    evidence_entries: List[EvidenceEntry]  # Supporting evidence
    supersedes: Optional[str]  # Previous decision ID
    superseded_by: Optional[str]  # Newer decision ID

    # Review
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]

@dataclass
class EvidenceEntry:
    """
    A piece of evidence supporting a decision.

    Can be from web sources, documentation, research papers,
    internal documents, or expert consultation.
    """

    # Identification
    id: str  # UUID
    decision_id: str  # FK to Decision
    source_id: str  # FK to Source

    # Content
    excerpt: str  # Key quote or finding (≤25 words)
    full_content_hash: str  # SHA256 of full content
    page_screenshot: Optional[str]  # Path to screenshot (for web)

    # Metadata
    captured_at: datetime
    captured_by: str  # Agent or human
    confidence: float  # How confident in this evidence (0.0-1.0)
    relevance: float  # How relevant to decision (0.0-1.0)

    # Verification
    verified: bool
    verified_at: Optional[datetime]
    verification_method: Optional[str]

@dataclass
class Source:
    """
    A source of information (URL, document, API, expert).
    """

    # Identification
    id: str  # UUID
    url: str  # Primary identifier
    title: str
    author: Optional[str]

    # Classification
    source_type: Literal[
        "primary",    # Official docs, research papers, specs
        "secondary",  # Blog posts, tutorials, Stack Overflow
        "internal"    # Internal docs, team knowledge, code
    ]

    # Credibility
    credibility_score: float  # 0.0-1.0
    credibility_rationale: str
    last_verified: datetime
    verification_status: Literal["verified", "stale", "broken"]

    # Access
    access_method: Literal["web", "api", "local", "expert"]
    access_credentials: Optional[Dict[str, str]]
```

### Confidence Scoring System

```python
class ConfidenceCalculator:
    """
    Calculate confidence scores for decisions based on evidence.

    Factors:
    1. Number of evidence entries (more = higher confidence)
    2. Source credibility (official docs > blog posts)
    3. Evidence recency (newer = more reliable)
    4. Evidence convergence (multiple sources agree)
    5. Decision maker expertise (experienced agent/human)
    """

    def calculate_decision_confidence(self, decision: Decision) -> float:
        """
        Calculate overall confidence in a decision.

        Formula:
        confidence = (
            evidence_quantity_score * 0.2 +
            source_credibility_score * 0.3 +
            evidence_recency_score * 0.15 +
            evidence_convergence_score * 0.25 +
            decision_maker_score * 0.1
        )

        Returns: float 0.0-1.0
        """

        # 1. Evidence quantity (diminishing returns after 5 sources)
        quantity_score = min(len(decision.evidence_entries) / 5.0, 1.0)

        # 2. Source credibility (weighted average)
        credibility_scores = [
            e.source.credibility_score * e.relevance
            for e in decision.evidence_entries
        ]
        credibility_score = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.0

        # 3. Evidence recency (decay over time)
        now = datetime.now()
        recency_scores = []
        for evidence in decision.evidence_entries:
            age_days = (now - evidence.captured_at).days
            # Decay: 100% fresh, 50% after 90 days, 25% after 180 days
            recency = max(0.25, 1.0 - (age_days / 180.0) * 0.75)
            recency_scores.append(recency)
        recency_score = sum(recency_scores) / len(recency_scores) if recency_scores else 0.0

        # 4. Evidence convergence (do sources agree?)
        convergence_score = self._calculate_convergence(decision.evidence_entries)

        # 5. Decision maker score
        maker_score = self._get_maker_credibility(decision.made_by)

        # Weighted average
        confidence = (
            quantity_score * 0.2 +
            credibility_score * 0.3 +
            recency_score * 0.15 +
            convergence_score * 0.25 +
            maker_score * 0.1
        )

        return round(confidence, 2)

    def _calculate_convergence(self, evidence_entries: List[EvidenceEntry]) -> float:
        """
        Measure if evidence entries agree with each other.

        High convergence: All sources say similar things
        Low convergence: Sources contradict each other
        """
        if len(evidence_entries) < 2:
            return 1.0  # Single source = no contradiction

        # Use semantic similarity of excerpts
        # For now, simple heuristic: longer shared keywords = higher convergence
        excerpts = [e.excerpt.lower() for e in evidence_entries]

        # Count shared words (simple approach)
        all_words = set()
        for excerpt in excerpts:
            all_words.update(excerpt.split())

        # Calculate overlap
        overlaps = []
        for i, excerpt1 in enumerate(excerpts):
            for excerpt2 in excerpts[i+1:]:
                words1 = set(excerpt1.split())
                words2 = set(excerpt2.split())
                overlap = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
                overlaps.append(overlap)

        return sum(overlaps) / len(overlaps) if overlaps else 0.5

    def _get_maker_credibility(self, made_by: str) -> float:
        """
        Score credibility of decision maker.

        - Senior agents: 0.9
        - Standard agents: 0.8
        - Human experts: 1.0
        - Human non-experts: 0.7
        """
        # Look up from agent registry or user database
        # For now, simple mapping
        credibility_map = {
            "aipm-owner": 1.0,
            "aipm-team-leader": 0.9,
            "aipm-development-orchestrator": 0.9,
            "aipm-database-developer": 0.8,
            "aipm-python-cli-developer": 0.8,
            # ... etc
        }
        return credibility_map.get(made_by, 0.7)
```

### Evidence Capture System

```python
class EvidenceCaptureService:
    """
    Captures evidence from various sources.
    """

    def capture_web_evidence(
        self,
        url: str,
        excerpt: str,
        decision_id: str
    ) -> EvidenceEntry:
        """
        Capture evidence from web source.

        Steps:
        1. Fetch page content
        2. Take screenshot (for verification)
        3. Calculate content hash (SHA256)
        4. Extract metadata (title, author, date)
        5. Assess credibility
        6. Create evidence entry

        Example:
        capture_web_evidence(
            url="https://www.postgresql.org/docs/current/mvcc-intro.html",
            excerpt="PostgreSQL provides true MVCC with no read locks",
            decision_id="dec_uuid_123"
        )
        """

        # Fetch content
        response = requests.get(url)
        content = response.text

        # Take screenshot
        screenshot_path = self._capture_screenshot(url)

        # Calculate hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Extract metadata
        metadata = self._extract_metadata(content)

        # Get or create source
        source = self._get_or_create_source(
            url=url,
            title=metadata['title'],
            author=metadata.get('author'),
            source_type=self._classify_source_type(url)
        )

        # Create evidence
        evidence = EvidenceEntry(
            id=generate_uuid(),
            decision_id=decision_id,
            source_id=source.id,
            excerpt=excerpt,
            full_content_hash=content_hash,
            page_screenshot=screenshot_path,
            captured_at=datetime.now(),
            captured_by=get_current_agent(),
            confidence=source.credibility_score,
            relevance=0.9,  # Assume high relevance (can be refined)
            verified=True,
            verified_at=datetime.now(),
            verification_method="web_fetch"
        )

        db.add(evidence)
        db.commit()

        return evidence

    def capture_internal_evidence(
        self,
        document_path: str,
        excerpt: str,
        decision_id: str
    ) -> EvidenceEntry:
        """
        Capture evidence from internal documentation.

        Example:
        capture_internal_evidence(
            document_path="docs/architecture/database-decision.md",
            excerpt="Team agreed on PostgreSQL for ACID guarantees",
            decision_id="dec_uuid_123"
        )
        """

    def capture_api_evidence(
        self,
        api_url: str,
        query: Dict[str, Any],
        excerpt: str,
        decision_id: str
    ) -> EvidenceEntry:
        """
        Capture evidence from API calls (e.g., GitHub API, library docs API).

        Example:
        capture_api_evidence(
            api_url="https://api.github.com/repos/django/django/issues",
            query={"state": "closed", "labels": "database"},
            excerpt="Django team closed 15 issues related to PostgreSQL",
            decision_id="dec_uuid_123"
        )
        """
```

### Evidence Verification System

```python
class EvidenceVerificationService:
    """
    Verifies evidence is still valid and accessible.
    """

    def verify_evidence(self, evidence: EvidenceEntry) -> VerificationResult:
        """
        Verify evidence is still valid.

        Checks:
        1. Source still accessible
        2. Content hasn't changed (hash match)
        3. Source still credible
        4. Evidence still relevant

        Returns: VerificationResult with status and details
        """

        # 1. Check source accessibility
        try:
            response = requests.get(evidence.source.url, timeout=10)
            accessible = response.status_code == 200
        except Exception as e:
            accessible = False
            return VerificationResult(
                verified=False,
                reason=f"Source not accessible: {e}",
                recommended_action="REMOVE or FIND_ALTERNATIVE"
            )

        # 2. Check content hash
        current_content = response.text
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()

        if current_hash != evidence.full_content_hash:
            return VerificationResult(
                verified=False,
                reason="Content changed since capture",
                recommended_action="REVIEW_CHANGES or RECAPTURE"
            )

        # 3. Check source credibility (may degrade over time)
        current_credibility = self._assess_source_credibility(evidence.source)
        if current_credibility < 0.5:
            return VerificationResult(
                verified=False,
                reason="Source credibility degraded",
                recommended_action="FIND_BETTER_SOURCE"
            )

        # 4. Check relevance (with current decision context)
        decision = db.query(Decision).get(evidence.decision_id)
        relevance = self._assess_relevance(evidence, decision)
        if relevance < 0.5:
            return VerificationResult(
                verified=False,
                reason="Evidence no longer relevant",
                recommended_action="UPDATE_DECISION"
            )

        # All checks passed
        evidence.verified = True
        evidence.verified_at = datetime.now()
        db.commit()

        return VerificationResult(
            verified=True,
            reason="All verification checks passed",
            recommended_action="NONE"
        )

    def verify_all_evidence_for_decision(self, decision_id: str):
        """
        Verify all evidence entries for a decision.

        Use case: Periodic verification (monthly)
        """
        evidence_entries = db.query(EvidenceEntry).filter(
            EvidenceEntry.decision_id == decision_id
        ).all()

        results = []
        for evidence in evidence_entries:
            result = self.verify_evidence(evidence)
            results.append(result)

            if not result.verified:
                # Log for review
                log_verification_failure(evidence, result)

        return results
```

---

## Consequences

### Positive

1. **Full Auditability**
   - Every decision linked to evidence
   - Can answer "why did we decide X?"
   - Compliance ready (SOC 2, ISO 27001)

2. **Confidence Quantification**
   - Know how certain we are
   - Flag low-confidence decisions for review
   - Prioritize evidence gathering

3. **Knowledge Preservation**
   - Decisions survive team changes
   - Rationale never lost
   - Onboarding easier (read decision history)

4. **Better Decisions**
   - Evidence-based, not gut-feel
   - Alternatives explicitly considered
   - Assumptions documented

5. **Continuous Validation**
   - Evidence verification detects staleness
   - Can update decisions when evidence changes
   - Living documentation

### Negative

1. **Evidence Capture Overhead**
   - Takes time to document evidence
   - Requires discipline from agents/humans
   - May slow down decision-making

2. **Storage Requirements**
   - Screenshots, full content hashes
   - Grows over time
   - May require archival strategy

3. **Verification Maintenance**
   - Web sources go stale
   - Links break
   - Requires periodic re-verification

4. **Confidence Calculation Complexity**
   - Many factors to consider
   - Subjectivity in scoring
   - May disagree with human judgment

### Mitigation Strategies

1. **Evidence Capture Automation**
   - Auto-capture when AI queries web
   - Browser extensions for humans
   - CLI commands for quick capture
   - Template-based capture

2. **Storage Optimization**
   - Compress screenshots
   - Archive old evidence
   - Deduplicate sources
   - S3/cloud storage for binaries

3. **Verification Automation**
   - Scheduled verification jobs
   - Alert when evidence fails
   - Auto-update credibility scores
   - Community verification (crowdsourced)

4. **Confidence Calibration**
   - A/B test confidence vs outcomes
   - Human feedback on confidence accuracy
   - Tune weights based on results
   - Override mechanism for humans

---

## Implementation Plan

### Phase 1: Core Models & Storage (Week 1-2)

```yaml
Week 1: Database Schema
  Tasks:
    - Create decisions table
    - Create evidence_entries table
    - Create sources table
    - Add indices for performance

  Deliverables:
    - Migration: 0017_add_evidence_system.py
    - Models: Decision, EvidenceEntry, Source
    - Tests: test_evidence_models.py

  Success Criteria:
    - All CRUD operations work
    - Queries perform <100ms
    - Relationships correct

Week 2: Confidence Scoring
  Tasks:
    - Implement ConfidenceCalculator
    - Test scoring algorithm
    - Calibrate weights
    - Add confidence to decisions

  Deliverables:
    - agentpm/core/evidence/confidence.py
    - Confidence calculation tests-BAK
    - Calibration report

  Success Criteria:
    - Confidence scores 0.0-1.0
    - Scores correlate with decision quality
    - Weights validated
```

### Phase 2: Evidence Capture (Week 3-4)

```yaml
Week 3: Capture System
  Tasks:
    - Implement EvidenceCaptureService
    - Web evidence capture (with screenshots)
    - Internal document capture
    - API evidence capture

  Deliverables:
    - agentpm/core/evidence/capture.py
    - Screenshot service
    - Metadata extraction
    - Capture CLI commands

  Success Criteria:
    - Can capture from web, files, APIs
    - Screenshots captured correctly
    - Content hashes calculated

Week 4: Agent Integration
  Tasks:
    - Update agents to capture evidence
    - Auto-capture when making decisions
    - Evidence templates for common sources
    - CLI commands for manual capture

  Deliverables:
    - Agent evidence capture hooks
    - Evidence templates
    - CLI: apm evidence capture
    - Documentation

  Success Criteria:
    - Agents automatically capture evidence
    - Humans can easily add evidence
    - Common sources have templates
```

### Phase 3: Verification (Week 5-6)

```yaml
Week 5: Verification System
  Tasks:
    - Implement EvidenceVerificationService
    - Hash verification
    - Source accessibility checks
    - Credibility assessment

  Deliverables:
    - agentpm/core/evidence/verification.py
    - Verification scheduler
    - CLI: apm evidence verify
    - Verification reports

  Success Criteria:
    - Can verify all evidence types
    - Detects stale/broken evidence
    - Verification <1s per evidence

Week 6: Automated Verification
  Tasks:
    - Scheduled verification jobs
    - Alert system for failures
    - Auto-update evidence status
    - Verification dashboard

  Deliverables:
    - Cron job / background worker
    - Alert system
    - Dashboard (CLI)
    - Metrics tracking

  Success Criteria:
    - Runs daily automatically
    - Alerts when evidence fails
    - Dashboard shows health
```

### Phase 4: Reporting & Analysis (Week 7-8)

```yaml
Week 7: Decision Reports
  Tasks:
    - Generate decision audit reports
    - Confidence trend analysis
    - Evidence coverage reports
    - Compliance reports

  Deliverables:
    - Report generation service
    - CLI: apm evidence report
    - Report templates (PDF, HTML)
    - Metrics dashboard

  Success Criteria:
    - Can generate audit reports
    - Reports show confidence trends
    - Compliance-ready format

Week 8: Integration Testing
  Tasks:
    - E2E evidence capture → verification → reporting
    - Multi-provider testing
    - Performance testing
    - Load testing

  Deliverables:
    - E2E test suite
    - Performance benchmarks
    - Load test results
    - Documentation

  Success Criteria:
    - All workflows work
    - Performance targets met
    - Scales to 1000s of decisions
```

---

## Usage Examples

### Example 1: Technology Decision with Evidence

```python
from agentpm.core.evidence import EvidenceCaptureService, ConfidenceCalculator

# Step 1: Make decision
decision = Decision(
    id=generate_uuid(),
    work_item_id=5,
    title="Database Selection: PostgreSQL vs MongoDB",
    decision="Use PostgreSQL for primary database",
    rationale="""
    PostgreSQL chosen for:
    1. ACID compliance (critical for e-commerce)
    2. Mature ecosystem and tooling
    3. Better fit for relational data model
    4. Team expertise
    """,
    alternatives_considered=[
        "MongoDB: Rejected due to lack of true ACID before v4.0",
        "MySQL: Rejected due to weaker JSON support",
        "CockroachDB: Rejected due to limited team expertise"
    ],
    context="Multi-tenant e-commerce platform with complex relationships",
    constraints=[
        "Must support 10,000+ tenants",
        "Must handle complex queries",
        "Must integrate with Django ORM"
    ],
    assumptions=[
        "Traffic will be read-heavy (90% reads)",
        "Most tenants will have <10K records",
        "Need strong consistency over eventual consistency"
    ],
    made_by="aipm-database-developer",
    made_at=datetime.now(),
    status="proposed"
)

# Step 2: Capture evidence
capture = EvidenceCaptureService()

# Evidence 1: Official PostgreSQL docs
evidence1 = capture.capture_web_evidence(
    url="https://www.postgresql.org/docs/current/mvcc-intro.html",
    excerpt="PostgreSQL provides true MVCC with no read locks",
    decision_id=decision.id
)

# Evidence 2: Django compatibility
evidence2 = capture.capture_web_evidence(
    url="https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes",
    excerpt="Django has best support for PostgreSQL features",
    decision_id=decision.id
)

# Evidence 3: Internal team expertise
evidence3 = capture.capture_internal_evidence(
    document_path="docs/team/skills-matrix.md",
    excerpt="5/7 backend engineers have PostgreSQL experience",
    decision_id=decision.id
)

# Evidence 4: Performance benchmarks
evidence4 = capture.capture_web_evidence(
    url="https://www.postgresql.org/about/news/benchmarks",
    excerpt="PostgreSQL handles 100K+ transactions/sec on modest hardware",
    decision_id=decision.id
)

# Step 3: Calculate confidence
calculator = ConfidenceCalculator()
confidence = calculator.calculate_decision_confidence(decision)

decision.confidence = confidence  # e.g., 0.87
decision.status = "accepted"
db.add(decision)
db.commit()

print(f"Decision confidence: {confidence:.2f}")
print(f"Based on {len(decision.evidence_entries)} evidence sources")
```

### Example 2: Reviewing Old Decisions

```python
from agentpm.core.evidence import EvidenceVerificationService

# 6 months later: Review PostgreSQL decision
decision = db.query(Decision).filter(
    Decision.title.contains("PostgreSQL")
).first()

print(f"Original decision: {decision.decision}")
print(f"Made: {decision.made_at}")
print(f"Original confidence: {decision.confidence:.2f}")

# Verify evidence is still valid
verifier = EvidenceVerificationService()
results = verifier.verify_all_evidence_for_decision(decision.id)

print(f"\nEvidence verification:")
for i, result in enumerate(results, 1):
    print(f"{i}. {'✅' if result.verified else '❌'} {result.reason}")
    if not result.verified:
        print(f"   Action: {result.recommended_action}")

# Recalculate confidence with current evidence
new_confidence = calculator.calculate_decision_confidence(decision)
print(f"\nConfidence change: {decision.confidence:.2f} → {new_confidence:.2f}")

if new_confidence < 0.6:
    print("⚠️  Low confidence - consider reviewing decision")
```

### Example 3: Compliance Audit Report

```python
from agentpm.core.evidence import generate_audit_report

# Generate compliance report for work item
report = generate_audit_report(
    work_item_id=5,
    report_type="compliance",
    format="pdf"
)

# Report includes:
# - All decisions made
# - Evidence for each decision
# - Confidence scores
# - Verification status
# - Decision timeline
# - Alternative considerations
# - Current status

print(f"Audit report generated: {report.path}")
print(f"Decisions covered: {report.decision_count}")
print(f"Average confidence: {report.avg_confidence:.2f}")
print(f"Evidence entries: {report.evidence_count}")
print(f"Verified evidence: {report.verified_evidence_count}")
```

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Overall system
- **ADR-001**: Provider Abstraction Architecture
- **ADR-002**: Context Compression Strategy
- **ADR-003**: Sub-Agent Communication Protocol
- **ADR-005**: Multi-Provider Session Management

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Structured evidence storage in database | Queryable, auditable, persistent |
| 2025-10-12 | Confidence scoring required | Quantify decision quality |
| 2025-10-12 | SHA256 content hashing | Detect evidence changes |
| 2025-10-12 | Screenshot capture for web evidence | Visual verification |
| 2025-10-12 | Three-tier source classification | Clear credibility hierarchy |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype evidence capture for one decision
3. Test confidence calculation accuracy
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
