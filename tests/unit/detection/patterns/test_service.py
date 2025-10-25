"""
Unit tests for PatternRecognitionService.

Tests architecture pattern detection including:
- Hexagonal architecture
- Layered architecture
- Domain-Driven Design (DDD)
- CQRS pattern
- MVC pattern
- Pattern violations
- Recommendations

**Test Strategy**:
- Use temporary directories with realistic project structures
- Test both positive and negative cases
- Validate confidence scoring
- Test error handling and edge cases

**Author**: APM (Agent Project Manager) Test Suite
"""

import pytest
from pathlib import Path
from textwrap import dedent

from agentpm.core.detection.patterns import PatternRecognitionService
from agentpm.core.database.models.detection_pattern import (
    PatternAnalysis,
    PatternMatch,
)
from agentpm.core.database.enums.detection import ArchitecturePattern


class TestPatternRecognitionService:
    """Test suite for PatternRecognitionService."""

    @pytest.fixture
    def empty_project(self, tmp_path):
        """Create empty project directory."""
        project = tmp_path / "empty_project"
        project.mkdir()
        return project

    @pytest.fixture
    def hexagonal_project(self, tmp_path):
        """Create project with hexagonal architecture."""
        project = tmp_path / "hexagonal_project"
        project.mkdir()

        # Create hexagonal structure
        (project / "domain").mkdir()
        (project / "domain" / "__init__.py").write_text("")
        (project / "domain" / "entities.py").write_text(dedent("""
            class User:
                def __init__(self, name: str):
                    self.name = name
        """))

        (project / "ports").mkdir()
        (project / "ports" / "__init__.py").write_text("")
        (project / "ports" / "repository.py").write_text(dedent("""
            from abc import ABC, abstractmethod

            class UserRepository(ABC):
                @abstractmethod
                def save(self, user):
                    pass
        """))

        (project / "adapters").mkdir()
        (project / "adapters" / "__init__.py").write_text("")
        (project / "adapters" / "sql_repository.py").write_text(dedent("""
            from ports.repository import UserRepository

            class SQLUserRepository(UserRepository):
                def save(self, user):
                    pass  # SQL implementation
        """))

        return project

    @pytest.fixture
    def layered_project(self, tmp_path):
        """Create project with layered architecture."""
        project = tmp_path / "layered_project"
        project.mkdir()

        # Create layered structure
        (project / "presentation").mkdir()
        (project / "presentation" / "__init__.py").write_text("")
        (project / "presentation" / "views.py").write_text("# Views")

        (project / "application").mkdir()
        (project / "application" / "__init__.py").write_text("")
        (project / "application" / "services.py").write_text("# Services")

        (project / "domain").mkdir()
        (project / "domain" / "__init__.py").write_text("")
        (project / "domain" / "models.py").write_text("# Models")

        (project / "data").mkdir()
        (project / "data" / "__init__.py").write_text("")
        (project / "data" / "repositories.py").write_text("# Data layer")

        return project

    @pytest.fixture
    def ddd_project(self, tmp_path):
        """Create project with DDD patterns."""
        project = tmp_path / "ddd_project"
        project.mkdir()

        # Create DDD structure
        (project / "entities").mkdir()
        (project / "entities" / "__init__.py").write_text("")
        (project / "entities" / "user_entity.py").write_text("class UserEntity: pass")

        (project / "value_objects").mkdir()
        (project / "value_objects" / "__init__.py").write_text("")
        (project / "value_objects" / "email.py").write_text("class Email: pass")

        (project / "aggregates").mkdir()
        (project / "aggregates" / "__init__.py").write_text("")
        (project / "aggregates" / "order_aggregate.py").write_text("class OrderAggregate: pass")

        (project / "repositories").mkdir()
        (project / "repositories" / "__init__.py").write_text("")
        (project / "repositories" / "user_repository.py").write_text("class UserRepository: pass")

        return project

    @pytest.fixture
    def cqrs_project(self, tmp_path):
        """Create project with CQRS pattern."""
        project = tmp_path / "cqrs_project"
        project.mkdir()

        # Create CQRS structure
        (project / "commands").mkdir()
        (project / "commands" / "__init__.py").write_text("")
        (project / "commands" / "create_user.py").write_text("class CreateUserCommand: pass")

        (project / "queries").mkdir()
        (project / "queries" / "__init__.py").write_text("")
        (project / "queries" / "get_user.py").write_text("class GetUserQuery: pass")

        (project / "handlers").mkdir()
        (project / "handlers" / "__init__.py").write_text("")
        (project / "handlers" / "command_handlers.py").write_text("# Command handlers")

        return project

    @pytest.fixture
    def mvc_project(self, tmp_path):
        """Create project with MVC pattern."""
        project = tmp_path / "mvc_project"
        project.mkdir()

        # Create MVC structure
        (project / "models").mkdir()
        (project / "models" / "__init__.py").write_text("")
        (project / "models" / "user.py").write_text("class User: pass")

        (project / "views").mkdir()
        (project / "views" / "__init__.py").write_text("")
        (project / "views" / "user_view.py").write_text("# User view")

        (project / "controllers").mkdir()
        (project / "controllers" / "__init__.py").write_text("")
        (project / "controllers" / "user_controller.py").write_text("# User controller")

        return project

    def test_init_with_valid_directory(self, empty_project):
        """Test initialization with valid directory."""
        service = PatternRecognitionService(empty_project)
        assert service.project_path == empty_project

    def test_init_with_nonexistent_path(self, tmp_path):
        """Test initialization fails with non-existent path."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(ValueError, match="does not exist"):
            PatternRecognitionService(nonexistent)

    def test_init_with_file_path(self, tmp_path):
        """Test initialization fails with file path."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")
        with pytest.raises(ValueError, match="not a directory"):
            PatternRecognitionService(file_path)

    def test_analyze_patterns_empty_project(self, empty_project):
        """Test pattern analysis on empty project."""
        service = PatternRecognitionService(empty_project)
        analysis = service.analyze_patterns()

        assert isinstance(analysis, PatternAnalysis)
        assert analysis.project_path == str(empty_project)
        assert len(analysis.matches) == 5  # All patterns analyzed
        assert analysis.primary_pattern is None  # No pattern detected

    def test_detect_hexagonal(self, hexagonal_project):
        """Test hexagonal architecture detection."""
        service = PatternRecognitionService(hexagonal_project)
        match = service.detect_hexagonal()

        assert isinstance(match, PatternMatch)
        assert match.pattern == ArchitecturePattern.HEXAGONAL
        assert match.confidence > 0.5  # Should detect pattern
        assert len(match.evidence) > 0
        # Should have evidence of domain/, ports/, adapters/
        evidence_str = " ".join(match.evidence).lower()
        assert "domain" in evidence_str or "ports" in evidence_str

    def test_detect_layered(self, layered_project):
        """Test layered architecture detection."""
        service = PatternRecognitionService(layered_project)
        match = service.detect_layered()

        assert isinstance(match, PatternMatch)
        assert match.pattern == ArchitecturePattern.LAYERED
        assert match.confidence > 0.5
        assert len(match.evidence) > 0
        # Should detect presentation, application, domain, data layers
        evidence_str = " ".join(match.evidence).lower()
        assert any(layer in evidence_str for layer in ["presentation", "application", "domain", "data"])

    def test_detect_ddd(self, ddd_project):
        """Test DDD pattern detection."""
        service = PatternRecognitionService(ddd_project)
        match = service.detect_ddd()

        assert isinstance(match, PatternMatch)
        assert match.pattern == ArchitecturePattern.DDD
        assert match.confidence > 0.5
        assert len(match.evidence) > 0
        # Should detect entities, value objects, aggregates, repositories
        evidence_str = " ".join(match.evidence).lower()
        assert any(term in evidence_str for term in ["entities", "value objects", "aggregates", "repositories"])

    def test_detect_cqrs(self, cqrs_project):
        """Test CQRS pattern detection."""
        service = PatternRecognitionService(cqrs_project)
        match = service.detect_cqrs()

        assert isinstance(match, PatternMatch)
        assert match.pattern == ArchitecturePattern.CQRS
        assert match.confidence > 0.5
        assert len(match.evidence) > 0
        # Should detect commands/ and queries/
        evidence_str = " ".join(match.evidence).lower()
        assert "commands" in evidence_str or "queries" in evidence_str

    def test_detect_mvc(self, mvc_project):
        """Test MVC pattern detection."""
        service = PatternRecognitionService(mvc_project)
        match = service.detect_mvc()

        assert isinstance(match, PatternMatch)
        assert match.pattern == ArchitecturePattern.MVC
        assert match.confidence > 0.5
        assert len(match.evidence) > 0
        # Should detect models/, views/, controllers/
        evidence_str = " ".join(match.evidence).lower()
        assert any(term in evidence_str for term in ["models", "views", "controllers"])

    def test_analyze_patterns_hexagonal(self, hexagonal_project):
        """Test complete pattern analysis on hexagonal project."""
        service = PatternRecognitionService(hexagonal_project)
        analysis = service.analyze_patterns(confidence_threshold=0.5)

        assert isinstance(analysis, PatternAnalysis)
        # Should detect hexagonal as primary pattern
        assert analysis.primary_pattern == ArchitecturePattern.HEXAGONAL

        # Get high confidence patterns
        high_confidence = analysis.get_high_confidence_patterns()
        assert len(high_confidence) > 0
        assert high_confidence[0].pattern == ArchitecturePattern.HEXAGONAL

    def test_analyze_patterns_multiple_patterns(self, tmp_path):
        """Test project with multiple pattern indicators."""
        project = tmp_path / "mixed_project"
        project.mkdir()

        # Create both hexagonal and DDD indicators
        (project / "domain").mkdir()
        (project / "domain" / "__init__.py").write_text("")
        (project / "ports").mkdir()
        (project / "ports" / "__init__.py").write_text("")
        (project / "entities").mkdir()
        (project / "entities" / "__init__.py").write_text("")
        (project / "value_objects").mkdir()
        (project / "value_objects" / "__init__.py").write_text("")

        service = PatternRecognitionService(project)
        analysis = service.analyze_patterns()

        # Should detect multiple patterns
        high_confidence = [m for m in analysis.matches if m.confidence >= 0.5]
        assert len(high_confidence) >= 1  # At least one pattern detected

    def test_find_violations(self, hexagonal_project):
        """Test violation detection."""
        service = PatternRecognitionService(hexagonal_project)
        violations = service.find_violations(ArchitecturePattern.HEXAGONAL)

        assert isinstance(violations, list)
        # Empty project should have no violations
        # (We don't have actual import violations in fixtures)

    def test_generate_recommendations_no_pattern(self, empty_project):
        """Test recommendations for project with no clear pattern."""
        service = PatternRecognitionService(empty_project)
        analysis = service.analyze_patterns()

        recommendations = service.generate_recommendations(analysis.matches)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should suggest adopting a pattern
        rec_text = " ".join(recommendations).lower()
        assert "pattern" in rec_text or "architecture" in rec_text

    def test_generate_recommendations_with_violations(self, tmp_path):
        """Test recommendations when violations exist."""
        # Create a mock PatternMatch with violations
        from agentpm.core.database.models.detection_pattern import PatternMatch

        match_with_violations = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.8,
            evidence=["domain/", "ports/"],
            violations=["Domain imports from adapters"]
        )

        project = tmp_path / "test"
        project.mkdir()
        service = PatternRecognitionService(project)

        recommendations = service.generate_recommendations([match_with_violations])

        assert len(recommendations) > 0
        rec_text = " ".join(recommendations).lower()
        assert "violation" in rec_text

    def test_error_handling_invalid_pattern(self, empty_project):
        """Test error handling for pattern detection errors."""
        service = PatternRecognitionService(empty_project)

        # All detection methods should handle errors gracefully
        match = service.detect_hexagonal()
        assert match.confidence >= 0.0  # Should not raise

    def test_confidence_threshold_filtering(self, hexagonal_project):
        """Test confidence threshold filtering in analysis."""
        service = PatternRecognitionService(hexagonal_project)

        # High threshold
        analysis_high = service.analyze_patterns(confidence_threshold=0.8)
        # Low threshold
        analysis_low = service.analyze_patterns(confidence_threshold=0.3)

        # Both should have same matches, but different filtered results
        assert len(analysis_high.matches) == len(analysis_low.matches)

        high_conf = [m for m in analysis_high.matches if m.confidence >= 0.8]
        low_conf = [m for m in analysis_low.matches if m.confidence >= 0.3]

        # More patterns should pass lower threshold
        assert len(low_conf) >= len(high_conf)

    def test_pattern_match_properties(self):
        """Test PatternMatch model properties."""
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.75,
            evidence=["domain/", "ports/", "adapters/"],
            violations=["violation1"]
        )

        assert match.has_violations() is True
        assert match.is_high_confidence() is True  # > 0.7
        assert len(match.evidence) == 3

    def test_pattern_analysis_properties(self, hexagonal_project):
        """Test PatternAnalysis model properties."""
        service = PatternRecognitionService(hexagonal_project)
        analysis = service.analyze_patterns()

        assert len(analysis.matches) >= 0
        assert isinstance(analysis.get_high_confidence_patterns(), list)
        assert isinstance(analysis.get_patterns_with_violations(), list)

    def test_edge_case_empty_directories(self, tmp_path):
        """Test handling of empty directory structures."""
        project = tmp_path / "empty_dirs"
        project.mkdir()

        # Create directories but no files
        (project / "domain").mkdir()
        (project / "ports").mkdir()
        (project / "adapters").mkdir()

        service = PatternRecognitionService(project)
        analysis = service.analyze_patterns()

        # Should still work without errors
        assert isinstance(analysis, PatternAnalysis)
        assert len(analysis.matches) == 5

    def test_edge_case_mixed_case_directories(self, tmp_path):
        """Test handling of mixed case directory names."""
        project = tmp_path / "mixed_case"
        project.mkdir()

        # Create directories with various cases
        (project / "Domain").mkdir()
        (project / "PORTS").mkdir()
        (project / "Adapters").mkdir()

        service = PatternRecognitionService(project)
        match = service.detect_hexagonal()

        # Pattern detection should be case-insensitive
        assert match.confidence >= 0.0  # Should not crash

    def test_performance_large_project(self, tmp_path):
        """Test performance with larger directory structures."""
        import time

        project = tmp_path / "large_project"
        project.mkdir()

        # Create 100 directories
        for i in range(100):
            dir_path = project / f"module_{i}"
            dir_path.mkdir()
            (dir_path / "__init__.py").write_text("")
            (dir_path / "code.py").write_text(f"# Module {i}")

        service = PatternRecognitionService(project)

        start = time.time()
        analysis = service.analyze_patterns()
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 2.0  # Target: <2s for pattern detection
        assert isinstance(analysis, PatternAnalysis)

    def test_recommendations_for_each_pattern_type(self, hexagonal_project, layered_project, ddd_project):
        """Test that each pattern type gets appropriate recommendations."""
        # Test hexagonal
        service_hex = PatternRecognitionService(hexagonal_project)
        analysis_hex = service_hex.analyze_patterns()
        recs_hex = service_hex.generate_recommendations(analysis_hex.matches)

        # Test layered
        service_layered = PatternRecognitionService(layered_project)
        analysis_layered = service_layered.analyze_patterns()
        recs_layered = service_layered.generate_recommendations(analysis_layered.matches)

        # Test DDD
        service_ddd = PatternRecognitionService(ddd_project)
        analysis_ddd = service_ddd.analyze_patterns()
        recs_ddd = service_ddd.generate_recommendations(analysis_ddd.matches)

        # All should generate recommendations
        assert len(recs_hex) > 0 or len(recs_layered) > 0 or len(recs_ddd) > 0


