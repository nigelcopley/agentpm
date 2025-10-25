"""
Secure Command Execution Module for AIPM CLI

Provides secure patterns for executing external commands without shell injection risks.
"""

import subprocess
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .input_validator import InputValidator, SecurityError


class SecureCommandExecutor:
    """Secure command execution without shell injection vulnerabilities"""

    # Timeout limits for different command types
    DEFAULT_TIMEOUT = 30  # 30 seconds
    BUILD_TIMEOUT = 300   # 5 minutes
    TEST_TIMEOUT = 600    # 10 minutes

    # Safe environment variables to pass through
    SAFE_ENV_VARS = {
        'PATH', 'HOME', 'USER', 'PWD', 'LANG', 'LC_ALL',
        'PYTHONPATH', 'NODE_ENV', 'JAVA_HOME', 'GOPATH'
    }

    @classmethod
    def execute_build_command(
        cls,
        command: str,
        working_directory: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute build command securely without shell injection

        Args:
            command: Build command string to execute
            working_directory: Working directory for command execution
            timeout: Timeout in seconds (defaults to BUILD_TIMEOUT)

        Returns:
            Dict[str, Any]: Execution result with stdout, stderr, return code

        Raises:
            SecurityError: If command validation fails
            subprocess.TimeoutExpired: If command times out
        """
        # Validate and parse command
        command_list = InputValidator.validate_build_command(command)

        # Validate working directory
        if working_directory:
            work_dir = InputValidator.validate_file_path(working_directory, allow_absolute=True)
        else:
            work_dir = Path.cwd()

        # Ensure working directory exists and is accessible
        if not work_dir.exists():
            raise SecurityError(f"Working directory does not exist: {work_dir}")

        if not work_dir.is_dir():
            raise SecurityError(f"Working directory is not a directory: {work_dir}")

        # Create secure environment
        secure_env = cls._create_secure_environment()

        # Execute command safely
        start_time = datetime.utcnow()

        try:
            result = subprocess.run(
                command_list,  # Use list format - NO shell=True
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout or cls.BUILD_TIMEOUT,
                env=secure_env,
                check=False  # Don't raise on non-zero exit
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Sanitize output for safe logging/display
            stdout = cls._sanitize_output(result.stdout)
            stderr = cls._sanitize_output(result.stderr)

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time_seconds": execution_time,
                "working_directory": str(work_dir),
                "command_executed": command_list,  # Show what was actually executed
                "sanitized": True
            }

        except subprocess.TimeoutExpired as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {e.timeout} seconds",
                "execution_time_seconds": execution_time,
                "working_directory": str(work_dir),
                "command_executed": command_list,
                "error": "timeout"
            }

    @classmethod
    def execute_safe_command(
        cls,
        command_list: List[str],
        working_directory: Optional[Path] = None,
        timeout: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """
        Execute a pre-validated command list safely

        Args:
            command_list: Pre-validated command as list of strings
            working_directory: Working directory for execution
            timeout: Timeout in seconds

        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)

        Raises:
            SecurityError: If execution parameters are invalid
        """
        if not command_list or not isinstance(command_list, list):
            raise SecurityError("Command must be a non-empty list")

        # Validate working directory
        if working_directory:
            if not working_directory.exists() or not working_directory.is_dir():
                raise SecurityError(f"Invalid working directory: {working_directory}")
        else:
            working_directory = Path.cwd()

        # Create secure environment
        secure_env = cls._create_secure_environment()

        try:
            result = subprocess.run(
                command_list,
                cwd=str(working_directory),
                capture_output=True,
                text=True,
                timeout=timeout or cls.DEFAULT_TIMEOUT,
                env=secure_env,
                check=False
            )

            # Sanitize outputs
            stdout = cls._sanitize_output(result.stdout)
            stderr = cls._sanitize_output(result.stderr)

            return (result.returncode == 0, stdout, stderr)

        except subprocess.TimeoutExpired:
            return (False, "", "Command timed out")

    @classmethod
    def _create_secure_environment(cls) -> Dict[str, str]:
        """
        Create a secure environment for command execution

        Returns:
            Dict[str, str]: Sanitized environment variables
        """
        secure_env = {}

        # Only include safe environment variables
        for var_name in cls.SAFE_ENV_VARS:
            if var_name in os.environ:
                secure_env[var_name] = os.environ[var_name]

        # Set secure defaults
        secure_env['PS1'] = '$ '  # Simple prompt
        secure_env['IFS'] = ' \t\n'  # Standard field separators

        return secure_env

    @classmethod
    def _sanitize_output(cls, output: str) -> str:
        """
        Sanitize command output to remove sensitive information

        Args:
            output: Raw command output

        Returns:
            str: Sanitized output safe for logging/display
        """
        if not output:
            return ""

        sanitized = output

        # Remove potential sensitive patterns
        sensitive_patterns = [
            r'password[=:]\s*\S+',  # password=value
            r'token[=:]\s*\S+',     # token=value
            r'key[=:]\s*\S+',       # key=value
            r'secret[=:]\s*\S+',    # secret=value
            r'api_key[=:]\s*\S+',   # api_key=value
            r'--password\s+\S+',    # --password value
            r'--token\s+\S+',       # --token value
        ]

        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)

        # Limit output length
        max_output_length = 10000  # 10KB limit
        if len(sanitized) > max_output_length:
            sanitized = sanitized[:max_output_length] + "\n... [OUTPUT TRUNCATED] ..."

        return sanitized

    @classmethod
    def validate_command_safety(cls, command_list: List[str]) -> bool:
        """
        Validate that a command is safe to execute

        Args:
            command_list: Command as list of strings

        Returns:
            bool: True if command appears safe

        Raises:
            SecurityError: If command is deemed unsafe
        """
        if not command_list:
            raise SecurityError("Empty command")

        base_command = command_list[0]

        # Check for dangerous base commands
        dangerous_commands = {
            'rm', 'del', 'format', 'fdisk', 'dd', 'mkfs',
            'sudo', 'su', 'chmod', 'chown', 'passwd',
            'eval', 'exec', 'source', 'bash', 'sh',
            'curl', 'wget', 'nc', 'netcat', 'telnet'
        }

        if base_command.lower() in dangerous_commands:
            raise SecurityError(f"Dangerous command not allowed: {base_command}")

        # Check for dangerous argument patterns
        full_command = ' '.join(command_list)
        dangerous_patterns = [
            r'--password', r'--secret', r'--token',  # Credential arguments
            r'>\s*/dev/', r'>\s*/proc/',             # System file redirects
            r'\|\s*sudo', r'\|\s*su',                # Pipe to privilege escalation
            r'&&\s*rm', r';\s*rm',                   # Chained dangerous commands
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, full_command, re.IGNORECASE):
                raise SecurityError(f"Dangerous pattern detected: {pattern}")

        return True