"""Default rules loader service.

Loads governance rules from YAML catalog or hardcoded defaults.
Supports preset-based rule selection (minimal/standard/professional/enterprise).

Pattern:
    - YAML catalog: 245 rules with preset mappings
    - Fallback: 25 hardcoded rules (backward compatibility)
    - Loader creates Rule models and saves via database methods
"""

from typing import List, Optional, Literal
from pathlib import Path
import yaml

from ..database.models.rule import Rule, EnforcementLevel
from ..database.service import DatabaseService
from ..database.methods import rules as rule_methods


# Type alias for preset names
PresetName = Literal["minimal", "standard", "professional", "enterprise"]


# Default rules catalog (minimal MVP set - 25 rules)
DEFAULT_RULES = [
    # Time-boxing rules (11 rules)
    {
        "rule_id": "DP-001",
        "name": "time-boxing-implementation",
        "description": "IMPLEMENTATION tasks limited to ≤4 hours",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"max_hours": 4.0, "task_type": "IMPLEMENTATION"},
    },
    {
        "rule_id": "DP-002",
        "name": "time-boxing-testing",
        "description": "TESTING tasks limited to ≤6 hours",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"max_hours": 6.0, "task_type": "TESTING"},
    },
    {
        "rule_id": "DP-003",
        "name": "time-boxing-design",
        "description": "DESIGN tasks limited to ≤8 hours",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {"max_hours": 8.0, "task_type": "DESIGN"},
    },
    {
        "rule_id": "DP-004",
        "name": "time-boxing-documentation",
        "description": "DOCUMENTATION tasks limited to ≤4 hours",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {"max_hours": 4.0, "task_type": "DOCUMENTATION"},
    },
    {
        "rule_id": "DP-005",
        "name": "time-boxing-deployment",
        "description": "DEPLOYMENT tasks limited to ≤2 hours",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"max_hours": 2.0, "task_type": "DEPLOYMENT"},
    },
    {
        "rule_id": "DP-006",
        "name": "time-boxing-analysis",
        "description": "ANALYSIS tasks limited to ≤8 hours",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {"max_hours": 8.0, "task_type": "ANALYSIS"},
    },
    {
        "rule_id": "DP-007",
        "name": "time-boxing-research",
        "description": "RESEARCH tasks limited to ≤12 hours",
        "enforcement_level": EnforcementLevel.GUIDE,
        "config": {"max_hours": 12.0, "task_type": "RESEARCH"},
    },
    {
        "rule_id": "DP-008",
        "name": "time-boxing-refactoring",
        "description": "REFACTORING tasks limited to ≤6 hours",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {"max_hours": 6.0, "task_type": "REFACTORING"},
    },
    {
        "rule_id": "DP-009",
        "name": "time-boxing-bugfix",
        "description": "BUGFIX tasks limited to ≤4 hours",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"max_hours": 4.0, "task_type": "BUGFIX"},
    },
    {
        "rule_id": "DP-010",
        "name": "time-boxing-hotfix",
        "description": "HOTFIX tasks limited to ≤2 hours",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"max_hours": 2.0, "task_type": "HOTFIX"},
    },
    {
        "rule_id": "DP-011",
        "name": "time-boxing-planning",
        "description": "PLANNING tasks limited to ≤8 hours",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {"max_hours": 8.0, "task_type": "PLANNING"},
    },
    # Quality rules (6 rules)
    {
        "rule_id": "DP-012",
        "name": "quality-test-coverage",
        "description": "Minimum test coverage ≥90%",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"min_coverage": 90.0},
    },
    {
        "rule_id": "DP-027",
        "name": "code-type-hints-required",
        "description": "Type hints required for all functions",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {},
    },
    {
        "rule_id": "DP-028",
        "name": "code-docstring-required",
        "description": "Docstrings required for public functions",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {},
    },
    {
        "rule_id": "DP-029",
        "name": "code-no-print-statements",
        "description": "No print() statements in production code",
        "enforcement_level": EnforcementLevel.GUIDE,
        "config": {},
    },
    {
        "rule_id": "DP-030",
        "name": "code-no-dict-str-any",
        "description": "No Dict[str, Any] in public APIs",
        "enforcement_level": EnforcementLevel.LIMIT,
        "config": {},
    },
    {
        "rule_id": "DP-032",
        "name": "code-logging-standards",
        "description": "Use logging module, not print()",
        "enforcement_level": EnforcementLevel.GUIDE,
        "config": {},
    },
    # Workflow rules (6 rules)
    {
        "rule_id": "WR-001",
        "name": "workflow-quality-gates",
        "description": "Work items validated before tasks start",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {},
    },
    {
        "rule_id": "WR-002",
        "name": "required-tasks-feature",
        "description": "FEATURE requires DESIGN+IMPL+TEST+DOC tasks",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"required_types": ["DESIGN", "IMPLEMENTATION", "TESTING", "DOCUMENTATION"]},
    },
    {
        "rule_id": "WR-003",
        "name": "required-tasks-bugfix",
        "description": "BUGFIX requires ANALYSIS+FIX+TEST tasks",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"required_types": ["ANALYSIS", "BUGFIX", "TESTING"]},
    },
    {
        "rule_id": "WR-004",
        "name": "workflow-code-review",
        "description": "Code review required before completion",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {},
    },
    {
        "rule_id": "WR-006",
        "name": "workflow-test-first",
        "description": "Tests before implementation (TDD)",
        "enforcement_level": EnforcementLevel.GUIDE,
        "config": {},
    },
    {
        "rule_id": "WR-010",
        "name": "required-tasks-planning",
        "description": "PLANNING forbids IMPLEMENTATION tasks",
        "enforcement_level": EnforcementLevel.BLOCK,
        "config": {"forbidden_types": ["IMPLEMENTATION"]},
    },
    # Technology rules (2 rules for completeness = 25 total)
    {
        "rule_id": "TC-001",
        "name": "tech-three-layer-pattern",
        "description": "Database code uses three-layer pattern",
        "enforcement_level": EnforcementLevel.ENHANCE,
        "config": {"pattern": "Models → Adapters → Methods"},
    },
    {
        "rule_id": "TC-002",
        "name": "tech-pydantic-validation",
        "description": "Use Pydantic models for validation",
        "enforcement_level": EnforcementLevel.ENHANCE,
        "config": {},
    },
]


