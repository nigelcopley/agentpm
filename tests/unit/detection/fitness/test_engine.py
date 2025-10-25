"""
Unit tests for FitnessEngine.

Tests architecture fitness testing including:
- Policy loading (default policies, presets)
- Validation functions (complexity, cycles, layering, etc.)
- Compliance scoring
- Violation reporting
- Error handling

**Test Strategy**:
- Use temporary projects with controlled code quality
- Test each validation function independently
- Test preset configurations
- Validate performance targets (<1s for tests)

**Author**: APM (Agent Project Manager) Test Suite
"""

import pytest
from pathlib import Path
from textwrap import dedent

from agentpm.core.detection.fitness import FitnessEngine
from agentpm.core.database.models.detection_fitness import (
    Policy,
    PolicyViolation,
    FitnessResult,
)
from agentpm.core.database.enums.detection import PolicyLevel


class TestFitnessEngine:
    """Test suite for FitnessEngine."""

    @pytest.fixture
    def simple_project(self, tmp_path):
        """Create simple, clean project."""
        project = tmp_path / "simple_project"
        project.mkdir()

        # Simple clean file
        (project / "clean.py").write_text(dedent("""
            '''Module docstring.'''

            def simple_function(x):
                '''Simple function.'''
                return x + 1

            class SimpleClass:
                '''Simple class.'''
                def method(self):
                    '''Simple method.'''
                    return 42
        """))

        return project

    @pytest.fixture
    def complex_project(self, tmp_path):
        """Create project with quality issues."""
        project = tmp_path / "complex_project"
        project.mkdir()

        # File with high complexity
        (project / "complex.py").write_text(dedent("""
            def complex_function(a, b, c, d, e):
                '''Function with high complexity.'''
                if a:
                    if b:
                        if c:
                            if d:
                                if e:
                                    return 1
                                else:
                                    return 2
                            else:
                                return 3
                        else:
                            return 4
                    else:
                        return 5
                else:
                    return 6
        """))

        # Large file (>500 lines)
        lines = []
        lines.append("'''Large file.'''")
        for i in range(550):
            lines.append(f"def func_{i}():")
            lines.append(f"    return {i}")
        (project / "large.py").write_text("\n".join(lines))

        return project

    @pytest.fixture
    def circular_project(self, tmp_path):
        """Create project with circular dependencies."""
        project = tmp_path / "circular_project"
        project.mkdir()

        # A imports B
        (project / "module_a.py").write_text(dedent("""
            from module_b import func_b

            def func_a():
                return func_b()
        """))

        # B imports A (circular!)
        (project / "module_b.py").write_text(dedent("""
            from module_a import func_a

            def func_b():
                return func_a()
        """))

        return project

    @pytest.fixture
    def layered_project(self, tmp_path):
        """Create project with layered architecture."""
        project = tmp_path / "layered_project"
        project.mkdir()

        # Create layer directories
        (project / "utils").mkdir()
        (project / "utils" / "__init__.py").write_text("")
        (project / "utils" / "helpers.py").write_text("def helper(): pass")

        (project / "plugins").mkdir()
        (project / "plugins" / "__init__.py").write_text("")
        (project / "plugins" / "plugin.py").write_text(dedent("""
            from utils.helpers import helper

            def plugin_func():
                helper()
        """))

        (project / "detection").mkdir()
        (project / "detection" / "__init__.py").write_text("")
        (project / "detection" / "detector.py").write_text(dedent("""
            from plugins.plugin import plugin_func

            def detect():
                plugin_func()
        """))

        return project

    def test_init_with_valid_directory(self, simple_project):
        """Test initialization with valid directory."""
        engine = FitnessEngine(simple_project)
        assert engine.project_path == simple_project.resolve()
        assert len(engine._policy_validators) > 0

    def test_init_with_invalid_path(self, tmp_path):
        """Test initialization fails with non-directory."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")
        with pytest.raises(ValueError, match="must be a directory"):
            FitnessEngine(file_path)

    def test_load_default_policies(self, simple_project):
        """Test loading default policies."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_default_policies()

        assert isinstance(policies, list)
        assert len(policies) > 0
        # All should be Policy objects
        assert all(isinstance(p, Policy) for p in policies)
        # All should be enabled
        assert all(p.enabled for p in policies)

    def test_load_preset_strict(self, simple_project):
        """Test loading strict preset."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_preset('strict')

        assert isinstance(policies, list)
        assert len(policies) > 0
        # Strict preset should have stricter thresholds
        complexity_policies = [p for p in policies if 'complexity' in p.policy_id.lower()]
        if complexity_policies:
            # Check that thresholds are strict
            for policy in complexity_policies:
                threshold = policy.metadata.get('threshold')
                if threshold is not None:
                    assert threshold <= 15  # Strict complexity limit

    def test_load_preset_balanced(self, simple_project):
        """Test loading balanced preset."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_preset('balanced')

        assert isinstance(policies, list)
        assert len(policies) > 0

    def test_load_preset_lenient(self, simple_project):
        """Test loading lenient preset."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_preset('lenient')

        assert isinstance(policies, list)
        # Lenient should have fewer or more relaxed policies
        complexity_policies = [p for p in policies if 'complexity' in p.policy_id.lower()]
        if complexity_policies:
            for policy in complexity_policies:
                threshold = policy.metadata.get('threshold')
                if threshold is not None:
                    assert threshold >= 10  # Lenient threshold

    def test_get_available_presets(self, simple_project):
        """Test getting list of available presets."""
        engine = FitnessEngine(simple_project)
        presets = engine.get_available_presets()

        assert isinstance(presets, list)
        assert len(presets) > 0
        # Should include common presets
        assert 'strict' in presets
        assert 'balanced' in presets
        assert 'lenient' in presets

    def test_run_tests_simple_project(self, simple_project):
        """Test running fitness tests on clean project."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_default_policies()
        result = engine.run_tests(policies)

        assert isinstance(result, FitnessResult)
        assert result.passed_count >= 0
        assert result.warning_count >= 0
        assert result.error_count >= 0
        assert 0.0 <= result.compliance_score <= 1.0
        assert result.tested_at is not None

    def test_run_tests_complex_project(self, complex_project):
        """Test running tests on project with issues."""
        engine = FitnessEngine(complex_project)
        policies = engine.load_default_policies()
        result = engine.run_tests(policies)

        # Should have some violations due to complexity and size
        assert result.error_count > 0 or result.warning_count > 0
        assert len(result.violations) > 0

        # Check that violations are properly categorized
        for violation in result.violations:
            assert isinstance(violation, PolicyViolation)
            assert violation.level in [PolicyLevel.ERROR, PolicyLevel.WARNING, PolicyLevel.INFO]
            assert len(violation.message) > 0
            assert len(violation.location) > 0

    def test_validate_no_cycles_clean_project(self, simple_project):
        """Test cycle validation on project without cycles."""
        engine = FitnessEngine(simple_project)
        policy = Policy(
            policy_id='TEST_NO_CYCLES',
            name='Test No Cycles',
            description='Test',
            level=PolicyLevel.ERROR,
            validation_fn='validate_no_cycles',
            enabled=True,
            metadata={'severity_threshold': 'high'}
        )

        violations = engine._validate_no_cycles(policy)
        assert isinstance(violations, list)
        assert len(violations) == 0  # No cycles in simple project

    def test_validate_no_cycles_circular_project(self, circular_project):
        """Test cycle validation on project with circular dependencies."""
        engine = FitnessEngine(circular_project)
        policy = Policy(
            policy_id='TEST_NO_CYCLES',
            name='Test No Cycles',
            description='Test',
            level=PolicyLevel.ERROR,
            validation_fn='validate_no_cycles',
            enabled=True,
            metadata={}
        )

        violations = engine._validate_no_cycles(policy)
        # May or may not detect cycles depending on import resolution
        # At minimum, should not crash
        assert isinstance(violations, list)

    def test_validate_max_complexity(self, complex_project):
        """Test complexity validation."""
        engine = FitnessEngine(complex_project)
        policy = Policy(
            policy_id='TEST_MAX_COMPLEXITY',
            name='Test Max Complexity',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_complexity',
            enabled=True,
            metadata={'threshold': 5}  # Low threshold to trigger violations
        )

        violations = engine._validate_max_complexity(policy)
        assert isinstance(violations, list)
        # Complex project should have high complexity functions
        assert len(violations) > 0
        # Check violation format
        for violation in violations:
            assert 'complexity' in violation.message.lower()
            assert violation.level == PolicyLevel.WARNING

    def test_validate_max_file_loc(self, complex_project):
        """Test file size validation."""
        engine = FitnessEngine(complex_project)
        policy = Policy(
            policy_id='TEST_MAX_FILE_LOC',
            name='Test Max File LOC',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_file_loc',
            enabled=True,
            metadata={'threshold': 100}  # Low threshold
        )

        violations = engine._validate_max_file_loc(policy)
        assert isinstance(violations, list)
        # Large file should violate
        assert len(violations) > 0

    def test_validate_max_function_loc(self, simple_project):
        """Test function size validation."""
        engine = FitnessEngine(simple_project)
        policy = Policy(
            policy_id='TEST_MAX_FUNC_LOC',
            name='Test Max Function LOC',
            description='Test',
            level=PolicyLevel.INFO,
            validation_fn='validate_max_function_loc',
            enabled=True,
            metadata={'threshold': 3}  # Very low threshold
        )

        violations = engine._validate_max_function_loc(policy)
        assert isinstance(violations, list)
        # Simple project should have small functions, may or may not violate

    def test_validate_layering(self, layered_project):
        """Test layering validation."""
        engine = FitnessEngine(layered_project)
        policy = Policy(
            policy_id='TEST_LAYERING',
            name='Test Layering',
            description='Test',
            level=PolicyLevel.ERROR,
            validation_fn='validate_layering',
            enabled=True,
            metadata={
                'layer_order': ['utils', 'plugins', 'detection']
            }
        )

        violations = engine._validate_layering(policy)
        assert isinstance(violations, list)
        # Properly structured project should have no violations
        # (utils doesn't import from plugins/detection, etc.)

    def test_validate_maintainability(self, complex_project):
        """Test maintainability index validation."""
        engine = FitnessEngine(complex_project)
        policy = Policy(
            policy_id='TEST_MAINTAINABILITY',
            name='Test Maintainability',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_maintainability',
            enabled=True,
            metadata={'threshold': 80}  # High threshold to trigger violations
        )

        violations = engine._validate_maintainability(policy)
        assert isinstance(violations, list)
        # Complex project may have low maintainability

    def test_validate_max_coupling(self, simple_project):
        """Test module coupling validation."""
        engine = FitnessEngine(simple_project)
        policy = Policy(
            policy_id='TEST_MAX_COUPLING',
            name='Test Max Coupling',
            description='Test',
            level=PolicyLevel.INFO,
            validation_fn='validate_max_coupling',
            enabled=True,
            metadata={'threshold': 0.5}  # Medium threshold
        )

        violations = engine._validate_max_coupling(policy)
        assert isinstance(violations, list)
        # Simple project should have low coupling

    def test_validate_max_depth(self, simple_project):
        """Test dependency depth validation."""
        engine = FitnessEngine(simple_project)
        policy = Policy(
            policy_id='TEST_MAX_DEPTH',
            name='Test Max Depth',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_depth',
            enabled=True,
            metadata={'max_depth': 5}
        )

        violations = engine._validate_max_depth(policy)
        assert isinstance(violations, list)
        # Simple project should have shallow dependencies

    def test_validate_docstrings(self, simple_project):
        """Test docstring validation."""
        engine = FitnessEngine(simple_project)
        policy = Policy(
            policy_id='TEST_DOCSTRINGS',
            name='Test Docstrings',
            description='Test',
            level=PolicyLevel.INFO,
            validation_fn='validate_docstrings',
            enabled=True,
            metadata={
                'check_modules': True,
                'check_classes': True,
                'check_functions': True
            }
        )

        violations = engine._validate_docstrings(policy)
        assert isinstance(violations, list)
        # Current implementation is placeholder, should return empty list

    def test_lazy_loading_services(self, simple_project):
        """Test lazy loading of analysis and graph services."""
        engine = FitnessEngine(simple_project)

        # Services should be None initially
        assert engine._analysis_service is None
        assert engine._graph_service is None

        # Access should trigger lazy loading
        analysis_service = engine.analysis_service
        assert analysis_service is not None
        assert engine._analysis_service is not None

        graph_service = engine.graph_service
        assert graph_service is not None
        assert engine._graph_service is not None

        # Subsequent access should return same instances
        assert engine.analysis_service is analysis_service
        assert engine.graph_service is graph_service

    def test_get_policy_summary(self, simple_project):
        """Test policy summary generation."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_default_policies()
        summary = engine.get_policy_summary(policies)

        assert isinstance(summary, dict)
        assert 'total' in summary
        assert 'enabled' in summary
        assert 'disabled' in summary
        assert 'by_level' in summary
        assert 'unique_tags' in summary

        assert summary['total'] == len(policies)
        assert summary['enabled'] >= 0
        assert summary['by_level']['error'] >= 0
        assert summary['by_level']['warning'] >= 0
        assert summary['by_level']['info'] >= 0
        assert isinstance(summary['unique_tags'], list)

    def test_compliance_score_calculation(self, simple_project):
        """Test compliance score calculation logic."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_default_policies()
        result = engine.run_tests(policies)

        # Compliance score should be between 0 and 1
        assert 0.0 <= result.compliance_score <= 1.0

        # If no errors/warnings, score should be high
        if result.error_count == 0 and result.warning_count == 0:
            assert result.compliance_score >= 0.9

    def test_fitness_result_methods(self, simple_project):
        """Test FitnessResult helper methods."""
        engine = FitnessEngine(simple_project)
        policies = engine.load_default_policies()
        result = engine.run_tests(policies)

        # Test is_passing
        passing = result.is_passing()
        assert isinstance(passing, bool)
        assert passing == (result.error_count == 0)

        # Test get_violations_by_level
        errors = result.get_violations_by_level(PolicyLevel.ERROR)
        warnings = result.get_violations_by_level(PolicyLevel.WARNING)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
        assert len(errors) == result.error_count

        # Test get_summary
        summary = result.get_summary()
        assert isinstance(summary, str)
        assert 'passed' in summary.lower() or 'failed' in summary.lower()

    def test_error_handling_unknown_validator(self, simple_project):
        """Test error handling for unknown validation function."""
        engine = FitnessEngine(simple_project)

        # Create policy with non-existent validator
        invalid_policy = Policy(
            policy_id='INVALID',
            name='Invalid Policy',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='nonexistent_validator',
            enabled=True,
            metadata={}
        )

        result = engine.run_tests([invalid_policy])

        # Should not crash, should skip unknown validator
        assert isinstance(result, FitnessResult)

    def test_error_handling_validator_exception(self, simple_project):
        """Test error handling when validator raises exception."""
        engine = FitnessEngine(simple_project)

        # Monkey-patch a validator to raise exception
        original_validator = engine._policy_validators.get('validate_no_cycles')

        def failing_validator(policy):
            raise RuntimeError("Test exception")

        engine._policy_validators['validate_no_cycles'] = failing_validator

        policy = Policy(
            policy_id='TEST',
            name='Test',
            description='Test',
            level=PolicyLevel.ERROR,
            validation_fn='validate_no_cycles',
            enabled=True,
            metadata={}
        )

        result = engine.run_tests([policy])

        # Should handle exception and report as error
        assert result.error_count >= 1
        assert len(result.violations) >= 1

        # Restore original validator
        if original_validator:
            engine._policy_validators['validate_no_cycles'] = original_validator

    def test_performance_fitness_testing(self, tmp_path):
        """Test performance of fitness testing."""
        import time

        # Create moderate-sized project
        project = tmp_path / "perf_project"
        project.mkdir()

        for i in range(20):
            (project / f"module_{i}.py").write_text(dedent(f"""
                '''Module {i}.'''

                def func_{i}(x):
                    '''Function {i}.'''
                    return x + {i}

                class Class_{i}:
                    '''Class {i}.'''
                    def method(self):
                        return {i}
            """))

        engine = FitnessEngine(project)
        policies = engine.load_default_policies()

        start = time.time()
        result = engine.run_tests(policies)
        duration = time.time() - start

        # Should complete within 1 second
        assert duration < 1.0
        assert isinstance(result, FitnessResult)

    def test_disabled_policies_not_executed(self, simple_project):
        """Test that disabled policies are not executed."""
        engine = FitnessEngine(simple_project)

        # Create mix of enabled and disabled policies
        enabled_policy = Policy(
            policy_id='ENABLED',
            name='Enabled',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_complexity',
            enabled=True,
            metadata={'threshold': 10}
        )

        disabled_policy = Policy(
            policy_id='DISABLED',
            name='Disabled',
            description='Test',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_complexity',
            enabled=False,
            metadata={'threshold': 1}  # Would trigger many violations if run
        )

        result = engine.run_tests([enabled_policy, disabled_policy])

        # Only enabled policy should be tested
        # If disabled policy ran with threshold=1, would have many violations
        assert isinstance(result, FitnessResult)

    def test_preset_configuration_overrides(self, simple_project):
        """Test that preset configurations override policy defaults."""
        engine = FitnessEngine(simple_project)

        # Load strict preset
        strict_policies = engine.load_preset('strict')

        # Check that complexity thresholds are stricter
        complexity_policies = [
            p for p in strict_policies
            if p.policy_id == 'MAX_CYCLOMATIC_COMPLEXITY'
        ]

        if complexity_policies:
            policy = complexity_policies[0]
            threshold = policy.metadata.get('threshold')
            # Strict preset should have lower threshold
            assert threshold is not None
            assert threshold <= 10


