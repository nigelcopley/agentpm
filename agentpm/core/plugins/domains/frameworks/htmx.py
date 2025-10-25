"""
HTMX Plugin - Hypermedia Framework Context Extraction

Extracts HTMX usage patterns from HTML templates and JavaScript.
Focuses on hypermedia-driven architecture patterns.

Pattern: BasePlugin implementation for HTMX framework
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory


class HTMXPlugin(BasePlugin):
    """
    HTMX framework plugin for context extraction.

    Provides:
    1. Project facts (HTMX version, usage patterns, attributes)
    2. Code amalgamations (templates with hx-*, endpoints, partials)
    3. Hypermedia patterns (hx-get, hx-post, hx-swap, hx-trigger)
    """

    @property
    def plugin_id(self) -> str:
        return "framework:htmx"

    @property
    def enriches(self) -> str:
        return "htmx"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.FRAMEWORK

    def detect(self, project_path: Path) -> float:
        """
        Detect HTMX presence with 3-phase approach.

        Phase 1: Files (30%) - Script tags, CDN references
        Phase 2: Attributes (40%) - hx-* attributes in HTML
        Phase 3: Structure (30%) - Partial templates, HTMX endpoints

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            # Check for HTMX script tag in HTML files
            html_files = list(project_path.glob("**/*.html"))[:20]
            for html_file in html_files:
                try:
                    content = html_file.read_text()
                    if "htmx" in content.lower() or "unpkg.com/htmx" in content:
                        confidence += 0.30
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 2: Attributes (0.4 max) - Look for hx-* attributes
            hx_pattern = r'hx-(?:get|post|put|delete|patch|swap|target|trigger|select|vals)'
            for html_file in html_files[:30]:
                try:
                    content = html_file.read_text()
                    if re.search(hx_pattern, content, re.IGNORECASE):
                        confidence += 0.40
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 3: Structure (0.3 max)
            # Check for partials/ or fragments/ directories (HTMX pattern)
            if any(project_path.glob("**/partials")) or any(project_path.glob("**/fragments")):
                confidence += 0.15
            # Check for HTMX-style endpoints (often in templates/)
            if any(project_path.glob("**/templates/**/*.html")):
                confidence += 0.15

        except Exception:
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract HTMX project facts.

        Returns technical facts about HTMX usage and patterns.
        """
        facts = {}

        # Framework info
        facts['framework'] = 'HTMX'
        facts['htmx_version'] = self._get_htmx_version(project_path)

        # Usage patterns
        patterns = self._analyze_htmx_patterns(project_path)
        facts['common_attributes'] = patterns.get('attributes', [])
        facts['swap_strategies'] = patterns.get('swap_strategies', [])
        facts['trigger_patterns'] = patterns.get('triggers', [])

        # Architecture
        facts['architecture'] = 'hypermedia_driven'
        if any(project_path.glob("**/partials")):
            facts['partial_templates'] = True

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate HTMX code amalgamations.

        Collects hypermedia patterns and template organization.
        """
        amalgamations = {}

        # HTMX templates with hx-* attributes
        amalgamations['htmx_templates'] = self._collect_htmx_templates(project_path)

        # Partial templates
        amalgamations['partials'] = self._collect_partials(project_path)

        # HTMX endpoints (backend handlers)
        amalgamations['endpoints'] = self._collect_htmx_endpoints(project_path)

        return amalgamations

    # ========== Helper Methods ==========

    def _get_htmx_version(self, project_path: Path) -> Optional[str]:
        """Extract HTMX version from script tag"""
        html_files = list(project_path.glob("**/*.html"))[:10]
        for html_file in html_files:
            try:
                content = html_file.read_text()
                # Look for htmx@version in CDN URL
                match = re.search(r'htmx\.org@(\d+\.\d+\.\d+)', content)
                if match:
                    return match.group(1)
            except Exception:
                continue
        return None

    def _analyze_htmx_patterns(self, project_path: Path) -> Dict[str, List[str]]:
        """Analyze HTMX attribute usage patterns"""
        patterns = {
            'attributes': set(),
            'swap_strategies': set(),
            'triggers': set(),
        }

        html_files = list(project_path.glob("**/*.html"))[:50]
        for html_file in html_files:
            try:
                content = html_file.read_text()

                # Find hx-* attributes
                hx_attrs = re.findall(r'hx-(\w+)', content)
                patterns['attributes'].update(hx_attrs)

                # Find swap strategies
                swaps = re.findall(r'hx-swap=["\'](\w+)', content)
                patterns['swap_strategies'].update(swaps)

                # Find trigger patterns
                triggers = re.findall(r'hx-trigger=["\']([^"\']+)', content)
                patterns['triggers'].update(triggers)

            except Exception:
                continue

        return {
            'attributes': sorted(list(patterns['attributes']))[:20],
            'swap_strategies': sorted(list(patterns['swap_strategies'])),
            'triggers': sorted(list(patterns['triggers']))[:10],
        }

    def _collect_htmx_templates(self, project_path: Path) -> str:
        """Collect HTML templates using HTMX"""
        templates_content = []
        html_files = list(project_path.glob("**/*.html"))

        for html_file in html_files:
            try:
                content = html_file.read_text()
                # Only include if has hx-* attributes
                if re.search(r'hx-\w+', content):
                    templates_content.append(f"# {html_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(templates_content[:30])

    def _collect_partials(self, project_path: Path) -> str:
        """Collect partial templates (fragments)"""
        partials_content = []
        partial_patterns = [
            '**/partials/**/*.html',
            '**/fragments/**/*.html',
            '**/_*.html',  # Django partial convention
        ]

        for pattern in partial_patterns:
            for partial_file in project_path.glob(pattern):
                try:
                    content = partial_file.read_text()
                    partials_content.append(f"# {partial_file.relative_to(project_path)}\n{content}\n")
                except Exception:
                    continue

        return "\n".join(partials_content[:20])

    def _collect_htmx_endpoints(self, project_path: Path) -> str:
        """Collect backend endpoints that return HTMX responses"""
        endpoints_content = []

        # Django views that return partials
        for views_file in project_path.glob("**/views.py"):
            try:
                content = views_file.read_text()
                # Look for HTMX-specific patterns
                if "render" in content and ("partial" in content.lower() or "fragment" in content.lower()):
                    endpoints_content.append(f"# {views_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(endpoints_content[:10])
