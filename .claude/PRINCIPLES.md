# Development Principles Pyramid

**Total Principles**: 14
**Generated**: 2025-10-21 11:08:26

---

## Core Development Principles

APM (Agent Project Manager) follows a structured approach to software development:

- **Time-Boxing**: All work is time-boxed to maintain focus and prevent scope creep
- **Quality Gates**: Each phase has defined entry/exit criteria
- **Database-First**: Schema defines contracts, code follows schema
- **Type Safety**: Pydantic models provide runtime validation

---

## Active Principles

### Tier 1: Non-Negotiable Principles

**DP-001**: time-boxing-implementation

IMPLEMENTATION tasks ≤4h

**DP-002**: time-boxing-testing

TESTING tasks ≤6h

**DP-003**: time-boxing-design

DESIGN tasks ≤8h

**DP-004**: time-boxing-documentation

DOCUMENTATION tasks ≤4h

**DP-005**: time-boxing-deployment

DEPLOYMENT tasks ≤2h

**DP-006**: time-boxing-analysis

ANALYSIS tasks ≤8h

**DP-007**: time-boxing-research

RESEARCH tasks ≤12h

**DP-008**: time-boxing-refactoring

REFACTORING tasks ≤6h

**DP-009**: time-boxing-bugfix

BUGFIX tasks ≤4h

**DP-010**: time-boxing-hotfix

HOTFIX tasks ≤2h

**DP-011**: time-boxing-planning

PLANNING tasks ≤8h

**DP-036**: security-no-hardcoded-secrets

No secrets in code

### Tier 3: Best Practices

**DP-030**: code-no-dict-str-any

No Dict[str, Any] in public APIs

**DP-046**: perf-api-response-time

API responses <200ms (p95)

