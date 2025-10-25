"""
Idea Enumerations - Lightweight Brainstorming Entity

Ideas have a simpler lifecycle than work items:
  idea → research → design → accepted → converted (terminal)
  any state → rejected (terminal)

Ideas are lightweight entry points before committing to formal work items.
"""

from enum import Enum
from typing import Optional


class IdeaStatus(str, Enum):
    """
    Idea lifecycle states (6-state simple workflow).

    Flow:
        idea → research → design → accepted → converted (terminal)
        any state → rejected (terminal)

    Terminal states:
        - converted: Successfully became work item
        - rejected: Not viable (kept for audit trail)

    Ideas have simpler workflow than work items - no validation/review gates.

    Phase Alignment with Work Items:
        - IDEA (brainstorming) → aligns with pre-D1 (before discovery)
        - RESEARCH (investigation) → aligns with D1_DISCOVERY phase
        - DESIGN (planning) → aligns with P1_PLAN phase  
        - ACTIVE/accepted (ready to execute) → ready for I1_IMPLEMENTATION phase
        - CONVERTED → became work item (continues in work item phases)
        - REJECTED → not viable (no work item created)

    This alignment ensures smooth transition from idea exploration to work item execution.
    """
    IDEA = "idea"
    RESEARCH = "research"
    DESIGN = "design"
    ACTIVE = "accepted"
    CONVERTED = "converted"  # Terminal state
    REJECTED = "rejected"    # Terminal state

    @classmethod
    def is_terminal_state(cls, status: 'IdeaStatus') -> bool:
        """Check if status is terminal (converted or rejected)"""
        return status in (cls.CONVERTED, cls.REJECTED)

    @classmethod
    def allowed_transitions(cls, current: 'IdeaStatus') -> list['IdeaStatus']:
        """
        Get allowed state transitions from current state.

        Transition Rules:
        - idea → research
        - research → design
        - design → accepted
        - accepted → converted (via convert_idea_to_work_item)
        - any → rejected

        Returns:
            List of allowed next states
        """
        # Terminal states cannot transition
        if cls.is_terminal_state(current):
            return []

        # Map current state to allowed next states
        transitions = {
            cls.IDEA: [cls.RESEARCH, cls.REJECTED],
            cls.RESEARCH: [cls.DESIGN, cls.REJECTED],
            cls.DESIGN: [cls.ACTIVE, cls.REJECTED],
            cls.ACTIVE: [cls.CONVERTED, cls.REJECTED],
        }

        return transitions.get(current, [])

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def get_aligned_phase(cls, status: 'IdeaStatus') -> Optional[str]:
        """
        Get the work item phase that aligns with this idea status.
        
        Args:
            status: Idea status to get aligned phase for
            
        Returns:
            Work item phase code (e.g., 'D1_DISCOVERY') or None if no alignment
        """
        phase_mapping = {
            cls.IDEA: None,  # Pre-discovery
            cls.RESEARCH: "D1_DISCOVERY",
            cls.DESIGN: "P1_PLAN", 
            cls.ACTIVE: "P1_PLAN",  # Ready for implementation
            cls.CONVERTED: None,  # Now a work item
            cls.REJECTED: None,  # No work item
        }
        return phase_mapping.get(status)

    @classmethod
    def get_conversion_readiness(cls, status: 'IdeaStatus') -> dict:
        """
        Get conversion readiness information for an idea status.
        
        Args:
            status: Idea status to check
            
        Returns:
            Dictionary with readiness info
        """
        if status == cls.ACTIVE:
            return {
                "ready": True,
                "message": "Ready for conversion to work item",
                "recommended_phase": "P1_PLAN",
                "next_steps": ["Convert to work item", "Start implementation planning"]
            }
        elif status == cls.DESIGN:
            return {
                "ready": True,
                "message": "Design complete, ready for conversion",
                "recommended_phase": "P1_PLAN", 
                "next_steps": ["Convert to work item", "Begin implementation"]
            }
        elif status == cls.RESEARCH:
            return {
                "ready": False,
                "message": "Research phase - complete design before conversion",
                "recommended_phase": "D1_DISCOVERY",
                "next_steps": ["Transition to design", "Complete planning phase"]
            }
        elif status == cls.IDEA:
            return {
                "ready": False,
                "message": "Early idea - needs research and design",
                "recommended_phase": "D1_DISCOVERY",
                "next_steps": ["Start research", "Define requirements", "Create design"]
            }
        else:
            return {
                "ready": False,
                "message": f"Cannot convert from {status.value} state",
                "recommended_phase": None,
                "next_steps": []
            }


class IdeaSource(str, Enum):
    """
    Idea origin categorization.

    Tracks where ideas come from for analytics and prioritization.
    """
    USER = "user"
    AI_SUGGESTION = "ai_suggestion"
    BRAINSTORMING_SESSION = "brainstorming_session"
    CUSTOMER_FEEDBACK = "customer_feedback"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    OTHER = "other"

    @classmethod
    def requires_attribution(cls, source: 'IdeaSource') -> bool:
        """
        Check if source type should include created_by attribution.

        Returns:
            True if created_by should be populated
        """
        # All sources benefit from attribution, but especially these:
        return source in (
            cls.USER,
            cls.BRAINSTORMING_SESSION,
            cls.CUSTOMER_FEEDBACK
        )

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")
