"""
apm context show - Display hierarchical context with confidence scoring using ContextAssemblyService
"""

import click
import json
from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists, validate_work_item_exists
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import work_item_summaries as summary_methods
from agentpm.core.database.adapters import ContextAdapter
from agentpm.core.database.enums import EntityType
from agentpm.core.detection import DetectionOrchestrator
from agentpm.core.plugins import PluginOrchestrator
from agentpm.core.context.assembly_service import ContextAssemblyService


def _display_task_context_from_payload(console, payload, format: str):
    """
    Display task context from ContextAssemblyService payload.

    Args:
        console: Rich console for output
        payload: ContextPayload from assembly service
        format: Output format ('rich', 'json', 'markdown')
    """
    if format == 'json':
        # Agent-consumable JSON format
        output = {
            'task': payload.task,
            'work_item': payload.work_item,
            'project': payload.project,
            'assigned_agent': payload.assigned_agent,
            'merged_6w': {
                'who': {
                    'end_users': payload.merged_6w.end_users or [],
                    'implementers': payload.merged_6w.implementers or [],
                    'reviewers': payload.merged_6w.reviewers or []
                },
                'what': {
                    'functional_requirements': payload.merged_6w.functional_requirements or [],
                    'technical_constraints': payload.merged_6w.technical_constraints or [],
                    'acceptance_criteria': payload.merged_6w.acceptance_criteria or []
                },
                'where': {
                    'affected_services': payload.merged_6w.affected_services or [],
                    'repositories': payload.merged_6w.repositories or [],
                    'deployment_targets': payload.merged_6w.deployment_targets or []
                },
                'when': {
                    'deadline': str(payload.merged_6w.deadline) if payload.merged_6w.deadline else None,
                    'dependencies_timeline': payload.merged_6w.dependencies_timeline or []
                },
                'why': {
                    'business_value': payload.merged_6w.business_value,
                    'risk_if_delayed': payload.merged_6w.risk_if_delayed
                },
                'how': {
                    'suggested_approach': payload.merged_6w.suggested_approach,
                    'existing_patterns': payload.merged_6w.existing_patterns or []
                }
            },
            'plugin_facts': payload.plugin_facts,
            'amalgamations': payload.amalgamations,
            'temporal_context': payload.temporal_context,
            'confidence': {
                'score': payload.confidence_score,
                'band': payload.confidence_band.value,
                'breakdown': payload.confidence_breakdown
            },
            'warnings': payload.warnings,
            'assembly_duration_ms': payload.assembly_duration_ms
        }
        # Clean the output to remove control characters that break JSON
        def clean_for_json(obj):
            if isinstance(obj, str):
                # Replace control characters with escaped versions
                return obj.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            elif isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            else:
                return obj
        
        cleaned_output = clean_for_json(output)
        console.print(json.dumps(cleaned_output, indent=2, default=str, ensure_ascii=False))
        return

    # Rich human-readable format
    console.print()
    task_info = payload.task
    console.print(Panel.fit(
        f"[bold cyan]Task #{task_info['id']}: {task_info['name']}[/bold cyan]",
        title="📖 Hierarchical Context",
        subtitle=f"⚡ Assembled in {payload.assembly_duration_ms:.0f}ms"
    ))
    console.print()

    # Assigned Agent section (prominent)
    if payload.assigned_agent:
        console.print(Panel(
            f"[bold green]{payload.assigned_agent}[/bold green]\n"
            f"[dim]Read: .claude/agents/{payload.assigned_agent}.md[/dim]",
            title="🤖 Assigned Agent",
            border_style="green"
        ))
        console.print()

    # Task Context section
    console.print("[bold cyan]─── TASK CONTEXT ───[/bold cyan]")
    console.print(f"  [dim]Type:[/dim] {task_info.get('type', 'N/A')}")
    console.print(f"  [dim]Status:[/dim] {task_info.get('status', 'N/A')}")
    console.print(f"  [dim]Effort:[/dim] {task_info.get('effort_hours', 'N/A')}h")
    if task_info.get('description'):
        console.print(f"  [dim]Description:[/dim] {task_info['description'][:100]}...")
    console.print()

    # Work Item Context section
    if payload.work_item:
        wi_info = payload.work_item
        console.print("[bold cyan]─── WORK ITEM CONTEXT ───[/bold cyan]")
        console.print(f"  [dim]Name:[/dim] {wi_info.get('name', 'N/A')}")
        console.print(f"  [dim]Type:[/dim] {wi_info.get('type', 'N/A')}")
        if payload.merged_6w.business_value:
            console.print(f"  [dim]Business Value:[/dim] {payload.merged_6w.business_value[:100]}...")
        console.print()

    # Project Context section
    if payload.project:
        proj_info = payload.project
        console.print("[bold cyan]─── PROJECT CONTEXT ───[/bold cyan]")
        console.print(f"  [dim]Project:[/dim] {proj_info.get('name', 'N/A')}")
        if payload.merged_6w.end_users or payload.merged_6w.implementers:
            who_parts = []
            if payload.merged_6w.end_users:
                who_parts.append(f"Users: {', '.join(payload.merged_6w.end_users)}")
            if payload.merged_6w.implementers:
                who_parts.append(f"Team: {', '.join(payload.merged_6w.implementers)}")
            console.print(f"  [dim]Who:[/dim] {' | '.join(who_parts)}")
        console.print()

    # Tech Stack / Plugin Facts
    if payload.plugin_facts:
        console.print("[bold cyan]Tech Stack:[/bold cyan]")
        # Display first 5 framework facts
        fact_count = 0
        for key, value in payload.plugin_facts.items():
            if fact_count >= 5:
                break
            if isinstance(value, (str, int, float)) and value:
                console.print(f"  • [dim]{key}:[/dim] {value}")
                fact_count += 1
            elif isinstance(value, dict) and 'version' in value:
                console.print(f"  • [dim]{key}:[/dim] {value['version']}")
                fact_count += 1
        console.print()

    # Relevant Code / Amalgamations
    if payload.amalgamations:
        console.print("[bold cyan]Relevant Code:[/bold cyan]")
        for amalg_type, path in list(payload.amalgamations.items())[:5]:
            console.print(f"  • {amalg_type}: [dim]{path}[/dim]")
        if len(payload.amalgamations) > 5:
            console.print(f"  [dim]... and {len(payload.amalgamations) - 5} more files[/dim]")
        console.print()

    # Temporal Context (session summaries)
    if payload.temporal_context:
        console.print("[bold cyan]Recent Session History:[/bold cyan]")
        for summary in payload.temporal_context[:3]:
            date = summary.get('session_date', 'N/A')
            summary_text = summary.get('summary_text', '')
            console.print(f"  • [cyan]{date}[/cyan]: {summary_text[:80]}...")
        console.print()

    # Context Quality
    confidence_band = payload.confidence_band.value
    band_colors = {'GREEN': 'green', 'YELLOW': 'yellow', 'RED': 'red'}
    band_color = band_colors.get(confidence_band, 'white')

    console.print(f"[bold cyan]Context Quality:[/bold cyan]")
    console.print(f"  Confidence: [{band_color}]{confidence_band}[/{band_color}] ({payload.confidence_score:.0%})")

    # Breakdown
    breakdown = payload.confidence_breakdown
    console.print(f"  [dim]• 6W Completeness:[/dim] {breakdown.get('six_w_completeness', 0):.0%}")
    console.print(f"  [dim]• Plugin Facts:[/dim] {breakdown.get('plugin_facts_quality', 0):.0%}")
    console.print(f"  [dim]• Code Coverage:[/dim] {breakdown.get('amalgamations_coverage', 0):.0%}")
    console.print(f"  [dim]• Freshness:[/dim] {breakdown.get('freshness_factor', 0):.0%}")
    console.print()

    # Warnings
    if payload.warnings:
        console.print("[yellow]⚠️  Warnings:[/yellow]")
        for warning in payload.warnings:
            console.print(f"  • {warning}")
        console.print()

    # Guidance
    console.print("[bold cyan]💡 Context System:[/bold cyan]")
    console.print("   Context assembled from hierarchical merge (Task → Work Item → Project)")
    console.print(f"   Assembly completed in {payload.assembly_duration_ms:.0f}ms")
    if payload.assigned_agent:
        console.print(f"   Agent SOP: .claude/agents/{payload.assigned_agent}.md")
    console.print()


