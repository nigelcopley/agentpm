"""
Intelligent Plugin Detection System
Smart, sequential plugin execution for optimal performance and accuracy
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .indicators import ProjectIndicators
# Note: plugin_registry will be replaced with PluginOrchestrator in integration
# from agentpm.core.plugins.orchestrator import PluginOrchestrator


class DetectionPhase(Enum):
    """Phases of intelligent detection"""
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    ECOSYSTEM = "ecosystem"
    ARCHITECTURE = "architecture"


@dataclass
class DetectionContext:
    """Context accumulated during detection phases"""
    project_path: Path
    primary_languages: List[str]
    secondary_languages: List[str]
    confidence_scores: Dict[str, float]
    detected_frameworks: List[str]
    project_indicators: Dict[str, Any]
    phase_timings: Dict[DetectionPhase, float]

    def __post_init__(self):
        if not hasattr(self, 'phase_timings'):
            self.phase_timings = {}


class IntelligentDetectionSystem:
    """
    Smart plugin detection system that:
    1. Quickly identifies languages first
    2. Only runs relevant framework plugins
    3. Detects ecosystem tools based on context
    4. Provides early termination for obvious cases
    """

    def __init__(self):
        self.performance_budget = 0.05  # 50ms total budget
        self._language_cache = {}

    def detect_project_context(self, project_path: Path) -> Tuple[List[PluginDetectionResult], DetectionContext]:
        """
        Intelligently detect project context with optimal performance

        Returns: (detection_results, context_used)
        """
        start_time = time.time()
        context = DetectionContext(
            project_path=project_path,
            primary_languages=[],
            secondary_languages=[],
            confidence_scores={},
            detected_frameworks=[],
            project_indicators={},
            phase_timings={}
        )

        results = []

        # Phase 1: Fast Language Detection (target: 5-10ms)
        phase_start = time.time()
        self._detect_languages_fast(context)
        context.phase_timings[DetectionPhase.LANGUAGE] = time.time() - phase_start

        # Early termination if no languages detected
        if not context.primary_languages and not context.secondary_languages:
            return results, context

        # Phase 2: Smart Framework Detection (target: 10-15ms per relevant framework)
        phase_start = time.time()
        framework_results = self._detect_frameworks_smart(context)
        results.extend(framework_results)
        context.phase_timings[DetectionPhase.FRAMEWORK] = time.time() - phase_start

        # Phase 3: Ecosystem Detection (target: 5-10ms)
        phase_start = time.time()
        ecosystem_results = self._detect_ecosystem_tools(context)
        results.extend(ecosystem_results)
        context.phase_timings[DetectionPhase.ECOSYSTEM] = time.time() - phase_start

        # Phase 4: Architecture Patterns (optional, if time allows)
        remaining_budget = self.performance_budget - (time.time() - start_time)
        if remaining_budget > 0.01:  # 10ms minimum for architecture detection
            phase_start = time.time()
            arch_results = self._detect_architecture_patterns(context)
            results.extend(arch_results)
            context.phase_timings[DetectionPhase.ARCHITECTURE] = time.time() - phase_start

        return results, context

    def _detect_languages_fast(self, context: DetectionContext) -> None:
        """
        Ultra-fast language detection using file extensions and key indicators
        Target: 5-10ms for typical projects
        """
        project_path = context.project_path

        # Language indicators by priority (most definitive first)
        language_indicators = ProjectIndicators.get_language_indicator_map()

        language_scores = {}

        # Quick scan - limit files checked for performance
        files_checked = 0
        max_files = 50  # Performance limit

        for file_path in project_path.rglob("*"):
            if files_checked >= max_files:
                break

            if file_path.is_file():
                # Check extensions
                ext = file_path.suffix.lower()
                name = file_path.name.lower()

                for lang, indicators in language_indicators.items():
                    # Extension matching
                    if ext in indicators['extensions']:
                        score = indicators['extensions'][ext]
                        language_scores[lang] = language_scores.get(lang, 0) + score

                    # Key file matching
                    if name in indicators['files']:
                        score = indicators['files'][name]
                        language_scores[lang] = language_scores.get(lang, 0) + score

                files_checked += 1

            elif file_path.is_dir():
                # Directory matching
                dir_name = file_path.name.lower()
                relative_path = str(file_path.relative_to(project_path)).lower()

                for lang, indicators in language_indicators.items():
                    for dir_pattern, score in indicators['directories'].items():
                        if dir_pattern in [dir_name, relative_path]:
                            language_scores[lang] = language_scores.get(lang, 0) + score

        # Classify languages by confidence
        sorted_languages = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)

        for lang, score in sorted_languages:
            confidence = min(score / 2.0, 1.0)  # Normalize to 0-1 range
            context.confidence_scores[lang] = confidence

            if confidence > 0.7:
                context.primary_languages.append(lang)
            elif confidence > 0.3:
                context.secondary_languages.append(lang)

        # Store indicators for framework detection
        context.project_indicators['language_scores'] = language_scores

    def _detect_frameworks_smart(self, context: DetectionContext) -> List[PluginDetectionResult]:
        """
        Smart framework detection - only run relevant plugins based on detected languages
        """
        results = []

        # Language → Framework mapping
        framework_mapping = {
            'python': ['django', 'python_language'],  # Python language plugin handles base Python
            'javascript': ['react', 'vue', 'angular', 'node'],
            'java': ['spring', 'maven', 'gradle'],
            'go': ['gin', 'echo', 'fiber'],
            'rust': ['actix', 'rocket', 'axum']
        }

        relevant_plugins = set()

        # Only load plugins for detected languages
        for lang in context.primary_languages + context.secondary_languages:
            if lang in framework_mapping:
                relevant_plugins.update(framework_mapping[lang])

        # Run only relevant plugins
        for plugin_name in relevant_plugins:
            plugin = plugin_registry.get_plugin(plugin_name)
            if plugin:
                try:
                    plugin_start = time.time()
                    result = plugin.detect_technology(context.project_path)
                    plugin_time = time.time() - plugin_start

                    if result:
                        results.append(result)
                        context.detected_frameworks.append(result.technology_name)

                    # Performance monitoring
                    if plugin_time > 0.02:  # 20ms warning threshold
                        print(f"⚠️ Plugin {plugin_name} took {plugin_time*1000:.1f}ms (consider optimization)")

                except Exception as e:
                    print(f"⚠️ Plugin {plugin_name} failed: {e}")

        return results

    def _detect_ecosystem_tools(self, context: DetectionContext) -> List[PluginDetectionResult]:
        """
        Detect ecosystem tools based on detected languages and frameworks
        """
        results = []

        # Ecosystem tool mapping based on context
        ecosystem_mapping = {
            'python': ['pytest'],  # Only check pytest if Python detected
            'javascript': ['jest', 'webpack', 'vite'],
            'any': ['docker']  # Docker can be used with any language
        }

        relevant_plugins = set()

        # Add language-specific ecosystem tools
        for lang in context.primary_languages:
            if lang in ecosystem_mapping:
                relevant_plugins.update(ecosystem_mapping[lang])

        # Always check universal tools
        relevant_plugins.update(ecosystem_mapping.get('any', []))

        # Run ecosystem plugins
        for plugin_name in relevant_plugins:
            plugin = plugin_registry.get_plugin(plugin_name)
            if plugin:
                try:
                    result = plugin.detect_technology(context.project_path)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️ Ecosystem plugin {plugin_name} failed: {e}")

        return results

    def _detect_architecture_patterns(self, context: DetectionContext) -> List[PluginDetectionResult]:
        """
        Detect architecture patterns - only for complex projects
        """
        results = []

        # Only run architecture detection for complex projects
        project_complexity = self._assess_project_complexity(context)

        if project_complexity < 0.5:
            return results  # Skip for simple projects

        # Architecture pattern plugins (if time allows)
        arch_plugins = ['hexagonal']

        for plugin_name in arch_plugins:
            plugin = plugin_registry.get_plugin(plugin_name)
            if plugin:
                try:
                    result = plugin.detect_technology(context.project_path)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️ Architecture plugin {plugin_name} failed: {e}")

        return results

    def _assess_project_complexity(self, context: DetectionContext) -> float:
        """
        Quick assessment of project complexity to decide on architecture pattern detection
        """
        complexity_score = 0.0

        # Multiple languages increase complexity
        total_languages = len(context.primary_languages) + len(context.secondary_languages)
        if total_languages > 1:
            complexity_score += 0.3

        # Multiple frameworks increase complexity
        if len(context.detected_frameworks) > 2:
            complexity_score += 0.3

        # High confidence scores indicate well-structured projects
        avg_confidence = sum(context.confidence_scores.values()) / len(context.confidence_scores) if context.confidence_scores else 0
        if avg_confidence > 0.8:
            complexity_score += 0.4

        return min(complexity_score, 1.0)

    def get_performance_report(self, context: DetectionContext) -> Dict[str, Any]:
        """
        Generate performance report for monitoring and optimization
        """
        total_time = sum(context.phase_timings.values())

        return {
            'total_time_ms': total_time * 1000,
            'phase_breakdown': {
                phase.value: timing * 1000 for phase, timing in context.phase_timings.items()
            },
            'languages_detected': len(context.primary_languages) + len(context.secondary_languages),
            'frameworks_detected': len(context.detected_frameworks),
            'performance_budget_used': (total_time / self.performance_budget) * 100,
            'recommendations': self._generate_performance_recommendations(context)
        }

    def _generate_performance_recommendations(self, context: DetectionContext) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        total_time = sum(context.phase_timings.values())

        if total_time > self.performance_budget:
            recommendations.append(f"Detection exceeded budget by {(total_time - self.performance_budget) * 1000:.1f}ms")

        # Identify slow phases
        for phase, timing in context.phase_timings.items():
            if timing > 0.015:  # 15ms threshold
                recommendations.append(f"{phase.value} phase slow: {timing*1000:.1f}ms")

        if not recommendations:
            recommendations.append("Performance within optimal range")

        return recommendations


# Global instance for use throughout the system
intelligent_detector = IntelligentDetectionSystem()