"""
Security utilities for AIPM CLI commands.

Provides path validation and content hashing to prevent security vulnerabilities.
"""

import hashlib
from pathlib import Path
from typing import Tuple


def validate_file_path(file_path: str, project_root: Path) -> Tuple[bool, str]:
    """
    Validate file path to prevent directory traversal attacks (SEC-001).

    Security checks:
    1. Reject paths containing '..' (directory traversal attempts)
    2. Reject absolute paths (must be relative to project root)
    3. Ensure resolved path stays within project root boundaries

    Args:
        file_path: File path to validate (should be relative)
        project_root: Project root directory path

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if path is safe, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Examples:
        >>> validate_file_path("docs/spec.md", Path("/project"))
        (True, "")

        >>> validate_file_path("../../etc/passwd", Path("/project"))
        (False, "Path contains '..' (directory traversal not allowed)")

        >>> validate_file_path("/etc/passwd", Path("/project"))
        (False, "Path must be relative to project root")
    """
    # Security Check 1: Reject paths with '..' (directory traversal)
    if '..' in file_path:
        return False, "Path contains '..' (directory traversal not allowed)"

    # Security Check 2: Reject absolute paths
    if file_path.startswith('/'):
        return False, "Path must be relative to project root"

    # Security Check 3: Ensure resolved path is within project root
    try:
        abs_path = (project_root / file_path).resolve()
        abs_path.relative_to(project_root.resolve())
        return True, ""
    except ValueError:
        return False, "Path escapes project root"
    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def calculate_content_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of file content (SEC-003).

    Computes cryptographic hash for file integrity verification and
    change detection. Uses SHA-256 algorithm for security and reliability.

    Args:
        file_path: Path to file to hash

    Returns:
        SHA-256 hex digest string (64 characters)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read

    Examples:
        >>> calculate_content_hash(Path("test.txt"))
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

    Notes:
        - Reads file in 4KB chunks to handle large files efficiently
        - Returns raw hex digest to fit within 64-character database constraint
        - Empty files produce consistent hash (SHA-256 of empty input)
    """
    sha256 = hashlib.sha256()

    # Read file in chunks to handle large files efficiently
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)

    return sha256.hexdigest()


def validate_and_hash_file(file_path: str, project_root: Path) -> Tuple[bool, str, int, str]:
    """
    Combined security validation and content hashing operation.

    Convenience function that validates file path security and calculates
    file metadata (size and content hash) in a single operation.

    Args:
        file_path: Relative file path to validate
        project_root: Project root directory

    Returns:
        Tuple of (is_valid, error_message, file_size, content_hash)
        - is_valid: True if path is safe and file is readable
        - error_message: Empty if valid, error description if invalid
        - file_size: Size in bytes (0 if invalid)
        - content_hash: SHA-256 hash (empty string if invalid)

    Examples:
        >>> validate_and_hash_file("docs/spec.md", Path("/project"))
        (True, "", 1024, "sha256:abc123...")

        >>> validate_and_hash_file("../../etc/passwd", Path("/project"))
        (False, "Path contains '..'...", 0, "")
    """
    # Step 1: Validate path security
    is_valid, error_msg = validate_file_path(file_path, project_root)
    if not is_valid:
        return False, error_msg, 0, ""

    # Step 2: Get file metadata
    try:
        abs_path = project_root / file_path

        # Check file exists
        if not abs_path.exists():
            return False, f"File not found: {file_path}", 0, ""

        # Check it's a file (not directory)
        if not abs_path.is_file():
            return False, f"Path is not a file: {file_path}", 0, ""

        # Get file size
        file_size = abs_path.stat().st_size

        # Calculate content hash
        content_hash = calculate_content_hash(abs_path)

        return True, "", file_size, content_hash

    except PermissionError:
        return False, f"Permission denied reading file: {file_path}", 0, ""
    except Exception as e:
        return False, f"Error processing file: {str(e)}", 0, ""
