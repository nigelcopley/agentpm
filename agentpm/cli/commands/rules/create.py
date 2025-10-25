"""
apm rules create - Create custom rules for the project
"""

import click
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any

from agentpm.core.database import DatabaseService
from agentpm.core.database.models.rule import Rule, EnforcementLevel
from agentpm.core.database.adapters import RuleAdapter
from agentpm.core.database.methods import projects as project_methods
from agentpm.cli.utils.project import get_current_project_id


@click.command()
@click.option(
    '--template',
    '-t',
    type=click.Choice(['timeboxing', 'coverage', 'required-tasks', 'custom']),
    help='Rule template to use'
)
@click.option(
    '--interactive',
    '-i',
    is_flag=True,
    help='Interactive mode for guided rule creation'
)
@click.pass_context
def create_rule(ctx: click.Context, template: str, interactive: bool):
    """
    Create a custom rule for the project.
    
    This command allows you to create custom governance rules tailored to your
    project's specific needs. You can use templates or create completely custom rules.
    
    \b
    Examples:
      apm rules create --template timeboxing    # Create timeboxing rule
      apm rules create --interactive           # Guided rule creation
      apm rules create                         # Custom rule creation
    """
    console = ctx.obj['console']
    
    # Find project database
    cwd = Path.cwd()
    aipm_dir = cwd / '.aipm'
    
    if not aipm_dir.exists():
        console.print("[red]❌ Not an AIPM project (no .aipm directory found)[/red]")
        console.print("[dim]Run 'apm init' to initialize this project[/dim]")
        raise click.Abort()
    
    db_path = aipm_dir / 'data' / 'aipm.db'
    if not db_path.exists():
        console.print("[red]❌ Project database not found[/red]")
        raise click.Abort()
    
    # Connect to database
    db = DatabaseService(str(db_path))
    
    # Get project
    try:
        project_id = get_current_project_id(ctx)
        project = project_methods.get_project(db, project_id)
        if not project:
            console.print("[red]❌ Project not found in database[/red]")
            raise click.Abort()
    except Exception as e:
        console.print(f"[red]❌ Error loading project: {e}[/red]")
        raise click.Abort()
    
    console.print("\n[bold blue]🔧 Custom Rule Creation[/bold blue]")
    console.print("Create governance rules tailored to your project's needs.\n")
    
    # Determine creation mode
    if interactive:
        rule_data = _interactive_rule_creation(console)
    elif template:
        rule_data = _template_rule_creation(console, template)
    else:
        rule_data = _custom_rule_creation(console)
    
    # Validate rule data
    if not _validate_rule_data(console, rule_data):
        console.print("[red]❌ Rule validation failed[/red]")
        raise click.Abort()
    
    # Create the rule
    try:
        rule = Rule(
            project_id=project.id,
            rule_id=rule_data['rule_id'],
            name=rule_data['name'],
            description=rule_data['description'],
            category=rule_data.get('category'),
            enforcement_level=EnforcementLevel(rule_data['enforcement_level']),
            validation_logic=rule_data.get('validation_logic'),
            error_message=rule_data.get('error_message'),
            config=rule_data.get('config', {}),
            enabled=rule_data.get('enabled', True)
        )
        
        created_rule = RuleAdapter.create(db, rule)
        
        console.print(f"\n[green]✅ Rule created successfully![/green]")
        console.print(f"Rule ID: [cyan]{created_rule.rule_id}[/cyan]")
        console.print(f"Name: [cyan]{created_rule.name}[/cyan]")
        console.print(f"Enforcement: [yellow]{created_rule.enforcement_level.value}[/yellow]")
        
        console.print("\n[dim]Commands:[/dim]")
        console.print(f"  apm rules show {created_rule.rule_id}    # View rule details")
        console.print("  apm rules list                    # View all rules")
        
    except Exception as e:
        console.print(f"\n[red]❌ Failed to create rule: {e}[/red]")
        raise click.Abort()


def _interactive_rule_creation(console: Console) -> Dict[str, Any]:
    """Interactive guided rule creation."""
    console.print("[bold]Interactive Rule Creation[/bold]")
    console.print("I'll guide you through creating a custom rule step by step.\n")
    
    # Rule type selection
    console.print("What type of rule would you like to create?")
    rule_types = {
        '1': ('timeboxing', 'Time-boxing rule (limit task duration)'),
        '2': ('coverage', 'Test coverage rule (minimum coverage requirement)'),
        '3': ('required-tasks', 'Required task types rule (work item requirements)'),
        '4': ('code-quality', 'Code quality rule (naming, structure, etc.)'),
        '5': ('workflow', 'Workflow rule (process requirements)'),
        '6': ('custom', 'Custom rule (completely custom validation)')
    }
    
    for key, (_, description) in rule_types.items():
        console.print(f"  {key}. {description}")
    
    choice = Prompt.ask("Select rule type", choices=list(rule_types.keys()), default="6")
    rule_type = rule_types[choice][0]
    
    return _template_rule_creation(console, rule_type)


