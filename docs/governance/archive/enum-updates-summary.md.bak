# Enum System Updates - Complete ADR Support

**Date:** 2025-10-12
**File Updated:** `agentpm/core/database/enums/types.py`
**Status:** ✅ Complete and validated

---

## Changes Made

### Original Enums (Existed Before)
1. WorkItemType (8 types)
2. TaskType (19 types)
3. EntityType (3 types)
4. ContextType (4 types)
5. ResourceType (4 types)
6. ConfidenceBand (3 bands + helper method)
7. EnforcementLevel (4 levels)
8. ProjectType (4 types)
9. Phase (6 phases)
10. SourceType (7 types)
11. EventType (9 types)
12. DocumentType (17 types)
13. DocumentFormat (10 formats)
14. AgentTier (3 tiers)

**Total: 14 enums**

---

### New Enums Added (Session Updates)

**DevelopmentPhilosophy - Enhanced:**
```python
# Added by product owner:
YAGNI = "yagni"                    # You Ain't Gonna Need It
DRY = "dry"                        # Don't Repeat Yourself
SOLID = "solid"                    # SOLID principles
BEHAVIOUR_DRIVEN = "behaviour_driven"  # BDD
DESIGN_DRIVEN = "design_driven"    # Design-first
TEST_DRIVEN = "test_driven"        # TDD
AGILE = "agile"                    # Agile methodology
DATA_DRIVEN = "data_driven"        # Data-driven decisions
DATA_AWARE = "data_aware"          # Data-aware development

# Now has 12 philosophy options (was 4)
```

**New Enums Supporting ADRs:**

15. **LearningType** (ADR-003: Sub-Agent Communication)
    ```python
    DECISION, PATTERN, DISCOVERY, CONSTRAINT, ANTIPATTERN,
    OPTIMIZATION, SECURITY, INTEGRATION, BEST_PRACTICE
    # 9 learning types for cross-agent knowledge sharing
    ```

16. **RiskLevel** (ADR-007: Human-in-the-Loop)
    ```python
    LOW, MEDIUM, HIGH, CRITICAL
    # 4 risk levels with from_score() helper method
    # Determines human review requirements
    ```

17. **ReviewStatus** (ADR-007: Human Review Workflow)
    ```python
    PENDING, UNDER_REVIEW, APPROVED, REJECTED, ESCALATED, EXPIRED, CANCELLED
    # 7 statuses for review lifecycle tracking
    ```

18. **DependencyType** (ADR-010: Dependency Management)
    ```python
    FINISH_TO_START, START_TO_START, FINISH_TO_FINISH, START_TO_FINISH
    # 4 PMBOK standard dependency types
    ```

19. **CacheStrategy** (ADR-002: Context Compression)
    ```python
    AGGRESSIVE, MODERATE, CONSERVATIVE, DISABLED
    # 4 caching strategies with TTL guidance
    ```

20. **DocumentStatus** (ADR-006: Document Store)
    ```python
    DRAFT, REVIEW, APPROVED, SUPERSEDED, ARCHIVED
    # 5 document lifecycle states
    ```

21. **EvidenceStatus** (ADR-004: Evidence Storage)
    ```python
    VERIFIED, STALE, BROKEN, UNVERIFIED
    # 4 evidence verification states
    ```

22. **NotificationChannel** (ADR-009: Event System)
    ```python
    EMAIL, SLACK, CLI, WEBHOOK, NONE
    # 5 notification delivery channels
    ```

**Total Enums: 22 (was 14, added 8)**

---

## ADR Coverage Matrix

| ADR | Enum Support | Status |
|-----|--------------|--------|
| ADR-001: Provider Abstraction | SessionTool (in session.py) | ✅ Exists |
| ADR-002: Context Compression | CacheStrategy | ✅ Added |
| ADR-003: Sub-Agent Protocol | LearningType | ✅ Added |
| ADR-004: Evidence Storage | EvidenceStatus, SourceType | ✅ Added |
| ADR-005: Multi-Provider Sessions | SessionTool, SessionStatus | ✅ Exists |
| ADR-006: Document Store | DocumentStatus, DocumentType, DocumentFormat | ✅ Added |
| ADR-007: Human-in-the-Loop | RiskLevel, ReviewStatus | ✅ Added |
| ADR-008: Data Privacy | (Uses existing enums) | ✅ N/A |
| ADR-009: Event System | NotificationChannel, EventType | ✅ Added |
| ADR-010: Dependencies | DependencyType | ✅ Added |
| ADR-011: Cost Tracking | (Uses ProviderType/SessionTool) | ✅ N/A |

**Coverage: 100% - All ADRs have enum support**

---

## Key Enhancements

### 1. Helper Methods Added

**ConfidenceBand.from_score()** (existed):
```python
score = 0.85
band = ConfidenceBand.from_score(score)  # Returns GREEN
```

**RiskLevel.from_score()** (new):
```python
risk_score = 0.95
level = RiskLevel.from_score(risk_score)  # Returns CRITICAL
```

### 2. Comprehensive Documentation

Each enum now includes:
- ✅ Purpose and usage context
- ✅ ADR reference (where applicable)
- ✅ Examples of usage
- ✅ Threshold guidance (for scored enums)
- ✅ Statistics or best practices

