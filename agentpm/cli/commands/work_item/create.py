"""
apm work-item create - Create new work item command
"""

import json
from copy import deepcopy

import click
from agentpm.core.database.models import WorkItem, Context, UnifiedSixW
from agentpm.core.database.enums import WorkItemType, WorkItemStatus, ContextType, EntityType, ConfidenceBand, Phase
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.methods import contexts as context_methods
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import get_work_item_type_choices
from agentpm.cli.utils.templates import load_template


@click.command()
@click.argument('name')
@click.option(
    '--type', 'wi_type',
    type=click.Choice(get_work_item_type_choices(), case_sensitive=False),
    required=True,
    help='Work item type (feature, bugfix, research, etc.)'
)
@click.option(
    '--continuous/--no-continuous',
    default=None,
    help='Mark work item as a continuous backlog (defaults by type)'
)
@click.option(
    '--description', '-d',
    default='',
    help='Work item description'
)
@click.option(
    '--priority', '-p',
    type=click.IntRange(1, 5),
    default=3,
    help='Priority (1=highest, 5=lowest, default=3)'
)
@click.option(
    '--business-context',
    help='Business justification and impact (stored in work_item.business_context)'
)
@click.option(
    '--acceptance-criteria',
    help='JSON array of acceptance criteria strings (e.g., \'["Users can login", "JWT tokens issued"]\')'
)
@click.option(
    '--who',
    'six_w_who',
    help='WHO: Target users/stakeholders (e.g., "Small business owners, Enterprise customers")'
)
@click.option(
    '--what',
    'six_w_what',
    help='WHAT: What is being built (e.g., "Secure OAuth2 authentication system")'
)
@click.option(
    '--where',
    'six_w_where',
    help='WHERE: System boundaries/locations (e.g., "auth-service, user-api, frontend-app")'
)
@click.option(
    '--when',
    'six_w_when',
    help='WHEN: Timeline/deadlines (e.g., "Q2 2025, Before product launch")'
)
@click.option(
    '--why',
    'six_w_why',
    help='WHY: Business value/rationale (e.g., "Protect user data, Enable personalization")'
)
@click.option(
    '--how',
    'six_w_how',
    help='HOW: Technical approach (e.g., "OAuth2 flow, JWT tokens, Redis session store")'
)
@click.option(
    '--quality-target',
    help='JSON object with quality standards (e.g., \'{"test_coverage": 0.95, "performance_p95_ms": 200}\')'
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
    '--phase',
    type=click.Choice(Phase.choices(), case_sensitive=False),
    help='Phase in lifecycle (D1 → P1 → I1 → R1 → O1 → E1)'
)
@click.option(
    '--metadata-template',
    help='Seed metadata from template ID (e.g., "work_items/metadata"). Use "default" for the canonical structure.'
)
@click.pass_context
def create(ctx: click.Context, name: str, wi_type: str, continuous: bool, description: str, priority: int,
           business_context: str, acceptance_criteria: str, ownership: str, scope: str,
           artifacts: str, phase: str, metadata_template: str, **six_w_fields):
    """
    Create new work item with type-specific quality gates.

    Supports full WorkItem contract including business context, acceptance criteria,
    6W framework fields, and quality standards.

    \b
    Quality Gates by Type:
      FEATURE    → Must have: DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks
      BUGFIX     → Must have: ANALYSIS, BUGFIX, TESTING tasks
      PLANNING   → Cannot have: IMPLEMENTATION or DEPLOYMENT tasks
      RESEARCH   → Must have: ANALYSIS, DOCUMENTATION tasks

    \b
    Examples:
      # Basic work item
      apm work-item create "Add OAuth2" --type=feature

      # With business context
      apm work-item create "Add OAuth2" --type=feature \\
        --business-context "Enable personalized dashboards for 10K users"

      # With full context (6W framework)
      apm work-item create "User Authentication" \\
        --type=feature \\
        --priority=1 \\
        --business-context "Secure user access and enable personalization" \\
        --acceptance-criteria '["Users can login with email/password", "JWT tokens issued"]' \\
        --who "Small business owners, Enterprise customers" \\
        --what "OAuth2 authentication system" \\
        --where "auth-service, user-api, frontend" \\
        --when "Q2 2025, Before product launch" \\
        --why "Protect user data, Enable personalization, Reduce support tickets" \\
        --how "OAuth2 flow, JWT tokens, Redis session store" \\
        --quality-target '{"test_coverage": 0.95, "performance_p95_ms": 200}'
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Parse and validate JSON inputs
    metadata = {}
    if metadata_template:
        template_id = (
            'work_items/metadata'
            if metadata_template.lower() in ('default', 'canonical')
            else metadata_template
        )
        try:
            template_data = load_template(
                template_id, project_root=project_root, prefer_project=True
            )
        except FileNotFoundError:
            console.print(
                f"[red]❌ Error: Metadata template '{template_id}' not found[/red]"
            )
            console.print("   Use `apm template list` to view available templates.")
            raise click.Abort()
        if not isinstance(template_data, dict):
            console.print(
                f"[red]❌ Error: Template '{template_id}' is not a JSON object[/red]"
            )
            raise click.Abort()
        metadata = deepcopy(template_data)

    if acceptance_criteria:
        try:
            criteria = json.loads(acceptance_criteria)
            if not isinstance(criteria, list):
                console.print("[red]❌ Error: --acceptance-criteria must be a JSON array[/red]")
                raise click.Abort()
            metadata['acceptance_criteria'] = criteria
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --acceptance-criteria: {e}[/red]")
            raise click.Abort()

    if six_w_fields.get('quality_target'):
        try:
            quality = json.loads(six_w_fields['quality_target'])
            if not isinstance(quality, dict):
                console.print("[red]❌ Error: --quality-target must be a JSON object[/red]")
                raise click.Abort()
            metadata['quality_target'] = quality
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --quality-target: {e}[/red]")
            raise click.Abort()

    # CI-006 GAP-3: Parse contract v1.0 metadata fields
    if ownership:
        try:
            ownership_data = json.loads(ownership)
            if not isinstance(ownership_data, dict):
                console.print("[red]❌ Error: --ownership must be a JSON object[/red]")
                raise click.Abort()
            # Validate RACI roles
            required_roles = ['responsible', 'accountable', 'consulted', 'informed']
            missing_roles = [r for r in required_roles if not ownership_data.get(r)]
            if missing_roles:
                console.print(f"[red]❌ Error: --ownership missing required RACI roles: {', '.join(missing_roles)}[/red]")
                console.print("[yellow]Required: responsible, accountable, consulted, informed[/yellow]")
                raise click.Abort()
            metadata['ownership'] = {'raci': ownership_data}
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --ownership: {e}[/red]")
            raise click.Abort()

    if scope:
        try:
            scope_data = json.loads(scope)
            if not isinstance(scope_data, dict):
                console.print("[red]❌ Error: --scope must be a JSON object[/red]")
                raise click.Abort()
            # Validate in_scope is non-empty
            in_scope = scope_data.get('in_scope', [])
            if not isinstance(in_scope, list) or len(in_scope) == 0:
                console.print("[red]❌ Error: --scope must contain 'in_scope' array with at least one item[/red]")
                raise click.Abort()
            metadata['scope'] = scope_data
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --scope: {e}[/red]")
            raise click.Abort()

    if artifacts:
        try:
            artifacts_data = json.loads(artifacts)
            if not isinstance(artifacts_data, dict):
                console.print("[red]❌ Error: --artifacts must be a JSON object[/red]")
                raise click.Abort()
            # Validate code_paths for FEATURE/ENHANCEMENT work items
            if wi_type.lower() in ['feature', 'enhancement']:
                code_paths = artifacts_data.get('code_paths', [])
                if not isinstance(code_paths, list) or len(code_paths) == 0:
                    console.print("[red]❌ Error: Feature/Enhancement work items require 'code_paths' array with at least one path[/red]")
                    raise click.Abort()
            metadata['artifacts'] = artifacts_data
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --artifacts: {e}[/red]")
            raise click.Abort()

    work_item_type = WorkItemType(wi_type)
    type_is_continuous = WorkItemType.is_continuous_type(work_item_type)

    if continuous is None:
        is_continuous = type_is_continuous
    else:
        if type_is_continuous and not continuous:
            console.print(
                "[yellow]⚠️ Continuous backlog type detected. Ignoring --no-continuous flag.[/yellow]"
            )
        is_continuous = type_is_continuous or continuous

    # Create work item with metadata and phase
    work_item = WorkItem(
        name=name,
        description=description,
        type=work_item_type,
        status=WorkItemStatus.DRAFT,
        project_id=project_id,
        priority=priority,
        business_context=business_context,
        phase=phase,
        metadata=json.dumps(metadata) if metadata else '{}',
        is_continuous=is_continuous
    )

    # THREE-LAYER PATTERN: Use adapter, not direct methods call
    created_wi = WorkItemAdapter.create(db, work_item)

    # Create 6W context if any 6W fields provided
    six_w_who = six_w_fields.get('six_w_who')
    six_w_what = six_w_fields.get('six_w_what')
    six_w_where = six_w_fields.get('six_w_where')
    six_w_when = six_w_fields.get('six_w_when')
    six_w_why = six_w_fields.get('six_w_why')
    six_w_how = six_w_fields.get('six_w_how')

    if any([six_w_who, six_w_what, six_w_where, six_w_when, six_w_why, six_w_how]):
        # Create UnifiedSixW structure
        six_w_data = UnifiedSixW(
            end_users=[six_w_who] if six_w_who else [],
            functional_requirements=[six_w_what] if six_w_what else [],
            affected_services=[six_w_where] if six_w_where else [],
            dependencies_timeline=[six_w_when] if six_w_when else [],
            business_value=six_w_why,
            suggested_approach=six_w_how
        )

        # Create context entry
        context = Context(
            project_id=project_id,
            context_type=ContextType.WORK_ITEM_CONTEXT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=created_wi.id,
            six_w=six_w_data,
            confidence_score=0.7,  # User-provided = medium confidence
            confidence_band=ConfidenceBand.YELLOW
        )

        context_methods.create_context(db, context)

    # Success message
    console.print(f"\n✅ [green]Work item created:[/green] {created_wi.name}")
    console.print(f"   ID: {created_wi.id}")
    console.print(f"   Type: {created_wi.type.value}")
    console.print(f"   Status: {created_wi.status.value}")
    console.print(f"   Priority: {created_wi.priority}")

    if phase:
        console.print(f"   Phase: {phase}")

    if business_context:
        console.print(f"   Business Context: ✓")

    if metadata.get('acceptance_criteria'):
        console.print(f"   Acceptance Criteria: {len(metadata['acceptance_criteria'])} items")

    if metadata.get('ownership'):
        console.print("   Ownership (RACI): ✓")

    if metadata.get('scope'):
        in_scope_count = len(metadata['scope'].get('in_scope', []))
        console.print(f"   Scope: ✓ ({in_scope_count} items in scope)")

    if metadata.get('artifacts'):
        code_paths_count = len(metadata['artifacts'].get('code_paths', []))
        docs_paths_count = len(metadata['artifacts'].get('docs_paths', []))
        console.print(f"   Artifacts: ✓ ({code_paths_count} code paths, {docs_paths_count} doc paths)")

    if any([six_w_who, six_w_what, six_w_where, six_w_when, six_w_why, six_w_how]):
        console.print(f"   6W Context: ✓ (stored in contexts table)")

    console.print()

    # Show required tasks for this type
    console.print("📋 [cyan]Required tasks for this work item type:[/cyan]")

    if created_wi.type == WorkItemType.FEATURE:
        console.print("   • DESIGN task (architecture/design)")
        console.print("   • IMPLEMENTATION task (code changes)")
        console.print("   • TESTING task (test coverage)")
        console.print("   • DOCUMENTATION task (docs/guides)")
    elif created_wi.type == WorkItemType.BUGFIX:
        console.print("   • ANALYSIS task (root cause analysis)")
        console.print("   • BUGFIX task (actual fix)")
        console.print("   • TESTING task (regression tests)")
    elif created_wi.type == WorkItemType.RESEARCH:
        console.print("   • ANALYSIS task (conduct research)")
        console.print("   • DOCUMENTATION task (findings document)")
    elif created_wi.type == WorkItemType.PLANNING:
        console.print("   • ANALYSIS, DESIGN, DOCUMENTATION, REVIEW tasks")
        console.print("   ⚠️  IMPLEMENTATION and DEPLOYMENT tasks FORBIDDEN")

    console.print(f"\n📚 [cyan]Next step:[/cyan]")
    console.print(f"   apm task create \"Task name\" --work-item-id={created_wi.id} --type=design\n")
