"""
Claude Code Headless Integration

Wrapper for invoking Claude Code in headless mode to fill agent templates.

Pattern: Real implementation + Mock for testing
"""

import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path
import time


class ClaudeIntegrationError(Exception):
    """Raised when Claude Code invocation fails"""
    pass


def invoke_claude_code_headless(
    base_template: str,
    project_context: Dict[str, Any],
    max_retries: int = 3,
    timeout_seconds: int = 60,
    use_mock: bool = False
) -> str:
    """
    Invoke Claude Code headless to fill agent template with project context.

    Uses real Claude Code CLI in headless mode if available, otherwise falls back to mock.

    Args:
        base_template: Base template content with [INSTRUCTION] placeholders
        project_context: Project-specific context to inject
        max_retries: Number of retry attempts on failure
        timeout_seconds: Timeout for Claude invocation
        use_mock: Force mock implementation (for testing)

    Returns:
        Filled template with [INSTRUCTION] placeholders replaced

    Raises:
        ClaudeIntegrationError: If invocation fails after retries
    """
    # Use mock if requested or Claude not available
    if use_mock or not is_claude_code_available():
        mock = MockClaudeIntegration()
        return mock.fill_template(base_template, project_context)

    # Build prompt for Claude
    prompt = _build_fill_template_prompt(base_template, project_context)

    # Find Claude CLI
    claude_cmd = _find_claude_cli()
    if not claude_cmd:
        raise ClaudeIntegrationError(
            "Claude CLI not found. Install from: https://claude.ai/download\n"
            "Or use mock mode (default, no --use-claude flag needed)"
        )

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [claude_cmd, '-p', prompt,
                 '--output-format', 'json',
                 '--allowedTools', '',  # Disable tool use for speed
                 '--max-turns', '1'],   # Single turn, no extended reasoning
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            if result.returncode != 0:
                raise ClaudeIntegrationError(
                    f"Claude invocation failed (exit code {result.returncode}): {result.stderr}"
                )

            # Parse JSON response
            response = json.loads(result.stdout)

            if response.get('subtype') == 'success':
                full_result = response.get('result', '')

                # Claude often includes reasoning before the actual result
                # Try to extract just the filled template
                # Look for common patterns like "**Result:**" or just return the last substantial block
                if '**Result:**' in full_result or '**Output:**' in full_result:
                    # Extract after the Result: marker
                    for marker in ['**Result:**', '**Output:**', 'Result:']:
                        if marker in full_result:
                            parts = full_result.split(marker, 1)
                            if len(parts) > 1:
                                return parts[1].strip()

                # If no marker, return full result (might include reasoning, but better than nothing)
                return full_result
            else:
                raise ClaudeIntegrationError(
                    f"Claude returned non-success: {response.get('subtype')}"
                )

        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                time.sleep(1)  # Brief pause before retry
                continue
            raise ClaudeIntegrationError(f"Claude invocation timed out after {timeout_seconds}s")

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                continue
            raise ClaudeIntegrationError(f"Failed to parse Claude response: {e}")

        except Exception as e:
            if attempt < max_retries - 1:
                continue
            raise ClaudeIntegrationError(f"Claude invocation error: {e}")

    raise ClaudeIntegrationError(f"Failed after {max_retries} attempts")


def _build_fill_template_prompt(base_template: str, project_context: Dict[str, Any]) -> str:
    """
    Build prompt for Claude to fill template with project context.

    Uses simplified prompt format for faster Claude response.

    Args:
        base_template: Template with [INSTRUCTION] placeholders
        project_context: Project data to inject

    Returns:
        Prompt string for Claude
    """
    # Simplified, direct prompt format
    tech_stack = "\n".join(f"- {t}" for t in project_context.get('tech_stack', []))
    patterns = "\n".join(f"- {p}" for p in project_context.get('patterns', []))
    rules = "\n".join(f"- {r}" for r in project_context.get('rules', []))

    prompt = f"""Fill the template below by replacing each [INSTRUCTION: ...] with relevant content.

Context:
Tech Stack: {tech_stack or "Generic project"}
Patterns: {patterns or "Follow existing code"}
Rules: {rules or "Standard quality gates"}

Template to fill:
{base_template}

Replace ALL [INSTRUCTION: ...] markers with appropriate content. Output ONLY the filled template."""

    return prompt


