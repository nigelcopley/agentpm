"""
APM (Agent Project Manager) CLI - Main entry point with LazyGroup pattern

Provides fast CLI startup (<100ms) through lazy command loading.
Only imports command modules when they are actually invoked.

Performance:
- Standard import: 400-600ms startup
- Lazy loading: 80-120ms startup (70-85% faster)

Architecture:
- LazyGroup pattern for command registration
- Click context for shared state
- Rich console for professional output
"""

import click
from typing import Optional


class LazyGroup(click.Group):
    """
    Custom click.Group subclass for lazy command registration.

    This subclass provides an efficient mechanism to import and register commands
    only when they are invoked. It delays the importing of command modules until
    they are explicitly called, thereby reducing startup time and memory usage for
    the CLI tooling. It also offers the ability to dynamically list all available
    commands for help and CLI interface display.

    Attributes:
        None
    """

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """
        Import and return command only when invoked.

        Args:
            ctx: Click context
            cmd_name: Command name to load

        Returns:
            Command object if found, None otherwise
        """
        # Command registry: maps command name to module path
        COMMANDS = {
            'init': 'agentpm.cli.commands.init:init',
            'work-item': 'agentpm.cli.commands.work_item:work_item',
            'task': 'agentpm.cli.commands.task:task',
            'idea': 'agentpm.cli.commands.idea:idea',
            'session': 'agentpm.cli.commands.session:session',
            'hooks': 'agentpm.cli.commands.hooks:hooks',
            'context': 'agentpm.cli.commands.context:context',
            'status': 'agentpm.cli.commands.status:status',
            'web': 'agentpm.cli.commands.web:web',
            'testing': 'agentpm.cli.commands.testing:testing_group',
            'agents': 'agentpm.cli.commands.agents:agents',
            'rules': 'agentpm.cli.commands.rules:rules',
            'commands': 'agentpm.cli.commands.commands:commands_group',
            'migrate': 'agentpm.cli.commands.migrate:migrate',
            'migrate-v1-to-v2': 'agentpm.cli.commands.migrate_v1:migrate_v1_to_v2',
            'principles': 'agentpm.cli.commands.principles:principles',
            'document': 'agentpm.cli.commands.document:document',
            'template': 'agentpm.cli.commands.template:template',
            'principle-check': 'agentpm.cli.commands.principle_check:principle_check',
            'summary': 'agentpm.cli.commands.summary:summary',
            'search': 'agentpm.cli.commands.search:search',
            'skills': 'agentpm.cli.commands.skills:skills',
            'claude-code': 'agentpm.cli.commands.claude_code:claude_code',
            'provider': 'agentpm.cli.commands.provider:provider',
            'memory': 'agentpm.cli.commands.memory:memory',
            'detect': 'agentpm.cli.commands.detect:detect',
        }

        if cmd_name not in COMMANDS:
            return None

        # Dynamic import: module_path:attribute
        module_path, attr = COMMANDS[cmd_name].rsplit(':', 1)

        try:
            mod = __import__(module_path, fromlist=[attr])
            return getattr(mod, attr)
        except (ImportError, AttributeError) as e:
            # Graceful failure with helpful error
            ctx.fail(
                f"Command '{cmd_name}' not available: {e}\n"
                f"This may indicate a missing implementation or import error."
            )
            return None

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        Return all available commands for help display.

        Returns:
            List of command names
        """
        return ['init', 'work-item', 'task', 'idea', 'session', 'context', 'status', 'web', 'agents', 'rules', 'testing', 'commands', 'migrate', 'migrate-v1-to-v2', 'document', 'template', 'summary', 'search', 'skills', 'claude-code', 'provider', 'memory', 'detect']


@click.group(
    cls=LazyGroup,
    context_settings={'help_option_names': ['-h', '--help']},
    invoke_without_command=True
)
@click.version_option(version='0.1.0', prog_name='apm')
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output for debugging'
)
@click.pass_context
def main(ctx: click.Context, verbose: bool):
    """
    🤖 APM (Agent Project Manager) - Agent Project Manager

    Persistent context and framework intelligence for AI coding agents.

    \b
    Common Commands:
      init        Initialize new APM project with database and detection
      status      Show project health dashboard with quality metrics
      work-item   Manage work items (features, bugs, research, planning)
      task        Manage tasks with strict time-boxing and quality gates
      context     Access hierarchical project context for AI agents

    \b
    Quick Start:
      apm init "My Project"                              # 1. Initialize
      apm work-item create "Feature Name" --type=feature # 2. Create work item
      apm task create "Task Name" --work-item-id=1 \\
          --type=implementation --effort=3               # 3. Create task
      apm status                                         # 4. View dashboard

    \b
    Quality Gates Enforced:
      • Time-boxing: IMPLEMENTATION ≤4h, TESTING ≤6h, DESIGN ≤8h
      • Required tasks: FEATURE needs DESIGN+IMPL+TEST+DOC
      • State machine: Enforces validated → accepted → in_progress flow
      • Coverage: >90% test coverage required (CI-004)

    \b
    Performance:
      • Help/version: <100ms (lazy loading)
      • Database queries: <1s (indexed)
      • Project init: <5s (with progress bars)

    \b
    Learn More:
      apm COMMAND --help           # Detailed command help
      apm work-item create --help  # See all work item types
      apm task create --help       # See time-boxing limits

    For documentation, see: docs/project-plan/01-specifications/cli/
    """
    from rich.console import Console

    # Initialize shared context object
    ctx.ensure_object(dict)

    # Rich consoles for output (allow test override)
    if 'console' not in ctx.obj:
        ctx.obj['console'] = Console()
    if 'console_err' not in ctx.obj:
        ctx.obj['console_err'] = Console(stderr=True, style="red")
    ctx.obj['verbose'] = verbose

    # Detect project root (lazy - cached in context)
    # Commands can access via ensure_project_root()
    # Allow tests to override project_root
    if 'project_root' not in ctx.obj:
        from agentpm.cli.utils.project import find_project_root
        ctx.obj['project_root'] = find_project_root()

    # Initialize database service at startup (except for init command)
    if 'db_service' not in ctx.obj:
        try:
            # Skip database initialization for init command
            if ctx.invoked_subcommand != 'init':
                from agentpm.core.database.initializer import DatabaseInitializer
                ctx.obj['db_service'] = DatabaseInitializer.initialize()
            else:
                ctx.obj['db_service'] = None
        except Exception as e:
            # Database initialization failed - commands will handle gracefully
            ctx.obj['db_service'] = None
            if verbose:
                ctx.obj['console_err'].print(f"[yellow]Database initialization skipped: {e}[/yellow]")
    
    # Other services initialized on-demand by commands
    if 'workflow_service' not in ctx.obj:
        ctx.obj['workflow_service'] = None
    if 'context_service' not in ctx.obj:
        ctx.obj['context_service'] = None

    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Export for testing
cli = main

def cleanup():
    """Cleanup resources on application shutdown."""
    try:
        from agentpm.core.database.initializer import DatabaseInitializer
        DatabaseInitializer.cleanup()
    except Exception:
        # Ignore cleanup errors during shutdown
        pass

if __name__ == '__main__':
    try:
        main()
    finally:
        cleanup()
