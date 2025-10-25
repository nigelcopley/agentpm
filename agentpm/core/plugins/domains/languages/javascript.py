"""
JavaScript Plugin - Language-Specific Context Extraction

Extracts JavaScript project facts and generates code amalgamations.
Detects npm/yarn/pnpm, analyzes package.json, and collects JS patterns.

Pattern: BasePlugin implementation for JavaScript language
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory


class JavaScriptPlugin(BasePlugin):
    """
    JavaScript language plugin for context extraction.

    Provides:
    1. Project facts (Node version, package manager, dependencies)
    2. Code amalgamations (functions, classes, modules, utilities)
    3. Library detection (React, Vue, Express, etc.)
    """

    @property
    def plugin_id(self) -> str:
        return "lang:javascript"

    @property
    def enriches(self) -> str:
        return "javascript"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.LANGUAGE

    def detect(self, project_path: Path) -> float:
        """
        Detect JavaScript presence with 3-phase approach.

        Phase 1: Files (30%) - package.json, node configs
        Phase 2: Extensions (40%) - Count .js/.mjs/.cjs files
        Phase 3: Structure (30%) - node_modules, src/, package organization

        Returns:
            Confidence score 0.0-1.0 (graceful degradation on errors)
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            if (project_path / "package.json").exists():
                confidence += 0.20  # Strong signal
            if (project_path / "package-lock.json").exists() or \
               (project_path / "yarn.lock").exists() or \
               (project_path / "pnpm-lock.yaml").exists():
                confidence += 0.10  # Package manager lock file

        except Exception:
            pass

        try:
            # Phase 2: Extensions (0.4 max) - Count JS files
            js_files = list(project_path.glob("**/*.js")) + \
                      list(project_path.glob("**/*.mjs")) + \
                      list(project_path.glob("**/*.cjs"))
            js_file_count = len(js_files)

            if js_file_count > 0:
                if js_file_count >= 50:
                    confidence += 0.40
                elif js_file_count >= 20:
                    confidence += 0.35
                elif js_file_count >= 10:
                    confidence += 0.30
                else:
                    confidence += 0.20

        except Exception:
            pass

        try:
            # Phase 3: Structure (0.3 max)
            if (project_path / "src").exists():
                confidence += 0.10
            if (project_path / "node_modules").exists():
                confidence += 0.10  # May be filtered by gitignore
            # Check for JS package structure
            if any(p.is_dir() and (p / "package.json").exists()
                   for p in project_path.iterdir()
                   if not p.name.startswith('.')):
                confidence += 0.10

        except Exception:
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract JavaScript project facts.

        Returns technical facts about JavaScript configuration and structure.
        """
        facts = {}

        # Language info
        facts['language'] = 'JavaScript'
        facts['node_version'] = self._get_node_version(project_path)
        facts['package_manager'] = self._detect_package_manager(project_path)

        # Dependencies
        package_data = self._parse_package_json(project_path)
        if package_data:
            facts['dependencies'] = package_data.get('dependencies', {})
            facts['dev_dependencies'] = package_data.get('devDependencies', {})
            facts['scripts'] = list(package_data.get('scripts', {}).keys())

        # Project structure
        facts['project_type'] = self._detect_project_type(project_path)
        facts['entry_point'] = self._find_entry_point(project_path)

        # Build tools
        facts['build_tool'] = self._detect_build_tool(project_path)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate JavaScript code amalgamations.

        Detects libraries and collects patterns comprehensively.
        """
        amalgamations = {}

        # Core JavaScript patterns (always collect)
        amalgamations['functions'] = self._collect_functions(project_path)
        amalgamations['classes'] = self._collect_classes(project_path)
        amalgamations['modules'] = self._collect_modules(project_path)
        amalgamations['config'] = self._collect_config(project_path)

        return amalgamations

    # ========== Helper Methods ==========

    def _get_node_version(self, project_path: Path) -> Optional[str]:
        """Extract Node.js version from .nvmrc or package.json"""
        # Check .nvmrc
        nvmrc = project_path / ".nvmrc"
        if nvmrc.exists():
            try:
                return nvmrc.read_text().strip()
            except Exception:
                pass

        # Check package.json engines
        package_data = self._parse_package_json(project_path)
        if package_data and 'engines' in package_data:
            node_version = package_data['engines'].get('node')
            if node_version:
                return node_version

        return None

    def _detect_package_manager(self, project_path: Path) -> str:
        """Detect npm, yarn, or pnpm"""
        if (project_path / "pnpm-lock.yaml").exists():
            return "pnpm"
        elif (project_path / "yarn.lock").exists():
            return "yarn"
        elif (project_path / "package-lock.json").exists():
            return "npm"
        return "npm"  # Default

    def _parse_package_json(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Parse package.json"""
        package_json = project_path / "package.json"
        if not package_json.exists():
            return None

        try:
            return json.loads(package_json.read_text())
        except Exception:
            return None

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect JavaScript project type"""
        package_data = self._parse_package_json(project_path)
        if not package_data:
            return "javascript_project"

        deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

        if 'next' in deps:
            return "nextjs"
        elif 'react' in deps:
            return "react"
        elif 'vue' in deps:
            return "vue"
        elif 'express' in deps:
            return "express_api"
        elif '@angular/core' in deps:
            return "angular"
        else:
            return "javascript_project"

    def _find_entry_point(self, project_path: Path) -> Optional[str]:
        """Find main entry point"""
        package_data = self._parse_package_json(project_path)
        if package_data and 'main' in package_data:
            return package_data['main']

        # Common entry points
        for entry in ['index.js', 'app.js', 'server.js', 'main.js', 'src/index.js']:
            if (project_path / entry).exists():
                return entry

        return None

    def _detect_build_tool(self, project_path: Path) -> Optional[str]:
        """Detect build tool (webpack, vite, parcel, etc.)"""
        if (project_path / "webpack.config.js").exists():
            return "webpack"
        elif (project_path / "vite.config.js").exists() or (project_path / "vite.config.ts").exists():
            return "vite"
        elif (project_path / "rollup.config.js").exists():
            return "rollup"
        elif (project_path / "parcel.config.js").exists():
            return "parcel"

        # Check package.json scripts
        package_data = self._parse_package_json(project_path)
        if package_data and 'scripts' in package_data:
            build_script = package_data['scripts'].get('build', '')
            if 'vite' in build_script:
                return "vite"
            elif 'webpack' in build_script:
                return "webpack"

        return None

    # ========== Code Collection Methods ==========

    def _collect_functions(self, project_path: Path) -> str:
        """Collect JavaScript function definitions"""
        functions_content = []
        for js_file in project_path.glob("**/*.js"):
            try:
                content = js_file.read_text()
                # Look for function definitions
                if "function " in content or "const " in content or "export " in content:
                    functions_content.append(f"# {js_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(functions_content[:20])

    def _collect_classes(self, project_path: Path) -> str:
        """Collect JavaScript class definitions"""
        classes_content = []
        for js_file in project_path.glob("**/*.js"):
            try:
                content = js_file.read_text()
                if "class " in content:
                    classes_content.append(f"# {js_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(classes_content[:20])

    def _collect_modules(self, project_path: Path) -> str:
        """Collect module exports and imports"""
        modules_content = []
        for js_file in project_path.glob("**/*.js"):
            try:
                content = js_file.read_text()
                # Look for import/export statements
                if "import " in content or "export " in content or "require(" in content:
                    # Extract just imports/exports
                    lines = [l for l in content.split('\n') if 'import ' in l or 'export ' in l or 'require(' in l]
                    if lines:
                        modules_content.append(f"# {js_file.relative_to(project_path)}\n" + "\n".join(lines[:20]) + "\n")
            except Exception:
                continue
        return "\n".join(modules_content[:30])

    def _collect_config(self, project_path: Path) -> str:
        """Collect JavaScript configuration files"""
        config_content = []
        config_patterns = [
            '**/.eslintrc*',
            '**/.prettierrc*',
            '**/tsconfig.json',
            '**/jsconfig.json',
            '**/babel.config.*',
            '**/.babelrc*',
        ]

        for pattern in config_patterns:
            for config_file in project_path.glob(pattern):
                try:
                    content = config_file.read_text()
                    config_content.append(f"# {config_file.relative_to(project_path)}\n{content}\n")
                except Exception:
                    continue

        return "\n".join(config_content[:10])