class MockClaudeIntegration:
    """
    Mock Claude Code integration for testing and development.

    Simulates Claude Code headless by doing basic placeholder replacement.
    Replace with real implementation when Claude Code headless is available.
    """

    def fill_template(
        self,
        base_template: str,
        project_context: Dict[str, Any]
    ) -> str:
        """
        Fill template placeholders with project context.

        This is a simplified mock. Real Claude would:
        - Understand [INSTRUCTION] semantics
        - Query project files intelligently
        - Generate comprehensive, context-aware content

        Args:
            base_template: Template with [INSTRUCTION] markers
            project_context: Project data (tech_stack, patterns, rules)

        Returns:
            Template with placeholders filled
        """
        filled = base_template

        # Extract context
        tech_stack = project_context.get('tech_stack', [])
        patterns = project_context.get('patterns', [])
        rules = project_context.get('rules', [])
        examples = project_context.get('code_examples', [])

        # Simple placeholder replacement (real Claude would be smarter)
        filled = self._fill_tech_stack(filled, tech_stack)
        filled = self._fill_patterns(filled, patterns)
        filled = self._fill_rules(filled, rules)
        filled = self._fill_examples(filled, examples)

        return filled

    def _fill_tech_stack(self, template: str, tech_stack: list) -> str:
        """Fill tech stack instructions"""
        if not tech_stack:
            return template

        tech_list = "\n".join(f"- {tech}" for tech in tech_stack)

        # Replace tech stack instruction
        template = template.replace(
            "[INSTRUCTION: List detected languages, frameworks, libraries with versions]",
            tech_list
        )
        template = template.replace(
            "[INSTRUCTION: List all detected frameworks and versions from PluginOrchestrator]",
            tech_list
        )

        return template

    def _fill_patterns(self, template: str, patterns: list) -> str:
        """Fill pattern instructions"""
        if not patterns:
            return template

        pattern_text = "\n\n".join(patterns)

        # Replace pattern instructions
        template = template.replace(
            "[INSTRUCTION: Extract key implementation patterns from project codebase]",
            pattern_text
        )
        template = template.replace(
            "[INSTRUCTION: Extract implementation patterns specific to this project]",
            pattern_text
        )

        return template

    def _fill_rules(self, template: str, rules: list) -> str:
        """Fill rules instructions"""
        if not rules:
            return template

        rules_list = "\n".join(f"- {rule}" for rule in rules)

        # Replace rules instructions
        template = template.replace(
            "[INSTRUCTION: Query rules table for time-boxing limits, quality requirements, and enforcement levels]",
            rules_list
        )
        template = template.replace(
            "[INSTRUCTION: Query rules table WHERE enforcement_level='BLOCK' OR enforcement_level='LIMIT']",
            rules_list
        )

        return template

    def _fill_examples(self, template: str, examples: list) -> str:
        """Fill code example instructions"""
        if not examples:
            return template

        examples_text = "\n\n".join(f"```\n{ex}\n```" for ex in examples)

        # Replace example instructions
        template = template.replace(
            "[INSTRUCTION: Insert 2-3 actual code examples from project showing correct patterns]",
            examples_text
        )
        template = template.replace(
            "[INSTRUCTION: Provide code examples showing \"the right way\" in this project]",
            examples_text
        )

        return template


def _find_claude_cli() -> Optional[str]:
    """
    Find Claude CLI executable.

    Checks multiple common installation paths.

    Returns:
        Path to claude executable or None
    """
    claude_paths = [
        'claude',  # In PATH
        '/opt/homebrew/bin/claude',  # Homebrew on Apple Silicon
        '/usr/local/bin/claude',  # Homebrew on Intel Mac
        str(Path.home() / '.claude' / 'bin' / 'claude'),  # User install
    ]

    for path in claude_paths:
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return None


def get_claude_version() -> Optional[str]:
    """
    Get Claude Code version if installed.

    Returns:
        Version string or None if not installed
    """
    claude_cmd = _find_claude_cli()
    if not claude_cmd:
        return None

    try:
        result = subprocess.run(
            [claude_cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def is_claude_code_available() -> bool:
    """Check if Claude Code CLI is available"""
    return _find_claude_cli() is not None
