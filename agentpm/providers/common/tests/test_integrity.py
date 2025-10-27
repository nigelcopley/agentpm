"""
Tests for SHA-256 Integrity Checking System

Validates cryptographic hash generation, file verification,
and batch verification workflows.

Test Coverage:
- Hash generation (deterministic, consistent)
- File hash computation (chunked reading)
- Single file verification (clean, modified, missing)
- Batch file verification
- FileOutput integration
- Edge cases (empty files, large files, unicode)
"""

import pytest
import hashlib
from pathlib import Path
from datetime import datetime
from agentpm.providers.common.integrity import SHA256HashVerifier
from agentpm.providers.base import FileOutput


class TestHashGeneration:
    """Test SHA-256 hash generation from content."""

    def test_generate_hash_from_string(self):
        """Hash generation from string content."""
        content = "hello world"
        hash_val = SHA256HashVerifier.generate_hash(content)

        # Verify hash format
        assert len(hash_val) == 64
        assert all(c in '0123456789abcdef' for c in hash_val)

        # Verify deterministic (same input = same hash)
        hash_val2 = SHA256HashVerifier.generate_hash(content)
        assert hash_val == hash_val2

    def test_generate_hash_from_bytes(self):
        """Hash generation from bytes content."""
        content = b"hello world"
        hash_val = SHA256HashVerifier.generate_hash(content)

        # Verify hash format
        assert len(hash_val) == 64
        assert all(c in '0123456789abcdef' for c in hash_val)

    def test_generate_hash_string_vs_bytes_equivalent(self):
        """String and bytes produce same hash."""
        content_str = "hello world"
        content_bytes = b"hello world"

        hash_str = SHA256HashVerifier.generate_hash(content_str)
        hash_bytes = SHA256HashVerifier.generate_hash(content_bytes)

        assert hash_str == hash_bytes

    def test_generate_hash_known_value(self):
        """Hash generation matches known SHA-256 value."""
        content = "hello world"
        # Known SHA-256 hash for "hello world"
        expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

        hash_val = SHA256HashVerifier.generate_hash(content)
        assert hash_val == expected_hash

    def test_generate_hash_empty_content(self):
        """Hash generation for empty content."""
        content = ""
        hash_val = SHA256HashVerifier.generate_hash(content)

        # Known SHA-256 hash for empty string
        expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_val == expected_hash

    def test_generate_hash_unicode_content(self):
        """Hash generation for unicode content."""
        content = "Hello 世界 🌍"
        hash_val = SHA256HashVerifier.generate_hash(content)

        # Verify hash format
        assert len(hash_val) == 64

        # Verify deterministic for unicode
        hash_val2 = SHA256HashVerifier.generate_hash(content)
        assert hash_val == hash_val2

    def test_generate_hash_different_content_different_hash(self):
        """Different content produces different hashes."""
        hash1 = SHA256HashVerifier.generate_hash("content1")
        hash2 = SHA256HashVerifier.generate_hash("content2")

        assert hash1 != hash2


