"""Preset selection service.

Intelligently recommends preset based on project characteristics.
Uses questionnaire answers to select minimal/standard/professional/enterprise.

Selection Logic:
    - Team size + Development stage + Compliance needs → Preset
    - Overridable by user (Q19: explicit preset choice)
"""

from typing import Dict, Any, Literal

PresetName = Literal["minimal", "standard", "professional", "enterprise"]


class PresetSelector:
    """Intelligent preset selection based on project characteristics.
    
    Selection Algorithm:
        1. Check for explicit user choice (Q19)
        2. If none, score project on 3 axes:
           - Scale: team_size + expected_complexity
           - Maturity: development_stage + timeline
           - Governance: compliance_needs + security_requirements
        3. Map score → preset
    
    Examples:
        >>> selector = PresetSelector()
        >>> answers = {"team_size": "solo", "development_stage": "prototype"}
        >>> preset = selector.select(answers)
        >>> preset
        'minimal'
        
        >>> answers = {"team_size": "large", "development_stage": "production"}
        >>> preset = selector.select(answers)
        >>> preset
        'professional'
    """
    
    def select(self, answers: Dict[str, Any]) -> PresetName:
        """Select optimal preset based on questionnaire answers.
        
        Args:
            answers: Questionnaire responses
            
        Returns:
            Preset name (minimal/standard/professional/enterprise)
        """
        # 1. Check for explicit choice (Q19)
        if "preset_choice" in answers and answers["preset_choice"]:
            return answers["preset_choice"]
        
        # 2. Calculate composite score (0-100)
        scale_score = self._score_scale(answers)
        maturity_score = self._score_maturity(answers)
        governance_score = self._score_governance(answers)
        
        total_score = (scale_score + maturity_score + governance_score) / 3
        
        # 3. Map score to preset
        return self._score_to_preset(total_score)
    
    def _score_scale(self, answers: Dict) -> float:
        """Score project scale (team + complexity).
        
        Returns:
            0-100 score (0=solo prototype, 100=enterprise system)
        """
        team_size = answers.get("team_size", "solo")
        
        team_scores = {
            "solo": 0,
            "small": 25,      # 2-5 people
            "medium": 50,     # 6-15 people
            "large": 75,      # 16-50 people
            "enterprise": 100  # 50+ people
        }
        
        return team_scores.get(team_size, 0)
    
    def _score_maturity(self, answers: Dict) -> float:
        """Score project maturity (stage + timeline).
        
        Returns:
            0-100 score (0=prototype, 100=production)
        """
        stage = answers.get("development_stage", "prototype")
        
        stage_scores = {
            "prototype": 0,
            "mvp": 33,
            "production": 66,
            "enterprise": 100
        }
        
        return stage_scores.get(stage, 0)
    
    def _score_governance(self, answers: Dict) -> float:
        """Score governance needs (compliance + security).
        
        Returns:
            0-100 score (0=none, 100=regulated industry)
        """
        # Check for compliance indicators in constraints
        constraints = answers.get("constraints", "").lower()
        
        compliance_keywords = [
            "gdpr", "hipaa", "sox", "pci", "compliance",
            "audit", "regulated", "certification"
        ]
        
        # Check if any compliance keywords mentioned
        compliance_mentioned = any(kw in constraints for kw in compliance_keywords)
        
        if compliance_mentioned:
            return 100  # Enterprise preset required
        
        # Check security emphasis
        security_emphasis = answers.get("security_emphasis", "standard")
        
        security_scores = {
            "low": 0,
            "standard": 33,
            "high": 66,
            "critical": 100
        }
        
        return security_scores.get(security_emphasis, 33)
    
    def _score_to_preset(self, score: float) -> PresetName:
        """Map composite score to preset.
        
        Args:
            score: 0-100 composite score
            
        Returns:
            Preset name
        """
        if score < 25:
            return "minimal"
        elif score < 55:
            return "standard"
        elif score < 80:
            return "professional"
        else:
            return "enterprise"
    
    def get_recommendation_reason(
        self,
        answers: Dict[str, Any]
    ) -> str:
        """Explain why a preset was recommended.
        
        Args:
            answers: Questionnaire responses
            
        Returns:
            Human-readable explanation
        """
        preset = self.select(answers)
        
        scale = self._score_scale(answers)
        maturity = self._score_maturity(answers)
        governance = self._score_governance(answers)
        
        return (
            f"Recommended: {preset.upper()}\n"
            f"  Scale: {scale:.0f}/100 (team size: {answers.get('team_size', 'solo')})\n"
            f"  Maturity: {maturity:.0f}/100 (stage: {answers.get('development_stage', 'prototype')})\n"
            f"  Governance: {governance:.0f}/100\n"
            f"  → Composite: {(scale + maturity + governance)/3:.0f}/100"
        )
