"""
Testing Configuration Management Commands

Provides commands to manage testing configuration for projects.
"""

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agentpm.core.testing import (
    TestingConfigManager,
    ensure_testing_config_installed,
    create_agentpm_testing_config
)


@click.group(name='testing')
def testing_group():
    """Manage testing configuration and category-specific coverage requirements."""
    pass


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.pass_context
def status(ctx: click.Context, project_path: str):
    """Show testing configuration status and category information."""
    console = Console()
    
    try:
        manager = TestingConfigManager()
        config = manager.load_merged_config(project_path)
        info = manager.get_config_info(project_path)
        
        # Show configuration status
        status_table = Table(title="🧪 Testing Configuration Status")
        status_table.add_column("Setting", style="cyan")
        status_table.add_column("Value", style="green")
        
        status_table.add_row("Version", config.version)
        status_table.add_row("Source", config.source)
        status_table.add_row("Global Config", "✅" if info['global_config_exists'] else "❌")
        status_table.add_row("Project Config", "✅" if info['project_config_exists'] else "❌")
        status_table.add_row("Categories", str(len(config.categories)))
        
        console.print(status_table)
        
        # Show category details
        if config.categories:
            categories_table = Table(title="📊 Testing Categories")
            categories_table.add_column("Category", style="cyan")
            categories_table.add_column("Coverage", justify="right", style="green")
            categories_table.add_column("Description", style="dim")
            
            for category_name, category_config in config.categories.items():
                coverage = category_config.get('min_coverage', 0)
                description = category_config.get('description', 'No description')
                categories_table.add_row(
                    category_name.replace('_', ' ').title(),
                    f"{coverage}%",
                    description
                )
            
            console.print(categories_table)
        
        # Show file paths
        console.print(f"\n📁 [cyan]Configuration Files:[/cyan]")
        console.print(f"   Global: {info['global_config_path']}")
        console.print(f"   Project: {info['project_config_path']}")
        
    except Exception as e:
        console.print(f"❌ [red]Error loading testing configuration: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing configuration')
@click.pass_context
def install(ctx: click.Context, project_path: str, force: bool):
    """Install testing configuration for the project."""
    console = Console()
    
    try:
        # Check if config already exists
        config_path = Path(project_path) / '.agentpm' / 'testing_config.json'
        if config_path.exists() and not force:
            console.print(f"⚠️  [yellow]Testing configuration already exists at {config_path}[/yellow]")
            console.print("Use --force to overwrite existing configuration")
            return
        
        # Install configuration
        success = ensure_testing_config_installed(project_path)
        
        if success:
            console.print("✅ [green]Testing configuration installed successfully![/green]")
            console.print(f"📁 [dim]Configuration file: {config_path}[/dim]")
        else:
            console.print("❌ [red]Failed to install testing configuration[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error installing testing configuration: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.option('--category', '-c', help='Specific category to show details for')
@click.pass_context
def show(ctx: click.Context, project_path: str, category: Optional[str]):
    """Show detailed testing configuration."""
    console = Console()
    
    try:
        manager = TestingConfigManager()
        config = manager.load_merged_config(project_path)
        
        if category:
            # Show specific category
            if category in config.categories:
                category_config = config.categories[category]
                
                panel_content = f"""
[bold]Category:[/bold] {category.replace('_', ' ').title()}
[bold]Coverage Requirement:[/bold] {category_config.get('min_coverage', 0)}%
[bold]Description:[/bold] {category_config.get('description', 'No description')}

[bold]Path Patterns:[/bold]
"""
                for pattern in category_config.get('path_patterns', []):
                    panel_content += f"  • {pattern}\n"
                
                console.print(Panel(panel_content.strip(), title=f"🧪 {category.replace('_', ' ').title()} Category"))
            else:
                console.print(f"❌ [red]Category '{category}' not found[/red]")
                console.print(f"Available categories: {', '.join(config.categories.keys())}")
        else:
            # Show all categories
            for category_name, category_config in config.categories.items():
                panel_content = f"""
[bold]Coverage Requirement:[/bold] {category_config.get('min_coverage', 0)}%
[bold]Description:[/bold] {category_config.get('description', 'No description')}

[bold]Path Patterns:[/bold]
"""
                for pattern in category_config.get('path_patterns', []):
                    panel_content += f"  • {pattern}\n"
                
                console.print(Panel(panel_content.strip(), title=f"🧪 {category_name.replace('_', ' ').title()}"))
                console.print()
                
    except Exception as e:
        console.print(f"❌ [red]Error showing testing configuration: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: stdout)')
@click.pass_context
def export(ctx: click.Context, project_path: str, output: Optional[str]):
    """Export testing configuration to JSON file."""
    console = Console()
    
    try:
        manager = TestingConfigManager()
        config = manager.load_merged_config(project_path)
        
        # Prepare export data
        export_data = {
            "version": config.version,
            "source": config.source,
            "testing_categories": config.categories
        }
        
        # Output to file or stdout
        if output:
            output_path = Path(output)
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            console.print(f"✅ [green]Configuration exported to {output_path}[/green]")
        else:
            console.print(json.dumps(export_data, indent=2))
            
    except Exception as e:
        console.print(f"❌ [red]Error exporting testing configuration: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.pass_context
def validate(ctx: click.Context, project_path: str):
    """Validate testing configuration and show any issues."""
    console = Console()
    
    try:
        manager = TestingConfigManager()
        config = manager.load_merged_config(project_path)
        
        # Validate configuration
        issues = []
        warnings = []
        
        # Check for required categories
        required_categories = ['critical_paths', 'user_facing', 'data_layer', 'security', 'utilities']
        for category in required_categories:
            if category not in config.categories:
                issues.append(f"Missing required category: {category}")
        
        # Check coverage requirements
        for category_name, category_config in config.categories.items():
            coverage = category_config.get('min_coverage', 0)
            if coverage < 0 or coverage > 100:
                issues.append(f"Invalid coverage for {category_name}: {coverage}% (must be 0-100)")
            elif coverage < 50:
                warnings.append(f"Low coverage requirement for {category_name}: {coverage}%")
            
            # Check path patterns
            patterns = category_config.get('path_patterns', [])
            if not patterns:
                warnings.append(f"No path patterns defined for {category_name}")
        
        # Show results
        if not issues and not warnings:
            console.print("✅ [green]Testing configuration is valid![/green]")
        else:
            if issues:
                console.print("❌ [red]Configuration Issues:[/red]")
                for issue in issues:
                    console.print(f"  • {issue}")
                console.print()
            
            if warnings:
                console.print("⚠️  [yellow]Configuration Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")
                console.print()
                
    except Exception as e:
        console.print(f"❌ [red]Error validating testing configuration: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.option('--force', '-f', is_flag=True, help='Force reconfiguration even if already configured')
@click.pass_context
def configure_rules(ctx: click.Context, project_path: str, force: bool):
    """Configure generic testing rules with project-specific path patterns."""
    console = Console()
    
    try:
        from agentpm.core.testing.rule_configurator import TestingRuleConfigurator
        from agentpm.core.database.service import DatabaseService
        from agentpm.cli.utils.services import get_database_service
        
        # Get database service
        db = get_database_service(Path(project_path))
        
        # Create configurator
        configurator = TestingRuleConfigurator(db)
        
        # Get project ID (assuming we're in an APM project)
        # For now, we'll use a default project ID of 1
        project_id = 1
        
        console.print("🔧 [cyan]Configuring testing rules with project-specific patterns...[/cyan]")
        
        # Configure rules
        result = configurator.configure_project_rules(project_id, project_path)
        
        if result['success']:
            console.print(f"✅ [green]Successfully configured {result['updated_rules']} testing rules![/green]")
            
            if result['updated_rules'] > 0:
                rules_table = Table(title="📊 Configured Testing Rules")
                rules_table.add_column("Rule ID", style="cyan")
                rules_table.add_column("Category", style="green")
                rules_table.add_column("Coverage", justify="right", style="yellow")
                rules_table.add_column("Path Patterns", style="dim")
                
                for rule in result['rules']:
                    patterns_str = ", ".join(rule['path_patterns'][:2])
                    if len(rule['path_patterns']) > 2:
                        patterns_str += f" (+{len(rule['path_patterns'])-2} more)"
                    
                    rules_table.add_row(
                        rule['rule_id'],
                        rule['category'].replace('_', ' ').title(),
                        f"{rule['min_coverage']}%",
                        patterns_str
                    )
                
                console.print(rules_table)
            
            if result['skipped_rules'] > 0:
                console.print(f"⚠️  [yellow]Skipped {result['skipped_rules']} rules (no matching category)[/yellow]")
        else:
            console.print(f"❌ [red]Failed to configure rules: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error configuring testing rules: {e}[/red]")


@testing_group.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.', 
              help='Project path (default: current directory)')
@click.pass_context
def rules_status(ctx: click.Context, project_path: str):
    """Show status of configured testing rules."""
    console = Console()
    
    try:
        from agentpm.core.testing.rule_configurator import TestingRuleConfigurator
        from agentpm.core.database.service import DatabaseService
        from agentpm.cli.utils.services import get_database_service
        
        # Get database service
        db = get_database_service(Path(project_path))
        
        # Create configurator
        configurator = TestingRuleConfigurator(db)
        
        # Get project ID
        project_id = 1
        
        # Get configured rules
        rules = configurator.get_configured_rules(project_id)
        
        if rules:
            console.print(f"📊 [cyan]Found {len(rules)} configured testing rules:[/cyan]")
            
            rules_table = Table(title="🧪 Configured Testing Rules")
            rules_table.add_column("Rule ID", style="cyan")
            rules_table.add_column("Category", style="green")
            rules_table.add_column("Coverage", justify="right", style="yellow")
            rules_table.add_column("Enabled", justify="center", style="green")
            rules_table.add_column("Configured For", style="dim")
            
            for rule in rules:
                rules_table.add_row(
                    rule['rule_id'],
                    rule['category'].replace('_', ' ').title(),
                    f"{rule['min_coverage']}%",
                    "✅" if rule['enabled'] else "❌",
                    rule['configured_for']
                )
            
            console.print(rules_table)
        else:
            console.print("⚠️  [yellow]No configured testing rules found[/yellow]")
            console.print("Run 'apm testing configure-rules' to configure rules with project-specific patterns")
            
    except Exception as e:
        console.print(f"❌ [red]Error getting rules status: {e}[/red]")


# Example usage
if __name__ == "__main__":
    testing_group()
