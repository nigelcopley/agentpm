"""
Tailwind CSS Plugin - Utility-First CSS Framework Context Extraction

Extracts Tailwind usage patterns, configuration, and component patterns.

Pattern: BasePlugin implementation for Tailwind CSS
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory


class TailwindPlugin(BasePlugin):
    """
    Tailwind CSS framework plugin for context extraction.

    Provides:
    1. Project facts (Tailwind version, config, plugins, theme)
    2. Code amalgamations (config, custom utilities, component patterns)
    3. Usage patterns (common class combinations, responsive design)
    """

    @property
    def plugin_id(self) -> str:
        return "framework:tailwind"

    @property
    def enriches(self) -> str:
        return "tailwind"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.FRAMEWORK

    def detect(self, project_path: Path) -> float:
        """
        Detect Tailwind CSS presence with 3-phase approach.

        Phase 1: Files (30%) - tailwind.config.js, postcss.config.js
        Phase 2: Content (40%) - Utility classes in HTML/JSX
        Phase 3: Structure (30%) - Build setup, CDN usage

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            if (project_path / "tailwind.config.js").exists() or \
               (project_path / "tailwind.config.ts").exists() or \
               (project_path / "tailwind.config.cjs").exists():
                confidence += 0.30  # Definitive signal

        except Exception:
            pass

        try:
            # Phase 2: Content (0.4 max) - Look for Tailwind utility classes
            template_files = list(project_path.glob("**/*.html")) + \
                           list(project_path.glob("**/*.jsx")) + \
                           list(project_path.glob("**/*.tsx"))

            tailwind_pattern = r'class(?:Name)?=["\'](?:[^"\']*(?:flex|grid|bg-|text-|p-|m-|w-|h-)[^"\']*)'

            for template_file in template_files[:30]:
                try:
                    content = template_file.read_text()
                    if re.search(tailwind_pattern, content):
                        confidence += 0.40
                        break
                except Exception:
                    continue

        except Exception:
            pass

        try:
            # Phase 3: Structure (0.3 max)
            # Check package.json for tailwindcss
            package_json = project_path / "package.json"
            if package_json.exists():
                content = package_json.read_text()
                if "tailwindcss" in content:
                    confidence += 0.15

            # Check postcss.config.js
            if (project_path / "postcss.config.js").exists():
                try:
                    content = (project_path / "postcss.config.js").read_text()
                    if "tailwind" in content.lower():
                        confidence += 0.15
                except Exception:
                    pass

        except Exception:
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract Tailwind CSS project facts.

        Returns technical facts about Tailwind configuration and usage.
        """
        facts = {}

        # Framework info
        facts['framework'] = 'Tailwind CSS'
        facts['tailwind_version'] = self._get_tailwind_version(project_path)

        # Configuration
        config_data = self._parse_tailwind_config(project_path)
        if config_data:
            facts['custom_theme'] = bool(config_data.get('theme'))
            facts['plugins'] = self._extract_tailwind_plugins(config_data)
            facts['purge_enabled'] = bool(config_data.get('content') or config_data.get('purge'))

        # Usage patterns
        facts['common_utilities'] = self._analyze_utility_usage(project_path)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate Tailwind CSS code amalgamations.

        Collects configuration, custom utilities, and component patterns.
        """
        amalgamations = {}

        # Tailwind configuration
        amalgamations['config'] = self._collect_tailwind_config(project_path)

        # Custom CSS (if any)
        amalgamations['custom_css'] = self._collect_custom_css(project_path)

        # Component patterns (common utility combinations)
        amalgamations['component_patterns'] = self._collect_component_patterns(project_path)

        return amalgamations

    # ========== Helper Methods ==========

    def _get_tailwind_version(self, project_path: Path) -> Optional[str]:
        """Extract Tailwind version from package.json"""
        package_json = project_path / "package.json"
        if not package_json.exists():
            return None

        try:
            data = json.loads(package_json.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

            tailwind_dep = deps.get('tailwindcss', '')
            match = re.search(r'(\d+\.\d+\.\d+)', tailwind_dep)
            if match:
                return match.group(1)
        except Exception:
            pass

        return None

    def _parse_tailwind_config(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Parse tailwind.config.js (simplified - just extract structure)"""
        config_files = list(project_path.glob("tailwind.config.*"))
        if not config_files:
            return None

        try:
            content = config_files[0].read_text()
            # Basic extraction - just check for key sections
            return {
                'theme': 'theme' in content,
                'plugins': 'plugins' in content,
                'content': 'content' in content or 'purge' in content,
            }
        except Exception:
            return None

    def _extract_tailwind_plugins(self, config_data: Dict[str, Any]) -> List[str]:
        """Extract Tailwind plugins from config"""
        # Simplified - would need JS parsing for real extraction
        return []

    def _analyze_utility_usage(self, project_path: Path) -> List[str]:
        """Analyze most common Tailwind utility patterns"""
        utility_pattern = r'class(?:Name)?=["\']([^"\']+)["\']'
        all_classes = []

        template_files = list(project_path.glob("**/*.html")) + \
                       list(project_path.glob("**/*.jsx"))[:20]

        for template_file in template_files:
            try:
                content = template_file.read_text()
                classes = re.findall(utility_pattern, content)
                all_classes.extend(classes)
            except Exception:
                continue

        # Return most common patterns
        common_patterns = [
            'flex', 'grid', 'bg-', 'text-', 'p-', 'm-', 'w-', 'h-',
            'rounded', 'shadow', 'border', 'hover:', 'focus:'
        ]

        found = [p for p in common_patterns if any(p in c for c in all_classes)]
        return found[:15]

    def _collect_tailwind_config(self, project_path: Path) -> str:
        """Collect Tailwind configuration"""
        config_files = list(project_path.glob("tailwind.config.*")) + \
                      list(project_path.glob("postcss.config.*"))

        config_content = []
        for config_file in config_files:
            try:
                content = config_file.read_text()
                config_content.append(f"# {config_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(config_content)

    def _collect_custom_css(self, project_path: Path) -> str:
        """Collect custom Tailwind CSS (@layer directives)"""
        css_content = []
        for css_file in list(project_path.glob("**/*.css")) + \
                       list(project_path.glob("**/styles/**/*.css")):
            try:
                content = css_file.read_text()
                # Only include if has Tailwind directives
                if "@tailwind" in content or "@layer" in content or "@apply" in content:
                    css_content.append(f"# {css_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(css_content[:10])

    def _collect_component_patterns(self, project_path: Path) -> str:
        """Collect common component patterns (class combinations)"""
        patterns_content = []

        template_files = list(project_path.glob("**/*.html")) + \
                       list(project_path.glob("**/*.jsx"))[:30]

        for template_file in template_files:
            try:
                content = template_file.read_text()
                # Look for component-like elements with Tailwind classes
                if re.search(r'class(?:Name)?=["\'][^"\']{30,}["\']', content):
                    patterns_content.append(f"# {template_file.relative_to(project_path)}\n{content}\n")
            except Exception:
                continue

        return "\n".join(patterns_content[:20])