def _template_rule_creation(console: Console, template: str) -> Dict[str, Any]:
    """Create rule from template."""
    console.print(f"[bold]Creating {template} rule[/bold]\n")
    
    if template == 'timeboxing':
        return _create_timeboxing_rule(console)
    elif template == 'coverage':
        return _create_coverage_rule(console)
    elif template == 'required-tasks':
        return _create_required_tasks_rule(console)
    elif template == 'code-quality':
        return _create_code_quality_rule(console)
    elif template == 'workflow':
        return _create_workflow_rule(console)
    else:
        return _custom_rule_creation(console)


def _create_timeboxing_rule(console: Console) -> Dict[str, Any]:
    """Create a timeboxing rule."""
    console.print("Creating a time-boxing rule to limit task duration.\n")
    
    # Get task type
    task_types = ['IMPLEMENTATION', 'TESTING', 'DESIGN', 'DOCUMENTATION', 'ANALYSIS', 'RESEARCH', 'REFACTORING', 'BUGFIX', 'HOTFIX', 'PLANNING', 'DEPLOYMENT']
    console.print("Available task types:")
    for i, task_type in enumerate(task_types, 1):
        console.print(f"  {i}. {task_type}")
    
    choice = Prompt.ask("Select task type", choices=[str(i) for i in range(1, len(task_types) + 1)], default="1")
    task_type = task_types[int(choice) - 1]
    
    # Get time limit
    max_hours = float(Prompt.ask("Maximum hours allowed", default="4.0"))
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE'],
        default='BLOCK'
    )
    
    # Generate rule data
    rule_id = f"CUSTOM-{task_type[:3]}-{int(max_hours)}H"
    name = f"custom-timeboxing-{task_type.lower()}"
    description = f"{task_type} tasks limited to ≤{max_hours} hours"
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': 'CUSTOM',
        'enforcement_level': enforcement,
        'validation_logic': f"effort_hours > {max_hours}",
        'error_message': f"{task_type} tasks limited to {max_hours} hours",
        'config': {
            'max_hours': max_hours,
            'task_type': task_type
        },
        'enabled': True
    }


def _create_coverage_rule(console: Console) -> Dict[str, Any]:
    """Create a test coverage rule."""
    console.print("Creating a test coverage rule.\n")
    
    # Get coverage threshold
    min_coverage = float(Prompt.ask("Minimum test coverage (%)", default="90.0"))
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE'],
        default='BLOCK'
    )
    
    # Generate rule data
    rule_id = f"CUSTOM-COV-{int(min_coverage)}"
    name = f"custom-test-coverage-{int(min_coverage)}"
    description = f"Minimum test coverage ≥{min_coverage}%"
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': 'CUSTOM',
        'enforcement_level': enforcement,
        'validation_logic': f"test_coverage < {min_coverage}",
        'error_message': f"Test coverage must be >= {min_coverage}%",
        'config': {
            'min_coverage': min_coverage
        },
        'enabled': True
    }


def _create_required_tasks_rule(console: Console) -> Dict[str, Any]:
    """Create a required tasks rule."""
    console.print("Creating a required task types rule.\n")
    
    # Get work item type
    work_item_types = ['FEATURE', 'ENHANCEMENT', 'BUGFIX', 'RESEARCH', 'PLANNING', 'REFACTORING']
    console.print("Available work item types:")
    for i, wi_type in enumerate(work_item_types, 1):
        console.print(f"  {i}. {wi_type}")
    
    choice = Prompt.ask("Select work item type", choices=[str(i) for i in range(1, len(work_item_types) + 1)], default="1")
    work_item_type = work_item_types[int(choice) - 1]
    
    # Get required task types
    task_types = ['DESIGN', 'IMPLEMENTATION', 'TESTING', 'DOCUMENTATION', 'ANALYSIS', 'RESEARCH', 'REFACTORING', 'BUGFIX', 'HOTFIX', 'PLANNING', 'DEPLOYMENT']
    console.print("\nAvailable task types (select multiple, comma-separated):")
    for i, task_type in enumerate(task_types, 1):
        console.print(f"  {i}. {task_type}")
    
    choices = Prompt.ask("Select required task types (e.g., 1,2,3)", default="1,2,3")
    required_types = [task_types[int(c.strip()) - 1] for c in choices.split(',')]
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE'],
        default='BLOCK'
    )
    
    # Generate rule data
    rule_id = f"CUSTOM-REQ-{work_item_type[:3]}"
    name = f"custom-required-tasks-{work_item_type.lower()}"
    description = f"{work_item_type} requires {', '.join(required_types)} tasks"
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': 'CUSTOM',
        'enforcement_level': enforcement,
        'validation_logic': 'missing_required_task_types',
        'error_message': f"{work_item_type} work items require {', '.join(required_types)} tasks",
        'config': {
            'required_types': required_types,
            'work_item_type': work_item_type
        },
        'enabled': True
    }


