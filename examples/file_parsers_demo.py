#!/usr/bin/env python3
"""
File Parsers Demo

Demonstrates usage of file_parsers.py utilities for extracting
project metadata and dependencies.

Usage:
    python examples/file_parsers_demo.py [project_path]

Example:
    python examples/file_parsers_demo.py .
    python examples/file_parsers_demo.py /path/to/project
"""

import sys
from pathlib import Path
from typing import Dict, Any

from agentpm.utils.file_parsers import (
    parse_toml,
    parse_yaml,
    parse_json,
    parse_ini,
    parse_python_dependencies,
    parse_javascript_dependencies,
    TOML_AVAILABLE,
    YAML_AVAILABLE,
)


def analyze_python_project(project_path: Path) -> Dict[str, Any]:
    """Analyze Python project structure and dependencies."""
    print("\n" + "=" * 60)
    print("Python Project Analysis")
    print("=" * 60)

    analysis = {}

    # Extract dependencies
    print("\n📦 Dependencies:")
    deps = parse_python_dependencies(project_path)
    analysis['dependencies'] = deps

    print(f"  Source: {deps['source']}")
    print(f"  Runtime packages: {len(deps['runtime'])}")
    print(f"  Dev packages: {len(deps['dev'])}")

    if deps['runtime']:
        print("\n  Runtime (first 10):")
        for dep in deps['runtime'][:10]:
            print(f"    - {dep}")

    if deps['dev']:
        print("\n  Dev (first 10):")
        for dep in deps['dev'][:10]:
            print(f"    - {dep}")

    # Parse pyproject.toml if available
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists() and TOML_AVAILABLE:
        print("\n⚙️  pyproject.toml:")
        pyproject = parse_toml(pyproject_path)
        if pyproject:
            # Try Poetry format
            poetry = pyproject.get("tool", {}).get("poetry", {})
            if poetry:
                print(f"  Name: {poetry.get('name')}")
                print(f"  Version: {poetry.get('version')}")
                print(f"  Description: {poetry.get('description')}")

            # Try PEP 621 format
            project = pyproject.get("project", {})
            if project:
                print(f"  Name: {project.get('name')}")
                print(f"  Version: {project.get('version')}")
                print(f"  Description: {project.get('description')}")

            # Show build tools
            build_system = pyproject.get("build-system", {})
            if build_system:
                print(f"  Build backend: {build_system.get('build-backend')}")

            analysis['metadata'] = {
                'poetry': poetry,
                'project': project,
                'build_system': build_system
            }

    # Parse setup.cfg if available
    setup_cfg_path = project_path / "setup.cfg"
    if setup_cfg_path.exists():
        print("\n⚙️  setup.cfg:")
        setup_cfg = parse_ini(setup_cfg_path)
        if setup_cfg:
            metadata = setup_cfg.get("metadata", {})
            print(f"  Name: {metadata.get('name')}")
            print(f"  Version: {metadata.get('version')}")

    return analysis


def analyze_javascript_project(project_path: Path) -> Dict[str, Any]:
    """Analyze JavaScript/Node.js project structure and dependencies."""
    print("\n" + "=" * 60)
    print("JavaScript Project Analysis")
    print("=" * 60)

    analysis = {}

    # Check for package.json
    package_json_path = project_path / "package.json"
    if not package_json_path.exists():
        print("\n❌ No package.json found")
        return analysis

    # Extract dependencies
    print("\n📦 Dependencies:")
    deps = parse_javascript_dependencies(project_path)
    analysis['dependencies'] = deps

    print(f"  Source: {deps['source']}")
    print(f"  Runtime: {len(deps['runtime'])} packages")
    print(f"  Dev: {len(deps['dev'])} packages")
    print(f"  Peer: {len(deps['peer'])} packages")
    print(f"  Optional: {len(deps['optional'])} packages")

    if deps['runtime']:
        print("\n  Runtime (first 10):")
        for dep in deps['runtime'][:10]:
            print(f"    - {dep}")

    # Parse package.json for metadata
    print("\n⚙️  package.json:")
    package = parse_json(package_json_path)
    if package:
        print(f"  Name: {package.get('name')}")
        print(f"  Version: {package.get('version')}")
        print(f"  Description: {package.get('description')}")

        # Show scripts
        scripts = package.get("scripts", {})
        if scripts:
            print("\n  Scripts:")
            for name in list(scripts.keys())[:10]:
                print(f"    - {name}")

        # Show engines
        engines = package.get("engines", {})
        if engines:
            print("\n  Engines:")
            for name, version in engines.items():
                print(f"    - {name}: {version}")

        analysis['metadata'] = package

    return analysis


def analyze_ci_cd(project_path: Path) -> Dict[str, Any]:
    """Analyze CI/CD configuration."""
    print("\n" + "=" * 60)
    print("CI/CD Configuration")
    print("=" * 60)

    analysis = {}

    if not YAML_AVAILABLE:
        print("\n⚠️  PyYAML not available - skipping YAML analysis")
        return analysis

    # Check for GitLab CI
    gitlab_ci_path = project_path / ".gitlab-ci.yml"
    if gitlab_ci_path.exists():
        print("\n🔧 GitLab CI (.gitlab-ci.yml):")
        gitlab_ci = parse_yaml(gitlab_ci_path)
        if gitlab_ci:
            stages = gitlab_ci.get("stages", [])
            print(f"  Stages: {', '.join(stages) if stages else 'none'}")

            # Count jobs
            jobs = [k for k, v in gitlab_ci.items() if isinstance(v, dict) and k not in ('variables', 'stages')]
            print(f"  Jobs: {len(jobs)}")

            analysis['gitlab_ci'] = {
                'stages': stages,
                'jobs': jobs
            }

    # Check for GitHub Actions
    github_workflows = project_path / ".github" / "workflows"
    if github_workflows.exists():
        print("\n🔧 GitHub Actions:")
        workflows = list(github_workflows.glob("*.yml")) + list(github_workflows.glob("*.yaml"))
        print(f"  Workflows: {len(workflows)}")

        for workflow_path in workflows:
            workflow = parse_yaml(workflow_path)
            if workflow:
                print(f"  - {workflow_path.name}: {workflow.get('name', 'unnamed')}")

        analysis['github_actions'] = [w.name for w in workflows]

    return analysis


def main():
    """Main entry point."""
    # Get project path from command line or use current directory
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path.cwd()

    if not project_path.exists():
        print(f"❌ Error: Path not found: {project_path}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"Analyzing Project: {project_path.resolve()}")
    print("=" * 60)

    # Check library availability
    print("\n📚 Library Availability:")
    print(f"  TOML: {'✅ Available' if TOML_AVAILABLE else '❌ Not available'}")
    print(f"  YAML: {'✅ Available' if YAML_AVAILABLE else '❌ Not available'}")

    # Detect project type
    has_python = (
        (project_path / "pyproject.toml").exists() or
        (project_path / "setup.py").exists() or
        (project_path / "requirements.txt").exists()
    )

    has_javascript = (project_path / "package.json").exists()

    # Analyze based on project type
    if has_python:
        analyze_python_project(project_path)

    if has_javascript:
        analyze_javascript_project(project_path)

    if not has_python and not has_javascript:
        print("\n❌ No Python or JavaScript project detected")
        print("   Looking for: pyproject.toml, setup.py, requirements.txt, package.json")

    # Always check for CI/CD
    analyze_ci_cd(project_path)

    print("\n" + "=" * 60)
    print("Analysis Complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
