"""
Work Item Types Command

Exposes work item-related Pydantic models and enums via CLI.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agentpm.core.database.enums import (
    WorkItemType, WorkItemStatus, ProjectType, Phase, 
    DevelopmentPhilosophy
)
from agentpm.core.database.enums.types import ProjectManagementPhilosophy


@click.command()
@click.option('--type', 'type_filter', 
              type=click.Choice([
                  'work-item-type', 'work-item-status', 'project-type', 
                  'phase', 'development-philosophy', 'pm-philosophy', 'all'
              ]),
              default='all',
              help='Filter which types to display')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'list', 'json']),
              default='table',
              help='Output format')
@click.pass_context
def types(ctx: click.Context, type_filter: str, output_format: str):
    """
    📋 Show available work item types, statuses, and related enums.
    
    Displays all valid values for work item-related enums that can be used
    in work item commands. Essential for AI agents and users to discover
    valid options without hardcoding values.
    
    \b
    Examples:
      apm work-item types                           # Show all types
      apm work-item types --type=work-item-type     # Show only work item types
      apm work-item types --type=phase              # Show project phases
      apm work-item types --format=list             # Simple list format
    """
    console = Console()
    
    if type_filter == 'all' or type_filter == 'work-item-type':
        _show_work_item_types(console, output_format)
    
    if type_filter == 'all' or type_filter == 'work-item-status':
        _show_work_item_statuses(console, output_format)
    
    if type_filter == 'all' or type_filter == 'project-type':
        _show_project_types(console, output_format)
    
    if type_filter == 'all' or type_filter == 'phase':
        _show_phases(console, output_format)
    
    if type_filter == 'all' or type_filter == 'development-philosophy':
        _show_development_philosophies(console, output_format)
    
    if type_filter == 'all' or type_filter == 'pm-philosophy':
        _show_pm_philosophies(console, output_format)


def _show_work_item_types(console: Console, output_format: str):
    """Show work item types with descriptions."""
    if output_format == 'table':
        table = Table(title="📋 Work Item Types", show_header=True, header_style="bold blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        labels = WorkItemType.labels()
        for work_item_type in WorkItemType:
            table.add_row(work_item_type.value, labels.get(work_item_type.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(WorkItemType)} work item types[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Work Item Types", style="bold blue"))
        labels = WorkItemType.labels()
        for work_item_type in WorkItemType:
            console.print(f"  • {work_item_type.value}: {labels.get(work_item_type.value, '')}")
    
    elif output_format == 'json':
        import json
        labels = WorkItemType.labels()
        types_data = {
            "work_item_types": [
                {"value": work_item_type.value, "description": labels.get(work_item_type.value, "")}
                for work_item_type in WorkItemType
            ]
        }
        console.print(json.dumps(types_data, indent=2))


def _show_work_item_statuses(console: Console, output_format: str):
    """Show work item statuses."""
    if output_format == 'table':
        table = Table(title="📋 Work Item Statuses", show_header=True, header_style="bold blue")
        table.add_column("Status", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        status_descriptions = {
            WorkItemStatus.PROPOSED.value: "Initial proposal, not yet validated",
            WorkItemStatus.VALIDATED.value: "Validated and ready for acceptance",
            WorkItemStatus.ACCEPTED.value: "Accepted and ready to start",
            WorkItemStatus.IN_PROGRESS.value: "Currently being worked on",
            WorkItemStatus.REVIEW.value: "Under review",
            WorkItemStatus.COMPLETED.value: "Completed successfully",
            WorkItemStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        
        for status in WorkItemStatus:
            table.add_row(status.value, status_descriptions.get(status.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(WorkItemStatus)} work item statuses[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Work Item Statuses", style="bold blue"))
        status_descriptions = {
            WorkItemStatus.PROPOSED.value: "Initial proposal, not yet validated",
            WorkItemStatus.VALIDATED.value: "Validated and ready for acceptance",
            WorkItemStatus.ACCEPTED.value: "Accepted and ready to start",
            WorkItemStatus.IN_PROGRESS.value: "Currently being worked on",
            WorkItemStatus.REVIEW.value: "Under review",
            WorkItemStatus.COMPLETED.value: "Completed successfully",
            WorkItemStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        for status in WorkItemStatus:
            console.print(f"  • {status.value}: {status_descriptions.get(status.value, '')}")
    
    elif output_format == 'json':
        import json
        status_descriptions = {
            WorkItemStatus.PROPOSED.value: "Initial proposal, not yet validated",
            WorkItemStatus.VALIDATED.value: "Validated and ready for acceptance",
            WorkItemStatus.ACCEPTED.value: "Accepted and ready to start",
            WorkItemStatus.IN_PROGRESS.value: "Currently being worked on",
            WorkItemStatus.REVIEW.value: "Under review",
            WorkItemStatus.COMPLETED.value: "Completed successfully",
            WorkItemStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        statuses_data = {
            "work_item_statuses": [
                {"value": status.value, "description": status_descriptions.get(status.value, "")}
                for status in WorkItemStatus
            ]
        }
        console.print(json.dumps(statuses_data, indent=2))


def _show_project_types(console: Console, output_format: str):
    """Show project types."""
    if output_format == 'table':
        table = Table(title="📋 Project Types", show_header=True, header_style="bold blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        type_descriptions = {
            ProjectType.GREENFIELD.value: "New project from scratch",
            ProjectType.BROWNFIELD.value: "Existing codebase modernization",
            ProjectType.MAINTENANCE.value: "Ongoing support and updates",
            ProjectType.RESEARCH.value: "Experimental/spike project",
        }
        
        for project_type in ProjectType:
            table.add_row(project_type.value, type_descriptions.get(project_type.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(ProjectType)} project types[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Project Types", style="bold blue"))
        type_descriptions = {
            ProjectType.GREENFIELD.value: "New project from scratch",
            ProjectType.BROWNFIELD.value: "Existing codebase modernization",
            ProjectType.MAINTENANCE.value: "Ongoing support and updates",
            ProjectType.RESEARCH.value: "Experimental/spike project",
        }
        for project_type in ProjectType:
            console.print(f"  • {project_type.value}: {type_descriptions.get(project_type.value, '')}")
    
    elif output_format == 'json':
        import json
        type_descriptions = {
            ProjectType.GREENFIELD.value: "New project from scratch",
            ProjectType.BROWNFIELD.value: "Existing codebase modernization",
            ProjectType.MAINTENANCE.value: "Ongoing support and updates",
            ProjectType.RESEARCH.value: "Experimental/spike project",
        }
        types_data = {
            "project_types": [
                {"value": project_type.value, "description": type_descriptions.get(project_type.value, "")}
                for project_type in ProjectType
            ]
        }
        console.print(json.dumps(types_data, indent=2))


def _show_phases(console: Console, output_format: str):
    """Show project phases."""
    if output_format == 'table':
        table = Table(title="📋 Project Phases", show_header=True, header_style="bold blue")
        table.add_column("Phase", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        phase_descriptions = {
            Phase.D1_DISCOVERY.value: "Discovery - Market research, requirements gathering",
            Phase.P1_PLAN.value: "Planning - Architecture, design, task decomposition",
            Phase.I1_IMPLEMENTATION.value: "Implementation - Coding, building",
            Phase.R1_REVIEW.value: "Review - Testing, QA, validation",
            Phase.O1_OPERATIONS.value: "Operations - Deployment, go-live, monitoring",
            Phase.E1_EVOLUTION.value: "Evolution - Iteration, improvements, technical debt",
        }
        
        for phase in Phase:
            table.add_row(phase.value, phase_descriptions.get(phase.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(Phase)} project phases[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Project Phases", style="bold blue"))
        phase_descriptions = {
            Phase.D1_DISCOVERY.value: "Discovery - Market research, requirements gathering",
            Phase.P1_PLAN.value: "Planning - Architecture, design, task decomposition",
            Phase.I1_IMPLEMENTATION.value: "Implementation - Coding, building",
            Phase.R1_REVIEW.value: "Review - Testing, QA, validation",
            Phase.O1_OPERATIONS.value: "Operations - Deployment, go-live, monitoring",
            Phase.E1_EVOLUTION.value: "Evolution - Iteration, improvements, technical debt",
        }
        for phase in Phase:
            console.print(f"  • {phase.value}: {phase_descriptions.get(phase.value, '')}")
    
    elif output_format == 'json':
        import json
        phase_descriptions = {
            Phase.D1_DISCOVERY.value: "Discovery - Market research, requirements gathering",
            Phase.P1_PLAN.value: "Planning - Architecture, design, task decomposition",
            Phase.I1_IMPLEMENTATION.value: "Implementation - Coding, building",
            Phase.R1_REVIEW.value: "Review - Testing, QA, validation",
            Phase.O1_OPERATIONS.value: "Operations - Deployment, go-live, monitoring",
            Phase.E1_EVOLUTION.value: "Evolution - Iteration, improvements, technical debt",
        }
        phases_data = {
            "project_phases": [
                {"value": phase.value, "description": phase_descriptions.get(phase.value, "")}
                for phase in Phase
            ]
        }
        console.print(json.dumps(phases_data, indent=2))


def _show_development_philosophies(console: Console, output_format: str):
    """Show development philosophies."""
    if output_format == 'table':
        table = Table(title="📋 Development Philosophies", show_header=True, header_style="bold blue")
        table.add_column("Philosophy", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        philosophy_descriptions = {
            DevelopmentPhilosophy.KISS_FIRST.value: "Keep It Simple, Stupid - Start simple",
            DevelopmentPhilosophy.YAGNI.value: "You Aren't Gonna Need It - Don't over-engineer",
            DevelopmentPhilosophy.DRY.value: "Don't Repeat Yourself - Avoid duplication",
            DevelopmentPhilosophy.SOLID.value: "SOLID principles - Object-oriented design",
            DevelopmentPhilosophy.BEHAVIOUR_DRIVEN.value: "Behaviour-driven development",
            DevelopmentPhilosophy.DESIGN_DRIVEN.value: "Design-driven development",
            DevelopmentPhilosophy.TEST_DRIVEN.value: "Test-driven development",
            DevelopmentPhilosophy.AGILE.value: "Agile methodology",
            DevelopmentPhilosophy.PROFESSIONAL_STANDARDS.value: "Professional standards and practices",
            DevelopmentPhilosophy.CONTEXT_AWARE.value: "Context-aware development",
            DevelopmentPhilosophy.DOMAIN_DRIVEN.value: "Domain-driven design",
            DevelopmentPhilosophy.DATA_DRIVEN.value: "Data-driven development",
            DevelopmentPhilosophy.DATA_AWARE.value: "Data-aware development",
        }
        
        for philosophy in DevelopmentPhilosophy:
            table.add_row(philosophy.value, philosophy_descriptions.get(philosophy.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(DevelopmentPhilosophy)} development philosophies[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Development Philosophies", style="bold blue"))
        philosophy_descriptions = {
            DevelopmentPhilosophy.KISS_FIRST.value: "Keep It Simple, Stupid - Start simple",
            DevelopmentPhilosophy.YAGNI.value: "You Aren't Gonna Need It - Don't over-engineer",
            DevelopmentPhilosophy.DRY.value: "Don't Repeat Yourself - Avoid duplication",
            DevelopmentPhilosophy.SOLID.value: "SOLID principles - Object-oriented design",
            DevelopmentPhilosophy.BEHAVIOUR_DRIVEN.value: "Behaviour-driven development",
            DevelopmentPhilosophy.DESIGN_DRIVEN.value: "Design-driven development",
            DevelopmentPhilosophy.TEST_DRIVEN.value: "Test-driven development",
            DevelopmentPhilosophy.AGILE.value: "Agile methodology",
            DevelopmentPhilosophy.PROFESSIONAL_STANDARDS.value: "Professional standards and practices",
            DevelopmentPhilosophy.CONTEXT_AWARE.value: "Context-aware development",
            DevelopmentPhilosophy.DOMAIN_DRIVEN.value: "Domain-driven design",
            DevelopmentPhilosophy.DATA_DRIVEN.value: "Data-driven development",
            DevelopmentPhilosophy.DATA_AWARE.value: "Data-aware development",
        }
        for philosophy in DevelopmentPhilosophy:
            console.print(f"  • {philosophy.value}: {philosophy_descriptions.get(philosophy.value, '')}")
    
    elif output_format == 'json':
        import json
        philosophy_descriptions = {
            DevelopmentPhilosophy.KISS_FIRST.value: "Keep It Simple, Stupid - Start simple",
            DevelopmentPhilosophy.YAGNI.value: "You Aren't Gonna Need It - Don't over-engineer",
            DevelopmentPhilosophy.DRY.value: "Don't Repeat Yourself - Avoid duplication",
            DevelopmentPhilosophy.SOLID.value: "SOLID principles - Object-oriented design",
            DevelopmentPhilosophy.BEHAVIOUR_DRIVEN.value: "Behaviour-driven development",
            DevelopmentPhilosophy.DESIGN_DRIVEN.value: "Design-driven development",
            DevelopmentPhilosophy.TEST_DRIVEN.value: "Test-driven development",
            DevelopmentPhilosophy.AGILE.value: "Agile methodology",
            DevelopmentPhilosophy.PROFESSIONAL_STANDARDS.value: "Professional standards and practices",
            DevelopmentPhilosophy.CONTEXT_AWARE.value: "Context-aware development",
            DevelopmentPhilosophy.DOMAIN_DRIVEN.value: "Domain-driven design",
            DevelopmentPhilosophy.DATA_DRIVEN.value: "Data-driven development",
            DevelopmentPhilosophy.DATA_AWARE.value: "Data-aware development",
        }
        philosophies_data = {
            "development_philosophies": [
                {"value": philosophy.value, "description": philosophy_descriptions.get(philosophy.value, "")}
                for philosophy in DevelopmentPhilosophy
            ]
        }
        console.print(json.dumps(philosophies_data, indent=2))


def _show_pm_philosophies(console: Console, output_format: str):
    """Show project management philosophies."""
    if output_format == 'table':
        table = Table(title="📋 Project Management Philosophies", show_header=True, header_style="bold blue")
        table.add_column("Philosophy", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        pm_philosophy_descriptions = {
            ProjectManagementPhilosophy.LEAN.value: "Eliminate waste, MVP focus, just-enough planning/docs",
            ProjectManagementPhilosophy.AGILE.value: "Iterative delivery, time-boxed, working software over docs",
            ProjectManagementPhilosophy.PMBOK.value: "Structured, comprehensive, formal processes and gates",
            ProjectManagementPhilosophy.AIPM_HYBRID.value: "AIPM's default: Agile time-boxing + PMBOK dependencies + Lean waste elimination",
        }
        
        for philosophy in ProjectManagementPhilosophy:
            table.add_row(philosophy.value, pm_philosophy_descriptions.get(philosophy.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(ProjectManagementPhilosophy)} PM philosophies[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📋 Project Management Philosophies", style="bold blue"))
        pm_philosophy_descriptions = {
            ProjectManagementPhilosophy.LEAN.value: "Eliminate waste, MVP focus, just-enough planning/docs",
            ProjectManagementPhilosophy.AGILE.value: "Iterative delivery, time-boxed, working software over docs",
            ProjectManagementPhilosophy.PMBOK.value: "Structured, comprehensive, formal processes and gates",
            ProjectManagementPhilosophy.AIPM_HYBRID.value: "AIPM's default: Agile time-boxing + PMBOK dependencies + Lean waste elimination",
        }
        for philosophy in ProjectManagementPhilosophy:
            console.print(f"  • {philosophy.value}: {pm_philosophy_descriptions.get(philosophy.value, '')}")
    
    elif output_format == 'json':
        import json
        pm_philosophy_descriptions = {
            ProjectManagementPhilosophy.LEAN.value: "Eliminate waste, MVP focus, just-enough planning/docs",
            ProjectManagementPhilosophy.AGILE.value: "Iterative delivery, time-boxed, working software over docs",
            ProjectManagementPhilosophy.PMBOK.value: "Structured, comprehensive, formal processes and gates",
            ProjectManagementPhilosophy.AIPM_HYBRID.value: "AIPM's default: Agile time-boxing + PMBOK dependencies + Lean waste elimination",
        }
        philosophies_data = {
            "project_management_philosophies": [
                {"value": philosophy.value, "description": pm_philosophy_descriptions.get(philosophy.value, "")}
                for philosophy in ProjectManagementPhilosophy
            ]
        }
        console.print(json.dumps(philosophies_data, indent=2))
