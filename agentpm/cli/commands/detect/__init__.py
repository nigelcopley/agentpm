"""
Detection Pack CLI Commands

Comprehensive project analysis and intelligence.

Commands:
- analyze: Static code analysis (complexity, maintainability metrics)
- graph: Dependency graph analysis (cycles, coupling)
- sbom: SBOM generation (CycloneDX, SPDX formats)
- patterns: Architecture pattern detection
- fitness: Architecture fitness testing (policy validation)
"""

import click

# Import all subcommands
from .analyze import analyze
from .graph import graph
from .sbom import sbom
from .patterns import patterns
from .fitness import fitness


@click.group(name='detect')
def detect():
    """
    🔍 Detection Pack - Comprehensive project analysis.

    Provides deep project intelligence for architecture, dependencies,
    code quality, and security compliance.

    \b
    Analysis Capabilities:
      analyze  - Static code analysis (complexity, maintainability)
      graph    - Dependency graphs (cycles, coupling)
      sbom     - Software Bill of Materials (CycloneDX, SPDX)
      patterns - Architecture pattern detection
      fitness  - Fitness testing (policy validation)

    \b
    Examples:
      apm detect analyze                          # Code quality metrics
      apm detect graph --detect-cycles            # Find circular dependencies
      apm detect sbom --format spdx               # Generate SPDX SBOM
      apm detect patterns                         # Detect architecture patterns
      apm detect fitness                          # Run fitness tests

    \b
    Use Cases:
      - Code quality assessment before work items
      - Dependency management and risk analysis
      - Compliance reporting (SBOM generation)
      - Architecture validation and governance
      - Security vulnerability detection

    \b
    Integration:
      Results are stored in AIPM database for tracking:
      - Detection results linked to work items
      - Historical trend analysis
      - Quality gate enforcement
    """
    pass


# Register subcommands
detect.add_command(analyze)
detect.add_command(graph)
detect.add_command(sbom)
detect.add_command(patterns)
detect.add_command(fitness)