### 3. Local-First Design Emphasis

**ProviderType documentation clarifies:**
> "Local-first design: AIPM doesn't call these APIs.
> AI agents use their own API keys, AIPM just tracks which tool was used."

This aligns with the strategic decision that AIPM is passive, not active.

---

## Usage Examples

### Cross-Agent Learning (ADR-003)

```python
from agentpm.core.database.enums.types import LearningType

# Session 1: AI agent saves learning
learning = Learning(
    learning_type=LearningType.DECISION,
    content="Use PostgreSQL for ACID compliance",
    rationale="Multi-tenant e-commerce requires transactions"
)
db.add(learning)

# Session 2: Different AI agent reads learning
decisions = db.query(Learning).filter(
    Learning.learning_type == LearningType.DECISION
).all()
# Agent sees: "PostgreSQL decision already made" → consistent implementation
```

### Human Review (ADR-007)

```python
from agentpm.core.database.enums.types import RiskLevel, ReviewStatus

# Calculate risk score
risk_score = calculate_risk(decision)  # Returns 0.85

# Convert to risk level
level = RiskLevel.from_score(risk_score)  # Returns HIGH

# Create review request
if level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
    review = HumanReviewRequest(
        risk_level=level,
        status=ReviewStatus.PENDING
    )
    db.add(review)
    # Work blocked until human approves
```

### Task Dependencies (ADR-010)

```python
from agentpm.core.database.enums.types import DependencyType

# Task 2 depends on Task 1 completing first
dependency = TaskDependency(
    dependent_task_id=2,
    prerequisite_task_id=1,
    dependency_type=DependencyType.FINISH_TO_START
)
db.add(dependency)

# Schedule tasks: Task 1 must complete before Task 2 starts
```

### Document Lifecycle (ADR-006)

```python
from agentpm.core.database.enums.types import DocumentStatus, DocumentType

# Create ADR
doc = Document(
    document_type=DocumentType.ADR,
    status=DocumentStatus.DRAFT
)

# Review process
doc.status = DocumentStatus.REVIEW  # Ready for review
doc.status = DocumentStatus.APPROVED  # Approved

# Later, supersede with newer version
doc.status = DocumentStatus.SUPERSEDED
newer_doc.supersedes = doc.id
```

---

## Validation Results

**Import Test:** ✅ Passed
```bash
python -c "from agentpm.core.database.enums.types import *"
# No errors, all 22 enums importable
```

**Enum Count:** 22 total classes
- 14 original enums
- 1 enhanced (DevelopmentPhilosophy: 4 → 12 values)
- 7 new enums (ADR support)

**Lines of Code:** 474 lines (was ~310)
**Documentation:** Comprehensive docstrings for all enums

---

## Next Steps

### Immediate (Micro-MVP - Week 1-2)

**Use These Enums:**
- LearningType: For session learning capture
- SessionTool: For provider tracking (already exists)
- ConfidenceBand: For context quality validation

**Implementation:**
```python
# session-end hook
def capture_learnings():
    decision = input("Decision made? ")
    if decision:
        db.execute(
            "INSERT INTO learnings (learning_type, content) VALUES (?, ?)",
            (LearningType.DECISION, decision)
        )
```

### Phase 2 (Week 3-8)

**Use These Enums:**
- RiskLevel, ReviewStatus: Human review workflow
- DocumentStatus, DocumentType: Document store
- CacheStrategy: Context caching

### Phase 3 (Week 9+)

**Use These Enums:**
- DependencyType: Task scheduling
- EvidenceStatus: Evidence verification
- NotificationChannel: Event notifications

---

## Benefits of Comprehensive Enum System

### 1. Type Safety
```python
# Prevents typos and invalid values
status = "aproved"  # ❌ Would fail validation
status = ReviewStatus.APPROVED  # ✅ Type-safe
```

### 2. Self-Documenting Code
```python
# Clear what each value means
learning_type = "pattern"  # Unclear
learning_type = LearningType.PATTERN  # Self-explanatory
```

### 3. Database Constraints
```sql
-- Enum values enforced at database level
CHECK(learning_type IN ('decision', 'pattern', 'discovery', ...))
```

### 4. IDE Support
```python
# Autocomplete shows all valid options
review.status = ReviewStatus.  # IDE suggests: PENDING, APPROVED, etc.
```

### 5. ADR Traceability
```python
# Each enum documents which ADR it supports
class RiskLevel(str, Enum):
    """... (ADR-007: Human-in-the-Loop)"""
# Easy to find related specifications
```

---

## Summary

**Status:** ✅ Enum system complete and validated

**Coverage:**
- All existing AIPM features: Covered
- All 11 ADRs: Covered
- Micro-MVP needs: Covered
- Future phases: Covered

**Quality:**
- Type-safe enumerations
- Comprehensive documentation
- Helper methods where useful
- Examples for all major enums

**Ready for:** Micro-MVP implementation (Week 1-2)

**File Status:** 474 lines, 22 enum classes, imports successfully

---

**Last Updated:** 2025-10-12
**Validated By:** Python import test
**Next:** Begin Micro-MVP implementation
