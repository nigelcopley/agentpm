"""
Pattern Recognition Service - Usage Examples

Demonstrates how to use the PatternRecognitionService to detect
architecture patterns in Python projects.

Run this example:
    python examples/pattern_recognition_example.py

Author: APM (Agent Project Manager)
Date: 2025-10-24
"""

from pathlib import Path
from agentpm.core.detection.patterns import (
    ArchitecturePattern,
    PatternRecognitionService,
)


def example_1_basic_usage():
    """Example 1: Basic pattern detection on current project."""
    print("=" * 80)
    print("Example 1: Basic Pattern Detection")
    print("=" * 80)

    # Initialize service for current project
    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Analyze all patterns
    analysis = service.analyze_patterns(confidence_threshold=0.5)

    # Display results
    print(f"\nProject: {analysis.project_path}")
    print(f"Primary Pattern: {analysis.primary_pattern}")
    print(f"Analyzed At: {analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal Patterns Detected: {len(analysis.matches)}")

    # Show all matches
    print("\n" + "-" * 80)
    print("All Pattern Matches:")
    print("-" * 80)
    for match in analysis.get_sorted_matches():
        confidence_bar = "█" * int(match.confidence * 20)
        print(f"\n{match.pattern.value.upper()}: {match.confidence:.0%} {confidence_bar}")

        if match.evidence:
            print("  Evidence:")
            for evidence in match.evidence[:3]:  # Show first 3
                print(f"    ✓ {evidence}")
            if len(match.evidence) > 3:
                print(f"    ... and {len(match.evidence) - 3} more")

        if match.violations:
            print("  Violations:")
            for violation in match.violations[:2]:  # Show first 2
                print(f"    ✗ {violation}")
            if len(match.violations) > 2:
                print(f"    ... and {len(match.violations) - 2} more")


def example_2_high_confidence_patterns():
    """Example 2: Filter and display only high confidence patterns."""
    print("\n" + "=" * 80)
    print("Example 2: High Confidence Patterns Only")
    print("=" * 80)

    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Analyze with higher threshold
    analysis = service.analyze_patterns(confidence_threshold=0.7)

    high_confidence = analysis.get_high_confidence_patterns()

    print(f"\nHigh Confidence Patterns (>= 70%):")
    print("-" * 80)

    if high_confidence:
        for match in high_confidence:
            print(f"\n{match.pattern.value.upper()}")
            print(f"  Confidence: {match.confidence:.0%}")
            print(f"  Evidence Count: {len(match.evidence)}")
            print(f"  Violations: {len(match.violations)}")

            if match.recommendations:
                print(f"  Recommendations:")
                for rec in match.recommendations:
                    print(f"    → {rec}")
    else:
        print("  No patterns with confidence >= 70%")


def example_3_individual_pattern_detection():
    """Example 3: Detect specific individual patterns."""
    print("\n" + "=" * 80)
    print("Example 3: Individual Pattern Detection")
    print("=" * 80)

    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Detect hexagonal architecture
    print("\n1. Hexagonal Architecture Detection:")
    print("-" * 80)
    hexagonal = service.detect_hexagonal()
    print(f"   Confidence: {hexagonal.confidence:.0%}")
    if hexagonal.evidence:
        print(f"   Evidence:")
        for evidence in hexagonal.evidence[:3]:
            print(f"     • {evidence}")

    # Detect DDD patterns
    print("\n2. Domain-Driven Design Detection:")
    print("-" * 80)
    ddd = service.detect_ddd()
    print(f"   Confidence: {ddd.confidence:.0%}")
    if ddd.evidence:
        print(f"   Evidence:")
        for evidence in ddd.evidence[:3]:
            print(f"     • {evidence}")

    # Detect layered architecture
    print("\n3. Layered Architecture Detection:")
    print("-" * 80)
    layered = service.detect_layered()
    print(f"   Confidence: {layered.confidence:.0%}")
    if layered.evidence:
        print(f"   Evidence:")
        for evidence in layered.evidence[:3]:
            print(f"     • {evidence}")


