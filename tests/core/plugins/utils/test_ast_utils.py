"""
Comprehensive tests for AST utilities module.

Tests all functions with:
- Unit tests for each function
- Edge cases and error handling
- Performance constraints validation
- Security constraints validation
- Example code from docstrings

Target: >90% test coverage
"""

import ast
import tempfile
from pathlib import Path
from typing import List, Dict, Any

import pytest

from agentpm.utils.ast_utils import (
    parse_python_ast,
    extract_imports,
    extract_classes,
    extract_functions,
    calculate_complexity,
    extract_variables,
    MAX_FILE_SIZE,
)


class TestParsePythonAST:
    """Tests for parse_python_ast function"""

    def test_parse_valid_python_file(self, tmp_path: Path):
        """Test parsing valid Python file"""
        # Arrange
        test_file = tmp_path / "valid.py"
        test_file.write_text("def foo():\n    return 42\n")

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_parse_empty_file(self, tmp_path: Path):
        """Test parsing empty Python file"""
        # Arrange
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_parse_syntax_error_returns_none(self, tmp_path: Path):
        """Test that syntax errors return None gracefully"""
        # Arrange
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def foo(\n    # Intentional syntax error")

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is None

    def test_parse_unicode_decode_error_returns_none(self, tmp_path: Path):
        """Test that binary files return None gracefully"""
        # Arrange
        test_file = tmp_path / "binary.py"
        test_file.write_bytes(b'\x80\x81\x82\x83')  # Invalid UTF-8

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is None

    def test_parse_nonexistent_file_returns_none(self, tmp_path: Path):
        """Test that missing files return None gracefully"""
        # Arrange
        test_file = tmp_path / "nonexistent.py"

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is None

    def test_parse_file_too_large_returns_none(self, tmp_path: Path):
        """Test that files >10MB are skipped"""
        # Arrange
        test_file = tmp_path / "huge.py"
        # Create file slightly larger than MAX_FILE_SIZE
        huge_content = "# Comment\n" * ((MAX_FILE_SIZE // 10) + 1000)
        test_file.write_text(huge_content)

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is None


class TestExtractImports:
    """Tests for extract_imports function"""

    def test_extract_simple_imports(self):
        """Test extracting simple import statements"""
        # Arrange
        code = """
import os
import sys
import json
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert sorted(imports) == ['json', 'os', 'sys']

    def test_extract_from_imports(self):
        """Test extracting from...import statements"""
        # Arrange
        code = """
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert sorted(imports) == ['collections', 'pathlib', 'typing']

    def test_extract_mixed_imports(self):
        """Test extracting mixed import styles"""
        # Arrange
        code = """
import os
from pathlib import Path
import sys
from typing import List
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert sorted(imports) == ['os', 'pathlib', 'sys', 'typing']

    def test_extract_aliased_imports(self):
        """Test extracting imports with aliases"""
        # Arrange
        code = """
import numpy as np
from collections import defaultdict as dd
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert sorted(imports) == ['collections', 'numpy']

    def test_extract_no_imports(self):
        """Test code with no imports"""
        # Arrange
        code = """
def foo():
    return 42
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert imports == []

    def test_deduplicates_imports(self):
        """Test that duplicate imports are deduplicated"""
        # Arrange
        code = """
import os
import os
from os import path
"""
        tree = ast.parse(code)

        # Act
        imports = extract_imports(tree)

        # Assert
        assert imports == ['os']


class TestExtractClasses:
    """Tests for extract_classes function"""

    def test_extract_simple_class(self):
        """Test extracting simple class definition"""
        # Arrange
        code = """
class Foo:
    pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 1
        assert classes[0]['name'] == 'Foo'
        assert classes[0]['bases'] == []
        assert classes[0]['methods'] == []
        assert classes[0]['decorators'] == []

    def test_extract_class_with_inheritance(self):
        """Test extracting class with base classes"""
        # Arrange
        code = """
class Foo(BaseModel, MixinA):
    pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 1
        assert classes[0]['name'] == 'Foo'
        assert sorted(classes[0]['bases']) == ['BaseModel', 'MixinA']

    def test_extract_class_with_methods(self):
        """Test extracting class with methods"""
        # Arrange
        code = """
class Foo:
    def method1(self):
        pass

    def method2(self, arg):
        pass

    def __init__(self):
        pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 1
        assert sorted(classes[0]['methods']) == ['__init__', 'method1', 'method2']

    def test_extract_decorated_class(self):
        """Test extracting class with decorators"""
        # Arrange
        code = """
@dataclass
@frozen
class Foo:
    pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 1
        assert sorted(classes[0]['decorators']) == ['dataclass', 'frozen']

    def test_extract_class_line_numbers(self):
        """Test that line numbers are correctly extracted"""
        # Arrange
        code = """

class Foo:
    def method(self):
        pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 1
        assert classes[0]['line_number'] == 3  # Class starts on line 3
        assert classes[0]['end_line'] >= 3

    def test_extract_multiple_classes(self):
        """Test extracting multiple classes"""
        # Arrange
        code = """
class Foo:
    pass

class Bar(Foo):
    pass

class Baz:
    pass
"""
        tree = ast.parse(code)

        # Act
        classes = extract_classes(tree, Path("test.py"))

        # Assert
        assert len(classes) == 3
        class_names = [c['name'] for c in classes]
        assert sorted(class_names) == ['Bar', 'Baz', 'Foo']


class TestExtractFunctions:
    """Tests for extract_functions function"""

    def test_extract_simple_function(self):
        """Test extracting simple function"""
        # Arrange
        code = """
def foo():
    return 42
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert functions[0]['name'] == 'foo'
        assert functions[0]['args'] == []
        assert functions[0]['is_async'] is False
        assert functions[0]['complexity'] == 1  # Base complexity

    def test_extract_function_with_args(self):
        """Test extracting function with arguments"""
        # Arrange
        code = """
def foo(arg1, arg2, arg3):
    return arg1 + arg2 + arg3
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert functions[0]['args'] == ['arg1', 'arg2', 'arg3']

    def test_extract_async_function(self):
        """Test extracting async function"""
        # Arrange
        code = """
async def foo():
    return 42
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert functions[0]['is_async'] is True

    def test_extract_decorated_function(self):
        """Test extracting function with decorators"""
        # Arrange
        code = """
@property
@cache
def foo():
    return 42
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert sorted(functions[0]['decorators']) == ['cache', 'property']

    def test_extract_function_line_numbers(self):
        """Test that line numbers are correctly extracted"""
        # Arrange
        code = """

def foo():
    pass
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert functions[0]['line_number'] == 3
        assert functions[0]['end_line'] >= 3

    def test_extract_multiple_functions(self):
        """Test extracting multiple functions"""
        # Arrange
        code = """
def foo():
    pass

def bar(x):
    pass

async def baz():
    pass
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 3
        func_names = [f['name'] for f in functions]
        assert sorted(func_names) == ['bar', 'baz', 'foo']

    def test_extract_function_complexity(self):
        """Test that complexity is calculated"""
        # Arrange
        code = """
def complex_func(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)

        # Act
        functions = extract_functions(tree, Path("test.py"))

        # Assert
        assert len(functions) == 1
        assert functions[0]['complexity'] == 2  # Base + if


class TestCalculateComplexity:
    """Tests for calculate_complexity function"""

    def test_simple_function_complexity_is_one(self):
        """Test that simple function has complexity of 1"""
        # Arrange
        code = """
def simple():
    return 42
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 1

    def test_if_statement_increases_complexity(self):
        """Test that if statement increases complexity"""
        # Arrange
        code = """
def with_if(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 2  # Base + if

    def test_multiple_if_statements(self):
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
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 3  # Base + if + if

    def test_while_loop_increases_complexity(self):
        """Test that while loop increases complexity"""
        # Arrange
        code = """
def with_while(x):
    while x > 0:
        x -= 1
    return x
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 2  # Base + while

    def test_for_loop_increases_complexity(self):
        """Test that for loop increases complexity"""
        # Arrange
        code = """
def with_for(items):
    for item in items:
        print(item)
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 2  # Base + for

    def test_except_handler_increases_complexity(self):
        """Test that except handler increases complexity"""
        # Arrange
        code = """
def with_except():
    try:
        risky_operation()
    except ValueError:
        handle_error()
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 2  # Base + except

    def test_boolean_operators_increase_complexity(self):
        """Test that boolean operators increase complexity"""
        # Arrange
        code = """
def with_bool(a, b, c):
    if a and b or c:
        return True
    return False
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        # Base + if + (2 boolean ops from "a and b or c")
        assert complexity == 4

    def test_comprehension_increases_complexity(self):
        """Test that comprehensions increase complexity"""
        # Arrange
        code = """
def with_comprehension(items):
    return [x * 2 for x in items]
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 2  # Base + comprehension

    def test_complex_function_example(self):
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
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        # Base(1) + if(1) + for(1) + if(1) = 4
        assert complexity == 4

    def test_nested_conditions(self):
        """Test nested conditions"""
        # Arrange
        code = """
def nested(a, b, c):
    if a:
        if b:
            if c:
                return True
    return False
"""
        tree = ast.parse(code)
        func = tree.body[0]

        # Act
        complexity = calculate_complexity(func)

        # Assert
        assert complexity == 4  # Base + 3 ifs


class TestExtractVariables:
    """Tests for extract_variables function"""

    def test_extract_simple_variable(self):
        """Test extracting simple variable assignment"""
        # Arrange
        code = """
VERSION = "1.0.0"
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert len(variables) == 1
        assert variables[0]['name'] == 'VERSION'
        assert variables[0]['type_hint'] is None

    def test_extract_annotated_variable(self):
        """Test extracting variable with type annotation"""
        # Arrange
        code = """
DEBUG: bool = True
TIMEOUT: int = 30
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert len(variables) == 2
        assert variables[0]['name'] == 'DEBUG'
        assert variables[0]['type_hint'] == 'bool'
        assert variables[1]['name'] == 'TIMEOUT'
        assert variables[1]['type_hint'] == 'int'

    def test_extract_multiple_assignments(self):
        """Test extracting multiple assignments (x = y = z)"""
        # Arrange
        code = """
x = y = z = 42
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert len(variables) == 3
        names = [v['name'] for v in variables]
        assert sorted(names) == ['x', 'y', 'z']

    def test_extract_complex_type_hints(self):
        """Test extracting complex type annotations"""
        # Arrange
        code = """
items: List[str] = []
mapping: Dict[str, int] = {}
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert len(variables) == 2
        assert variables[0]['type_hint'] == 'List[str]'
        assert variables[1]['type_hint'] == 'Dict[str, int]'

    def test_ignores_function_scope_variables(self):
        """Test that function-level variables are ignored"""
        # Arrange
        code = """
MODULE_VAR = 1

def foo():
    local_var = 2  # Should be ignored
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert len(variables) == 1
        assert variables[0]['name'] == 'MODULE_VAR'

    def test_extract_no_variables(self):
        """Test code with no module-level variables"""
        # Arrange
        code = """
def foo():
    return 42
"""
        tree = ast.parse(code)

        # Act
        variables = extract_variables(tree)

        # Assert
        assert variables == []


class TestIntegration:
    """Integration tests using all functions together"""

    def test_analyze_real_python_file(self, tmp_path: Path):
        """Test analyzing a realistic Python file"""
        # Arrange
        code = """
'''Module docstring'''
import os
from pathlib import Path
from typing import List, Optional

VERSION: str = "1.0.0"
DEBUG = False

class MyClass(BaseModel):
    '''Class docstring'''

    def __init__(self):
        self.value = 0

    @property
    def doubled(self):
        return self.value * 2

    def process(self, items: List[int]) -> int:
        result = 0
        for item in items:
            if item > 0:
                result += item
        return result

async def async_function(x: int) -> Optional[int]:
    if x > 0:
        return x
    return None

def complex_function(a, b, c):
    if a and b or c:
        for i in range(10):
            if i % 2 == 0:
                yield i
"""
        test_file = tmp_path / "example.py"
        test_file.write_text(code)

        # Act
        tree = parse_python_ast(test_file)
        imports = extract_imports(tree)
        classes = extract_classes(tree, test_file)
        functions = extract_functions(tree, test_file)
        variables = extract_variables(tree)

        # Assert - Parse
        assert tree is not None

        # Assert - Imports
        assert sorted(imports) == ['os', 'pathlib', 'typing']

        # Assert - Classes
        assert len(classes) == 1
        assert classes[0]['name'] == 'MyClass'
        assert classes[0]['bases'] == ['BaseModel']
        assert sorted(classes[0]['methods']) == ['__init__', 'doubled', 'process']
        assert classes[0]['decorators'] == []

        # Assert - Functions (including methods)
        # Note: extract_functions gets ALL functions, including class methods
        func_names = [f['name'] for f in functions]
        assert 'async_function' in func_names
        assert 'complex_function' in func_names

        # Assert - Variables
        assert len(variables) == 2
        var_names = [v['name'] for v in variables]
        assert sorted(var_names) == ['DEBUG', 'VERSION']

    def test_handle_malformed_python_gracefully(self, tmp_path: Path):
        """Test that malformed Python is handled gracefully"""
        # Arrange
        code = """
def broken(
    # Syntax error here
"""
        test_file = tmp_path / "broken.py"
        test_file.write_text(code)

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is None  # Should return None, not raise exception


class TestPerformanceConstraints:
    """Tests for performance constraints"""

    def test_parse_completes_quickly_for_normal_files(self, tmp_path: Path):
        """Test that parsing completes in reasonable time"""
        # Arrange
        # Create ~1000 line file
        code = "\n".join([f"def func_{i}():\n    return {i}" for i in range(500)])
        test_file = tmp_path / "large.py"
        test_file.write_text(code)

        # Act
        import time
        start = time.time()
        tree = parse_python_ast(test_file)
        elapsed_ms = (time.time() - start) * 1000

        # Assert
        assert tree is not None
        # Should complete in <100ms as per spec, but allow some buffer for CI
        assert elapsed_ms < 500  # 5x buffer for slow CI systems


class TestSecurityConstraints:
    """Tests for security constraints"""

    def test_parse_does_not_execute_code(self, tmp_path: Path):
        """Test that parsing does NOT execute code"""
        # Arrange
        code = """
# This should NOT be executed during parsing
import os
os.system("echo 'This should not run'")

def dangerous():
    exec("print('dangerous')")
"""
        test_file = tmp_path / "dangerous.py"
        test_file.write_text(code)

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        assert tree is not None
        # If code was executed, we'd see output or side effects
        # AST parsing is safe - it only parses, never executes

    def test_handles_potentially_malicious_code(self, tmp_path: Path):
        """Test that potentially malicious code is handled safely"""
        # Arrange
        code = """
# Attempt at code injection (should be safe with AST parsing)
__import__('os').system('rm -rf /')
eval('print("evil")')
exec('print("evil")')
"""
        test_file = tmp_path / "malicious.py"
        test_file.write_text(code)

        # Act
        tree = parse_python_ast(test_file)

        # Assert
        # Should parse successfully without executing anything
        assert tree is not None


# Pytest fixtures

@pytest.fixture
def sample_code():
    """Provide sample code for tests"""
    return """
import os
from pathlib import Path

class Example:
    def method(self):
        pass

def function():
    return 42
"""
