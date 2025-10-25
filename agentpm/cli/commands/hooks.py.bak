"""
Hooks management commands.

Install and manage Claude Code integration hooks.
"""

import click
import shutil
from pathlib import Path
from typing import List, Optional

from agentpm.core.hooks import (
    HOOKS_METADATA,
    PHASE_1_HOOKS,
    PHASE_2_HOOKS,
    PHASE_3_HOOKS,
    ALL_HOOKS
)


@click.group()
def hooks():
    """Manage Claude Code integration hooks.

    Install hooks to .claude/hooks/ for automatic activation.
    Hooks provide session continuity, context injection, and workflow guidance.

    Phases:
      Phase 1 (MVP): session-start, session-end, user-prompt-submit
      Phase 2: pre-tool-use, post-tool-use, pre-compact
      Phase 3: stop, subagent-stop

    Examples:
      apm hooks install                  # Install Phase 1 hooks (recommended)
      apm hooks install --phase 2        # Install Phase 1 + 2 hooks
      apm hooks install --all            # Install all hooks
      apm hooks list                     # Show available hooks
      apm hooks status                   # Show installed hooks
    """
    pass


@hooks.command()
@click.option('--phase', type=int, help='Install hooks up to this phase (1, 2, or 3)')
@click.option('--all', 'install_all', is_flag=True, help='Install all hooks (Phase 1+2+3)')
@click.option('--hooks', help='Comma-separated list of specific hooks to install')
@click.option('--force', is_flag=True, help='Overwrite existing hooks')
def install(phase: Optional[int], install_all: bool, hooks: Optional[str], force: bool):
    """Install Claude Code hooks to .claude/hooks/ directory.

    By default, installs Phase 1 hooks (SessionStart, SessionEnd, UserPromptSubmit).
    These provide 80% of value with minimal risk.

    Examples:
      apm hooks install                           # Phase 1 only (default)
      apm hooks install --phase 2                 # Phase 1 + 2
      apm hooks install --all                     # All phases
      apm hooks install --hooks session-start     # Specific hook only
    """
    # Determine which hooks to install
    hooks_to_install = []

    if hooks:
        # Specific hooks requested
        hooks_to_install = [h.strip() for h in hooks.split(',')]
        invalid = [h for h in hooks_to_install if h not in ALL_HOOKS]
        if invalid:
            click.echo(f"❌ Invalid hook names: {', '.join(invalid)}", err=True)
            click.echo(f"Available hooks: {', '.join(ALL_HOOKS)}")
            raise click.Abort()
    elif install_all:
        # All hooks
        hooks_to_install = ALL_HOOKS
        click.echo("📦 Installing all hooks (Phase 1 + 2 + 3)...")
    elif phase:
        # Phase-based installation
        if phase == 1:
            hooks_to_install = PHASE_1_HOOKS
            click.echo("📦 Installing Phase 1 hooks (MVP)...")
        elif phase == 2:
            hooks_to_install = PHASE_1_HOOKS + PHASE_2_HOOKS
            click.echo("📦 Installing Phase 1 + 2 hooks...")
        elif phase == 3:
            hooks_to_install = ALL_HOOKS
            click.echo("📦 Installing all hooks (Phase 1 + 2 + 3)...")
        else:
            click.echo(f"❌ Invalid phase: {phase}. Must be 1, 2, or 3.", err=True)
            raise click.Abort()
    else:
        # Default: Phase 1 only
        hooks_to_install = PHASE_1_HOOKS
        click.echo("📦 Installing Phase 1 hooks (default)...")

    # Get paths
    project_root = Path.cwd()
    claude_hooks_dir = project_root / ".claude" / "hooks"
    source_hooks_dir = project_root / "agentpm" / "core" / "hooks" / "implementations"

    # Verify source directory exists
    if not source_hooks_dir.exists():
        click.echo(f"❌ Source hooks directory not found: {source_hooks_dir}", err=True)
        click.echo("Are you in the aipm-v2 project root?")
        raise click.Abort()

    # Create .claude/hooks/ if it doesn't exist
    claude_hooks_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"📁 Target directory: {claude_hooks_dir}")

    # Install hooks
    installed = []
    skipped = []

    for hook_name in hooks_to_install:
        metadata = HOOKS_METADATA[hook_name]
        source_file = source_hooks_dir / metadata["file"]
        target_file = claude_hooks_dir / metadata["file"]

        # Check if source exists
        if not source_file.exists():
            click.echo(f"⚠️  Source not found: {hook_name} ({source_file})", err=True)
            continue

        # Check if target already exists
        if target_file.exists() and not force:
            click.echo(f"⏭️  Skipping {hook_name} (already exists, use --force to overwrite)")
            skipped.append(hook_name)
            continue

        # Copy hook
        shutil.copy2(source_file, target_file)

        # Ensure executable
        target_file.chmod(0o755)

        click.echo(f"✅ Installed: {hook_name} ({metadata['description']})")
        installed.append(hook_name)

    # Summary
    click.echo("")
    click.echo(f"📊 Installation Summary:")
    click.echo(f"   ✅ Installed: {len(installed)} hooks")
    if skipped:
        click.echo(f"   ⏭️  Skipped: {len(skipped)} hooks (already exist)")

    if installed:
        click.echo("")
        click.echo("🎉 Hooks installed successfully!")
        click.echo("")
        click.echo("📚 Next steps:")
        click.echo("   1. Restart Claude Code to activate hooks")
        click.echo("   2. Start a new session to test SessionStart hook")
        click.echo("   3. Check .claude/hooks/ directory to verify installation")
        click.echo("")
        click.echo("💡 Verification:")
        click.echo("   echo '{}' | .claude/hooks/session-start.py")