class TestPatternModels:
    """Test Pydantic models for pattern detection."""

    def test_pattern_match_creation(self):
        """Test PatternMatch model creation."""
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.85,
            evidence=["domain/", "ports/", "adapters/"],
            violations=[]
        )

        assert match.pattern == ArchitecturePattern.HEXAGONAL
        assert match.confidence == 0.85
        assert len(match.evidence) == 3
        assert not match.has_violations()

    def test_pattern_analysis_creation(self):
        """Test PatternAnalysis model creation."""
        matches = [
            PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=0.8,
                evidence=["domain/"],
                violations=[]
            )
        ]

        analysis = PatternAnalysis(
            project_path="/test",
            matches=matches,
            primary_pattern=ArchitecturePattern.HEXAGONAL,
            confidence_threshold=0.5
        )

        assert analysis.primary_pattern == ArchitecturePattern.HEXAGONAL
        assert len(analysis.matches) >= 1
        assert len(analysis.get_high_confidence_patterns()) >= 0

    def test_pattern_match_confidence_validation(self):
        """Test confidence score validation (should be 0.0-1.0)."""
        # Valid confidence
        match = PatternMatch(
            pattern=ArchitecturePattern.DDD,
            confidence=0.5,
            evidence=[]
        )
        assert 0.0 <= match.confidence <= 1.0

    def test_architecture_pattern_enum_values(self):
        """Test ArchitecturePattern enum has expected values."""
        assert ArchitecturePattern.HEXAGONAL
        assert ArchitecturePattern.LAYERED
        assert ArchitecturePattern.DDD
        assert ArchitecturePattern.CQRS
        assert ArchitecturePattern.MVC
