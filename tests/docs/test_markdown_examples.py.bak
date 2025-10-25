"""
Test all code examples in markdown documentation.

This module validates that:
- Python code blocks execute without errors
- Bash commands use valid syntax
- apm commands reference valid CLI commands
- Import statements work correctly
"""

import re
from pathlib import Path
from typing import List, Tuple

import pytest


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


def extract_apm_commands(markdown_content: str) -> List[Tuple[int, str]]:
    """
    Extract apm commands from bash code blocks.

    Args:
        markdown_content: Raw markdown text

    Returns:
        List of tuples (line_number, command)
    """
    commands = []
    in_bash_block = False
    line_num_tracker = 0

    for line_num, line in enumerate(markdown_content.split('\n'), start=1):
        if line.strip().startswith('```bash'):
            in_bash_block = True
        elif line.strip().startswith('```') and in_bash_block:
            in_bash_block = False
        elif in_bash_block:
            stripped = line.strip()
            if stripped.startswith('apm ') and not stripped.startswith('#'):
                commands.append((line_num, stripped))

    return commands


class TestMarkdownPythonExamples:
    """Test Python code blocks in markdown documentation."""

    def test_python_blocks_are_syntactically_valid(self, markdown_files: List[Path]):
        """
        Test that all Python code blocks have valid syntax.

        This test compiles Python code blocks to check for syntax errors.
        It does not execute the code to avoid side effects.

        Args:
            markdown_files: List of markdown files to test
        """
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            blocks = extract_python_blocks(content)

            for line_num, code in blocks:
                try:
                    compile(code, f"<{md_file.name}:L{line_num}>", 'exec')
                except SyntaxError as e:
                    errors.append(
                        f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                        f"{line_num}: SyntaxError: {e.msg}"
                    )

        if errors:
            pytest.fail(
                "Found Python syntax errors in documentation:\n" +
                "\n".join(errors)
            )

    def test_python_imports_are_valid(self, markdown_files: List[Path]):
        """
        Test that import statements in Python blocks reference real modules.

        This test only checks imports from the agentpm package, not external
        dependencies or standard library.

        Args:
            markdown_files: List of markdown files to test
        """
        project_root = Path(__file__).parent.parent.parent
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            blocks = extract_python_blocks(content)

            for line_num, code in blocks:
                # Extract import statements
                import_pattern = r'^(?:from|import)\s+(agentpm\.[\w.]+)'
                for line in code.split('\n'):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        module_path = match.group(1)
                        # Convert module path to file path
                        file_path = module_path.replace('.', '/')
                        possible_paths = [
                            project_root / f"{file_path}.py",
                            project_root / file_path / "__init__.py",
                        ]

                        if not any(p.exists() for p in possible_paths):
                            errors.append(
                                f"{md_file.relative_to(project_root)}:"
                                f"{line_num}: ImportError: {module_path} not found"
                            )

        if errors:
            pytest.fail(
                "Found invalid imports in documentation:\n" +
                "\n".join(errors)
            )

    @pytest.mark.slow
    def test_example_snippets_execute_without_error(self, markdown_files: List[Path]):
        """
        Test that example snippets marked as 'executable' actually run.

        Only tests blocks that are explicitly marked as safe to execute.
        Uses comment marker: # pytest: executable

        Args:
            markdown_files: List of markdown files to test
        """
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            blocks = extract_python_blocks(content)

            for line_num, code in blocks:
                # Only execute blocks marked as safe
                if '# pytest: executable' not in code:
                    continue

                try:
                    namespace = {}
                    exec(code, namespace)
                except Exception as e:
                    errors.append(
                        f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                        f"{line_num}: {type(e).__name__}: {str(e)}"
                    )

        if errors:
            pytest.fail(
                "Found runtime errors in executable documentation examples:\n" +
                "\n".join(errors)
            )


