#!/usr/bin/env python3
"""
Example: Architecture Fitness Testing with APM (Agent Project Manager)

Demonstrates how to use the FitnessEngine to validate code quality
and architectural compliance.

Usage:
    python examples/fitness_example.py

Author: APM (Agent Project Manager) Detection Pack Team
"""

from pathlib import Path
from agentpm.core.detection.fitness import (
    FitnessEngine,
    PolicyLevel,
    Policy,
)
from agentpm.core.detection.fitness.policies import (
    get_policies_by_tag,
    get_policy_statistics,
    create_policy_from_dict,
)


def example_1_basic_testing():
    """Example 1: Basic fitness testing."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Fitness Testing")
    print("="*70)

    # Initialize engine for current project
    project_path = Path.cwd()
    print(f"\nProject: {project_path}")

    engine = FitnessEngine(project_path)

    # Load default policies
    policies = engine.load_default_policies()
    print(f"Loaded {len(policies)} policies")

    # Get summary
    summary = engine.get_policy_summary(policies)
    print(f"\nPolicy Summary:")
    print(f"  Total: {summary['total']}")
    print(f"  Enabled: {summary['enabled']}")
    print(f"  By level:")
    for level, count in summary['by_level'].items():
        print(f"    {level}: {count}")

    # Run tests
    print("\nRunning fitness tests...")
    result = engine.run_tests(policies)

    # Print results
    print(f"\n{result.get_summary()}")

    if result.violations:
        print(f"\nViolations found:")
        for violation in result.violations[:5]:  # First 5
            print(f"\n  {violation.level.upper()}: {violation.message}")
            print(f"  Location: {violation.location}")
            if violation.suggestion:
                print(f"  Fix: {violation.suggestion}")

        if len(result.violations) > 5:
            print(f"\n  ... and {len(result.violations) - 5} more")


def example_2_complexity_only():
    """Example 2: Test complexity policies only."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Complexity Policies Only")
    print("="*70)

    engine = FitnessEngine(Path.cwd())

    # Get complexity policies
    complexity_dicts = get_policies_by_tag("complexity")
    complexity_policies = [create_policy_from_dict(p) for p in complexity_dicts]

    print(f"\nTesting {len(complexity_policies)} complexity policies:")
    for policy in complexity_policies:
        print(f"  - {policy.name} ({policy.level.upper()})")

    # Run tests
    result = engine.run_tests(complexity_policies)
    print(f"\n{result.get_summary()}")


def example_3_error_only():
    """Example 3: Test ERROR-level policies only."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Critical (ERROR-level) Policies Only")
    print("="*70)

    engine = FitnessEngine(Path.cwd())

    # Get all policies and filter to ERROR
    all_policies = engine.load_default_policies()
    error_policies = [p for p in all_policies if p.level == PolicyLevel.ERROR]

    print(f"\nTesting {len(error_policies)} critical policies:")
    for policy in error_policies:
        print(f"  - {policy.name}")

    # Run tests
    result = engine.run_tests(error_policies)

    # Exit with error code if failed
    if not result.is_passing():
        print(f"\n✗ FAILED: {result.error_count} critical violations")
        for violation in result.get_violations_by_level(PolicyLevel.ERROR):
            print(f"\n  ERROR: {violation.message}")
            print(f"  Location: {violation.location}")
    else:
        print(f"\n✓ PASSED: All critical policies passed")


def example_4_custom_policy():
    """Example 4: Create and test custom policy."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Policy")
    print("="*70)

    engine = FitnessEngine(Path.cwd())

    # Create custom policy with stricter complexity threshold
    custom_policy = Policy(
        policy_id="STRICT_COMPLEXITY",
        name="Very Strict Complexity",
        description="Functions must not exceed complexity of 5",
        level=PolicyLevel.ERROR,
        validation_fn="validate_max_complexity",
        tags=["complexity", "strict"],
        enabled=True,
        metadata={"threshold": 5}
    )

    print(f"\nCustom policy: {custom_policy.name}")
    print(f"  Threshold: {custom_policy.metadata['threshold']}")
    print(f"  Level: {custom_policy.level.upper()}")

    # Run test
    result = engine.run_tests([custom_policy])
    print(f"\n{result.get_summary()}")

    if result.violations:
        print(f"\nFunctions exceeding complexity of 5:")
        for violation in result.violations[:10]:
            print(f"  - {violation.location}: {violation.message}")


def example_5_statistics():
    """Example 5: Policy statistics."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Policy Statistics")
    print("="*70)

    # Get statistics
    stats = get_policy_statistics()

    print(f"\nDefault Policy Statistics:")
    print(f"  Total policies: {stats['total']}")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Disabled: {stats['disabled']}")

    print(f"\n  By enforcement level:")
    for level, count in stats['by_level'].items():
        print(f"    {level}: {count}")

    print(f"\n  By category:")
    for tag, count in sorted(stats['by_tag'].items()):
        print(f"    {tag}: {count}")

    print(f"\n  Available tags: {', '.join(stats['all_tags'])}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("APM (Agent Project Manager) Fitness Engine - Examples")
    print("="*70)

    try:
        # Run examples
        example_1_basic_testing()
        example_2_complexity_only()
        example_3_error_only()
        example_4_custom_policy()
        example_5_statistics()

        print("\n" + "="*70)
        print("Examples completed!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
