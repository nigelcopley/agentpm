#!/usr/bin/env python3
"""
Claude Code SessionEnd Hook - Python Version

Generates NEXT-SESSION.md handover document using direct database access.
Runs in background when Claude Code session ends.

Performance: ~200ms (faster than bash with subprocess overhead)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentpm.core.database import DatabaseService
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.enums import WorkItemStatus, TaskStatus


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def get_database() -> DatabaseService:
    """Get database service instance."""
    db_path = PROJECT_ROOT / ".aipm" / "data" / "aipm.db"
    return DatabaseService(str(db_path))


def validate_session_summaries(session_id: str) -> None:
    """Validate session has required handover summaries.

    CRITICAL: This runs BEFORE try/except so sys.exit(1) actually blocks.

    Raises:
        SystemExit(1): If summaries missing (blocks Claude Code exit)
    """
    # Write to file for persistent debug
    debug_log = Path(__file__).parent.parent.parent / ".aipm" / "session-validation-debug.log"
    debug_log.parent.mkdir(parents=True, exist_ok=True)

    with open(debug_log, 'a') as f:
        f.write(f"\n[{datetime.now()}] validate_session_summaries called for session_id={session_id}\n")

    print(f"🔍 [DEBUG] validate_session_summaries called for session_id={session_id}", file=sys.stderr)

    db = get_database()
    from agentpm.core.database.methods import sessions as session_methods

    # Get EXISTING session
    existing_session = session_methods.get_session(db, session_id)

    with open(debug_log, 'a') as f:
        f.write(f"  Session found: {existing_session is not None}\n")

    if not existing_session:
        # No session found - don't block (might be first session)
        print(f"🔍 [DEBUG] No session found for {session_id}, allowing exit", file=sys.stderr)
        with open(debug_log, 'a') as f:
            f.write(f"  Action: Allowing exit (no session)\n")
        return

    metadata = existing_session.metadata

    has_current = bool(metadata.current_status)
    has_next = bool(metadata.next_session)

    with open(debug_log, 'a') as f:
        f.write(f"  current_status present: {has_current}\n")
        f.write(f"  next_session present: {has_next}\n")

    print(f"🔍 [DEBUG] current_status present: {has_current}", file=sys.stderr)
    print(f"🔍 [DEBUG] next_session present: {has_next}", file=sys.stderr)

    # ⚠️ CRITICAL: Block if handover summaries missing
    if not metadata.current_status or not metadata.next_session:
        with open(debug_log, 'a') as f:
            f.write(f"  Action: BLOCKING EXIT - summaries missing!\n")

        print("", file=sys.stderr)
        print("❌ Session handover incomplete - missing required summaries", file=sys.stderr)
        print("", file=sys.stderr)
        print("🤖 RECOMMENDED: Type /aipm:handover in Claude Code", file=sys.stderr)
        print("   (AI will analyze session and generate summaries automatically)", file=sys.stderr)
        print("", file=sys.stderr)
        print("OR manually provide:", file=sys.stderr)
        if not metadata.current_status:
            print("  • current_status: Project status summary", file=sys.stderr)
        if not metadata.next_session:
            print("  • next_session: Next session priorities", file=sys.stderr)
        print("", file=sys.stderr)
        print("Manual commands:", file=sys.stderr)
        print(f"  apm session update --current-status '...'", file=sys.stderr)
        print(f"  apm session update --next-session '...'", file=sys.stderr)
        print("", file=sys.stderr)

        # Don't block - just warn (SessionEnd can't block per Claude Code docs)
        # User will see this warning in Claude Code UI


def end_session_record(session_id: str, reason: str) -> None:
    """End session record in database with captured end-of-session state and emit SESSION_ENDED event.

    NEW (WI-35 Task #173): Integrates with EventBus for automatic event capture.

    CRITICAL: Merges with existing metadata (from WorkflowService tracking).
    Does NOT replace automatically-captured work items/tasks!

    Graceful degradation: If database write fails, log error but continue.
    NEXT-SESSION.md generation must still work (primary function).
    """
    try:
        db = get_database()
        from agentpm.core.database.models.session import SessionMetadata, SessionStatus
        from agentpm.core.database.methods import sessions as session_methods
        from agentpm.core.database.enums import WorkItemStatus, TaskStatus
        from agentpm.core.sessions.event_bus import EventBus
        from agentpm.core.events.models import Event, EventType, EventCategory, EventSeverity
        import subprocess

        # Get EXISTING session from database (preserves WorkflowService tracking)
        existing_session = session_methods.get_session(db, session_id)
        if not existing_session:
            print(f"⚠️ Session {session_id} not found in database", file=sys.stderr)
            return

        # MERGE with existing metadata (don't replace!)
        metadata = existing_session.metadata

        # Capture ACTIVE state for next session (handover context)
        active_wis = wi_methods.list_work_items(db, status=WorkItemStatus.ACTIVE)
        review_wis = wi_methods.list_work_items(db, status=WorkItemStatus.REVIEW)
        all_active = active_wis + review_wis
        metadata.active_work_items = [wi.id for wi in all_active]

        # Capture ACTIVE tasks for next session
        all_active_tasks = []
        for wi in wi_methods.list_work_items(db):
            tasks = task_methods.list_tasks(db, work_item_id=wi.id)
            active = [t for t in tasks if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)]
            all_active_tasks.extend(active)
        metadata.active_tasks = [t.id for t in all_active_tasks]

        # Capture git status (uncommitted files)
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                uncommitted = [line[3:] for line in result.stdout.strip().split('\n') if line.strip()]
                metadata.uncommitted_files = uncommitted
        except Exception:
            pass

        # Capture current branch
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                metadata.current_branch = result.stdout.strip()
        except Exception:
            pass

        # Capture recent commits (with full details)
        try:
            result = subprocess.run(
                ['git', 'log', '-3', '--pretty=format:%H|%s|%an'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 2)
                        if len(parts) == 3:
                            commits.append({
                                'sha': parts[0],
                                'message': parts[1],
                                'author': parts[2]
                            })
                metadata.recent_commits = commits
        except Exception:
            pass

        # End session with MERGED metadata
        updated_session = session_methods.end_session(
            db,
            session_id,
            metadata=metadata,  # Merged metadata (preserves work_items_touched, tasks_completed)
            exit_reason=reason
        )

        # Update status to completed
        updated_session.status = SessionStatus.DONE
        session_methods.update_session(db, updated_session)

        # NEW (WI-35): Emit SESSION_ENDED event
        try:
            event_bus = EventBus(db)
            event = Event(
                event_type=EventType.SESSION_ENDED,
                event_category=EventCategory.SESSION_LIFECYCLE,
                event_severity=EventSeverity.INFO,
                session_id=updated_session.id,
                source='session_end_hook',
                event_data={
                    'session_uuid': session_id,
                    'exit_reason': reason,
                    'duration_minutes': updated_session.duration_minutes,
                    'work_items_touched': len(metadata.work_items_touched),
                    'tasks_completed': len(metadata.tasks_completed),
                    'git_commits': len(metadata.git_commits),
                    'decisions_made': len(metadata.decisions_made)
                },
                project_id=existing_session.project_id
            )
            event_bus.emit(event)
            event_bus.shutdown(timeout=2.0)  # Graceful shutdown
            print(f"✅ SESSION_ENDED event emitted", file=sys.stderr)
        except Exception as e:
            # Event emission failure is non-critical
            print(f"⚠️ Event emission failed (non-critical): {e}", file=sys.stderr)

        # Validate session completeness (warn but don't block)
        is_complete, missing = session_methods.validate_session_completeness(updated_session)
        if not is_complete:
            print(f"⚠️  Session completeness warnings:", file=sys.stderr)
            for item in missing:
                print(f"   - {item}", file=sys.stderr)

        # Clear current session
        session_methods.clear_current_session(db)

        print(f"✅ Session {session_id} ended and saved to database", file=sys.stderr)
        print(f"✅ Current session cleared", file=sys.stderr)

    except Exception as e:
        # Graceful degradation - log but don't fail
        print(f"⚠️ Session end tracking failed (non-critical): {e}", file=sys.stderr)


def save_context_snapshots(session_id: str, reason: str) -> None:
    """Save rich context snapshots for active tasks using ContextAssemblyService.
    
    NEW: Enhanced session-end context persistence with hierarchical context snapshots.
    Performance: <1 second (non-blocking background)
    
    Args:
        session_id: Session ID for tracking
        reason: Exit reason for context
    """
    try:
        from agentpm.core.hooks.context_integration import ContextHookAdapter
        from agentpm.core.database.methods import tasks as task_methods
        from agentpm.core.database.enums import TaskStatus
        from agentpm.core.database.methods import work_item_summaries as summary_methods
        from datetime import datetime
        
        print(f"🔍 [DEBUG] Starting context snapshots for session {session_id}", file=sys.stderr)
        
        # Initialize context adapter
        adapter = ContextHookAdapter(PROJECT_ROOT)
        db = get_database()
        
        # Get active tasks
        active_tasks = task_methods.list_tasks(db, status=TaskStatus.ACTIVE, limit=3)
        
        if not active_tasks:
            print(f"🔍 [DEBUG] No active tasks found, skipping context snapshots", file=sys.stderr)
            return
            
        print(f"🔍 [DEBUG] Found {len(active_tasks)} active tasks for context snapshots", file=sys.stderr)
        
        # Save context snapshots for each active task
        for task in active_tasks:
            try:
                print(f"🔍 [DEBUG] Saving context snapshot for Task #{task.id}", file=sys.stderr)
                
                # Assemble rich context for this task
                start_time = datetime.now()
                payload = adapter.assembly_service.assemble_task_context(task.id)
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Create context snapshot summary
                snapshot_summary = f"Context snapshot for Task #{task.id}: {task.name}\n"
                snapshot_summary += f"Work Item: WI-{task.work_item_id}\n"
                snapshot_summary += f"Agent: {payload.assigned_agent or 'unassigned'}\n"
                snapshot_summary += f"Confidence: {payload.confidence_score:.0%} ({payload.confidence_band.value.upper()})\n"
                snapshot_summary += f"Assembly Time: {duration_ms:.0f}ms\n\n"
                
                # Add 6W context summary
                if payload.merged_6w:
                    snapshot_summary += "Context Summary:\n"
                    if payload.merged_6w.who:
                        snapshot_summary += f"WHO: {payload.merged_6w.who}\n"
                    if payload.merged_6w.what:
                        snapshot_summary += f"WHAT: {payload.merged_6w.what}\n"
                    if payload.merged_6w.why:
                        snapshot_summary += f"WHY: {payload.merged_6w.why}\n"
                    if payload.merged_6w.how:
                        snapshot_summary += f"HOW: {payload.merged_6w.how}\n"
                    snapshot_summary += "\n"
                
                # Add warnings if any
                if payload.warnings:
                    snapshot_summary += "Warnings:\n"
                    for warning in payload.warnings[:3]:
                        snapshot_summary += f"- {warning}\n"
                    snapshot_summary += "\n"
                
                # Save as work item summary for next session
                summary_data = {
                    'work_item_id': task.work_item_id,
                    'session_date': datetime.now().strftime('%Y-%m-%d'),
                    'summary_text': snapshot_summary,
                    'context_metadata': {
                        'task_id': task.id,
                        'session_id': session_id,
                        'exit_reason': reason,
                        'context_confidence': payload.confidence_score,
                        'context_band': payload.confidence_band.value,
                        'assembly_time_ms': duration_ms,
                        'warnings_count': len(payload.warnings)
                    },
                    'created_by': 'session-end-hook',
                    'summary_type': 'context_snapshot'
                }
                
                # Create summary record
                from agentpm.core.database.models.work_item_summary import WorkItemSummary
                summary = WorkItemSummary(**summary_data)
                summary_methods.create_work_item_summary(db, summary)
                
                print(f"✅ Context snapshot saved for Task #{task.id}", file=sys.stderr)
                
            except Exception as e:
                # Graceful degradation for individual task
                print(f"⚠️ Context snapshot failed for Task #{task.id}: {e}", file=sys.stderr)
                continue
                
        print(f"✅ Context snapshots completed for session {session_id}", file=sys.stderr)
        
    except Exception as e:
        # Graceful degradation - log but don't fail
        print(f"⚠️ Context snapshots failed (non-critical): {e}", file=sys.stderr)


def generate_handover_context(session_id: str, reason: str) -> None:
    """Generate NEXT-SESSION.md with handover context."""

    db = get_database()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    handover_path = PROJECT_ROOT / "NEXT-SESSION.md"

    with open(handover_path, 'w') as f:
        # Header
        f.write("# Next Session Handover\n\n")
        f.write("**Auto-generated by SessionEnd hook (Python)**\n\n")
        f.write(f"**Last Updated**: {timestamp}\n")
        f.write(f"**Session ID**: {session_id}\n")
        f.write(f"**Exit Reason**: {reason}\n\n")

        # Active Work Items
        f.write("## 📋 Active Work Items\n\n")
        try:
            active_wis = wi_methods.list_work_items(
                db,
                status=WorkItemStatus.ACTIVE
            )
            review_wis = wi_methods.list_work_items(
                db,
                status=WorkItemStatus.REVIEW
            )
            all_active = active_wis + review_wis

            if all_active:
                for wi in all_active[:5]:  # Show top 5
                    f.write(f"- **WI-{wi.id}**: {wi.name}\n")
                    f.write(f"  - Type: {wi.type.value}, Status: {wi.status.value}, Priority: {wi.priority}\n")

                    # Get task count
                    tasks = task_methods.list_tasks(db, work_item_id=wi.id)
                    completed = sum(1 for t in tasks if t.status == TaskStatus.DONE)
                    f.write(f"  - Progress: {completed}/{len(tasks)} tasks completed\n")
                f.write("\n")
            else:
                f.write("No active work items\n\n")
        except Exception as e:
            f.write(f"⚠️ Error loading work items: {e}\n\n")

        # Active Tasks
        f.write("## ✅ Active Tasks\n\n")
        try:
            all_active_tasks = []
            all_wis = wi_methods.list_work_items(db)
            for wi in all_wis:
                tasks = task_methods.list_tasks(db, work_item_id=wi.id)
                active = [t for t in tasks if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)]
                all_active_tasks.extend([(t, wi.name) for t in active])

            if all_active_tasks:
                for task, wi_name in all_active_tasks[:5]:  # Show top 5
                    f.write(f"- **Task #{task.id}**: {task.name}\n")
                    f.write(f"  - Type: {task.type.value}, Status: {task.status.value}\n")
                    f.write(f"  - Work Item: {wi_name}\n")
                    if task.effort_hours:
                        f.write(f"  - Effort: {task.effort_hours}h\n")
                f.write("\n")
            else:
                f.write("No active tasks\n\n")
        except Exception as e:
            f.write(f"⚠️ Error loading tasks: {e}\n\n")

        # Git Status
        f.write("## 🔄 Uncommitted Changes\n\n")
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                f.write("```\n")
                f.write(result.stdout[:500])  # Limit output
                f.write("```\n\n")
                f.write("⚠️ **Action needed**: Review and commit changes\n\n")
            else:
                f.write("✅ Working tree is clean\n\n")
        except Exception as e:
            f.write(f"⚠️ Unable to check git status: {e}\n\n")

        # Recent Commits
        f.write("## 📝 Recent Commits (Last 3)\n\n")
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-3'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                f.write("```\n")
                f.write(result.stdout)
                f.write("```\n\n")
        except Exception:
            pass

        # Quick Start
        f.write("## 🚀 Quick Start Commands\n\n")
        f.write("```bash\n")
        f.write("# Check status\n")
        f.write("apm status\n\n")
        f.write("# Continue work on active items\n")
        if all_active:
            f.write(f"apm work-item show {all_active[0].id}\n")
        if all_active_tasks:
            f.write(f"apm task show {all_active_tasks[0][0].id}\n")
        f.write("\n# Flask Dashboard\n")
        f.write("flask --app agentpm.web.app run\n")
        f.write("```\n\n")

        # Resources
        f.write("## 📖 Key Resources\n\n")
        f.write("- RULES.md - Development standards\n")
        f.write("- master-orchestrator.md - AIPM entry point\n")
        f.write("- STATUS.md - Project state\n\n")
        f.write("---\n\n")
        f.write("*Auto-generated by SessionEnd hook (Python)*\n")

    # Log success
    log_path = PROJECT_ROOT / ".aipm" / "session-end.log"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(f"\n✅ [{timestamp}] Handover generated (session: {session_id}, reason: {reason})\n")


def main():
    """Main hook entry point."""
    # Log FIRST thing
    print(f"🔍 [DEBUG] SessionEnd main() called", file=sys.stderr)

    try:
        # Read hook input
        hook_data = read_hook_input()
        session_id = hook_data.get('session_id', 'unknown')
        reason = hook_data.get('reason', 'unknown')

        # Log to stderr (visible in debug mode)
        print(f"🪝 SessionEnd (Python): session={session_id}, reason={reason}", file=sys.stderr)

        # ⚠️ CRITICAL: Validate summaries FIRST (blocks if missing)
        print(f"🔍 [DEBUG] About to call validate_session_summaries", file=sys.stderr)
        validate_session_summaries(session_id)
        print(f"🔍 [DEBUG] Validation passed, continuing...", file=sys.stderr)

        # NEW: End session record in database (non-blocking)
        end_session_record(session_id, reason)

        # NEW: Save rich context snapshots for next session
        save_context_snapshots(session_id, reason)

        # DEPRECATED (Task #357): NEXT-SESSION.md replaced by database session management
        # Database now stores all handover context via session metadata
        # Rollback: Uncomment line below to restore file-based handover
        #
        # generate_handover_context(session_id, reason)

        sys.exit(0)

    except Exception as e:
        print(f"❌ SessionEnd hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
