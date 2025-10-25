"""
Idea Elements CLI Commands

Commands for managing idea elements - components/parts of ideas that can be
broken down into tasks when ideas are converted to work items.
"""

import click
from typing import Optional

from agentpm.core.database.models import IdeaElement
from agentpm.core.database.adapters import IdeaElementAdapter
from agentpm.core.database.enums import TaskType
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.group()
def elements():
    """Manage idea elements (components/parts of ideas)"""
    pass


@elements.command()
@click.argument('idea_id', type=int)
@click.option('--title', '-t', required=True, help='Element title')
@click.option('--description', '-d', help='Element description')
@click.option('--type', type=click.Choice([t.value for t in TaskType]), 
              default=TaskType.IMPLEMENTATION.value, help='Element type')
@click.option('--effort-hours', type=float, required=True, help='Estimated effort in hours')
@click.option('--order', type=int, default=0, help='Display order within idea')
@click.pass_context
def create(ctx, idea_id: int, title: str, description: Optional[str], 
           type: str, effort_hours: float, order: int):
    """Create a new element for an idea"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    element = IdeaElement(
        idea_id=idea_id,
        title=title,
        description=description,
        type=TaskType(type),
        effort_hours=effort_hours,
        order_index=order
    )
    
    created = IdeaElementAdapter.create(db, element)
    
    click.echo(f"✅ Created element {created.id}: {created.title}")
    click.echo(f"   Type: {created.type.value}")
    click.echo(f"   Effort: {created.effort_hours}h")
    click.echo(f"   Order: {created.order_index}")


@elements.command()
@click.argument('idea_id', type=int)
@click.option('--include-completed/--no-completed', default=True, 
              help='Include completed elements')
@click.option('--order-by', type=click.Choice(['order_index', 'created_at', 'effort_hours']),
              default='order_index', help='Sort order')
@click.pass_context
def list(ctx, idea_id: int, include_completed: bool, order_by: str):
    """List elements for an idea"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    elements = IdeaElementAdapter.list(
        db, 
        idea_id=idea_id,
        include_completed=include_completed,
        order_by=order_by
    )
    
    if not elements:
        click.echo(f"No elements found for idea {idea_id}")
        return
    
    click.echo(f"\n📋 Elements for Idea {idea_id} ({len(elements)} total)")
    click.echo("=" * 60)
    
    for element in elements:
        status = "✅" if element.is_completed else "⏳"
        click.echo(f"{status} {element.id:2d}. {element.title}")
        click.echo(f"    Type: {element.type.value}")
        click.echo(f"    Effort: {element.effort_hours}h")
        click.echo(f"    Order: {element.order_index}")
        if element.description:
            click.echo(f"    Description: {element.description}")
        if element.is_completed and element.completed_at:
            click.echo(f"    Completed: {element.completed_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo()


@elements.command()
@click.argument('element_id', type=int)
@click.pass_context
def show(ctx, element_id: int):
    """Show details for an idea element"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    element = IdeaElementAdapter.get(db, element_id)
    if not element:
        click.echo(f"❌ Element {element_id} not found")
        return
    
    click.echo(f"\n🔍 Element {element.id}: {element.title}")
    click.echo("=" * 50)
    click.echo(f"Idea ID: {element.idea_id}")
    click.echo(f"Type: {element.type.value}")
    click.echo(f"Effort: {element.effort_hours}h")
    click.echo(f"Order: {element.order_index}")
    click.echo(f"Status: {'Completed' if element.is_completed else 'Incomplete'}")
    
    if element.description:
        click.echo(f"\nDescription:")
        click.echo(f"  {element.description}")
    
    if element.is_completed and element.completed_at:
        click.echo(f"\nCompleted: {element.completed_at.strftime('%Y-%m-%d %H:%M')}")
    
    click.echo(f"\nCreated: {element.created_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"Updated: {element.updated_at.strftime('%Y-%m-%d %H:%M')}")


@elements.command()
@click.argument('element_id', type=int)
@click.pass_context
def complete(ctx, element_id: int):
    """Mark an idea element as completed"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    element = IdeaElementAdapter.mark_completed(db, element_id)
    click.echo(f"✅ Marked element {element.id} as completed: {element.title}")


@elements.command()
@click.argument('element_id', type=int)
@click.pass_context
def incomplete(ctx, element_id: int):
    """Mark an idea element as incomplete"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    element = IdeaElementAdapter.mark_incomplete(db, element_id)
    click.echo(f"⏳ Marked element {element.id} as incomplete: {element.title}")


@elements.command()
@click.argument('idea_id', type=int)
@click.pass_context
def stats(ctx, idea_id: int):
    """Show completion statistics for an idea's elements"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    stats = IdeaElementAdapter.get_completion_stats(db, idea_id)
    
    click.echo(f"\n📊 Completion Statistics for Idea {idea_id}")
    click.echo("=" * 40)
    click.echo(f"Total Elements: {stats['total_elements']}")
    click.echo(f"Completed: {stats['completed_elements']}")
    click.echo(f"Completion: {stats['completion_percentage']:.1%}")
    click.echo(f"Total Effort: {stats['total_effort_hours']:.1f}h")
    click.echo(f"Completed Effort: {stats['completed_effort_hours']:.1f}h")
    click.echo(f"Effort Progress: {stats['effort_completion_percentage']:.1%}")


@elements.command()
@click.argument('element_id', type=int)
@click.pass_context
def delete(ctx, element_id: int):
    """Delete an idea element"""
    
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    # Get element first to show what we're deleting
    element = IdeaElementAdapter.get(db, element_id)
    if not element:
        click.echo(f"❌ Element {element_id} not found")
        return
    
    if click.confirm(f"Delete element '{element.title}'?"):
        deleted = IdeaElementAdapter.delete(db, element_id)
        if deleted:
            click.echo(f"✅ Deleted element {element_id}: {element.title}")
        else:
            click.echo(f"❌ Failed to delete element {element_id}")
    else:
        click.echo("Cancelled")
