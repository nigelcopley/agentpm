"""
Output Sanitization Module for AIPM CLI Security

Provides secure output handling to prevent information disclosure and ensure
safe display of potentially sensitive data.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class OutputSanitizer:
    """Sanitize outputs to prevent information disclosure"""

    # Sensitive patterns to redact from outputs
    SENSITIVE_PATTERNS = [
        # Credential patterns
        (r'password[=:]\s*["\']?([^"\'\s]+)["\']?', r'password=\*\*\*REDACTED\*\*\*'),
        (r'token[=:]\s*["\']?([^"\'\s]+)["\']?', r'token=\*\*\*REDACTED\*\*\*'),
        (r'key[=:]\s*["\']?([^"\'\s]+)["\']?', r'key=\*\*\*REDACTED\*\*\*'),
        (r'secret[=:]\s*["\']?([^"\'\s]+)["\']?', r'secret=\*\*\*REDACTED\*\*\*'),
        (r'api_key[=:]\s*["\']?([^"\'\s]+)["\']?', r'api_key=\*\*\*REDACTED\*\*\*'),

        # Command line credential arguments
        (r'--password\s+\S+', r'--password \*\*\*REDACTED\*\*\*'),
        (r'--token\s+\S+', r'--token \*\*\*REDACTED\*\*\*'),
        (r'--api-key\s+\S+', r'--api-key \*\*\*REDACTED\*\*\*'),

        # Database connection strings
        (r'://[^:]+:[^@]+@', r'://\*\*\*REDACTED\*\*\*:\*\*\*REDACTED\*\*\*@'),

        # File paths with usernames
        (r'/Users/([^/\s]+)/', r'/Users/\*\*\*USER\*\*\*/'),
        (r'/home/([^/\s]+)/', r'/home/\*\*\*USER\*\*\*/'),
        (r'C:\\Users\\([^\\]+)\\', r'C:\\Users\\\*\*\*USER\*\*\*\\'),

        # IP addresses (optional - may be needed for debugging)
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', r'\*\*\*IP\*\*\*'),

        # UUIDs and potential session IDs
        (r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', r'\*\*\*UUID\*\*\*'),
        (r'\b[A-Za-z0-9]{32,}\b', r'\*\*\*HASH\*\*\*'),
    ]

    # Path patterns to sanitize
    SENSITIVE_PATH_PATTERNS = [
        # System paths
        r'/etc/',
        r'/var/',
        r'/usr/',
        r'/root/',
        r'C:\\Windows\\',
        r'C:\\Program Files\\',
    ]

    @classmethod
    def sanitize_text(cls, text: str, redact_paths: bool = True) -> str:
        """
        Sanitize text output to remove sensitive information

        Args:
            text: Text to sanitize
            redact_paths: Whether to redact sensitive file paths

        Returns:
            str: Sanitized text safe for display/logging
        """
        if not text:
            return ""

        sanitized = text

        # Apply sensitive pattern replacements
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Redact sensitive paths if requested
        if redact_paths:
            for path_pattern in cls.SENSITIVE_PATH_PATTERNS:
                sanitized = re.sub(
                    path_pattern,
                    '***SYSTEM_PATH***/',
                    sanitized,
                    flags=re.IGNORECASE
                )

        return sanitized

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], redact_paths: bool = True) -> Dict[str, Any]:
        """
        Sanitize dictionary data recursively

        Args:
            data: Dictionary to sanitize
            redact_paths: Whether to redact sensitive file paths

        Returns:
            Dict[str, Any]: Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}

        for key, value in data.items():
            # Sanitize key
            sanitized_key = cls.sanitize_text(str(key), redact_paths)

            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[sanitized_key] = cls.sanitize_text(value, redact_paths)
            elif isinstance(value, dict):
                sanitized[sanitized_key] = cls.sanitize_dict(value, redact_paths)
            elif isinstance(value, list):
                sanitized[sanitized_key] = cls.sanitize_list(value, redact_paths)
            elif isinstance(value, Path):
                sanitized[sanitized_key] = cls.sanitize_path(value)
            else:
                # For other types (int, bool, etc.), keep as-is
                sanitized[sanitized_key] = value

        return sanitized

    @classmethod
    def sanitize_list(cls, data: List[Any], redact_paths: bool = True) -> List[Any]:
        """
        Sanitize list data recursively

        Args:
            data: List to sanitize
            redact_paths: Whether to redact sensitive file paths

        Returns:
            List[Any]: Sanitized list
        """
        if not isinstance(data, list):
            return data

        sanitized = []

        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_text(item, redact_paths))
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item, redact_paths))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item, redact_paths))
            elif isinstance(item, Path):
                sanitized.append(cls.sanitize_path(item))
            else:
                sanitized.append(item)

        return sanitized

    @classmethod
    def sanitize_path(cls, path: Union[str, Path]) -> str:
        """
        Sanitize file path to remove sensitive information

        Args:
            path: Path to sanitize

        Returns:
            str: Sanitized path safe for display
        """
        path_str = str(path)

        # Check if path contains sensitive directories
        for sensitive_pattern in cls.SENSITIVE_PATH_PATTERNS:
            if re.search(sensitive_pattern, path_str, re.IGNORECASE):
                # Replace with generic indicator
                return "***SYSTEM_PATH***"

        # Sanitize username in home directories
        path_str = re.sub(r'/Users/([^/]+)/', r'/Users/\*\*\*USER\*\*\*/', path_str)
        path_str = re.sub(r'/home/([^/]+)/', r'/home/\*\*\*USER\*\*\*/', path_str)
        path_str = re.sub(r'C:\\Users\\([^\\]+)\\', r'C:\\Users\\\*\*\*USER\*\*\*\\', path_str)

        return path_str

    @classmethod
    def sanitize_error_message(cls, error: Exception) -> str:
        """
        Sanitize error message to prevent information disclosure

        Args:
            error: Exception to sanitize

        Returns:
            str: Safe error message for display
        """
        error_msg = str(error)

        # Sanitize the error message
        sanitized_msg = cls.sanitize_text(error_msg)

        # Remove stack trace information that might leak paths
        sanitized_msg = re.sub(r'File "([^"]+)"', r'File "\*\*\*PATH\*\*\*"', sanitized_msg)
        sanitized_msg = re.sub(r'line \d+', r'line \*\*\*', sanitized_msg)

        return sanitized_msg

    @classmethod
    def sanitize_command_output(cls, stdout: str, stderr: str) -> tuple[str, str]:
        """
        Sanitize command output streams

        Args:
            stdout: Standard output to sanitize
            stderr: Standard error output to sanitize

        Returns:
            tuple[str, str]: Sanitized (stdout, stderr)
        """
        # Sanitize both streams
        clean_stdout = cls.sanitize_text(stdout, redact_paths=True)
        clean_stderr = cls.sanitize_text(stderr, redact_paths=True)

        # Additional sanitization for command outputs
        # Remove potential environment variable dumps
        clean_stdout = re.sub(r'^[A-Z_]+=.*$', r'\*\*\*ENV_VAR\*\*\*', clean_stdout, flags=re.MULTILINE)
        clean_stderr = re.sub(r'^[A-Z_]+=.*$', r'\*\*\*ENV_VAR\*\*\*', clean_stderr, flags=re.MULTILINE)

        return clean_stdout, clean_stderr

    @classmethod
    def create_safe_display_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a safe version of data for display to users

        Args:
            data: Original data dictionary

        Returns:
            Dict[str, Any]: Safe data for display
        """
        # Deep copy and sanitize
        safe_data = cls.sanitize_dict(data, redact_paths=True)

        # Add metadata about sanitization
        safe_data['_sanitized'] = True
        safe_data['_sanitization_note'] = "Sensitive information has been redacted for security"

        return safe_data

    @classmethod
    def truncate_large_output(cls, text: str, max_length: int = 5000) -> str:
        """
        Truncate large outputs to prevent overwhelming displays

        Args:
            text: Text to potentially truncate
            max_length: Maximum allowed length

        Returns:
            str: Truncated text if necessary
        """
        if len(text) <= max_length:
            return text

        # Truncate and add indicator
        truncated = text[:max_length]
        truncated += f"\n\n... [OUTPUT TRUNCATED - Original length: {len(text)} chars] ..."

        return truncated