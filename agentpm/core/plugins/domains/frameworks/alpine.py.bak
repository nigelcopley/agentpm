"""
Alpine.js Plugin - Reactive Framework Context Extraction

Extracts Alpine.js usage patterns from HTML templates.
Focuses on reactive data binding and component patterns.

Pattern: BasePlugin implementation for Alpine.js framework
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory


class AlpinePlugin(BasePlugin):
    """
    Alpine.js framework plugin for context extraction.

    Provides:
    1. Project facts (Alpine version, directive usage)
    2. Code amalgamations (components with x-data, reusable patterns)
    3. Reactive patterns (x-bind, x-model, x-show, x-if)
    """

    @property
    def plugin_id(self) -> str:
        return "framework:alpine"

    @property
    def enriches(self) -> str:
        return "alpine"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.FRAMEWORK

    def detect(self, project_path: Path) -> float:
        """
        Detect Alpine.js presence with 3-phase approach.

        Phase 1: Files (30%) - Script tags, CDN references
        Phase 2: Directives (40%) - x-* attributes in HTML
        Phase 3: Structure (30%) - Component organization

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            html_files = list(project_path.glob("**/*.html"))[:20]
            for html_file in html_files:
                try:
                    content = html_file.read_text()
                    if "alpine" in content.lower() or "alpinejs" in content:
                        confidence += 0.30
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 2: Directives (0.4 max) - Look for x-* directives
            x_pattern = r'x-(?:data|bind|model|show|if|for|on|text|html|init)'
            for html_file in html_files[:30]:
                try:
                    content = html_file.read_text()
                    if re.search(x_pattern, content):
                        confidence += 0.40
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 3: Structure (0.3 max)
            # Alpine components often in components/ directory
            if any(project_path.glob("**/components/**/*.html")):
                confidence += 0.15
            # Check for Alpine.store usage
            if any("Alpine.store" in html_file.read_text()
                   for html_file in html_files[:10]
                   if html_file.exists()):
                confidence += 0.15

        except Exception:
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract Alpine.js project facts.

        Returns technical facts about Alpine usage and patterns.
        """
        facts = {}

        # Framework info
        facts['framework'] = 'Alpine.js'
        facts['alpine_version'] = self._get_alpine_version(project_path)

        # Usage patterns
        patterns = self._analyze_alpine_patterns(project_path)
        facts['common_directives'] = patterns.get('directives', [])
        facts['event_handlers'] = patterns.get('events', [])
        facts['uses_store'] = patterns.get('uses_store', False)
        facts['uses_magic'] = patterns.get('uses_magic', False)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate Alpine.js code amalgamations.

        Collects reactive components and patterns.
        """
        amalgamations = {}

        # Components with x-data
        amalgamations['components'] = self._collect_alpine_components(project_path)

        # Stores and global state
        amalgamations['stores'] = self._collect_alpine_stores(project_path)

        # Reusable patterns
        amalgamations['patterns'] = self._collect_alpine_patterns(project_path)

        return amalgamations

    # ========== Helper Methods ==========

    def _get_alpine_version(self, project_path: Path) -> Optional[str]:
        """Extract Alpine.js version from script tag"""
        html_files = list(project_path.glob("**/*.html"))[:10]
        for html_file in html_files:
            try:
                content = html_file.read_text()
                # Look for alpine@version in CDN URL
                match = re.search(r'alpine(?:js)?@(\d+\.\d+\.\d+)', content, re.IGNORECASE)
                if match:
                    return match.group(1)
            except Exception:
                continue
        return None

    def _analyze_alpine_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Alpine.js usage patterns"""
        patterns = {
            'directives': set(),
            'events': set(),
            'uses_store': False,
            'uses_magic': False,
        }

        html_files = list(project_path.glob("**/*.html"))[:50]
        for html_file in html_files:
            try:
                content = html_file.read_text()

                # Find x-* directives
                x_dirs = re.findall(r'x-(\w+)', content)
                patterns['directives'].update(x_dirs)

                # Find event handlers
                events = re.findall(r'@(\w+)', content)
                patterns['events'].update(events)

                # Check for stores and magic
                if "Alpine.store" in content:
                    patterns['uses_store'] = True
                if "$" in content and "x-" in content:  # Magic properties like $el, $refs
                    patterns['uses_magic'] = True

            except Exception:
                continue

        return {
            'directives': sorted(list(patterns['directives']))[:20],
            'events': sorted(list(patterns['events']))[:20],
            'uses_store': patterns['uses_store'],
            'uses_magic': patterns['uses_magic'],
        }

    def _collect_alpine_components(self, project_path: Path) -> str:
        """Collect templates with x-data (Alpine components)"""
        components_content = []
        html_files = list(project_path.glob("**/*.html"))

        for html_file in html_files:
            try:
                content = html_file.read_text()
                if "x-data" in content:
                    components_content.append(f"# {html_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(components_content[:30])

    def _collect_alpine_stores(self, project_path: Path) -> str:
        """Collect Alpine.store definitions"""
        stores_content = []

        # Check HTML and JS files for store definitions
        for file_pattern in ["**/*.html", "**/*.js"]:
            for store_file in project_path.glob(file_pattern):
                try:
                    content = store_file.read_text()
                    if "Alpine.store" in content:
                        stores_content.append(f"# {store_file.relative_to(project_path)}\n{content}\n")
                except Exception:
                    continue

        return "\n".join(stores_content[:10])

    def _collect_alpine_patterns(self, project_path: Path) -> str:
        """Collect common Alpine.js patterns"""
        patterns_content = []
        html_files = list(project_path.glob("**/*.html"))

        for html_file in html_files:
            try:
                content = html_file.read_text()
                # Look for interesting patterns
                if any(pattern in content for pattern in ['x-show', 'x-if', 'x-for', '@click', 'x-model']):
                    # Extract the div/section with Alpine directives
                    patterns_content.append(f"# {html_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(patterns_content[:20])
