"""
SHA-256 Integrity Checking System

Provides cryptographic hash verification for provider-generated files.
Enables detection of manual modifications and verification workflows.

This module supports the multi-provider configuration architecture by:
1. Computing SHA-256 hashes for file content
2. Verifying files against stored hashes
3. Batch verification for multiple files
4. Integration with FileOutput model

Pattern: Static utility class with cryptographic hash operations
Security: Uses hashlib.sha256 for content verification
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Union
from datetime import datetime, UTC

from agentpm.providers.base import FileOutput


class SHA256HashVerifier:
    """
    SHA-256 integrity verification for provider-generated files.

    Provides cryptographic hash generation and verification to detect
    manual modifications to provider configuration files.

    All methods are static to enable stateless verification operations.

    Example:
        >>> # Generate hash from content
        >>> hash_val = SHA256HashVerifier.generate_hash("file content")
        >>>
        >>> # Generate hash from file
        >>> hash_val = SHA256HashVerifier.generate_file_hash(Path("config.md"))
        >>>
        >>> # Verify file hasn't been modified
        >>> is_clean = SHA256HashVerifier.verify_file(
        ...     Path("config.md"),
        ...     expected_hash="abc123..."
        ... )
        >>>
        >>> # Batch verification
        >>> results = SHA256HashVerifier.verify_files([file1, file2])
    """

    # Chunk size for reading large files (4KB)
    CHUNK_SIZE = 4096

    @staticmethod
    def generate_hash(content: Union[str, bytes]) -> str:
        """
        Generate SHA-256 hash from content.

        Supports both string and bytes content for flexibility.
        Strings are automatically encoded to UTF-8.

        Args:
            content: Content to hash (str or bytes)

        Returns:
            Hexadecimal SHA-256 hash string (64 characters)

        Example:
            >>> hash_val = SHA256HashVerifier.generate_hash("hello world")
            >>> len(hash_val)
            64
            >>> hash_val == SHA256HashVerifier.generate_hash("hello world")
            True
        """
        if isinstance(content, str):
            content = content.encode('utf-8')

        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def generate_file_hash(file_path: Path) -> str:
        """
        Generate SHA-256 hash from file content.

        Reads file in chunks for memory efficiency with large files.
        Uses 4KB chunks by default for optimal performance.

        Args:
            file_path: Path to file to hash

        Returns:
            Hexadecimal SHA-256 hash string (64 characters)

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
            IOError: If file read fails

        Example:
            >>> hash_val = SHA256HashVerifier.generate_file_hash(
            ...     Path("/project/.claude/agents/developer.md")
            ... )
            >>> len(hash_val)
            64
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # Read file in chunks for memory efficiency
            while chunk := f.read(SHA256HashVerifier.CHUNK_SIZE):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    @staticmethod
    def verify_file(file_path: Path, expected_hash: str) -> bool:
        """
        Verify file matches expected hash.

        Computes current file hash and compares with expected value.
        Returns False if file is missing or hash doesn't match.

        Args:
            file_path: Path to file to verify
            expected_hash: Expected SHA-256 hash (64 hex chars)

        Returns:
            True if file exists and hash matches, False otherwise

        Example:
            >>> # File unchanged
            >>> SHA256HashVerifier.verify_file(
            ...     Path("config.md"),
            ...     "abc123..."
            ... )
            True

            >>> # File modified
            >>> SHA256HashVerifier.verify_file(
            ...     Path("config.md"),
            ...     "old_hash..."
            ... )
            False

            >>> # File missing
            >>> SHA256HashVerifier.verify_file(
            ...     Path("missing.md"),
            ...     "abc123..."
            ... )
            False
        """
        if not file_path.exists():
            return False

        try:
            current_hash = SHA256HashVerifier.generate_file_hash(file_path)
            return current_hash == expected_hash
        except (FileNotFoundError, PermissionError, IOError):
            # Handle read errors gracefully
            return False

    @staticmethod
    def verify_files(files: List[FileOutput]) -> Dict[Path, bool]:
        """
        Verify multiple files against stored hashes.

        Performs batch verification and returns modification status
        for each file. Useful for checking entire configuration sets.

        Args:
            files: List of FileOutput instances with stored hashes

        Returns:
            Dictionary mapping file paths to verification status
            - True: File exists and hash matches (unmodified)
            - False: File missing or modified (hash mismatch)

        Example:
            >>> results = SHA256HashVerifier.verify_files([
            ...     FileOutput(path=Path("CLAUDE.md"), content_hash="abc...", ...),
            ...     FileOutput(path=Path("settings.json"), content_hash="def...", ...)
            ... ])
            >>> results
            {Path('CLAUDE.md'): True, Path('settings.json'): False}

            >>> # Check for modifications
            >>> modified_files = [path for path, clean in results.items() if not clean]
            >>> if modified_files:
            ...     print(f"Modified files: {modified_files}")
        """
        results = {}

        for file_output in files:
            results[file_output.path] = SHA256HashVerifier.verify_file(
                file_output.path,
                file_output.content_hash
            )

        return results

    @classmethod
    def create_file_output(
        cls,
        path: Path,
        content: str
    ) -> FileOutput:
        """
        Create FileOutput with computed hash.

        Helper method to create FileOutput instances from content,
        automatically computing hash, size, and timestamp.

        This is the recommended way to create FileOutput instances
        when generating configuration files.

        Args:
            path: Absolute path to file
            content: File content (string)

        Returns:
            FileOutput instance with computed metadata

        Example:
            >>> output = SHA256HashVerifier.create_file_output(
            ...     Path("/project/.claude/agents/developer.md"),
            ...     "# Developer Agent\\n\\nSOP content..."
            ... )
            >>> output.path
            PosixPath('/project/.claude/agents/developer.md')
            >>> len(output.content_hash)
            64
            >>> output.size_bytes > 0
            True
        """
        content_bytes = content.encode('utf-8')

        return FileOutput(
            path=path,
            content_hash=cls.generate_hash(content_bytes),
            size_bytes=len(content_bytes),
            generated_at=datetime.now(UTC)
        )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "SHA256HashVerifier",
]
