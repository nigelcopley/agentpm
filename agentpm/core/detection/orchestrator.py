"""
Detection Orchestrator - Two-Phase Detection Coordinator

Coordinates Phase 1 (IndicatorService) and Phase 2 (Plugin.detect) detection.

Implements ADR-001 two-phase detection architecture for scalable performance
with 200+ plugins.

Pattern: Service coordinator using IndicatorService + PluginOrchestrator
"""

from pathlib import Path
from typing import Set, List, Dict, Type, Optional
import time

from .indicator_service import IndicatorService
from .models import DetectionResult, TechnologyMatch, EvidenceType
from ..plugins.base.plugin_interface import BasePlugin
from ...utils import DependencyGraph


class DetectionOrchestrator:
    """
    Coordinate two-phase detection for scalable plugin system.

    Phase 1: Fast indicator scan (IndicatorService, <100ms)
    Phase 2: Selective plugin detection (only candidates, <500ms)

    Performance: ~300ms total for typical project vs 10s naive approach

    Example:
        orchestrator = DetectionOrchestrator(min_confidence=0.5)
        result = orchestrator.detect_all(project_path)
        # Returns: DetectionResult with 3-5 high-confidence matches
        # Performance: <600ms (Phase 1: 100ms + Phase 2: 200ms)
    """

    # Plugin registry - maps technology name to plugin class path
    # (Strings only for memory efficiency, lazy loading)
    PLUGIN_REGISTRY: Dict[str, str] = {
        # Languages
        'python': 'agentpm.core.plugins.domains.languages.python.PythonPlugin',
        'javascript': 'agentpm.core.plugins.domains.languages.javascript.JavaScriptPlugin',
        'typescript': 'agentpm.core.plugins.domains.languages.typescript.TypeScriptPlugin',

        # Backend Frameworks
        'django': 'agentpm.core.plugins.domains.frameworks.django.DjangoPlugin',
        'click': 'agentpm.core.plugins.domains.frameworks.click.ClickPlugin',

        # Frontend Frameworks
        'react': 'agentpm.core.plugins.domains.frameworks.react.ReactPlugin',
        'htmx': 'agentpm.core.plugins.domains.frameworks.htmx.HTMXPlugin',
        'alpine': 'agentpm.core.plugins.domains.frameworks.alpine.AlpinePlugin',
        'tailwind': 'agentpm.core.plugins.domains.frameworks.tailwind.TailwindPlugin',

        # Testing
        'pytest': 'agentpm.core.plugins.domains.testing.pytest.PytestPlugin',

        # Databases
        'sqlite': 'agentpm.core.plugins.domains.data.sqlite.SQLitePlugin',
    }

    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize detection orchestrator.

        Args:
            min_confidence: Minimum confidence threshold for matches (0.0-1.0)
                           Default 0.5 filters out weak signals
        """
        self.min_confidence = min_confidence
        self._plugin_cache: Dict[str, Type[BasePlugin]] = {}
        self._indicator_service = IndicatorService()
        self._dependency_graph = self._build_technology_dependency_graph()

    def detect_all(self, project_path: Path) -> DetectionResult:
        """
        Run two-phase detection on project.

        Phase 1: Fast indicator scan (IndicatorService)
        Phase 2: Selective plugin detection (only candidates)

        Args:
            project_path: Path to project directory

        Returns:
            DetectionResult with high-confidence technology matches

        Performance:
            Phase 1: <100ms (indicator scan)
            Phase 2: <500ms (3-10 plugins × 50ms each)
            Total: <600ms typical

        Example:
            >>> orchestrator = DetectionOrchestrator()
            >>> result = orchestrator.detect_all(Path('/my/django/project'))
            >>> print(result.matches.keys())
            dict_keys(['python', 'django', 'pytest'])
            >>> print(result.scan_time_ms)
            287.5
        """
        start_time = time.time()

        # Phase 1: Fast indicator scan (<100ms)
        phase1_start = time.time()
        candidates = self._indicator_service.scan_for_candidates(project_path)
        phase1_time = (time.time() - phase1_start) * 1000

        # Phase 2: Selective plugin detection (<500ms)
        phase2_start = time.time()
        matches = self._detect_with_plugins(project_path, candidates)
        phase2_time = (time.time() - phase2_start) * 1000

        # Add candidates without plugins (detected but no enrichment)
        # Only add if confidence would be >= threshold
        for candidate in candidates:
            if candidate not in matches:
                # Skip low-confidence indicator-only detections (reduces false positives)
                # Config file extensions (.json, .yaml, .xml) are too generic
                if candidate.lower() in ['json', 'yaml', 'xml', 'toml', 'markdown', 'html', 'css', 'shell']:
                    continue  # Suppress config format noise

                # Technology detected by indicator but no plugin available for enrichment
                matches[candidate] = TechnologyMatch(
                    technology=candidate,
                    confidence=0.6,  # Raised from 0.5 to reduce noise
                    evidence=[f"Detected by IndicatorService (no enrichment plugin available)"],
                    evidence_types=[EvidenceType.CONFIG_FILE]
                )

        # Apply dependency-based confidence boosting
        matches = self._apply_dependency_boosting(matches)

        total_time = (time.time() - start_time) * 1000

        # Create detection result
        result = DetectionResult(
            matches=matches,
            scan_time_ms=total_time,
            project_path=str(project_path.absolute())
        )

        # TODO: Add structured logging when available
        # Log performance for monitoring
        # if total_time > 600:
        #     logger.warning(f"Detection slow: {total_time:.1f}ms (Phase 1: {phase1_time:.1f}ms, Phase 2: {phase2_time:.1f}ms)")

        return result

    def _detect_with_plugins(
        self,
        project_path: Path,
        candidates: Set[str]
    ) -> Dict[str, TechnologyMatch]:
        """
        Run plugin detection on filtered candidates only.

        Loads only plugins matching candidates (selective loading from ADR-002).

        Args:
            project_path: Path to project
            candidates: Plugin IDs from Phase 1 indicator scan

        Returns:
            Dictionary of technology -> TechnologyMatch for high-confidence matches
        """
        matches: Dict[str, TechnologyMatch] = {}

        # Load only candidate plugins (not all 200+)
        plugins = self._load_plugins(candidates)

        # Run detect() on each candidate plugin
        for plugin in plugins:
            try:
                # Phase 2 detection: 3-phase within plugin
                confidence = plugin.detect(project_path)

                # Filter by confidence threshold
                if confidence >= self.min_confidence:
                    matches[plugin.enriches] = TechnologyMatch(
                        technology=plugin.enriches,
                        confidence=confidence,
                        evidence=[],  # TODO: Add evidence collection from plugin
                        evidence_types=[]
                    )

            except Exception as e:
                # Plugin detection failure doesn't crash system (fail-safe design)
                # TODO: Add logging when available
                # logger.warning(f"Plugin {plugin.plugin_id} detection failed: {e}")
                pass

        return matches

    def _load_plugins(self, candidates: Set[str]) -> List[BasePlugin]:
        """
        Load plugin instances for candidate technologies only.

        Implements selective plugin loading (ADR-002) - loads 3-10 plugins
        instead of all 200+.

        Args:
            candidates: Set of technology names from Phase 1

        Returns:
            List of instantiated plugin objects
        """
        plugins: List[BasePlugin] = []

        for tech_name in candidates:
            # Check if we have a plugin for this technology
            if tech_name not in self.PLUGIN_REGISTRY:
                continue

            # Lazy load plugin class
            plugin_class = self._import_plugin(tech_name)
            if plugin_class:
                # Instantiate plugin
                plugins.append(plugin_class())

        return plugins

    def _import_plugin(self, tech_name: str) -> Optional[Type[BasePlugin]]:
        """
        Lazy import plugin class with caching.

        Caches plugin classes to avoid repeated imports.

        Args:
            tech_name: Technology name (e.g., 'python', 'django')

        Returns:
            Plugin class or None if import fails
        """
        # Check cache first
        if tech_name in self._plugin_cache:
            return self._plugin_cache[tech_name]

        try:
            # Get plugin class path from registry
            class_path = self.PLUGIN_REGISTRY[tech_name]

            # Import module and get class
            module_path, class_name = class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            plugin_class = getattr(module, class_name)

            # Cache for future use
            self._plugin_cache[tech_name] = plugin_class

            return plugin_class

        except Exception as e:
            # Import failure: Plugin might not exist yet or has errors
            # Graceful degradation - return None
            # TODO: Add logging when available
            # logger.error(f"Failed to import plugin {tech_name}: {e}")
            return None

    def _build_technology_dependency_graph(self) -> DependencyGraph:
        """
        Build technology dependency graph from TECHNOLOGY_DEPENDENCIES mapping.

        Returns:
            DependencyGraph with all technology relationships

        Example graph:
            python
            ├── django [HARD: match]
            ├── flask [HARD: match]
            ├── click [HARD: match]
            └── pytest [SOFT: +10%]
        """
        from .indicators import ProjectIndicators

        graph = DependencyGraph()

        for child_tech, dependencies in ProjectIndicators.TECHNOLOGY_DEPENDENCIES.items():
            for parent_tech, boost_strategy in dependencies:
                # Determine relationship type and metadata
                if boost_strategy == 'match':
                    rel_type = 'HARD'
                    metadata = {'boost': 'match'}
                else:
                    rel_type = 'SOFT'
                    metadata = {'boost': float(boost_strategy)}

                graph.add_dependency(
                    child=child_tech,
                    parent=parent_tech,
                    relationship_type=rel_type,
                    metadata=metadata
                )

        return graph

    def _apply_dependency_boosting(self, matches: Dict[str, TechnologyMatch]) -> Dict[str, TechnologyMatch]:
        """
        Apply dependency-based confidence boosting using dependency graph.

        If Django detected at 100%, Python should also be 100% (Django requires Python).
        Uses DependencyGraph for relationship modeling and traversal.

        Strategy:
        - HARD dependencies: Parent confidence = max(parent, child)
        - SOFT dependencies: Parent confidence += child × multiplier

        Args:
            matches: Current detection matches

        Returns:
            Updated matches with boosted confidences

        Example:
            Before: {python: 70%, django: 100%}
            After: {python: 100%, django: 100%}  # Python boosted by Django
        """
        # Create a mutable copy
        boosted = dict(matches)

        # Apply dependency boosts using graph
        for child_tech, match in matches.items():
            # Get dependencies from graph
            dependencies = self._dependency_graph.get_dependencies(child_tech)

            for edge in dependencies:
                parent_tech = edge.parent
                boost_strategy = edge.metadata.get('boost')

                # Calculate boost
                if boost_strategy == 'match':
                    # HARD dependency: Parent should match child confidence
                    new_confidence = match.confidence
                    reason = f"HARD dependency on {child_tech} ({match.confidence:.0%})"
                else:
                    # SOFT dependency: Boost by percentage
                    boost_amount = match.confidence * boost_strategy
                    reason = f"{child_tech} ({match.confidence:.0%}) × {boost_strategy:.0%} = +{boost_amount:.0%}"
                    new_confidence = (boosted.get(parent_tech).confidence if parent_tech in boosted else 0.0) + boost_amount

                # Update parent confidence if boost is higher
                if parent_tech in boosted:
                    old_confidence = boosted[parent_tech].confidence
                    if new_confidence > old_confidence:
                        # Create new TechnologyMatch with boosted confidence
                        boosted[parent_tech] = TechnologyMatch(
                            technology=parent_tech,
                            confidence=min(new_confidence, 1.0),  # Cap at 100%
                            evidence=boosted[parent_tech].evidence + [reason],
                            evidence_types=boosted[parent_tech].evidence_types + [EvidenceType.DEPENDENCY]
                        )
                else:
                    # Parent not detected independently, add it with boosted confidence
                    # Only if boost is significant (>= threshold)
                    if new_confidence >= self.min_confidence:
                        boosted[parent_tech] = TechnologyMatch(
                            technology=parent_tech,
                            confidence=min(new_confidence, 1.0),
                            evidence=[f"Inferred from {child_tech} dependency ({reason})"],
                            evidence_types=[EvidenceType.DEPENDENCY]
                        )

        return boosted

    def get_loaded_plugins_info(self) -> List[Dict[str, str]]:
        """
        Get information about currently loaded plugins.

        Useful for debugging and monitoring.

        Returns:
            List of dicts with plugin metadata
        """
        return [
            {
                'technology': tech,
                'class_path': class_path,
                'loaded': tech in self._plugin_cache
            }
            for tech, class_path in self.PLUGIN_REGISTRY.items()
        ]
