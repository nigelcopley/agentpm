"""
Comprehensive tests for Code Metrics Calculator module.

Tests all functions with:
- Unit tests for each function
- Edge cases and error handling
- Performance constraints validation
- Security constraints validation
- Example code from docstrings

Target: >90% test coverage
"""

import ast
import math
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from agentpm.utils.metrics_calculator import (
    count_lines,
    calculate_cyclomatic_complexity,
    calculate_maintainability_index,
    aggregate_file_metrics,
    calculate_radon_metrics,
    calculate_size_metrics,
    mi_rank,
    MAX_FILE_SIZE,
    RADON_AVAILABLE
)


class TestCountLines:
    """Tests for count_lines function"""

    def test_count_simple_file(self, tmp_path: Path):
        """Test counting lines in simple Python file"""
        # Arrange
        test_file = tmp_path / "simple.py"
        code = """def foo():
    return 42

print(foo())
"""
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['total_lines'] == 5
        assert counts['code_lines'] == 3
        assert counts['blank_lines'] >= 1  # May vary slightly

    def test_count_file_with_comments(self, tmp_path: Path):
        """Test counting file with single-line comments"""
        # Arrange
        test_file = tmp_path / "comments.py"
        code = """# This is a comment
def foo():
    # Another comment
    return 42
"""
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['comment_lines'] == 2
        assert counts['code_lines'] == 2

    def test_count_file_with_docstrings(self, tmp_path: Path):
        """Test counting file with module docstring"""
        # Arrange
        test_file = tmp_path / "docstring.py"
        code = '''"""
This is a module docstring.
It spans multiple lines.
"""

def foo():
    """Function docstring"""
    return 42
'''
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['docstring_lines'] >= 1  # At least module or function docstrings

    def test_count_file_with_multiline_strings(self, tmp_path: Path):
        """Test counting file with multi-line strings"""
        # Arrange
        test_file = tmp_path / "multiline.py"
        code = '''
text = """
This is a
multi-line string
"""

def foo():
    return text
'''
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['total_lines'] > 0
        assert counts['code_lines'] > 0

    def test_count_empty_file(self, tmp_path: Path):
        """Test counting empty file"""
        # Arrange
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['total_lines'] == 1
        assert counts['code_lines'] == 0
        assert counts['blank_lines'] == 1

    def test_count_blank_lines(self, tmp_path: Path):
        """Test counting blank lines"""
        # Arrange
        test_file = tmp_path / "blanks.py"
        code = """
def foo():
    pass


def bar():
    pass
"""
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['blank_lines'] >= 2

    def test_count_mixed_line_types(self, tmp_path: Path):
        """Test file with all line types"""
        # Arrange
        test_file = tmp_path / "mixed.py"
        code = '''"""Module docstring"""
# Comment
import os

def foo():
    """Function docstring"""
    # Inline comment
    x = 42  # Code with comment
    return x

'''
        test_file.write_text(code)

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['total_lines'] == len(code.split('\n'))
        assert counts['code_lines'] > 0
        assert counts['comment_lines'] > 0
        assert counts['blank_lines'] > 0
        assert counts['docstring_lines'] > 0

    def test_file_not_found_raises_error(self, tmp_path: Path):
        """Test that missing file raises FileNotFoundError"""
        # Arrange
        nonexistent = tmp_path / "nonexistent.py"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            count_lines(nonexistent)

    def test_file_too_large_raises_error(self, tmp_path: Path):
        """Test that files >10MB raise ValueError"""
        # Arrange
        large_file = tmp_path / "huge.py"
        # Create file larger than MAX_FILE_SIZE (10MB)
        # Each line is ~11 bytes, so need (10MB / 11) + buffer lines
        huge_content = "# Comment\n" * ((MAX_FILE_SIZE // 11) + 100000)
        large_file.write_text(huge_content)

        # Act & Assert
        with pytest.raises(ValueError, match="File too large"):
            count_lines(large_file)

    def test_unicode_file_handling(self, tmp_path: Path):
        """Test handling of Unicode characters"""
        # Arrange
        test_file = tmp_path / "unicode.py"
        code = """# Пример кода
def hello():
    return "Привет мир"
"""
        test_file.write_text(code, encoding='utf-8')

        # Act
        counts = count_lines(test_file)

        # Assert
        assert counts['total_lines'] == 4
        assert counts['code_lines'] == 2


class TestCalculateCyclomaticComplexity:
    """Tests for calculate_cyclomatic_complexity function"""

    def test_simple_function_complexity_is_one(self):
        """Test that simple function has complexity of 1"""
        # Arrange
        code = """
def simple():
    return 42
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['simple'] == 1

    def test_function_with_if_statement(self):
        """Test complexity increases with if statement"""
        # Arrange
        code = """
def with_if(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_if'] == 2  # Base + if

    def test_function_with_multiple_ifs(self):
        """Test multiple if statements"""
        # Arrange
        code = """
def multiple_ifs(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['multiple_ifs'] == 3  # Base + if + if

    def test_function_with_while_loop(self):
        """Test while loop increases complexity"""
        # Arrange
        code = """
def with_while(x):
    while x > 0:
        x -= 1
    return x
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_while'] == 2  # Base + while

    def test_function_with_for_loop(self):
        """Test for loop increases complexity"""
        # Arrange
        code = """
def with_for(items):
    for item in items:
        print(item)
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_for'] == 2  # Base + for

    def test_function_with_except_handler(self):
        """Test except handler increases complexity"""
        # Arrange
        code = """
def with_except():
    try:
        risky_operation()
    except ValueError:
        handle_error()
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_except'] == 2  # Base + except

    def test_function_with_boolean_operators(self):
        """Test boolean operators increase complexity"""
        # Arrange
        code = """
def with_bool(a, b, c):
    if a and b or c:
        return True
    return False
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        # Base + if + and + or = 4
        assert complexity['with_bool'] == 4

    def test_function_with_comprehension(self):
        """Test comprehension increases complexity"""
        # Arrange
        code = """
def with_comprehension(items):
    return [x * 2 for x in items]
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_comprehension'] == 2  # Base + comprehension

    def test_function_with_lambda(self):
        """Test lambda increases complexity"""
        # Arrange
        code = """
def with_lambda():
    func = lambda x: x * 2
    return func
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_lambda'] == 2  # Base + lambda

    def test_function_with_assert(self):
        """Test assert increases complexity"""
        # Arrange
        code = """
def with_assert(x):
    assert x > 0
    return x
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_assert'] == 2  # Base + assert

    def test_function_with_with_statement(self):
        """Test with statement increases complexity"""
        # Arrange
        code = """
def with_context():
    with open('file.txt') as f:
        return f.read()
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['with_context'] == 2  # Base + with

    def test_complex_function(self):
        """Test real-world complex function"""
        # Arrange
        code = """
def complex_func(x, items):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                yield i
    else:
        return None
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        # Base(1) + if(1) + for(1) + if(1) = 4
        assert complexity['complex_func'] == 4

    def test_method_complexity(self):
        """Test complexity calculation for class method"""
        # Arrange
        code = """
class MyClass:
    def method(self, x):
        if x > 0:
            return x
        return 0
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert 'MyClass.method' in complexity
        assert complexity['MyClass.method'] == 2

    def test_async_function_complexity(self):
        """Test async function complexity"""
        # Arrange
        code = """
async def async_func(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert complexity['async_func'] == 2

    def test_nested_classes(self):
        """Test nested class methods"""
        # Arrange
        code = """
class Outer:
    class Inner:
        def method(self):
            if True:
                return 1
"""
        tree = ast.parse(code)

        # Act
        complexity = calculate_cyclomatic_complexity(tree)

        # Assert
        assert 'Outer.Inner.method' in complexity


class TestCalculateMaintainabilityIndex:
    """Tests for calculate_maintainability_index function"""

    def test_simple_maintainability_calculation(self):
        """Test basic MI calculation"""
        # Arrange
        loc = 100
        complexity = 5

        # Act
        mi = calculate_maintainability_index(loc, complexity)

        # Assert
        assert 0.0 <= mi <= 100.0
        assert isinstance(mi, float)

    def test_empty_file_is_perfectly_maintainable(self):
        """Test that empty file has MI of 100"""
        # Arrange
        loc = 0
        complexity = 0

        # Act
        mi = calculate_maintainability_index(loc, complexity)

        # Assert
        assert mi == 100.0

    def test_high_complexity_reduces_mi(self):
        """Test that high complexity reduces MI"""
        # Arrange
        loc = 100
        low_complexity = 5
        high_complexity = 50

        # Act
        mi_low = calculate_maintainability_index(loc, low_complexity)
        mi_high = calculate_maintainability_index(loc, high_complexity)

        # Assert
        assert mi_low > mi_high

    def test_high_loc_reduces_mi(self):
        """Test that high LOC reduces MI"""
        # Arrange
        complexity = 5
        low_loc = 50
        high_loc = 500

        # Act
        mi_low = calculate_maintainability_index(low_loc, complexity)
        mi_high = calculate_maintainability_index(high_loc, complexity)

        # Assert
        assert mi_low > mi_high

    def test_with_halstead_volume(self):
        """Test MI calculation with Halstead volume"""
        # Arrange
        loc = 100
        complexity = 10
        volume = 500.0

        # Act
        mi = calculate_maintainability_index(loc, complexity, volume)

        # Assert
        assert 0.0 <= mi <= 100.0

    def test_negative_loc_raises_error(self):
        """Test that negative LOC raises ValueError"""
        # Arrange
        loc = -10
        complexity = 5

        # Act & Assert
        with pytest.raises(ValueError, match="LOC must be non-negative"):
            calculate_maintainability_index(loc, complexity)

    def test_negative_complexity_raises_error(self):
        """Test that negative complexity raises ValueError"""
        # Arrange
        loc = 100
        complexity = -5

        # Act & Assert
        with pytest.raises(ValueError, match="Complexity must be non-negative"):
            calculate_maintainability_index(loc, complexity)

    def test_mi_clamped_to_valid_range(self):
        """Test MI is clamped to 0-100 range"""
        # Arrange
        loc = 1
        complexity = 1

        # Act
        mi = calculate_maintainability_index(loc, complexity)

        # Assert
        assert 0.0 <= mi <= 100.0


class TestAggregateFileMetrics:
    """Tests for aggregate_file_metrics function"""

    def test_aggregate_empty_list(self):
        """Test aggregating empty file list"""
        # Arrange
        files = []

        # Act
        metrics = aggregate_file_metrics(files)

        # Assert
        assert metrics['total_files'] == 0
        assert metrics['total_lines'] == 0
        assert metrics['avg_complexity'] == 0.0

    def test_aggregate_single_file(self, tmp_path: Path):
        """Test aggregating single file"""
        # Arrange
        test_file = tmp_path / "test.py"
        code = """def foo():
    if True:
        return 42
"""
        test_file.write_text(code)
        files = [test_file]

        # Act
        metrics = aggregate_file_metrics(files)

        # Assert
        assert metrics['total_files'] == 1
        assert metrics['total_code_lines'] > 0

    def test_aggregate_multiple_files(self, tmp_path: Path):
        """Test aggregating multiple files"""
        # Arrange
        file1 = tmp_path / "file1.py"
        file1.write_text("def foo():\n    return 42\n")

        file2 = tmp_path / "file2.py"
        file2.write_text("def bar():\n    return 100\n")

        files = [file1, file2]

        # Act
        metrics = aggregate_file_metrics(files)

        # Assert
        assert metrics['total_files'] == 2
        assert metrics['total_code_lines'] > 0

    def test_aggregate_counts_high_complexity_files(self, tmp_path: Path):
        """Test counting files with high complexity"""
        # Arrange
        complex_file = tmp_path / "complex.py"
        code = """
def complex_func(a, b, c, d, e, f, g, h, i, j, k, l):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    if i:
                                        if j:
                                            if k:
                                                if l:
                                                    return True
    return False
"""
        complex_file.write_text(code)
        files = [complex_file]

        # Act
        metrics = aggregate_file_metrics(files)

        # Assert
        assert metrics['max_complexity'] > 10
        assert metrics['files_high_complexity'] > 0

    def test_aggregate_handles_syntax_errors(self, tmp_path: Path):
        """Test that syntax errors don't break aggregation"""
        # Arrange
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n")

        files = [bad_file]

        # Act
        metrics = aggregate_file_metrics(files)

        # Assert
        # Should process file for line counts even if syntax error
        assert metrics['total_files'] >= 0


class TestCalculateRadonMetrics:
    """Tests for calculate_radon_metrics function"""

    def test_radon_available_or_gracefully_degrades(self, tmp_path: Path):
        """Test Radon integration or graceful degradation"""
        # Arrange
        test_file = tmp_path / "test.py"
        code = """
def foo(x):
    if x > 0:
        return x
    return 0
"""
        test_file.write_text(code)

        # Act
        metrics = calculate_radon_metrics(test_file)

        # Assert
        if RADON_AVAILABLE:
            assert metrics is not None
            assert 'complexity' in metrics
            assert 'maintainability' in metrics
        else:
            assert metrics is None

    @pytest.mark.skipif(not RADON_AVAILABLE, reason="Radon not installed")
    def test_radon_complexity_metrics(self, tmp_path: Path):
        """Test Radon complexity metrics (if available)"""
        # Arrange
        test_file = tmp_path / "test.py"
        code = """
def simple():
    return 42

def complex_func(x):
    if x > 0:
        for i in range(x):
            if i % 2:
                yield i
"""
        test_file.write_text(code)

        # Act
        metrics = calculate_radon_metrics(test_file)

        # Assert
        assert metrics is not None
        assert len(metrics['complexity']) >= 2
        assert any(item['name'] == 'simple' for item in metrics['complexity'])


class TestMiRank:
    """Tests for mi_rank function"""

    def test_high_mi_gets_a_rank(self):
        """Test MI >= 85 gets A rank"""
        # Arrange
        mi = 90.0

        # Act
        rank = mi_rank(mi)

        # Assert
        assert rank == 'A'

    def test_medium_mi_gets_b_rank(self):
        """Test MI 65-85 gets B rank"""
        # Arrange
        mi = 75.0

        # Act
        rank = mi_rank(mi)

        # Assert
        assert rank == 'B'

    def test_low_mi_gets_c_rank(self):
        """Test MI < 65 gets C rank"""
        # Arrange
        mi = 50.0

        # Act
        rank = mi_rank(mi)

        # Assert
        assert rank == 'C'


class TestCalculateSizeMetrics:
    """Tests for calculate_size_metrics function"""

    def test_size_metrics_for_functions(self):
        """Test size metrics calculation for functions"""
        # Arrange
        code = """
def short_func():
    return 42

def long_func():
    # Many lines here
""" + "\n    pass" * 60
        tree = ast.parse(code)

        # Act
        metrics = calculate_size_metrics(tree)

        # Assert
        assert metrics['functions']['count'] == 2
        assert metrics['functions']['functions_over_50_lines'] >= 1

    def test_size_metrics_for_classes(self):
        """Test size metrics for classes"""
        # Arrange
        code = """
class SmallClass:
    def method1(self):
        pass

class LargeClass:
    def method1(self):
        pass
    def method2(self):
        pass
    def method3(self):
        pass
    def method4(self):
        pass
    def method5(self):
        pass
"""
        tree = ast.parse(code)

        # Act
        metrics = calculate_size_metrics(tree)

        # Assert
        assert metrics['classes']['count'] == 2
        assert metrics['classes']['max_methods'] >= 5

    def test_empty_ast_returns_zeros(self):
        """Test empty AST returns zero metrics"""
        # Arrange
        code = ""
        tree = ast.parse(code)

        # Act
        metrics = calculate_size_metrics(tree)

        # Assert
        assert metrics['functions']['count'] == 0
        assert metrics['classes']['count'] == 0


class TestIntegration:
    """Integration tests combining multiple metrics"""

    def test_analyze_real_python_file(self, tmp_path: Path):
        """Test analyzing realistic Python file"""
        # Arrange
        test_file = tmp_path / "example.py"
        code = '''"""Module docstring"""
import os
from pathlib import Path

VERSION = "1.0.0"

class MyClass:
    def __init__(self):
        self.value = 0

    def process(self, items):
        result = 0
        for item in items:
            if item > 0:
                result += item
        return result

def complex_function(a, b, c):
    if a and b or c:
        for i in range(10):
            if i % 2 == 0:
                yield i
'''
        test_file.write_text(code)

        # Act
        line_counts = count_lines(test_file)
        tree = ast.parse(test_file.read_text())
        complexity_map = calculate_cyclomatic_complexity(tree)
        size_metrics = calculate_size_metrics(tree)

        # Assert - Lines
        assert line_counts['total_lines'] > 0
        assert line_counts['code_lines'] > 0

        # Assert - Complexity
        assert len(complexity_map) >= 3  # __init__, process, complex_function
        assert any(c > 1 for c in complexity_map.values())

        # Assert - Size
        assert size_metrics['functions']['count'] >= 2
        assert size_metrics['classes']['count'] == 1
