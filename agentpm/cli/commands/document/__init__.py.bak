"""
apm document - Document management commands

Comprehensive document management for work items, tasks, and ideas.
Links documents to entities and tracks document metadata.
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.group()
@click.pass_context
def document(ctx: click.Context):
    """
    📄 Document Management Commands
    
    Manage document references for work items, tasks, and ideas.
    Links documents to entities and tracks document metadata.
    
    \b
    Document Types:
      architecture      System architecture documents
      design           Design specifications and diagrams
      specification    Technical specifications
      user_guide       User documentation and guides
      api_docs         API documentation
      test_plan        Testing plans and strategies
      deployment_guide Deployment and operations guides
      troubleshooting  Troubleshooting and support docs
      changelog        Release notes and changelogs
      adr              Architecture Decision Records
      requirements     Requirements documents
      user_story       User stories and use cases
      other            Other document types
    
    \b
    Document Formats:
      markdown         Markdown files (.md)
      html            HTML files (.html)
      pdf             PDF documents (.pdf)
      text            Plain text files (.txt)
      json            JSON files (.json)
      yaml            YAML files (.yaml)
      other           Other formats
    
    \b
    Examples:
      # Add document to work item
      apm document add --entity-type=work-item --entity-id=5 \\
          --file-path="docs/api-specification.md" \\
          --type=specification --title="API Specification"
      
      # List documents for task
      apm document list --entity-type=task --entity-id=12
      
      # Show document details
      apm document show 25
      
      # Update document metadata
      apm document update 25 --title="Updated API Spec" --description="Latest version"
      
      # Delete document reference
      apm document delete 25
    
    \b
    See Also:
      apm work-item show <id>    # Show work item with documents
      apm task show <id>         # Show task with documents
      apm idea show <id>         # Show idea with documents
    """
    # Initialize shared context
    ctx.ensure_object(dict)
    
    # Respect injected context from tests; only derive if missing
    if 'project_root' not in ctx.obj or ctx.obj['project_root'] is None:
        project_root = ensure_project_root(ctx)
        ctx.obj['project_root'] = project_root
    
    if 'db_service' not in ctx.obj or ctx.obj['db_service'] is None:
        ctx.obj['db_service'] = get_database_service(ctx.obj['project_root'])


# Import subcommands
from .add import add
from .list import list_documents
from .show import show
from .update import update
from .delete import delete
from .types import types
from .migrate import migrate_to_structure

# Register subcommands
document.add_command(add)
document.add_command(list_documents)
document.add_command(show)
document.add_command(update)
document.add_command(delete)
document.add_command(types)
document.add_command(migrate_to_structure)
