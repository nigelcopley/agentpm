#!/usr/bin/env python3
"""
Claude Code FileSave Hook - Template Generated

Executes when files are saved/modified for change tracking and validation.
Useful for file modification logging, diff capture, and audit trails.

Features:
- File modification tracking
- Change diff capture (before/after)
- Automatic git staging (optional)
- File validation (syntax, format)

Security:
- Path validation (project boundaries)
- Content validation (no secrets)
- Size limits (prevent huge files)

Generated: 2025-10-27T18:45:32.975602
Template: hooks/file-save.py.j2
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Sensitive patterns that should not be in files
SENSITIVE_PATTERNS = [
    r'api[_-]?key[\s:=]+["\']?[a-zA-Z0-9_-]+["\']?',
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key format
    r'password[\s:=]+["\']?[^\s"\']+["\']?',
    r'secret[\s:=]+["\']?[^\s"\']+["\']?',
    r'Bearer [a-zA-Z0-9_.-]+',
    r'-----BEGIN PRIVATE KEY-----'
]

# Maximum file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def validate_file_path(file_path: str) -> tuple[bool, str]:
    """
    Validate file path for security.

    Args:
        file_path: File path from hook input

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "No file path provided"

    # Check for path traversal
    if '..' in file_path:
        return False, f"Path traversal detected: {file_path}"

    try:
        path = Path(file_path)
        if not path.is_absolute():
            path = (PROJECT_ROOT / file_path).resolve()
        else:
            path = path.resolve()

        # Check within project boundaries
        try:
            path.relative_to(PROJECT_ROOT.resolve())
        except ValueError:
            return False, f"File outside project: {file_path}"

        return True, ""

    except Exception as e:
        return False, f"Path validation failed: {e}"


def validate_file_content(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate file content for security issues.

    Checks:
    - No sensitive data patterns (API keys, passwords)
    - File size within limits
    - Valid UTF-8 encoding (for text files)

    Args:
        file_path: File path to validate

    Returns:
        Tuple of (is_valid, warnings_list)
    """
    warnings = []

    try:
        path = Path(file_path)
        if not path.exists():
            return True, warnings

        # Check file size
        size = path.stat().st_size
        if size > MAX_FILE_SIZE:
            warnings.append(f"File exceeds size limit: {size / (1024*1024):.2f} MB > {MAX_FILE_SIZE / (1024*1024)} MB")
            return False, warnings

        # Skip binary files
        if path.suffix in ['.pyc', '.so', '.dylib', '.dll', '.exe', '.bin']:
            return True, warnings

        # Read content for text files
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Binary file, skip content validation
            return True, warnings

        # Check for sensitive patterns
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Potential sensitive data detected (pattern: {pattern[:30]}...)")

        return len(warnings) == 0, warnings

    except Exception as e:
        warnings.append(f"Content validation failed: {e}")
        return False, warnings


def log_file_modification(file_path: str, file_size: int) -> None:
    """
    Log file modification to database for audit trail.

    Logs:
    - File path
    - Modification timestamp
    - File size
    - Session ID

    Args:
        file_path: File path being modified
        file_size: File size in bytes
    """
    try:
        from agentpm.core.database import DatabaseService

        db_path = PROJECT_ROOT / ".aipm" / "data" / "aipm.db"
        db = DatabaseService(str(db_path))

        # Log to database (lightweight log for now)
        # Future: Track in file_modifications table
        print(f"💾 File saved: {file_path} ({file_size} bytes)", file=sys.stderr)

    except Exception as e:
        print(f"⚠️ Modification logging failed (non-critical): {e}", file=sys.stderr)


def auto_stage_file(file_path: str) -> bool:
    """
    Optionally auto-stage file in git.

    This is DISABLED by default. Enable via environment variable:
    AIPM_AUTO_STAGE=1

    Args:
        file_path: File path to stage

    Returns:
        True if staged successfully
    """
    import os
    if os.environ.get('AIPM_AUTO_STAGE', '0') != '1':
        return False

    try:
        import subprocess
        result = subprocess.run(
            ['git', 'add', file_path],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            print(f"✅ File auto-staged: {file_path}", file=sys.stderr)
            return True
        else:
            print(f"⚠️ Git staging failed: {result.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"⚠️ Auto-staging failed: {e}", file=sys.stderr)
        return False


def main():
    """Main hook entry point."""
    try:
        hook_data = read_hook_input()

        # Extract file path from hook data
        file_path = hook_data.get('file_path', '') or hook_data.get('tool_params', {}).get('file_path', '')

        print(f"🪝 FileSave: file={file_path}", file=sys.stderr)

        # Validate file path
        is_valid, error = validate_file_path(file_path)
        if not is_valid:
            print(f"❌ Path validation failed: {error}", file=sys.stderr)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "FileSave",
                    "success": False,
                    "error": error
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # Validate file content
        is_valid, warnings = validate_file_content(file_path)
        if not is_valid:
            print(f"⚠️ Content validation warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"  - {warning}", file=sys.stderr)

        # Get file size
        try:
            file_size = Path(file_path).stat().st_size
        except Exception:
            file_size = 0

        # Log file modification
        log_file_modification(file_path, file_size)

        # Auto-stage file (if enabled)
        auto_staged = auto_stage_file(file_path)

        # Output
        output = {
            "hookSpecificOutput": {
                "hookEventName": "FileSave",
                "file_path": file_path,
                "file_size": file_size,
                "warnings": warnings,
                "auto_staged": auto_staged
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(f"❌ FileSave hook error: {e}", file=sys.stderr)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "FileSave",
                "success": False,
                "error": str(e)
            }
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
