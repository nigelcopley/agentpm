"""
Rules Catalog Migrator - YAML to Database Metadata

Migrates rules_catalog.yaml content to projects.metadata JSON field.
Enables configuration consolidation (WI-40, Task #217).

Pattern: One-time data migration, preserves YAML file for fallback.

Usage:
    >>> from agentpm.core.database import DatabaseService
    >>> from agentpm.core.rules.migrator import migrate_rules_catalog
    >>>
    >>> db = DatabaseService("project.db")
    >>> migrate_rules_catalog(db, project_id=1, preset="standard")
    >>> # Rules catalog now in projects.metadata
"""

import json
from pathlib import Path
from typing import Literal, Optional
import yaml

from ..database.service import DatabaseService
from ..database.models import Project

PresetName = Literal["minimal", "standard", "professional", "enterprise"]


def migrate_rules_catalog(
    db: DatabaseService,
    project_id: int,
    preset: PresetName = "standard",
    overwrite: bool = False
) -> dict:
    """
    Migrate rules_catalog.yaml to projects.metadata JSON field.

    Args:
        db: DatabaseService instance
        project_id: Project to migrate
        preset: Active preset name (minimal/standard/professional/enterprise)
        overwrite: If True, replace existing metadata

    Returns:
        Updated metadata dictionary

    Raises:
        FileNotFoundError: If rules_catalog.yaml not found
        ValueError: If project not found or preset invalid

    Example:
        >>> db = DatabaseService("project.db")
        >>> metadata = migrate_rules_catalog(db, project_id=1, preset="standard")
        >>> print(f"Migrated {len(metadata['rules_catalog']['presets'])} presets")
        Migrated 4 presets
    """
    # Load YAML catalog
    catalog_path = Path(__file__).parent / "config" / "rules_catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Rules catalog not found: {catalog_path}")

    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)

    # Validate preset
    if preset not in catalog['presets']:
        valid = list(catalog['presets'].keys())
        raise ValueError(f"Invalid preset '{preset}'. Valid: {valid}")

    # Get project
    project = db.projects.get(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Parse existing metadata
    metadata = {}
    if project.metadata:
        try:
            metadata = json.loads(project.metadata)
        except json.JSONDecodeError:
            # Invalid JSON, start fresh
            metadata = {}

    # Check if already migrated
    if 'rules_catalog' in metadata and not overwrite:
        return metadata

    # Build catalog metadata (store presets only, not all 245 rules)
    # Rules are loaded from catalog on demand via DefaultRulesLoader
    metadata['rules_catalog'] = {
        'version': catalog['version'],
        'last_updated': catalog['last_updated'],
        'total_rules': catalog['total_rules'],
        'presets': catalog['presets'],  # Preset metadata only
        'active_preset': preset,
        'custom_rules': [],  # Future: user-defined rules
        'catalog_path': str(catalog_path),  # Reference for loader
    }

    # Update project
    project.metadata = json.dumps(metadata, indent=2)
    updated_project = db.projects.update(project)

    return json.loads(updated_project.metadata)


def get_rules_catalog_metadata(db: DatabaseService, project_id: int) -> Optional[dict]:
    """
    Get rules catalog metadata from projects.metadata.

    Args:
        db: DatabaseService instance
        project_id: Project ID

    Returns:
        Rules catalog metadata dict or None if not found

    Example:
        >>> catalog = get_rules_catalog_metadata(db, project_id=1)
        >>> if catalog:
        ...     print(f"Active preset: {catalog['active_preset']}")
        ...     print(f"Presets available: {list(catalog['presets'].keys())}")
        Active preset: standard
        Presets available: ['minimal', 'standard', 'professional', 'enterprise']
    """
    project = db.projects.get(project_id)
    if not project or not project.metadata:
        return None

    try:
        metadata = json.loads(project.metadata)
        return metadata.get('rules_catalog')
    except json.JSONDecodeError:
        return None


def update_active_preset(
    db: DatabaseService,
    project_id: int,
    preset: PresetName
) -> dict:
    """
    Update active preset in projects.metadata.

    Args:
        db: DatabaseService instance
        project_id: Project ID
        preset: New preset name

    Returns:
        Updated metadata dictionary

    Raises:
        ValueError: If project not found or metadata missing

    Example:
        >>> metadata = update_active_preset(db, project_id=1, preset="professional")
        >>> print(f"Active preset: {metadata['rules_catalog']['active_preset']}")
        Active preset: professional
    """
    project = db.projects.get(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    if not project.metadata:
        raise ValueError(f"Project {project_id} has no metadata (run migrate_rules_catalog first)")

    metadata = json.loads(project.metadata)
    if 'rules_catalog' not in metadata:
        raise ValueError(f"Project {project_id} has no rules_catalog metadata")

    # Validate preset exists
    if preset not in metadata['rules_catalog']['presets']:
        valid = list(metadata['rules_catalog']['presets'].keys())
        raise ValueError(f"Invalid preset '{preset}'. Valid: {valid}")

    # Update preset
    metadata['rules_catalog']['active_preset'] = preset

    # Save
    project.metadata = json.dumps(metadata, indent=2)
    updated_project = db.projects.update(project)

    return json.loads(updated_project.metadata)


def is_migrated(db: DatabaseService, project_id: int) -> bool:
    """
    Check if rules catalog has been migrated to database metadata.

    Args:
        db: DatabaseService instance
        project_id: Project ID

    Returns:
        True if migrated, False otherwise

    Example:
        >>> if not is_migrated(db, project_id=1):
        ...     migrate_rules_catalog(db, project_id=1)
    """
    catalog = get_rules_catalog_metadata(db, project_id)
    return catalog is not None


def migrate_all_projects(db: DatabaseService, preset: PresetName = "standard") -> dict:
    """
    Migrate all projects in database to use rules catalog metadata.

    Args:
        db: DatabaseService instance
        preset: Default preset for projects without metadata

    Returns:
        Dictionary with migration results:
            - total_projects: Total projects found
            - migrated: Number of projects migrated
            - skipped: Number already migrated
            - errors: List of (project_id, error_message) tuples

    Example:
        >>> results = migrate_all_projects(db, preset="standard")
        >>> print(f"Migrated {results['migrated']}/{results['total_projects']} projects")
        Migrated 3/5 projects
    """
    results = {
        'total_projects': 0,
        'migrated': 0,
        'skipped': 0,
        'errors': []
    }

    # Get all projects
    projects = db.projects.list_all()
    results['total_projects'] = len(projects)

    for project in projects:
        try:
            if is_migrated(db, project.id):
                results['skipped'] += 1
                continue

            migrate_rules_catalog(db, project.id, preset=preset)
            results['migrated'] += 1

        except Exception as e:
            results['errors'].append((project.id, str(e)))

    return results
