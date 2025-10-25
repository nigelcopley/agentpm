"""Google Gemini formatter for context payloads."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from ..base import LLMContextFormatter, TokenAllocation
from agentpm.core.context.assembly_service import ContextPayload
from agentpm.core.database.models.context import UnifiedSixW


class GoogleFormatter(LLMContextFormatter):
    """Render context payloads into Gemini-friendly markdown.

    Optimized for Google Gemini's 32K token context window with:
    - 55% system context (17.6K tokens)
    - 35% user content (11.2K tokens)
    - 10% assistant response buffer (3.2K tokens)

    Formatting optimized for Gemini's markdown processing:
    - Clear hierarchical headers
    - Bulleted lists for scanability
    - Concise summaries (SOP limited to 400 chars)
    - Compact temporal context (max 5 recent sessions)
    """

    provider = "google"
    _SOP_MAX_CHARS = 400  # Smaller than Anthropic (500) due to tighter token budget
    _MAX_TEMPORAL_SESSIONS = 5  # Limit recent sessions for token efficiency

    def format_task(
        self,
        payload: ContextPayload,
        *,
        token_allocation: Optional[TokenAllocation] = None,
        **metadata: object,
    ) -> str:
        """Format task context for Gemini.

        Args:
            payload: Complete context payload from assembly service
            token_allocation: Token budget allocation (optional)
            **metadata: Additional metadata (assembly_duration_ms, warnings, etc.)

        Returns:
            Markdown-formatted task context optimized for Gemini
        """
        task = payload.task or {}
        merged_6w = payload.merged_6w
        plugin_facts = payload.plugin_facts or {}
        temporal_context = payload.temporal_context or []

        # Use metadata if provided, otherwise fallback to payload
        assembly_duration_ms = metadata.get("assembly_duration_ms", payload.assembly_duration_ms)
        warnings: Sequence[str] = metadata.get("warnings") or payload.warnings or []

        lines: List[str] = []
        lines.append("")
        lines.append("## Task Context (Gemini Context Assembly)")
        lines.append("")

        # Task header - compact format
        if task:
            task_id = task.get("id")
            task_name = task.get("name", "Unknown Task")
            task_type = task.get("type", "unknown").lower()
            effort_hours = task.get("effort_hours")
            work_item_id = task.get("work_item_id")

            effort_text = f"{effort_hours}h" if effort_hours is not None else "n/a"
            lines.append(
                f"**Task #{task_id}**: {task_name} "
                f"({task_type}, {effort_text})"
            )
            if work_item_id:
                lines.append(f"**Work Item**: WI-{work_item_id}")
        else:
            lines.append("**Task**: Unknown")

        if payload.assigned_agent:
            lines.append(f"**Agent**: {payload.assigned_agent}")

        lines.append("")

        # 6W context - hierarchical merge
        if merged_6w:
            lines.extend(self._format_6w_context(merged_6w))

        # Plugin intelligence
        if plugin_facts:
            lines.extend(self._format_plugin_facts(plugin_facts))

        # Agent SOP - compressed for token efficiency
        if payload.agent_sop:
            sop = payload.agent_sop
            if len(sop) > self._SOP_MAX_CHARS:
                sop = sop[: self._SOP_MAX_CHARS] + "..."
            lines.append("### Agent SOP")
            lines.append("")
            lines.append(sop)
            lines.append("")

        # Temporal context - limited to recent sessions
        if temporal_context:
            lines.extend(
                self._format_temporal_context(
                    temporal_context[: self._MAX_TEMPORAL_SESSIONS]
                )
            )

        # Quality metrics
        lines.append(
            f"**Context Confidence**: {payload.confidence_score:.0%} "
            f"({payload.confidence_band.value.upper()})"
        )

        if assembly_duration_ms is not None:
            lines.append(f"**Assembly Time**: {assembly_duration_ms:.0f}ms")

        # Warnings - max 3 for brevity
        if warnings:
            lines.append("")
            lines.append("**Warnings**:")
            for warning in list(warnings)[:3]:
                lines.append(f"- {warning}")

        lines.append("")
        return "\n".join(lines)

    def format_session(
        self,
        history: str,
        *,
        token_allocation: Optional[TokenAllocation] = None,
        **metadata: object,
    ) -> str:
        """Format session context for Gemini.

        Args:
            history: Raw session history (fallback if no structured data)
            token_allocation: Token budget allocation (optional)
            **metadata: Structured context (project, active_work, etc.)

        Returns:
            Markdown-formatted session context optimized for Gemini
        """
        project = metadata.get("project") or {}
        tech_stack = metadata.get("tech_stack")
        active_work = metadata.get("active_work") or []
        active_task_contexts = metadata.get("active_task_contexts") or []
        static_context = metadata.get("static_context") or []
        handover = metadata.get("handover") or []

        has_structured = (
            project or tech_stack or active_work or active_task_contexts or static_context or handover
        )

        if not has_structured:
            return history or "_No recent session history available._"

        lines: List[str] = []
        lines.append("")
        lines.append("## Project Context (Gemini Context Assembly)")
        lines.append("")

        # Project header
        project_name = project.get("name")
        project_status = project.get("status")
        if project_name:
            lines.append(f"**Project**: {project_name}")
        if project_status:
            lines.append(f"**Status**: {project_status}")

        if tech_stack:
            lines.append(f"**Tech Stack**: {tech_stack}")

        lines.append("")

        # Active work - compact bullet format
        if active_work:
            lines.append("### Active Work")
            lines.append("")
            for item in active_work[:10]:  # Limit to 10 items for token efficiency
                wi_id = item.get("id")
                wi_name = item.get("name", "Unknown")
                wi_status = item.get("status", "unknown")
                wi_priority = item.get("priority")
                summary_count = item.get("summary_count")

                if wi_id is not None:
                    lines.append(f"- **WI-{wi_id}**: {wi_name}")
                else:
                    lines.append(f"- {wi_name}")

                detail_parts = []
                if wi_status:
                    detail_parts.append(f"Status: {wi_status}")
                if wi_priority is not None:
                    detail_parts.append(f"Priority: {wi_priority}")
                if summary_count:
                    detail_parts.append(f"History: {summary_count} sessions")

                if detail_parts:
                    lines.append("  - " + ", ".join(detail_parts))

            lines.append("")

        # Active task contexts
        if active_task_contexts:
            lines.extend(active_task_contexts)

        # Static context
        if static_context:
            lines.extend(static_context)

        # Handover notes
        if handover:
            lines.extend(handover)

        lines.append("Use `apm status` for complete dashboard")
        lines.append("")

        return "\n".join(lines)

    # ── Helpers ──────────────────────────────────────────────────────────────────

    def _format_6w_context(self, merged_6w: UnifiedSixW) -> List[str]:
        """Format hierarchical 6W context for Gemini."""
        lines = ["### Merged Context (Task → Work Item → Project)", ""]

        if merged_6w.who:
            lines.append(f"**WHO**: {merged_6w.who}")
        if merged_6w.what:
            lines.append(f"**WHAT**: {merged_6w.what}")
        if merged_6w.when:
            lines.append(f"**WHEN**: {merged_6w.when}")
        if merged_6w.where:
            lines.append(f"**WHERE**: {merged_6w.where}")
        if merged_6w.why:
            lines.append(f"**WHY**: {merged_6w.why}")
        if merged_6w.how:
            lines.append(f"**HOW**: {merged_6w.how}")

        lines.append("")
        return lines

    def _format_plugin_facts(self, plugin_facts: Dict[str, object]) -> List[str]:
        """Format plugin intelligence for Gemini."""
        lines = ["### Tech Stack", ""]
        for framework, facts in plugin_facts.items():
            if isinstance(facts, dict) and facts.get("version"):
                lines.append(f"- {framework}: {facts.get('version')}")
            else:
                lines.append(f"- {framework}")
        lines.append("")
        return lines

    def _format_temporal_context(self, summaries: Iterable[Dict[str, object]]) -> List[str]:
        """Format recent session history for Gemini.

        More compact than Anthropic version due to tighter token budget.
        """
        lines: List[str] = ["### Recent Sessions", ""]
        for summary in summaries:
            session_type = summary.get("summary_type", "session")
            session_date = summary.get("session_date")
            summary_text = summary.get("summary_text", "")
            metadata = summary.get("metadata") or {}

            header = f"- {session_type.title()}"
            if session_date:
                header += f" ({session_date})"
            lines.append(header)

            if summary_text:
                # Truncate long summaries for token efficiency
                truncated_text = summary_text.strip()
                if len(truncated_text) > 200:
                    truncated_text = truncated_text[:200] + "..."
                lines.append(f"  {truncated_text}")

            # Compact metadata rendering
            if metadata:
                key_decisions = metadata.get("key_decisions") or []
                if key_decisions:
                    lines.append("  Key Decisions:")
                    for decision in key_decisions[:2]:  # Max 2 decisions per session
                        lines.append(f"    • {decision}")

                tasks_completed = metadata.get("tasks_completed")
                if tasks_completed:
                    lines.append(f"  Tasks Completed: {len(tasks_completed)}")

                blockers_resolved = metadata.get("blockers_resolved")
                if blockers_resolved:
                    lines.append(f"  Blockers Resolved: {len(blockers_resolved)}")

                next_steps = metadata.get("next_steps") or []
                if next_steps:
                    lines.append("  Next Steps:")
                    for step in next_steps[:2]:  # Max 2 next steps per session
                        lines.append(f"    • {step}")

            lines.append("")

        if len(lines) == 2:
            # No sessions appended; remove placeholder
            return []
        return lines
