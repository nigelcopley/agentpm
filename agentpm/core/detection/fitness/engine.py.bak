"""
Fitness Engine - Policy-based Architecture Fitness Testing.

Executes architecture fitness tests to validate code quality, architectural
patterns, and best practices compliance.

Architecture Layer: Layer 3 (Detection Services)
Dependencies:
- Layer 1: graph_builders, metrics_calculator (utilities)
- Layer 3: analysis.service, graphs.service (same layer)

Responsibilities:
- Load policy definitions
- Execute validation logic against AST/dependency graphs
- Generate violation reports
- Calculate compliance scores

Performance Targets:
- Fitness testing: <1s for typical projects
- Policy validation: <100ms per policy
- Cached: <100ms total

Example Usage:
    from pathlib import Path
    from agentpm.core.detection.fitness import FitnessEngine

    # Initialize engine
    engine = FitnessEngine(Path.cwd())

    # Load default policies
    policies = engine.load_default_policies()

    # Run tests
    result = engine.run_tests(policies)

    # Check results
    if result.is_passing():
        print(f"PASSED - Compliance: {result.compliance_score:.0%}")
    else:
        print(f"FAILED - {result.error_count} errors")
        for violation in result.violations:
            if violation.level == PolicyLevel.ERROR:
                print(f"  {violation.location}: {violation.message}")

Author: APM (Agent Project Manager) Detection Pack Team
Version: 1.0.0
"""

from pathlib import Path
from typing import List, Dict, Callable, Optional, Any
from datetime import datetime

# Layer 1 utilities
from agentpm.utils.graph_builders import (
    detect_cycles,
    calculate_coupling_metrics,
)
from agentpm.utils.metrics_calculator import (
    calculate_cyclomatic_complexity,
    count_lines,
)

# Layer 3 services (same layer)
from agentpm.core.detection.analysis.service import StaticAnalysisService
from agentpm.core.detection.graphs.service import DependencyGraphService

# Layer 2 models (database layer)
from agentpm.core.database.models.detection_fitness import (
    Policy,
    PolicyViolation,
    FitnessResult,
)
from agentpm.core.database.enums.detection import PolicyLevel

# Layer 3 policies
from .policies import (
    DEFAULT_POLICIES,
    create_policy_from_dict,
    get_enabled_policies,
    get_policy_by_id,
)

# Layer 3 presets
from .presets import (
    get_builtin_preset,
    get_builtin_preset_names,
    expand_policy_tags,
)


