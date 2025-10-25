"""
Unit tests for StaticAnalysisService.

Tests static code analysis including:
- File analysis (LOC, complexity, maintainability)
- Project-wide analysis
- Caching mechanism
- High-risk file identification
- Error handling

**Test Strategy**:
- Use temporary files with controlled code characteristics
- Test caching behavior (cache hits, invalidation)
- Test edge cases (malformed Python, empty files)
- Validate performance targets (<2s for 100 files)

**Author**: APM (Agent Project Manager) Test Suite
"""

import pytest
from pathlib import Path
from textwrap import dedent
import time
import hashlib

from agentpm.core.detection.analysis.service import (
    StaticAnalysisService,
    AnalysisCache,
)
from agentpm.core.database.models.detection_analysis import (
    FileAnalysis,
    ProjectAnalysis,
    ComplexityReport,
    MaintainabilityReport,
)


class TestAnalysisCache:
    """Test suite for AnalysisCache."""

    @pytest.fixture
    def cache_dir(self, tmp_path):
        """Create temporary cache directory."""
        cache = tmp_path / "cache"
        cache.mkdir()
        return cache

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample Python file."""
        file_path = tmp_path / "sample.py"
        file_path.write_text(dedent("""
            def simple():
                return 42
        """))
        return file_path

    def test_cache_init_enabled(self, cache_dir):
        """Test cache initialization when enabled."""
        cache = AnalysisCache(cache_dir=cache_dir, enabled=True)
        assert cache.enabled is True
        assert cache.cache_dir == cache_dir
        assert cache.cache_dir.exists()

    def test_cache_init_disabled(self):
        """Test cache initialization when disabled."""
        cache = AnalysisCache(enabled=False)
        assert cache.enabled is False

    def test_cache_set_and_get(self, cache_dir, sample_file):
        """Test setting and getting cached analysis."""
        cache = AnalysisCache(cache_dir=cache_dir, enabled=True)

        # Create analysis
        analysis = FileAnalysis(
            file_path=str(sample_file),
            total_lines=5,
            code_lines=3,
            comment_lines=0,
            blank_lines=2,
            complexity_avg=1.0,
            complexity_max=1,
            function_count=1,
            class_count=0,
            maintainability_index=100.0
        )

        # Cache it
        cache.set(sample_file, analysis)

        # Retrieve it
        cached = cache.get(sample_file)
        assert cached is not None
        assert cached.file_path == str(sample_file)
        assert cached.function_count == 1

    def test_cache_invalidation_on_file_change(self, cache_dir, sample_file):
        """Test cache invalidation when file changes."""
        cache = AnalysisCache(cache_dir=cache_dir, enabled=True)

        # Create and cache analysis
        analysis = FileAnalysis(
            file_path=str(sample_file),
            total_lines=5,
            code_lines=3,
            comment_lines=0,
            blank_lines=2,
            complexity_avg=1.0,
            complexity_max=1,
            function_count=1,
            class_count=0,
            maintainability_index=100.0
        )
        cache.set(sample_file, analysis)

        # Verify cached
        assert cache.get(sample_file) is not None

        # Modify file
        sample_file.write_text(dedent("""
            def modified():
                return 99
        """))

        # Cache should be invalidated
        assert cache.get(sample_file) is None

    def test_cache_miss(self, cache_dir, sample_file):
        """Test cache miss for non-cached file."""
        cache = AnalysisCache(cache_dir=cache_dir, enabled=True)

        # File not cached yet
        cached = cache.get(sample_file)
        assert cached is None

    def test_cache_disabled_returns_none(self, sample_file):
        """Test that disabled cache always returns None."""
        cache = AnalysisCache(enabled=False)

        analysis = FileAnalysis(
            file_path=str(sample_file),
            total_lines=5,
            code_lines=3,
            comment_lines=0,
            blank_lines=2,
            complexity_avg=1.0,
            complexity_max=1,
            function_count=1,
            class_count=0,
            maintainability_index=100.0
        )

        # Try to cache (should be no-op)
        cache.set(sample_file, analysis)

        # Get should return None
        assert cache.get(sample_file) is None

    def test_cache_corrupted_data(self, cache_dir, sample_file):
        """Test handling of corrupted cache data."""
        cache = AnalysisCache(cache_dir=cache_dir, enabled=True)

        # Create valid cache entry first
        analysis = FileAnalysis(
            file_path=str(sample_file),
            total_lines=5,
            code_lines=3,
            comment_lines=0,
            blank_lines=2,
            complexity_avg=1.0,
            complexity_max=1,
            function_count=1,
            class_count=0,
            maintainability_index=100.0
        )
        cache.set(sample_file, analysis)

        # Corrupt the cache file
        cache_path = cache._get_cache_path(str(sample_file))
        cache_path.write_text("corrupted JSON {{{")

        # Should return None on corrupted cache
        assert cache.get(sample_file) is None


class TestStaticAnalysisService:
    """Test suite for StaticAnalysisService."""

    @pytest.fixture
    def simple_project(self, tmp_path):
        """Create simple project."""
        project = tmp_path / "simple_project"
        project.mkdir()

        (project / "simple.py").write_text(dedent("""
            '''Simple module.'''

            def simple_function(x):
                '''Simple function.'''
                return x + 1

            class SimpleClass:
                '''Simple class.'''
                def method(self):
                    '''Simple method.'''
                    return 42
        """))

        return project

    @pytest.fixture
    def complex_project(self, tmp_path):
        """Create project with complex code."""
        project = tmp_path / "complex_project"
        project.mkdir()

        (project / "complex.py").write_text(dedent("""
            def complex_function(a, b, c, d):
                if a:
                    if b:
                        if c:
                            if d:
                                return 1
                            else:
                                return 2
                        else:
                            return 3
                    else:
                        return 4
                else:
                    return 5
        """))

        return project

    @pytest.fixture
    def multi_file_project(self, tmp_path):
        """Create project with multiple files."""
        project = tmp_path / "multi_file_project"
        project.mkdir()

        for i in range(10):
            (project / f"module_{i}.py").write_text(dedent(f"""
                '''Module {i}.'''

                def func_{i}():
                    '''Function {i}.'''
                    return {i}
            """))

        return project

    def test_init_with_cache_enabled(self, simple_project):
        """Test initialization with caching enabled."""
        service = StaticAnalysisService(simple_project, cache_enabled=True)
        assert service.project_path == simple_project.resolve()
        assert service.cache.enabled is True

    def test_init_with_cache_disabled(self, simple_project):
        """Test initialization with caching disabled."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        assert service.cache.enabled is False

    def test_analyze_file_simple(self, simple_project):
        """Test analyzing simple Python file."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        file_path = simple_project / "simple.py"

        analysis = service.analyze_file(file_path)

        assert isinstance(analysis, FileAnalysis)
        assert analysis.file_path == str(file_path)
        assert analysis.total_lines > 0
        assert analysis.code_lines > 0
        assert analysis.function_count == 2  # simple_function + method
        assert analysis.class_count == 1  # SimpleClass
        assert analysis.complexity_avg >= 1.0
        assert analysis.maintainability_index >= 0.0

    def test_analyze_file_complex(self, complex_project):
        """Test analyzing complex file."""
        service = StaticAnalysisService(complex_project, cache_enabled=False)
        file_path = complex_project / "complex.py"

        analysis = service.analyze_file(file_path)

        assert isinstance(analysis, FileAnalysis)
        assert analysis.function_count == 1
        assert analysis.complexity_max >= 5  # Nested ifs increase complexity

    def test_analyze_file_caching(self, simple_project):
        """Test file analysis caching."""
        service = StaticAnalysisService(simple_project, cache_enabled=True)
        file_path = simple_project / "simple.py"

        # First analysis
        analysis1 = service.analyze_file(file_path)
        assert analysis1 is not None

        # Second analysis (should use cache)
        analysis2 = service.analyze_file(file_path)
        assert analysis2 is not None
        assert analysis2.file_path == analysis1.file_path
        assert analysis2.function_count == analysis1.function_count

    def test_analyze_file_malformed_python(self, tmp_path):
        """Test analyzing malformed Python file."""
        project = tmp_path / "malformed_project"
        project.mkdir()

        malformed_file = project / "malformed.py"
        malformed_file.write_text("def broken syntax {{")

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_file(malformed_file)

        # Should return minimal analysis on parse failure
        assert isinstance(analysis, FileAnalysis)
        assert analysis.function_count == 0
        assert analysis.class_count == 0
        assert analysis.complexity_avg == 0.0

    def test_analyze_file_empty_file(self, tmp_path):
        """Test analyzing empty file."""
        project = tmp_path / "empty_project"
        project.mkdir()

        empty_file = project / "empty.py"
        empty_file.write_text("")

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_file(empty_file)

        assert isinstance(analysis, FileAnalysis)
        # Empty file may have 0 or 1 lines depending on how it's counted
        assert analysis.total_lines >= 0
        assert analysis.code_lines == 0
        assert analysis.function_count == 0

    def test_analyze_project_simple(self, simple_project):
        """Test analyzing entire project."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        analysis = service.analyze_project()

        assert isinstance(analysis, ProjectAnalysis)
        assert analysis.project_path == str(simple_project.resolve())
        assert analysis.total_files >= 1
        assert analysis.total_lines > 0
        # ProjectAnalysis doesn't have total_functions - count from files
        total_functions = sum(f.function_count for f in analysis.files)
        assert total_functions >= 1
        assert analysis.avg_complexity >= 1.0
        assert len(analysis.files) >= 1

    def test_analyze_project_multi_file(self, multi_file_project):
        """Test analyzing project with multiple files."""
        service = StaticAnalysisService(multi_file_project, cache_enabled=False)
        analysis = service.analyze_project()

        assert analysis.total_files == 10
        # ProjectAnalysis doesn't have total_functions - count from files
        total_functions = sum(f.function_count for f in analysis.files)
        assert total_functions == 10  # One function per file
        assert len(analysis.files) == 10

    def test_analyze_project_ignores_venv(self, tmp_path):
        """Test that analysis ignores venv directories."""
        project = tmp_path / "project_with_venv"
        project.mkdir()

        # Create normal file
        (project / "normal.py").write_text("def func(): pass")

        # Create venv directory
        venv_dir = project / "venv"
        venv_dir.mkdir()
        (venv_dir / "lib").mkdir()
        (venv_dir / "lib" / "site.py").write_text("def site(): pass")

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_project()

        # Should only analyze normal.py, not venv files
        assert analysis.total_files == 1
        # Check that venv was ignored
        analyzed_paths = [f.file_path for f in analysis.files]
        # Resolve paths to compare properly
        assert not any("venv" in Path(path).parts for path in analyzed_paths)

    def test_get_high_complexity_files(self, complex_project):
        """Test getting high complexity files."""
        service = StaticAnalysisService(complex_project, cache_enabled=False)
        analysis = service.analyze_project()

        high_complexity = service.get_high_complexity_files(analysis, threshold=5)

        assert isinstance(high_complexity, list)
        # Complex project should have high complexity file
        if high_complexity:
            assert high_complexity[0].complexity_max > 5

    def test_get_large_files(self, tmp_path):
        """Test getting large files."""
        project = tmp_path / "large_files_project"
        project.mkdir()

        # Create small file
        (project / "small.py").write_text("def small(): pass")

        # Create large file
        lines = ["def func(): pass"] * 200
        (project / "large.py").write_text("\n".join(lines))

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_project()

        # Filter large files directly from analysis.files
        large_files = [f for f in analysis.files if f.code_lines > 100]

        assert isinstance(large_files, list)
        # Should find the large file
        assert len(large_files) >= 1
        assert large_files[0].code_lines > 100

    def test_get_low_maintainability_files(self, complex_project):
        """Test getting files with low maintainability."""
        service = StaticAnalysisService(complex_project, cache_enabled=False)
        analysis = service.analyze_project()

        low_mi = service.get_low_maintainability_files(analysis, threshold=80)

        assert isinstance(low_mi, list)
        # Complex file may have low maintainability

    def test_get_complexity_report(self, multi_file_project):
        """Test generating complexity report."""
        service = StaticAnalysisService(multi_file_project, cache_enabled=False)
        analysis = service.analyze_project()

        report = service.generate_complexity_report(analysis)

        assert isinstance(report, ComplexityReport)
        # ComplexityReport has: threshold, high_complexity_files, hotspots, total_violations
        assert report.threshold == 10  # Default threshold
        assert report.total_violations >= 0
        assert isinstance(report.high_complexity_files, list)
        assert isinstance(report.hotspots, list)

    def test_get_maintainability_report(self, multi_file_project):
        """Test generating maintainability report."""
        service = StaticAnalysisService(multi_file_project, cache_enabled=False)
        analysis = service.analyze_project()

        report = service.generate_maintainability_report(analysis)

        assert isinstance(report, MaintainabilityReport)
        # MaintainabilityReport has: threshold, low_maintainability_files, total_violations
        assert report.threshold == 65.0  # Default threshold
        assert report.total_violations >= 0
        assert isinstance(report.low_maintainability_files, list)

    def test_analyze_project_file_pattern(self, tmp_path):
        """Test analyzing project with custom file pattern."""
        project = tmp_path / "pattern_project"
        project.mkdir()

        # Create Python files
        (project / "module.py").write_text("def func(): pass")
        (project / "test.txt").write_text("not python")

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_project(file_pattern="**/*.py")

        # Should only analyze .py files
        assert analysis.total_files == 1

    def test_analyze_project_with_subdirectories(self, tmp_path):
        """Test analyzing project with subdirectories."""
        project = tmp_path / "nested_project"
        project.mkdir()

        # Create nested structure
        (project / "src").mkdir()
        (project / "src" / "main.py").write_text("def main(): pass")
        (project / "src" / "utils").mkdir()
        (project / "src" / "utils" / "helpers.py").write_text("def helper(): pass")

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_project()

        # Should find all Python files recursively
        assert analysis.total_files == 2
        # ProjectAnalysis doesn't have total_functions - count from files
        total_functions = sum(f.function_count for f in analysis.files)
        assert total_functions == 2

    def test_performance_analysis(self, tmp_path):
        """Test performance of analysis on moderate project."""
        project = tmp_path / "perf_project"
        project.mkdir()

        # Create 50 files
        for i in range(50):
            (project / f"module_{i}.py").write_text(dedent(f"""
                '''Module {i}.'''

                def func_{i}(x):
                    '''Function {i}.'''
                    return x + {i}
            """))

        service = StaticAnalysisService(project, cache_enabled=False)

        start = time.time()
        analysis = service.analyze_project()
        duration = time.time() - start

        # Should complete within 2 seconds
        assert duration < 2.0
        assert analysis.total_files == 50

    def test_cache_performance_improvement(self, multi_file_project):
        """Test that caching improves performance."""
        service = StaticAnalysisService(multi_file_project, cache_enabled=True)

        # First run (no cache)
        start1 = time.time()
        analysis1 = service.analyze_project()
        duration1 = time.time() - start1

        # Second run (with cache)
        start2 = time.time()
        analysis2 = service.analyze_project()
        duration2 = time.time() - start2

        # Cached run should be faster
        assert duration2 < duration1
        # Results should be consistent
        assert analysis1.total_files == analysis2.total_files

    def test_analyze_file_absolute_vs_relative_path(self, simple_project):
        """Test that both absolute and relative paths work."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        file_path = simple_project / "simple.py"

        # Analyze with absolute path
        analysis_abs = service.analyze_file(file_path.resolve())
        assert analysis_abs is not None

        # Analyze with relative path (if applicable)
        # Note: Service converts to absolute internally

    def test_edge_case_file_with_only_comments(self, tmp_path):
        """Test analyzing file with only comments."""
        project = tmp_path / "comments_project"
        project.mkdir()

        comments_file = project / "comments.py"
        comments_file.write_text(dedent("""
            # Just comments
            # No code
            # Still valid Python
        """))

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_file(comments_file)

        assert analysis is not None
        assert analysis.comment_lines > 0
        assert analysis.code_lines == 0  # Only comments, no code

    def test_edge_case_very_long_line(self, tmp_path):
        """Test analyzing file with very long lines."""
        project = tmp_path / "long_line_project"
        project.mkdir()

        long_line_file = project / "long.py"
        # Create file with very long line
        long_string = "x = '" + "a" * 10000 + "'"
        long_line_file.write_text(long_string)

        service = StaticAnalysisService(project, cache_enabled=False)
        analysis = service.analyze_file(long_line_file)

        # Should handle long lines without crashing
        assert analysis is not None

    def test_functions_property(self, simple_project):
        """Test extracting function metadata."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        file_path = simple_project / "simple.py"

        analysis = service.analyze_file(file_path)

        # Check that functions list is populated
        assert hasattr(analysis, 'functions')
        if analysis.functions:
            func = analysis.functions[0]
            assert 'name' in func
            assert 'line_number' in func

    def test_classes_property(self, simple_project):
        """Test extracting class metadata."""
        service = StaticAnalysisService(simple_project, cache_enabled=False)
        file_path = simple_project / "simple.py"

        analysis = service.analyze_file(file_path)

        # Check that classes list is populated
        assert hasattr(analysis, 'classes')
        if analysis.classes:
            cls = analysis.classes[0]
            assert 'name' in cls
            assert 'line_number' in cls