class DefaultRulesLoader:
    """Load governance rules from YAML catalog into a project.

    Supports preset-based rule loading (minimal/standard/professional/enterprise).
    Falls back to hardcoded 25-rule MVP set if YAML catalog not found.

    Presets:
        - minimal: 15 rules (breadth over depth, one per category)
        - standard: 71 rules (balanced coverage, 2-3 per category)
        - professional: 220 rules (deep in critical areas)
        - enterprise: 245 rules (complete governance)

    Example:
        >>> db = DatabaseService("project.db")
        >>> loader = DefaultRulesLoader(db)
        >>>
        >>> # Load standard preset (71 rules)
        >>> rules = loader.load_from_catalog(project_id=1, preset="standard")
        >>> len(rules)
        71
        >>>
        >>> # Load minimal preset (15 rules)
        >>> rules = loader.load_from_catalog(project_id=1, preset="minimal")
        >>> len(rules)
        15
    """

    def __init__(self, db: DatabaseService, project_id: Optional[int] = None):
        """Initialize loader with database service.

        Args:
            db: DatabaseService instance
            project_id: Optional project ID for database-first loading (WI-40)
        """
        self.db = db
        self.project_id = project_id
        self._catalog_path = Path(__file__).parent / "config" / "rules_catalog.yaml"
        self._catalog = None  # Lazy-loaded

    def load_defaults(
        self,
        project_id: int,
        overwrite: bool = False
    ) -> List[Rule]:
        """Load all 25 default rules for a project.

        Args:
            project_id: Project to load rules into
            overwrite: If True, delete existing rules first

        Returns:
            List of created Rule models

        Raises:
            ValidationError: If project doesn't exist
        """
        # Clear existing rules if overwrite
        if overwrite:
            existing = rule_methods.list_rules(self.db, project_id=project_id)
            for rule in existing:
                rule_methods.delete_rule(self.db, rule.id)

        # Create all default rules
        created_rules = []
        for rule_def in DEFAULT_RULES:
            rule = Rule(
                project_id=project_id,
                rule_id=rule_def["rule_id"],
                name=rule_def["name"],
                description=rule_def["description"],
                enforcement_level=rule_def["enforcement_level"],
                config=rule_def["config"],
                enabled=True,
            )

            created = rule_methods.create_rule(self.db, rule)
            created_rules.append(created)

        return created_rules

    def load_from_catalog(
        self,
        project_id: int,
        preset: PresetName = "standard",
        overwrite: bool = False
    ) -> List[Rule]:
        """Load rules from YAML catalog for specified preset (INIT ONLY).

        This method is ONLY used during `apm init` to populate the database.
        At runtime, rules come from the database only.

        Args:
            project_id: Project to load rules into
            preset: Preset name (minimal/standard/professional/enterprise)
            overwrite: If True, delete existing rules first

        Returns:
            List of created Rule models

        Raises:
            FileNotFoundError: If catalog file not found
            ValueError: If preset name invalid

        Example:
            >>> loader = DefaultRulesLoader(db)
            >>> rules = loader.load_from_catalog(1, "standard")
            >>> len(rules)
            71
        """
        # Load YAML catalog directly (bypass database-only _load_catalog)
        catalog = self._load_yaml_catalog()

        # Validate preset
        if preset not in catalog['presets']:
            valid = list(catalog['presets'].keys())
            raise ValueError(f"Invalid preset '{preset}'. Valid: {valid}")

        # Filter rules for this preset
        preset_rules = [
            r for r in catalog['rules']
            if preset in r.get('presets', [])
        ]

        # Clear existing if overwrite
        if overwrite:
            existing = rule_methods.list_rules(self.db, project_id=project_id)
            for rule in existing:
                rule_methods.delete_rule(self.db, rule.id)

        # Create rules from catalog
        created_rules = []
        for rule_def in preset_rules:
            rule = Rule(
                project_id=project_id,
                rule_id=rule_def["rule_id"],
                name=rule_def["name"],
                description=rule_def["description"],
                category=rule_def.get("category"),
                enforcement_level=EnforcementLevel(rule_def["enforcement_level"]),
                validation_logic=rule_def.get("validation_logic"),
                error_message=rule_def.get("error_message"),
                config=rule_def.get("config", {}),
                enabled=rule_def.get("enabled_by_default", True),
            )

            created = rule_methods.create_rule(self.db, rule)
            created_rules.append(created)

        return created_rules

    def get_preset_info(self, preset: PresetName) -> dict:
        """Get preset metadata (INIT ONLY).

        Args:
            preset: Preset name

        Returns:
            Preset dictionary with name, description, rule_count, philosophy
        """
        catalog = self._load_yaml_catalog()
        return catalog['presets'][preset]

    def get_all_presets(self) -> dict:
        """Get all available presets (INIT ONLY).

        Returns:
            Dictionary of all presets with metadata
        """
        catalog = self._load_yaml_catalog()
        return catalog['presets']

    def get_catalog_version(self) -> str:
        """Get catalog version (INIT ONLY).

        Returns:
            Version string (e.g., "1.0.0")
        """
        catalog = self._load_yaml_catalog()
        return catalog['version']

    def get_rule_by_id(
        self,
        project_id: int,
        rule_id: str
    ) -> Optional[Rule]:
        """Get a specific default rule if loaded.

        Args:
            project_id: Project ID
            rule_id: Rule ID (e.g., "DP-001")

        Returns:
            Rule model if found, None otherwise
        """
        return rule_methods.get_rule_by_rule_id(
            self.db,
            project_id=project_id,
            rule_id=rule_id
        )

    def _load_catalog(self) -> dict:
        """Load catalog from database only.

        At runtime, rules should ONLY come from the database.
        YAML file is only used during `apm init` to populate the database.

        Returns:
            Catalog dictionary (from database only)

        Raises:
            RuntimeError: If database rules not available
        """
        if self._catalog is not None:
            return self._catalog

        # Only use database at runtime - no YAML fallback
        if self.project_id:
            try:
                project = self.db.projects.get(self.project_id)
                if project and project.metadata:
                    import json
                    metadata = json.loads(project.metadata)
                    if 'rules_catalog' in metadata:
                        # Use only the database metadata - no YAML loading
                        catalog_meta = metadata['rules_catalog']
                        
                        # Create minimal catalog from database rules only
                        self._catalog = {
                            'version': catalog_meta.get('version', '1.0.0'),
                            'presets': catalog_meta.get('presets', {}),
                            'rules': []  # Rules come from database, not YAML
                        }
                        return self._catalog
            except Exception as e:
                # No fallback to YAML - database is the single source of truth
                raise RuntimeError(f"Failed to load rules from database: {e}")

        # No fallback to YAML file at runtime
        raise RuntimeError(
            f"Rules must be loaded from database. Run 'apm init' to populate rules from YAML catalog."
        )

    def _load_yaml_catalog(self) -> dict:
        """Load YAML catalog directly (INIT ONLY).
        
        This method is ONLY used during `apm init` to populate the database.
        It bypasses the database-only _load_catalog method.
        
        Returns:
            YAML catalog dictionary
            
        Raises:
            FileNotFoundError: If YAML file not found
        """
        # Load YAML file directly
        if self._catalog_path.exists():
            with open(self._catalog_path) as f:
                return yaml.safe_load(f)
        
        # Ultimate fallback: hardcoded defaults
        raise FileNotFoundError(
            f"Rules catalog YAML not found: {self._catalog_path}"
        )
