#!/usr/bin/env python3
"""
Claude Code SessionEnd Hook - Template Generated

Executes when Claude Code session ends for cleanup and state capture.
Useful for session summarization, state persistence, and resource cleanup.

Features:
- Session summary generation
- Active work state capture
- Uncommitted changes detection
- Session metrics calculation
- Database cleanup

Security:
- No external network calls
- Database operations use parameterized queries
- File operations within project boundaries

Generated: 2025-10-27T18:45:32.975602
Template: hooks/session-end.py.j2
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def get_database():
    """Get database service instance."""
    from agentpm.core.database import DatabaseService
    db_path = PROJECT_ROOT / ".aipm" / "data" / "aipm.db"
    return DatabaseService(str(db_path))


def finalize_session(session_id: str) -> None:
    """
    Finalize session in database and emit SESSION_ENDED event.

    Updates:
    - Session end_time
    - Session duration
    - Session metrics (tools used, work items touched)

    Args:
        session_id: Session UUID
    """
    try:
        db = get_database()
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.sessions.event_bus import EventBus
        from agentpm.core.events.models import Event, EventType, EventCategory, EventSeverity

        # Finalize session
        session = session_methods.get_current_session(db)
        if session and session.session_id == session_id:
            session_methods.finalize_session(db, session.id, datetime.now())

            # Emit SESSION_ENDED event
            try:
                event_bus = EventBus(db)
                event = Event(
                    event_type=EventType.SESSION_ENDED,
                    event_category=EventCategory.SESSION_LIFECYCLE,
                    event_severity=EventSeverity.INFO,
                    session_id=session.id,
                    source='session_end_hook',
                    event_data={
                        'session_uuid': session_id,
                        'duration_seconds': (datetime.now() - session.start_time).total_seconds()
                    },
                    project_id=session.project_id
                )
                event_bus.emit(event)
                event_bus.shutdown(timeout=2.0)
                print(f"✅ SESSION_ENDED event emitted", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Event emission failed (non-critical): {e}", file=sys.stderr)

        print(f"✅ Session {session_id} finalized", file=sys.stderr)

    except Exception as e:
        print(f"⚠️ Session finalization failed (non-critical): {e}", file=sys.stderr)


def capture_active_state() -> dict:
    """
    Capture current active work state for next session.

    Captures:
    - Active work items
    - Active tasks
    - Uncommitted changes
    - Recent activity

    Returns:
        Dictionary with state information
    """
    try:
        db = get_database()
        from agentpm.core.database.methods import work_items as wi_methods
        from agentpm.core.database.methods import tasks as task_methods
        from agentpm.core.database.enums import WorkItemStatus, TaskStatus

        state = {
            'captured_at': datetime.now().isoformat(),
            'active_work_items': [],
            'active_tasks': [],
            'uncommitted_changes': False
        }

        # Get active work items
        active_wis = wi_methods.list_work_items(db, status=WorkItemStatus.ACTIVE)
        for wi in active_wis[:5]:  # Limit to 5
            state['active_work_items'].append({
                'id': wi.id,
                'name': wi.name,
                'type': wi.type.value,
                'phase': wi.phase.value if wi.phase else None
            })

        # Get active tasks
        active_tasks = task_methods.list_tasks(db, status=TaskStatus.ACTIVE)
        for task in active_tasks[:10]:  # Limit to 10
            state['active_tasks'].append({
                'id': task.id,
                'objective': task.objective,
                'work_item_id': task.work_item_id
            })

        # Check for uncommitted changes (git)
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0 and result.stdout.strip():
                state['uncommitted_changes'] = True
        except Exception:
            pass

        return state

    except Exception as e:
        print(f"⚠️ State capture failed (non-critical): {e}", file=sys.stderr)
        return {}


def generate_session_summary() -> str:
    """
    Generate human-readable session summary.

    Returns:
        Markdown-formatted session summary
    """
    try:
        state = capture_active_state()

        lines = []
        lines.append("## Session Summary")
        lines.append("")
        lines.append(f"**Ended**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if state.get('active_work_items'):
            lines.append("### Active Work Items")
            for wi in state['active_work_items']:
                lines.append(f"- WI-{wi['id']}: {wi['name']} ({wi['type']}, {wi['phase']})")
            lines.append("")

        if state.get('active_tasks'):
            lines.append("### Active Tasks")
            for task in state['active_tasks']:
                lines.append(f"- Task-{task['id']}: {task['objective']}")
            lines.append("")

        if state.get('uncommitted_changes'):
            lines.append("### ⚠️ Uncommitted Changes")
            lines.append("You have uncommitted changes. Consider committing before next session.")
            lines.append("")

        lines.append("**Next Session**: Use `apm status` to resume work")

        return "\n".join(lines)

    except Exception as e:
        print(f"⚠️ Summary generation failed: {e}", file=sys.stderr)
        return "Session ended. Use `apm status` to check project state."


def main():
    """Main hook entry point."""
    try:
        hook_data = read_hook_input()
        session_id = hook_data.get('session_id', 'unknown')

        print(f"🪝 SessionEnd (Python): session={session_id}", file=sys.stderr)

        # Finalize session in database
        finalize_session(session_id)

        # Capture active state for next session
        state = capture_active_state()

        # Generate summary
        summary = generate_session_summary()

        # Output summary to user
        import os
        use_json = os.environ.get('AIPM_HOOK_JSON', '0') == '1'

        if use_json:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionEnd",
                    "summary": summary[:2000],  # Limit size
                    "state": state
                }
            }
            print(json.dumps(output))
        else:
            print(summary)

        sys.exit(0)

    except Exception as e:
        print(f"❌ SessionEnd hook error: {e}", file=sys.stderr)
        print("\n⚠️ Session cleanup failed - state may not be saved\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
