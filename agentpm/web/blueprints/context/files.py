"""
Context Files Module for APM (Agent Project Manager) Web Application

Handles file-related context functionality including:
- File listing and management
- File preview and download
- File-based context creation
"""

from flask import render_template, request, send_file, abort
import os
import logging

from . import context_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable size string (e.g., "15.2 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

@context_bp.route('/documents')
def context_documents():
    """Documents context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get document contexts
    document_contexts = contexts.list_contexts(db, project_id=project_id) or []
    document_contexts = [ctx for ctx in document_contexts if ctx.context_type and ctx.context_type.value == 'resource_file']
    
    return render_template('context/documents.html', 
                         contexts=document_contexts,
                         total_documents=len(document_contexts))

@context_bp.route('/files')
def context_files():
    """Files context view - reads actual files from .agentpm/contexts/ directory"""
    from pathlib import Path
    from datetime import datetime
    
    # Find the .agentpm/contexts directory
    current_dir = Path.cwd()
    contexts_dir = None
    
    # Look for .agentpm/contexts in current directory or parent directories
    search_dir = current_dir
    while search_dir != search_dir.parent:
        potential_contexts = search_dir / '.agentpm' / 'contexts'
        if potential_contexts.exists() and potential_contexts.is_dir():
            contexts_dir = potential_contexts
            break
        search_dir = search_dir.parent
    
    if not contexts_dir:
        # Fallback to current directory .agentpm/contexts
        contexts_dir = current_dir / '.agentpm' / 'contexts'
    
    # Read files from the contexts directory
    context_files = []
    file_types = {}
    total_size = 0
    
    if contexts_dir.exists():
        for file_path in contexts_dir.rglob('*'):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    file_ext = file_path.suffix.lower()
                    
                    # Create file info object
                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path.relative_to(contexts_dir)),
                        'full_path': str(file_path),
                        'size_bytes': stat.st_size,
                        'size_human': format_file_size(stat.st_size),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'file_type': file_ext or 'no extension',
                        'created_at': datetime.fromtimestamp(stat.st_ctime)
                    }
                    
                    context_files.append(file_info)
                    total_size += stat.st_size
                    
                    # Group by file type
                    if file_ext not in file_types:
                        file_types[file_ext] = []
                    file_types[file_ext].append(file_info)
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not read file {file_path}: {e}")
                    continue
    
    # Sort files by modification time (newest first)
    context_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('context/files.html', 
                         contexts=context_files,
                         file_types=file_types,
                         total_files=len(context_files),
                         total_size=total_size)

@context_bp.route('/files/preview/<path:filepath>')
def preview_file(filepath: str):
    """Preview a file from .agentpm/contexts/ directory"""
    try:
        from pathlib import Path
        
        # Security check - ensure filepath is safe
        if '..' in filepath or filepath.startswith('/'):
            abort(403, description="Invalid file path")
        
        # Find the .agentpm/contexts directory
        current_dir = Path.cwd()
        contexts_dir = None
        
        # Look for .agentpm/contexts in current directory or parent directories
        search_dir = current_dir
        while search_dir != search_dir.parent:
            potential_contexts = search_dir / '.agentpm' / 'contexts'
            if potential_contexts.exists() and potential_contexts.is_dir():
                contexts_dir = potential_contexts
                break
            search_dir = search_dir.parent
        
        if not contexts_dir:
            contexts_dir = current_dir / '.agentpm' / 'contexts'
        
        # Build full file path
        full_file_path = contexts_dir / filepath
        
        # Security check - ensure file is within contexts directory
        try:
            full_file_path.resolve().relative_to(contexts_dir.resolve())
        except ValueError:
            abort(403, description="File path outside contexts directory")
        
        if not full_file_path.exists() or not full_file_path.is_file():
            abort(404, description="File not found")
        
        # Read file content
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding or show binary message
            content = f"[Binary file - {full_file_path.suffix} - Preview not available]"
        
        # Truncate very large files
        is_truncated = len(content) > 10000
        if is_truncated:
            content = content[:10000] + "\n\n... [Content truncated for preview]"
        
        stat = full_file_path.stat()
        
        from datetime import datetime
        
        return render_template('context/file_preview.html', 
                             file_name=full_file_path.name,
                             file_path=filepath,
                             content=content,
                             is_truncated=is_truncated,
                             file_size=stat.st_size,
                             modified=datetime.fromtimestamp(stat.st_mtime))
        
    except Exception as e:
        logger.error(f"Error previewing file {filepath}: {e}")
        abort(500, description="Error previewing file")

@context_bp.route('/files/download/<path:filepath>')
def download_file(filepath: str):
    """Download a file from .agentpm/contexts/ directory"""
    try:
        from pathlib import Path
        
        # Security check - ensure filepath is safe
        if '..' in filepath or filepath.startswith('/'):
            abort(403, description="Invalid file path")
        
        # Find the .agentpm/contexts directory
        current_dir = Path.cwd()
        contexts_dir = None
        
        # Look for .agentpm/contexts in current directory or parent directories
        search_dir = current_dir
        while search_dir != search_dir.parent:
            potential_contexts = search_dir / '.agentpm' / 'contexts'
            if potential_contexts.exists() and potential_contexts.is_dir():
                contexts_dir = potential_contexts
                break
            search_dir = search_dir.parent
        
        if not contexts_dir:
            contexts_dir = current_dir / '.agentpm' / 'contexts'
        
        # Build full file path
        full_file_path = contexts_dir / filepath
        
        # Security check - ensure file is within contexts directory
        try:
            full_file_path.resolve().relative_to(contexts_dir.resolve())
        except ValueError:
            abort(403, description="File path outside contexts directory")
        
        if not full_file_path.exists() or not full_file_path.is_file():
            abort(404, description="File not found")
        
        # Send file for download
        return send_file(
            full_file_path,
            as_attachment=True,
            download_name=full_file_path.name,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading file {filepath}: {e}")
        abort(500, description="Error downloading file")
