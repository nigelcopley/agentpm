#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit Hook - Python Version

Called when user submits a prompt. Can inject relevant context based on
the user's question or request.

Hook Input (JSON):
{
    "prompt": "user's input text",
    "session_id": "uuid"
}

Hook Output (stdout): Additional context injected alongside user's prompt
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentpm.core.database import DatabaseService
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods

# NEW: Import Context Agent integration
from agentpm.core.hooks.context_integration import ContextHookAdapter


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def extract_mentions(prompt: str) -> dict:
    """Extract AIPM entity mentions from user prompt."""
    mentions = {
        'work_items': [],
        'tasks': [],
        'keywords': []
    }

    # Extract work item references (WI-27, WI-0017, etc.)
    wi_pattern = r'WI[-\s]*(\d+)'
    for match in re.finditer(wi_pattern, prompt, re.IGNORECASE):
        wi_id = int(match.group(1))
        mentions['work_items'].append(wi_id)

    # Extract task references (Task 123, task #45, etc.)
    task_pattern = r'task\s*#?(\d+)'
    for match in re.finditer(task_pattern, prompt, re.IGNORECASE):
        task_id = int(match.group(1))
        mentions['tasks'].append(task_id)

    # Detect workflow keywords
    workflow_keywords = [
        'start', 'complete', 'review', 'validate', 'accept',
        'block', 'dependency', 'commit', 'test'
    ]
    for keyword in workflow_keywords:
        if keyword in prompt.lower():
            mentions['keywords'].append(keyword)

    return mentions


def format_context_injection(prompt: str, db: DatabaseService) -> str:
    """
    Format context to inject based on user prompt.

    Integration: Uses ContextHookAdapter for entity context (Task #147)
    Fallback: If Context Agent fails, use original manual injection
    """
    lines = []
    mentions = extract_mentions(prompt)

    # Try Context Agent integration first (Task #147)
    try:
        adapter = ContextHookAdapter(PROJECT_ROOT)

        # Inject work item context if mentioned (using Context Agent)
        if mentions['work_items']:
            for wi_id in mentions['work_items'][:3]:
                try:
                    context = adapter.inject_entity_context('work_item', wi_id)
                    if context:
                        lines.append(f"\n{context}")
                except Exception:
                    # Fallback to manual injection for this specific entity
                    lines.extend(_inject_work_item_fallback(db, wi_id))

        # Inject task context if mentioned (using Context Agent)
        if mentions['tasks']:
            for task_id in mentions['tasks'][:3]:
                try:
                    context = adapter.inject_entity_context('task', task_id)
                    if context:
                        lines.append(f"\n{context}")
                except Exception:
                    # Fallback to manual injection for this specific entity
                    lines.extend(_inject_task_fallback(db, task_id))

    except Exception as e:
        # Complete fallback if Context Agent unavailable
        print(f"⚠️ Context Agent unavailable: {e}", file=sys.stderr)

        # Use manual injection for all entities
        if mentions['work_items']:
            for wi_id in mentions['work_items'][:3]:
                lines.extend(_inject_work_item_fallback(db, wi_id))

        if mentions['tasks']:
            for task_id in mentions['tasks'][:3]:
                lines.extend(_inject_task_fallback(db, task_id))

    # Inject workflow guidance (keep original logic - not Context Agent scope)
    if mentions['keywords']:
        workflow_reminders = {
            'start': "Remember: Work item must be in_progress before tasks can start",
            'complete': "Ensure all acceptance criteria are met before marking complete",
            'review': "Different agent should review (no self-approval)",
            'validate': "Check all required fields and quality gates",
            'commit': "Good! Commit frequently (every 30-60 min)",
            'test': "Target ≥90% coverage for core modules (CI-004)"
        }

        for keyword in mentions['keywords'][:2]:
            if keyword in workflow_reminders:
                lines.append(f"\n💡 {workflow_reminders[keyword]}")

    # Return injected context (empty if no relevant mentions)
    if lines:
        lines.insert(0, "\n---")
        lines.insert(1, "## 🎯 Contextual AIPM Intelligence")
        lines.append("---\n")

    return "\n".join(lines)


def _inject_work_item_fallback(db: DatabaseService, wi_id: int) -> list:
    """Fallback: Manual work item context injection."""
    lines = []
    try:
        wi = wi_methods.get_work_item(db, wi_id)
        if wi:
            lines.append(f"\n📋 **WI-{wi_id} Context**:")
            lines.append(f"- Name: {wi.name}")
            lines.append(f"- Type: {wi.type.value}")
            lines.append(f"- Status: {wi.status.value}")
            lines.append(f"- Priority: {wi.priority}")

            # Show active tasks
            tasks = task_methods.list_tasks(db, work_item_id=wi_id)
            active_tasks = [t for t in tasks if t.status.value in ['in_progress', 'review']]
            if active_tasks:
                lines.append(f"- Active Tasks: {len(active_tasks)}")
                for task in active_tasks[:2]:
                    lines.append(f"  • Task #{task.id}: {task.name} ({task.status.value})")
    except Exception:
        pass

    return lines


def _inject_task_fallback(db: DatabaseService, task_id: int) -> list:
    """Fallback: Manual task context injection."""
    lines = []
    try:
        task = task_methods.get_task(db, task_id)
        if task:
            lines.append(f"\n📝 **Task #{task_id} Context**:")
            lines.append(f"- Name: {task.name}")
            lines.append(f"- Type: {task.type.value}")
            lines.append(f"- Status: {task.status.value}")
            lines.append(f"- Effort: {task.effort_hours}h")
            lines.append(f"- Work Item: WI-{task.work_item_id}")

            # Show dependencies/blockers
            from agentpm.core.database.methods import dependencies as dep_methods
            deps = dep_methods.get_task_dependencies(db, task_id)
            blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=True)

            if deps:
                lines.append(f"- Dependencies: {len(deps)} prerequisites")
            if blockers:
                lines.append(f"- ⚠️ Blockers: {len(blockers)} unresolved")
    except Exception:
        pass

    return lines


def main():
    """Main hook entry point."""
    try:
        # Read hook input
        hook_data = read_hook_input()
        prompt = hook_data.get('prompt', '')
        session_id = hook_data.get('session_id', 'unknown')

        # Log to stderr
        print(f"🪝 UserPromptSubmit: session={session_id}, prompt_length={len(prompt)}",
              file=sys.stderr)

        # Get database connection
        db_path = PROJECT_ROOT / ".aipm" / "data" / "aipm.db"
        db = DatabaseService(str(db_path))

        # Generate contextual injection
        context = format_context_injection(prompt, db)

        if context:
            # Output context to stdout (injected alongside user prompt)
            print(context)

        sys.exit(0)

    except Exception as e:
        print(f"❌ UserPromptSubmit hook error: {e}", file=sys.stderr)
        # Don't inject errors into context
        sys.exit(1)


if __name__ == "__main__":
    main()
