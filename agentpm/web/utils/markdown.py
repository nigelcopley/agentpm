"""
Markdown rendering utilities for APM (Agent Project Manager) Web Application
"""

import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc
import re
from markupsafe import Markup


def render_markdown(text, safe_mode=False):
    """
    Render markdown text to HTML with extensions.
    
    Args:
        text (str): Markdown text to render
        safe_mode (bool): Whether to use safe mode (strip HTML)
    
    Returns:
        str: Rendered HTML
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Configure markdown extensions
    extensions = [
        'codehilite',
        'fenced_code', 
        'tables',
        'toc',
        'nl2br',  # Convert newlines to <br>
        'attr_list',  # Allow attributes on elements
    ]
    
    # Configure extension options
    extension_configs = {
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': False,  # Use simple highlighting
        },
        'toc': {
            'permalink': True,
            'permalink_title': 'Link to this section',
        }
    }
    
    # Create markdown instance
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=extension_configs,
        safe_mode=safe_mode
    )
    
    # Render markdown
    html = md.convert(text)
    
    # Post-process to add Tailwind classes for better styling
    html = add_tailwind_classes(html)
    
    # Return as safe HTML (won't be escaped by Jinja2)
    return Markup(html)


def add_tailwind_classes(html):
    """
    Add Tailwind CSS classes to markdown-rendered HTML for better styling.
    
    Args:
        html (str): HTML content
    
    Returns:
        str: HTML with Tailwind classes
    """
    if not html:
        return html
    
    # Add classes to common elements
    replacements = [
        # Headings
        (r'<h1>', '<h1 class="text-3xl font-bold text-gray-900 mb-4">'),
        (r'<h2>', '<h2 class="text-2xl font-semibold text-gray-800 mb-3">'),
        (r'<h3>', '<h3 class="text-xl font-semibold text-gray-800 mb-2">'),
        (r'<h4>', '<h4 class="text-lg font-medium text-gray-800 mb-2">'),
        (r'<h5>', '<h5 class="text-base font-medium text-gray-800 mb-1">'),
        (r'<h6>', '<h6 class="text-sm font-medium text-gray-800 mb-1">'),
        
        # Paragraphs
        (r'<p>', '<p class="text-gray-700 leading-relaxed mb-4">'),
        
        # Lists
        (r'<ul>', '<ul class="list-disc list-inside text-gray-700 mb-4 space-y-1">'),
        (r'<ol>', '<ol class="list-decimal list-inside text-gray-700 mb-4 space-y-1">'),
        (r'<li>', '<li class="text-gray-700">'),
        
        # Code blocks
        (r'<pre>', '<pre class="bg-gray-100 rounded-lg p-4 overflow-x-auto mb-4">'),
        (r'<code>', '<code class="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm">'),
        
        # Blockquotes
        (r'<blockquote>', '<blockquote class="border-l-4 border-blue-500 pl-4 italic text-gray-600 mb-4">'),
        
        # Tables
        (r'<table>', '<table class="min-w-full divide-y divide-gray-200 mb-4">'),
        (r'<thead>', '<thead class="bg-gray-50">'),
        (r'<th>', '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">'),
        (r'<td>', '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">'),
        
        # Links
        (r'<a href=', '<a href='),
        (r'<a href="([^"]*)"', r'<a href="\1" class="text-blue-600 hover:text-blue-800 underline"'),
        
        # Strong and emphasis
        (r'<strong>', '<strong class="font-semibold text-gray-900">'),
        (r'<em>', '<em class="italic text-gray-800">'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        html = re.sub(pattern, replacement, html)
    
    return html


def markdown_to_text(text, max_length=None):
    """
    Convert markdown to plain text (strip HTML tags).
    
    Args:
        text (str): Markdown text
        max_length (int): Maximum length of returned text
    
    Returns:
        str: Plain text
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Render markdown to HTML first
    html = render_markdown(text, safe_mode=True)
    
    # Strip HTML tags
    import re
    text_only = re.sub(r'<[^>]+>', '', html)
    
    # Clean up whitespace
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    
    # Truncate if needed
    if max_length and len(text_only) > max_length:
        text_only = text_only[:max_length] + "..."
    
    return text_only