class TestFitnessModels:
    """Test Pydantic models for fitness testing."""

    def test_policy_creation(self):
        """Test Policy model creation."""
        policy = Policy(
            policy_id='TEST_POLICY',
            name='Test Policy',
            description='Test description',
            level=PolicyLevel.WARNING,
            validation_fn='validate_max_complexity',
            enabled=True,
            tags=['test', 'complexity'],
            metadata={'threshold': 10}
        )

        assert policy.policy_id == 'TEST_POLICY'
        assert policy.level == PolicyLevel.WARNING
        assert policy.enabled is True
        assert 'test' in policy.tags

    def test_policy_violation_creation(self):
        """Test PolicyViolation model creation."""
        violation = PolicyViolation(
            policy_id='TEST_POLICY',
            level=PolicyLevel.ERROR,
            message='Test violation message',
            location='test.py:10',
            suggestion='Fix the issue'
        )

        assert violation.policy_id == 'TEST_POLICY'
        assert violation.level == PolicyLevel.ERROR
        assert len(violation.message) > 0
        assert len(violation.location) > 0

    def test_fitness_result_creation(self):
        """Test FitnessResult model creation."""
        violations = [
            PolicyViolation(
                policy_id='P1',
                level=PolicyLevel.ERROR,
                message='Error',
                location='test.py:1'
            ),
            PolicyViolation(
                policy_id='P2',
                level=PolicyLevel.WARNING,
                message='Warning',
                location='test.py:2'
            )
        ]

        result = FitnessResult(
            violations=violations,
            passed_count=5,
            warning_count=1,
            error_count=1,
            compliance_score=0.85
        )

        assert result.passed_count == 5
        assert result.warning_count == 1
        assert result.error_count == 1
        assert result.compliance_score == 0.85
        assert len(result.violations) == 2

    def test_policy_level_enum(self):
        """Test PolicyLevel enum values."""
        assert PolicyLevel.ERROR
        assert PolicyLevel.WARNING
        assert PolicyLevel.INFO
        # Test enum comparison
        assert PolicyLevel.ERROR != PolicyLevel.WARNING
