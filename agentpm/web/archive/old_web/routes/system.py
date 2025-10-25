"""
System Blueprint - System Health, Database Metrics, Workflow Visualization

Handles:
- Health check endpoint
- Database metrics dashboard
- Workflow state machine visualization
- Context files browser
"""

from flask import Blueprint, render_template, abort, send_file
from pathlib import Path
from datetime import datetime

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods
from ...core.workflow.state_machine import StateMachine
from ...core.workflow.work_item_requirements import WORK_ITEM_TASK_REQUIREMENTS
from ...core.database.enums import TaskStatus, EntityType

# Import helper functions and models from app
from ..app import (
    get_database_service,
    format_file_size,
    TASK_TYPE_MAX_HOURS,
    TableInfo,
    DatabaseMetrics,
    ContextFilesView,
    ContextFileInfo,
    ContextFilePreview,
    WorkflowVisualization,
    WorkflowState
)

system_bp = Blueprint('system', __name__)


@system_bp.route('/health')
def health():
    """
    Health check endpoint.

    Returns:
        JSON health status
    """
    return {'status': 'ok', 'service': 'aipm-v2-dashboard'}


@system_bp.route('/system/database')
def database_metrics():
    """
    Database metrics dashboard.

    Displays AIPM database schema information and system health statistics.

    Returns:
        Rendered database metrics template
    """
    db = get_database_service()

    # Get entity counts using database methods
    all_projects = project_methods.list_projects(db)
    total_projects = len(all_projects)

    all_work_items = wi_methods.list_work_items(db)
    total_work_items = len(all_work_items)

    # Get all tasks across all work items
    all_tasks = []
    for wi in all_work_items:
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        all_tasks.extend(tasks)
    total_tasks = len(all_tasks)

    all_agents = agent_methods.list_agents(db)
    total_agents = len(all_agents)

    all_rules = rule_methods.list_rules(db)
    total_rules = len(all_rules)

    # Get contexts count and schema info using context manager
    with db.connect() as conn:
        # Get contexts count (raw SQL since no list method)
        cursor = conn.execute("SELECT COUNT(*) FROM contexts")
        total_contexts = cursor.fetchone()[0]

        # Get schema information from sqlite_master
        cursor = conn.execute("""
            SELECT name, type
            FROM sqlite_master
            WHERE type IN ('table', 'index', 'trigger')
            ORDER BY type, name
        """)
        schema_objects = cursor.fetchall()

        # Count schema objects
        total_tables = sum(1 for obj in schema_objects if obj[1] == 'table')
        total_indexes = sum(1 for obj in schema_objects if obj[1] == 'index')
        total_triggers = sum(1 for obj in schema_objects if obj[1] == 'trigger')

        # Get table details
        table_names = [obj[0] for obj in schema_objects if obj[1] == 'table' and not obj[0].startswith('sqlite_')]
        tables_info = []

        for table_name in table_names:
            # Get row count
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Get column count
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_count = len(columns)

            # Get index count for this table
            cursor = conn.execute(f"""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'index' AND tbl_name = ?
            """, (table_name,))
            index_count = cursor.fetchone()[0]

            tables_info.append(
                TableInfo(
                    name=table_name,
                    row_count=row_count,
                    column_count=column_count,
                    index_count=index_count
                )
            )

    # Sort tables by row count (descending)
    tables_info.sort(key=lambda t: t.row_count, reverse=True)

    metrics = DatabaseMetrics(
        total_tables=total_tables,
        total_indexes=total_indexes,
        total_triggers=total_triggers,
        total_projects=total_projects,
        total_work_items=total_work_items,
        total_tasks=total_tasks,
        total_agents=total_agents,
        total_rules=total_rules,
        total_contexts=total_contexts,
        tables=tables_info
    )

    # 🎨 Prepare chart data for Chart.js (Phase 4)

    # Entity Counts Chart (Horizontal Bar)
    entity_labels = ['Projects', 'Work Items', 'Tasks', 'Agents', 'Rules', 'Contexts']
    entity_data = [
        total_projects,
        total_work_items,
        total_tasks,
        total_agents,
        total_rules,
        total_contexts
    ]

    return render_template(
        'database_metrics.html',
        metrics=metrics,
        entity_labels=entity_labels,
        entity_data=entity_data
    )


