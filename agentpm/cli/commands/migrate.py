"""
apm migrate - Run pending database migrations
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.migrations import (
    get_pending_migrations,
    run_pending_migrations,
    get_applied_migrations
)


@click.command(name='migrate')
@click.option('--list', 'list_only', is_flag=True, help='List pending migrations without applying')
@click.option('--show-applied', is_flag=True, help='Show applied migrations')
@click.pass_context
def migrate(ctx: click.Context, list_only: bool, show_applied: bool):
    """
    Run pending database migrations.

    Migrations are Python files in migrations/files/ with upgrade() and
    downgrade() functions. Tracks applied migrations in schema_migrations table.

    \b
    Examples:
      apm migrate                    # Run all pending migrations
      apm migrate --list             # Show pending migrations
      apm migrate --show-applied     # Show applied migrations
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    try:
        # Show applied migrations
        if show_applied:
            applied = get_applied_migrations(db)
            console.print(f"\n📋 [bold]Applied Migrations:[/bold] {len(applied)}")
            for mig in applied:
                console.print(f"   ✅ {mig.version}: {mig.description}")
            console.print()
            return

        # Get pending migrations
        pending = get_pending_migrations(db)

        if not pending:
            console.print("\n✅ [green]No pending migrations[/green]")
            console.print("   Database schema is up to date\n")
            return

        # List only (don't apply)
        if list_only:
            console.print(f"\n📋 [bold]Pending Migrations:[/bold] {len(pending)}")
            for migration in pending:
                console.print(f"   ⏳ {migration.version}: {migration.description}")
            console.print(f"\n💡 [cyan]Run migrations with:[/cyan]")
            console.print("   apm migrate\n")
            return

        # Apply pending migrations
        console.print(f"\n🔄 [bold]Running {len(pending)} migration(s)...[/bold]\n")

        for migration in pending:
            console.print(f"   ⏳ Applying: {migration.version}: {migration.description}")

        # Run migrations
        success_count, failure_count = run_pending_migrations(db)

        if failure_count > 0:
            console_err.print(f"\n❌ [red]{failure_count} migration(s) failed![/red]")
            console_err.print(f"✅ {success_count} migration(s) succeeded\n")
            raise click.Abort()

        console.print(f"\n✅ [green]Applied {success_count} migration(s) successfully![/green]")
        console.print(f"\n📚 [cyan]Verify with:[/cyan]")
        console.print("   apm migrate --show-applied\n")

    except Exception as e:
        console_err.print(f"\n❌ [red]Migration failed:[/red] {e}\n")
        console_err.print("💡 [yellow]Check migration files for errors[/yellow]")
        console_err.print(f"   Location: agentpm/core/database/migrations/files/\n")
        raise click.Abort()
