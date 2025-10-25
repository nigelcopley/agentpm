"""
Unit tests for graph_builders path normalization.

Tests verify that file paths and import statements are normalized to consistent
module format (dot-separated, no .py extension) to prevent duplicate nodes.

Bug Context:
- Before fix: Files created duplicate nodes
  * Node 1: "agentpm/cli/utils/project.py" (from file scan)
  * Node 2: "agentpm/cli/utils/project" (from import statement)
- After fix: All nodes use consistent format "agentpm.cli.utils.project"
"""

import pytest
from pathlib import Path
import networkx as nx
import tempfile
import shutil

from agentpm.utils.graph_builders import (
    build_import_graph,
    build_dependency_graph,
    _normalize_file_path_to_module,
    _normalize_import_path,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestPathNormalization:
    """Test path normalization functions."""

    def test_normalize_file_path_removes_py_extension(self):
        """Should remove .py extension from file paths."""
        assert _normalize_file_path_to_module("module.py") == "module"
        assert _normalize_file_path_to_module("path/to/module.py") == "path.to.module"

    def test_normalize_file_path_handles_init_py(self):
        """Should remove __init__.py suffix for package imports."""
        assert _normalize_file_path_to_module("package/__init__.py") == "package"
        assert _normalize_file_path_to_module("path/to/package/__init__.py") == "path.to.package"

    def test_normalize_file_path_converts_slashes_to_dots(self):
        """Should convert path separators to dots."""
        assert _normalize_file_path_to_module("a/b/c.py") == "a.b.c"
        assert _normalize_file_path_to_module("agentpm/core/database.py") == "agentpm.core.database"

    def test_normalize_import_path_absolute_imports(self):
        """Should keep absolute imports as-is (already in dot format)."""
        source = Path("/project/agentpm/cli/main.py")
        project = Path("/project")

        # Absolute imports already use dots
        result = _normalize_import_path("agentpm.core.database", source, project)
        assert result == "agentpm.core.database"

    def test_normalize_import_path_relative_imports(self):
        """Should resolve relative imports to module format."""
        source = Path("/project/agentpm/cli/commands/work_item/create.py")
        project = Path("/project")

        # Relative import: from ...core import database
        # Starting from: agentpm/cli/commands/work_item/
        # Go up 3 levels: agentpm/cli/commands → agentpm/cli → agentpm/
        # Then add core.database: agentpm/cli/core.database
        # (Note: This would be wrong import path in real code, but tests normalization logic)
        result = _normalize_import_path("...core.database", source, project)
        assert result == "agentpm.cli.core.database"


class TestBuildImportGraphNoDuplicates:
    """Test build_import_graph() prevents duplicate nodes."""

    def test_no_duplicate_nodes_for_same_module(self, temp_project_dir):
        """File path and import path should create single node."""
        project = temp_project_dir

        imports_by_file = {
            str(project / "agentpm/cli/main.py"): ["agentpm.core.database"],
            str(project / "agentpm/core/database.py"): [],
        }

        graph = build_import_graph(imports_by_file, project)

        # Should have exactly 2 nodes (not 3 or 4)
        assert graph.number_of_nodes() == 2

        # Both nodes should use dot format
        nodes = list(graph.nodes())
        assert "agentpm.cli.main" in nodes
        assert "agentpm.core.database" in nodes

        # No nodes with slashes or .py
        for node in nodes:
            assert "/" not in str(node)
            assert not str(node).endswith(".py")

    def test_edge_connects_normalized_nodes(self, temp_project_dir):
        """Edge should connect normalized node names."""
        project = temp_project_dir

        imports_by_file = {
            str(project / "agentpm/cli/main.py"): ["agentpm.core.database"],
        }

        graph = build_import_graph(imports_by_file, project)

        # Edge should exist between normalized names
        assert graph.has_edge("agentpm.cli.main", "agentpm.core.database")

    def test_multiple_files_importing_same_module(self, temp_project_dir):
        """Multiple importers of same module should not create duplicates."""
        project = temp_project_dir

        imports_by_file = {
            str(project / "agentpm/cli/main.py"): ["agentpm.core.database"],
            str(project / "agentpm/cli/utils.py"): ["agentpm.core.database"],
            str(project / "agentpm/core/database.py"): [],
        }

        graph = build_import_graph(imports_by_file, project)

        # Should have exactly 3 nodes
        assert graph.number_of_nodes() == 3

        # database module should have 2 incoming edges
        assert graph.in_degree("agentpm.core.database") == 2

    def test_init_py_normalized_correctly(self, temp_project_dir):
        """__init__.py files should be normalized to package name."""
        project = temp_project_dir

        imports_by_file = {
            str(project / "agentpm/cli/__init__.py"): ["agentpm.core"],
            str(project / "agentpm/core/__init__.py"): [],
        }

        graph = build_import_graph(imports_by_file, project)

        # Should have exactly 2 nodes
        assert graph.number_of_nodes() == 2

        # Nodes should be package names (no __init__)
        nodes = list(graph.nodes())
        assert "agentpm.cli" in nodes
        assert "agentpm.core" in nodes

        # Edge should exist
        assert graph.has_edge("agentpm.cli", "agentpm.core")


class TestBuildDependencyGraphNormalization:
    """Test build_dependency_graph() normalization."""

    def test_dependency_graph_uses_normalized_paths(self):
        """Nodes should be normalized even with custom extraction function."""
        file_paths = [
            Path("agentpm/cli/main.py"),
            Path("agentpm/core/database.py"),
        ]

        # Custom extraction function that returns module names
        def extract_deps(path: Path) -> list:
            if "main" in str(path):
                return ["agentpm.core.database"]
            return []

        graph = build_dependency_graph(file_paths, extract_deps)

        # All nodes should be normalized
        nodes = list(graph.nodes())
        assert "agentpm.cli.main" in nodes
        assert "agentpm.core.database" in nodes

        # No slashes or .py extensions
        for node in nodes:
            assert "/" not in str(node)
            assert not str(node).endswith(".py")


class TestGraphDepthCalculation:
    """Test that normalized graphs allow correct depth calculation."""

    def test_max_depth_calculation_on_simple_chain(self, temp_project_dir):
        """Max depth should work on simple dependency chain."""
        project = temp_project_dir

        # Create chain: A → B → C → D
        imports_by_file = {
            str(project / "a.py"): ["b"],
            str(project / "b.py"): ["c"],
            str(project / "c.py"): ["d"],
            str(project / "d.py"): [],
        }

        graph = build_import_graph(imports_by_file, project)

        # Should be acyclic
        assert nx.is_directed_acyclic_graph(graph)

        # Max depth should be 3 (A at level 0, D at level 3)
        max_depth = nx.dag_longest_path_length(graph)
        assert max_depth == 3

    def test_no_duplicate_breaks_in_chain(self, temp_project_dir):
        """Duplicates used to break chains - verify they don't anymore."""
        project = temp_project_dir

        # Before fix: each node would create duplicate, breaking chain
        imports_by_file = {
            str(project / "agentpm/cli/main.py"): ["agentpm.core.workflow"],
            str(project / "agentpm/core/workflow.py"): ["agentpm.core.database"],
            str(project / "agentpm/core/database.py"): ["agentpm.core.models"],
            str(project / "agentpm/core/models.py"): [],
        }

        graph = build_import_graph(imports_by_file, project)

        # Chain should be connected (no duplicate breaks)
        assert nx.has_path(graph, "agentpm.cli.main", "agentpm.core.models")

        # Max depth should be 3
        max_depth = nx.dag_longest_path_length(graph)
        assert max_depth == 3


class TestEdgeCaseHandling:
    """Test edge cases in normalization."""

    def test_file_without_py_extension(self):
        """Should handle files without .py extension gracefully."""
        result = _normalize_file_path_to_module("README")
        assert result == "README"

    def test_deeply_nested_path(self):
        """Should handle deeply nested paths."""
        result = _normalize_file_path_to_module("a/b/c/d/e/f/g.py")
        assert result == "a.b.c.d.e.f.g"

    def test_empty_path(self):
        """Should handle empty path."""
        result = _normalize_file_path_to_module("")
        assert result == ""

    def test_single_module_name(self):
        """Should handle single module name (no path separators)."""
        result = _normalize_file_path_to_module("module")
        assert result == "module"
