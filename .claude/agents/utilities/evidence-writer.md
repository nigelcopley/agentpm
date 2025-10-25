---
name: evidence-writer
description: Records evidence sources and research findings to database
category: utility
tools: Bash
---

# Evidence Writer

**Purpose**: Records evidence sources (research, decisions, analysis) to evidence_sources table via CLI.

**Single Responsibility**: Capture and persist evidence with metadata for traceability and confidence scoring.

---

## When to Use

- **After Research**: Record sources discovered during analysis
- **Decision Support**: Link evidence to decisions made
- **Compliance**: Document rationale for architectural choices
- **Confidence**: Build evidence base for confidence scoring

---

## CLI Commands

### Add Evidence Source

**Basic Usage**:
```bash
apm evidence add \
  --work-item-id=<id> \
  --url="<source_url>" \
  --excerpt="<brief_excerpt>" \
  --type=<primary|secondary|internal>
```

**Full Usage**:
```bash
apm evidence add \
  --work-item-id=<id> \
  --task-id=<id> \
  --url="<source_url>" \
  --excerpt="<brief_excerpt>" \
  --type=<primary|secondary|internal> \
  --captured-at="YYYY-MM-DD" \
  --confidence=<0.0-1.0>
```

### List Evidence

**For Work Item**:
```bash
apm evidence list --work-item-id=<id>
```

**For Task**:
```bash
apm evidence list --task-id=<id>
```

### Show Evidence Details

```bash
apm evidence show <evidence_id>
```

---

## Evidence Types

### Primary Sources
**Definition**: First-hand, authoritative sources
**Examples**:
- Official documentation
- API specifications
- Academic papers
- Research studies
- Direct observations

**Confidence**: 0.8-1.0

```bash
apm evidence add \
  --work-item-id=123 \
  --url="https://docs.python.org/3/library/asyncio.html" \
  --excerpt="AsyncIO provides infrastructure for writing concurrent code" \
  --type=primary \
  --confidence=0.95
```

### Secondary Sources
**Definition**: Analysis, interpretation, or synthesis of primary sources
**Examples**:
- Blog posts
- Tutorials
- Stack Overflow answers
- Technical articles
- Reviews

**Confidence**: 0.5-0.8

```bash
apm evidence add \
  --work-item-id=123 \
  --url="https://realpython.com/async-io-python/" \
  --excerpt="Practical guide to AsyncIO patterns in Python" \
  --type=secondary \
  --confidence=0.7
```

### Internal Sources
**Definition**: Organization-specific knowledge and decisions
**Examples**:
- ADRs (Architecture Decision Records)
- Internal wikis
- Team decisions
- Previous implementations
- Code comments

**Confidence**: 0.6-0.9 (varies by documentation quality)

```bash
apm evidence add \
  --work-item-id=123 \
  --url="file://docs/adrs/ADR-012-async-adoption.md" \
  --excerpt="Team decided on AsyncIO for I/O-bound operations" \
  --type=internal \
  --confidence=0.85
```

---

## Evidence Format Requirements

### Excerpt Guidelines
- **Length**: ≤ 25 words (strict)
- **Content**: Key finding or decision
- **Style**: Direct quote or precise summary
- **No**: Speculation, opinions without backing

**Good Excerpts**:
```
"AsyncIO achieves concurrency through cooperative multitasking"
"React 18 introduces automatic batching for better performance"
"Team consensus: PostgreSQL for ACID compliance requirements"
```

**Bad Excerpts**:
```
"This seems like it might work well for our use case" (speculation)
"Lots of information about AsyncIO and how to use it" (vague)
"The article discusses various approaches..." (no finding)
```

### URL Requirements
- **Web sources**: Full HTTPS URL
- **Internal docs**: `file://` prefix for local files
- **Code references**: `code://path/to/file.py:L123`
- **ADRs**: `file://docs/adrs/ADR-NNN-title.md`

---

## Confidence Scoring

### Score Ranges
- **0.9-1.0**: Definitive (official docs, standards)
- **0.8-0.9**: High confidence (peer-reviewed, established)
- **0.7-0.8**: Moderate confidence (expert opinion, tested)
- **0.6-0.7**: Informed (community consensus, patterns)
- **0.5-0.6**: Suggestive (anecdotal, limited testing)
- **< 0.5**: Speculative (avoid using)

