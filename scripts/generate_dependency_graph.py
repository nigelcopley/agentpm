#!/usr/bin/env python3
"""
Generate comprehensive dependency graph for AIPM system.
Analyzes Python imports and creates visual dependency maps.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict

class DependencyAnalyzer:
    """Analyze Python module dependencies in AIPM codebase."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.dependencies = defaultdict(set)
        self.module_info = {}
        self.external_deps = defaultdict(set)

    def analyze_file(self, file_path: Path) -> Dict[str, Set[str]]:
        """Analyze a single Python file for dependencies."""
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            module_name = self._get_module_name(file_path)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

            # Classify imports
            internal_imports = set()
            external_imports = set()

            for imp in imports:
                if imp.startswith('aipm_cli'):
                    internal_imports.add(imp)
                elif not imp.startswith('.'):
                    external_imports.add(imp)

            self.dependencies[module_name] = internal_imports
            self.external_deps[module_name] = external_imports

            # Store module info
            self.module_info[module_name] = {
                'path': str(file_path),
                'lines': len(open(file_path).readlines()),
                'imports': len(imports),
                'internal_deps': len(internal_imports),
                'external_deps': len(external_imports)
            }

            return {module_name: internal_imports}

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = file_path.relative_to(self.root_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(module_parts)

    def analyze_directory(self, directory: Path):
        """Recursively analyze all Python files in directory."""
        for py_file in directory.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                self.analyze_file(py_file)

    def generate_mermaid_graph(self) -> str:
        """Generate Mermaid graph syntax for dependencies."""
        lines = ["graph TD"]

        # Group modules by package
        packages = defaultdict(list)
        for module in self.dependencies:
            if '.' in module:
                package = module.rsplit('.', 1)[0]
                packages[package].append(module)

        # Add subgraphs for packages
        for package, modules in packages.items():
            if len(modules) > 1:
                lines.append(f"    subgraph {package.replace('.', '_')}")
                for module in modules:
                    short_name = module.split('.')[-1]
                    lines.append(f"        {module.replace('.', '_')}[{short_name}]")
                lines.append("    end")

        # Add dependencies
        added_deps = set()
        for module, deps in self.dependencies.items():
            for dep in deps:
                dep_tuple = (module.replace('.', '_'), dep.replace('.', '_'))
                if dep_tuple not in added_deps:
                    added_deps.add(dep_tuple)
                    lines.append(f"    {dep_tuple[0]} --> {dep_tuple[1]}")

        return '\n'.join(lines)

    def calculate_metrics(self) -> Dict:
        """Calculate dependency metrics."""
        metrics = {
            'total_modules': len(self.dependencies),
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'avg_dependencies': 0,
            'max_dependencies': 0,
            'most_dependent': '',
            'most_depended_upon': '',
            'circular_dependencies': []
        }

        if self.dependencies:
            metrics['avg_dependencies'] = metrics['total_dependencies'] / metrics['total_modules']

            # Find module with most dependencies
            max_deps = 0
            for module, deps in self.dependencies.items():
                if len(deps) > max_deps:
                    max_deps = len(deps)
                    metrics['most_dependent'] = module
                    metrics['max_dependencies'] = max_deps

            # Find most depended upon module
            dependency_count = defaultdict(int)
            for deps in self.dependencies.values():
                for dep in deps:
                    dependency_count[dep] += 1

            if dependency_count:
                metrics['most_depended_upon'] = max(dependency_count, key=dependency_count.get)

            # Detect circular dependencies
            metrics['circular_dependencies'] = self._find_circular_dependencies()

        return metrics

    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the dependency graph."""
        circular = []
        visited = set()
        rec_stack = set()

        def visit(module, path):
            if module in rec_stack:
                # Found circular dependency
                cycle_start = path.index(module)
                circular.append(path[cycle_start:])
                return

            if module in visited:
                return

            visited.add(module)
            rec_stack.add(module)

            for dep in self.dependencies.get(module, []):
                visit(dep, path + [dep])

            rec_stack.remove(module)

        for module in self.dependencies:
            if module not in visited:
                visit(module, [module])

        return circular

    def generate_report(self) -> str:
        """Generate comprehensive dependency report."""
        metrics = self.calculate_metrics()

        report = [
            "# AIPM Python Module Dependency Analysis",
            "",
            f"**Total Modules**: {metrics['total_modules']}",
            f"**Total Dependencies**: {metrics['total_dependencies']}",
            f"**Average Dependencies per Module**: {metrics['avg_dependencies']:.2f}",
            f"**Most Dependent Module**: {metrics['most_dependent']} ({metrics['max_dependencies']} deps)",
            f"**Most Depended Upon**: {metrics['most_depended_upon']}",
            "",
            "## Module Statistics",
            "",
            "| Module | Lines | Imports | Internal Deps | External Deps |",
            "|--------|-------|---------|---------------|---------------|"
        ]

        # Sort modules by number of dependencies
        sorted_modules = sorted(self.module_info.items(),
                              key=lambda x: x[1]['internal_deps'],
                              reverse=True)

        for module, info in sorted_modules[:20]:  # Top 20 modules
            report.append(
                f"| {module.split('.')[-1]} | {info['lines']} | "
                f"{info['imports']} | {info['internal_deps']} | {info['external_deps']} |"
            )

        # Add circular dependencies if found
        if metrics['circular_dependencies']:
            report.extend([
                "",
                "## ⚠️ Circular Dependencies Detected",
                ""
            ])
            for cycle in metrics['circular_dependencies']:
                report.append(f"- {' → '.join(cycle)}")

        # Add external dependencies
        report.extend([
            "",
            "## External Dependencies",
            "",
            "| Module | External Libraries |",
            "|--------|-------------------|"
        ])

        for module, deps in list(self.external_deps.items())[:10]:
            if deps:
                report.append(f"| {module.split('.')[-1]} | {', '.join(list(deps)[:3])} |")

        return '\n'.join(report)


def main():
    """Generate dependency analysis for AIPM system."""
    # Analyze AIPM CLI
    aipm_root = Path('/Users/nigelcopley/.project_manager/aipm-cli')
    analyzer = DependencyAnalyzer(aipm_root)

    print("Analyzing AIPM codebase...")
    analyzer.analyze_directory(aipm_root / 'aipm_cli')

    # Generate reports
    print("\nGenerating dependency graph...")
    mermaid_graph = analyzer.generate_mermaid_graph()

    print("\nGenerating metrics report...")
    report = analyzer.generate_report()

    # Save outputs
    output_dir = Path('/Users/nigelcopley/.project_manager/docs/artifacts/analysis')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save Mermaid graph
    graph_file = output_dir / 'module-dependency-graph.md'
    with open(graph_file, 'w') as f:
        f.write("# AIPM Module Dependency Graph\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_graph)
        f.write("\n```\n")

    # Save detailed report
    report_file = output_dir / 'dependency-analysis-report.md'
    with open(report_file, 'w') as f:
        f.write(report)

    # Save JSON data
    json_file = output_dir / 'dependency-data.json'
    with open(json_file, 'w') as f:
        json.dump({
            'dependencies': {k: list(v) for k, v in analyzer.dependencies.items()},
            'external_deps': {k: list(v) for k, v in analyzer.external_deps.items()},
            'module_info': analyzer.module_info,
            'metrics': analyzer.calculate_metrics()
        }, f, indent=2)

    print(f"\n✅ Analysis complete!")
    print(f"📊 Graph saved to: {graph_file}")
    print(f"📝 Report saved to: {report_file}")
    print(f"💾 Data saved to: {json_file}")

    # Print summary
    metrics = analyzer.calculate_metrics()
    print(f"\n📈 Summary:")
    print(f"  - Total modules: {metrics['total_modules']}")
    print(f"  - Total dependencies: {metrics['total_dependencies']}")
    print(f"  - Most dependent: {metrics['most_dependent']}")
    print(f"  - Circular dependencies: {len(metrics['circular_dependencies'])}")


if __name__ == '__main__':
    main()