def _get_project_intelligence(project_root: Path, project_id: int, db, console):
    """
    Get project intelligence from database, or re-detect if not found.

    Returns tuple of (technologies_dict, enrichment_dict) or (None, None) on error.

    Note: Returns dicts from stored data, not DetectionResult/EnrichmentResult objects.
    """
    try:
        # Try to load from database first
        project_context = ContextAdapter.get_entity_context(db, EntityType.PROJECT, project_id)

        if project_context and project_context.confidence_factors:
            plugin_facts = project_context.confidence_factors.get('plugin_facts')
            if plugin_facts:
                # Return stored data
                return (
                    plugin_facts.get('detected_technologies', {}),
                    plugin_facts.get('plugin_enrichment', {})
                )

        # No stored data - run fresh detection
        detector = DetectionOrchestrator(min_confidence=0.5)
        detection_result = detector.detect_all(project_root)

        # Run enrichment if technologies detected
        enrichment = None
        if detection_result.matches:
            orchestrator = PluginOrchestrator(min_confidence=0.5)
            enrichment = orchestrator.enrich_context(project_root, detection_result)

            # Convert to dict format for return
            technologies = {
                tech: {
                    'confidence': match.confidence,
                    'plugin_id': next((d.plugin_id for d in enrichment.deltas if tech in d.plugin_id), None)
                }
                for tech, match in detection_result.matches.items()
            }
            enrichment_data = {
                delta.plugin_id: delta.additions
                for delta in enrichment.deltas
            }

            return technologies, enrichment_data

        return None, None

    except Exception as e:
        # Silent failure - project intelligence is optional enhancement
        return None, None