def format_enum_display(enum_value):
    """
    Format enum values for display by removing enum class prefixes.
    
    Args:
        enum_value: Enum value (e.g., IdeaStatus.IDEA, TaskStatus.ACTIVE)
    
    Returns:
        str: Formatted display value (e.g., "Idea", "Active")
    """
    if not enum_value:
        return "Unknown"
    
    # If it's already a string, process it
    if isinstance(enum_value, str):
        value = enum_value
    else:
        # If it has a value attribute (enum), use that
        if hasattr(enum_value, 'value'):
            value = enum_value.value
        else:
            value = str(enum_value)
    
    # Remove common enum prefixes and format
    value = str(value)
    
    # Remove enum class prefixes (e.g., "IdeaStatus.IDEA" -> "IDEA")
    if '.' in value:
        value = value.split('.')[-1]
    
    # Convert to title case and replace underscores
    formatted = value.replace('_', ' ').title()
    
    return formatted


def render_context_data(context_data):
    """
    Render context data (JSON or text) into a readable format.
    
    Args:
        context_data: Context data (could be JSON string, dict, or text)
    
    Returns:
        str: Rendered HTML
    """
    if not context_data:
        return ""
    
    # If it's already a string and looks like JSON, try to parse it
    if isinstance(context_data, str):
        # Check if it looks like JSON
        if context_data.strip().startswith('{') or context_data.strip().startswith('['):
            try:
                import json
                data = json.loads(context_data)
                return render_json_context(data)
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, treat as regular text
                return render_markdown(context_data, safe_mode=True)
        else:
            # Regular text, render as markdown
            return render_markdown(context_data, safe_mode=True)
    
    # If it's already a dict/list, render it directly
    elif isinstance(context_data, (dict, list)):
        return render_json_context(context_data)
    
    # Fallback to string conversion and markdown rendering
    else:
        return render_markdown(str(context_data), safe_mode=True)


def render_json_context(data):
    """
    Render JSON context data into a readable HTML format.
    
    Args:
        data: JSON data (dict or list)
    
    Returns:
        str: Rendered HTML
    """
    if not data:
        return ""
    
    html_parts = []
    
    if isinstance(data, dict):
        # Handle dict data
        for key, value in data.items():
            if value:  # Only show non-empty values
                formatted_key = key.replace('_', ' ').title()
                
                if isinstance(value, list):
                    if value:  # Only show non-empty lists
                        html_parts.append(f"<div class='mb-2'><strong class='text-gray-900'>{formatted_key}:</strong></div>")
                        html_parts.append("<ul class='list-disc list-inside ml-4 mb-3 space-y-1'>")
                        for item in value:
                            html_parts.append(f"<li class='text-sm text-gray-700'>{item}</li>")
                        html_parts.append("</ul>")
                elif isinstance(value, dict):
                    html_parts.append(f"<div class='mb-2'><strong class='text-gray-900'>{formatted_key}:</strong></div>")
                    html_parts.append("<div class='ml-4 mb-3 border-l-2 border-gray-200 pl-4'>")
                    html_parts.append(render_json_context(value))
                    html_parts.append("</div>")
                else:
                    html_parts.append(f"<div class='mb-2'><strong class='text-gray-900'>{formatted_key}:</strong> <span class='text-gray-700'>{value}</span></div>")
    
    elif isinstance(data, list):
        # Handle list data
        html_parts.append("<ul class='list-disc list-inside ml-4 space-y-1'>")
        for item in data:
            if isinstance(item, dict):
                html_parts.append("<li class='mb-2'>")
                html_parts.append(render_json_context(item))
                html_parts.append("</li>")
            else:
                html_parts.append(f"<li class='text-sm text-gray-700'>{item}</li>")
        html_parts.append("</ul>")
    
    return Markup(''.join(html_parts))
