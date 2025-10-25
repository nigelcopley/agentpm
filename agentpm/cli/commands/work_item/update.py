"""
apm work-item update - Update work item fields command
"""

import click
import json
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import Phase
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command(name='update')
@click.argument('work_item_id', type=int)
@click.option('--name', help='Update work item name')
@click.option('--description', '-d', help='Update work item description')
@click.option('--business-context', help='Update business context')
@click.option('--priority', '-p', type=click.IntRange(1, 5), help='Update priority (1-5)')
@click.option('--effort-estimate', type=float, help='Update effort estimate in hours')
@click.option(
    '--phase',
    type=click.Choice(Phase.choices(), case_sensitive=False),
    help='Phase in lifecycle (D1 → P1 → I1 → R1 → O1 → E1)'
)
@click.option(
    '--ownership',
    help='JSON object with RACI roles (e.g., \'{"responsible": "jane", "accountable": "bob", "consulted": "team", "informed": "stakeholders"}\')'
)
@click.option(
    '--scope',
    help='JSON object with in_scope and out_of_scope arrays (e.g., \'{"in_scope": ["feature A"], "out_of_scope": ["feature B"]}\')'
)
@click.option(
    '--artifacts',
    help='JSON object with code_paths and docs_paths arrays (e.g., \'{"code_paths": ["src/module.py"], "docs_paths": ["docs/guide.md"]}\')'
)
@click.option(
    '--metadata',
    help='JSON object with complete metadata (e.g., \'{"why_value": {"problem": "...", "desired_outcome": "...", "business_impact": "...", "target_metrics": [...]}}\')'
)
@click.pass_context
def update(ctx: click.Context, work_item_id: int, name: str, description: str, business_context: str, priority: int,
           effort_estimate: float, phase: str, ownership: str, scope: str, artifacts: str, metadata: str):
    """
    Update work item fields.

    Updates one or more work item fields. Only specified fields are updated.
    Note: Type and status cannot be changed via update (use workflow commands).

    \b
    Examples:
      apm work-item update 5 --name "Updated feature name"
      apm work-item update 5 --description "New description"
      apm work-item update 5 --priority 1
      apm work-item update 5 --name "New name" --priority 2
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console_err.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        console_err.print("💡 [yellow]List work items with:[/yellow]")
        console_err.print("   apm work-item list\n")
        raise click.Abort()

    # Check if any updates provided
    if not any([name, description, business_context, priority, effort_estimate, phase, ownership, scope, artifacts, metadata]):
        console_err.print("\n⚠️  [yellow]No updates specified[/yellow]\n")
        console_err.print("💡 [cyan]Specify at least one field to update:[/cyan]")
        console_err.print("   --name, --description, --business-context, --priority, --effort-estimate, --phase")
        console_err.print("   --ownership, --scope, --artifacts, --metadata\n")
        console_err.print("Example:")
        console_err.print(f"   apm work-item update {work_item_id} --name \"New name\" --priority 1\n")
        raise click.Abort()

    # Parse and merge metadata fields (CI-006 GAP-3)
    metadata_updates = {}
    if ownership or scope or artifacts:
        # Load existing metadata
        existing_metadata = {}
        if work_item.metadata and work_item.metadata != '{}':
            try:
                existing_metadata = json.loads(work_item.metadata)
            except json.JSONDecodeError:
                console_err.print("\n⚠️  [yellow]Warning: Existing metadata is invalid JSON, creating new metadata[/yellow]\n")

        # Merge ownership
        if ownership:
            try:
                ownership_data = json.loads(ownership)
                if not isinstance(ownership_data, dict):
                    console_err.print("[red]❌ Error: --ownership must be a JSON object[/red]")
                    raise click.Abort()
                # Validate RACI roles
                required_roles = ['responsible', 'accountable', 'consulted', 'informed']
                missing_roles = [r for r in required_roles if not ownership_data.get(r)]
                if missing_roles:
                    console_err.print(f"[red]❌ Error: --ownership missing required RACI roles: {', '.join(missing_roles)}[/red]")
                    console_err.print("[yellow]Required: responsible, accountable, consulted, informed[/yellow]")
                    raise click.Abort()
                existing_metadata['ownership'] = {'raci': ownership_data}
            except json.JSONDecodeError as e:
                console_err.print(f"[red]❌ Error: Invalid JSON in --ownership: {e}[/red]")
                raise click.Abort()

        # Merge scope
        if scope:
            try:
                scope_data = json.loads(scope)
                if not isinstance(scope_data, dict):
                    console_err.print("[red]❌ Error: --scope must be a JSON object[/red]")
                    raise click.Abort()
                # Validate in_scope is non-empty
                in_scope = scope_data.get('in_scope', [])
                if not isinstance(in_scope, list) or len(in_scope) == 0:
                    console_err.print("[red]❌ Error: --scope must contain 'in_scope' array with at least one item[/red]")
                    raise click.Abort()
                existing_metadata['scope'] = scope_data
            except json.JSONDecodeError as e:
                console_err.print(f"[red]❌ Error: Invalid JSON in --scope: {e}[/red]")
                raise click.Abort()

        # Merge artifacts
        if artifacts:
            try:
                artifacts_data = json.loads(artifacts)
                if not isinstance(artifacts_data, dict):
                    console_err.print("[red]❌ Error: --artifacts must be a JSON object[/red]")
                    raise click.Abort()
                # Validate code_paths for FEATURE/ENHANCEMENT work items
                if work_item.type.value.lower() in ['feature', 'enhancement']:
                    code_paths = artifacts_data.get('code_paths', [])
                    if not isinstance(code_paths, list) or len(code_paths) == 0:
                        console_err.print("[red]❌ Error: Feature/Enhancement work items require 'code_paths' array with at least one path[/red]")
                        raise click.Abort()
                existing_metadata['artifacts'] = artifacts_data
            except json.JSONDecodeError as e:
                console_err.print(f"[red]❌ Error: Invalid JSON in --artifacts: {e}[/red]")
                raise click.Abort()

        metadata_updates['metadata'] = json.dumps(existing_metadata)

    # Handle complete metadata replacement
    if metadata:
        try:
            metadata_data = json.loads(metadata)
            if not isinstance(metadata_data, dict):
                console_err.print("[red]❌ Error: --metadata must be a JSON object[/red]")
                raise click.Abort()
            metadata_updates['metadata'] = json.dumps(metadata_data)
        except json.JSONDecodeError as e:
            console_err.print(f"[red]❌ Error: Invalid JSON in --metadata: {e}[/red]")
            raise click.Abort()

    # Build updates
    updates = {}
    if name:
        updates['name'] = name
    if description:
        updates['description'] = description
    if business_context:
        updates['business_context'] = business_context
    if priority:
        updates['priority'] = priority
    if effort_estimate is not None:
        updates['effort_estimate_hours'] = effort_estimate
    if phase:
        updates['phase'] = Phase(phase)
    if metadata_updates:
        updates.update(metadata_updates)

    # Update work item
    try:
        # Use WorkItemAdapter.update method with keyword arguments
        updated_wi = WorkItemAdapter.update(db, work_item_id, **updates)

        # Show what changed
        console.print(f"\n✅ [green]Work item updated:[/green] #{updated_wi.id}")

        if name:
            console.print(f"   Name: → {name}")
        if description:
            desc_preview = description[:60] + "..." if len(description) > 60 else description
            console.print(f"   Description: → {desc_preview}")
        if business_context:
            ctx_preview = business_context[:60] + "..." if len(business_context) > 60 else business_context
            console.print(f"   Business context: → {ctx_preview}")
        if priority:
            console.print(f"   Priority: → P{priority}")
        if effort_estimate is not None:
            console.print(f"   Effort estimate: → {effort_estimate}h")
        if phase:
            console.print(f"   Phase: → {phase}")
        if ownership:
            console.print("   Ownership (RACI): → Updated")
        if scope:
            scope_data = json.loads(scope)
            in_scope_count = len(scope_data.get('in_scope', []))
            console.print(f"   Scope: → Updated ({in_scope_count} items in scope)")
        if artifacts:
            artifacts_data = json.loads(artifacts)
            code_paths_count = len(artifacts_data.get('code_paths', []))
            docs_paths_count = len(artifacts_data.get('docs_paths', []))
            console.print(f"   Artifacts: → Updated ({code_paths_count} code paths, {docs_paths_count} doc paths)")
        if metadata:
            console.print("   Metadata: → Updated")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm work-item show {work_item_id}  # View updated details")
        console.print(f"   apm task list --work-item-id={work_item_id}  # View tasks\n")

    except Exception as e:
        console_err.print(f"\n❌ [red]Update failed:[/red] {e}\n")
        raise click.Abort()
