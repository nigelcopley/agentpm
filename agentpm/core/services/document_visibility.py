"""
Document Visibility Policy Engine

Evaluates document visibility based on type, context, and lifecycle.
Uses scoring system (0-100+) with context modifiers to determine visibility.

Part of Work Item #164: Auto-Generate Document File Paths

Architecture: Three-Layer Pattern
  Layer 1 (Models): document_visibility.py - Pydantic models
  Layer 2 (Services): This file - Business logic
  Layer 3 (Adapters): visibility_policy_adapter.py - Database I/O
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

from ..database.service import DatabaseService
from ..database.adapters.visibility_policy_adapter import VisibilityPolicyAdapter
from ..models.document_visibility import (
    VisibilityPolicy,
    ProjectVisibilityContext,
    VisibilityEvaluation,
    AutoPublishResult,
)

# Scoring modifiers (from policy matrix design)
TEAM_SIZE_MODIFIERS = {
    "solo": -20,
    "small": 0,
    "medium": 10,
    "large": 20,
}

DEVELOPMENT_STAGE_MODIFIERS = {
    "development": -10,
    "staging": 0,
    "production": 15,
}

COLLABORATION_MODEL_MODIFIERS = {
    "private": -30,
    "internal": 0,
    "open_source": 30,
}

LIFECYCLE_STAGE_MODIFIERS = {
    "draft": -50,
    "review": 0,
    "approved": 10,
    "published": 20,
    "archived": -100,
}

VISIBILITY_THRESHOLDS = {
    "private": 0,
    "restricted": 40,
    "public": 60,
}

# Auto-publish trigger lists (from policy matrix)
AUTO_PUBLISH_ON_APPROVED = [
    "guides.user_guide",
    "guides.admin_guide",
    "guides.developer_guide",
    "guides.troubleshooting",
    "guides.faq",
    "reference.api_doc",
    "reference.specification",
    "processes.migration_guide",
    "processes.integration_guide",
]

AUTO_PUBLISH_ON_WORK_ITEM_PHASE_R1 = [
    "architecture.design_doc",
]

AUTO_PUBLISH_ON_WORK_ITEM_PHASE_O1 = [
    "architecture.architecture_doc",
    "architecture.adr",
    "architecture.technical_spec",
]


class VisibilityPolicyEngine:
    """
    Evaluates document visibility based on type and context.

    Uses policy matrix from database and context modifiers to determine:
    - Visibility level (private, restricted, public)
    - Target audience
    - Auto-publish triggers
    - Review requirements

    Example:
        >>> engine = VisibilityPolicyEngine(db)
        >>> result = engine.determine_visibility(
        ...     category="guides",
        ...     doc_type="user_guide",
        ...     lifecycle_stage="approved"
        ... )
        >>> print(result.visibility)  # "public"
        >>> print(result.rationale)   # "guides.user_guide is force_public..."
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize visibility policy engine.

        Args:
            db: DatabaseService instance for policy loading
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

        # Load project context from database/settings
        self.project_context = self._load_project_context()

        # Cache policies for performance (loaded on demand)
        self._policy_cache: Dict[str, VisibilityPolicy] = {}

    def determine_visibility(
        self,
        category: str,
        doc_type: str,
        lifecycle_stage: str = "draft",
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
    ) -> VisibilityEvaluation:
        """
        Determine visibility for a document.

        Args:
            category: Document category (planning, architecture, guides, etc.)
            doc_type: Document type within category (idea, adr, user_guide, etc.)
            lifecycle_stage: Current lifecycle stage (draft, review, approved, published, archived)
            entity_type: Optional entity type (work-item, task, etc.)
            entity_id: Optional entity ID

        Returns:
            VisibilityEvaluation with final visibility and rationale

        Example:
            >>> result = engine.determine_visibility("guides", "user_guide", "approved")
            >>> assert result.visibility == "public"
            >>> assert result.auto_publish_on_approved == True
        """
        # 1. Get base policy from database
        policy = self._get_base_policy(category, doc_type)

        # 2. Check lifecycle overrides (draft/archived always private)
        if lifecycle_stage in ['draft', 'archived']:
            return VisibilityEvaluation(
                visibility="private",
                audience="internal",
                base_score=policy.base_score,
                final_score=0,  # Force override
                context_modifiers={"lifecycle_override": -100},
                requires_review=policy.requires_review,
                auto_publish_on_approved=False,  # Can't auto-publish private
                rationale=f"Lifecycle stage '{lifecycle_stage}' forces private visibility"
            )

        # 3. Check force_private flag
        if policy.force_private:
            return VisibilityEvaluation(
                visibility="private",
                audience="internal",
                base_score=policy.base_score,
                final_score=0,  # Force override
                context_modifiers={"force_private": -100},
                requires_review=policy.requires_review,
                auto_publish_on_approved=False,  # Can't auto-publish private
                rationale=f"{category}.{doc_type} has force_private=true (never public)"
            )

        # 4. Check force_public flag (only applies when approved/published)
        if policy.force_public and lifecycle_stage in ['approved', 'published']:
            return VisibilityEvaluation(
                visibility="public",
                audience=policy.default_audience,
                base_score=policy.base_score,
                final_score=100,  # Force override
                context_modifiers={"force_public": +100},
                requires_review=policy.requires_review,
                auto_publish_on_approved=policy.auto_publish_on_approved,
                rationale=f"{category}.{doc_type} has force_public=true (always public when approved)"
            )

        # 5. Calculate score with context modifiers
        score, modifiers = self._calculate_visibility_score(policy, lifecycle_stage)

        # 6. Determine visibility from score
        visibility = self._score_to_visibility(score)
        audience = self._score_to_audience(score)

        # 7. Generate rationale
        rationale = self._generate_rationale(policy, score, visibility, modifiers)

        return VisibilityEvaluation(
            visibility=visibility,
            audience=audience,
            base_score=policy.base_score,
            final_score=score,
            context_modifiers=modifiers,
            requires_review=policy.requires_review,
            auto_publish_on_approved=policy.auto_publish_on_approved,
            rationale=rationale
        )

    def should_auto_publish(
        self,
        category: str,
        doc_type: str,
        lifecycle_stage: str,
        work_item_phase: Optional[str] = None,
    ) -> AutoPublishResult:
        """
        Determine if document should auto-publish.

        Checks:
        1. on_approved triggers (immediate when approved)
        2. on_work_item_phase_R1 triggers (when work item reaches R1_REVIEW)
        3. on_work_item_phase_O1 triggers (when work item reaches O1_OPERATIONS)
        4. manual_only types (never auto-publish)

        Args:
            category: Document category
            doc_type: Document type
            lifecycle_stage: Current lifecycle stage
            work_item_phase: Optional work item phase (e.g., "O1_OPERATIONS")

        Returns:
            AutoPublishResult with decision and trigger reason

        Example:
            >>> result = engine.should_auto_publish(
            ...     "guides", "user_guide", "approved"
            ... )
            >>> assert result.should_publish == True
            >>> assert result.trigger_type == "on_approved"
        """
        # Check if already published
        if lifecycle_stage == 'published':
            return AutoPublishResult(
                should_publish=False,
                trigger_reason="already published",
                trigger_type=None
            )

        # Build full type identifier
        full_type = f"{category}.{doc_type}"

        # Get policy to check auto_publish_on_approved flag
        policy = self._get_base_policy(category, doc_type)

        # Check on_approved trigger
        if lifecycle_stage == 'approved' and full_type in AUTO_PUBLISH_ON_APPROVED:
            return AutoPublishResult(
                should_publish=True,
                trigger_reason=f"auto_publish_on_approved for {full_type}",
                trigger_type="on_approved"
            )

        # Check work item phase triggers (if work item provided)
        if work_item_phase:
            if work_item_phase == 'R1_REVIEW' and full_type in AUTO_PUBLISH_ON_WORK_ITEM_PHASE_R1:
                return AutoPublishResult(
                    should_publish=True,
                    trigger_reason=f"{full_type} published when work item reaches R1_REVIEW",
                    trigger_type="on_work_item_phase_R1"
                )

            if work_item_phase == 'O1_OPERATIONS' and full_type in AUTO_PUBLISH_ON_WORK_ITEM_PHASE_O1:
                return AutoPublishResult(
                    should_publish=True,
                    trigger_reason=f"{full_type} published when work item reaches O1_OPERATIONS",
                    trigger_type="on_work_item_phase_O1"
                )

        # Check policy auto_publish_on_approved flag
        if lifecycle_stage == 'approved' and policy.auto_publish_on_approved:
            return AutoPublishResult(
                should_publish=True,
                trigger_reason=f"policy.auto_publish_on_approved=true for {full_type}",
                trigger_type="on_approved"
            )

        # Default: manual publish required
        return AutoPublishResult(
            should_publish=False,
            trigger_reason="manual publish required (no auto-publish triggers matched)",
            trigger_type=None
        )

    # ============================================================================
    # PRIVATE METHODS
    # ============================================================================

    def _get_base_policy(self, category: str, doc_type: str) -> VisibilityPolicy:
        """
        Get policy from database or use default.

        Args:
            category: Document category
            doc_type: Document type

        Returns:
            VisibilityPolicy from database or default policy
        """
        # Check cache first
        cache_key = f"{category}.{doc_type}"
        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]

        # Try to load from database
        policy = VisibilityPolicyAdapter.get_by_type(self.db, category, doc_type)

        if policy:
            # Cache and return
            self._policy_cache[cache_key] = policy
            return policy

        # Return default policy
        self.logger.warning(
            f"No policy found for {category}.{doc_type}, using default"
        )

        default_policy = VisibilityPolicy(
            category=category,
            doc_type=doc_type,
            default_visibility="private",
            default_audience="internal",
            requires_review=True,
            auto_publish_on_approved=False,
            base_score=50,
            force_private=False,
            force_public=False,
            description=f"Default policy for {category}.{doc_type}",
            rationale="No specific policy defined, using safe defaults"
        )

        # Cache default
        self._policy_cache[cache_key] = default_policy

        return default_policy

    def _calculate_visibility_score(
        self,
        policy: VisibilityPolicy,
        lifecycle_stage: str
    ) -> Tuple[int, Dict[str, int]]:
        """
        Calculate final visibility score with context modifiers.

        Score = base_score + team_modifier + stage_modifier + collab_modifier + lifecycle_modifier

        Args:
            policy: Base policy
            lifecycle_stage: Current lifecycle stage

        Returns:
            Tuple of (final_score, modifiers_dict)
        """
        modifiers: Dict[str, int] = {}
        score = policy.base_score

        # Team size modifier
        team_modifier = TEAM_SIZE_MODIFIERS.get(self.project_context.team_size, 0)
        if team_modifier != 0:
            modifiers['team_size'] = team_modifier
            score += team_modifier

        # Dev stage modifier
        stage_modifier = DEVELOPMENT_STAGE_MODIFIERS.get(self.project_context.dev_stage, 0)
        if stage_modifier != 0:
            modifiers['dev_stage'] = stage_modifier
            score += stage_modifier

        # Collaboration model modifier
        collab_modifier = COLLABORATION_MODEL_MODIFIERS.get(self.project_context.collaboration_model, 0)
        if collab_modifier != 0:
            modifiers['collaboration_model'] = collab_modifier
            score += collab_modifier

        # Lifecycle modifier
        lifecycle_modifier = LIFECYCLE_STAGE_MODIFIERS.get(lifecycle_stage, 0)
        if lifecycle_modifier != 0:
            modifiers['lifecycle_stage'] = lifecycle_modifier
            score += lifecycle_modifier

        # Clamp to 0-100 for thresholding (but return actual score for transparency)
        return (score, modifiers)

    def _score_to_visibility(self, score: int) -> str:
        """
        Convert score to visibility level.

        Args:
            score: Final visibility score

        Returns:
            Visibility level (private|restricted|public)
        """
        if score < VISIBILITY_THRESHOLDS["restricted"]:
            return "private"
        elif score < VISIBILITY_THRESHOLDS["public"]:
            return "restricted"
        else:
            return "public"

    def _score_to_audience(self, score: int) -> str:
        """
        Convert score to target audience.

        Args:
            score: Final visibility score

        Returns:
            Audience (internal|team|contributors|users|public)
        """
        if score < 30:
            return "internal"
        elif score < 50:
            return "team"
        elif score < 70:
            return "contributors"
        elif score < 85:
            return "users"
        else:
            return "public"

    def _generate_rationale(
        self,
        policy: VisibilityPolicy,
        score: int,
        visibility: str,
        modifiers: Dict[str, int]
    ) -> str:
        """
        Generate human-readable rationale for visibility decision.

        Args:
            policy: Base policy
            score: Final score
            visibility: Final visibility
            modifiers: Applied modifiers

        Returns:
            Rationale string
        """
        parts = [
            f"Base score: {policy.base_score}",
        ]

        if modifiers:
            modifier_str = ", ".join([f"{k}={v:+d}" for k, v in modifiers.items()])
            parts.append(f"Modifiers: {modifier_str}")

        parts.append(f"Final score: {score}")
        parts.append(f"Visibility: {visibility}")

        if policy.rationale:
            parts.append(f"Policy rationale: {policy.rationale}")

        return " | ".join(parts)

    def _load_project_context(self) -> ProjectVisibilityContext:
        """
        Load project context from database/settings.

        For now, returns default context. In future, this would query
        project settings table to get actual team size, dev stage, etc.

        Returns:
            ProjectVisibilityContext with current project settings
        """
        # TODO: Load from project settings table
        # For now, use safe defaults
        return ProjectVisibilityContext(
            team_size="solo",
            dev_stage="development",
            collaboration_model="private"
        )

    def clear_cache(self):
        """Clear policy cache. Useful after policy updates."""
        self._policy_cache.clear()
        self.logger.info("Policy cache cleared")
