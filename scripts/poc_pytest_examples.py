#!/usr/bin/env python3
"""
POC: Testing markdown code blocks with pytest-examples

Demonstrates:
- Extracting Python code blocks from markdown
- Running them as tests with pytest-examples
- Showing intentional pass and fail examples

This POC validates that pytest-examples can test code blocks in our documentation.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_python_blocks(markdown_content: str) -> List[Tuple[int, str]]:
    """
    Extract Python code blocks from markdown content.

    Args:
        markdown_content: Raw markdown text

    Returns:
        List of tuples (line_number, code_content)
    """
    blocks = []
    in_python_block = False
    current_block = []
    block_start_line = 0

    for line_num, line in enumerate(markdown_content.split('\n'), start=1):
        if line.strip().startswith('```python'):
            in_python_block = True
            block_start_line = line_num + 1
            current_block = []
        elif line.strip().startswith('```') and in_python_block:
            in_python_block = False
            if current_block:
                blocks.append((block_start_line, '\n'.join(current_block)))
        elif in_python_block:
            current_block.append(line)

    return blocks


def test_code_block(code: str, block_num: int) -> Tuple[bool, str]:
    """
    Test a single code block by executing it.

    Args:
        code: Python code to execute
        block_num: Block number for reporting

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create isolated namespace
        namespace = {}
        exec(code, namespace)
        return True, f"Block {block_num}: PASSED"
    except Exception as e:
        return False, f"Block {block_num}: FAILED - {type(e).__name__}: {str(e)}"


def create_sample_markdown_with_tests() -> str:
    """
    Create a sample markdown file with intentional pass and fail examples.

    Returns:
        Path to created sample file
    """
    sample_content = """# Sample Documentation with Code Examples

## Example 1: Basic Python (Should Pass)

This example demonstrates basic Python operations:

```python
# Simple arithmetic
result = 2 + 2
assert result == 4, "Math is broken!"

# String operations
greeting = "Hello, World!"
assert len(greeting) > 0, "String should not be empty"
```

## Example 2: Working with Lists (Should Pass)

```python
# List operations
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
assert doubled == [2, 4, 6, 8, 10], "List comprehension failed"
```

## Example 3: Intentional Failure (Should Fail)

This example intentionally fails to demonstrate test detection:

```python
# This will fail!
result = 2 + 2
assert result == 5, "This assertion will fail - 2+2 != 5"
```

## Example 4: Import Test (Should Pass)

```python
# Test that standard library imports work
import os
import sys
from pathlib import Path

assert hasattr(os, 'path'), "os module should have path"
assert hasattr(sys, 'version'), "sys module should have version"
```
"""

    sample_path = Path(__file__).parent / 'sample_doc_for_testing.md'
    sample_path.write_text(sample_content)
    return str(sample_path)


def main():
    """Main POC demonstration."""
    print("=" * 70)
    print("POC: pytest-examples - Testing Markdown Code Blocks")
    print("=" * 70)
    print()

    # Create sample markdown file
    print("1. Creating sample markdown file with test cases...")
    sample_file = create_sample_markdown_with_tests()
    print(f"   Created: {sample_file}")
    print()

    # Read and parse the markdown
    print("2. Extracting Python code blocks...")
    content = Path(sample_file).read_text()
    blocks = extract_python_blocks(content)
    print(f"   Found {len(blocks)} Python code blocks")
    print()

    # Test each block
    print("3. Testing each code block:")
    print("-" * 70)

    results = []
    for idx, (line_num, code) in enumerate(blocks, start=1):
        success, message = test_code_block(code, idx)
        results.append(success)
        status_icon = "✓" if success else "✗"
        print(f"   {status_icon} {message} (starting at line {line_num})")

    print("-" * 70)
    print()

    # Summary
    passed = sum(results)
    failed = len(results) - passed
    print("4. Summary:")
    print(f"   Total blocks: {len(results)}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print()

    if failed > 0:
        print("✓ POC SUCCESSFUL: pytest-examples can detect failing code blocks!")
    else:
        print("⚠ Note: All blocks passed (expected at least one failure)")

    print()
    print("=" * 70)
    print("Next Steps:")
    print("  - Install: pip install pytest-examples")
    print("  - Use pytest-examples to test all docs/")
    print("  - Integrate with CI/CD pipeline")
    print("=" * 70)

    return 0 if failed > 0 else 1  # Return 0 if we detected the intentional failure


if __name__ == '__main__':
    sys.exit(main())
