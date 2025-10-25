"""
Tests for Pattern Recognition Service (Layer 3)

Tests the PatternRecognitionService and related models.

Run tests:
    pytest tests/test_pattern_recognition_service.py -v
    pytest tests/test_pattern_recognition_service.py -v --cov=agentpm/core/detection/patterns
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentpm.core.detection.patterns import (
    ArchitecturePattern,
    PatternAnalysis,
    PatternMatch,
    PatternRecognitionService,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory structure."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create hexagonal structure
    (project / "domain").mkdir()
    (project / "ports").mkdir()
    (project / "adapters").mkdir()

    # Create some Python files
    (project / "domain" / "entity.py").write_text("class UserEntity: pass")
    (project / "ports" / "repository.py").write_text("class UserRepository: pass")
    (project / "adapters" / "db_adapter.py").write_text("class DbAdapter: pass")

    return project


@pytest.fixture
def layered_project(tmp_path):
    """Create a temporary layered project structure."""
    project = tmp_path / "layered_project"
    project.mkdir()

    # Create layered structure
    (project / "presentation").mkdir()
    (project / "application").mkdir()
    (project / "domain").mkdir()
    (project / "data").mkdir()

    return project


@pytest.fixture
def ddd_project(tmp_path):
    """Create a temporary DDD project structure."""
    project = tmp_path / "ddd_project"
    project.mkdir()

    # Create DDD structure
    entities = project / "entities"
    entities.mkdir()
    (entities / "UserEntity.py").write_text("class UserEntity: pass")

    repositories = project / "repositories"
    repositories.mkdir()
    (repositories / "UserRepository.py").write_text("class UserRepository: pass")

    aggregates = project / "aggregates"
    aggregates.mkdir()
    (aggregates / "OrderAggregate.py").write_text("class OrderAggregate: pass")

    return project


# ==============================================================================
# Model Tests
# ==============================================================================

class TestArchitecturePattern:
    """Tests for ArchitecturePattern enum."""

    def test_pattern_values(self):
        """Test all pattern enum values."""
        assert ArchitecturePattern.HEXAGONAL.value == "hexagonal"
        assert ArchitecturePattern.LAYERED.value == "layered"
        assert ArchitecturePattern.CLEAN.value == "clean"
        assert ArchitecturePattern.DDD.value == "domain_driven_design"
        assert ArchitecturePattern.CQRS.value == "cqrs"
        assert ArchitecturePattern.EVENT_SOURCING.value == "event_sourcing"
        assert ArchitecturePattern.MICROSERVICES.value == "microservices"
        assert ArchitecturePattern.MVC.value == "mvc"
        assert ArchitecturePattern.MONOLITHIC.value == "monolithic"

    def test_pattern_is_string_enum(self):
        """Test that patterns can be used as strings."""
        pattern = ArchitecturePattern.HEXAGONAL
        assert isinstance(pattern.value, str)
        assert str(pattern) == "ArchitecturePattern.HEXAGONAL"


class TestPatternMatch:
    """Tests for PatternMatch model."""

    def test_create_pattern_match(self):
        """Test creating a pattern match."""
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.85,
            evidence=["domain/ found", "ports/ found"],
            violations=["Domain imports from adapters"],
            recommendations=["Fix domain imports"]
        )

        assert match.pattern == ArchitecturePattern.HEXAGONAL
        assert match.confidence == 0.85
        assert len(match.evidence) == 2
        assert len(match.violations) == 1
        assert len(match.recommendations) == 1

    def test_has_violations(self):
        """Test has_violations method."""
        match_with = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.8,
            violations=["Some violation"]
        )
        assert match_with.has_violations()

        match_without = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.8
        )
        assert not match_without.has_violations()

    def test_is_high_confidence(self):
        """Test is_high_confidence method."""
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.85
        )
        assert match.is_high_confidence(threshold=0.7)
        assert match.is_high_confidence(threshold=0.85)
        assert not match.is_high_confidence(threshold=0.9)

    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.5
        )
        assert match.confidence == 0.5

        # Invalid confidence (should raise validation error)
        with pytest.raises(Exception):  # Pydantic ValidationError
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=1.5  # > 1.0
            )

        with pytest.raises(Exception):  # Pydantic ValidationError
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=-0.1  # < 0.0
            )


class TestPatternAnalysis:
    """Tests for PatternAnalysis model."""

    def test_create_pattern_analysis(self):
        """Test creating a pattern analysis."""
        matches = [
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=0.85
            ),
            PatternMatch(
                pattern=ArchitecturePattern.DDD,
                confidence=0.75
            )
        ]

        analysis = PatternAnalysis(
            project_path="/path/to/project",
            matches=matches,
            primary_pattern=ArchitecturePattern.HEXAGONAL,
            confidence_threshold=0.6
        )

        assert analysis.project_path == "/path/to/project"
        assert len(analysis.matches) == 2
        assert analysis.primary_pattern == ArchitecturePattern.HEXAGONAL
        assert analysis.confidence_threshold == 0.6
        assert isinstance(analysis.analyzed_at, datetime)

    def test_get_high_confidence_patterns(self):
        """Test filtering high confidence patterns."""
        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.85),
            PatternMatch(pattern=ArchitecturePattern.DDD, confidence=0.75),
            PatternMatch(pattern=ArchitecturePattern.LAYERED, confidence=0.45),
            PatternMatch(pattern=ArchitecturePattern.MVC, confidence=0.30)
        ]

        analysis = PatternAnalysis(
            project_path="/path/to/project",
            matches=matches,
            confidence_threshold=0.5
        )

        high_conf = analysis.get_high_confidence_patterns()
        assert len(high_conf) == 2
        assert high_conf[0].pattern == ArchitecturePattern.HEXAGONAL
        assert high_conf[1].pattern == ArchitecturePattern.DDD

    def test_get_patterns_with_violations(self):
        """Test filtering patterns with violations."""
        matches = [
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=0.85,
                violations=["Some violation"]
            ),
            PatternMatch(
                pattern=ArchitecturePattern.DDD,
                confidence=0.75,
                violations=[]
            )
        ]

        analysis = PatternAnalysis(
            project_path="/path/to/project",
            matches=matches
        )

        with_violations = analysis.get_patterns_with_violations()
        assert len(with_violations) == 1
        assert with_violations[0].pattern == ArchitecturePattern.HEXAGONAL

    def test_get_match(self):
        """Test getting specific pattern match."""
        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.85),
            PatternMatch(pattern=ArchitecturePattern.DDD, confidence=0.75)
        ]

        analysis = PatternAnalysis(
            project_path="/path/to/project",
            matches=matches
        )

        hexagonal = analysis.get_match(ArchitecturePattern.HEXAGONAL)
        assert hexagonal is not None
        assert hexagonal.confidence == 0.85

        cqrs = analysis.get_match(ArchitecturePattern.CQRS)
        assert cqrs is None

    def test_get_sorted_matches(self):
        """Test sorting matches by confidence."""
        matches = [
            PatternMatch(pattern=ArchitecturePattern.LAYERED, confidence=0.45),
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.85),
            PatternMatch(pattern=ArchitecturePattern.DDD, confidence=0.75)
        ]

        analysis = PatternAnalysis(
            project_path="/path/to/project",
            matches=matches
        )

        # Descending order (default)
        sorted_desc = analysis.get_sorted_matches()
        assert sorted_desc[0].confidence == 0.85
        assert sorted_desc[1].confidence == 0.75
        assert sorted_desc[2].confidence == 0.45

        # Ascending order
        sorted_asc = analysis.get_sorted_matches(reverse=False)
        assert sorted_asc[0].confidence == 0.45
        assert sorted_asc[1].confidence == 0.75
        assert sorted_asc[2].confidence == 0.85


# ==============================================================================
# Service Tests
# ==============================================================================

class TestPatternRecognitionService:
    """Tests for PatternRecognitionService."""

    def test_init_with_valid_path(self, temp_project):
        """Test service initialization with valid path."""
        service = PatternRecognitionService(temp_project)
        assert service.project_path == temp_project

    def test_init_with_invalid_path(self, tmp_path):
        """Test service initialization with invalid path."""
        invalid_path = tmp_path / "nonexistent"

        with pytest.raises(ValueError, match="does not exist"):
            PatternRecognitionService(invalid_path)

    def test_init_with_file_path(self, tmp_path):
        """Test service initialization with file path (should fail)."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            PatternRecognitionService(file_path)

    @patch('agentpm.core.detection.patterns.service.detect_hexagonal_architecture')
    def test_detect_hexagonal(self, mock_detect, temp_project):
        """Test hexagonal architecture detection."""
        mock_detect.return_value = {
            'pattern': 'hexagonal',
            'confidence': 0.85,
            'evidence': ['domain/ found', 'ports/ found', 'adapters/ found'],
            'violations': []
        }

        service = PatternRecognitionService(temp_project)
        result = service.detect_hexagonal()

        assert result.pattern == ArchitecturePattern.HEXAGONAL
        assert result.confidence == 0.85
        assert len(result.evidence) == 3
        assert len(result.violations) == 0

        mock_detect.assert_called_once_with(temp_project)

    @patch('agentpm.core.detection.patterns.service.detect_layered_architecture')
    def test_detect_layered(self, mock_detect, layered_project):
        """Test layered architecture detection."""
        mock_detect.return_value = {
            'pattern': 'layered',
            'confidence': 0.75,
            'evidence': [
                'Presentation layer found',
                'Application layer found',
                'Domain layer found',
                'Data layer found'
            ],
            'violations': []
        }

        service = PatternRecognitionService(layered_project)
        result = service.detect_layered()

        assert result.pattern == ArchitecturePattern.LAYERED
        assert result.confidence == 0.75
        assert len(result.evidence) == 4

    @patch('agentpm.core.detection.patterns.service.detect_ddd_patterns')
    def test_detect_ddd(self, mock_detect, ddd_project):
        """Test DDD pattern detection."""
        mock_detect.return_value = {
            'pattern': 'ddd',
            'confidence': 0.80,
            'evidence': [
                'Entities: 1 found',
                'Repositories: 1 found',
                'Aggregates: 1 found'
            ],
            'violations': []
        }

        service = PatternRecognitionService(ddd_project)
        result = service.detect_ddd()

        assert result.pattern == ArchitecturePattern.DDD
        assert result.confidence == 0.80
        assert len(result.evidence) == 3

    @patch('agentpm.core.detection.patterns.service.detect_cqrs_pattern')
    def test_detect_cqrs(self, mock_detect, temp_project):
        """Test CQRS pattern detection."""
        mock_detect.return_value = {
            'pattern': 'cqrs',
            'confidence': 0.70,
            'evidence': ['commands/ found', 'queries/ found'],
            'violations': []
        }

        service = PatternRecognitionService(temp_project)
        result = service.detect_cqrs()

        assert result.pattern == ArchitecturePattern.CQRS
        assert result.confidence == 0.70

    @patch('agentpm.core.detection.patterns.service.detect_mvc_pattern')
    def test_detect_mvc(self, mock_detect, temp_project):
        """Test MVC pattern detection."""
        mock_detect.return_value = {
            'pattern': 'mvc',
            'confidence': 0.90,
            'evidence': [
                'models found (models/)',
                'views found (views/)',
                'controllers found (controllers/)'
            ],
            'violations': []
        }

        service = PatternRecognitionService(temp_project)
        result = service.detect_mvc()

        assert result.pattern == ArchitecturePattern.MVC
        assert result.confidence == 0.90

    @patch('agentpm.core.detection.patterns.service.detect_pattern_violations')
    def test_find_violations(self, mock_detect, temp_project):
        """Test violation detection."""
        mock_detect.return_value = [
            {
                'type': 'hexagonal_violation',
                'description': 'Domain importing from adapters',
                'location': 'domain/entity.py'
            }
        ]

        service = PatternRecognitionService(temp_project)
        violations = service.find_violations(ArchitecturePattern.HEXAGONAL)

        assert len(violations) == 1
        assert 'Domain importing from adapters' in violations[0]
        assert 'domain/entity.py' in violations[0]

    def test_format_violations_with_dict(self, temp_project):
        """Test formatting violations from dictionaries."""
        service = PatternRecognitionService(temp_project)

        violations = [
            {
                'type': 'violation_type',
                'description': 'Test violation',
                'location': 'file.py'
            }
        ]

        formatted = service._format_violations(violations)
        assert len(formatted) == 1
        assert 'violation_type' in formatted[0]
        assert 'Test violation' in formatted[0]
        assert 'file.py' in formatted[0]

    def test_format_violations_with_string(self, temp_project):
        """Test formatting violations from strings."""
        service = PatternRecognitionService(temp_project)

        violations = ['Simple violation string']
        formatted = service._format_violations(violations)

        assert len(formatted) == 1
        assert formatted[0] == 'Simple violation string'

    @patch('agentpm.core.detection.patterns.service.detect_hexagonal_architecture')
    @patch('agentpm.core.detection.patterns.service.detect_layered_architecture')
    @patch('agentpm.core.detection.patterns.service.detect_ddd_patterns')
    @patch('agentpm.core.detection.patterns.service.detect_cqrs_pattern')
    @patch('agentpm.core.detection.patterns.service.detect_mvc_pattern')
    def test_analyze_patterns(
        self,
        mock_mvc,
        mock_cqrs,
        mock_ddd,
        mock_layered,
        mock_hexagonal,
        temp_project
    ):
        """Test complete pattern analysis."""
        # Mock all pattern detectors
        mock_hexagonal.return_value = {
            'confidence': 0.85,
            'evidence': ['domain/', 'ports/', 'adapters/'],
            'violations': []
        }
        mock_layered.return_value = {
            'confidence': 0.45,
            'evidence': [],
            'violations': []
        }
        mock_ddd.return_value = {
            'confidence': 0.75,
            'evidence': ['Entities found'],
            'violations': []
        }
        mock_cqrs.return_value = {
            'confidence': 0.30,
            'evidence': [],
            'violations': []
        }
        mock_mvc.return_value = {
            'confidence': 0.20,
            'evidence': [],
            'violations': []
        }

        service = PatternRecognitionService(temp_project)
        analysis = service.analyze_patterns(confidence_threshold=0.5)

        assert analysis.project_path == str(temp_project)
        assert len(analysis.matches) == 5
        assert analysis.primary_pattern == ArchitecturePattern.HEXAGONAL

        # Check high confidence patterns
        high_conf = analysis.get_high_confidence_patterns()
        assert len(high_conf) == 2  # Hexagonal (0.85) and DDD (0.75)

    def test_determine_primary_pattern(self, temp_project):
        """Test determining primary pattern."""
        service = PatternRecognitionService(temp_project)

        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.85),
            PatternMatch(pattern=ArchitecturePattern.DDD, confidence=0.75),
            PatternMatch(pattern=ArchitecturePattern.LAYERED, confidence=0.45)
        ]

        primary = service._determine_primary_pattern(matches)
        assert primary == ArchitecturePattern.HEXAGONAL

    def test_determine_primary_pattern_no_valid(self, temp_project):
        """Test determining primary pattern with no valid matches."""
        service = PatternRecognitionService(temp_project)

        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.30),
            PatternMatch(pattern=ArchitecturePattern.DDD, confidence=0.40)
        ]

        primary = service._determine_primary_pattern(matches)
        assert primary is None

    def test_generate_recommendations_no_clear_pattern(self, temp_project):
        """Test recommendations when no clear pattern."""
        service = PatternRecognitionService(temp_project)

        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.30)
        ]

        recommendations = service.generate_recommendations(matches)
        assert len(recommendations) > 0
        assert any('No clear architecture pattern' in r for r in recommendations)

    def test_generate_recommendations_multiple_patterns(self, temp_project):
        """Test recommendations with multiple patterns."""
        service = PatternRecognitionService(temp_project)

        matches = [
            PatternMatch(pattern=ArchitecturePattern.HEXAGONAL, confidence=0.75),
            PatternMatch(pattern=ArchitecturePattern.LAYERED, confidence=0.75),
            PatternMatch(pattern=ArchitecturePattern.MVC, confidence=0.75)
        ]

        recommendations = service.generate_recommendations(matches)
        assert any('Multiple architecture patterns' in r for r in recommendations)

    def test_generate_recommendations_with_violations(self, temp_project):
        """Test recommendations with violations."""
        service = PatternRecognitionService(temp_project)

        matches = [
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=0.85,
                violations=['Domain imports from adapters']
            )
        ]

        recommendations = service.generate_recommendations(matches)
        assert any('violation' in r.lower() for r in recommendations)

    @patch('agentpm.core.detection.patterns.service.detect_hexagonal_architecture')
    def test_detect_hexagonal_with_error(self, mock_detect, temp_project):
        """Test hexagonal detection with error handling."""
        mock_detect.side_effect = Exception("Test error")

        service = PatternRecognitionService(temp_project)
        result = service.detect_hexagonal()

        assert result.pattern == ArchitecturePattern.HEXAGONAL
        assert result.confidence == 0.0
        assert len(result.violations) > 0
        assert 'Error during detection' in result.violations[0]


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestPatternRecognitionIntegration:
    """Integration tests for pattern recognition."""

    def test_real_hexagonal_project_detection(self, temp_project):
        """Test detection on real hexagonal project structure."""
        service = PatternRecognitionService(temp_project)
        analysis = service.analyze_patterns()

        # Should detect hexagonal architecture
        hexagonal = analysis.get_match(ArchitecturePattern.HEXAGONAL)
        assert hexagonal is not None
        # Confidence should be reasonable (structure exists)
        assert hexagonal.confidence > 0.0

    def test_real_layered_project_detection(self, layered_project):
        """Test detection on real layered project structure."""
        service = PatternRecognitionService(layered_project)
        analysis = service.analyze_patterns()

        # Should detect layered architecture
        layered = analysis.get_match(ArchitecturePattern.LAYERED)
        assert layered is not None
        assert layered.confidence > 0.0

    def test_real_ddd_project_detection(self, ddd_project):
        """Test detection on real DDD project structure."""
        service = PatternRecognitionService(ddd_project)
        analysis = service.analyze_patterns()

        # Should detect DDD patterns
        ddd = analysis.get_match(ArchitecturePattern.DDD)
        assert ddd is not None
        assert ddd.confidence > 0.0
        assert len(ddd.evidence) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
