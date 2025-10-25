"""
Unified Search Command

Vector search across all APM (Agent Project Manager) entities (work items, tasks, ideas, documents, summaries, evidence, learnings).
"""

import click
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from typing import List, Optional

from agentpm.core.database.models.search_result import SearchResult, SearchResults
from agentpm.core.database.enums import SearchResultType
from agentpm.core.search.service import SearchService
from agentpm.core.search.models import SearchQuery, SearchFilter, SearchScope
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option(
    '--scope',
    type=click.Choice([
        'all',
        'work_items',
        'tasks',
        'ideas',
        'documents',
        'summaries',
        'evidence',
        'sessions'
    ], case_sensitive=False),
    default='all',
    help='Search scope (default: all)'
)
@click.option(
    '--entity-type',
    type=click.Choice([
        'work_items',
        'tasks',
        'ideas',
        'documents',
        'summaries',
        'evidence',
        'sessions'
    ], case_sensitive=False),
    help='(Deprecated: use --scope) Filter by entity type'
)
@click.option(
    '--limit',
    type=int,
    default=20,
    help='Maximum number of results to show (default: 20)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'list', 'json'], case_sensitive=False),
    default='table',
    help='Output format (default: table)'
)
@click.option(
    '--min-relevance',
    type=float,
    default=0.3,
    help='Minimum relevance score (0.0-1.0, default: 0.3)'
)
@click.option(
    '--include-content',
    is_flag=True,
    help='Include full content in results (slower but more detailed)'
)
@click.pass_context
def search(ctx: click.Context, query: tuple, scope: str, entity_type: Optional[str],
           limit: int, format: str, min_relevance: float, include_content: bool):
    """
    🔍 Unified vector search across all APM (Agent Project Manager) entities.

    Search across work items, tasks, ideas, documents, summaries, evidence, and sessions
    to find all content related to your query. Uses semantic matching to find relevant
    content even with different terminology.

    \b
    Examples:
      # General search
      apm search "oauth"                           # Find all OAuth-related content
      apm search "validation"                      # Find validation-related work
      apm search "database schema"                 # Find database schema content

      # Scope-specific search
      apm search "oauth" --scope work_items        # Only work items
      apm search "session handover" --scope summaries  # Search summaries
      apm search "research findings" --scope evidence  # Search evidence
      apm search "debugging session" --scope sessions  # Search sessions
      apm search "API design" --scope documents    # Search documents only

      # Output control
      apm search "validation" --limit 10           # Limit results
      apm search "oauth" --min-relevance 0.7       # High relevance only
      apm search "oauth" --format json             # JSON output
      apm search "oauth" --include-content         # Include full content

\b
    Search Scopes:
      • all        - Search all entity types (default)
      • work_items - Search work items only
      • tasks      - Search tasks only
      • ideas      - Search ideas only
      • documents  - Search documents only
      • summaries  - Search summaries only
      • evidence   - Search evidence sources only
      • sessions   - Search sessions only

\b
    Search Features:
      • Semantic matching - finds related concepts
      • Cross-entity search - searches all entity types
      • Relevance scoring - results ranked by relevance
      • Multiple output formats - table, list, or JSON
      • Flexible filtering - by scope, relevance, etc.
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)

    # Join query words
    search_query_text = ' '.join(query)

    try:
        # Create search service
        search_service = SearchService(db_service)

        # Determine search scope (prefer --scope, fallback to --entity-type for backward compatibility)
        effective_scope = scope
        if entity_type:
            console.print("[yellow]Warning: --entity-type is deprecated. Use --scope instead.[/yellow]")
            effective_scope = entity_type

        # Create search query
        search_query = SearchQuery(
            query=search_query_text,
            scope=SearchScope(effective_scope),
            limit=limit,
            include_content=include_content
        )

        # Perform search
        search_results = search_service.search(search_query)
        
        if not search_results.results:
            console.print(f"\n[yellow]No results found for '{search_query_text}'[/yellow]")
            console.print("\n💡 [cyan]Try:[/cyan]")
            console.print("   • Different search terms")
            console.print("   • Lower minimum relevance: --min-relevance 0.1")
            console.print("   • Broader scope: --scope all")
            console.print("   • Specific scope: --scope summaries, --scope evidence, --scope sessions")
            return
        
        # Display results based on format
        if format == 'json':
            _display_json_results(console, search_results)
        elif format == 'list':
            _display_list_results(console, search_results, include_content)
        else:
            _display_table_results(console, search_results)
        
        # Show search summary
        console.print(f"\n[dim]{search_results.get_summary()}[/dim]")
        if search_results.entity_type_counts:
            console.print(f"[dim]By entity: {search_results.get_entity_type_summary()}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Search error: {e}[/red]")


def _display_json_results(console: Console, search_results: SearchResults):
    """Display search results in JSON format."""
    import json
    console.print(json.dumps(search_results.to_dict(), indent=2))


def _display_list_results(console: Console, search_results: SearchResults, include_content: bool):
    """Display search results in list format."""
    for i, result in enumerate(search_results.results, 1):
        # Result header
        console.print(f"\n[bold cyan]{i}.[/bold cyan] {result.get_display_title()}")
        console.print(f"   [dim]{result.get_entity_reference()} • {result.get_relevance_indicator()} {result.relevance_score:.2f}[/dim]")
        
        # Excerpt
        if result.excerpt:
            console.print(f"   [italic]{result.excerpt}[/italic]")
        
        # Full content if requested
        if include_content and result.content:
            console.print(f"   [dim]Content: {result.content[:200]}{'...' if len(result.content) > 200 else ''}[/dim]")
        
        # Metadata
        if result.tags:
            console.print(f"   [dim]Tags: {', '.join(result.tags)}[/dim]")


def _display_table_results(console: Console, search_results: SearchResults):
    """Display search results in table format."""
    table = Table(title=f"Search Results for '{search_results.query}'")
    
    # Add columns
    table.add_column("#", style="cyan", width=3)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Title", style="bold", width=40)
    table.add_column("Relevance", style="green", width=10)
    table.add_column("Excerpt", style="dim", width=50)
    
    # Add rows
    for i, result in enumerate(search_results.results, 1):
        table.add_row(
            str(i),
            result.entity_type.value,
            result.title[:37] + "..." if len(result.title) > 40 else result.title,
            f"{result.get_relevance_indicator()} {result.relevance_score:.2f}",
            result.excerpt[:47] + "..." if result.excerpt and len(result.excerpt) > 50 else (result.excerpt or "")
        )
    
    console.print(table)