def _create_code_quality_rule(console: Console) -> Dict[str, Any]:
    """Create a code quality rule."""
    console.print("Creating a code quality rule.\n")
    
    # Get rule name and description
    name = Prompt.ask("Rule name (kebab-case)", default="custom-code-quality")
    description = Prompt.ask("Rule description", default="Custom code quality requirement")
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE'],
        default='GUIDE'
    )
    
    # Generate rule data
    rule_id = f"CUSTOM-CQ-{name.upper().replace('-', '')[:8]}"
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': 'CUSTOM',
        'enforcement_level': enforcement,
        'validation_logic': 'code_quality_violation',
        'error_message': f"Code quality violation: {description}",
        'config': {},
        'enabled': True
    }


def _create_workflow_rule(console: Console) -> Dict[str, Any]:
    """Create a workflow rule."""
    console.print("Creating a workflow rule.\n")
    
    # Get rule name and description
    name = Prompt.ask("Rule name (kebab-case)", default="custom-workflow")
    description = Prompt.ask("Rule description", default="Custom workflow requirement")
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE'],
        default='GUIDE'
    )
    
    # Generate rule data
    rule_id = f"CUSTOM-WF-{name.upper().replace('-', '')[:8]}"
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': 'CUSTOM',
        'enforcement_level': enforcement,
        'validation_logic': 'workflow_violation',
        'error_message': f"Workflow violation: {description}",
        'config': {},
        'enabled': True
    }


def _custom_rule_creation(console: Console) -> Dict[str, Any]:
    """Create a completely custom rule."""
    console.print("[bold]Custom Rule Creation[/bold]")
    console.print("Create a completely custom rule with your own validation logic.\n")
    
    # Get basic rule information
    rule_id = Prompt.ask("Rule ID (format: CUSTOM-XXX-001)", default="CUSTOM-001")
    name = Prompt.ask("Rule name (kebab-case)", default="custom-rule")
    description = Prompt.ask("Rule description")
    category = Prompt.ask("Category", default="CUSTOM")
    
    # Get enforcement level
    enforcement = Prompt.ask(
        "Enforcement level",
        choices=['BLOCK', 'LIMIT', 'GUIDE', 'ENHANCE'],
        default='GUIDE'
    )
    
    # Get validation logic
    console.print("\nValidation logic patterns:")
    console.print("  - effort_hours > 4.0")
    console.print("  - test_coverage < 90.0")
    console.print("  - missing_required_task_types")
    console.print("  - custom_violation")
    
    validation_logic = Prompt.ask("Validation logic", default="custom_violation")
    error_message = Prompt.ask("Error message", default=f"Rule violation: {description}")
    
    # Get configuration
    config = {}
    if Confirm.ask("Add configuration parameters?", default=False):
        while True:
            key = Prompt.ask("Config key (or press Enter to finish)")
            if not key:
                break
            value = Prompt.ask(f"Config value for '{key}'")
            try:
                # Try to parse as number
                config[key] = float(value) if '.' in value else int(value)
            except ValueError:
                # Keep as string
                config[key] = value
    
    return {
        'rule_id': rule_id,
        'name': name,
        'description': description,
        'category': category,
        'enforcement_level': enforcement,
        'validation_logic': validation_logic,
        'error_message': error_message,
        'config': config,
        'enabled': True
    }


def _validate_rule_data(console: Console, rule_data: Dict[str, Any]) -> bool:
    """Validate rule data before creation."""
    console.print("\n[bold]Validating Rule Data[/bold]")
    
    # Check required fields
    required_fields = ['rule_id', 'name', 'description', 'enforcement_level']
    for field in required_fields:
        if not rule_data.get(field):
            console.print(f"[red]❌ Missing required field: {field}[/red]")
            return False
    
    # Validate rule ID format
    rule_id = rule_data['rule_id']
    if not rule_id.startswith('CUSTOM-'):
        console.print("[red]❌ Rule ID must start with 'CUSTOM-'[/red]")
        return False
    
    # Validate name format (kebab-case)
    name = rule_data['name']
    if not all(c.islower() or c.isdigit() or c == '-' for c in name):
        console.print("[red]❌ Rule name must be kebab-case (lowercase-with-hyphens)[/red]")
        return False
    
    # Show rule summary
    console.print("\n[bold]Rule Summary[/bold]")
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Rule ID", rule_data['rule_id'])
    table.add_row("Name", rule_data['name'])
    table.add_row("Description", rule_data['description'])
    table.add_row("Category", rule_data.get('category', 'N/A'))
    table.add_row("Enforcement", rule_data['enforcement_level'])
    table.add_row("Validation Logic", rule_data.get('validation_logic', 'N/A'))
    
    if rule_data.get('config'):
        table.add_row("Config", str(rule_data['config']))
    
    console.print(table)
    
    return Confirm.ask("\nCreate this rule?", default=True)
