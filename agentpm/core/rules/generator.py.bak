"""Rule generation service.

Orchestrates preset selection and rule loading from YAML catalog.
Main entry point for rules during `apm init`.

Flow:
    QuestionnaireAnswers → PresetSelector → DefaultRulesLoader → Rules in DB
"""

from typing import Dict, Any, List

from ..database.service import DatabaseService
from ..database.models.rule import Rule
from .preset_selector import PresetSelector, PresetName
from .loader import DefaultRulesLoader


class RuleGenerationService:
    """Generate and load governance rules for a project.
    
    Orchestrates:
        1. Preset selection (based on questionnaire or explicit choice)
        2. Rule loading from YAML catalog
        3. Database persistence
    
    Example:
        >>> db = DatabaseService("project.db")
        >>> generator = RuleGenerationService(db)
        >>>
        >>> # From questionnaire answers
        >>> answers = {
        ...     "team_size": "small",
        ...     "development_stage": "mvp",
        ...     "preset_choice": None  # Auto-select
        ... }
        >>> rules = generator.generate(answers, project_id=1)
        >>> len(rules)
        71  # Standard preset
        >>>
        >>> # Explicit preset choice
        >>> answers["preset_choice"] = "minimal"
        >>> rules = generator.generate(answers, project_id=1, overwrite=True)
        >>> len(rules)
        15  # Minimal preset
    """
    
    def __init__(self, db: DatabaseService):
        """Initialize generator with database service.
        
        Args:
            db: DatabaseService instance
        """
        self.db = db
        self.selector = PresetSelector()
        self.loader = DefaultRulesLoader(db)
    
    def generate(
        self,
        answers: Dict[str, Any],
        project_id: int,
        overwrite: bool = False
    ) -> List[Rule]:
        """Generate rules from questionnaire answers.
        
        Args:
            answers: Questionnaire responses
            project_id: Target project
            overwrite: Clear existing rules first
            
        Returns:
            List of created Rule models
        """
        # 1. Select preset (intelligent or explicit)
        preset = self.selector.select(answers)
        
        # 2. Load rules from catalog
        rules = self.loader.load_from_catalog(
            project_id=project_id,
            preset=preset,
            overwrite=overwrite
        )
        
        return rules
    
    def generate_with_preset(
        self,
        project_id: int,
        preset: PresetName,
        overwrite: bool = False
    ) -> List[Rule]:
        """Generate rules with explicit preset (bypass selection).
        
        Args:
            project_id: Target project
            preset: Explicit preset choice
            overwrite: Clear existing rules first
            
        Returns:
            List of created Rule models
        """
        return self.loader.load_from_catalog(
            project_id=project_id,
            preset=preset,
            overwrite=overwrite
        )
    
    def get_recommendation(
        self,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get preset recommendation with explanation.
        
        Args:
            answers: Questionnaire responses
            
        Returns:
            Dictionary with:
                - preset: Recommended preset name
                - reason: Explanation of recommendation
                - rule_count: Number of rules in preset
                - alternatives: Other available presets
        """
        preset = self.selector.select(answers)
        reason = self.selector.get_recommendation_reason(answers)
        preset_info = self.loader.get_preset_info(preset)
        all_presets = self.loader.get_all_presets()
        
        return {
            "preset": preset,
            "reason": reason,
            "rule_count": preset_info["rule_count"],
            "description": preset_info["description"],
            "alternatives": {
                name: info["rule_count"]
                for name, info in all_presets.items()
                if name != preset
            }
        }
