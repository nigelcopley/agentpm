"""
AST Utils Demonstration Script

Shows practical usage of all AST utility functions.
"""

from pathlib import Path
from agentpm.utils.ast_utils import (
    parse_python_ast,
    extract_imports,
    extract_classes,
    extract_functions,
    calculate_complexity,
    extract_variables,
)


def demo_ast_utils():
    """Demonstrate AST utilities on this file"""
    # Parse this file
    this_file = Path(__file__)
    print(f"Analyzing: {this_file.name}\n")

    # 1. Parse to AST
    tree = parse_python_ast(this_file)
    if tree is None:
        print("Failed to parse file")
        return

    print("✓ Successfully parsed file\n")

    # 2. Extract imports
    imports = extract_imports(tree)
    print(f"Imports ({len(imports)}):")
    for imp in imports:
        print(f"  - {imp}")
    print()

    # 3. Extract classes
    classes = extract_classes(tree, this_file)
    print(f"Classes ({len(classes)}):")
    for cls in classes:
        print(f"  - {cls['name']} (line {cls['line_number']})")
        if cls['bases']:
            print(f"    Bases: {', '.join(cls['bases'])}")
        if cls['methods']:
            print(f"    Methods: {', '.join(cls['methods'])}")
    print()

    # 4. Extract functions
    functions = extract_functions(tree, this_file)
    print(f"Functions ({len(functions)}):")
    for func in functions:
        print(f"  - {func['name']} (line {func['line_number']})")
        print(f"    Args: {', '.join(func['args']) if func['args'] else 'none'}")
        print(f"    Complexity: {func['complexity']}")
        print(f"    Async: {func['is_async']}")
    print()

    # 5. Extract variables
    variables = extract_variables(tree)
    print(f"Module Variables ({len(variables)}):")
    for var in variables:
        type_hint = f": {var['type_hint']}" if var['type_hint'] else ""
        print(f"  - {var['name']}{type_hint} (line {var['line_number']})")
    print()

    # 6. Complexity analysis
    print("Complexity Analysis:")
    complexities = [(f['name'], f['complexity']) for f in functions]
    complexities.sort(key=lambda x: x[1], reverse=True)
    for name, complexity in complexities[:5]:  # Top 5 most complex
        print(f"  - {name}: {complexity}")
    print()


class ExampleClass:
    """Example class for demonstration"""

    def simple_method(self):
        """Simple method with complexity 1"""
        return 42

    def complex_method(self, x, y, z):
        """More complex method"""
        if x > 0:
            for i in range(x):
                if i % 2 == 0:
                    yield i
        elif y > 0:
            return y
        else:
            return z


if __name__ == "__main__":
    demo_ast_utils()
