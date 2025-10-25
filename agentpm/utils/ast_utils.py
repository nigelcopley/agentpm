"""
AST Utilities Module - Layer 1 (Shared Utilities)

Provides low-level AST parsing primitives used by BOTH plugins (Layer 2)
AND detection services (Layer 3).

**Architecture Compliance**:
- Layer 1: NO dependencies on plugins or detection services
- Safe AST parsing (no eval/exec)
- Performance: <100ms per file, handles files up to 10MB
- Shared by both PythonPlugin AND StaticAnalysisService

**Security**:
- Uses ast.parse() only (no eval/exec)
- Handles malformed Python gracefully
- No code execution during parsing

**Usage Examples**:

    # Example 1: Plugin using this utility (Layer 2 → Layer 1)
    from agentpm.core.plugins.utils.ast_utils import parse_python_ast

    class PythonPlugin:
        def detect(self, path):
            tree = parse_python_ast(some_file)  # ✅ Layer 2 → Layer 1
            if tree:
                return 0.9

    # Example 2: Detection service using this utility (Layer 3 → Layer 1)
    from agentpm.core.plugins.utils.ast_utils import extract_classes

    class StaticAnalysisService:
        def analyze(self, path):
            classes = extract_classes(tree, path)  # ✅ Layer 3 → Layer 1
            return classes

**Functions**:
- parse_python_ast: Parse Python file to AST tree
- extract_imports: Extract all import statements
- extract_classes: Extract class definitions with metadata
- extract_functions: Extract function definitions with metadata
- calculate_complexity: Calculate cyclomatic complexity
- extract_variables: Extract module-level variable assignments
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

# Performance and safety constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PARSE_TIMEOUT_MS = 100  # Target: <100ms per file


def parse_python_ast(file_path: Path) -> Optional[ast.AST]:
    """
    Parse Python file to AST.

    Safe parsing:
    - Use ast.parse() only (no eval/exec)
    - Handle syntax errors gracefully
    - Return None on parse failure
    - Skip files larger than 10MB

    Args:
        file_path: Path to Python file

    Returns:
        AST tree or None if parse fails

    Examples:
        >>> from pathlib import Path
        >>> tree = parse_python_ast(Path("example.py"))
        >>> if tree:
        ...     print("Successfully parsed")

        >>> # Handles syntax errors gracefully
        >>> tree = parse_python_ast(Path("malformed.py"))
        >>> if tree is None:
        ...     print("Parse failed, but no exception raised")

    Performance:
        - Target: <100ms per file
        - Skips files >10MB
        - Early return on syntax errors

    Security:
        - NO eval() or exec() - uses ast.parse() only
        - Safe for untrusted code analysis
        - No code execution during parsing
    """
    try:
        # Safety: Check file size
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return None

        # Read file content
        content = file_path.read_text(encoding='utf-8')

        # Safe parsing: ast.parse() does NOT execute code
        return ast.parse(content, filename=str(file_path))

    except (SyntaxError, ValueError, UnicodeDecodeError, FileNotFoundError, OSError):
        # Handle malformed Python gracefully
        return None


def extract_imports(tree: ast.AST) -> List[str]:
    """
    Extract all import statements from AST.

    Handles:
    - import foo
    - from foo import bar
    - from foo.bar import baz as qux

    Args:
        tree: AST tree from parse_python_ast()

    Returns:
        List of imported module names (deduplicated)

    Examples:
        >>> import ast
        >>> code = '''
        ... import os
        ... import sys
        ... from pathlib import Path
        ... from typing import List, Dict
        ... '''
        >>> tree = ast.parse(code)
        >>> imports = extract_imports(tree)
        >>> sorted(imports)
        ['os', 'pathlib', 'sys', 'typing']

        >>> # Handles aliased imports
        >>> code = "from foo.bar import baz as qux"
        >>> tree = ast.parse(code)
        >>> extract_imports(tree)
        ['foo.bar']
    """
    imports = set()  # Use set to deduplicate

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # import foo, bar
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            # from foo import bar
            if node.module:  # from foo import bar
                imports.add(node.module)
            # else: relative import (from . import foo)

    return sorted(imports)  # Return sorted list for consistency


def extract_classes(tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract class definitions from AST.

    Returns list of dicts with:
    - name: Class name
    - bases: Base class names
    - line_number: Starting line
    - end_line: Ending line
    - methods: List of method names
    - decorators: List of decorator names

    Args:
        tree: AST tree from parse_python_ast()
        file_path: Path to source file (for context)

    Returns:
        List of class metadata dictionaries

    Examples:
        >>> import ast
        >>> code = '''
        ... @dataclass
        ... class Foo(BaseModel):
        ...     def method1(self):
        ...         pass
        ...     def method2(self):
        ...         pass
        ... '''
        >>> tree = ast.parse(code)
        >>> classes = extract_classes(tree, Path("example.py"))
        >>> classes[0]['name']
        'Foo'
        >>> classes[0]['bases']
        ['BaseModel']
        >>> sorted(classes[0]['methods'])
        ['method1', 'method2']
        >>> classes[0]['decorators']
        ['dataclass']
    """
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Extract base class names
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    # Handle foo.Bar style bases
                    bases.append(_get_attribute_name(base))

            # Extract method names
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)

            # Extract decorator names
            decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)

            classes.append({
                'name': node.name,
                'bases': bases,
                'line_number': node.lineno,
                'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                'methods': methods,
                'decorators': decorators,
            })

    return classes