@hooks.command()
def list():
    """List all available hooks with metadata."""
    click.echo("📋 Available AIPM Hooks:\n")

    for phase_num, phase_hooks in enumerate([PHASE_1_HOOKS, PHASE_2_HOOKS, PHASE_3_HOOKS], 1):
        phase_name = ["Essential (MVP)", "Enhancement", "Future"][phase_num - 1]
        click.echo(f"Phase {phase_num}: {phase_name}")
        click.echo("─" * 70)

        for hook_name in phase_hooks:
            metadata = HOOKS_METADATA[hook_name]
            click.echo(f"  {hook_name:<20} {metadata['priority']:<8} ~{metadata['performance_ms']}ms")
            click.echo(f"    {metadata['description']}")
            click.echo("")

    click.echo("📚 Installation:")
    click.echo(f"   apm hooks install              # Phase 1 only (recommended)")
    click.echo(f"   apm hooks install --phase 2    # Phase 1 + 2")
    click.echo(f"   apm hooks install --all        # All phases")


@hooks.command()
def status():
    """Show installation status of hooks."""
    project_root = Path.cwd()
    claude_hooks_dir = project_root / ".claude" / "hooks"

    if not claude_hooks_dir.exists():
        click.echo("❌ .claude/hooks/ directory not found")
        click.echo("   Run: apm hooks install")
        return

    click.echo("📊 Hook Installation Status:\n")

    for phase_num, phase_hooks in enumerate([PHASE_1_HOOKS, PHASE_2_HOOKS, PHASE_3_HOOKS], 1):
        phase_name = ["Essential (MVP)", "Enhancement", "Future"][phase_num - 1]
        click.echo(f"Phase {phase_num}: {phase_name}")

        for hook_name in phase_hooks:
            metadata = HOOKS_METADATA[hook_name]
            hook_file = claude_hooks_dir / metadata["file"]

            if hook_file.exists():
                # Check if executable
                is_executable = hook_file.stat().st_mode & 0o111
                status_icon = "✅" if is_executable else "⚠️ "
                status_text = "installed" if is_executable else "installed (not executable)"
            else:
                status_icon = "❌"
                status_text = "not installed"

            click.echo(f"  {status_icon} {hook_name:<20} {status_text}")

        click.echo("")

    # Count installed
    installed_count = sum(
        1 for hook in ALL_HOOKS
        if (claude_hooks_dir / HOOKS_METADATA[hook]["file"]).exists()
    )

    click.echo(f"Summary: {installed_count}/{len(ALL_HOOKS)} hooks installed")

    if installed_count == 0:
        click.echo("\n💡 Install hooks with: apm hooks install")
    elif installed_count < len(PHASE_1_HOOKS):
        click.echo("\n💡 Complete Phase 1 with: apm hooks install")


@hooks.command()
@click.option('--hook', required=True, help='Hook name to test (e.g., session-start)')
def test(hook: str):
    """Test a hook by running it manually.

    Examples:
      apm hooks test --hook session-start
      apm hooks test --hook user-prompt-submit
    """
    if hook not in ALL_HOOKS:
        click.echo(f"❌ Invalid hook name: {hook}", err=True)
        click.echo(f"Available hooks: {', '.join(ALL_HOOKS)}")
        raise click.Abort()

    project_root = Path.cwd()
    hook_file = project_root / ".claude" / "hooks" / HOOKS_METADATA[hook]["file"]

    if not hook_file.exists():
        click.echo(f"❌ Hook not installed: {hook}", err=True)
        click.echo(f"   Run: apm hooks install --hooks {hook}")
        raise click.Abort()

    click.echo(f"🧪 Testing hook: {hook}")
    click.echo(f"   File: {hook_file}")
    click.echo("")

    # Test with empty JSON input
    import subprocess
    result = subprocess.run(
        [str(hook_file)],
        input='{"session_id": "test-123"}\n',
        capture_output=True,
        text=True
    )

    click.echo("─" * 70)
    click.echo("📤 Output (injected into Claude's context):")
    click.echo("─" * 70)
    if result.stdout:
        click.echo(result.stdout)
    else:
        click.echo("(no output)")

    if result.stderr:
        click.echo("")
        click.echo("─" * 70)
        click.echo("📋 Logs (stderr, not shown to Claude):")
        click.echo("─" * 70)
        click.echo(result.stderr)

    click.echo("")
    if result.returncode == 0:
        click.echo("✅ Hook executed successfully")
    else:
        click.echo(f"❌ Hook failed with exit code {result.returncode}")