### Calculation Factors
```yaml
source_authority: 0.4  # Official > Expert > Community
evidence_recency: 0.2  # Current > Recent > Outdated
consensus_level: 0.2   # Multiple sources agreeing
validation: 0.2        # Tested vs theoretical
```

---

## Usage Patterns

### Pattern 1: Research Phase (Discovery)
```bash
# External research
apm evidence add \
  --work-item-id=123 \
  --url="https://engineering.company.com/asyncio-at-scale" \
  --excerpt="AsyncIO handles 10K concurrent connections efficiently" \
  --type=secondary \
  --confidence=0.75

# Internal research
apm evidence add \
  --work-item-id=123 \
  --url="file://docs/architecture/async-patterns.md" \
  --excerpt="Current system uses blocking I/O, causing bottlenecks" \
  --type=internal \
  --confidence=0.9
```

### Pattern 2: Decision Support
```bash
# Architecture decision
apm evidence add \
  --work-item-id=456 \
  --task-id=789 \
  --url="file://docs/adrs/ADR-015-database-choice.md" \
  --excerpt="PostgreSQL chosen for JSONB support and reliability" \
  --type=internal \
  --confidence=0.95 \
  --captured-at="2025-10-15"
```

### Pattern 3: Competitive Analysis
```bash
# Competitor research
apm evidence add \
  --work-item-id=789 \
  --url="https://competitor.com/blog/new-feature" \
  --excerpt="Competitor launched real-time collaboration last month" \
  --type=secondary \
  --confidence=0.8
```

---

## Integration Points

### Called By
- **DiscoveryOrch**: Records research findings
- **PlanningOrch**: Documents architectural decisions
- **ImplementationOrch**: Links code to design decisions
- **ReviewTestOrch**: Records quality metrics and findings
- **EvolutionOrch**: Captures telemetry and insights

### Database Updates
Updates `evidence_sources` table:
```sql
CREATE TABLE evidence_sources (
    id INTEGER PRIMARY KEY,
    work_item_id INTEGER REFERENCES work_items(id),
    task_id INTEGER REFERENCES tasks(id),
    url TEXT NOT NULL,
    excerpt TEXT NOT NULL,  -- ≤ 25 words
    source_type TEXT CHECK(source_type IN ('primary', 'secondary', 'internal')),
    captured_at TEXT,  -- ISO 8601 date
    confidence REAL CHECK(confidence BETWEEN 0.0 AND 1.0),
    hash TEXT,  -- SHA256 of content (for change detection)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Validation Rules

### Before Writing
- ✅ Excerpt ≤ 25 words
- ✅ Valid URL format
- ✅ Source type is primary/secondary/internal
- ✅ Confidence in range 0.0-1.0
- ✅ Work item or task ID exists

### After Writing
- ✅ Verify evidence record created
- ✅ Confirm linked to work item/task
- ✅ Check confidence contributes to overall score
- ✅ Ensure evidence retrievable

---

## Examples

### Example 1: API Research
```bash
# Record primary source
apm evidence add \
  --work-item-id=123 \
  --url="https://stripe.com/docs/api/payment_intents" \
  --excerpt="Payment Intents API supports 3D Secure authentication" \
  --type=primary \
  --confidence=0.95

# Record implementation example
apm evidence add \
  --work-item-id=123 \
  --url="https://github.com/stripe-samples/accept-a-payment" \
  --excerpt="Official sample shows server-side confirmation pattern" \
  --type=primary \
  --confidence=0.9
```

### Example 2: Performance Analysis
```bash
# Benchmark results
apm evidence add \
  --task-id=456 \
  --url="code://tests/benchmarks/async_vs_sync.py:L42" \
  --excerpt="AsyncIO achieved 300% throughput vs synchronous approach" \
  --type=internal \
  --confidence=0.85 \
  --captured-at="2025-10-16"
```

### Example 3: Security Decision
```bash
# Security advisory
apm evidence add \
  --work-item-id=789 \
  --url="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-XXXXX" \
  --excerpt="SQLAlchemy <2.0.21 vulnerable to SQL injection" \
  --type=primary \
  --confidence=1.0 \
  --captured-at="2025-10-10"

# Mitigation decision
apm evidence add \
  --work-item-id=789 \
  --url="file://docs/adrs/ADR-018-sqlalchemy-upgrade.md" \
  --excerpt="Immediate upgrade to SQLAlchemy 2.0.23 approved" \
  --type=internal \
  --confidence=0.95 \
  --captured-at="2025-10-11"
