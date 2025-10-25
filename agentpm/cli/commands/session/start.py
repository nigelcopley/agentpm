"""
apm session start - Start a new development session
"""

import uuid
from datetime import datetime
from typing import Optional

import click
from pydantic import ValidationError

from agentpm.core.database.models.session import (
    Session,
    SessionMetadata,
    SessionTool,
    SessionType,
)
from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.templates import load_template


@click.command()
@click.option(
    "--type",
    "session_type",
    type=click.Choice(["coding", "review", "planning", "debugging", "research"]),
    default="coding",
    help="Session type (default: coding)",
)
@click.option("--developer", help="Developer name (optional)")
@click.option("--email", help="Developer email (optional)")
@click.option(
    "--metadata-template",
    default="sessions/metadata",
    show_default=True,
    help="Seed session metadata from template ID (supports project overrides).",
)
@click.pass_context
def start(
    ctx: click.Context,
    session_type: str,
    developer: Optional[str],
    email: Optional[str],
    metadata_template: str,
):
    """
    Start a new development session.

    Creates a new session record with a unique session ID and pre-populates
    structured metadata so handovers remain consistent.
    """
    console = ctx.obj["console"]
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    active_sessions = SessionAdapter.get_active_sessions(db, project_id)
    if active_sessions:
        console.print("\n⚠️  [yellow]Warning: Active session already exists:[/yellow]\n")
        for session in active_sessions:
            console.print(f"   Session ID: {session.session_id}")
            console.print(
                f"   Started: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            console.print(f"   Tool: {session.tool_name.value}\n")

        console.print("💡 [yellow]End current session first:[/yellow]")
        console.print("   apm session end\n")
        raise click.Abort()

    # Load session metadata template (project override supported)
    template_id = metadata_template.strip()
    metadata_payload = {}
    if template_id and template_id.lower() not in ("none", "off"):
        try:
            metadata_payload = load_template(
                template_id, project_root=project_root, prefer_project=True
            )
            if not isinstance(metadata_payload, dict):
                console.print(
                    f"[red]❌ Error: Template '{template_id}' must be a JSON object[/red]"
                )
                raise click.Abort()
        except FileNotFoundError:
            console.print(
                f"[red]❌ Error: Metadata template '{template_id}' not found[/red]"
            )
            console.print("   Use `apm template list` to discover available IDs.")
            raise click.Abort()
        except Exception as exc:
            console.print(
                f"[red]❌ Error: Failed to load metadata template '{template_id}': {exc}[/red]"
            )
            raise click.Abort()

    try:
        metadata = SessionMetadata(**metadata_payload)
    except ValidationError as exc:
        console.print(
            "[red]❌ Error: Template payload is not valid SessionMetadata[/red]"
        )
        console.print(str(exc))
        raise click.Abort()

    session_id = str(uuid.uuid4())
    session = Session(
        session_id=session_id,
        project_id=project_id,
        tool_name=SessionTool.CLAUDE_CODE,  # Default to Claude Code
        llm_model=None,
        tool_version="1.0.0",
        start_time=datetime.now(),
        session_type=SessionType(session_type),
        developer_name=developer,
        developer_email=email,
        metadata=metadata,
    )

    try:
        created_session = SessionAdapter.create(db, session)

        console.print("\n✅ [green]Session started successfully![/green]\n")
        console.print(f"[bold]Session ID:[/bold] {created_session.session_id}")
        console.print(f"[bold]Type:[/bold] {created_session.session_type.value}")
        console.print(
            f"[bold]Started:[/bold] {created_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if developer:
            console.print(f"[bold]Developer:[/bold] {developer}")

        console.print("\n📝 [cyan]Session metadata initialized from template[/cyan]")
        console.print("\n💡 [yellow]End session when done:[/yellow]")
        console.print("   apm session end\n")

    except Exception as exc:
        console.print(f"\n❌ [red]Failed to start session:[/red] {exc}\n")
        raise click.Abort()
