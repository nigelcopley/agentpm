"""
Markdown Demo Route for APM (Agent Project Manager) Web Application
"""

from flask import Blueprint, render_template

markdown_demo_bp = Blueprint('markdown_demo', __name__, url_prefix='/markdown-demo')


@markdown_demo_bp.route('/')
def markdown_demo():
    """Display markdown demo page with enhanced formatting examples."""
    
    # Sample markdown content for demonstration
    sample_markdown = """# Enhanced Markdown Features

This demonstrates the improved markdown rendering capabilities in AgentPM.

## Code Highlighting

Here's some Python code with syntax highlighting:

```python
def render_markdown(text, safe_mode=False, prose_class="prose prose-slate max-w-none"):
    \"\"\"
    Render markdown text to HTML with enhanced extensions and Tailwind Typography.
    
    Args:
        text (str): Markdown text to render
        safe_mode (bool): Whether to use safe mode (strip HTML)
        prose_class (str): Tailwind prose classes for styling
    
    Returns:
        str: Rendered HTML wrapped in prose container
    \"\"\"
    if not text:
        return ""
    
    # Configure markdown extensions for enhanced formatting
    extensions = [
        'codehilite',
        'fenced_code', 
        'tables',
        'toc',
        'nl2br',
        'attr_list',
        'def_list',
        'footnotes',
        'md_in_html',
    ]
    
    return render_markdown(text, prose_class=prose_class)
```

## Tables

| Feature | Description | Status |
|---------|-------------|--------|
| Syntax Highlighting | Code blocks with language detection | ✅ Complete |
| Responsive Tables | Tables that work on all screen sizes | ✅ Complete |
| Typography | Beautiful text formatting | ✅ Complete |
| Dark Mode | Automatic dark theme support | ✅ Complete |
| Interactive Elements | Copy buttons and smooth scrolling | ✅ Complete |
| Extensions | Footnotes, definition lists, etc. | ✅ Complete |

## Lists and Formatting

### Unordered List
- **Bold text** for emphasis
- *Italic text* for subtle emphasis
- `Inline code` for technical terms
- [Links](https://example.com) for references

### Ordered List
1. First item with detailed explanation
2. Second item with more information
3. Third item with additional context

## Blockquotes

> This is a blockquote that demonstrates the enhanced styling.
> It includes proper spacing, colours, and visual hierarchy.
> Perfect for highlighting important information or quotes.

## Definition Lists

Term 1
: Definition of the first term with detailed explanation

Term 2
: Definition of the second term with additional context

Term 3
: Definition of the third term with more information

## Horizontal Rules

Content above the rule.

---

Content below the rule.

## Footnotes

This text has a footnote[^1] and another footnote[^2].

[^1]: This is the first footnote with detailed information.
[^2]: This is the second footnote with additional context.

## Conclusion

The enhanced markdown rendering provides:

- **Professional appearance** with Tailwind Typography
- **Interactive features** like copy buttons
- **Responsive design** that works on all devices
- **Dark mode support** for better accessibility
- **Extended markdown features** for richer content

Perfect for documentation, README files, and content management!
"""
    
    return render_template('markdown_demo.html', sample_markdown=sample_markdown)