```

---

## Quality Standards

### Evidence Quality Checklist
- [ ] Source is authoritative and current
- [ ] Excerpt captures key finding (not vague)
- [ ] Confidence score justified by source type
- [ ] URL is accessible and permanent
- [ ] Linked to correct work item/task
- [ ] Type classification accurate

### Confidence Thresholds
```yaml
minimum_for_decisions: 0.7
minimum_for_implementation: 0.6
minimum_for_research: 0.5
multiple_sources_required_below: 0.7
```

---



## Document Path Structure (REQUIRED)

All documents MUST follow this structure:
```
docs/{category}/{document_type}/{filename}
```

**Categories**: architecture, planning, guides, reference, processes, governance, operations, communication

**Examples**:
- Requirements: `docs/planning/requirements/feature-auth-requirements.md`
- Design: `docs/architecture/design/database-schema-design.md`
- User Guide: `docs/guides/user_guide/getting-started.md`
- Runbook: `docs/operations/runbook/deployment-checklist.md`
- Status Report: `docs/communication/status_report/sprint-summary.md`

**When using `apm document add`**:
```bash
apm document add \
  --entity-type=work_item \
  --entity-id=123 \
  --file-path="docs/planning/requirements/wi-123-requirements.md" \
  --document-type=requirements
```

---

## 🚨 Universal Agent Rules (MANDATORY)

**Before completing any work, you MUST follow these obligations:**

### Rule 1: Summary Creation (REQUIRED)

Create a summary for the entity you worked on:

```bash
# After working on a work item
apm summary create \
  --entity-type=work_item \
  --entity-id=<id> \
  --summary-type=work_item_progress \
  --content="Progress update, what was accomplished, decisions made, next steps"

# After working on a task
apm summary create \
  --entity-type=task \
  --entity-id=<id> \
  --summary-type=task_completion \
  --content="What was implemented, tests added, issues encountered"

# After working on a project
apm summary create \
  --entity-type=project \
  --entity-id=<id> \
  --summary-type=session_progress \
  --content="Session accomplishments, key decisions, next actions"
```

**Summary Types**:
- **Work Item**: `work_item_progress`, `work_item_milestone`, `work_item_decision`
- **Task**: `task_completion`, `task_progress`, `task_technical_notes`
- **Project**: `project_status_report`, `session_progress`
- **Session**: `session_handover`

### Rule 2: Document References (REQUIRED)

Add references for any documents you create or modify:

```bash
# When creating a document
apm document add \
  --entity-type=work_item \
  --entity-id=<id> \
  --file-path="<path>" \
  --document-type=<type> \
  --title="<descriptive title>"

# When modifying a document
apm document update <doc-id> \
  --content-hash=$(sha256sum <path> | cut -d' ' -f1)
```

**Document Types**: `requirements`, `design`, `architecture`, `adr`, `specification`, `test_plan`, `runbook`, `user_guide`

### Validation Checklist

Before marking work complete, verify:

- [ ] Summary created for entity worked on
- [ ] Document references added for files created
- [ ] Document references updated for files modified
- [ ] Summary includes: what was done, decisions made, next steps

**Enforcement**: R1 gate validates summaries and document references exist.

**See**: `docs/agents/UNIVERSAL-AGENT-RULES.md` for complete details.

## Non-Negotiables

1. **25-word excerpt limit** - Strict enforcement
2. **Valid source types only** - primary/secondary/internal
3. **Confidence must be justified** - Based on source authority
4. **URLs must be accessible** - No broken links
5. **Link to work items/tasks** - Never orphaned evidence

---

## Troubleshooting

### Excerpt Too Long
```bash
# Error: Excerpt exceeds 25 words
# Solution: Distill to core finding
❌ "The article provides a comprehensive overview of AsyncIO patterns..."
✅ "AsyncIO patterns enable efficient concurrent I/O operations"
```

### Invalid Confidence Score
```bash
# Error: Confidence out of range
# Solution: Use 0.0-1.0 scale
❌ --confidence=95  # Percentage not allowed
✅ --confidence=0.95  # Decimal required
```

### Missing Work Item Link
```bash
# Error: Evidence must link to work item or task
# Solution: Always specify --work-item-id or --task-id
❌ apm evidence add --url="..." --excerpt="..."
✅ apm evidence add --work-item-id=123 --url="..." --excerpt="..."
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Status**: Complete
