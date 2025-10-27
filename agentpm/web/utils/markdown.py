"""
Enhanced markdown rendering utilities for APM (Agent Project Manager) Web Application
"""

import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc, attr_list, nl2br, def_list, footnotes
import re
from markupsafe import Markup


def render_markdown(text, safe_mode=False, prose_class="prose prose-slate max-w-none"):
    """
    Render markdown text to HTML with enhanced extensions and Tailwind Typography.
    
    Args:
        text (str): Markdown text to render
        safe_mode (bool): Whether to use safe mode (strip HTML)
        prose_class (str): Tailwind prose classes for styling
    
    Returns:
        str: Rendered HTML wrapped in prose container
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Configure markdown extensions for enhanced formatting
    extensions = [
        'codehilite',
        'fenced_code', 
        'tables',
        'toc',
        'nl2br',  # Convert newlines to <br>
        'attr_list',  # Allow attributes on elements
        'def_list',  # Definition lists
        'footnotes',  # Footnotes support
        'md_in_html',  # Allow HTML in markdown
    ]
    
    # Configure extension options
    extension_configs = {
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,  # Enable syntax highlighting
            'linenums': True,  # Enable line numbers
            'guess_lang': True,  # Auto-detect language
        },
        'toc': {
            'permalink': True,
            'permalink_title': 'Link to this section',
            'permalink_class': 'text-blue-600 hover:text-blue-800',
        },
        'footnotes': {
            'BACKLINK_TEXT': '↩',
            'BACKLINK_TITLE': 'Jump back to footnote %d in the text',
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
    
    # Post-process to enhance styling and add custom classes
    html = enhance_markdown_html(html)
    
    # Wrap in prose container with custom classes
    wrapped_html = f'<div class="{prose_class}">{html}</div>'
    
    # Return as safe HTML (won't be escaped by Jinja2)
    return Markup(wrapped_html)


def enhance_markdown_html(html):
    """
    Enhance markdown-rendered HTML with custom styling and features.
    
    Args:
        html (str): HTML content
    
    Returns:
        str: Enhanced HTML with custom classes and features
    """
    if not html:
        return html
    
    # Enhance code blocks with better styling
    html = enhance_code_blocks(html)
    
    # Enhance tables with responsive design
    html = enhance_tables(html)
    
    # Add custom styling for specific elements
    html = add_custom_styling(html)
    
    return html


def enhance_code_blocks(html):
    """
    Enhance code blocks with better styling and features.
    
    Args:
        html (str): HTML content
    
    Returns:
        str: HTML with enhanced code blocks
    """
    # Add copy button functionality to code blocks
    def add_copy_button(match):
        code_content = match.group(1)
        language = match.group(2) if match.group(2) else 'text'
        
        return f'''
        <div class="relative group">
            <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onclick="copyToClipboard(this)" 
                        class="bg-gray-800 text-white px-2 py-1 rounded text-xs hover:bg-gray-700 transition-colors"
                        data-code="{code_content.replace('"', '&quot;')}">
                    <i class="bi bi-clipboard mr-1"></i>Copy
                </button>
            </div>
            <pre class="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm"><code class="language-{language}">{code_content}</code></pre>
        </div>
        '''
    
    # Pattern to match code blocks
    pattern = r'<pre><code class="language-(\w+)">(.*?)</code></pre>'
    html = re.sub(pattern, add_copy_button, html, flags=re.DOTALL)
    
    return html


def enhance_tables(html):
    """
    Enhance tables with responsive design and better styling.
    
    Args:
        html (str): HTML content
    
    Returns:
        str: HTML with enhanced tables
    """
    # Wrap tables in responsive container
    def wrap_table(match):
        table_content = match.group(0)
        return f'''
        <div class="overflow-x-auto shadow-sm rounded-lg border border-gray-200 mb-6">
            {table_content}
        </div>
        '''
    
    # Pattern to match tables
    pattern = r'<table>.*?</table>'
    html = re.sub(pattern, wrap_table, html, flags=re.DOTALL)
    
    return html


def add_custom_styling(html):
    """
    Add custom styling to specific markdown elements.
    
    Args:
        html (str): HTML content
    
    Returns:
        str: HTML with custom styling
    """
    # Enhance blockquotes with better styling
    html = re.sub(
        r'<blockquote>',
        '<blockquote class="border-l-4 border-blue-500 bg-blue-50 pl-6 pr-4 py-4 rounded-r-lg my-6">',
        html
    )
    
    # Enhance horizontal rules
    html = re.sub(
        r'<hr>',
        '<hr class="border-gray-300 my-8">',
        html
    )
    
    # Enhance definition lists
    html = re.sub(
        r'<dl>',
        '<dl class="space-y-2">',
        html
    )
    html = re.sub(
        r'<dt>',
        '<dt class="font-semibold text-gray-900">',
        html
    )
    html = re.sub(
        r'<dd>',
        '<dd class="ml-4 text-gray-700">',
        html
    )
    
    # Enhance footnotes
    html = re.sub(
        r'<div class="footnote">',
        '<div class="footnote border-t border-gray-200 pt-4 mt-8 text-sm text-gray-600">',
        html
    )
    
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


def render_markdown_compact(text, max_length=200):
    """
    Render markdown text in a compact format suitable for previews and cards.
    
    Args:
        text (str): Markdown text to render
        max_length (int): Maximum length of rendered text
    
    Returns:
        str: Compact HTML
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Truncate text first
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Use compact prose classes
    return render_markdown(text, prose_class="prose prose-sm prose-slate max-w-none")


def render_markdown_large(text):
    """
    Render markdown text in a large format suitable for full document display.
    
    Args:
        text (str): Markdown text to render
    
    Returns:
        str: Large format HTML
    """
    if not text:
        return ""
    
    # Use large prose classes
    return render_markdown(text, prose_class="prose prose-lg prose-slate max-w-none")


def render_markdown_dark(text):
    """
    Render markdown text with dark theme styling.
    
    Args:
        text (str): Markdown text to render
    
    Returns:
        str: Dark themed HTML
    """
    if not text:
        return ""
    
    # Use dark prose classes
    return render_markdown(text, prose_class="prose prose-slate dark:prose-invert max-w-none")


def get_markdown_toc(text):
    """
    Extract table of contents from markdown text.
    
    Args:
        text (str): Markdown text
    
    Returns:
        str: Table of contents HTML
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Create markdown instance with TOC extension
    md = markdown.Markdown(extensions=['toc'])
    md.convert(text)
    
    # Get the TOC
    toc_html = md.toc
    
    if toc_html:
        return Markup(f'<div class="prose prose-sm prose-slate max-w-none">{toc_html}</div>')
    
    return ""


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
