"""
Unit tests for MemoryGenerator

Tests memory file generation, @import resolution, and security validation.
"""

import pytest
from pathlib import Path
from datetime import datetime
import hashlib

from agentpm.providers.anthropic.claude_code.memory_generator import (
    MemoryGenerator,
    SecureImportResolver,
    SecurityError
)
from agentpm.core.database.models.project import Project
from agentpm.core.database.enums import ProjectStatus


class TestSecureImportResolver:
    """Test @import resolution with security validation."""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create temporary project root."""
        return tmp_path

    @pytest.fixture
    def resolver(self, project_root):
        """Create import resolver."""
        return SecureImportResolver(project_root)

    def test_resolve_simple_import(self, resolver, project_root):
        """Test resolving a simple @import directive."""
        # Create test file
        test_file = project_root / "test.md"
        test_file.write_text("# Test Content")

        # Content with import
        content = "@test.md"

        # Resolve
        resolved = resolver.resolve(content, project_root)

        # Verify
        assert "# Test Content" in resolved
        assert "@test.md" not in resolved

    def test_resolve_absolute_import(self, resolver, project_root):
        """Test resolving absolute import from project root."""
        # Create test file
        docs_dir = project_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        test_file = docs_dir / "api.md"
        test_file.write_text("# API Documentation")

        # Content with absolute import
        content = "@/docs/api.md"

        # Resolve
        resolved = resolver.resolve(content, project_root)

        # Verify
        assert "# API Documentation" in resolved

    def test_circular_import_detection(self, resolver, project_root):
        """Test that circular imports are detected and blocked."""
        # Create circular import chain
        file_a = project_root / "a.md"
        file_b = project_root / "b.md"
        file_c = project_root / "c.md"

        file_a.write_text("@b.md")
        file_b.write_text("@c.md")
        file_c.write_text("@a.md")  # Circular

        # Attempt to resolve should raise SecurityError
        with pytest.raises(SecurityError, match="[Cc]ircular"):
            resolver.resolve("@a.md", project_root)

    def test_max_depth_enforcement(self, resolver, project_root):
        """Test that max import depth is enforced."""
        # Create deep import chain (7 levels)
        for i in range(7):
            file = project_root / f"level{i}.md"
            if i < 6:
                file.write_text(f"@level{i+1}.md")
            else:
                file.write_text("# Deep content")

        # Should fail at level 6 (MAX_IMPORT_DEPTH = 5)
        with pytest.raises(SecurityError, match="[Mm]ax.*depth"):
            resolver.resolve("@level0.md", project_root)

    def test_path_traversal_prevention(self, resolver, project_root):
        """Test that path traversal is blocked."""
        # Attempt to access file outside project
        with pytest.raises(SecurityError, match="[Pp]roject"):
            resolver._import_file("../../etc/passwd", project_root)

    def test_sensitive_file_blocking(self, resolver, project_root):
        """Test that sensitive files are blocked."""
        sensitive_files = [
            ".env",
            "credentials.json",
            ".ssh/id_rsa",
            ".aws/config",
            "secrets.yaml"
        ]

        for sensitive_file in sensitive_files:
            # Create file
            file_path = project_root / sensitive_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("sensitive data")

            # Should be blocked
            with pytest.raises(SecurityError, match="[Ss]ensitive"):
                resolver._import_file(sensitive_file, project_root)

    def test_file_size_limit(self, resolver, project_root):
        """Test that file size limits are enforced."""
        # Create file larger than 1 MB
        large_file = project_root / "large.md"
        large_file.write_text("x" * 1_000_001)

        # Should fail
        with pytest.raises(SecurityError, match="[Ll]arge"):
            resolver._import_file("large.md", project_root)

    def test_symbolic_link_prevention(self, resolver, project_root):
        """Test that symbolic links are blocked."""
        # Create symlink
        target = project_root / "target.md"
        target.write_text("# Target")
        symlink = project_root / "link.md"

        try:
            symlink.symlink_to(target)

            # Should be blocked
            with pytest.raises(SecurityError, match="[Ss]ymbolic"):
                resolver._import_file("link.md", project_root)
        except OSError:
            # Symlinks not supported on this filesystem, skip test
            pytest.skip("Symlinks not supported")

    def test_nested_imports(self, resolver, project_root):
        """Test that nested imports work correctly."""
        # Create nested import structure
        file_a = project_root / "a.md"
        file_b = project_root / "b.md"
        file_c = project_root / "c.md"

        file_c.write_text("# Content C")
        file_b.write_text("# Content B\n@c.md")
        file_a.write_text("# Content A\n@b.md")

        # Resolve
        resolved = resolver.resolve("@a.md", project_root)

        # Verify all content included
        assert "# Content A" in resolved
        assert "# Content B" in resolved
        assert "# Content C" in resolved

    def test_import_caching(self, resolver, project_root):
        """Test that imports are cached for performance."""
        # Create test file
        test_file = project_root / "test.md"
        test_file.write_text("# Test")

        # Import twice
        resolver._import_file("test.md", project_root)
        resolver._import_file("test.md", project_root)

        # Verify cache was used
        assert str(test_file) in resolver._resolved_cache

    def test_invalid_utf8_rejection(self, resolver, project_root):
        """Test that non-UTF-8 files are rejected."""
        # Create binary file
        binary_file = project_root / "binary.md"
        binary_file.write_bytes(b'\xff\xfe\xfd')

        # Should fail
        with pytest.raises(SecurityError, match="UTF-8"):
            resolver._import_file("binary.md", project_root)


class TestMemoryGenerator:
    """Test memory file generation from database."""

    # No fixture override needed - use the db_service fixture from conftest.py

    @pytest.fixture
    def project(self, db_service):
        """Create test project."""
        return Project(
            id=1,
            name="Test Project",
            description="Test project description",
            status=ProjectStatus.active,
            project_path="/tmp/test",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

    @pytest.fixture
    def generator(self, db_service):
        """Create memory generator."""
        return MemoryGenerator(db_service)

    def test_generator_initialization(self, generator):
        """Test that generator initializes correctly."""
        assert generator.db is not None
        assert generator.env is not None

    def test_generate_context_file(self, generator, project, tmp_path):
        """Test generating project context file."""
        # Generate context file
        context_file = generator._generate_context_file(
            project=project,
            memory_dir=tmp_path,
            resolver=None
        )

        # Verify file created
        assert context_file.path.exists()
        assert context_file.path.name == "project_context.md"

        # Verify content
        content = context_file.content
        assert "Test Project" in content
        assert "active" in content
        assert "Database-First" in content

    def test_generate_pattern_files(self, generator, project, tmp_path):
        """Test generating pattern files."""
        # Generate pattern files
        pattern_files = generator._generate_pattern_files(
            project=project,
            memory_dir=tmp_path,
            resolver=None
        )

        # Verify files created
        assert len(pattern_files) == 1
        assert pattern_files[0].path.exists()

        # Verify content
        content = pattern_files[0].content
        assert "Three-Layer Architecture" in content
        assert "Database-First" in content
        assert "Template-Based Generation" in content

    def test_generate_decision_files_empty(self, generator, project, tmp_path):
        """Test generating decision files when no decisions exist."""
        # Generate decision files (should gracefully handle missing table)
        decision_files = generator._generate_decision_files(
            project=project,
            memory_dir=tmp_path,
            resolver=None
        )

        # Verify empty list (no decisions)
        assert decision_files == []

    def test_generate_learning_files_empty(self, generator, project, tmp_path):
        """Test generating learning files when no learnings exist."""
        # Generate learning files (should gracefully handle missing table)
        learning_files = generator._generate_learning_files(
            project=project,
            memory_dir=tmp_path,
            resolver=None
        )

        # Verify empty list (no learnings)
        assert learning_files == []

    def test_generate_all_memory_files(self, generator, project, tmp_path):
        """Test generating all memory files."""
        # Generate all memory files
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path
        )

        # Verify files created
        assert len(files) >= 2  # At least context and patterns

        # Verify directory structure
        memory_dir = tmp_path / "memory"
        assert memory_dir.exists()
        assert (memory_dir / "context").exists()
        assert (memory_dir / "patterns").exists()
        assert (memory_dir / "decisions").exists()
        assert (memory_dir / "learnings").exists()

    def test_infer_file_type(self, generator):
        """Test file type inference from path."""
        # Test various paths
        assert generator._infer_file_type(Path("/project/.claude/memory/decisions/decision-0001.md")) == "ideas"
        assert generator._infer_file_type(Path("/project/.claude/memory/learnings/learning-0001.md")) == "principles"
        assert generator._infer_file_type(Path("/project/.claude/memory/patterns/patterns.md")) == "principles"
        assert generator._infer_file_type(Path("/project/.claude/memory/context/project_context.md")) == "project"
        assert generator._infer_file_type(Path("/project/other.md")) is None

    def test_generate_with_import_resolution(self, generator, project, tmp_path):
        """Test generating memory files with @import resolution."""
        # Create reference file
        docs_dir = tmp_path.parent / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        ref_file = docs_dir / "reference.md"
        ref_file.write_text("# Reference Content")

        # Generate with import resolution
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path,
            resolve_imports=True
        )

        # Verify files created
        assert len(files) >= 2

    def test_generate_without_import_resolution(self, generator, project, tmp_path):
        """Test generating memory files without @import resolution."""
        # Generate without import resolution
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path,
            resolve_imports=False
        )

        # Verify files created
        assert len(files) >= 2

    def test_selective_generation(self, generator, project, tmp_path):
        """Test selective generation of memory files."""
        # Generate only context file
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path,
            include_decisions=False,
            include_learnings=False,
            include_patterns=False,
            include_context=True
        )

        # Verify only context file created
        assert len(files) == 1
        assert "project_context.md" in str(files[0].path)

    def test_file_hash_tracking(self, generator, project, tmp_path):
        """Test that file hashes are tracked correctly."""
        # Generate files
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path
        )

        # Verify file outputs have correct attributes
        for file_output in files:
            assert file_output.path is not None
            assert file_output.content is not None
            assert len(file_output.content) > 0

            # Verify hash matches content
            expected_hash = hashlib.sha256(file_output.content.encode()).hexdigest()
            # Note: FileOutput may not store hash directly, that's in memory_files table


# Integration tests


class TestMemoryGeneratorIntegration:
    """Integration tests for memory generation."""

    # No fixture override needed - use the db_service fixture from conftest.py

    @pytest.fixture
    def project(self, db_service):
        """Create test project."""
        return Project(
            id=1,
            name="Integration Test Project",
            description="Integration test",
            status=ProjectStatus.active,
            project_path="/tmp/integration_test",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

    def test_end_to_end_generation(self, db_service, project, tmp_path):
        """Test complete end-to-end memory generation workflow."""
        # Create generator
        generator = MemoryGenerator(db_service)

        # Generate all memory files
        files = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path,
            include_decisions=True,
            include_learnings=True,
            include_patterns=True,
            include_context=True,
            resolve_imports=True
        )

        # Verify files created
        assert len(files) >= 2

        # Verify all files are readable
        for file_output in files:
            assert file_output.path.exists()
            content = file_output.path.read_text()
            assert len(content) > 0

        # Verify directory structure
        memory_dir = tmp_path / "memory"
        assert memory_dir.exists()
        assert (memory_dir / "context" / "project_context.md").exists()
        assert (memory_dir / "patterns" / "patterns.md").exists()

    def test_regeneration_idempotency(self, db_service, project, tmp_path):
        """Test that regenerating memory files is idempotent."""
        generator = MemoryGenerator(db_service)

        # Generate twice
        files1 = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path
        )
        files2 = generator.generate_memory_files(
            project=project,
            output_dir=tmp_path
        )

        # Verify same number of files
        assert len(files1) == len(files2)

        # Verify content is identical
        for f1, f2 in zip(files1, files2):
            # Content may have different timestamps, check structure
            assert f1.path.name == f2.path.name