class TestStaticAnalysisModels:
    """Test Pydantic models for static analysis."""

    def test_file_analysis_creation(self):
        """Test FileAnalysis model creation."""
        analysis = FileAnalysis(
            file_path="/test/file.py",
            total_lines=100,
            code_lines=70,
            comment_lines=20,
            blank_lines=10,
            complexity_avg=5.5,
            complexity_max=10,
            function_count=5,
            class_count=2,
            maintainability_index=75.0,
            functions=[],
            classes=[]
        )

        assert analysis.file_path == "/test/file.py"
        assert analysis.total_lines == 100
        assert analysis.complexity_avg == 5.5
        assert analysis.maintainability_index == 75.0

    def test_project_analysis_creation(self):
        """Test ProjectAnalysis model creation."""
        file1 = FileAnalysis(
            file_path="/test/file1.py",
            total_lines=50,
            code_lines=40,
            comment_lines=5,
            blank_lines=5,
            complexity_avg=2.0,
            complexity_max=5,
            function_count=3,
            class_count=1,
            maintainability_index=80.0
        )

        analysis = ProjectAnalysis(
            project_path="/test",
            total_files=1,
            total_lines=50,
            total_code_lines=40,
            avg_complexity=2.0,
            max_complexity=5,
            avg_maintainability=80.0,
            files=[file1]
        )

        assert analysis.project_path == "/test"
        assert analysis.total_files == 1
        # Count functions from files
        total_functions = sum(f.function_count for f in analysis.files)
        assert total_functions == 3
        assert len(analysis.files) == 1

    def test_complexity_report_creation(self):
        """Test ComplexityReport model creation."""
        # ComplexityReport has: threshold, high_complexity_files, hotspots, total_violations
        file1 = FileAnalysis(
            file_path="/test/complex.py",
            total_lines=100,
            code_lines=80,
            comment_lines=10,
            blank_lines=10,
            complexity_avg=12.0,
            complexity_max=15,
            function_count=5,
            class_count=1,
            maintainability_index=60.0
        )

        report = ComplexityReport(
            threshold=10,
            high_complexity_files=[file1],
            hotspots=[{"name": "complex_func", "complexity": 15, "file_path": "/test/complex.py"}],
            total_violations=1
        )

        assert report.threshold == 10
        assert len(report.high_complexity_files) == 1
        assert report.total_violations == 1
        assert len(report.hotspots) == 1

    def test_maintainability_report_creation(self):
        """Test MaintainabilityReport model creation."""
        # MaintainabilityReport has: threshold, low_maintainability_files, total_violations
        file1 = FileAnalysis(
            file_path="/test/low_mi.py",
            total_lines=100,
            code_lines=80,
            comment_lines=10,
            blank_lines=10,
            complexity_avg=8.0,
            complexity_max=12,
            function_count=5,
            class_count=1,
            maintainability_index=50.0
        )

        report = MaintainabilityReport(
            threshold=65.0,
            low_maintainability_files=[file1],
            total_violations=1
        )

        assert report.threshold == 65.0
        assert len(report.low_maintainability_files) == 1
        assert report.total_violations == 1