@system_bp.route('/workflow')
def workflow_visualization():
    """
    Workflow state machine visualization.

    Displays AIPM's 9-state workflow and transition rules for
    work items and tasks.

    Returns:
        Rendered workflow visualization template
    """
    # Build workflow states for Task/WorkItem (9-state model)
    task_states_info = []

    # State descriptions (aligned with 9-state workflow)
    state_descriptions = {
        'proposed': 'Initial state: Work item/task created, awaiting validation',
        'validated': 'Requirements validated, design approved, ready for assignment',
        'accepted': 'Assigned to agent/developer, ready to start implementation',
        'in_progress': 'Active work in progress, agent is implementing',
        'blocked': 'Work blocked by dependency or external factor',
        'review': 'Implementation complete, awaiting quality review',
        'completed': 'Quality review passed, work done and accepted',
        'cancelled': 'Work item/task cancelled, will not be completed',
        'archived': 'Terminal state: Work archived for historical reference'
    }

    # Get allowed transitions for each TaskStatus
    for status in TaskStatus:
        allowed = StateMachine.get_valid_transitions(EntityType.TASK, status)
        allowed_names = [s.value for s in allowed]

        # Build requirements list based on state
        requirements = []
        if status == TaskStatus.READY:
            requirements.append("Task must have effort_hours estimate")
            requirements.append("Quality metadata required for certain task types")
        elif status == TaskStatus.ACTIVE:
            requirements.append("Task must be validated first")
            requirements.append("Parent work item must be accepted or later")
        elif status == TaskStatus.ACTIVE:
            requirements.append("Hard dependencies must be completed")
            requirements.append("Parent work item must be in_progress")
        elif status == TaskStatus.REVIEW:
            requirements.append("All acceptance criteria must be met")
            requirements.append("No unresolved blockers")
        elif status == TaskStatus.DONE:
            requirements.append("Quality review passed")
            requirements.append("All criteria validated")

        task_states_info.append(
            WorkflowState(
                name=status.value,
                description=state_descriptions.get(status.value, ''),
                allowed_transitions=allowed_names,
                requirements=requirements
            )
        )

    # Time-boxing rules (from type_validators.py)
    time_boxing_rules = {
        task_type.value: max_hours
        for task_type, max_hours in TASK_TYPE_MAX_HOURS.items()
    }

    # Required tasks by work item type
    required_tasks_by_work_item = {}
    for wi_type, req_obj in WORK_ITEM_TASK_REQUIREMENTS.items():
        required_tasks_by_work_item[wi_type.value] = [
            task_type.value for task_type in req_obj.required
        ]

    workflow_data = WorkflowVisualization(
        states=task_states_info,
        time_boxing_rules=time_boxing_rules,
        required_tasks_by_work_item=required_tasks_by_work_item
    )

    return render_template('workflow_visualization.html', workflow=workflow_data)


@system_bp.route('/context-files')
def context_files_list():
    """
    Context files browser - list all generated context files.

    Displays files from .aipm/contexts/ directory with metadata.

    Returns:
        Rendered context files list template
    """
    db = get_database_service()

    # Get project (for breadcrumb/navigation)
    projects = project_methods.list_projects(db)
    project = projects[0] if projects else None

    # Find .aipm/contexts directory
    context_dir = Path('.aipm/contexts')

    files_info = []
    if context_dir.exists() and context_dir.is_dir():
        for file_path in context_dir.rglob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                files_info.append(
                    ContextFileInfo(
                        name=file_path.name,
                        path=str(file_path.relative_to(context_dir)),
                        size_bytes=stat.st_size,
                        size_human=format_file_size(stat.st_size),
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        file_type=file_path.suffix or 'unknown'
                    )
                )

    # Sort by modified date (newest first)
    files_info.sort(key=lambda f: f.modified, reverse=True)

    view = ContextFilesView(
        project=project,
        files=files_info,
        total_files=len(files_info),
        total_size=sum(f.size_bytes for f in files_info)
    )

    return render_template('context_files_list.html', view=view)


@system_bp.route('/context-files/preview/<path:filepath>')
def context_file_preview(filepath: str):
    """
    Preview context file contents.

    Args:
        filepath: Relative path to file in .aipm/contexts/

    Returns:
        Rendered file preview template
    """
    # Security: Validate filepath to prevent directory traversal
    safe_path = Path(filepath).as_posix()
    if '..' in safe_path or safe_path.startswith('/'):
        abort(403, description="Invalid file path")

    context_dir = Path('.aipm/contexts')
    file_path = context_dir / filepath

    if not file_path.exists() or not file_path.is_file():
        abort(404, description=f"File not found: {filepath}")

    # Read file contents (limit to 1MB for preview)
    max_size = 1024 * 1024  # 1MB
    if file_path.stat().st_size > max_size:
        content = "[File too large for preview. Use download instead.]"
        is_truncated = True
    else:
        try:
            content = file_path.read_text(encoding='utf-8')
            is_truncated = False
        except UnicodeDecodeError:
            content = "[Binary file - cannot preview. Use download instead.]"
            is_truncated = True

    view = ContextFilePreview(
        filename=file_path.name,
        filepath=filepath,
        content=content,
        is_truncated=is_truncated,
        size_bytes=file_path.stat().st_size,
        modified=datetime.fromtimestamp(file_path.stat().st_mtime)
    )

    return render_template('context_file_preview.html', view=view)


@system_bp.route('/context-files/download/<path:filepath>')
def context_file_download(filepath: str):
    """
    Download context file.

    Args:
        filepath: Relative path to file in .aipm/contexts/

    Returns:
        File download response
    """
    # Security: Validate filepath
    safe_path = Path(filepath).as_posix()
    if '..' in safe_path or safe_path.startswith('/'):
        abort(403, description="Invalid file path")

    context_dir = Path('.aipm/contexts')
    file_path = context_dir / filepath

    if not file_path.exists() or not file_path.is_file():
        abort(404, description=f"File not found: {filepath}")

    # Convert to absolute path for send_file
    return send_file(
        file_path.resolve(),
        as_attachment=True,
        download_name=file_path.name
    )