class TestFileHashGeneration:
    """Test SHA-256 hash generation from files."""

    def test_generate_file_hash_simple(self, tmp_path):
        """Hash generation from file."""
        file_path = tmp_path / "test.txt"
        content = "hello world"
        file_path.write_text(content)

        hash_val = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify matches content hash
        expected_hash = SHA256HashVerifier.generate_hash(content)
        assert hash_val == expected_hash

    def test_generate_file_hash_binary_content(self, tmp_path):
        """Hash generation from binary file."""
        file_path = tmp_path / "test.bin"
        content = b"\x00\x01\x02\x03\xff\xfe\xfd"
        file_path.write_bytes(content)

        hash_val = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify matches content hash
        expected_hash = SHA256HashVerifier.generate_hash(content)
        assert hash_val == expected_hash

    def test_generate_file_hash_large_file(self, tmp_path):
        """Hash generation for large file (chunked reading)."""
        file_path = tmp_path / "large.txt"
        # Create 10MB file
        content = "a" * (10 * 1024 * 1024)
        file_path.write_text(content)

        hash_val = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify hash computed correctly
        expected_hash = SHA256HashVerifier.generate_hash(content)
        assert hash_val == expected_hash

    def test_generate_file_hash_empty_file(self, tmp_path):
        """Hash generation for empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        hash_val = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify matches empty content hash
        expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_val == expected_hash

    def test_generate_file_hash_missing_file(self, tmp_path):
        """Hash generation fails gracefully for missing file."""
        file_path = tmp_path / "missing.txt"

        with pytest.raises(FileNotFoundError):
            SHA256HashVerifier.generate_file_hash(file_path)

    def test_generate_file_hash_unicode_content(self, tmp_path):
        """Hash generation for unicode file content."""
        file_path = tmp_path / "unicode.txt"
        content = "Hello 世界 🌍"
        file_path.write_text(content, encoding='utf-8')

        hash_val = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify matches content hash
        expected_hash = SHA256HashVerifier.generate_hash(content)
        assert hash_val == expected_hash


class TestFileVerification:
    """Test single file verification."""

    def test_verify_file_clean(self, tmp_path):
        """Verification succeeds for unmodified file."""
        file_path = tmp_path / "test.txt"
        content = "original content"
        file_path.write_text(content)

        # Generate expected hash
        expected_hash = SHA256HashVerifier.generate_file_hash(file_path)

        # Verify file is clean
        is_clean = SHA256HashVerifier.verify_file(file_path, expected_hash)
        assert is_clean is True

    def test_verify_file_modified(self, tmp_path):
        """Verification fails for modified file."""
        file_path = tmp_path / "test.txt"
        original_content = "original content"
        file_path.write_text(original_content)

        # Generate hash for original
        expected_hash = SHA256HashVerifier.generate_file_hash(file_path)

        # Modify file
        modified_content = "modified content"
        file_path.write_text(modified_content)

        # Verify file is modified
        is_clean = SHA256HashVerifier.verify_file(file_path, expected_hash)
        assert is_clean is False

    def test_verify_file_missing(self, tmp_path):
        """Verification fails gracefully for missing file."""
        file_path = tmp_path / "missing.txt"
        expected_hash = "abc123def456"

        # Verify handles missing file
        is_clean = SHA256HashVerifier.verify_file(file_path, expected_hash)
        assert is_clean is False

    def test_verify_file_wrong_hash_format(self, tmp_path):
        """Verification fails for incorrect hash."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        # Use wrong hash
        wrong_hash = "0" * 64

        is_clean = SHA256HashVerifier.verify_file(file_path, wrong_hash)
        assert is_clean is False

    def test_verify_file_empty_file(self, tmp_path):
        """Verification works for empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        expected_hash = SHA256HashVerifier.generate_file_hash(file_path)

        is_clean = SHA256HashVerifier.verify_file(file_path, expected_hash)
        assert is_clean is True


class TestBatchVerification:
    """Test batch file verification."""

    def test_verify_files_all_clean(self, tmp_path):
        """Batch verification with all files clean."""
        # Create files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        # Create FileOutput instances
        files = [
            FileOutput(
                path=file1,
                content_hash=SHA256HashVerifier.generate_file_hash(file1),
                size_bytes=file1.stat().st_size,
                generated_at=datetime.utcnow()
            ),
            FileOutput(
                path=file2,
                content_hash=SHA256HashVerifier.generate_file_hash(file2),
                size_bytes=file2.stat().st_size,
                generated_at=datetime.utcnow()
            )
        ]

        # Verify all files
        results = SHA256HashVerifier.verify_files(files)

        assert results[file1] is True
        assert results[file2] is True
        assert len(results) == 2

    def test_verify_files_some_modified(self, tmp_path):
        """Batch verification with some files modified."""
        # Create files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        # Create FileOutput instances with original hashes
        files = [
            FileOutput(
                path=file1,
                content_hash=SHA256HashVerifier.generate_file_hash(file1),
                size_bytes=file1.stat().st_size,
                generated_at=datetime.utcnow()
            ),
            FileOutput(
                path=file2,
                content_hash=SHA256HashVerifier.generate_file_hash(file2),
                size_bytes=file2.stat().st_size,
                generated_at=datetime.utcnow()
            )
        ]

        # Modify file2
        file2.write_text("modified content")

        # Verify files
        results = SHA256HashVerifier.verify_files(files)

        assert results[file1] is True
        assert results[file2] is False
        assert len(results) == 2

    def test_verify_files_some_missing(self, tmp_path):
        """Batch verification with some files missing."""
        # Create only file1
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"  # Not created
        file1.write_text("content1")

        # Create FileOutput instances
        files = [
            FileOutput(
                path=file1,
                content_hash=SHA256HashVerifier.generate_file_hash(file1),
                size_bytes=file1.stat().st_size,
                generated_at=datetime.utcnow()
            ),
            FileOutput(
                path=file2,
                content_hash="abc123" * 10 + "abcd",  # 64 chars
                size_bytes=100,
                generated_at=datetime.utcnow()
            )
        ]

        # Verify files
        results = SHA256HashVerifier.verify_files(files)

        assert results[file1] is True
        assert results[file2] is False
        assert len(results) == 2

    def test_verify_files_empty_list(self):
        """Batch verification with empty file list."""
        results = SHA256HashVerifier.verify_files([])

        assert results == {}

    def test_verify_files_large_batch(self, tmp_path):
        """Batch verification with many files."""
        files = []
        num_files = 100

        # Create many files
        for i in range(num_files):
            file_path = tmp_path / f"file{i}.txt"
            file_path.write_text(f"content{i}")

            files.append(FileOutput(
                path=file_path,
                content_hash=SHA256HashVerifier.generate_file_hash(file_path),
                size_bytes=file_path.stat().st_size,
                generated_at=datetime.utcnow()
            ))

        # Verify all files
        results = SHA256HashVerifier.verify_files(files)

        assert len(results) == num_files
        assert all(results.values())  # All clean


class TestFileOutputIntegration:
    """Test integration with FileOutput model."""

    def test_create_file_output_basic(self, tmp_path):
        """Create FileOutput with computed hash."""
        file_path = tmp_path / "test.txt"
        content = "test content"

        output = SHA256HashVerifier.create_file_output(file_path, content)

        assert output.path == file_path
        assert len(output.content_hash) == 64
        assert output.size_bytes == len(content.encode('utf-8'))
        assert isinstance(output.generated_at, datetime)

    def test_create_file_output_hash_matches(self, tmp_path):
        """FileOutput hash matches content hash."""
        file_path = tmp_path / "test.txt"
        content = "test content"

        output = SHA256HashVerifier.create_file_output(file_path, content)
        expected_hash = SHA256HashVerifier.generate_hash(content)

        assert output.content_hash == expected_hash

    def test_create_file_output_unicode(self, tmp_path):
        """FileOutput creation with unicode content."""
        file_path = tmp_path / "unicode.txt"
        content = "Hello 世界 🌍"

        output = SHA256HashVerifier.create_file_output(file_path, content)

        assert output.content_hash == SHA256HashVerifier.generate_hash(content)
        assert output.size_bytes == len(content.encode('utf-8'))

    def test_create_file_output_empty_content(self, tmp_path):
        """FileOutput creation with empty content."""
        file_path = tmp_path / "empty.txt"
        content = ""

        output = SHA256HashVerifier.create_file_output(file_path, content)

        assert output.content_hash == SHA256HashVerifier.generate_hash(content)
        assert output.size_bytes == 0

    def test_create_file_output_large_content(self, tmp_path):
        """FileOutput creation with large content."""
        file_path = tmp_path / "large.txt"
        content = "a" * (1024 * 1024)  # 1MB

        output = SHA256HashVerifier.create_file_output(file_path, content)

        assert output.content_hash == SHA256HashVerifier.generate_hash(content)
        assert output.size_bytes == len(content.encode('utf-8'))

    def test_create_file_output_verification_roundtrip(self, tmp_path):
        """FileOutput creation and verification roundtrip."""
        file_path = tmp_path / "test.txt"
        content = "test content"

        # Create FileOutput
        output = SHA256HashVerifier.create_file_output(file_path, content)

        # Write content to file
        file_path.write_text(content)

        # Verify file matches FileOutput hash
        is_clean = SHA256HashVerifier.verify_file(file_path, output.content_hash)
        assert is_clean is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_hash_generation_consistency_across_calls(self):
        """Hash generation is consistent across multiple calls."""
        content = "test content"
        hashes = [SHA256HashVerifier.generate_hash(content) for _ in range(10)]

        # All hashes should be identical
        assert len(set(hashes)) == 1

    def test_file_hash_consistency_across_calls(self, tmp_path):
        """File hash generation is consistent across multiple calls."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test content")

        hashes = [SHA256HashVerifier.generate_file_hash(file_path) for _ in range(10)]

        # All hashes should be identical
        assert len(set(hashes)) == 1

    def test_verify_file_handles_permission_error(self, tmp_path):
        """Verification handles permission errors gracefully."""
        # This test is platform-specific and may not work on all systems
        # Skip on Windows where chmod doesn't work the same way
        import sys
        if sys.platform == "win32":
            pytest.skip("Permission test not applicable on Windows")

        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        expected_hash = SHA256HashVerifier.generate_file_hash(file_path)

        # Remove read permissions
        file_path.chmod(0o000)

        try:
            # Should return False, not raise exception
            is_clean = SHA256HashVerifier.verify_file(file_path, expected_hash)
            assert is_clean is False
        finally:
            # Restore permissions for cleanup
            file_path.chmod(0o644)

    def test_multiline_content_hashing(self):
        """Hash generation for multiline content."""
        content = """Line 1
Line 2
Line 3"""
        hash_val = SHA256HashVerifier.generate_hash(content)

        # Verify deterministic
        hash_val2 = SHA256HashVerifier.generate_hash(content)
        assert hash_val == hash_val2

    def test_content_with_special_characters(self):
        """Hash generation with special characters."""
        content = "Hello\n\t\r\0World"
        hash_val = SHA256HashVerifier.generate_hash(content)

        assert len(hash_val) == 64
        # Verify deterministic
        assert hash_val == SHA256HashVerifier.generate_hash(content)