def example_4_violation_detection():
    """Example 4: Detect and report architecture violations."""
    print("\n" + "=" * 80)
    print("Example 4: Architecture Violation Detection")
    print("=" * 80)

    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Analyze patterns
    analysis = service.analyze_patterns()

    # Get patterns with violations
    with_violations = analysis.get_patterns_with_violations()

    print(f"\nPatterns with Violations: {len(with_violations)}")
    print("-" * 80)

    if with_violations:
        for match in with_violations:
            print(f"\n{match.pattern.value.upper()}")
            print(f"  Confidence: {match.confidence:.0%}")
            print(f"  Violations ({len(match.violations)}):")
            for violation in match.violations:
                print(f"    ⚠ {violation}")
    else:
        print("  No violations detected! ✓")

    # Check specific pattern violations
    print("\n\nDetailed Hexagonal Violations:")
    print("-" * 80)
    hex_violations = service.find_violations(ArchitecturePattern.HEXAGONAL)
    if hex_violations:
        for violation in hex_violations:
            print(f"  ⚠ {violation}")
    else:
        print("  No hexagonal violations detected! ✓")


def example_5_recommendations():
    """Example 5: Generate architecture recommendations."""
    print("\n" + "=" * 80)
    print("Example 5: Architecture Recommendations")
    print("=" * 80)

    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Analyze patterns
    analysis = service.analyze_patterns()

    # Generate recommendations
    recommendations = service.generate_recommendations(analysis.matches)

    print(f"\nArchitecture Recommendations ({len(recommendations)}):")
    print("-" * 80)

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec}")
    else:
        print("  No recommendations - architecture looks good! ✓")


def example_6_json_export():
    """Example 6: Export analysis results to JSON."""
    print("\n" + "=" * 80)
    print("Example 6: Export Analysis to JSON")
    print("=" * 80)

    project_path = Path(__file__).parent.parent
    service = PatternRecognitionService(project_path)

    # Analyze patterns
    analysis = service.analyze_patterns(confidence_threshold=0.6)

    # Convert to JSON (Pydantic model_dump)
    json_data = analysis.model_dump(mode='json')

    print("\nJSON Export (sample):")
    print("-" * 80)
    print(f"Project: {json_data['project_path']}")
    print(f"Primary Pattern: {json_data['primary_pattern']}")
    print(f"Confidence Threshold: {json_data['confidence_threshold']}")
    print(f"\nMatches: {len(json_data['matches'])} patterns")

    # Show first match
    if json_data['matches']:
        first_match = json_data['matches'][0]
        print(f"\nFirst Match:")
        print(f"  Pattern: {first_match['pattern']}")
        print(f"  Confidence: {first_match['confidence']:.0%}")
        print(f"  Evidence: {len(first_match['evidence'])} items")
        print(f"  Violations: {len(first_match['violations'])} items")

    # Could save to file
    # import json
    # with open('pattern_analysis.json', 'w') as f:
    #     json.dump(json_data, f, indent=2, default=str)
    print("\n  (JSON data can be saved to file for reporting)")


def example_7_pattern_comparison():
    """Example 7: Compare multiple projects."""
    print("\n" + "=" * 80)
    print("Example 7: Pattern Comparison")
    print("=" * 80)

    # This example shows how to compare patterns across multiple projects
    project_path = Path(__file__).parent.parent

    # Analyze multiple subdirectories
    subdirs = [
        project_path / "agentpm" / "core",
        project_path / "agentpm" / "web",
        project_path / "agentpm" / "cli"
    ]

    results = []

    print("\nAnalyzing project components:")
    print("-" * 80)

    for subdir in subdirs:
        if subdir.exists():
            service = PatternRecognitionService(subdir)
            analysis = service.analyze_patterns(confidence_threshold=0.5)

            results.append({
                'path': subdir.name,
                'primary': analysis.primary_pattern,
                'confidence': max(
                    (m.confidence for m in analysis.matches),
                    default=0.0
                )
            })

    # Display comparison
    print("\nPattern Comparison:")
    print("-" * 80)
    print(f"{'Component':<20} {'Primary Pattern':<25} {'Confidence':<15}")
    print("-" * 80)

    for result in results:
        primary = result['primary'] or 'None'
        if isinstance(primary, ArchitecturePattern):
            primary = primary.value

        print(f"{result['path']:<20} {primary:<25} {result['confidence']:.0%}")


def main():
    """Run all examples."""
    try:
        example_1_basic_usage()
        example_2_high_confidence_patterns()
        example_3_individual_pattern_detection()
        example_4_violation_detection()
        example_5_recommendations()
        example_6_json_export()
        example_7_pattern_comparison()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
