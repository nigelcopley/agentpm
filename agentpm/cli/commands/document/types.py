"""
Document types and categories command.

Shows available document categories and types for the document add command.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agentpm.core.database.enums.types import DocumentCategory, DocumentType


@click.command()
@click.option('--category', '-c', help='Show types for specific category only')
@click.option('--format', 'output_format', type=click.Choice(['table', 'list', 'json']), 
              default='table', help='Output format')
def types(category: str, output_format: str):
    """Show available document categories and types.
    
    This command displays all available document categories and their associated
    document types. Use this to find the correct category and type values for
    the 'apm document add' command.
    
    Examples:
        apm document types                    # Show all categories and types
        apm document types --category=architecture  # Show types for architecture only
        apm document types --format=list      # Show as simple list
    """
    console = Console()
    
    if output_format == 'json':
        _show_json_format(console, category)
    elif output_format == 'list':
        _show_list_format(console, category)
    else:
        _show_table_format(console, category)


def _show_table_format(console: Console, category: str):
    """Show categories and types in a rich table format."""
    
    if category:
        # Show single category
        try:
            category_enum = DocumentCategory(category)
            _show_category_table(console, category_enum)
        except ValueError:
            console.print(f"[red]❌ Invalid category: {category}[/red]")
            console.print(f"[yellow]Available categories: {', '.join([c.value for c in DocumentCategory])}[/yellow]")
    else:
        # Show all categories
        console.print(Panel.fit(
            "[bold blue]📚 Document Categories and Types[/bold blue]\n"
            "Use these values with the 'apm document add' command",
            border_style="blue"
        ))
        
        for cat in DocumentCategory:
            _show_category_table(console, cat)


def _show_category_table(console: Console, category: DocumentCategory):
    """Show a single category with its types in a table."""
    
    # Get types for this category using the mapping
    category_types = _get_types_for_category(category)
    
    if not category_types:
        return
    
    # Create table for this category
    table = Table(
        title=f"[bold]{category.value.title()} Category[/bold]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Example Path", style="dim")
    
    for doc_type in category_types:
        # Use the full type name
        type_name = doc_type.value
        
        # Get description from docstring or create one
        description = _get_type_description(doc_type)
        
        # Example path
        example_path = f"docs/{category.value}/{type_name}/example.md"
        
        table.add_row(type_name, description, example_path)
    
    console.print(table)
    console.print()  # Add spacing between categories


def _show_list_format(console: Console, category: str):
    """Show categories and types in a simple list format."""
    
    if category:
        try:
            category_enum = DocumentCategory(category)
            category_types = _get_types_for_category(category_enum)
            
            console.print(f"[bold]{category_enum.value.title()} Types:[/bold]")
            for doc_type in category_types:
                console.print(f"  • {doc_type.value}")
        except ValueError:
            console.print(f"[red]❌ Invalid category: {category}[/red]")
    else:
        console.print("[bold]Available Categories:[/bold]")
        for cat in DocumentCategory:
            console.print(f"\n[bold]{cat.value.title()}:[/bold]")
            category_types = _get_types_for_category(cat)
            for doc_type in category_types:
                console.print(f"  • {doc_type.value}")


def _show_json_format(console: Console, category: str):
    """Show categories and types in JSON format."""
    import json
    
    if category:
        try:
            category_enum = DocumentCategory(category)
            category_types = _get_types_for_category(category_enum)
            result = {
                "category": category_enum.value,
                "types": [dt.value for dt in category_types]
            }
        except ValueError:
            result = {"error": f"Invalid category: {category}"}
    else:
        result = {}
        for cat in DocumentCategory:
            category_types = _get_types_for_category(cat)
            result[cat.value] = [dt.value for dt in category_types]
    
    console.print(json.dumps(result, indent=2))


def _get_types_for_category(category: DocumentCategory) -> list[DocumentType]:
    """Get all document types that belong to a specific category."""
    
    # Map categories to their document types
    category_mapping = {
        DocumentCategory.ARCHITECTURE: [
            DocumentType.ARCHITECTURE_DOC,
            DocumentType.DESIGN_DOC,
            DocumentType.ADR,
            DocumentType.TECHNICAL_SPEC,
        ],
        DocumentCategory.PROCESSES: [
            DocumentType.IMPLEMENTATION_PLAN,
            DocumentType.REFACTORING_GUIDE,
            DocumentType.MIGRATION_GUIDE,
            DocumentType.INTEGRATION_GUIDE,
            DocumentType.TEST_PLAN,
            DocumentType.TEST_REPORT,
            DocumentType.COVERAGE_REPORT,
            DocumentType.VALIDATION_REPORT,
        ],
        DocumentCategory.OPERATIONS: [
            DocumentType.RUNBOOK,
            DocumentType.DEPLOYMENT_GUIDE,
            DocumentType.MONITORING_GUIDE,
            DocumentType.INCIDENT_REPORT,
        ],
        DocumentCategory.GUIDES: [
            DocumentType.USER_GUIDE,
            DocumentType.ADMIN_GUIDE,
            DocumentType.DEVELOPER_GUIDE,
            DocumentType.TROUBLESHOOTING,
            DocumentType.FAQ,
            DocumentType.OTHER,
        ],
        DocumentCategory.REFERENCE: [
            DocumentType.API_DOC,
            DocumentType.SPECIFICATION,
        ],
        DocumentCategory.PLANNING: [
            DocumentType.IDEA,
            DocumentType.REQUIREMENTS,
            DocumentType.USER_STORY,
            DocumentType.USE_CASE,
            DocumentType.RESEARCH_REPORT,
            DocumentType.ANALYSIS_REPORT,
            DocumentType.INVESTIGATION_REPORT,
            DocumentType.ASSESSMENT_REPORT,
            DocumentType.FEASIBILITY_STUDY,
            DocumentType.COMPETITIVE_ANALYSIS,
        ],
        DocumentCategory.COMMUNICATION: [
            DocumentType.SESSION_SUMMARY,
            DocumentType.STATUS_REPORT,
            DocumentType.PROGRESS_REPORT,
            DocumentType.MILESTONE_REPORT,
            DocumentType.RETROSPECTIVE_REPORT,
        ],
        DocumentCategory.GOVERNANCE: [
            DocumentType.BUSINESS_PILLARS,
            DocumentType.MARKET_RESEARCH,
            DocumentType.STAKEHOLDER_ANALYSIS,
            DocumentType.QUALITY_GATES_SPEC,
        ],
    }
    
    return category_mapping.get(category, [])


def _get_type_description(doc_type: DocumentType) -> str:
    """Get a human-readable description for a document type."""
    
    descriptions = {
        # Architecture types
        "architecture_design_doc": "System design and architecture documentation",
        "architecture_decision_record": "Architecture Decision Records (ADRs)",
        "architecture_review": "Architecture review and analysis documents",
        "architecture_pattern": "Architectural patterns and best practices",
        
        # Communication types
        "communication_status_report": "Project status and progress reports",
        "communication_meeting_notes": "Meeting minutes and notes",
        "communication_announcement": "Project announcements and updates",
        "communication_handover": "Knowledge transfer and handover documents",
        
        # Development types
        "development_api_doc": "API documentation and specifications",
        "development_code_review": "Code review guidelines and templates",
        "development_deployment": "Deployment guides and procedures",
        "development_setup": "Development environment setup guides",
        
        # Governance types
        "governance_policy": "Project policies and standards",
        "governance_compliance": "Compliance and regulatory documentation",
        "governance_audit": "Audit reports and findings",
        "governance_risk": "Risk assessment and management documents",
        
        # Operations types
        "operations_runbook": "Operational runbooks and procedures",
        "operations_monitoring": "Monitoring and alerting documentation",
        "operations_incident": "Incident response and post-mortem reports",
        "operations_maintenance": "Maintenance schedules and procedures",
        
        # Planning types
        "planning_roadmap": "Product and project roadmaps",
        "planning_requirements": "Requirements and specifications",
        "planning_estimation": "Effort estimation and planning documents",
        "planning_milestone": "Milestone and deliverable tracking",
        
        # Process types
        "process_workflow": "Workflow and process documentation",
        "process_procedure": "Standard operating procedures",
        "process_checklist": "Checklists and validation procedures",
        "process_template": "Document and process templates",
        
        # Testing types
        "testing_strategy": "Testing strategy and approach",
        "testing_plan": "Test plans and test case documentation",
        "testing_results": "Test results and coverage reports",
        "testing_automation": "Test automation and CI/CD documentation",
        
        # Other types
        "other": "General documentation and miscellaneous content",
        "other_reference": "Reference materials and documentation",
        "other_tutorial": "Tutorials and learning materials",
        "other_faq": "Frequently Asked Questions",
    }
    
    return descriptions.get(doc_type.value, "Documentation and reference material")