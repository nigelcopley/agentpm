"""
Input Validation Module for AIPM CLI Security

Provides comprehensive input validation to prevent injection attacks,
path traversal, and other security vulnerabilities.
"""

import re
import shlex
from pathlib import Path
from typing import List, Optional, Dict, Any


class SecurityError(Exception):
    """Security-related validation error"""
    pass


class InputValidator:
    """Centralized input validation for AIPM CLI security"""

    # Allowed characters for project names
    PROJECT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    MAX_PROJECT_NAME_LENGTH = 100

    # Allowed characters for general text inputs
    SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?]+$')
    MAX_TEXT_LENGTH = 1000

    # Dangerous command patterns to block
    DANGEROUS_PATTERNS = [
        r'[;&|`$()]',  # Shell metacharacters
        r'\.\./|\.\.\/',  # Path traversal
        r'rm\s+-rf',  # Dangerous rm commands
        r'sudo\s+',  # Privilege escalation
        r'eval\s*\(',  # Code evaluation
        r'exec\s*\(',  # Code execution
        r'import\s+os',  # OS module imports
        r'subprocess\.',  # Subprocess calls
        r'__import__',  # Dynamic imports
    ]

    # Safe build commands whitelist
    SAFE_BUILD_COMMANDS = {
        'python': ['python', 'python3'],
        'npm': ['npm'],
        'make': ['make'],
        'mvn': ['mvn'],
        'gradle': ['gradle'],
        'cargo': ['cargo'],
        'go': ['go'],
        'echo': ['echo'],  # For testing
        'pytest': ['pytest'],
    }

    @classmethod
    def validate_project_name(cls, name: Optional[str]) -> str:
        """
        Validate project name format and content

        Args:
            name: Project name to validate

        Returns:
            str: Validated project name

        Raises:
            SecurityError: If validation fails
        """
        if not name:
            raise SecurityError("Project name is required")

        if len(name) > cls.MAX_PROJECT_NAME_LENGTH:
            raise SecurityError(f"Project name must be {cls.MAX_PROJECT_NAME_LENGTH} characters or less")

        if not cls.PROJECT_NAME_PATTERN.match(name):
            raise SecurityError("Project name can only contain letters, numbers, hyphens, and underscores")

        # Additional checks for reserved names
        reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'lpt1', 'lpt2'}
        if name.lower() in reserved_names:
            raise SecurityError(f"'{name}' is a reserved name and cannot be used")

        return name

    @classmethod
    def validate_file_path(cls, path_input: Optional[str], allow_absolute: bool = False) -> Path:
        """
        Validate file paths against traversal attacks

        Args:
            path_input: Path string to validate
            allow_absolute: Whether to allow absolute paths

        Returns:
            Path: Validated path object

        Raises:
            SecurityError: If validation fails
        """
        if not path_input:
            raise SecurityError("Path is required")

        try:
            # Convert to Path object
            path = Path(path_input)

            # Check for path traversal attempts
            if '..' in path.parts:
                raise SecurityError("Path traversal (..) is not allowed")

            # Check for absolute paths if not allowed
            if not allow_absolute and path.is_absolute():
                raise SecurityError("Absolute paths are not allowed")

            # Resolve path safely
            if allow_absolute:
                resolved_path = path.resolve()
            else:
                # Resolve relative to current working directory
                resolved_path = (Path.cwd() / path).resolve()

                # Ensure resolved path is still within current directory tree
                try:
                    resolved_path.relative_to(Path.cwd())
                except ValueError:
                    raise SecurityError("Path resolves outside allowed directory")

            return resolved_path

        except (OSError, ValueError) as e:
            raise SecurityError(f"Invalid path: {e}")

    @classmethod
    def validate_text_input(cls, text: Optional[str], max_length: Optional[int] = None) -> str:
        """
        Validate general text inputs

        Args:
            text: Text to validate
            max_length: Maximum allowed length (defaults to MAX_TEXT_LENGTH)

        Returns:
            str: Validated text

        Raises:
            SecurityError: If validation fails
        """
        if not text:
            raise SecurityError("Text input is required")

        max_len = max_length or cls.MAX_TEXT_LENGTH
        if len(text) > max_len:
            raise SecurityError(f"Text input must be {max_len} characters or less")

        # Check for potentially dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise SecurityError("Text contains potentially dangerous content")

        return text.strip()

    @classmethod
    def validate_build_command(cls, command: Optional[str]) -> List[str]:
        """
        Validate and parse build command safely

        Args:
            command: Build command string to validate

        Returns:
            List[str]: Validated command as list of arguments

        Raises:
            SecurityError: If validation fails
        """
        if not command:
            raise SecurityError("Build command is required")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError(f"Build command contains dangerous pattern: {pattern}")

        try:
            # Parse command safely using shlex
            parsed_command = shlex.split(command)
        except ValueError as e:
            raise SecurityError(f"Invalid command syntax: {e}")

        if not parsed_command:
            raise SecurityError("Empty command after parsing")

        # Validate command is in whitelist
        base_command = parsed_command[0].lower()

        # Check if base command is in our safe commands
        command_allowed = False
        for cmd_family, allowed_commands in cls.SAFE_BUILD_COMMANDS.items():
            if any(base_command.endswith(allowed_cmd) for allowed_cmd in allowed_commands):
                command_allowed = True
                break

        # Also allow direct command names
        if base_command in ['echo', 'python', 'python3', 'npm', 'make', 'mvn', 'gradle', 'cargo', 'go', 'pytest']:
            command_allowed = True

        if not command_allowed:
            raise SecurityError(f"Command '{base_command}' is not in the allowed commands list")

        # Additional validation for specific command patterns
        if len(parsed_command) > 10:  # Reasonable limit on command complexity
            raise SecurityError("Command is too complex (too many arguments)")

        return parsed_command

    @classmethod
    def validate_command_args(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all command arguments

        Args:
            args: Dictionary of command arguments to validate

        Returns:
            Dict[str, Any]: Validated arguments

        Raises:
            SecurityError: If validation fails
        """
        validated_args = {}

        for key, value in args.items():
            if value is None:
                continue

            # Validate key name
            if not isinstance(key, str) or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                raise SecurityError(f"Invalid argument name: {key}")

            # Validate value based on type and key
            if isinstance(value, str):
                if 'path' in key.lower():
                    validated_args[key] = str(cls.validate_file_path(value))
                elif 'name' in key.lower():
                    validated_args[key] = cls.validate_text_input(value, 100)
                elif 'command' in key.lower():
                    # Special handling for commands - convert to list
                    validated_args[key] = cls.validate_build_command(value)
                else:
                    validated_args[key] = cls.validate_text_input(value)
            elif isinstance(value, (int, float, bool)):
                # Numeric and boolean values are generally safe
                validated_args[key] = value
            elif isinstance(value, list):
                # Validate each item in list
                validated_list = []
                for item in value:
                    if isinstance(item, str):
                        validated_list.append(cls.validate_text_input(item))
                    else:
                        validated_list.append(item)
                validated_args[key] = validated_list
            else:
                raise SecurityError(f"Unsupported argument type for {key}: {type(value)}")

        return validated_args

    @classmethod
    def sanitize_for_display(cls, text: str) -> str:
        """
        Sanitize text for safe display (remove potential XSS, etc.)

        Args:
            text: Text to sanitize

        Returns:
            str: Sanitized text safe for display
        """
        if not text:
            return ""

        # Remove potential script tags and other dangerous content
        dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<link', '<meta']
        sanitized = text

        for tag in dangerous_tags:
            sanitized = re.sub(tag, f'&lt;{tag[1:]}', sanitized, flags=re.IGNORECASE)

        # Limit length for display
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."

        return sanitized