"""
Additional Type Enumerations for APM (Agent Project Manager) ADR Support

These enums support the 11 ADRs created in strategic planning.
Copy relevant enums to types.py as needed.

References:
- ADR-003: LearningType (cross-agent knowledge)
- ADR-004: EvidenceStatus (evidence verification)
- ADR-006: DocumentStatus (document lifecycle)
- ADR-007: RiskLevel, ReviewStatus (human review)
- ADR-009: NotificationChannel (event notifications)
- ADR-010: DependencyType (task dependencies)
"""

from enum import Enum


class LearningType(str, Enum):
    """
    Session learning categorization (ADR-003).

    Enables cross-agent knowledge sharing via database.
    AI agents save discoveries, other agents read them.

    Example:
      Claude session: Decides "Use JWT" → saves as DECISION
      Cursor session: Reads decisions → sees JWT choice → consistent
    """
    DECISION = "decision"
    PATTERN = "pattern"
    DISCOVERY = "discovery"
    CONSTRAINT = "constraint"
    ANTIPATTERN = "antipattern"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    INTEGRATION = "integration"
    BEST_PRACTICE = "best_practice"


class RiskLevel(str, Enum):
    """
    Risk classification for human review (ADR-007).

    Thresholds from risk scoring algorithm:
    - LOW (0.0-0.3): Auto-approve
    - MEDIUM (0.3-0.7): Peer review
    - HIGH (0.7-0.9): Senior review required
    - CRITICAL (0.9-1.0): Executive review required
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewStatus(str, Enum):
    """
    Human review request status (ADR-007).
    """
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DependencyType(str, Enum):
    """
    Task dependency types (ADR-010).

    PMBOK standards for dependency management.
    """
    FINISH_TO_START = "finish_to_start"    # Most common (90%)
    START_TO_START = "start_to_start"      # Parallel work
    FINISH_TO_FINISH = "finish_to_finish"  # Synchronized
    START_TO_FINISH = "start_to_finish"    # Rare


class CacheStrategy(str, Enum):
    """
    Context caching strategy (ADR-002).

    MVP: DISABLED
    Production: MODERATE
    """
    AGGRESSIVE = "aggressive"      # 1h TTL
    MODERATE = "moderate"          # 30min TTL
    CONSERVATIVE = "conservative"  # 15min TTL
    DISABLED = "disabled"          # No cache (MVP)


class DocumentStatus(str, Enum):
    """
    Document lifecycle status (ADR-006).
    """
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class EvidenceStatus(str, Enum):
    """
    Evidence verification status (ADR-004).
    """
    VERIFIED = "verified"
    STALE = "stale"
    BROKEN = "broken"
    UNVERIFIED = "unverified"


class NotificationChannel(str, Enum):
    """
    Notification channels (ADR-009).
    """
    EMAIL = "email"
    SLACK = "slack"
    CLI = "cli"
    WEBHOOK = "webhook"
    NONE = "none"


class ProviderType(str, Enum):
    """
    AI provider types for session tracking.

    Local-first: AIPM doesn't call APIs.
    Just tracks which tool the AI agent used.
    """
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    AIDER = "aider"
    COPILOT = "copilot"
    GEMINI = "gemini"
    CODEX = "codex"
    CODY = "cody"
    TABNINE = "tabnine"
    MANUAL = "manual"
    OTHER = "other"
