"""
Temporal Context Loader - Session History for Continuity

Loads session summaries from WI-0017 work_item_summaries table.
Provides temporal context (what happened in recent sessions) for continuity
across work sessions.

Pattern: Simple database query with formatting for agent consumption
"""

from typing import List, Dict, Any
from datetime import datetime


class TemporalContextLoader:
    """
    Load temporal context (session summaries) for work items.

    Provides session history for continuity across work sessions.
    Integrates with WI-0017 work_item_summaries table.

    Example usage:
        loader = TemporalContextLoader(db)
        summaries = loader.load_recent_summaries(work_item_id=7, limit=3)
        formatted = loader.format_for_agent(summaries)
    """

    def __init__(self, db):
        """
        Initialize temporal context loader.

        Args:
            db: DatabaseService instance
        """
        self.db = db

    def load_recent_summaries(
        self,
        work_item_id: int,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Load recent session summaries for a work item.

        Args:
            work_item_id: Work item ID
            limit: Number of recent summaries to load (default: 3)

        Returns:
            List of summary dicts with:
                - summary_text: Session summary text
                - summary_type: 'session', 'milestone', 'checkpoint', 'handoff'
                - session_date: ISO timestamp
                - session_duration_hours: Duration (if available)
                - metadata: JSON metadata (key_decisions, tasks_completed, etc.)

        Performance: <10ms (indexed query on work_item_id + date DESC)

        Example:
            >>> loader.load_recent_summaries(work_item_id=7, limit=3)
            [
                {
                    'summary_text': 'Completed database schema...',
                    'summary_type': 'session',
                    'session_date': '2025-10-09T14:30:00',
                    'session_duration_hours': 3.5,
                    'metadata': {'tasks_completed': [45, 46]}
                },
                ...
            ]
        """
        try:
            # Use existing work_item_summaries methods (WI-0017)
            from ..database.methods import work_item_summaries

            summaries = work_item_summaries.get_recent_summaries(
                self.db,
                work_item_id=work_item_id,
                limit=limit
            )

            # Convert to dict format for ContextPayload
            return [
                {
                    'summary_text': s.summary_text,
                    'summary_type': s.summary_type,
                    'session_date': s.session_date.isoformat() if hasattr(s.session_date, 'isoformat') else s.session_date,
                    'session_duration_hours': s.session_duration_hours,
                    'metadata': s.context_metadata or {}
                }
                for s in summaries
            ]

        except Exception:
            # Graceful degradation - no summaries available
            return []

    def format_for_agent(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Format summaries for agent consumption (markdown).

        Args:
            summaries: List of summary dicts from load_recent_summaries()

        Returns:
            Formatted markdown string for agent context

        Example output:
            ## Recent Session History

            ### Session 1: session
            **Date**: 2025-10-09T14:30:00
            **Duration**: 3.5h

            Completed database schema and implemented core CRUD operations.
            All tests passing with 95% coverage.

            **Key Decisions**:
            - Use three-layer pattern for all database operations
            - SQLite primary key: INTEGER PRIMARY KEY

            **Tasks Completed**: 2
            **Blockers Resolved**: 1

            ---

            ### Session 2: milestone
            ...
        """
        if not summaries:
            return "No recent session history available."

        lines = ["## Recent Session History\n"]

        for idx, summary in enumerate(summaries, 1):
            # Session header
            lines.append(f"### Session {idx}: {summary['summary_type']}")

            # Session metadata
            if summary.get('session_date'):
                lines.append(f"**Date**: {summary['session_date']}")

            if summary.get('session_duration_hours'):
                hours = summary['session_duration_hours']
                lines.append(f"**Duration**: {hours:.1f}h")

            # Session summary text
            lines.append(f"\n{summary['summary_text']}\n")

            # Add metadata if present
            metadata = summary.get('metadata', {})
            if metadata:
                # Key decisions
                if 'key_decisions' in metadata and metadata['key_decisions']:
                    lines.append("**Key Decisions**:")
                    for decision in metadata['key_decisions']:
                        lines.append(f"- {decision}")
                    lines.append("")

                # Tasks completed count
                if 'tasks_completed' in metadata:
                    count = len(metadata['tasks_completed'])
                    lines.append(f"**Tasks Completed**: {count}")

                # Blockers resolved count
                if 'blockers_resolved' in metadata:
                    count = len(metadata['blockers_resolved'])
                    lines.append(f"**Blockers Resolved**: {count}")

                # Next steps (for handoff summaries)
                if 'next_steps' in metadata and metadata['next_steps']:
                    lines.append("\n**Next Steps**:")
                    for step in metadata['next_steps']:
                        lines.append(f"- {step}")

            lines.append("\n---\n")

        return "\n".join(lines)
