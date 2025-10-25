"""
Hook Integration Module - Context Assembly for Claude Code Hooks

Provides helper functions for integrating ContextAssemblyService with Claude Code hooks.
Handles context assembly, formatting, and graceful degradation for hook execution.

Performance Targets:
- SessionStart: <2 seconds (background)
- TaskStart: <200ms (critical path)
- UserPromptSubmit: <100ms (real-time)

Design Pattern: Adapter layer between Context Agent and Hooks System
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentpm.core.database import DatabaseService
from agentpm.core.context.assembly_service import (
    ContextAssemblyService,
    ContextAssemblyError,
    ContextPayload,
)
from agentpm.core.database.models.context import UnifiedSixW
from agentpm.providers import get_provider
from agentpm.providers.anthropic import AnthropicAdapter
from agentpm.providers.anthropic.formatter import AnthropicFormatter


def get_llm_formatter(provider_name: str):
    """Get LLM formatter for the specified provider."""
    if provider_name == "anthropic":
        return AnthropicFormatter()
    return None


class ContextHookAdapter:
    """
    Adapter for integrating Context Assembly with Claude Code hooks.

    Responsibilities:
    - Initialize DatabaseService and ContextAssemblyService
    - Format context payloads for hook output
    - Handle graceful degradation on failures
    - Track performance for SLA monitoring

    Example:
        adapter = ContextHookAdapter()
        context_text = adapter.format_task_context(task_id=45)
        print(context_text)  # Injected into Claude's context
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize context hook adapter.

        Args:
            project_root: Project root directory (default: auto-detect from cwd)
        """
        self.project_root = project_root or self._find_project_root()
        self.db_path = self.project_root / ".agentpm" / "data" / "agentpm.db"

        # Initialize services (lazy loading for performance)
        self._db: Optional[DatabaseService] = None
        self._assembly_service: Optional[ContextAssemblyService] = None

    @property
    def db(self) -> DatabaseService:
        """Lazy-load database service."""
        if self._db is None:
            self._db = DatabaseService(str(self.db_path))
        return self._db

    @property
    def assembly_service(self) -> ContextAssemblyService:
        """Lazy-load context assembly service."""
        if self._assembly_service is None:
            self._assembly_service = ContextAssemblyService(
                db=self.db,
                project_path=self.project_root,
                enable_cache=False  # Cache disabled for MVP
            )
        return self._assembly_service

    # ─────────────────────────────────────────────────────────────────
    # SessionStart Hook - Background context loading
    # ─────────────────────────────────────────────────────────────────

    def format_session_start_context(self) -> str:
        """
        Format session start context (project-level overview).

        Performance: <2 seconds (non-blocking background)

        Returns:
            Formatted context text for hook output

        Example output:
            ## 🎯 Project Context Loaded

            **Project**: APM (Agent Project Manager) (active)
            **Tech Stack**: Python 3.9+, SQLite, Click, Pydantic

            ### Recent Work
            - WI-31: Context Delivery Agent (70% complete, 3 tasks active)
            - WI-27: Rules System (review, 2 blockers)

            See `apm status` for full dashboard
        """
        lines = []
        session_project: Optional[Dict[str, Any]] = None
        session_tech_stack: Optional[str] = None
        session_active_work: List[Dict[str, Any]] = []
        session_active_task_contexts: List[str] = []
        session_static_context: List[str] = []
        session_handover: List[str] = []

        try:
            # Load project information
            from agentpm.core.database.methods import projects as project_methods
            projects = project_methods.list_projects(self.db)

            if not projects:
                return self._format_no_project_warning()

            project = projects[0]  # Single project per workspace (MVP)
            session_project = {
                "name": project.name,
                "status": project.status.value,
            }

            lines.append("")
            lines.append("## 🎯 Project Context Loaded (Context Delivery Agent)")
            lines.append("")
            lines.append(f"**Project**: {project.name}")
            lines.append(f"**Status**: {project.status.value}")

            # Load tech stack from project context (if available)
            tech_stack = self._load_tech_stack(project.id)
            if tech_stack:
                lines.append(f"**Tech Stack**: {tech_stack}")
            session_tech_stack = tech_stack

            lines.append("")

            # Load recent work items with session summaries
            recent_work = self._load_recent_work_items(limit=3)
            if recent_work:
                lines.append("### 📊 Active Work")
                lines.append("")
                for wi, summary_count in recent_work:
                    session_active_work.append(
                        {
                            "id": wi.id,
                            "name": wi.name,
                            "status": wi.status.value,
                            "priority": wi.priority,
                            "summary_count": summary_count,
                        }
                    )
                    lines.append(f"- **WI-{wi.id}**: {wi.name}")
                    lines.append(f"  - Status: {wi.status.value}, Priority: {wi.priority}")
                    if summary_count > 0:
                        lines.append(f"  - History: {summary_count} sessions")

            lines.append("")

            # NEW: Load rich context for active tasks
            active_task_contexts = self._load_active_task_contexts()
            if active_task_contexts:
                session_active_task_contexts = active_task_contexts
                lines.extend(active_task_contexts)

            # NEW (Task #363): Load static project context from .claude/CONTEXT.md
            static_context = self._load_static_project_context()
            if static_context:
                session_static_context = static_context
                lines.extend(static_context)

            # NEW (Task #357): Database-driven handover from last session
            handover = self._load_database_handover()
            if handover:
                session_handover = handover
                lines.extend(handover)

            lines.append("Use `apm status` for complete dashboard")
            lines.append("")

            formatter = get_llm_formatter("anthropic")
            if formatter:
                try:
                    formatted_output = formatter.format_session(
                        "\n".join(lines),
                        project=session_project,
                        tech_stack=session_tech_stack,
                        active_work=session_active_work,
                        active_task_contexts=session_active_task_contexts,
                        static_context=session_static_context,
                        handover=session_handover,
                    )
                    return formatted_output
                except Exception:
                    pass

        except Exception as e:
            # Graceful degradation - return minimal context
            return self._format_error_fallback("SessionStart", str(e))

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────
    # TaskStart Hook - CRITICAL PATH context assembly
    # ─────────────────────────────────────────────────────────────────

    def format_task_context(self, task_id: int, agent_role: Optional[str] = None) -> str:
        """
        Format complete task context using ContextAssemblyService.

        Performance: <200ms (CRITICAL - blocks workflow)

        Args:
            task_id: Task ID to assemble context for
            agent_role: Optional agent role override

        Returns:
            Formatted context text with hierarchical 6W, plugin facts, SOP

        Example output:
            ## 🎯 Task Context Assembled

            **Task #45**: Implement Context Agent Hooks (implementation, 4.0h)
            **Work Item**: WI-31 Context Delivery Agent
            **Agent**: python-expert

            ### 🔍 Merged Context (Task → Work Item → Project)

            **WHO**: python-expert (core developer)
            **WHAT**: Integrate Context Agent with Hooks System
            **WHEN**: Session start, task start, user prompt
            **WHERE**: agentpm/hooks/implementations/
            **WHY**: Enable automatic context delivery
            **HOW**: Use ContextAssemblyService, enhance existing hooks

            ### 🔌 Tech Stack
            - Python 3.9+, Pydantic 2.5+
            - Click 8.1.7+ (CLI framework)

            ### 📝 Agent SOP
            [Python Expert methodology...]

            ### 🕒 Recent Sessions
            - 2 hours ago: "Core implementation complete"
            - 4 hours ago: "Started integration work"

            **Confidence**: 85% (GREEN)
        """
        try:
            start_time = datetime.now()

            # Assemble complete context using Context Agent
            payload = self.assembly_service.assemble_task_context(
                task_id=task_id,
                agent_role=agent_role
            )

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            formatter = get_llm_formatter("anthropic")
            formatted_output: Optional[str] = None
            token_allocation = None

            if formatter:
                try:
                    adapter = AnthropicAdapter()
                    token_allocation = adapter.plan_tokens(payload)
                except Exception:
                    token_allocation = None

                try:
                    formatted_output = formatter.format_task(
                        payload,
                        token_allocation=token_allocation,
                        assembly_duration_ms=duration_ms,
                        warnings=payload.warnings or [],
                    )
                except Exception:
                    formatted_output = None

            if not formatted_output:
                formatted_output = self._format_task_payload_fallback(
                    payload, duration_ms=duration_ms
                )

            return formatted_output

        except ContextAssemblyError as e:
            # Critical error - task context unavailable
            return self._format_error_fallback("TaskStart", f"Context assembly failed: {e}")

        except Exception as e:
            # Unexpected error - graceful degradation
            return self._format_error_fallback("TaskStart", str(e))

    # ─────────────────────────────────────────────────────────────────
    # UserPromptSubmit Hook - Real-time entity context injection
    # ─────────────────────────────────────────────────────────────────

    def inject_entity_context(self, entity_type: str, entity_id: int) -> str:
        """
        Inject just-in-time context for mentioned entity.

        Performance: <100ms (real-time, user is waiting)

        Args:
            entity_type: 'work_item' or 'task'
            entity_id: Entity ID

        Returns:
            Compact context summary

        Example output:
            📋 **WI-31 Context**:
            - Context Delivery Agent (in_progress, P0-CRITICAL)
            - 3 active tasks, 70% complete
            - Recent: "Integration work started" (2h ago)
        """
        lines = []

        try:
            if entity_type == 'work_item':
                lines.extend(self._inject_work_item_context(entity_id))
            elif entity_type == 'task':
                lines.extend(self._inject_task_context(entity_id))
            else:
                return ""  # Unknown entity type

        except Exception as e:
            # Graceful degradation - return minimal context
            return f"⚠️ Context unavailable for {entity_type} {entity_id}"

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────
    # PRIVATE - Formatting helpers
    # ─────────────────────────────────────────────────────────────────

    def _format_task_payload_fallback(
        self,
        payload: ContextPayload,
        *,
        assembly_duration_ms: Optional[float] = None,
    ) -> str:
        """Fallback implementation that mirrors legacy hook formatting."""
        lines: List[str] = []
        task = payload.task or {}

        lines.append("")
        lines.append("## 🎯 Task Context Assembled (Context Delivery Agent)")
        lines.append("")

        task_id = task.get("id")
        task_name = task.get("name", "Unknown Task")
        task_type = task.get("type", "unknown")
        effort_hours = task.get("effort_hours", "n/a")
        work_item_id = task.get("work_item_id")

        lines.append(
            f"**Task #{task_id}**: {task_name} ({task_type}, {effort_hours}h)"
        )
        if work_item_id:
            lines.append(f"**Work Item**: WI-{work_item_id}")

        if payload.assigned_agent:
            lines.append(f"**Agent**: {payload.assigned_agent}")

        lines.append("")

        if payload.merged_6w:
            lines.extend(self._format_6w_context(payload.merged_6w))

        if payload.plugin_facts:
            lines.extend(self._format_plugin_facts(payload.plugin_facts))

        if payload.agent_sop:
            sop = payload.agent_sop
            if len(sop) > 500:
                sop = sop[:500] + "..."
            lines.append("### 📝 Agent SOP")
            lines.append("")
            lines.append(sop)
            lines.append("")

        if payload.temporal_context:
            lines.extend(self._format_temporal_context(payload.temporal_context))

        lines.append(
            f"**Context Confidence**: {payload.confidence_score:.0%} "
            f"({payload.confidence_band.value.upper()})"
        )
        if assembly_duration_ms is not None:
            lines.append(f"**Assembly Time**: {assembly_duration_ms:.0f}ms")

        if payload.warnings:
            lines.append("")
            lines.append("⚠️ **Warnings**:")
            for warning in payload.warnings[:3]:
                lines.append(f"- {warning}")

        lines.append("")
        return "\n".join(lines)

    def _format_6w_context(self, merged_6w: UnifiedSixW) -> List[str]:
        """Format merged 6W context - platform agnostic structured format."""
        lines = []
        lines.append("### 🔍 Merged Context (Task → Work Item → Project)")
        lines.append("")

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

    def _format_plugin_facts(self, plugin_facts: Dict[str, Any]) -> List[str]:
        """Format plugin facts (tech stack) - platform agnostic structured format."""
        lines = []
        lines.append("### 🔌 Tech Stack")
        lines.append("")

        for framework, facts in plugin_facts.items():
            if isinstance(facts, dict) and 'version' in facts:
                lines.append(f"- {framework}: {facts.get('version')}")
            else:
                lines.append(f"- {framework}")

        lines.append("")
        return lines

    def _format_temporal_context(self, temporal_context: List[Dict[str, Any]]) -> List[str]:
        """Format temporal context (session summaries) - platform agnostic structured format."""
        lines = []
        lines.append("### 🕒 Recent Sessions")
        lines.append("")

        for summary in temporal_context[:3]:  # Limit to 3 recent summaries
            text = summary.get('summary_text', '')
            created = summary.get('created_at')

            if created:
                # Calculate time ago
                delta = datetime.now() - created
                hours_ago = int(delta.total_seconds() / 3600)
                time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{delta.days}d ago"
                lines.append(f"- {time_str}: \"{text[:60]}...\"" if len(text) > 60 else f"- {time_str}: \"{text}\"")
            else:
                lines.append(f"- {text[:60]}..." if len(text) > 60 else f"- {text}")

        lines.append("")
        return lines

    def _load_tech_stack(self, project_id: int) -> Optional[str]:
        """Load tech stack from project context."""
        try:
            from agentpm.core.database.methods import contexts as context_methods
            from agentpm.core.database.enums import EntityType

            project_ctx = context_methods.get_entity_context(
                self.db,
                EntityType.PROJECT,
                project_id
            )

            if project_ctx and project_ctx.confidence_factors:
                plugin_facts = project_ctx.confidence_factors.get('plugin_facts', {})

                # Extract detected technologies with confidence >0.6
                detected_techs = plugin_facts.get('detected_technologies', {})
                high_confidence_techs = [
                    tech for tech, data in detected_techs.items()
                    if isinstance(data, dict) and data.get('confidence', 0) > 0.6
                ]

                # Extract enrichment data for version info
                enrichment = plugin_facts.get('plugin_enrichment', {})

                # Build formatted tech stack
                tech_list = []
                for tech in high_confidence_techs[:6]:  # Limit to 6 frameworks
                    # Check for version info in enrichment
                    for plugin_id, enrichment_data in enrichment.items():
                        if isinstance(enrichment_data, dict):
                            # Python version
                            if tech == 'python' and 'python_version' in enrichment_data:
                                tech_list.append(f"Python {enrichment_data['python_version']}+")
                                break
                            # Framework names (capitalize)
                            elif tech in plugin_id.lower():
                                tech_list.append(tech.capitalize())
                                break
                    else:
                        # No enrichment found, just capitalize
                        tech_list.append(tech.capitalize())

                if tech_list:
                    return ", ".join(tech_list)

            return None

        except Exception:
            return None

    def _load_recent_work_items(self, limit: int = 3) -> List[tuple]:
        """Load recent work items with session summary counts."""
        try:
            from agentpm.core.database.methods import work_items as wi_methods
            from agentpm.core.database.methods import work_item_summaries as summary_methods
            from agentpm.core.database.enums import WorkItemStatus

            # Get active work items
            active_wis = wi_methods.list_work_items(self.db, status=WorkItemStatus.ACTIVE)
            review_wis = wi_methods.list_work_items(self.db, status=WorkItemStatus.REVIEW)
            all_wis = (active_wis + review_wis)[:limit]

            # Get summary counts for each
            results = []
            for wi in all_wis:
                summaries = summary_methods.list_summaries(self.db, work_item_id=wi.id)
                results.append((wi, len(summaries)))

            return results

        except Exception:
            return []

    def _load_active_task_contexts(self) -> List[str]:
        """Load rich context for active tasks using ContextAssemblyService.
        
        NEW: Enhanced session-start context with hierarchical task context.
        Performance: <1 second (non-blocking background)
        
        Returns:
            List of formatted context lines for active tasks
        """
        lines = []
        
        try:
            from agentpm.core.database.methods import tasks as task_methods
            from agentpm.core.database.enums import TaskStatus
            
            # Get active tasks (in_progress only for session start)
            active_tasks = task_methods.list_tasks(self.db, status=TaskStatus.ACTIVE, limit=2)
            
            if not active_tasks:
                return []  # No active tasks
                
            lines.append("### 🎯 Current Task Context (Rich Assembly)")
            lines.append("")
            
            for task in active_tasks:
                try:
                    # Assemble rich context for this task
                    start_time = datetime.now()
                    payload = self.assembly_service.assemble_task_context(task.id)
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Task header
                    lines.append(f"**Task #{task.id}**: {task.name} "
                                f"({task.type.value}, {task.effort_hours}h)")
                    lines.append(f"**Work Item**: WI-{task.work_item_id}")
                    
                    if payload.assigned_agent:
                        lines.append(f"**Agent**: {payload.assigned_agent}")
                    
                    lines.append("")
                    
                    # Merged 6W context (hierarchical)
                    if payload.merged_6w:
                        lines.extend(self._format_6w_context(payload.merged_6w))
                    
                    # Plugin facts (tech stack)
                    if payload.plugin_facts:
                        lines.extend(self._format_plugin_facts(payload.plugin_facts))
                    
                    # Agent SOP (if available, truncated)
                    if payload.agent_sop:
                        lines.append("#### 📝 Agent SOP")
                        lines.append("")
                        sop_preview = payload.agent_sop[:300] + "..." if len(payload.agent_sop) > 300 else payload.agent_sop
                        lines.append(sop_preview)
                        lines.append("")
                    
                    # Temporal context (session summaries)
                    if payload.temporal_context:
                        lines.extend(self._format_temporal_context(payload.temporal_context))
                    
                    # Confidence score
                    lines.append(f"**Context Confidence**: {payload.confidence_score:.0%} "
                                f"({payload.confidence_band.value.upper()})")
                    lines.append(f"**Assembly Time**: {duration_ms:.0f}ms")
                    
                    # Warnings (limit to 2)
                    if payload.warnings:
                        lines.append("")
                        lines.append("⚠️ **Warnings**:")
                        for warning in payload.warnings[:2]:
                            lines.append(f"- {warning}")
                    
                    lines.append("")
                    
                except Exception as e:
                    # Graceful degradation for individual task
                    lines.append(f"⚠️ Context assembly failed for Task #{task.id}: {e}")
                    lines.append("")
                    continue
                    
        except Exception as e:
            # Graceful degradation - return empty list
            print(f"⚠️ Active task context loading failed: {e}", file=sys.stderr)
            return []
            
        return lines

    def _load_static_project_context(self) -> List[str]:
        """Load static project context from .claude/CONTEXT.md

        NEW (Task #363): Pattern from disler/claude-code-hooks-mastery
        Static context: Architecture, patterns, constraints (doesn't change frequently)
        Character limit: 2000 chars to prevent token bloat
        """
        lines = []

        try:
            context_file = self.project_root / ".claude" / "CONTEXT.md"

            if context_file.exists():
                with open(context_file) as f:
                    static_context = f.read()

                # Cap at 2000 characters (token safety)
                if len(static_context) > 2000:
                    static_context = static_context[:2000] + "\n\n... (truncated, see .claude/CONTEXT.md for full content)"

                lines.append("### 📄 Project Context")
                lines.append("")
                lines.append(static_context)
                lines.append("")

            return lines

        except Exception:
            return []  # Graceful degradation

    def _load_database_handover(self) -> List[str]:
        """Load handover context from database (last session metadata).

        NEW (Task #357): Replaces NEXT-SESSION.md file-based handover
        NEW (Task #363): Character limit (5000 chars) for token safety
        """
        lines = []

        try:
            from agentpm.core.database.methods import sessions as session_methods
            from agentpm.core.database.methods import work_items as wi_methods
            from agentpm.core.database.methods import tasks as task_methods
            import subprocess

            # Get last completed session for handover context
            project_id = 1  # Single project per workspace (MVP)
            sessions = session_methods.list_sessions(self.db, project_id=project_id, limit=1)

            if not sessions:
                return []  # No previous session

            last_session = sessions[0]
            metadata = last_session.metadata

            lines.append("### 📝 Last Session Context")
            lines.append("")

            # Show what was worked on
            if metadata.work_items_touched:
                lines.append(f"**Work Items**: {len(metadata.work_items_touched)} touched")
            if metadata.tasks_completed:
                lines.append(f"**Tasks**: {len(metadata.tasks_completed)} completed")
            if metadata.git_commits:
                lines.append(f"**Commits**: {len(metadata.git_commits)} commits")

            # Show active items for next session
            if metadata.active_work_items:
                lines.append("")
                lines.append(f"**Continue**: {len(metadata.active_work_items)} active work items")

            lines.append("")

            # Show uncommitted changes (current state)
            try:
                result = subprocess.run(
                    ['git', 'status', '--short'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    cwd=self.project_root
                )
                if result.returncode == 0 and result.stdout.strip():
                    lines.append("**⚠️ Uncommitted Changes**:")
                    uncommitted_lines = result.stdout.strip().split('\n')[:5]  # Limit to 5 files
                    for line in uncommitted_lines:
                        lines.append(f"  - `{line.strip()}`")
                    lines.append("")
            except Exception:
                pass

            # NEW (Task #363): Character limit for token safety (pattern from disler's hook)
            handover_text = "\n".join(lines)
            if len(handover_text) > 5000:
                # Truncate and add note
                truncated = handover_text[:5000]
                lines = truncated.split('\n')
                lines.append("")
                lines.append("... (handover truncated at 5000 chars, use `apm session show` for full context)")

            return lines

        except Exception:
            return []  # Graceful degradation - no handover section

    def _inject_work_item_context(self, work_item_id: int) -> List[str]:
        """Inject work item context (compact format)."""
        from agentpm.core.database.methods import work_items as wi_methods
        from agentpm.core.database.methods import work_item_summaries as summary_methods

        lines = []

        wi = wi_methods.get_work_item(self.db, work_item_id)
        if not wi:
            return [f"⚠️ Work item {work_item_id} not found"]

        lines.append(f"📋 **WI-{work_item_id} Context**:")
        lines.append(f"- {wi.name} ({wi.status.value}, {wi.priority})")

        # Recent summary
        summaries = summary_methods.list_work_item_summaries(self.db, work_item_id, limit=1)
        if summaries:
            summary = summaries[0]
            text = summary.summary_text[:50] + "..." if len(summary.summary_text) > 50 else summary.summary_text
            lines.append(f"- Recent: \"{text}\"")

        return lines

    def _inject_task_context(self, task_id: int) -> List[str]:
        """Inject task context (compact format)."""
        from agentpm.core.database.methods import tasks as task_methods

        lines = []

        task = task_methods.get_task(self.db, task_id)
        if not task:
            return [f"⚠️ Task {task_id} not found"]

        lines.append(f"📝 **Task #{task_id} Context**:")
        lines.append(f"- {task.name} ({task.type.value}, {task.status.value})")
        lines.append(f"- Effort: {task.effort_hours}h, Work Item: WI-{task.work_item_id}")

        return lines

    def _format_no_project_warning(self) -> str:
        """Format warning when no project found."""
        return "\n⚠️ No APM project initialized. Run `apm init` first.\n"

    def _format_error_fallback(self, hook_name: str, error_msg: str) -> str:
        """Format graceful degradation message on error."""
        lines = []
        lines.append("")
        lines.append(f"⚠️ Context loading failed ({hook_name})")
        lines.append(f"Error: {error_msg}")
        lines.append("")
        lines.append("Continuing without context assembly...")
        lines.append("")
        return "\n".join(lines)

    def _find_project_root(self) -> Path:
        """Find APM project root from current directory."""
        cwd = Path.cwd()

        # Check current directory
        if (cwd / ".agentpm").exists():
            return cwd

        # Check parent directories (up to 3 levels)
        for parent in [cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]:
            if (parent / ".agentpm").exists():
                return parent

        # Default to cwd (will fail gracefully if no .agentpm)
        return cwd