def extract_functions(tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract function definitions from AST.

    Returns list of dicts with:
    - name: Function name
    - line_number: Starting line
    - end_line: Ending line
    - args: List of argument names
    - decorators: List of decorator names
    - is_async: Boolean
    - complexity: Cyclomatic complexity

    Args:
        tree: AST tree from parse_python_ast()
        file_path: Path to source file (for context)

    Returns:
        List of function metadata dictionaries

    Examples:
        >>> import ast
        >>> code = '''
        ... @property
        ... def foo(arg1, arg2, arg3="default"):
        ...     if arg1:
        ...         return arg2
        ...     return arg3
        ...
        ... async def bar(x):
        ...     return x * 2
        ... '''
        >>> tree = ast.parse(code)
        >>> funcs = extract_functions(tree, Path("example.py"))
        >>> funcs[0]['name']
        'foo'
        >>> funcs[0]['args']
        ['arg1', 'arg2', 'arg3']
        >>> funcs[0]['decorators']
        ['property']
        >>> funcs[0]['complexity']
        2
        >>> funcs[1]['is_async']
        True
    """
    functions = []

    # Track visited to avoid duplicates from nested functions
    visited = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip if already processed (nested functions)
            node_id = id(node)
            if node_id in visited:
                continue
            visited.add(node_id)

            # Extract argument names
            args = []
            for arg in node.args.args:
                args.append(arg.arg)

            # Extract decorator names
            decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)

            # Calculate complexity
            complexity = calculate_complexity(node)

            functions.append({
                'name': node.name,
                'line_number': node.lineno,
                'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                'args': args,
                'decorators': decorators,
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'complexity': complexity,
            })

    return functions


def calculate_complexity(node: ast.FunctionDef) -> int:
    """
    Calculate cyclomatic complexity for function/method.

    Complexity += 1 for each:
    - if/elif
    - while/for
    - except handler
    - and/or in boolean expressions
    - list/dict/set comprehensions

    Base complexity: 1

    Args:
        node: AST FunctionDef or AsyncFunctionDef node

    Returns:
        Cyclomatic complexity score (minimum 1)

    Examples:
        >>> import ast
        >>> code = '''
        ... def simple():
        ...     return 42
        ... '''
        >>> tree = ast.parse(code)
        >>> func = tree.body[0]
        >>> calculate_complexity(func)
        1

        >>> code = '''
        ... def complex_func(x):
        ...     if x > 0:
        ...         for i in range(x):
        ...             if i % 2 == 0:
        ...                 yield i
        ...     else:
        ...         return None
        ... '''
        >>> tree = ast.parse(code)
        >>> func = tree.body[0]
        >>> calculate_complexity(func)
        4

        >>> # Boolean operators increase complexity
        >>> code = '''
        ... def with_bool(a, b, c):
        ...     if a and b or c:
        ...         return True
        ...     return False
        ... '''
        >>> tree = ast.parse(code)
        >>> func = tree.body[0]
        >>> calculate_complexity(func)
        3

    Algorithm:
        McCabe Cyclomatic Complexity = Edges - Nodes + 2
        Simplified: 1 + decision_points
    """
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        # Control flow decision points
        if isinstance(child, ast.If):
            complexity += 1
        elif isinstance(child, ast.While):
            complexity += 1
        elif isinstance(child, ast.For):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1

        # Boolean operators (and/or)
        elif isinstance(child, ast.BoolOp):
            # Each boolean operator adds a decision point
            # "a and b and c" = 2 additional paths (3 operands - 1)
            complexity += len(child.values) - 1

        # Comprehensions (implicit loops)
        elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            # Each generator adds complexity
            complexity += len(child.generators)

        # Ternary expressions (a if b else c)
        elif isinstance(child, ast.IfExp):
            complexity += 1

    return complexity


def extract_variables(tree: ast.AST) -> List[Dict[str, Any]]:
    """
    Extract module-level variable assignments.

    Returns list of dicts with:
    - name: Variable name
    - line_number: Assignment line
    - type_hint: Type annotation if present

    Args:
        tree: AST tree from parse_python_ast()

    Returns:
        List of variable metadata dictionaries

    Examples:
        >>> import ast
        >>> code = '''
        ... VERSION = "1.0.0"
        ... DEBUG: bool = True
        ... TIMEOUT = 30
        ... DATABASE_URL: str = "sqlite:///db.sqlite"
        ... '''
        >>> tree = ast.parse(code)
        >>> vars = extract_variables(tree)
        >>> vars[0]
        {'name': 'VERSION', 'line_number': 2, 'type_hint': None}
        >>> vars[1]
        {'name': 'DEBUG', 'line_number': 3, 'type_hint': 'bool'}
        >>> vars[3]['type_hint']
        'str'

        >>> # Handles multiple assignments
        >>> code = "x = y = z = 42"
        >>> tree = ast.parse(code)
        >>> vars = extract_variables(tree)
        >>> [v['name'] for v in vars]
        ['x', 'y', 'z']
    """
    variables = []

    # Only extract module-level assignments (tree.body)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # Regular assignment: x = 1 or x = y = 1
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({
                        'name': target.id,
                        'line_number': node.lineno,
                        'type_hint': None,
                    })

        elif isinstance(node, ast.AnnAssign):
            # Annotated assignment: x: int = 1
            if isinstance(node.target, ast.Name):
                type_hint = _get_type_annotation(node.annotation)
                variables.append({
                    'name': node.target.id,
                    'line_number': node.lineno,
                    'type_hint': type_hint,
                })

    return variables


# Helper functions (internal)

def _get_attribute_name(node: ast.Attribute) -> str:
    """
    Extract full attribute name from AST node.

    Handles: foo.bar.baz → "foo.bar.baz"
    """
    parts = []
    current = node

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    return '.'.join(reversed(parts))


def _get_type_annotation(node: ast.AST) -> Optional[str]:
    """
    Extract type annotation as string.

    Handles:
    - Simple types: int, str, bool
    - Generic types: List[str], Dict[str, int]
    - Complex types: Optional[List[str]]
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Subscript):
        # Generic type like List[str]
        base = _get_type_annotation(node.value)
        if isinstance(node.slice, ast.Tuple):
            # Multiple args like Dict[str, int]
            args = [_get_type_annotation(elt) for elt in node.slice.elts]
            return f"{base}[{', '.join(args)}]"
        else:
            # Single arg like List[str]
            arg = _get_type_annotation(node.slice)
            return f"{base}[{arg}]"
    elif isinstance(node, ast.Attribute):
        return _get_attribute_name(node)
    else:
        return None