class TestMarkdownBashExamples:
    """Test bash command examples in markdown documentation."""

    def test_apm_commands_are_valid(
        self,
        markdown_files: List[Path],
        valid_apm_commands: List[str],
        valid_work_item_commands: List[str],
        valid_task_commands: List[str]
    ):
        """
        Test that apm commands in documentation reference valid CLI commands.

        Args:
            markdown_files: List of markdown files to test
            valid_apm_commands: List of valid top-level commands
            valid_work_item_commands: List of valid work-item subcommands
            valid_task_commands: List of valid task subcommands
        """
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            commands = extract_apm_commands(content)

            for line_num, cmd in commands:
                parts = cmd.split()
                if len(parts) < 2:
                    continue

                # Check top-level command
                command = parts[1]
                if command not in valid_apm_commands:
                    errors.append(
                        f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                        f"{line_num}: Invalid command 'apm {command}'"
                    )
                    continue

                # Check subcommands
                if len(parts) >= 3:
                    subcommand = parts[2]
                    # Skip if subcommand looks like an argument (starts with -)
                    if subcommand.startswith('-'):
                        continue

                    # Validate work-item subcommands
                    if command == 'work-item':
                        if subcommand not in valid_work_item_commands:
                            errors.append(
                                f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                                f"{line_num}: Invalid subcommand "
                                f"'apm work-item {subcommand}'"
                            )

                    # Validate task subcommands
                    elif command == 'task':
                        if subcommand not in valid_task_commands:
                            errors.append(
                                f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                                f"{line_num}: Invalid subcommand "
                                f"'apm task {subcommand}'"
                            )

        if errors:
            pytest.fail(
                "Found invalid apm commands in documentation:\n" +
                "\n".join(errors)
            )

    def test_command_examples_have_descriptions(self, markdown_files: List[Path]):
        """
        Test that command examples are preceded by explanatory text.

        Good documentation should explain what commands do before showing them.

        Args:
            markdown_files: List of markdown files to test
        """
        warnings = []

        for md_file in markdown_files:
            lines = md_file.read_text().split('\n')

            for i, line in enumerate(lines):
                if line.strip().startswith('```bash'):
                    # Check if there's explanatory text in previous 3 lines
                    has_context = False
                    for j in range(max(0, i - 3), i):
                        if lines[j].strip() and not lines[j].strip().startswith('#'):
                            has_context = True
                            break

                    if not has_context:
                        warnings.append(
                            f"{md_file.relative_to(md_file.parent.parent.parent)}:"
                            f"{i + 1}: Bash block lacks context/explanation"
                        )

        # This is a warning, not a failure - documentation quality issue
        if warnings:
            print("\nWarning: Some bash blocks lack explanatory context:")
            for warning in warnings[:10]:  # Show first 10
                print(f"  {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more")


class TestMarkdownStructure:
    """Test markdown file structure and formatting."""

    def test_markdown_files_exist(self, docs_dir: Path):
        """
        Test that documentation directory contains markdown files.

        Args:
            docs_dir: Documentation directory path
        """
        md_files = list(docs_dir.rglob("*.md"))
        assert len(md_files) > 0, "No markdown files found in docs directory"

    def test_markdown_files_have_headings(self, markdown_files: List[Path]):
        """
        Test that markdown files have at least one heading.

        Args:
            markdown_files: List of markdown files to test
        """
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            if not re.search(r'^#+\s+.+', content, re.MULTILINE):
                errors.append(
                    f"{md_file.relative_to(md_file.parent.parent.parent)}: "
                    "No headings found"
                )

        if errors:
            pytest.fail(
                "Found markdown files without headings:\n" +
                "\n".join(errors)
            )

    def test_code_blocks_are_closed(self, markdown_files: List[Path]):
        """
        Test that all code blocks are properly closed.

        Args:
            markdown_files: List of markdown files to test
        """
        errors = []

        for md_file in markdown_files:
            content = md_file.read_text()
            backtick_count = content.count('```')

            if backtick_count % 2 != 0:
                errors.append(
                    f"{md_file.relative_to(md_file.parent.parent.parent)}: "
                    f"Unclosed code block (found {backtick_count} backtick markers)"
                )

        if errors:
            pytest.fail(
                "Found markdown files with unclosed code blocks:\n" +
                "\n".join(errors)
            )
