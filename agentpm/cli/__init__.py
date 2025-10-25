"""
APM (Agent Project Manager) CLI - Command-line interface for Agent Project Manager

Provides professional-grade CLI for AI coding agents and developers to interact
with the quality-gated project management system.

Architecture:
- Lazy-loaded commands for fast startup (<100ms)
- Rich formatting for professional UX
- Quality gates enforced at CLI level
- Service factory pattern for efficient resource use

Usage:
    apm --help          # Show all commands
    apm init "Project"  # Initialize project
    apm status          # Show project dashboard
    apm task create "Task name" --work-item-id=1 --type=implementation --effort=3
"""

__version__ = "0.1.0"
__author__ = "AIPM Team"

from agentpm.cli.main import main

__all__ = ["main"]
