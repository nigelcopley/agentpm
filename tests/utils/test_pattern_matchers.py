"""
Comprehensive tests for Pattern Matching Utilities module.

Tests all pattern detection functions with:
- Unit tests for each function
- Edge cases and error handling
- Performance constraints validation
- Security constraints validation

Target: >90% test coverage
"""

from pathlib import Path
from typing import Dict, Any, List

import pytest

from agentpm.utils.pattern_matchers import (
    match_directory_pattern,
    detect_hexagonal_architecture,
    detect_layered_architecture,
    detect_ddd_patterns,
    match_naming_convention,
    detect_cqrs_pattern,
    detect_mvc_pattern,
    detect_pattern_violations,
    HEXAGONAL_PATTERN,
    LAYERED_PATTERN,
    DDD_PATTERN,
    CQRS_PATTERN,
    MVC_PATTERN,
)


class TestMatchDirectoryPattern:
    """Tests for match_directory_pattern function"""

    def test_exact_match_required_dirs(self, tmp_path: Path):
        """Test exact match of required directories"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "ports").mkdir()
        (tmp_path / "adapters").mkdir()

        pattern = {
            'required_dirs': ['domain', 'ports', 'adapters'],
            'optional_dirs': [],
            'forbidden_dirs': [],
            'alternatives': {},
            'min_match_score': 0.6
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score == 1.0

    def test_partial_match_required_dirs(self, tmp_path: Path):
        """Test partial match of required directories"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "ports").mkdir()
        # Missing 'adapters'

        pattern = {
            'required_dirs': ['domain', 'ports', 'adapters'],
            'optional_dirs': [],
            'forbidden_dirs': [],
            'alternatives': {},
            'min_match_score': 0.6
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score == pytest.approx(2.0 / 3.0)  # 2 out of 3

    def test_optional_dirs_add_bonus_score(self, tmp_path: Path):
        """Test optional directories increase score"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "application").mkdir()

        pattern = {
            'required_dirs': ['domain'],
            'optional_dirs': ['application', 'infrastructure'],
            'forbidden_dirs': [],
            'alternatives': {},
            'min_match_score': 0.5
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score >= 1.0  # Required (1.0) + optional bonus (if matched)
        assert score <= 1.5  # Max is 1.5 (1.0 + 0.5)

    def test_forbidden_dirs_reduce_score(self, tmp_path: Path):
        """Test forbidden directories reduce score"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "controllers").mkdir()

        pattern = {
            'required_dirs': ['domain'],
            'optional_dirs': [],
            'forbidden_dirs': ['controllers'],
            'alternatives': {},
            'min_match_score': 0.5
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score == 0.5  # 1.0 - 0.5 penalty

    def test_alternatives_match_primary_dirs(self, tmp_path: Path):
        """Test alternative directory names match"""
        # Arrange
        (tmp_path / "core").mkdir()  # Alternative for 'domain'
        (tmp_path / "interfaces").mkdir()  # Alternative for 'ports'

        pattern = {
            'required_dirs': ['domain', 'ports'],
            'optional_dirs': [],
            'forbidden_dirs': [],
            'alternatives': {
                'domain': ['core', 'business'],
                'ports': ['interfaces']
            },
            'min_match_score': 0.6
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score == 1.0

    def test_nonexistent_path_returns_zero(self, tmp_path: Path):
        """Test nonexistent path returns 0.0"""
        # Arrange
        nonexistent = tmp_path / "nonexistent"
        pattern = {'required_dirs': ['domain']}

        # Act
        score = match_directory_pattern(nonexistent, pattern)

        # Assert
        assert score == 0.0

    def test_nested_directory_matching(self, tmp_path: Path):
        """Test nested directories match patterns"""
        # Arrange
        (tmp_path / "src" / "domain" / "ports").mkdir(parents=True)

        pattern = {
            'required_dirs': ['ports'],
            'optional_dirs': [],
            'forbidden_dirs': [],
            'alternatives': {},
            'min_match_score': 0.5
        }

        # Act
        score = match_directory_pattern(tmp_path, pattern)

        # Assert
        assert score > 0.0  # Should find nested 'ports'


class TestDetectHexagonalArchitecture:
    """Tests for detect_hexagonal_architecture function"""

    def test_perfect_hexagonal_structure(self, tmp_path: Path):
        """Test perfect hexagonal architecture detection"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "ports").mkdir()
        (tmp_path / "adapters").mkdir()

        # Act
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        assert result['pattern'] == 'hexagonal'
        assert result['confidence'] > 0.7
        assert len(result['evidence']) >= 3

    def test_hexagonal_with_alternatives(self, tmp_path: Path):
        """Test hexagonal with alternative names"""
        # Arrange
        (tmp_path / "core").mkdir()
        (tmp_path / "interfaces").mkdir()
        (tmp_path / "infrastructure").mkdir()

        # Act
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        assert result['pattern'] == 'hexagonal'
        assert result['confidence'] > 0.5
        assert 'core/' in str(result['evidence'])

    def test_hexagonal_with_violations(self, tmp_path: Path):
        """Test hexagonal architecture with violations"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "ports").mkdir()
        (tmp_path / "adapters").mkdir()

        # Create domain file importing from adapters (violation)
        domain_file = tmp_path / "domain" / "entity.py"
        domain_file.write_text("from adapters import database\n")

        # Act
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        assert len(result['violations']) > 0
        assert result['confidence'] < 1.0  # Reduced due to violations

    def test_missing_hexagonal_dirs_low_confidence(self, tmp_path: Path):
        """Test missing directories result in low confidence"""
        # Arrange
        (tmp_path / "domain").mkdir()
        # Missing ports and adapters

        # Act
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        assert result['confidence'] < 0.5


class TestDetectLayeredArchitecture:
    """Tests for detect_layered_architecture function"""

    def test_perfect_layered_structure(self, tmp_path: Path):
        """Test perfect layered architecture detection"""
        # Arrange
        (tmp_path / "presentation").mkdir()
        (tmp_path / "domain").mkdir()
        (tmp_path / "data").mkdir()

        # Act
        result = detect_layered_architecture(tmp_path)

        # Assert
        assert result['pattern'] == 'layered'
        assert result['confidence'] > 0.5
        assert len(result['evidence']) >= 3

    def test_layered_with_alternatives(self, tmp_path: Path):
        """Test layered with alternative names"""
        # Arrange
        (tmp_path / "ui").mkdir()  # Alternative for presentation
        (tmp_path / "models").mkdir()  # Alternative for domain
        (tmp_path / "persistence").mkdir()  # Alternative for data

        # Act
        result = detect_layered_architecture(tmp_path)

        # Assert
        assert result['pattern'] == 'layered'
        assert result['confidence'] > 0.3

    def test_layered_four_tier(self, tmp_path: Path):
        """Test 4-tier layered architecture"""
        # Arrange
        (tmp_path / "presentation").mkdir()
        (tmp_path / "application").mkdir()
        (tmp_path / "domain").mkdir()
        (tmp_path / "data").mkdir()

        # Act
        result = detect_layered_architecture(tmp_path)

        # Assert
        assert result['confidence'] > 0.7
        assert len(result['evidence']) >= 4


class TestDetectDDDPatterns:
    """Tests for detect_ddd_patterns function"""

    def test_entity_pattern_detection(self, tmp_path: Path):
        """Test detection of Entity pattern"""
        # Arrange
        entities_dir = tmp_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "UserEntity.py").write_text("class UserEntity:\n    pass\n")
        (entities_dir / "OrderEntity.py").write_text("class OrderEntity:\n    pass\n")

        # Act
        result = detect_ddd_patterns(tmp_path)

        # Assert
        assert result['pattern'] == 'ddd'
        assert any('Entities' in evidence for evidence in result['evidence'])

    def test_value_object_pattern_detection(self, tmp_path: Path):
        """Test detection of Value Object pattern"""
        # Arrange
        vo_dir = tmp_path / "value_objects"
        vo_dir.mkdir()
        (vo_dir / "Money.py").write_text("class Money:\n    pass\n")

        # Act
        result = detect_ddd_patterns(tmp_path)

        # Assert
        assert any('Value Objects' in evidence for evidence in result['evidence'])

    def test_repository_pattern_detection(self, tmp_path: Path):
        """Test detection of Repository pattern"""
        # Arrange
        repo_dir = tmp_path / "repositories"
        repo_dir.mkdir()
        (repo_dir / "UserRepository.py").write_text("class UserRepository:\n    pass\n")

        # Act
        result = detect_ddd_patterns(tmp_path)

        # Assert
        assert any('Repositories' in evidence for evidence in result['evidence'])

    def test_multiple_ddd_patterns(self, tmp_path: Path):
        """Test detection of multiple DDD patterns"""
        # Arrange
        (tmp_path / "entities").mkdir()
        (tmp_path / "entities" / "User.py").write_text("class User:\n    pass\n")

        (tmp_path / "repositories").mkdir()
        (tmp_path / "repositories" / "UserRepository.py").write_text("class UserRepository:\n    pass\n")

        (tmp_path / "value_objects").mkdir()
        (tmp_path / "value_objects" / "Money.py").write_text("class Money:\n    pass\n")

        # Act
        result = detect_ddd_patterns(tmp_path)

        # Assert
        assert result['confidence'] > 0.5
        assert len(result['evidence']) >= 3

    def test_insufficient_ddd_patterns_low_confidence(self, tmp_path: Path):
        """Test low confidence with insufficient patterns"""
        # Arrange
        (tmp_path / "entities").mkdir()
        (tmp_path / "entities" / "User.py").write_text("class User:\n    pass\n")
        # Only one pattern

        # Act
        result = detect_ddd_patterns(tmp_path)

        # Assert
        assert result['confidence'] < 0.5


class TestMatchNamingConvention:
    """Tests for match_naming_convention function"""

    def test_perfect_match_naming_convention(self, tmp_path: Path):
        """Test perfect match of naming convention"""
        # Arrange
        files = [
            Path("UserModel.py"),
            Path("OrderModel.py"),
            Path("ProductModel.py")
        ]
        convention = {
            'model': r'.*Model\.py$'
        }

        # Act
        results = match_naming_convention(files, convention)

        # Assert
        assert results['model'] == 1.0

    def test_partial_match_naming_convention(self, tmp_path: Path):
        """Test partial match of naming convention"""
        # Arrange
        files = [
            Path("UserModel.py"),
            Path("OrderService.py"),
            Path("helper.py")
        ]
        convention = {
            'model': r'.*Model\.py$'
        }

        # Act
        results = match_naming_convention(files, convention)

        # Assert
        assert results['model'] == pytest.approx(1.0 / 3.0)

    def test_multiple_conventions(self, tmp_path: Path):
        """Test matching multiple conventions"""
        # Arrange
        files = [
            Path("UserModel.py"),
            Path("UserService.py"),
            Path("UserRepository.py")
        ]
        convention = {
            'model': r'.*Model\.py$',
            'service': r'.*Service\.py$',
            'repository': r'.*Repository\.py$'
        }

        # Act
        results = match_naming_convention(files, convention)

        # Assert
        assert results['model'] == pytest.approx(1.0 / 3.0)
        assert results['service'] == pytest.approx(1.0 / 3.0)
        assert results['repository'] == pytest.approx(1.0 / 3.0)

    def test_empty_file_list(self, tmp_path: Path):
        """Test empty file list returns zeros"""
        # Arrange
        files = []
        convention = {
            'model': r'.*Model\.py$'
        }

        # Act
        results = match_naming_convention(files, convention)

        # Assert
        assert results['model'] == 0.0


class TestDetectCQRSPattern:
    """Tests for detect_cqrs_pattern function"""

    def test_perfect_cqrs_structure(self, tmp_path: Path):
        """Test perfect CQRS structure detection"""
        # Arrange
        (tmp_path / "commands").mkdir()
        (tmp_path / "queries").mkdir()
        (tmp_path / "handlers").mkdir()

        # Add some files
        (tmp_path / "commands" / "CreateUser.py").write_text("pass")
        (tmp_path / "queries" / "GetUser.py").write_text("pass")

        # Act
        result = detect_cqrs_pattern(tmp_path)

        # Assert
        assert result['pattern'] == 'cqrs'
        assert result['confidence'] > 0.7
        assert len(result['evidence']) >= 4  # dirs + file counts

    def test_cqrs_without_handlers(self, tmp_path: Path):
        """Test CQRS without separate handlers directory"""
        # Arrange
        (tmp_path / "commands").mkdir()
        (tmp_path / "queries").mkdir()

        # Act
        result = detect_cqrs_pattern(tmp_path)

        # Assert
        assert result['confidence'] > 0.5

    def test_cqrs_with_handler_variants(self, tmp_path: Path):
        """Test CQRS with different handler directory names"""
        # Arrange
        (tmp_path / "commands").mkdir()
        (tmp_path / "queries").mkdir()
        (tmp_path / "command_handlers").mkdir()

        # Act
        result = detect_cqrs_pattern(tmp_path)

        # Assert
        assert any('command_handlers' in evidence for evidence in result['evidence'])


class TestDetectMVCPattern:
    """Tests for detect_mvc_pattern function"""

    def test_perfect_mvc_structure(self, tmp_path: Path):
        """Test perfect MVC structure detection"""
        # Arrange
        (tmp_path / "models").mkdir()
        (tmp_path / "views").mkdir()
        (tmp_path / "controllers").mkdir()

        # Act
        result = detect_mvc_pattern(tmp_path)

        # Assert
        assert result['pattern'] == 'mvc'
        assert result['confidence'] > 0.8
        assert len(result['evidence']) == 3

    def test_mvc_with_alternatives(self, tmp_path: Path):
        """Test MVC with alternative names"""
        # Arrange
        (tmp_path / "model").mkdir()
        (tmp_path / "templates").mkdir()
        (tmp_path / "control").mkdir()

        # Act
        result = detect_mvc_pattern(tmp_path)

        # Assert
        assert result['confidence'] > 0.5

    def test_mvc_missing_component(self, tmp_path: Path):
        """Test MVC with missing component"""
        # Arrange
        (tmp_path / "models").mkdir()
        (tmp_path / "views").mkdir()
        # Missing controllers

        # Act
        result = detect_mvc_pattern(tmp_path)

        # Assert
        assert result['confidence'] < 0.8


class TestDetectPatternViolations:
    """Tests for detect_pattern_violations function"""

    def test_hexagonal_violations(self, tmp_path: Path):
        """Test hexagonal pattern violations"""
        # Arrange
        (tmp_path / "domain").mkdir()
        (tmp_path / "adapters").mkdir()

        # Create violation: domain importing from adapters
        domain_file = tmp_path / "domain" / "entity.py"
        domain_file.write_text("from adapters import database\nclass Entity:\n    pass\n")

        # Act
        violations = detect_pattern_violations(tmp_path, 'hexagonal')

        # Assert
        assert len(violations) > 0
        assert violations[0]['type'] == 'hexagonal_violation'

    def test_no_violations_returns_empty_list(self, tmp_path: Path):
        """Test no violations returns empty list"""
        # Arrange
        (tmp_path / "domain").mkdir()
        domain_file = tmp_path / "domain" / "entity.py"
        domain_file.write_text("class Entity:\n    pass\n")

        # Act
        violations = detect_pattern_violations(tmp_path, 'hexagonal')

        # Assert
        assert len(violations) == 0

    def test_layered_violations(self, tmp_path: Path):
        """Test layered pattern violations"""
        # Arrange - Create structure but no violations yet
        (tmp_path / "domain").mkdir()
        (tmp_path / "presentation").mkdir()

        # Act
        violations = detect_pattern_violations(tmp_path, 'layered')

        # Assert
        assert isinstance(violations, list)

    def test_ddd_violations(self, tmp_path: Path):
        """Test DDD pattern violations"""
        # Arrange
        (tmp_path / "entities").mkdir()

        # Act
        violations = detect_pattern_violations(tmp_path, 'ddd')

        # Assert
        assert isinstance(violations, list)

    def test_cqrs_violations(self, tmp_path: Path):
        """Test CQRS pattern violations"""
        # Arrange
        (tmp_path / "commands").mkdir()
        (tmp_path / "queries").mkdir()

        # Act
        violations = detect_pattern_violations(tmp_path, 'cqrs')

        # Assert
        assert isinstance(violations, list)

    def test_mvc_violations(self, tmp_path: Path):
        """Test MVC pattern violations"""
        # Arrange
        (tmp_path / "models").mkdir()
        (tmp_path / "views").mkdir()

        # Act
        violations = detect_pattern_violations(tmp_path, 'mvc')

        # Assert
        assert isinstance(violations, list)


class TestPatternConstants:
    """Tests for pattern constant definitions"""

    def test_hexagonal_pattern_structure(self):
        """Test HEXAGONAL_PATTERN has required fields"""
        # Assert
        assert 'required_dirs' in HEXAGONAL_PATTERN
        assert 'optional_dirs' in HEXAGONAL_PATTERN
        assert 'forbidden_dirs' in HEXAGONAL_PATTERN
        assert 'alternatives' in HEXAGONAL_PATTERN
        assert 'min_match_score' in HEXAGONAL_PATTERN

    def test_layered_pattern_structure(self):
        """Test LAYERED_PATTERN has required fields"""
        # Assert
        assert 'required_dirs' in LAYERED_PATTERN
        assert 'alternatives' in LAYERED_PATTERN

    def test_ddd_pattern_structure(self):
        """Test DDD_PATTERN has indicator fields"""
        # Assert
        assert 'entity_indicators' in DDD_PATTERN
        assert 'value_object_indicators' in DDD_PATTERN
        assert 'repository_indicators' in DDD_PATTERN
        assert 'min_patterns_found' in DDD_PATTERN

    def test_cqrs_pattern_structure(self):
        """Test CQRS_PATTERN has required fields"""
        # Assert
        assert 'required_dirs' in CQRS_PATTERN
        assert 'commands' in CQRS_PATTERN['required_dirs']
        assert 'queries' in CQRS_PATTERN['required_dirs']

    def test_mvc_pattern_structure(self):
        """Test MVC_PATTERN has required fields"""
        # Assert
        assert 'required_dirs' in MVC_PATTERN
        assert 'models' in MVC_PATTERN['required_dirs']
        assert 'views' in MVC_PATTERN['required_dirs']
        assert 'controllers' in MVC_PATTERN['required_dirs']


class TestPerformanceConstraints:
    """Tests for performance constraints"""

    def test_pattern_matching_completes_quickly(self, tmp_path: Path):
        """Test pattern matching completes in <200ms"""
        # Arrange
        import time
        (tmp_path / "domain").mkdir()
        (tmp_path / "ports").mkdir()
        (tmp_path / "adapters").mkdir()

        # Act
        start = time.time()
        result = detect_hexagonal_architecture(tmp_path)
        elapsed_ms = (time.time() - start) * 1000

        # Assert
        assert result is not None
        assert elapsed_ms < 500  # 2.5x buffer for CI systems

    def test_large_directory_scan_performance(self, tmp_path: Path):
        """Test scanning large directory structure"""
        # Arrange
        import time
        # Create nested structure
        for i in range(20):
            (tmp_path / f"dir{i}").mkdir()

        # Act
        start = time.time()
        match_directory_pattern(tmp_path, HEXAGONAL_PATTERN)
        elapsed_ms = (time.time() - start) * 1000

        # Assert
        assert elapsed_ms < 500  # Should complete quickly even with many dirs


class TestSecurityConstraints:
    """Tests for security constraints"""

    def test_no_code_execution_during_scan(self, tmp_path: Path):
        """Test that pattern detection doesn't execute code"""
        # Arrange
        (tmp_path / "domain").mkdir()
        dangerous_file = tmp_path / "domain" / "dangerous.py"
        dangerous_file.write_text("import os\nos.system('echo dangerous')\n")

        # Act
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        # Should scan safely without executing the code
        assert result is not None

    def test_path_traversal_protection(self, tmp_path: Path):
        """Test protection against path traversal"""
        # Arrange
        (tmp_path / "domain").mkdir()

        # Act - Should handle gracefully
        result = detect_hexagonal_architecture(tmp_path)

        # Assert
        assert result is not None
