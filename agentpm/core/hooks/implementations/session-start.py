#!/usr/bin/env python3
"""
Claude Code SessionStart Hook - Python Version

Loads APM project context when Claude Code session starts.
Output is injected into Claude's context automatically.

Performance: ~200ms (faster than bash with subprocess overhead)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentpm.core.database import DatabaseService
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.enums import WorkItemStatus, TaskStatus, Phase

# NEW: Import Context Agent integration
from agentpm.core.hooks.context_integration import ContextHookAdapter

# NEW (Task #375): Phase-based orchestrator routing (O(1) lookup)
PHASE_TO_ORCHESTRATOR = {
    Phase.D1_DISCOVERY: 'definition-orch',      # Discovery/definition phase
    Phase.P1_PLAN: 'planning-orch',             # Planning phase
    Phase.I1_IMPLEMENTATION: 'implementation-orch',  # Implementation phase
    Phase.R1_REVIEW: 'review-test-orch',        # Review/test phase
    Phase.O1_OPERATIONS: 'release-ops-orch',    # Operations/release phase
    Phase.E1_EVOLUTION: 'evolution-orch'        # Evolution/improvement phase
}


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def get_database() -> DatabaseService:
    """Get database service instance."""
    db_path = PROJECT_ROOT / ".agentpm" / "data" / "agentpm.db"
    return DatabaseService(str(db_path))


def determine_orchestrator(db: DatabaseService) -> tuple[str | None, dict | None]:
    """
    Determine which orchestrator to route to based on active work item phase.

    NEW (Task #375): O(1) phase-based routing replacing metadata.gates parsing.

    Performance: <5ms (dictionary lookup + single DB query)

    Returns:
        Tuple of (orchestrator_name, work_item_dict) or (None, None) if no routing needed

    Example:
        orchestrator, wi = determine_orchestrator(db)
        if orchestrator:
            print(f"Route to: {orchestrator} for WI-{wi['id']}")
    """
    try:
        # Get highest priority active work item
        active_wis = wi_methods.list_work_items(db, status=WorkItemStatus.ACTIVE)
        review_wis = wi_methods.list_work_items(db, status=WorkItemStatus.REVIEW)
        all_active = active_wis + review_wis

        if not all_active:
            return None, None

        # Get highest priority (lowest priority number = highest priority)
        work_item = min(all_active, key=lambda wi: wi.priority)

        if not work_item.phase:
            return None, None

        # O(1) lookup
        orchestrator = PHASE_TO_ORCHESTRATOR.get(work_item.phase)

        if orchestrator:
            # Return orchestrator with minimal work item context
            wi_dict = {
                'id': work_item.id,
                'name': work_item.name,
                'type': work_item.type.value,
                'status': work_item.status.value,
                'phase': work_item.phase.value,
                'priority': work_item.priority
            }
            return orchestrator, wi_dict

        return None, None

    except Exception as e:
        # Graceful degradation - routing is non-critical
        print(f"⚠️ Orchestrator routing failed (non-critical): {e}", file=sys.stderr)
        return None, None


def create_session_record(session_id: str) -> None:
    """Create session record in database and emit SESSION_STARTED event.

    NEW (WI-35 Task #173): Integrates with EventBus for automatic event capture.

    Graceful degradation: If database write fails, log error but continue.
    Session tracking is nice-to-have, not critical for hook operation.
    """
    try:
        db = get_database()
        from agentpm.core.database.models.session import Session, SessionTool, SessionType
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.methods import projects as project_methods
        from agentpm.core.sessions.event_bus import EventBus
        from agentpm.core.events.models import Event, EventType, EventCategory, EventSeverity
        from datetime import datetime
        import subprocess

        # Get project_id (assume first project for now)
        projects = project_methods.list_projects(db)
        if not projects:
            print("⚠️ No project found, skipping session tracking", file=sys.stderr)
            return

        project_id = projects[0].id

        # Get developer info from git config
        try:
            name_result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True,
                text=True,
                timeout=1
            )
            email_result = subprocess.run(
                ['git', 'config', 'user.email'],
                capture_output=True,
                text=True,
                timeout=1
            )
            developer_name = name_result.stdout.strip() if name_result.returncode == 0 else None
            developer_email = email_result.stdout.strip() if email_result.returncode == 0 else None
        except Exception:
            developer_name = None
            developer_email = None

        # Create session
        session = Session(
            session_id=session_id,
            project_id=project_id,
            tool_name=SessionTool.CLAUDE_CODE,
            llm_model=None,  # Could parse from hook input in future
            start_time=datetime.now(),
            session_type=SessionType.CODING,  # Default
            developer_name=developer_name,
            developer_email=developer_email
        )

        created_session = session_methods.create_session(db, session)

        # Set as current session for agent tracking
        session_methods.set_current_session(db, session_id)

        # NEW (WI-35): Emit SESSION_STARTED event
        try:
            event_bus = EventBus(db)
            event = Event(
                event_type=EventType.SESSION_STARTED,
                event_category=EventCategory.SESSION_LIFECYCLE,
                event_severity=EventSeverity.INFO,
                session_id=created_session.id,
                source='session_start_hook',
                event_data={
                    'session_uuid': session_id,
                    'tool': 'claude_code',
                    'session_type': 'coding',
                    'developer': developer_name
                },
                project_id=project_id
            )
            event_bus.emit(event)
            event_bus.shutdown(timeout=2.0)  # Graceful shutdown
            print(f"✅ SESSION_STARTED event emitted", file=sys.stderr)
        except Exception as e:
            # Event emission failure is non-critical
            print(f"⚠️ Event emission failed (non-critical): {e}", file=sys.stderr)

        print(f"✅ Session {session_id} tracked in database", file=sys.stderr)
        print(f"✅ Current session set to {session_id}", file=sys.stderr)

    except Exception as e:
        # Graceful degradation - log but don't fail
        print(f"⚠️ Session tracking failed (non-critical): {e}", file=sys.stderr)


def format_context() -> str:
    """
    Format AIPM context for Claude using Context Delivery Agent.

    NEW (Task #356): Instructs Claude to use ContextAssemblyService for full context
    Integration: Uses ContextHookAdapter for session start context assembly
    Fallback: If Context Agent fails, use original manual context loading
    """
    # Try Context Agent first (Task #147, enhanced by Task #356)
    try:
        adapter = ContextHookAdapter(PROJECT_ROOT)
        context_agent_output = adapter.format_session_start_context()

        # Prepend session header and append reminders
        lines = []
        lines.append("")
        lines.append("---")
        lines.append(f"**Session Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append(context_agent_output)

        # DEPRECATED (Task #357): NEXT-SESSION.md replaced by database session management
        # Database-driven handover now provided via work_item_summaries queries
        # Rollback: Uncomment lines below to restore file-based handover
        #
        # handover_path = PROJECT_ROOT / "NEXT-SESSION.md"
        # if handover_path.exists():
        #     lines.append("### 📝 Handover from Previous Session")
        #     lines.append("")
        #     try:
        #         with open(handover_path) as f:
        #             handover = f.read()
        #             lines.append(handover)
        #     except Exception as e:
        #         lines.append(f"⚠️ Error loading handover: {e}")
        #     lines.append("")

        # NEW (Task #356): Instruct Claude to use Context Delivery Agent for deep context
        lines.append("### 🤖 Context Delivery Agent Available")
        lines.append("")
        lines.append("**For deep hierarchical context** (Project → Work Item → Task):")
        lines.append("- The Context Delivery Agent can assemble complete context with:")
        lines.append("  - Hierarchical 6W merging (task > work_item > project)")
        lines.append("  - Plugin facts and code amalgamations")
        lines.append("  - Agent SOPs and temporal context (session summaries)")
        lines.append("  - Confidence scoring (RED/YELLOW/GREEN quality assessment)")
        lines.append("")
        lines.append("**Usage**: `ContextAssemblyService` is available in `agentpm/core/context/assembly_service.py`")
        lines.append("")
        lines.append("**Example**:")
        lines.append("```python")
        lines.append("from agentpm.core.context.assembly_service import ContextAssemblyService")
        lines.append("assembler = ContextAssemblyService(db, project_path)")
        lines.append("context = assembler.assemble_task_context(task_id=355)")
        lines.append("# Returns: Complete hierarchical context with confidence scores")
        lines.append("```")
        lines.append("")

        # NEW (Task #375): Phase-based orchestrator routing
        try:
            db = get_database()
            orchestrator, work_item = determine_orchestrator(db)
            if orchestrator and work_item:
                lines.append("### 🎯 Recommended Orchestrator")
                lines.append("")
                lines.append(f"**Current Work**: WI-{work_item['id']} - {work_item['name']}")
                lines.append(f"**Phase**: {work_item['phase']} ({work_item['type']})")
                lines.append(f"**Route To**: `{orchestrator}`")
                lines.append("")
                lines.append(f"**Usage**: Delegate phase-specific work to `{orchestrator}` via Task tool")
                lines.append("")
        except Exception as e:
            # Graceful degradation - routing is non-critical
            print(f"⚠️ Orchestrator routing display failed: {e}", file=sys.stderr)

        # Append critical reminders
        lines.extend(_format_critical_reminders())
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    except Exception as e:
        # Fallback to original manual context loading
        print(f"⚠️ Context Agent unavailable, using fallback: {e}", file=sys.stderr)
        return _format_context_fallback()


def _format_context_fallback() -> str:
    """Original manual context loading (fallback if Context Agent fails)."""
    db = get_database()
    lines = []

    lines.append("")
    lines.append("---")
    lines.append("## 🤖 AIPM Session Context Loaded")
    lines.append("")
    lines.append(f"**Session Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Project Info
    try:
        projects = project_methods.list_projects(db)
        if projects:
            project = projects[0]
            lines.append(f"**Project**: {project.name} ({project.status.value})")
    except Exception:
        lines.append("**Project**: APM (Agent Project Manager)")

    lines.append("")

    # Load handover from previous session
    handover_path = PROJECT_ROOT / "NEXT-SESSION.md"
    if handover_path.exists():
        lines.append("### 📝 Handover from Previous Session")
        lines.append("")
        try:
            with open(handover_path) as f:
                handover = f.read()
                lines.append(handover)
        except Exception as e:
            lines.append(f"⚠️ Error loading handover: {e}")
        lines.append("")
    else:
        # No handover - show current state
        lines.append("### 📊 Current Project State")
        lines.append("")

        # Active Work Items Summary
        try:
            active_wis = wi_methods.list_work_items(db, status=WorkItemStatus.ACTIVE)
            review_wis = wi_methods.list_work_items(db, status=WorkItemStatus.REVIEW)
            all_active = active_wis + review_wis

            if all_active:
                lines.append(f"**Active Work Items** ({len(all_active)}):")
                for wi in all_active[:3]:
                    lines.append(f"- WI-{wi.id}: {wi.name} ({wi.type.value}, {wi.status.value})")
                lines.append("")
        except Exception:
            pass

        # Active Tasks Summary
        try:
            all_wis = wi_methods.list_work_items(db)
            all_tasks = []
            for wi in all_wis:
                tasks = task_methods.list_tasks(db, work_item_id=wi.id)
                active = [t for t in tasks if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)]
                all_tasks.extend(active)

            if all_tasks:
                lines.append(f"**Active Tasks** ({len(all_tasks)}):")
                for task in all_tasks[:3]:
                    lines.append(f"- Task #{task.id}: {task.name} ({task.type.value}, {task.status.value})")
                lines.append("")
        except Exception:
            pass

    # Critical Reminders
    lines.extend(_format_critical_reminders())
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def _format_critical_reminders() -> list:
    """Format critical reminders (reusable across fallback and Context Agent)."""
    lines = []
    lines.append("### ⚠️ Critical Reminders")
    lines.append("")
    lines.append("**AIPM Workflow** (README.md):")
    lines.append("- ✅ Use specialist agents via Task tool (never implement directly!)")
    lines.append("- ✅ Commit frequently (every 30-60 min)")
    lines.append("- ✅ Time-boxing STRICT: IMPLEMENTATION ≤4h")
    lines.append("- ✅ Testing >90% coverage (CI-004)")
    lines.append("- ✅ Three-layer pattern: Models → Adapters → Methods")
    lines.append("")
    lines.append("**State Transitions**:")
    lines.append("- Work item must be in_progress before tasks can start")
    lines.append("- Use: `apm work-item start <id>` then `apm task start <id>`")
    lines.append("- REVIEW state = different agent reviews (no self-approval)")
    lines.append("")
    lines.append("**Quick Commands**:")
    lines.append("```bash")
    lines.append("apm status              # Project dashboard")
    lines.append("apm task show <id>      # Task details")
    lines.append("apm task start <id>     # Begin work")
    lines.append("apm task submit-review <id>  # Submit for review")
    lines.append("```")
    lines.append("")

    return lines


def main():
    """Main hook entry point."""
    try:
        # Read hook input
        hook_data = read_hook_input()
        session_id = hook_data.get('session_id', 'unknown')

        # Log to stderr
        print(f"🪝 SessionStart (Python): session={session_id}", file=sys.stderr)

        # NEW: Create session record in database (non-blocking)
        create_session_record(session_id)

        # Output context to stdout (injected into Claude's context)
        context = format_context()

        # NEW (Task #363): Support JSON output format (pattern from disler's hook)
        # Set AIPM_HOOK_JSON=1 to use JSON format for testing
        import os
        use_json = os.environ.get('AIPM_HOOK_JSON', '0') == '1'

        if use_json:
            # JSON output format (disler pattern)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context[:5000]  # Limit for safety
                }
            }
            print(json.dumps(output))
        else:
            # Plain text output (current default)
            print(context)

        sys.exit(0)

    except Exception as e:
        print(f"❌ SessionStart hook error: {e}", file=sys.stderr)
        # Still output something useful
        print("\n⚠️ AIPM context loading failed - check hook configuration\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
