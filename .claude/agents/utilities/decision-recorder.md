---
name: decision-recorder
description: Records decisions, architectural choices, and rationale using summary system
category: utility
tools: Bash, Write
---

# Decision Recorder

**Purpose**: Creates immutable record of decisions, architectural choices, and rationale using the summary system.

**Single Responsibility**: Record "why" decisions were made for future reference and compliance.

---

## When to Use

- **Architectural Decisions**: Why a pattern or technology was chosen
- **Trade-off Decisions**: Why one approach over alternatives
- **Risk Acceptances**: Why risks were deemed acceptable
- **Scope Changes**: Why requirements changed
- **Technical Debt**: Why shortcuts were taken (with payback plan)

---

## CLI Commands (Using Summary System)

### Create Decision Record

**For Work Items**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=<id> \
  --summary-type=decision \
  --content="<decision summary>" \
  --metadata='{"decision_type": "architecture|technical|business|risk|scope", "rationale": "...", "alternatives_considered": [...]}'
```

**For Tasks**:
```bash
apm summary create \
  --entity-type=task \
  --entity-id=<id> \
  --summary-type=decision \
  --content="<decision summary>"
```

**For Sessions** (Key Decisions):
```bash
apm session add-decision "<decision>" \
  --rationale "<why>"
```

### List Decision Records

```bash
# All decisions for work item
apm summary list --entity-type=work-item --entity-id=<id> --summary-type=decision

# All decisions for task
apm summary list --entity-type=task --entity-id=<id> --summary-type=decision

# Search decisions
apm summary search "<keyword>" --entity-type=work-item

# Session decisions
apm session show <session-id>
```

### Show Decision Details

```bash
apm summary show <summary-id>
```

---

## Decision Record Format

### Minimal Decision (via CLI)
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=123 \
  --summary-type=decision \
  --content="Use PostgreSQL instead of MongoDB for ACID guarantees and relational integrity" \
  --metadata='{"decision_type": "architecture", "made_by": "planning-orch", "review_date": "2026-01-17"}'
```

### Detailed Decision (via Markdown File)
Create in `docs/decisions/` directory:

```markdown
---
id: DECISION-2025-10-17-001
timestamp: 2025-10-17T14:23:00Z
work_item_id: 123
decision_type: architecture
made_by: planning-orch
---

# Decision: PostgreSQL over MongoDB

## Context
Need database for structured project data with relationships.

## Options Considered

1. **PostgreSQL**: Relational, ACID, proven
   - Pros: ACID guarantees, JSONB for flexibility, team expertise
   - Cons: Less schema flexibility, requires migrations
   - Confidence: 0.9

2. **MongoDB**: Document, flexible schema, NoSQL
   - Pros: Flexible schema, scalable
   - Cons: No ACID guarantees, learning curve
   - Confidence: 0.7

## Decision Rationale

PostgreSQL chosen for:
- ACID guarantees for work item relationships
- JSONB supports flexible metadata
- Team expertise (3/5 developers)
- Mature ecosystem

## Trade-offs Accepted

- Less schema flexibility than MongoDB
- Requires migrations for schema changes

## Risks

- Migration complexity (Mitigation: Alembic)
- Performance at scale (Mitigation: Indexing strategy)

## Success Criteria

- Sub-100ms query response times
- Zero data corruption
- Easy schema evolution

## Review Date

2026-01-17 (3 months - assess if benefits realized)

## Evidence

- [RabbitMQ vs Kafka comparison](link)
- [Event-driven patterns guide](link)
- [Team experience assessment](link)
```

Then link it:
```bash
apm document add \
  --entity-type=work-item \
  --entity-id=123 \
  --file-path="docs/decisions/DECISION-2025-10-17-001.md" \
  --type=adr \
  --title="Database Choice: PostgreSQL"
```

---

## Decision Types

### Architecture Decisions
**When**: Major structural choices

**Example**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=123 \
  --summary-type=decision \
  --content="Use event-driven architecture for service communication. Decouples services, enables async processing, supports future scaling." \
  --metadata='{"decision_type": "architecture", "alternatives": ["synchronous HTTP", "GraphQL federation"], "chosen": "event-driven", "rationale": "Best balance of decoupling and team expertise"}'
```

### Technical Decisions
**When**: Implementation choices

**Example**:
```bash
apm summary create \
  --entity-type=task \
  --entity-id=456 \
  --summary-type=decision \
  --content="Use AsyncIO for concurrent API calls. 300% throughput improvement in benchmarks." \
  --metadata='{"decision_type": "technical", "benchmark_results": "300% improvement", "made_by": "code-implementer"}'
```

### Business Decisions
**When**: Requirements or scope changes

**Example**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=789 \
  --summary-type=decision \
  --content="Defer real-time notifications to v2. Focuses MVP on core workflow, reduces time-to-market by 3 weeks." \
  --metadata='{"decision_type": "business", "timeline_impact": "-3 weeks", "scope_change": "deferred", "made_by": "definition-orch"}'
```

### Risk Decisions
**When**: Accepting or mitigating risks

**Example**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=101 \
  --summary-type=decision \
  --content="Accept eventual consistency for analytics data. 1-minute lag acceptable, avoids distributed transactions." \
  --metadata='{"decision_type": "risk", "severity": "MEDIUM", "mitigation": "Monitoring dashboard, user expectations set", "made_by": "planning-orch"}'
```

### Scope Decisions
**When**: Changing what's included

**Example**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=202 \
  --summary-type=decision \
  --content="Limit initial auth to email/password only. OAuth adds 2-week timeline, not critical for beta." \
  --metadata='{"decision_type": "scope", "deferred_features": ["OAuth"], "timeline_savings": "2 weeks", "made_by": "definition-orch"}'
```

---

