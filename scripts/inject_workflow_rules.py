#!/usr/bin/env python3
"""
Inject workflow rules section into all agent templates.

This script:
1. Reads the workflow rules template
2. Finds all agent templates
3. Injects workflow section after "## 2. Rule Compliance"
4. Preserves all existing content
"""

import re
from pathlib import Path
from typing import List, Tuple


def read_workflow_template() -> str:
    """Read the workflow rules template (section content only)."""
    template_path = Path("agentpm/templates/agents/_workflow_rules_template.md")
    content = template_path.read_text()

    # Extract only the "## Workflow Rules" section and everything after
    # (skip the file header)
    lines = content.split('\n')
    start_idx = next(i for i, line in enumerate(lines) if line.startswith('## Workflow Rules'))

    return '\n'.join(lines[start_idx:])


def find_agent_templates() -> List[Path]:
    """Find all agent template files (excluding special files)."""
    templates_dir = Path("agentpm/templates/agents")

    # Get all .md files except README and _workflow_rules_template
    templates = [
        f for f in templates_dir.glob("*.md")
        if not f.name.startswith('_') and f.name != 'README.md'
    ]

    return sorted(templates)


def inject_workflow_section(template_path: Path, workflow_content: str) -> Tuple[bool, str]:
    """
    Inject workflow section into template after "## 2. Rule Compliance".

    Returns:
        Tuple of (success, message)
    """
    content = template_path.read_text()

    # Check if workflow section already exists
    if '## 2.1. Workflow Rules (MANDATORY)' in content or '## Workflow Rules (MANDATORY)' in content:
        return False, f"Workflow section already exists in {template_path.name}"

    # Find where to inject (after "## 2. Rule Compliance" section)
    # Look for the pattern: "## 2. Rule Compliance" followed by content, then "## 3. Core Expertise"

    # Split into sections
    pattern = r'(## 2\. Rule Compliance.*?)(## 3\. Core Expertise)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return False, f"Could not find insertion point in {template_path.name} (no '## 2. Rule Compliance' followed by '## 3. Core Expertise')"

    # Insert workflow section between section 2 and section 3
    rule_compliance_section = match.group(1)
    core_expertise_section = match.group(2)

    # Create new section 2.1 for workflow rules
    workflow_section = f"\n\n## 2.1. {workflow_content.lstrip('## ')}"

    # Replace in content
    new_content = content.replace(
        match.group(0),
        f"{rule_compliance_section}{workflow_section}\n\n{core_expertise_section}"
    )

    # Write back
    template_path.write_text(new_content)

    return True, f"✓ Injected workflow rules into {template_path.name}"


def main():
    """Main execution."""
    print("=" * 80)
    print("Injecting Workflow Rules into Agent Templates")
    print("=" * 80)
    print()

    # Read workflow template
    print("📖 Reading workflow rules template...")
    workflow_content = read_workflow_template()
    print(f"   Workflow rules: {len(workflow_content)} characters")
    print()

    # Find templates
    print("🔍 Finding agent templates...")
    templates = find_agent_templates()
    print(f"   Found {len(templates)} templates")
    print()

    # Inject into each template
    print("💉 Injecting workflow rules...")
    print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for template in templates:
        success, message = inject_workflow_section(template, workflow_content)

        if success:
            print(f"  {message}")
            success_count += 1
        elif "already exists" in message:
            print(f"  ⊘ {message}")
            skip_count += 1
        else:
            print(f"  ✗ {message}")
            error_count += 1

    print()
    print("=" * 80)
    print(f"Summary: {success_count} updated, {skip_count} skipped, {error_count} errors")
    print("=" * 80)

    if error_count > 0:
        print()
        print("⚠️  Some templates had errors. Review output above.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
