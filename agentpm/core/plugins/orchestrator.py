"""
Plugin Orchestrator - Selective Plugin Loading

Loads plugins ONLY for detected technologies.
Type-safe with Pydantic models throughout.

Pattern: Dynamic plugin loading based on detection results
"""

from pathlib import Path
from typing import List, Type, Optional
import time

from .base.plugin_interface import BasePlugin
from .base.types import EnrichmentResult, ContextDelta
from ..detection.models import DetectionResult


class PluginOrchestrator:
    """
    Loads plugins ONLY for detected technologies.

    If Python not detected, PythonPlugin never loaded.
    Type-safe with Pydantic models throughout.

    Example:
        orchestrator = PluginOrchestrator()
        result = orchestrator.enrich_context(project_path, detection_result)
        # Only loads plugins for detected technologies
    """

    # Technology → Plugin class mapping
    PLUGIN_MAPPING = {
        # Languages
        'python': 'domains.languages.python.PythonPlugin',
        'javascript': 'domains.languages.javascript.JavaScriptPlugin',
        'typescript': 'domains.languages.typescript.TypeScriptPlugin',

        # Backend Frameworks
        'django': 'domains.frameworks.django.DjangoPlugin',
        'click': 'domains.frameworks.click.ClickPlugin',

        # Frontend Frameworks
        'react': 'domains.frameworks.react.ReactPlugin',
        'htmx': 'domains.frameworks.htmx.HTMXPlugin',
        'alpine': 'domains.frameworks.alpine.AlpinePlugin',
        'tailwind': 'domains.frameworks.tailwind.TailwindPlugin',

        # Testing
        'pytest': 'domains.testing.pytest.PytestPlugin',

        # Data
        'sqlite': 'domains.data.sqlite.SQLitePlugin',
    }

    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize orchestrator with confidence threshold.

        Args:
            min_confidence: Minimum confidence to load plugin (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self._plugin_cache: dict[str, Type[BasePlugin]] = {}

    def load_plugins_for(self, detection: DetectionResult) -> List[BasePlugin]:
        """
        Load ONLY plugins for detected technologies.

        Type-safe with DetectionResult (Pydantic model).

        Args:
            detection: DetectionResult (Pydantic model) with detected technologies

        Returns:
            List of instantiated plugin objects

        Example:
            detection = DetectionResult(
                matches={
                    'python': TechnologyMatch(confidence=0.9, ...),
                    'django': TechnologyMatch(confidence=0.8, ...),
                },
                ...
            )
            → Returns: [PythonPlugin(), DjangoPlugin()]
            → NOT loaded: ReactPlugin, GoPlugin, etc. (not detected)
        """
        plugins: List[BasePlugin] = []

        # Get technologies above confidence threshold (type-safe)
        detected_techs = detection.get_detected_technologies(self.min_confidence)

        for tech_name in detected_techs:
            if tech_name in self.PLUGIN_MAPPING:
                plugin_class = self._import_plugin(tech_name)
                if plugin_class:
                    plugins.append(plugin_class())

        return plugins

    def enrich_context(self, project_path: Path, detection: DetectionResult) -> EnrichmentResult:
        """
        Each loaded plugin enriches context with type safety.

        Args:
            project_path: Path to project
            detection: DetectionResult (Pydantic model)

        Returns:
            EnrichmentResult (Pydantic model) with all plugin deltas:
            EnrichmentResult(
                project_path=str(project_path),
                deltas=[
                    ContextDelta(plugin_id='lang:python', additions={...}, recommendations=[...]),
                ],
                total_recommendations=5,
                enrichment_time_ms=45.2
            )
        """
        start_time = time.perf_counter()

        # Load plugins (type-safe)
        plugins = self.load_plugins_for(detection)

        # Create type-safe EnrichmentResult
        result = EnrichmentResult(
            project_path=str(project_path),
            deltas=[],
            enrichment_time_ms=0.0  # Will be set at end
        )

        # Ensure .aipm/contexts/ directory exists
        contexts_dir = project_path / ".aipm" / "contexts"
        contexts_dir.mkdir(parents=True, exist_ok=True)

        # Each plugin extracts facts AND generates code amalgamations
        for plugin in plugins:
            try:
                # Extract project facts
                facts = plugin.extract_project_facts(project_path)

                # Generate code amalgamations and write to files
                amalgamations = plugin.generate_code_amalgamations(project_path)
                amalgamation_files = {}

                for amalgamation_type, content in amalgamations.items():
                    # Skip if content is empty or just headers
                    # Headers are typically "# Title\n# Generated: date\n\n"
                    if not content:
                        continue

                    # Count actual content lines (not headers/comments/blank)
                    lines = content.split('\n')
                    content_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

                    if len(content_lines) == 0:  # No actual content, just headers
                        continue

                    # File naming: plugin_id_type.txt (e.g., lang:python_classes.txt)
                    safe_plugin_id = plugin.plugin_id.replace(':', '_')
                    filename = f"{safe_plugin_id}_{amalgamation_type}"
                    if not filename.endswith('.txt'):
                        filename += '.txt'

                    file_path = contexts_dir / filename
                    file_path.write_text(content, encoding='utf-8')
                    amalgamation_files[amalgamation_type] = str(file_path.relative_to(project_path))

                # Add amalgamation file paths to facts
                if amalgamation_files:
                    facts['amalgamation_files'] = amalgamation_files

                # Convert to ContextDelta
                delta = ContextDelta(
                    plugin_id=plugin.plugin_id,
                    additions=facts,
                    recommendations=[]  # Can be enhanced later
                )
                result.add_delta(delta)  # Type-safe addition
            except Exception as e:
                # Log error but continue with other plugins
                print(f"Plugin {plugin.plugin_id} failed: {e}")

        # Set enrichment time
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        result.enrichment_time_ms = elapsed_ms

        return result

    def _import_plugin(self, tech_name: str) -> Optional[Type[BasePlugin]]:
        """
        Import plugin class dynamically with caching.

        Args:
            tech_name: Technology name (e.g., 'python')

        Returns:
            Plugin class or None if import fails
        """
        # Check cache
        if tech_name in self._plugin_cache:
            return self._plugin_cache[tech_name]

        # Import plugin
        try:
            plugin_path = self.PLUGIN_MAPPING[tech_name]
            module_path, class_name = plugin_path.rsplit('.', 1)
            module = __import__(f'agentpm.core.plugins.{module_path}', fromlist=[class_name])
            plugin_class = getattr(module, class_name)

            # Cache for future use
            self._plugin_cache[tech_name] = plugin_class
            return plugin_class

        except (ImportError, AttributeError) as e:
            print(f"Failed to import plugin for {tech_name}: {e}")
            return None