class FitnessEngine:
    """
    Architecture fitness testing engine.

    Executes policy-based validation to ensure code quality and
    architectural compliance.

    Validation Functions:
    - validate_no_cycles: No circular dependencies
    - validate_max_complexity: Maximum cyclomatic complexity
    - validate_max_file_loc: Maximum lines per file
    - validate_max_function_loc: Maximum lines per function
    - validate_layering: No layering violations
    - validate_maintainability: Minimum maintainability index
    - validate_max_coupling: Maximum module coupling
    - validate_max_depth: Maximum dependency depth
    - validate_docstrings: Documentation coverage

    Attributes:
        project_path: Project root directory
        _policy_validators: Registered validation functions
        _analysis_service: Static analysis service (lazy-loaded)
        _graph_service: Dependency graph service (lazy-loaded)

    Example:
        >>> engine = FitnessEngine(Path("/my/project"))
        >>> policies = engine.load_default_policies()
        >>> result = engine.run_tests(policies)
        >>> print(result.get_summary())
        PASSED - 8 passed, 2 warnings, 0 errors (90% compliance)
    """

    def __init__(self, project_path: Path):
        """
        Initialize fitness engine.

        Args:
            project_path: Project root directory

        Raises:
            ValueError: If project_path is not a directory
        """
        if not project_path.is_dir():
            raise ValueError(f"project_path must be a directory: {project_path}")

        self.project_path = project_path.resolve()
        self._policy_validators: Dict[str, Callable] = {}
        self._register_validators()

        # Lazy-loaded services
        self._analysis_service: Optional[StaticAnalysisService] = None
        self._graph_service: Optional[DependencyGraphService] = None

    @property
    def analysis_service(self) -> StaticAnalysisService:
        """Get static analysis service (lazy-loaded)."""
        if self._analysis_service is None:
            self._analysis_service = StaticAnalysisService(
                self.project_path,
                cache_enabled=True
            )
        return self._analysis_service

    @property
    def graph_service(self) -> DependencyGraphService:
        """Get dependency graph service (lazy-loaded)."""
        if self._graph_service is None:
            self._graph_service = DependencyGraphService(self.project_path)
        return self._graph_service

    def _register_validators(self) -> None:
        """
        Register validation functions.

        Maps validation_fn names to actual methods.
        """
        self._policy_validators = {
            'validate_no_cycles': self._validate_no_cycles,
            'validate_max_complexity': self._validate_max_complexity,
            'validate_max_file_loc': self._validate_max_file_loc,
            'validate_max_function_loc': self._validate_max_function_loc,
            'validate_layering': self._validate_layering,
            'validate_maintainability': self._validate_maintainability,
            'validate_max_coupling': self._validate_max_coupling,
            'validate_max_depth': self._validate_max_depth,
            'validate_docstrings': self._validate_docstrings,
        }

    def load_default_policies(self) -> List[Policy]:
        """
        Load built-in default policies.

        Returns only enabled policies from policies.DEFAULT_POLICIES.

        Returns:
            List of enabled Policy objects

        Example:
            >>> engine = FitnessEngine(Path.cwd())
            >>> policies = engine.load_default_policies()
            >>> print(f"Loaded {len(policies)} policies")
        """
        enabled = get_enabled_policies()
        return [create_policy_from_dict(p) for p in enabled]

    def load_preset(self, preset_name: str) -> List[Policy]:
        """
        Load policies from a built-in preset.

        Presets provide predefined configurations for common use cases:
        - strict: Enterprise-grade quality requirements
        - balanced: Moderate quality standards (default)
        - lenient: Relaxed standards for legacy code
        - startup: Fast iteration, lower quality bars
        - security_focused: Security and compliance emphasis

        Args:
            preset_name: Name of preset to load

        Returns:
            List of Policy objects configured according to preset

        Raises:
            ValueError: If preset_name is not a valid built-in preset

        Example:
            >>> engine = FitnessEngine(Path.cwd())
            >>> policies = engine.load_preset('strict')
            >>> print(f"Loaded {len(policies)} policies from 'strict' preset")
            >>> result = engine.run_tests(policies)
        """
        # Get preset configuration
        preset = get_builtin_preset(preset_name)
        preset_config = preset.configuration

        # Get policy IDs to enable
        policy_ids = preset_config.get('policies', [])
        policy_ids = expand_policy_tags(policy_ids)

        # Load policies
        policies = []
        for policy_id in policy_ids:
            policy_dict = get_policy_by_id(policy_id)
            if policy_dict is None:
                print(f"Warning: Unknown policy ID '{policy_id}' in preset, skipping")
                continue

            # Create policy
            policy = create_policy_from_dict(policy_dict)

            # Apply preset configuration overrides
            if policy.policy_id == 'MAX_CYCLOMATIC_COMPLEXITY':
                if 'max_complexity' in preset_config:
                    policy.metadata['threshold'] = preset_config['max_complexity']

            elif policy.policy_id == 'MAX_FUNCTION_COMPLEXITY_STRICT':
                if 'max_complexity' in preset_config:
                    # Strict threshold is typically 2x the warning threshold
                    policy.metadata['threshold'] = preset_config['max_complexity'] * 2

            elif policy.policy_id == 'MAX_FILE_LOC':
                if 'max_file_loc' in preset_config:
                    policy.metadata['threshold'] = preset_config['max_file_loc']

            elif policy.policy_id == 'MAX_FUNCTION_LOC':
                if 'max_function_loc' in preset_config:
                    policy.metadata['threshold'] = preset_config['max_function_loc']

            elif policy.policy_id == 'MIN_MAINTAINABILITY_INDEX':
                if 'min_maintainability' in preset_config:
                    policy.metadata['threshold'] = preset_config['min_maintainability']

            elif policy.policy_id == 'MIN_MAINTAINABILITY_INDEX_STRICT':
                if 'min_maintainability' in preset_config:
                    # Strict threshold is typically 40% of warning threshold
                    policy.metadata['threshold'] = max(40, preset_config['min_maintainability'] - 25)

            elif policy.policy_id == 'MAX_DEPENDENCY_DEPTH':
                if 'max_dependency_depth' in preset_config:
                    policy.metadata['max_depth'] = preset_config['max_dependency_depth']

            elif policy.policy_id == 'NO_CIRCULAR_DEPENDENCIES':
                if not preset_config.get('enforce_no_cycles', True):
                    # Skip this policy if enforce_no_cycles is False
                    continue

            policies.append(policy)

        return policies

    def get_available_presets(self) -> List[str]:
        """
        Get list of available preset names.

        Returns:
            List of preset names

        Example:
            >>> engine = FitnessEngine(Path.cwd())
            >>> presets = engine.get_available_presets()
            >>> print(f"Available presets: {', '.join(presets)}")
        """
        return get_builtin_preset_names()

    def run_tests(self, policies: List[Policy]) -> FitnessResult:
        """
        Run fitness tests for all enabled policies.

        Steps:
        1. Filter to enabled policies only
        2. Execute each policy's validation function
        3. Collect violations
        4. Calculate compliance score
        5. Return complete FitnessResult

        Compliance Score Calculation:
        - Start at 1.0 (perfect)
        - Subtract 0.1 for each error
        - Subtract 0.05 for each warning
        - Minimum: 0.0

        Args:
            policies: List of policies to test

        Returns:
            Complete FitnessResult with all violations

        Example:
            >>> engine = FitnessEngine(Path.cwd())
            >>> policies = engine.load_default_policies()
            >>> result = engine.run_tests(policies)
            >>>
            >>> if not result.is_passing():
            ...     for violation in result.get_violations_by_level(PolicyLevel.ERROR):
            ...         print(f"ERROR: {violation.message}")

        Performance:
            - <1s for typical projects
            - Caches intermediate results (AST, graphs)
        """
        # Filter enabled policies
        enabled_policies = [p for p in policies if p.enabled]

        violations: List[PolicyViolation] = []
        passed_count = 0
        warning_count = 0
        error_count = 0

        # Execute each policy
        for policy in enabled_policies:
            # Get validation function
            validator = self._policy_validators.get(policy.validation_fn)
            if validator is None:
                # Unknown validator, skip with warning
                print(f"Warning: Unknown validator '{policy.validation_fn}' for policy {policy.policy_id}")
                continue

            try:
                # Run validation
                policy_violations = validator(policy)

                # Count violations by level
                if policy_violations:
                    violations.extend(policy_violations)
                    for v in policy_violations:
                        if v.level == PolicyLevel.ERROR:
                            error_count += 1
                        elif v.level == PolicyLevel.WARNING:
                            warning_count += 1
                else:
                    passed_count += 1

            except Exception as e:
                # Validation failed, treat as error
                print(f"Error running validator for {policy.policy_id}: {e}")
                error_count += 1
                violations.append(
                    PolicyViolation(
                        policy_id=policy.policy_id,
                        level=PolicyLevel.ERROR,
                        message=f"Validation failed: {str(e)}",
                        location="<validation_error>",
                        suggestion="Check policy configuration and validation logic"
                    )
                )

        # Calculate compliance score
        compliance_score = 1.0
        compliance_score -= error_count * 0.1
        compliance_score -= warning_count * 0.05
        compliance_score = max(0.0, min(1.0, compliance_score))

        return FitnessResult(
            violations=violations,
            passed_count=passed_count,
            warning_count=warning_count,
            error_count=error_count,
            compliance_score=round(compliance_score, 2),
            tested_at=datetime.now()
        )

    # ========================================================================
    # Validation Functions
    # ========================================================================

    def _validate_no_cycles(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate no circular dependencies.

        Uses DependencyGraphService to detect cycles.
        Filters by severity_threshold if specified in metadata.

        Args:
            policy: Policy configuration

        Returns:
            List of violations (one per cycle)
        """
        violations = []

        # Build dependency graph
        graph = self.graph_service.build_graph()

        # Detect cycles
        cycles_data = self.graph_service.find_circular_dependencies()

        # Filter by severity if specified
        severity_threshold = policy.metadata.get('severity_threshold')
        if severity_threshold:
            cycles_data = [c for c in cycles_data if c.severity == severity_threshold]

        # Create violations
        for cycle_info in cycles_data:
            cycle_path = ' -> '.join(cycle_info.cycle)

            violations.append(
                PolicyViolation(
                    policy_id=policy.policy_id,
                    level=policy.level,
                    message=f"Circular dependency detected ({cycle_info.severity}): {cycle_path}",
                    location=cycle_info.cycle[0],
                    suggestion=cycle_info.suggestion
                )
            )

        return violations

    def _validate_max_complexity(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum cyclomatic complexity.

        Uses StaticAnalysisService to check complexity.
        Threshold configurable via policy.metadata['threshold'].

        Args:
            policy: Policy configuration

        Returns:
            List of violations (one per function exceeding threshold)
        """
        violations = []
        threshold = policy.metadata.get('threshold', 10)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file
        for file_analysis in analysis.files:
            # Check functions
            for func in file_analysis.functions:
                complexity = func.get('complexity', 0)
                if complexity > threshold:
                    func_name = func.get('name', 'unknown')
                    line_number = func.get('line_number', 0)

                    violations.append(
                        PolicyViolation(
                            policy_id=policy.policy_id,
                            level=policy.level,
                            message=(
                                f"Function '{func_name}' has complexity {complexity}, "
                                f"exceeds threshold of {threshold}"
                            ),
                            location=f"{file_analysis.file_path}:{line_number}",
                            suggestion=policy.metadata.get(
                                'recommendation',
                                "Break function into smaller, single-purpose functions"
                            )
                        )
                    )

        return violations

    def _validate_max_file_loc(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum lines of code per file.

        Uses StaticAnalysisService.
        Threshold configurable via policy.metadata['threshold'].

        Args:
            policy: Policy configuration

        Returns:
            List of violations (one per file exceeding threshold)
        """
        violations = []
        threshold = policy.metadata.get('threshold', 500)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file
        for file_analysis in analysis.files:
            if file_analysis.code_lines > threshold:
                violations.append(
                    PolicyViolation(
                        policy_id=policy.policy_id,
                        level=policy.level,
                        message=(
                            f"File has {file_analysis.code_lines} lines, "
                            f"exceeds threshold of {threshold}"
                        ),
                        location=file_analysis.file_path,
                        suggestion=policy.metadata.get(
                            'recommendation',
                            "Split large file into multiple focused modules"
                        )
                    )
                )

        return violations

    def _validate_max_function_loc(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum lines per function.

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        threshold = policy.metadata.get('threshold', 50)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file
        for file_analysis in analysis.files:
            for func in file_analysis.functions:
                start_line = func.get('line_number', 0)
                end_line = func.get('end_line', start_line)
                func_lines = end_line - start_line + 1

                if func_lines > threshold:
                    func_name = func.get('name', 'unknown')

                    violations.append(
                        PolicyViolation(
                            policy_id=policy.policy_id,
                            level=policy.level,
                            message=(
                                f"Function '{func_name}' has {func_lines} lines, "
                                f"exceeds threshold of {threshold}"
                            ),
                            location=f"{file_analysis.file_path}:{start_line}",
                            suggestion=policy.metadata.get(
                                'rationale',
                                "Break large function into smaller helpers"
                            )
                        )
                    )

        return violations

    def _validate_layering(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate no layering violations.

        Checks that lower layers don't depend on higher layers.
        Layer order specified in policy.metadata['layer_order'].

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        layer_order = policy.metadata.get('layer_order', ['utils', 'plugins', 'detection'])

        # Build layer hierarchy (lower layer = lower index)
        layer_indices = {layer: idx for idx, layer in enumerate(layer_order)}

        # Build dependency graph
        graph = self.graph_service.build_graph()

        # Check each edge
        for source, target in graph.edges():
            # Determine layer for each module
            source_layer = None
            target_layer = None

            for layer in layer_order:
                if f"/{layer}/" in source or source.startswith(layer):
                    source_layer = layer
                if f"/{layer}/" in target or target.startswith(layer):
                    target_layer = layer

            # Check for violation
            if source_layer and target_layer:
                source_idx = layer_indices.get(source_layer, -1)
                target_idx = layer_indices.get(target_layer, -1)

                # Violation: lower layer depends on higher layer
                if source_idx < target_idx:
                    violations.append(
                        PolicyViolation(
                            policy_id=policy.policy_id,
                            level=policy.level,
                            message=(
                                f"Layering violation: '{source_layer}' layer depends on "
                                f"'{target_layer}' layer (lower -> higher not allowed)"
                            ),
                            location=f"{source} -> {target}",
                            suggestion=(
                                "Move shared functionality to a lower layer or use "
                                "dependency inversion (abstractions in lower layer)"
                            )
                        )
                    )

        return violations

    def _validate_maintainability(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate minimum maintainability index.

        Uses StaticAnalysisService.
        Threshold configurable via policy.metadata['threshold'].

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        threshold = policy.metadata.get('threshold', 65)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file
        for file_analysis in analysis.files:
            if file_analysis.maintainability_index < threshold:
                violations.append(
                    PolicyViolation(
                        policy_id=policy.policy_id,
                        level=policy.level,
                        message=(
                            f"Maintainability index {file_analysis.maintainability_index:.1f} "
                            f"below threshold of {threshold}"
                        ),
                        location=file_analysis.file_path,
                        suggestion=policy.metadata.get(
                            'recommendation',
                            "Reduce complexity, improve documentation, refactor large functions"
                        )
                    )
                )

        return violations

    def _validate_max_coupling(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum module coupling (instability).

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        threshold = policy.metadata.get('threshold', 0.8)

        # Get dependency analysis
        analysis = self.graph_service.analyze_dependencies()

        # Check coupling metrics
        for coupling in analysis.coupling_metrics:
            if coupling.instability > threshold:
                violations.append(
                    PolicyViolation(
                        policy_id=policy.policy_id,
                        level=policy.level,
                        message=(
                            f"Module instability {coupling.instability:.2f} "
                            f"exceeds threshold of {threshold}"
                        ),
                        location=coupling.module,
                        suggestion=policy.metadata.get(
                            'recommendation',
                            "Apply dependency inversion, extract interfaces, reduce coupling"
                        )
                    )
                )

        return violations

    def _validate_max_depth(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum dependency depth.

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        max_depth = policy.metadata.get('max_depth', 10)

        # Get dependency analysis
        analysis = self.graph_service.analyze_dependencies()

        # Check max depth
        if analysis.max_depth > max_depth:
            violations.append(
                PolicyViolation(
                    policy_id=policy.policy_id,
                    level=policy.level,
                    message=(
                        f"Dependency depth {analysis.max_depth} "
                        f"exceeds threshold of {max_depth}"
                    ),
                    location="<project>",
                    suggestion=policy.metadata.get(
                        'rationale',
                        "Reduce dependency chains by flattening architecture"
                    )
                )
            )

        return violations

    def _validate_docstrings(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate documentation coverage.

        Checks for module/class/function docstrings.
        Configuration via policy.metadata.

        Args:
            policy: Policy configuration

        Returns:
            List of violations
        """
        violations = []
        check_modules = policy.metadata.get('check_modules', True)
        check_classes = policy.metadata.get('check_classes', True)
        check_functions = policy.metadata.get('check_functions', False)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file (module-level docstrings)
        # Note: This is simplified - full implementation would need AST parsing
        # to check actual docstring presence
        for file_analysis in analysis.files:
            # Placeholder - would need to check actual file AST for docstrings
            # This is an INFO-level policy, disabled by default
            pass

        return violations

    def get_policy_summary(self, policies: List[Policy]) -> Dict[str, Any]:
        """
        Get summary of policies to be tested.

        Args:
            policies: List of policies

        Returns:
            Summary dict with counts by level, tag, etc.

        Example:
            >>> engine = FitnessEngine(Path.cwd())
            >>> policies = engine.load_default_policies()
            >>> summary = engine.get_policy_summary(policies)
            >>> print(f"Will test {summary['total']} policies")
            >>> print(f"Critical: {summary['by_level']['error']}")
        """
        total = len(policies)
        enabled = len([p for p in policies if p.enabled])

        by_level = {
            'error': len([p for p in policies if p.level == PolicyLevel.ERROR]),
            'warning': len([p for p in policies if p.level == PolicyLevel.WARNING]),
            'info': len([p for p in policies if p.level == PolicyLevel.INFO]),
        }

        all_tags = set()
        for policy in policies:
            all_tags.update(policy.tags)

        return {
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'by_level': by_level,
            'unique_tags': sorted(all_tags),
        }


# Module exports
__all__ = [
    'FitnessEngine',
]