## Session-Level Decisions

For quick decision capture during work sessions:

```bash
# Add key decision to current session
apm session add-decision "Use Pydantic for validation" \
  --rationale "Type safety and better error messages than manual validation"

# Add action item based on decision
apm session add-next-step "Migrate remaining validators to Pydantic"

# View session decisions
apm session show
```

---

## File Storage

### Summary Database
All decision records stored in `summaries` table:
```sql
SELECT * FROM summaries
WHERE summary_type = 'decision'
  AND entity_type = 'work_item'
  AND entity_id = 123;
```

### Document References
Detailed decision documents linked via `documents` table:
```sql
SELECT * FROM documents
WHERE entity_type = 'work_item'
  AND entity_id = 123
  AND type = 'adr';
```

### Session Decisions
Session-level decisions in `session_decisions` JSON field:
```sql
SELECT decisions FROM sessions WHERE id = <session_id>;
```

---

## Integration Points

### Called By
- **DefinitionOrch**: Scope and business decisions
- **PlanningOrch**: Architecture and technical decisions
- **ImplementationOrch**: Technical debt and shortcuts
- **ReviewTestOrch**: Quality trade-offs
- **ReleaseOpsOrch**: Deployment decisions
- **EvolutionOrch**: Refactoring priorities

### Database Updates
- Inserts into `summaries` table (via `apm summary create`)
- Links to `work_items`, `tasks`, or `sessions` tables
- Optional document references in `documents` table

---

## Quality Standards

### Decision Record Checklist
- [ ] Clear decision statement (one sentence)
- [ ] Context explains why decision needed
- [ ] ≥2 options considered with pros/cons
- [ ] Rationale explains choice
- [ ] Trade-offs explicitly stated
- [ ] Risks identified with mitigations
- [ ] Success criteria measurable
- [ ] Review date set (for major decisions)

### Metadata Requirements
```json
{
  "decision_type": "architecture|technical|business|risk|scope",
  "made_by": "<agent_role>",
  "alternatives_considered": ["option1", "option2"],
  "rationale": "<why chosen option was selected>",
  "review_date": "YYYY-MM-DD",
  "confidence": 0.0-1.0
}
```

---

## Examples

### Example 1: Quick Technical Decision
```bash
apm summary create \
  --entity-type=task \
  --entity-id=456 \
  --summary-type=decision \
  --content="Use Redis for session storage instead of in-memory. Supports horizontal scaling and session persistence across restarts."
```

### Example 2: Detailed Architecture Decision
```bash
# 1. Create markdown file
cat > docs/decisions/postgres-over-mongo.md << 'EOF'
# Decision: PostgreSQL over MongoDB

## Context
Need database for structured project data with complex relationships.

## Decision Rationale
- ACID guarantees for work item relationships
- JSONB supports flexible metadata
- Team has 3/5 developers with PostgreSQL experience
- Mature ecosystem with proven tools

## Trade-offs
- Less schema flexibility than MongoDB
- Requires migration scripts for changes

## Success Criteria
- Query response times < 100ms
- Zero data corruption
- Schema evolution without downtime
EOF

# 2. Link document to work item
apm document add \
  --entity-type=work-item \
  --entity-id=123 \
  --file-path="docs/decisions/postgres-over-mongo.md" \
  --type=adr \
  --title="Database Choice: PostgreSQL"

# 3. Create summary entry
apm summary create \
  --entity-type=work-item \
  --entity-id=123 \
  --summary-type=decision \
  --content="Use PostgreSQL over MongoDB for ACID guarantees and team expertise" \
  --metadata='{"decision_type": "architecture", "review_date": "2026-01-17"}'
```

### Example 3: Session Decision
```bash
# During active session
apm session add-decision "Defer OAuth to v2" \
  --rationale "Email/password meets beta needs, saves 2 weeks"

# Later, formalize as work item decision
apm summary create \
  --entity-type=work-item \
  --entity-id=789 \
  --summary-type=decision \
  --content="Limit auth to email/password in v1. OAuth deferred to v2 to save 2 weeks." \
  --metadata='{"decision_type": "scope", "timeline_impact": "-2 weeks"}'
```

---

## Usage Patterns

### Pattern 1: Inline Decision (Lightweight)
```bash
# Quick capture during implementation
apm summary create \
  --entity-type=task \
  --entity-id=456 \
  --summary-type=decision \
  --content="Accept N+1 queries temporarily. Traffic is low (<100 users), optimize in v1.1"
```

### Pattern 2: Documented Decision (Formal)
```bash
# 1. Write detailed markdown
# 2. Link as ADR document
# 3. Create summary reference
```

### Pattern 3: Session Capture (Real-time)
```bash
# During work session
apm session add-decision "<decision>" --rationale "<why>"

# End of session - promote to work item if significant
apm summary create --entity-type=work-item ...
```

---

## Non-Negotiables

1. **Document major decisions** - Capture rationale for architecture/scope changes
2. **Consider alternatives** - At least 2 options evaluated for significant decisions
3. **State trade-offs** - Be explicit about costs
4. **Identify risks** - Don't hide downsides
5. **Use existing commands** - Summary system, NOT audit commands

---

## Migration from Audit Logger

**Old (non-existent)**:
```bash
apm audit log --work-item-id=123 --type=architecture --decision="..." --rationale="..."
```

**New (using summary system)**:
```bash
apm summary create \
  --entity-type=work-item \
  --entity-id=123 \
  --summary-type=decision \
  --content="<decision + rationale>" \
  --metadata='{"decision_type": "architecture"}'
```

---

**Version**: 2.0.0 (Migrated from audit-logger to summary system)
**Last Updated**: 2025-10-17
**Status**: Active
**Replaces**: audit-logger.md (deprecated - used non-existent commands)


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