@click.command()
@click.option(
    '--task-id', 'task_id',
    type=int,
    help='Show context for specific task'
)
@click.option(
    '--work-item-id', 'work_item_id',
    type=int,
    help='Show context for specific work item'
)
@click.option(
    '--project', 'show_project',
    is_flag=True,
    help='Show project-level context'
)
@click.option(
    '--format',
    type=click.Choice(['rich', 'json', 'markdown'], case_sensitive=False),
    default='rich',
    help='Output format'
)
@click.pass_context
def show(ctx: click.Context, task_id: int, work_item_id: int, show_project: bool, format: str):
    """
    Show hierarchical context with confidence scoring.

    Displays 6W context (WHO/WHAT/WHERE/WHEN/WHY/HOW) with
    hierarchical merging (task overrides work item overrides project).

    \b
    Examples:
      apm context show --task-id=5           # Task + work item + project context
      apm context show --work-item-id=1      # Work item + project context
      apm context show --project             # Project context only
      apm context show --task-id=5 --format=json  # JSON for agents
    """
    console = ctx.obj['console']
    
    # Respect injected context from tests; only derive if missing
    if 'project_root' not in ctx.obj or ctx.obj['project_root'] is None:
        project_root = ensure_project_root(ctx)
        ctx.obj['project_root'] = project_root
    else:
        project_root = ctx.obj['project_root']
    
    if 'db_service' not in ctx.obj or ctx.obj['db_service'] is None:
        db = get_database_service(Path(project_root))
        ctx.obj['db_service'] = db
    else:
        db = ctx.obj['db_service']
    
    project_id = get_current_project_id(ctx)

    # Validate and get context
    if task_id:
        validate_task_exists(db, task_id, ctx)

        # NEW: Use ContextAssemblyService for rich hierarchical context
        assembly_service = ContextAssemblyService(db, project_root)
        payload = assembly_service.assemble_task_context(task_id)

        # Display using new format
        _display_task_context_from_payload(console, payload, format)
        return

    elif work_item_id:
        validate_work_item_exists(db, work_item_id, ctx)
        work_item = wi_methods.get_work_item(db, work_item_id)

        wi_context = ContextAdapter.get_entity_context(db, EntityType.WORK_ITEM, work_item_id)
        project_context = ContextAdapter.get_entity_context(db, EntityType.PROJECT, project_id)

        entity_name = f"Work Item #{work_item_id}: {work_item.name}"
        contexts = {
            'work_item': wi_context,
            'project': project_context
        }

    elif show_project:
        project_context = ContextAdapter.get_entity_context(db, EntityType.PROJECT, project_id)
        from agentpm.core.database.methods import projects as project_methods
        project = project_methods.get_project(db, project_id)

        entity_name = f"Project: {project.name}"
        contexts = {
            'project': project_context
        }

    else:
        console.print("\n❌ [red]Must specify --task-id, --work-item-id, or --project[/red]\n")
        console.print("💡 Examples:")
        console.print("   apm context show --task-id=5")
        console.print("   apm context show --work-item-id=1")
        console.print("   apm context show --project\n")
        raise click.Abort()

    if format == 'json':
        import json
        output = {
            'entity': entity_name,
            'contexts': {}
        }

        for level, ctx_data in contexts.items():
            if ctx_data and ctx_data.six_w:
                output['contexts'][level] = {
                    'who': ctx_data.six_w.who,
                    'what': ctx_data.six_w.what,
                    'where': ctx_data.six_w.where,
                    'when': ctx_data.six_w.when,
                    'why': ctx_data.six_w.why,
                    'how': ctx_data.six_w.how
                }

        # Clean the output to remove control characters that break JSON
        def clean_for_json(obj):
            if isinstance(obj, str):
                # Replace control characters with escaped versions
                return obj.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            elif isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            else:
                return obj
        
        cleaned_output = clean_for_json(output)
        console.print(json.dumps(cleaned_output, indent=2, default=str, ensure_ascii=False))

    else:
        # Rich format
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{entity_name}[/bold cyan]",
            title="📖 Hierarchical Context"
        ))
        console.print()

        # Display contexts by level
        level_names = {'task': '🎯 Task Context', 'work_item': '📋 Work Item Context', 'project': '🏗️  Project Context'}

        for level, ctx_data in contexts.items():
            if ctx_data and ctx_data.six_w:
                console.print(f"[bold]{level_names[level]}[/bold]")

                # 6W Display
                if ctx_data.six_w.who:
                    console.print(f"  [cyan]WHO:[/cyan] {ctx_data.six_w.who}")
                if ctx_data.six_w.what:
                    console.print(f"  [cyan]WHAT:[/cyan] {ctx_data.six_w.what}")
                if ctx_data.six_w.where:
                    console.print(f"  [cyan]WHERE:[/cyan] {ctx_data.six_w.where}")
                if ctx_data.six_w.when:
                    console.print(f"  [cyan]WHEN:[/cyan] {ctx_data.six_w.when}")
                if ctx_data.six_w.why:
                    console.print(f"  [cyan]WHY:[/cyan] {ctx_data.six_w.why}")
                if ctx_data.six_w.how:
                    console.print(f"  [cyan]HOW:[/cyan] {ctx_data.six_w.how}")

                console.print()
            else:
                console.print(f"[dim]{level_names[level]}: Not set[/dim]\n")

        # Recent Summaries (if viewing work item or task context)
        if work_item_id or (task_id and work_item):
            wi_id = work_item_id or work_item.id
            recent_summaries = summary_methods.get_recent_summaries(db, wi_id, limit=3)

            if recent_summaries:
                console.print("[bold]📝 Recent Summaries:[/bold]")
                for summary in recent_summaries:
                    # Build summary line
                    parts = [
                        f"[cyan]{summary.session_date}[/cyan]",
                        f"[dim]{summary.summary_type}[/dim]"
                    ]
                    if summary.session_duration_hours:
                        parts.append(f"[yellow]{summary.session_duration_hours}h[/yellow]")

                    # Add metadata counts
                    if summary.context_metadata:
                        meta = summary.context_metadata
                        counts = []
                        if 'key_decisions' in meta and meta['key_decisions']:
                            counts.append(f"{len(meta['key_decisions'])} decisions")
                        if 'tasks_completed' in meta and meta['tasks_completed']:
                            counts.append(f"{len(meta['tasks_completed'])} tasks")
                        if counts:
                            parts.append(f"[green]({', '.join(counts)})[/green]")

                    # Truncate summary text
                    text = summary.summary_text[:80] + "..." if len(summary.summary_text) > 80 else summary.summary_text
                    text = text.replace('\n', ' ')  # Single line

                    console.print(f"  • {' | '.join(parts)}")
                    console.print(f"    {text}")

                console.print()
                console.print(f"[dim]   View full history: apm work-item show-history {wi_id}[/dim]\n")

        # Project Intelligence (from plugins - loads from DB first, then re-detects if needed)
        technologies, enrichment_data = _get_project_intelligence(project_root, project_id, db, console)

        if technologies:
            console.print("[bold]🔍 Project Intelligence:[/bold]")

            # Technology table
            tech_table = Table(show_header=True, header_style="cyan", box=None, padding=(0, 1))
            tech_table.add_column("Technology", style="cyan")
            tech_table.add_column("Confidence", justify="right", style="green")
            tech_table.add_column("Facts", justify="right", style="yellow")

            for tech, tech_data in technologies.items():
                conf_pct = f"{tech_data['confidence']:.0%}"

                # Get facts count from enrichment
                facts_count = 0
                plugin_id = tech_data.get('plugin_id')
                if enrichment_data and plugin_id and plugin_id in enrichment_data:
                    facts_count = len(enrichment_data[plugin_id])

                tech_table.add_row(tech.capitalize(), conf_pct, str(facts_count) if facts_count > 0 else "-")

            console.print(tech_table)

            # Show key facts from enrichment
            if enrichment_data:
                console.print()
                for plugin_id, facts in list(enrichment_data.items())[:3]:  # Show first 3 plugins
                    if facts:
                        # Show a few key facts per plugin
                        key_facts = []
                        for key, value in list(facts.items())[:5]:  # First 5 facts
                            if isinstance(value, (str, int, float, bool)) and value:
                                key_facts.append(f"[dim]{key}:[/dim] {value}")
                            elif isinstance(value, list) and len(value) <= 3 and value:
                                key_facts.append(f"[dim]{key}:[/dim] {', '.join(str(v) for v in value)}")

                        if key_facts:
                            plugin_name = plugin_id.split(':')[-1].capitalize()
                            console.print(f"  [cyan]{plugin_name}:[/cyan] {' | '.join(key_facts[:3])}")

            console.print(f"\n  [dim]Run 'apm context refresh' to update detection[/dim]\n")

        # Guidance
        console.print("[bold cyan]💡 Context System:[/bold cyan]")
        console.print("   Context provides hierarchical 6W information for AI agents")
        console.print("   Task context overrides work item context overrides project context")
        console.print()
