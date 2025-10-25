"""
Claude Code Integration CLI Commands

Provides CLI commands for managing comprehensive Claude Code integration
including plugins, hooks, subagents, settings, slash commands, checkpointing,
and memory tools.
"""

import click
from pathlib import Path
from typing import Optional
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agentpm.core.database.service import DatabaseService
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator
from agentpm.services.claude_integration.settings import SettingsManager, ClaudeCodeSettings


@click.group()
def claude_code():
    """Claude Code integration management commands."""
    pass


@claude_code.command()
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory for Claude Code files')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific integration')
@click.option('--name', '-n', default='APM (Agent Project Manager) Claude Code Integration', help='Integration name')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='json', help='Export format')
@click.pass_context
def generate(ctx, output_dir: str, project_id: Optional[int], name: str, format: str):
    """Generate comprehensive Claude Code integration for APM (Agent Project Manager)."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        output_path = Path(output_dir)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating Claude Code integration...", total=None)
            
            # Initialize orchestrator
            orchestrator = ClaudeCodeOrchestrator(db_service)
            
            # Generate integration
            integration = orchestrator.create_comprehensive_integration(
                output_dir=output_path,
                project_id=project_id,
                integration_name=name
            )
            
            progress.update(task, description="Integration generated successfully!")
        
        # Display results
        console.print(Panel.fit(
            f"[green]✓[/green] Claude Code integration generated successfully!\n\n"
            f"Integration: {integration.name}\n"
            f"Version: {integration.version}\n"
            f"Components: {len(integration.plugins)} plugins, {len(integration.hooks)} hooks, "
            f"{len(integration.subagents)} subagents, {len(integration.settings)} settings, "
            f"{len(integration.slash_commands)} slash commands, {len(integration.checkpoints)} checkpoints, "
            f"{len(integration.memory_tools)} memory tools\n"
            f"Output: {output_path.absolute()}",
            title="Integration Generated",
            border_style="green"
        ))
        
        # Export integration manifest
        if format:
            export_path = output_path / f"integration.{format}"
            if orchestrator.export_integration(integration, export_path, format):
                console.print(f"[blue]Integration manifest exported to: {export_path}[/blue]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating Claude Code integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific integration')
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory')
@click.pass_context
def generate_project(ctx, project_id: int, output_dir: str):
    """Generate Claude Code integration for specific project."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        output_path = Path(output_dir)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating integration for project {project_id}...", total=None)
            
            # Initialize orchestrator
            orchestrator = ClaudeCodeOrchestrator(db_service)
            
            # Generate project integration
            integration = orchestrator.generate_project_integration(
                project_id=project_id,
                output_dir=output_path
            )
            
            progress.update(task, description="Project integration generated successfully!")
        
        # Display results
        console.print(Panel.fit(
            f"[green]✓[/green] Project {project_id} Claude Code integration generated!\n\n"
            f"Integration: {integration.name}\n"
            f"Components: {len(integration.plugins)} plugins, {len(integration.hooks)} hooks, "
            f"{len(integration.subagents)} subagents, {len(integration.settings)} settings, "
            f"{len(integration.slash_commands)} slash commands, {len(integration.checkpoints)} checkpoints, "
            f"{len(integration.memory_tools)} memory tools\n"
            f"Output: {output_path.absolute()}",
            title="Project Integration Generated",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating project integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--agent-role', '-a', required=True, help='Agent role name')
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory')
@click.pass_context
def generate_agent(ctx, agent_role: str, output_dir: str):
    """Generate Claude Code integration for specific agent."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        output_path = Path(output_dir)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating integration for agent {agent_role}...", total=None)
            
            # Initialize orchestrator
            orchestrator = ClaudeCodeOrchestrator(db_service)
            
            # Generate agent integration
            integration = orchestrator.generate_agent_integration(
                agent_role=agent_role,
                output_dir=output_path
            )
            
            progress.update(task, description="Agent integration generated successfully!")
        
        # Display results
        console.print(Panel.fit(
            f"[green]✓[/green] Agent {agent_role} Claude Code integration generated!\n\n"
            f"Integration: {integration.name}\n"
            f"Components: {len(integration.plugins)} plugins, {len(integration.hooks)} hooks, "
            f"{len(integration.subagents)} subagents, {len(integration.settings)} settings, "
            f"{len(integration.slash_commands)} slash commands, {len(integration.checkpoints)} checkpoints, "
            f"{len(integration.memory_tools)} memory tools\n"
            f"Output: {output_path.absolute()}",
            title="Agent Integration Generated",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating agent integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--integration-name', '-n', help='Integration name to validate')
@click.option('--file', '-f', type=click.Path(exists=True), help='Integration file to validate')
@click.pass_context
def validate(ctx, integration_name: Optional[str], file: Optional[str]):
    """Validate Claude Code integration configuration."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        
        if file:
            # Validate from file
            integration = orchestrator.import_integration(Path(file))
            if not integration:
                console.print(f"[red]✗[/red] Failed to import integration from {file}")
                raise click.Abort()
            
            integration_name = integration.name
        
        elif integration_name:
            # Validate from cache
            integration = orchestrator.get_integration(integration_name)
            if not integration:
                console.print(f"[red]✗[/red] Integration '{integration_name}' not found in cache")
                raise click.Abort()
        
        else:
            console.print("[red]✗[/red] Must specify either --integration-name or --file")
            raise click.Abort()
        
        # Validate integration
        validation_results = orchestrator.validate_integration(integration)
        
        # Display validation results
        if validation_results["valid"]:
            console.print(Panel.fit(
                f"[green]✓[/green] Integration '{integration_name}' is valid!\n\n"
                f"Components: {validation_results['component_counts']}\n"
                f"Warnings: {len(validation_results['warnings'])}",
                title="Validation Successful",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                f"[red]✗[/red] Integration '{integration_name}' has validation errors!\n\n"
                f"Errors: {validation_results['errors']}\n"
                f"Warnings: {validation_results['warnings']}",
                title="Validation Failed",
                border_style="red"
            ))
        
        # Show warnings if any
        if validation_results["warnings"]:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in validation_results["warnings"]:
                console.print(f"  • {warning}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error validating integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.pass_context
def list_integrations(ctx):
    """List all cached Claude Code integrations."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        integrations = orchestrator.list_integrations()
        
        if not integrations:
            console.print("[yellow]No integrations found in cache.[/yellow]")
            return
        
        # Create table
        table = Table(title="Claude Code Integrations")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Components", style="blue")
        table.add_column("Created", style="magenta")
        
        for integration_name in integrations:
            integration = orchestrator.get_integration(integration_name)
            if integration:
                component_count = (
                    len(integration.plugins) + len(integration.hooks) + 
                    len(integration.subagents) + len(integration.settings) +
                    len(integration.slash_commands) + len(integration.checkpoints) +
                    len(integration.memory_tools)
                )
                
                created_str = integration.created_at.strftime("%Y-%m-%d %H:%M") if integration.created_at else "Unknown"
                
                table.add_row(
                    integration.name,
                    integration.version,
                    str(component_count),
                    created_str
                )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing integrations: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--integration-name', '-n', required=True, help='Integration name to show')
@click.pass_context
def show(ctx, integration_name: str):
    """Show detailed information about Claude Code integration."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        integration = orchestrator.get_integration(integration_name)
        
        if not integration:
            console.print(f"[red]✗[/red] Integration '{integration_name}' not found")
            raise click.Abort()
        
        # Display integration details
        console.print(Panel.fit(
            f"Name: {integration.name}\n"
            f"Description: {integration.description}\n"
            f"Version: {integration.version}\n"
            f"Created: {integration.created_at.strftime('%Y-%m-%d %H:%M') if integration.created_at else 'Unknown'}\n"
            f"Updated: {integration.updated_at.strftime('%Y-%m-%d %H:%M') if integration.updated_at else 'Unknown'}",
            title="Integration Details",
            border_style="blue"
        ))
        
        # Display component counts
        component_table = Table(title="Component Counts")
        component_table.add_column("Component Type", style="cyan")
        component_table.add_column("Count", style="green")
        
        component_table.add_row("Plugins", str(len(integration.plugins)))
        component_table.add_row("Hooks", str(len(integration.hooks)))
        component_table.add_row("Subagents", str(len(integration.subagents)))
        component_table.add_row("Settings", str(len(integration.settings)))
        component_table.add_row("Slash Commands", str(len(integration.slash_commands)))
        component_table.add_row("Checkpoints", str(len(integration.checkpoints)))
        component_table.add_row("Memory Tools", str(len(integration.memory_tools)))
        
        console.print(component_table)
        
        # Display dependencies
        if integration.dependencies:
            console.print(Panel.fit(
                "\n".join(f"• {dep}" for dep in integration.dependencies),
                title="Dependencies",
                border_style="yellow"
            ))
        
        # Display requirements
        if integration.requirements:
            console.print(Panel.fit(
                "\n".join(f"• {req}" for req in integration.requirements),
                title="Requirements",
                border_style="yellow"
            ))
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error showing integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--integration-name', '-n', required=True, help='Integration name to export')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='json', help='Export format')
@click.pass_context
def export(ctx, integration_name: str, output_file: Optional[str], format: str):
    """Export Claude Code integration to file."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        integration = orchestrator.get_integration(integration_name)
        
        if not integration:
            console.print(f"[red]✗[/red] Integration '{integration_name}' not found")
            raise click.Abort()
        
        # Determine output file
        if not output_file:
            output_file = f"{integration_name.lower().replace(' ', '_')}.{format}"
        
        output_path = Path(output_file)
        
        # Export integration
        if orchestrator.export_integration(integration, output_path, format):
            console.print(f"[green]✓[/green] Integration exported to: {output_path.absolute()}")
        else:
            console.print(f"[red]✗[/red] Failed to export integration")
            raise click.Abort()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error exporting integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True, help='Input file path')
@click.pass_context
def import_integration(ctx, input_file: str):
    """Import Claude Code integration from file."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        input_path = Path(input_file)
        
        # Import integration
        integration = orchestrator.import_integration(input_path)
        
        if integration:
            console.print(f"[green]✓[/green] Integration '{integration.name}' imported successfully!")
            
            # Validate imported integration
            validation_results = orchestrator.validate_integration(integration)
            if not validation_results["valid"]:
                console.print(f"[yellow]⚠[/yellow] Imported integration has validation issues:")
                for error in validation_results["errors"]:
                    console.print(f"  • {error}")
        else:
            console.print(f"[red]✗[/red] Failed to import integration from {input_file}")
            raise click.Abort()
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error importing integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.pass_context
def stats(ctx):
    """Show Claude Code integration statistics."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']
    
    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        stats = orchestrator.get_integration_stats()
        
        # Display statistics
        console.print(Panel.fit(
            f"Total Integrations: {stats.get('total_integrations', 0)}\n"
            f"Total Components: {stats.get('total_components', 0)}\n"
            f"Cache Size: {stats.get('cache_size', 0)}",
            title="Integration Statistics",
            border_style="blue"
        ))
        
        # Display component breakdown
        if stats.get('component_breakdown'):
            breakdown_table = Table(title="Component Breakdown by Integration")
            breakdown_table.add_column("Integration", style="cyan")
            breakdown_table.add_column("Plugins", style="green")
            breakdown_table.add_column("Hooks", style="blue")
            breakdown_table.add_column("Subagents", style="magenta")
            breakdown_table.add_column("Settings", style="yellow")
            breakdown_table.add_column("Slash Commands", style="red")
            breakdown_table.add_column("Checkpoints", style="white")
            breakdown_table.add_column("Memory Tools", style="bright_white")
            
            for integration_name, breakdown in stats['component_breakdown'].items():
                breakdown_table.add_row(
                    integration_name,
                    str(breakdown.get('plugins', 0)),
                    str(breakdown.get('hooks', 0)),
                    str(breakdown.get('subagents', 0)),
                    str(breakdown.get('settings', 0)),
                    str(breakdown.get('slash_commands', 0)),
                    str(breakdown.get('checkpoints', 0)),
                    str(breakdown.get('memory_tools', 0))
                )
            
            console.print(breakdown_table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error getting integration stats: {e}")
        raise click.Abort()


@claude_code.command()
@click.confirmation_option(prompt='Are you sure you want to clear the integration cache?')
@click.pass_context
def clear_cache(ctx):
    """Clear Claude Code integration cache."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        orchestrator = ClaudeCodeOrchestrator(db_service)
        cleaned_count = orchestrator.cleanup_integration_cache()

        console.print(f"[green]✓[/green] Integration cache cleared. Removed {cleaned_count} integrations.")

    except Exception as e:
        console.print(f"[red]✗[/red] Error clearing integration cache: {e}")
        raise click.Abort()


# ============================================================================
# Settings Management Commands
# ============================================================================

@claude_code.group()
def settings():
    """Manage Claude Code settings."""
    pass


@settings.command(name='show')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']), default='text', help='Output format')
@click.pass_context
def settings_show(ctx, project_id: Optional[int], format: str):
    """Show current Claude Code settings."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)
        current_settings = manager.load_settings(project_id=project_id)

        if format == 'json':
            console.print_json(data=current_settings.model_dump())
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(current_settings.model_dump(), default_flow_style=False))
        else:
            # Text format - display in panels
            console.print(Panel.fit(
                f"Plugin Enabled: {current_settings.plugin_enabled}\n"
                f"Verbose Logging: {current_settings.verbose_logging}\n"
                f"Project ID: {current_settings.project_id or 'None'}",
                title="Core Settings",
                border_style="blue"
            ))

            # Hooks settings
            enabled_hooks = [k for k, v in current_settings.hooks.enabled.items() if v]
            console.print(Panel.fit(
                f"Enabled Hooks: {', '.join(enabled_hooks) if enabled_hooks else 'None'}\n"
                f"Timeout: {current_settings.hooks.timeout_seconds}s\n"
                f"Retry on Failure: {current_settings.hooks.retry_on_failure}\n"
                f"Max Retries: {current_settings.hooks.max_retries}",
                title="Hooks Settings",
                border_style="green"
            ))

            # Memory settings
            console.print(Panel.fit(
                f"Auto Load: {current_settings.memory.auto_load_memory}\n"
                f"Auto Generate: {current_settings.memory.auto_generate_memory}\n"
                f"Generation Frequency: {current_settings.memory.generation_frequency.value}\n"
                f"Retention: {current_settings.memory.retention_days} days\n"
                f"Max File Size: {current_settings.memory.max_file_size_kb} KB\n"
                f"Cache Duration: {current_settings.memory.cache_duration_minutes} min",
                title="Memory Settings",
                border_style="yellow"
            ))

            # Subagent settings
            console.print(Panel.fit(
                f"Enabled: {current_settings.subagents.enabled}\n"
                f"Max Parallel: {current_settings.subagents.max_parallel}\n"
                f"Timeout: {current_settings.subagents.timeout_seconds}s\n"
                f"Auto Cleanup: {current_settings.subagents.auto_cleanup}\n"
                f"Max Depth: {current_settings.subagents.max_depth}",
                title="Subagent Settings",
                border_style="magenta"
            ))

            # Performance settings
            console.print(Panel.fit(
                f"Caching: {current_settings.performance.enable_caching}\n"
                f"Cache TTL: {current_settings.performance.cache_ttl_seconds}s\n"
                f"Max Concurrent Requests: {current_settings.performance.max_concurrent_requests}\n"
                f"Request Timeout: {current_settings.performance.request_timeout_seconds}s\n"
                f"Metrics: {current_settings.performance.enable_metrics}\n"
                f"Metrics Interval: {current_settings.performance.metrics_interval_seconds}s",
                title="Performance Settings",
                border_style="cyan"
            ))

    except Exception as e:
        console.print(f"[red]✗[/red] Error showing settings: {e}")
        raise click.Abort()


@settings.command(name='set')
@click.option('--key', '-k', required=True, help='Setting key (dotted path, e.g., hooks.enabled.session_start)')
@click.option('--value', '-v', required=True, help='Setting value')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.option('--scope', '-s', type=click.Choice(['session', 'user', 'project']), default='session', help='Setting scope')
@click.option('--type', '-t', type=click.Choice(['bool', 'int', 'float', 'str']), default='str', help='Value type')
@click.pass_context
def settings_set(ctx, key: str, value: str, project_id: Optional[int], scope: str, type: str):
    """Set a specific Claude Code setting."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)

        # Convert value to appropriate type
        if type == 'bool':
            typed_value = value.lower() in ('true', '1', 'yes', 'on')
        elif type == 'int':
            typed_value = int(value)
        elif type == 'float':
            typed_value = float(value)
        else:
            typed_value = value

        # Set the setting
        success = manager.set_setting(
            key=key,
            value=typed_value,
            project_id=project_id,
            scope=scope
        )

        if success:
            console.print(f"[green]✓[/green] Setting '{key}' set to '{typed_value}' (scope: {scope})")

            # Show warnings if any
            current_settings = manager.load_settings(project_id=project_id, use_cache=False)
            warnings = manager.validate_settings(current_settings)
            if warnings:
                console.print("\n[yellow]⚠ Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")
        else:
            console.print(f"[red]✗[/red] Failed to set setting '{key}'")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]✗[/red] Error setting value: {e}")
        raise click.Abort()


@settings.command(name='reset')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.option('--scope', '-s', type=click.Choice(['session', 'user', 'project']), default='session', help='Scope to reset')
@click.confirmation_option(prompt='Are you sure you want to reset settings?')
@click.pass_context
def settings_reset(ctx, project_id: Optional[int], scope: str):
    """Reset Claude Code settings to defaults."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)
        success = manager.reset_settings(project_id=project_id, scope=scope)

        if success:
            console.print(f"[green]✓[/green] Settings reset to defaults (scope: {scope})")
        else:
            console.print(f"[red]✗[/red] Failed to reset settings")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]✗[/red] Error resetting settings: {e}")
        raise click.Abort()


@settings.command(name='validate')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.pass_context
def settings_validate(ctx, project_id: Optional[int]):
    """Validate current Claude Code settings."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)
        current_settings = manager.load_settings(project_id=project_id)
        warnings = manager.validate_settings(current_settings)

        if not warnings:
            console.print(Panel.fit(
                "[green]✓[/green] All settings are valid!\n\n"
                "No warnings detected.",
                title="Validation Successful",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                f"[yellow]⚠[/yellow] Settings are valid but have {len(warnings)} warning(s):\n\n" +
                "\n".join(f"• {w}" for w in warnings),
                title="Validation Warnings",
                border_style="yellow"
            ))

    except Exception as e:
        console.print(f"[red]✗[/red] Error validating settings: {e}")
        raise click.Abort()


@settings.command(name='export')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.option('--output-file', '-o', type=click.Path(), required=True, help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='json', help='Export format')
@click.pass_context
def settings_export(ctx, project_id: Optional[int], output_file: str, format: str):
    """Export Claude Code settings to file."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)
        current_settings = manager.load_settings(project_id=project_id)

        output_path = Path(output_file)

        with open(output_path, 'w') as f:
            if format == 'json':
                json.dump(current_settings.model_dump(), f, indent=2)
            else:  # yaml
                import yaml
                yaml.dump(current_settings.model_dump(), f, default_flow_style=False)

        console.print(f"[green]✓[/green] Settings exported to: {output_path.absolute()}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error exporting settings: {e}")
        raise click.Abort()


@settings.command(name='import')
@click.option('--project-id', '-p', type=int, help='Project ID for project-specific settings')
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True, help='Input file path')
@click.option('--scope', '-s', type=click.Choice(['session', 'user', 'project']), default='session', help='Import scope')
@click.pass_context
def settings_import(ctx, project_id: Optional[int], input_file: str, scope: str):
    """Import Claude Code settings from file."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        manager = SettingsManager(db_service)
        input_path = Path(input_file)

        with open(input_path, 'r') as f:
            if input_path.suffix == '.json':
                settings_data = json.load(f)
            else:  # yaml
                import yaml
                settings_data = yaml.safe_load(f)

        # Create settings object
        imported_settings = ClaudeCodeSettings(**settings_data)

        # Validate before importing
        warnings = manager.validate_settings(imported_settings)
        if warnings:
            console.print("[yellow]⚠ Warnings detected in imported settings:[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")

            if not click.confirm("Continue with import?"):
                console.print("[yellow]Import cancelled[/yellow]")
                return

        # Save settings
        success = manager.save_settings(
            project_id=project_id,
            settings=imported_settings,
            scope=scope
        )

        if success:
            console.print(f"[green]✓[/green] Settings imported from: {input_path.absolute()} (scope: {scope})")
        else:
            console.print(f"[red]✗[/red] Failed to import settings")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]✗[/red] Error importing settings: {e}")
        raise click.Abort()


# ============================================================================
# User-Facing Integration Management Commands
# ============================================================================

@claude_code.command()
@click.option('--force', is_flag=True, help='Force reinitialization if already initialized')
@click.pass_context
def init(ctx, force: bool):
    """Initialize Claude Code integration for current project."""
    console = ctx.obj.get('console')
    if not console:
        from rich.console import Console
        console = Console()

    try:
        project_root = ctx.obj.get('project_root') or Path.cwd()
        claude_dir = project_root / ".claude"

        # Check if already initialized
        if claude_dir.exists() and not force:
            console.print(f"[yellow]⚠[/yellow] Claude Code integration already initialized at {claude_dir}")
            console.print("Use --force to reinitialize")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing Claude Code integration...", total=None)

            # Create .claude/ directory structure
            claude_dir.mkdir(parents=True, exist_ok=True)
            (claude_dir / "plugins").mkdir(exist_ok=True)
            (claude_dir / "memory").mkdir(exist_ok=True)
            (claude_dir / "checkpoints").mkdir(exist_ok=True)
            (claude_dir / "settings").mkdir(exist_ok=True)

            progress.update(task, description="Creating directory structure...")

            # Create initial memory files
            memory_dir = claude_dir / "memory"
            (memory_dir / "project_context.md").write_text("# Project Context\n\nAPM (Agent Project Manager) Project\n")
            (memory_dir / "recent_work.md").write_text("# Recent Work\n\nNo work items yet.\n")

            progress.update(task, description="Generating memory files...")

            # Create default settings
            settings_file = claude_dir / "settings" / "integration.json"
            default_settings = {
                "plugin_enabled": True,
                "verbose_logging": False,
                "hooks": {
                    "enabled": {
                        "session_start": True,
                        "session_end": True,
                        "prompt_submit": True
                    }
                },
                "memory": {
                    "auto_load_memory": True,
                    "auto_generate_memory": True,
                    "generation_frequency": "on_change"
                }
            }
            settings_file.write_text(json.dumps(default_settings, indent=2))

            progress.update(task, description="Creating default settings...")

            # Create README
            readme = claude_dir / "README.md"
            readme.write_text(
                "# Claude Code Integration\n\n"
                "APM (Agent Project Manager) Claude Code integration initialized.\n\n"
                "## Directory Structure\n\n"
                "- `plugins/` - Claude Code plugins\n"
                "- `memory/` - Memory files for context\n"
                "- `checkpoints/` - Session checkpoints\n"
                "- `settings/` - Integration settings\n\n"
                "## Next Steps\n\n"
                "1. Review settings: `apm claude-code status`\n"
                "2. Sync context: `apm claude-code sync`\n"
                "3. Create checkpoint: `apm claude-code checkpoint create`\n"
            )

            progress.update(task, description="Initialization complete!")

        # Display results
        console.print(Panel.fit(
            f"[green]✓[/green] Claude Code integration initialized!\n\n"
            f"Location: {claude_dir.absolute()}\n\n"
            f"Next steps:\n"
            f"  1. Review settings: [cyan]apm claude-code status[/cyan]\n"
            f"  2. Sync context: [cyan]apm claude-code sync[/cyan]\n"
            f"  3. Create checkpoint: [cyan]apm claude-code checkpoint create --name initial[/cyan]",
            title="Initialization Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing Claude Code integration: {e}")
        raise click.Abort()


@claude_code.command()
@click.pass_context
def status(ctx):
    """Show Claude Code integration status."""
    console = ctx.obj.get('console')
    if not console:
        from rich.console import Console
        console = Console()

    try:
        project_root = ctx.obj.get('project_root') or Path.cwd()
        claude_dir = project_root / ".claude"

        if not claude_dir.exists():
            console.print("[yellow]⚠[/yellow] Claude Code integration not initialized")
            console.print("Run: [cyan]apm claude-code init[/cyan]")
            return

        # Check components
        has_plugins = (claude_dir / "plugins").exists()
        has_memory = (claude_dir / "memory").exists()
        has_checkpoints = (claude_dir / "checkpoints").exists()
        has_settings = (claude_dir / "settings").exists()

        # Count files
        memory_files = list((claude_dir / "memory").glob("*.md")) if has_memory else []
        checkpoint_files = list((claude_dir / "checkpoints").glob("*.json")) if has_checkpoints else []

        # Load settings if available
        settings_file = claude_dir / "settings" / "integration.json"
        settings_data = None
        if settings_file.exists():
            settings_data = json.loads(settings_file.read_text())

        # Display status
        console.print(Panel.fit(
            f"Location: {claude_dir.absolute()}\n"
            f"Status: [green]Initialized[/green]",
            title="Claude Code Integration Status",
            border_style="blue"
        ))
        console.print()

        # Component status table
        component_table = Table(title="Components")
        component_table.add_column("Component", style="cyan")
        component_table.add_column("Status", style="green")
        component_table.add_column("Details", style="yellow")

        component_table.add_row(
            "Plugins",
            "✓" if has_plugins else "✗",
            f"{len(list((claude_dir / 'plugins').glob('*.json')))} plugins" if has_plugins else "Not configured"
        )
        component_table.add_row(
            "Memory",
            "✓" if has_memory else "✗",
            f"{len(memory_files)} files" if has_memory else "Not configured"
        )
        component_table.add_row(
            "Checkpoints",
            "✓" if has_checkpoints else "✗",
            f"{len(checkpoint_files)} checkpoints" if has_checkpoints else "Not configured"
        )
        component_table.add_row(
            "Settings",
            "✓" if has_settings else "✗",
            "Configured" if settings_file.exists() else "Using defaults"
        )

        console.print(component_table)
        console.print()

        # Active hooks (if settings loaded)
        if settings_data and "hooks" in settings_data:
            enabled_hooks = [
                hook for hook, enabled in settings_data["hooks"].get("enabled", {}).items()
                if enabled
            ]

            if enabled_hooks:
                hooks_panel = Panel.fit(
                    "\n".join(f"• {hook}" for hook in enabled_hooks),
                    title="Active Hooks",
                    border_style="green"
                )
                console.print(hooks_panel)
                console.print()

        # Recent checkpoints
        if checkpoint_files:
            checkpoint_table = Table(title="Recent Checkpoints")
            checkpoint_table.add_column("Name", style="cyan")
            checkpoint_table.add_column("Created", style="yellow")

            # Sort by modification time, show last 5
            sorted_checkpoints = sorted(
                checkpoint_files,
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:5]

            for cp_file in sorted_checkpoints:
                cp_data = json.loads(cp_file.read_text())
                checkpoint_table.add_row(
                    cp_data.get("name", cp_file.stem),
                    cp_data.get("timestamp", "Unknown")
                )

            console.print(checkpoint_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Error showing status: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--force', is_flag=True, help='Force regeneration of all memory files')
@click.pass_context
def sync(ctx, force: bool):
    """Sync AIPM state to Claude Code memory files."""
    console = ctx.obj.get('console')
    if not console:
        from rich.console import Console
        console = Console()
    db_service = ctx.obj.get('db_service')

    try:
        project_root = ctx.obj.get('project_root') or Path.cwd()
        claude_dir = project_root / ".claude"

        if not claude_dir.exists():
            console.print("[yellow]⚠[/yellow] Claude Code integration not initialized")
            console.print("Run: [cyan]apm claude-code init[/cyan]")
            return

        memory_dir = claude_dir / "memory"
        memory_dir.mkdir(exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Syncing AIPM state to memory files...", total=None)

            # Generate memory files from database
            if db_service:
                from agentpm.core.database.methods import work_items as wi_methods
                from agentpm.core.database.methods import tasks as task_methods
                from agentpm.cli.utils.project import get_current_project_id

                project_id = get_current_project_id(ctx)

                # Get active work items
                work_items = wi_methods.list_work_items(db_service, project_id=project_id, status_filter=["active", "in_progress"])

                progress.update(task, description="Generating project context...")

                # Generate project_context.md
                context_content = "# Project Context\n\n"
                context_content += f"## Active Work Items ({len(work_items)})\n\n"
                for wi in work_items[:10]:  # Limit to 10 most recent
                    context_content += f"### WI-{wi.id}: {wi.name}\n"
                    context_content += f"- Type: {wi.type.value}\n"
                    context_content += f"- Status: {wi.status.value}\n"
                    context_content += f"- Phase: {wi.phase.value}\n"
                    if wi.business_context:
                        context_content += f"- Context: {wi.business_context[:200]}...\n"
                    context_content += "\n"

                (memory_dir / "project_context.md").write_text(context_content)

                progress.update(task, description="Generating recent work...")

                # Generate recent_work.md
                recent_content = "# Recent Work\n\n"
                all_tasks = []
                for wi in work_items:
                    all_tasks.extend(task_methods.list_tasks(db_service, work_item_id=wi.id))

                recent_tasks = sorted(all_tasks, key=lambda t: t.updated_at or t.created_at, reverse=True)[:20]
                recent_content += f"## Recent Tasks ({len(recent_tasks)})\n\n"
                for task in recent_tasks:
                    recent_content += f"- **Task #{task.id}**: {task.name} ({task.status.value})\n"

                (memory_dir / "recent_work.md").write_text(recent_content)
            else:
                # No database - just update timestamps
                for md_file in memory_dir.glob("*.md"):
                    md_file.touch()

            progress.update(task, description="Sync complete!")

        console.print(Panel.fit(
            f"[green]✓[/green] Memory files synchronized!\n\n"
            f"Location: {memory_dir.absolute()}\n"
            f"Files updated: {len(list(memory_dir.glob('*.md')))}",
            title="Sync Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗[/red] Error syncing memory files: {e}")
        raise click.Abort()


@claude_code.command()
@click.option('--enable', multiple=True, help='Hooks to enable')
@click.option('--disable', multiple=True, help='Hooks to disable')
@click.pass_context
def hooks(ctx, enable: tuple, disable: tuple):
    """Enable/disable Claude Code hooks."""
    console = ctx.obj.get('console')
    if not console:
        from rich.console import Console
        console = Console()

    try:
        project_root = ctx.obj.get('project_root') or Path.cwd()
        settings_file = project_root / ".claude" / "settings" / "integration.json"

        if not settings_file.exists():
            console.print("[yellow]⚠[/yellow] Settings file not found")
            console.print("Run: [cyan]apm claude-code init[/cyan]")
            return

        # Load current settings
        settings = json.loads(settings_file.read_text())

        if "hooks" not in settings:
            settings["hooks"] = {"enabled": {}}
        if "enabled" not in settings["hooks"]:
            settings["hooks"]["enabled"] = {}

        # Update hooks
        changes = []
        for hook in enable:
            settings["hooks"]["enabled"][hook] = True
            changes.append(f"[green]✓[/green] Enabled: {hook}")

        for hook in disable:
            settings["hooks"]["enabled"][hook] = False
            changes.append(f"[red]✗[/red] Disabled: {hook}")

        # Save settings
        settings_file.write_text(json.dumps(settings, indent=2))

        # Display results
        if changes:
            console.print(Panel.fit(
                "\n".join(changes),
                title="Hook Configuration Updated",
                border_style="blue"
            ))

        # Display current hook status
        console.print()
        hook_table = Table(title="Current Hook Status")
        hook_table.add_column("Hook", style="cyan")
        hook_table.add_column("Status", style="green")

        for hook, enabled in sorted(settings["hooks"]["enabled"].items()):
            hook_table.add_row(
                hook,
                "[green]Enabled[/green]" if enabled else "[dim]Disabled[/dim]"
            )

        console.print(hook_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Error managing hooks: {e}")
        raise click.Abort()


@claude_code.command()
@click.argument('action', type=click.Choice(['create', 'restore', 'list', 'delete']))
@click.option('--name', help='Checkpoint name')
@click.pass_context
def checkpoint(ctx, action: str, name: Optional[str]):
    """Manage session checkpoints."""
    console = ctx.obj.get('console')
    if not console:
        from rich.console import Console
        console = Console()

    try:
        project_root = ctx.obj.get('project_root') or Path.cwd()
        checkpoints_dir = project_root / ".claude" / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        if action == 'create':
            if not name:
                console.print("[red]✗[/red] Checkpoint name required for create action")
                console.print("Usage: [cyan]apm claude-code checkpoint create --name <name>[/cyan]")
                raise click.Abort()

            # Create checkpoint
            checkpoint_data = {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "project_root": str(project_root),
                "type": "manual"
            }

            checkpoint_file = checkpoints_dir / f"{name}.json"
            checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2))

            console.print(f"[green]✓[/green] Checkpoint '{name}' created at {checkpoint_file}")

        elif action == 'list':
            checkpoint_files = list(checkpoints_dir.glob("*.json"))

            if not checkpoint_files:
                console.print("[yellow]No checkpoints found[/yellow]")
                return

            table = Table(title="Session Checkpoints")
            table.add_column("Name", style="cyan")
            table.add_column("Created", style="yellow")
            table.add_column("Type", style="blue")

            for cp_file in sorted(checkpoint_files, key=lambda p: p.stat().st_mtime, reverse=True):
                cp_data = json.loads(cp_file.read_text())
                table.add_row(
                    cp_data.get("name", cp_file.stem),
                    cp_data.get("timestamp", "Unknown"),
                    cp_data.get("type", "manual")
                )

            console.print(table)

        elif action == 'restore':
            if not name:
                console.print("[red]✗[/red] Checkpoint name required for restore action")
                raise click.Abort()

            checkpoint_file = checkpoints_dir / f"{name}.json"
            if not checkpoint_file.exists():
                console.print(f"[red]✗[/red] Checkpoint '{name}' not found")
                raise click.Abort()

            cp_data = json.loads(checkpoint_file.read_text())
            console.print(Panel.fit(
                f"Name: {cp_data.get('name')}\n"
                f"Created: {cp_data.get('timestamp')}\n"
                f"Type: {cp_data.get('type')}\n\n"
                f"[yellow]Note: Restore functionality not yet implemented[/yellow]",
                title="Checkpoint Details",
                border_style="blue"
            ))

        elif action == 'delete':
            if not name:
                console.print("[red]✗[/red] Checkpoint name required for delete action")
                raise click.Abort()

            checkpoint_file = checkpoints_dir / f"{name}.json"
            if not checkpoint_file.exists():
                console.print(f"[red]✗[/red] Checkpoint '{name}' not found")
                raise click.Abort()

            checkpoint_file.unlink()
            console.print(f"[green]✓[/green] Checkpoint '{name}' deleted")

    except Exception as e:
        console.print(f"[red]✗[/red] Error managing checkpoint: {e}")
        raise click.Abort()
