"""
React Plugin - Framework-Specific Context Extraction

Extracts React project facts and generates code amalgamations.
Library-aware: detects React Router, Redux, React Query, etc.

Pattern: BasePlugin implementation for React framework
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory


class ReactPlugin(BasePlugin):
    """
    React framework plugin for context extraction.

    Provides:
    1. Project facts (React version, routing, state management)
    2. Code amalgamations (components, hooks, contexts, reducers)
    3. Library-specific patterns (Router, Redux, Query, etc.)
    """

    @property
    def plugin_id(self) -> str:
        return "framework:react"

    @property
    def enriches(self) -> str:
        return "react"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.FRAMEWORK

    def detect(self, project_path: Path) -> float:
        """
        Detect React presence with 3-phase approach.

        Phase 1: Files (30%) - package.json with React
        Phase 2: Imports (40%) - React imports in code
        Phase 3: Structure (30%) - Component structure, public/, src/

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            package_json = project_path / "package.json"
            if package_json.exists():
                content = package_json.read_text()
                if '"react"' in content:
                    confidence += 0.30  # Definitive if in package.json

        except Exception:
            pass

        try:
            # Phase 2: Imports (0.4 max)
            js_files = list(project_path.glob("**/*.js")) + \
                      list(project_path.glob("**/*.jsx")) + \
                      list(project_path.glob("**/*.tsx"))

            for js_file in js_files[:20]:
                try:
                    content = js_file.read_text()
                    if "from 'react'" in content or 'from "react"' in content or "import React" in content:
                        confidence += 0.40
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 3: Structure (0.3 max)
            if (project_path / "public").exists():
                confidence += 0.10  # React app structure
            if (project_path / "src").exists() and any(project_path.glob("src/**/*.jsx")):
                confidence += 0.10  # JSX files in src/
            if (project_path / "public" / "index.html").exists():
                confidence += 0.10  # CRA structure

        except Exception:
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract React project facts.

        Returns technical facts about React configuration and libraries.
        """
        facts = {}

        # Framework info
        facts['framework'] = 'React'
        facts['react_version'] = self._get_react_version(project_path)

        # Detect installed libraries
        libraries = self._detect_react_libraries(project_path)
        facts['libraries'] = libraries

        # Project structure
        facts['project_type'] = self._detect_project_type(project_path)

        # Routing
        if libraries.get('has_router'):
            facts['routing'] = 'React Router'

        # State management
        state_mgmt = []
        if libraries.get('has_redux'):
            state_mgmt.append('Redux')
        if libraries.get('has_zustand'):
            state_mgmt.append('Zustand')
        if libraries.get('has_recoil'):
            state_mgmt.append('Recoil')
        if state_mgmt:
            facts['state_management'] = ', '.join(state_mgmt)

        # Data fetching
        if libraries.get('has_react_query'):
            facts['data_fetching'] = 'React Query'
        elif libraries.get('has_swr'):
            facts['data_fetching'] = 'SWR'

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate comprehensive React code amalgamations.

        Detects React ecosystem libraries and collects ALL relevant patterns.
        """
        amalgamations = {}

        # Detect React libraries
        libraries = self._detect_react_libraries(project_path)

        # === CORE REACT PATTERNS (always collect) ===
        amalgamations['components'] = self._collect_components(project_path)
        amalgamations['hooks'] = self._collect_hooks(project_path)
        amalgamations['contexts'] = self._collect_contexts(project_path)

        # === ROUTING PATTERNS ===
        if libraries.get('has_router'):
            amalgamations['routes'] = self._collect_routes(project_path)
        if libraries.get('has_tanstack_router'):
            amalgamations['tanstack_routes'] = self._collect_tanstack_routes(project_path)

        # === STATE MANAGEMENT ===
        if libraries.get('has_redux'):
            amalgamations['redux_slices'] = self._collect_redux_slices(project_path)
            amalgamations['redux_store'] = self._collect_redux_store(project_path)

        # === DATA FETCHING ===
        if libraries.get('has_react_query'):
            amalgamations['queries'] = self._collect_queries(project_path)

        # === UI LIBRARIES ===
        if libraries.get('has_radix'):
            amalgamations['radix_components'] = self._collect_radix_components(project_path)
        if libraries.get('has_shadcn'):
            amalgamations['ui_components'] = self._collect_ui_components(project_path)

        # === FORMS ===
        if libraries.get('has_react_hook_form'):
            amalgamations['forms'] = self._collect_forms(project_path)

        # === TABLES ===
        if libraries.get('has_tanstack_table'):
            amalgamations['tables'] = self._collect_tables(project_path)

        # === UTILITIES ===
        amalgamations['utils'] = self._collect_utils(project_path)

        return amalgamations

    # ========== Library Detection ==========

    def _detect_react_libraries(self, project_path: Path) -> Dict[str, bool]:
        """Detect which React ecosystem libraries are installed"""
        libraries = {
            # Routing
            'has_router': False,
            'has_tanstack_router': False,

            # State Management
            'has_redux': False,
            'has_zustand': False,
            'has_recoil': False,

            # Data Fetching
            'has_react_query': False,
            'has_swr': False,

            # UI Libraries
            'has_radix': False,
            'has_shadcn': False,

            # Forms
            'has_react_hook_form': False,

            # Tables
            'has_tanstack_table': False,
        }

        package_data = self._parse_package_json(project_path)
        if not package_data:
            return libraries

        deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

        # Routing
        if 'react-router' in deps or 'react-router-dom' in deps:
            libraries['has_router'] = True
        if '@tanstack/react-router' in deps:
            libraries['has_tanstack_router'] = True

        # State
        if 'redux' in deps or '@reduxjs/toolkit' in deps:
            libraries['has_redux'] = True
        if 'zustand' in deps:
            libraries['has_zustand'] = True
        if 'recoil' in deps:
            libraries['has_recoil'] = True

        # Data fetching
        if '@tanstack/react-query' in deps or 'react-query' in deps:
            libraries['has_react_query'] = True
        if 'swr' in deps:
            libraries['has_swr'] = True

        # UI libraries
        if any(k.startswith('@radix-ui/') for k in deps.keys()):
            libraries['has_radix'] = True
        if 'class-variance-authority' in deps or 'clsx' in deps or 'tailwind-merge' in deps:
            libraries['has_shadcn'] = True  # shadcn/ui indicators

        # Forms
        if 'react-hook-form' in deps:
            libraries['has_react_hook_form'] = True

        # Tables
        if '@tanstack/react-table' in deps:
            libraries['has_tanstack_table'] = True

        return libraries

    def _get_react_version(self, project_path: Path) -> Optional[str]:
        """Extract React version from package.json"""
        package_data = self._parse_package_json(project_path)
        if package_data and 'dependencies' in package_data:
            react_dep = package_data['dependencies'].get('react', '')
            # Extract version number (remove ^, ~, etc.)
            match = re.search(r'(\d+\.\d+\.\d+)', react_dep)
            if match:
                return match.group(1)
        return None

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
        """Detect if CRA, Vite, or custom setup"""
        if (project_path / "vite.config.js").exists() or (project_path / "vite.config.ts").exists():
            return "vite"
        elif (project_path / "public" / "index.html").exists() and (project_path / "src" / "index.js").exists():
            return "create-react-app"
        else:
            return "react_custom"

    def _detect_build_tool(self, project_path: Path) -> Optional[str]:
        """Detect build tool"""
        if (project_path / "vite.config.js").exists():
            return "vite"
        elif (project_path / "webpack.config.js").exists():
            return "webpack"
        return None

    # ========== Code Collection Methods ==========

    def _collect_components(self, project_path: Path) -> str:
        """Collect React components"""
        components_content = []
        for jsx_file in list(project_path.glob("**/*.jsx")) + list(project_path.glob("**/*.tsx")):
            try:
                content = jsx_file.read_text()
                # Look for component patterns
                if "export " in content and ("function " in content or "const " in content or "class " in content):
                    components_content.append(f"# {jsx_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(components_content[:30])

    def _collect_hooks(self, project_path: Path) -> str:
        """Collect custom React hooks (use* pattern)"""
        hooks_content = []
        for js_file in list(project_path.glob("**/use*.js")) + \
                       list(project_path.glob("**/use*.jsx")) + \
                       list(project_path.glob("**/use*.ts")) + \
                       list(project_path.glob("**/use*.tsx")) + \
                       list(project_path.glob("**/hooks/*.js*")) + \
                       list(project_path.glob("**/hooks/*.ts*")):
            try:
                content = js_file.read_text()
                hooks_content.append(f"# {js_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(hooks_content[:20])

    def _collect_contexts(self, project_path: Path) -> str:
        """Collect React Context definitions"""
        contexts_content = []
        for ctx_file in list(project_path.glob("**/*Context.js*")) + \
                        list(project_path.glob("**/*context.js*")) + \
                        list(project_path.glob("**/contexts/*.js*")):
            try:
                content = ctx_file.read_text()
                if "createContext" in content or "Context.Provider" in content:
                    contexts_content.append(f"# {ctx_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(contexts_content[:10])

    def _collect_routes(self, project_path: Path) -> str:
        """Collect React Router route definitions"""
        routes_content = []
        for route_file in list(project_path.glob("**/routes.js*")) + \
                         list(project_path.glob("**/Routes.js*")) + \
                         list(project_path.glob("**/router.js*")) + \
                         list(project_path.glob("**/App.js*")):
            try:
                content = route_file.read_text()
                if "Route" in content or "Router" in content or "Routes" in content:
                    routes_content.append(f"# {route_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(routes_content[:10])

    def _collect_redux_slices(self, project_path: Path) -> str:
        """Collect Redux Toolkit slices"""
        slices_content = []
        for slice_file in list(project_path.glob("**/*Slice.js")) + \
                          list(project_path.glob("**/*slice.js")) + \
                          list(project_path.glob("**/slices/*.js")):
            try:
                content = slice_file.read_text()
                slices_content.append(f"# {slice_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(slices_content[:15])

    def _collect_redux_store(self, project_path: Path) -> str:
        """Collect Redux store configuration"""
        store_content = []
        for store_file in list(project_path.glob("**/store.js")) + \
                         list(project_path.glob("**/store/index.js")):
            try:
                content = store_file.read_text()
                store_content.append(f"# {store_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(store_content[:5])

    def _collect_queries(self, project_path: Path) -> str:
        """Collect React Query hooks and queries"""
        queries_content = []
        for query_file in list(project_path.glob("**/queries/*.js*")) + \
                         list(project_path.glob("**/*Queries.js*")) + \
                         list(project_path.glob("**/use*Query.js*")):
            try:
                content = query_file.read_text()
                if "useQuery" in content or "useMutation" in content:
                    queries_content.append(f"# {query_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(queries_content[:15])

    def _collect_utils(self, project_path: Path) -> str:
        """Collect utility functions"""
        utils_content = []
        for utils_file in list(project_path.glob("**/utils/*.js*")) + \
                         list(project_path.glob("**/helpers/*.js*")) + \
                         list(project_path.glob("**/lib/*.js*")):
            try:
                content = utils_file.read_text()
                utils_content.append(f"# {utils_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue
        return "\n".join(utils_content[:20])

    def _collect_tanstack_routes(self, project_path: Path) -> str:
        """Collect TanStack Router route definitions"""
        routes_content = []
        for route_file in list(project_path.glob("**/routes/**/*.tsx")) + list(project_path.glob("**/routes/**/*.ts")):
            try:
                content = route_file.read_text()
                routes_content.append(f"# {route_file.relative_to(project_path)}\n{content}\n")
            except: continue
        return "\n".join(routes_content[:15])

    def _collect_radix_components(self, project_path: Path) -> str:
        """Collect Radix UI component usage"""
        radix_content = []
        for comp_file in project_path.glob("**/components/**/*.tsx"):
            try:
                content = comp_file.read_text()
                if "@radix-ui/" in content:
                    radix_content.append(f"# {comp_file.relative_to(project_path)}\n{content}\n")
            except: continue
        return "\n".join(radix_content[:20])

    def _collect_ui_components(self, project_path: Path) -> str:
        """Collect shadcn/ui style components"""
        ui_content = []
        ui_dir = project_path / "components" / "ui"
        if ui_dir.exists():
            for ui_file in ui_dir.glob("*.tsx"):
                try:
                    content = ui_file.read_text()
                    ui_content.append(f"# {ui_file.relative_to(project_path)}\n{content}\n")
                except: continue
        return "\n".join(ui_content[:25])

    def _collect_forms(self, project_path: Path) -> str:
        """Collect React Hook Form implementations"""
        forms_content = []
        for form_file in project_path.glob("**/*.tsx"):
            try:
                content = form_file.read_text()
                if "useForm" in content or "react-hook-form" in content:
                    forms_content.append(f"# {form_file.relative_to(project_path)}\n{content}\n")
            except: continue
        return "\n".join(forms_content[:15])

    def _collect_tables(self, project_path: Path) -> str:
        """Collect TanStack Table implementations"""
        tables_content = []
        for table_file in project_path.glob("**/*.tsx"):
            try:
                content = table_file.read_text()
                if "useReactTable" in content or "@tanstack/react-table" in content:
                    tables_content.append(f"# {table_file.relative_to(project_path)}\n{content}\n")
            except: continue
        return "\n".join(tables_content[:10])
