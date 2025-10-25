"""
Context Confidence Scoring - Quality Assessment

Calculates confidence scores based on context completeness:
- 6W completeness (35% weight)
- Plugin facts quality (25% weight)
- Code amalgamations coverage (25% weight)
- Freshness factor (15% weight)

Returns confidence score (0.0-1.0) with band (RED/YELLOW/GREEN).

Pattern: Weighted scoring with detailed factor breakdown
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass

from ..database.models.context import UnifiedSixW
from ..database.enums import ConfidenceBand


@dataclass
class ConfidenceScore:
    """
    Confidence score with detailed breakdown.

    Attributes:
        total_score: Overall confidence (0.0-1.0)
        band: Confidence band (RED/YELLOW/GREEN)
        six_w_completeness: 6W completeness score (0.0-1.0)
        plugin_facts_quality: Plugin facts quality score (0.0-1.0)
        amalgamations_coverage: Code amalgamations coverage (0.0-1.0)
        freshness_factor: Freshness score (0.0-1.0, penalty for staleness)
        warnings: List of warning messages
    """
    total_score: float
    band: ConfidenceBand
    six_w_completeness: float
    plugin_facts_quality: float
    amalgamations_coverage: float
    freshness_factor: float
    warnings: list[str]


class ConfidenceScorer:
    """
    Calculate context confidence scores.

    Formula:
        confidence = (6w * 0.35) + (facts * 0.25) + (amalg * 0.25) + (fresh * 0.15)

    Bands:
        RED: < 0.5 (insufficient context, agent cannot operate)
        YELLOW: 0.5-0.8 (adequate context, agent can operate with limitations)
        GREEN: > 0.8 (high-quality context, agent fully enabled)
    """

    # Weights for each factor
    WEIGHT_SIX_W = 0.35
    WEIGHT_PLUGIN_FACTS = 0.25
    WEIGHT_AMALGAMATIONS = 0.25
    WEIGHT_FRESHNESS = 0.15

    @staticmethod
    def calculate_confidence(
        six_w: UnifiedSixW,
        plugin_facts: Dict[str, Any],
        amalgamations: Dict[str, str],
        freshness_days: int
    ) -> ConfidenceScore:
        """
        Calculate confidence score with detailed breakdown.

        Args:
            six_w: UnifiedSixW structure (14 fields)
            plugin_facts: Dictionary of plugin facts (by framework/language)
            amalgamations: Dictionary of amalgamation file paths (by type)
            freshness_days: Days since last context update

        Returns:
            ConfidenceScore with total score, band, factors, and warnings

        Examples:
            >>> six_w = UnifiedSixW(...)  # All 14 fields populated
            >>> plugin_facts = {'python': {...}, 'django': {...}}
            >>> amalgamations = {'classes': 'path/to/classes.txt', ...}
            >>> score = calculate_confidence(six_w, plugin_facts, amalgamations, 5)
            >>> score.total_score > 0.8  # GREEN band
            >>> score.band == ConfidenceBand.GREEN
        """
        warnings = []

        # 1. Calculate 6W completeness (35% weight)
        six_w_score = ConfidenceScorer._calculate_6w_completeness(six_w)
        if six_w_score < 0.5:
            warnings.append(f"6W context only {six_w_score*100:.0f}% complete (need >50%)")

        # 2. Calculate plugin facts quality (25% weight)
        facts_score = ConfidenceScorer._calculate_plugin_facts_quality(plugin_facts)
        if facts_score < 0.5:
            warnings.append("Missing plugin facts for detected technologies")

        # 3. Calculate amalgamations coverage (25% weight)
        amalg_score = ConfidenceScorer._calculate_amalgamations_coverage(amalgamations)
        if amalg_score < 0.5:
            warnings.append("Limited code amalgamations available")

        # 4. Calculate freshness factor (15% weight)
        fresh_score = ConfidenceScorer._calculate_freshness_factor(freshness_days)
        if fresh_score < 0.8:
            warnings.append(f"Context is {freshness_days} days old (consider refresh)")

        # Total weighted score
        total_score = (
            (six_w_score * ConfidenceScorer.WEIGHT_SIX_W) +
            (facts_score * ConfidenceScorer.WEIGHT_PLUGIN_FACTS) +
            (amalg_score * ConfidenceScorer.WEIGHT_AMALGAMATIONS) +
            (fresh_score * ConfidenceScorer.WEIGHT_FRESHNESS)
        )

        # Determine band
        band = ConfidenceBand.from_score(total_score)

        return ConfidenceScore(
            total_score=total_score,
            band=band,
            six_w_completeness=six_w_score,
            plugin_facts_quality=facts_score,
            amalgamations_coverage=amalg_score,
            freshness_factor=fresh_score,
            warnings=warnings
        )

    @staticmethod
    def _calculate_6w_completeness(six_w: UnifiedSixW) -> float:
        """
        Calculate 6W completeness score (0.0-1.0).

        Counts non-empty fields out of 14 total fields.

        WHO dimension (3 fields): end_users, implementers, reviewers
        WHAT dimension (3 fields): functional_requirements, technical_constraints, acceptance_criteria
        WHERE dimension (3 fields): affected_services, repositories, deployment_targets
        WHEN dimension (2 fields): deadline, dependencies_timeline
        WHY dimension (2 fields): business_value, risk_if_delayed
        HOW dimension (2 fields): suggested_approach, existing_patterns

        Args:
            six_w: UnifiedSixW structure

        Returns:
            Completeness score (0.0-1.0)
        """
        if six_w is None:
            return 0.0

        total_fields = 15  # 3 WHO + 3 WHAT + 3 WHERE + 2 WHEN + 2 WHY + 2 HOW
        populated_fields = 0

        # WHO dimension (list fields - count if non-empty)
        if six_w.end_users and len(six_w.end_users) > 0:
            populated_fields += 1
        if six_w.implementers and len(six_w.implementers) > 0:
            populated_fields += 1
        if six_w.reviewers and len(six_w.reviewers) > 0:
            populated_fields += 1

        # WHAT dimension (list fields)
        if six_w.functional_requirements and len(six_w.functional_requirements) > 0:
            populated_fields += 1
        if six_w.technical_constraints and len(six_w.technical_constraints) > 0:
            populated_fields += 1
        if six_w.acceptance_criteria and len(six_w.acceptance_criteria) > 0:
            populated_fields += 1

        # WHERE dimension (list fields)
        if six_w.affected_services and len(six_w.affected_services) > 0:
            populated_fields += 1
        if six_w.repositories and len(six_w.repositories) > 0:
            populated_fields += 1
        if six_w.deployment_targets and len(six_w.deployment_targets) > 0:
            populated_fields += 1

        # WHEN dimension (mixed: datetime + list)
        if six_w.deadline is not None:
            populated_fields += 1
        if six_w.dependencies_timeline and len(six_w.dependencies_timeline) > 0:
            populated_fields += 1

        # WHY dimension (string fields)
        if six_w.business_value and len(six_w.business_value) > 0:
            populated_fields += 1
        if six_w.risk_if_delayed and len(six_w.risk_if_delayed) > 0:
            populated_fields += 1

        # HOW dimension (mixed: string + list)
        if six_w.suggested_approach and len(six_w.suggested_approach) > 0:
            populated_fields += 1
        if six_w.existing_patterns and len(six_w.existing_patterns) > 0:
            populated_fields += 1

        return populated_fields / total_fields

    @staticmethod
    def _calculate_plugin_facts_quality(plugin_facts: Dict[str, Any]) -> float:
        """
        Calculate plugin facts quality score (0.0-1.0).

        Measures:
        - How many plugins provided facts?
        - Are facts comprehensive (not just version strings)?
        - Are critical plugins present (language, framework)?

        Args:
            plugin_facts: Dictionary of plugin facts by framework/language

        Returns:
            Facts quality score (0.0-1.0)
        """
        if not plugin_facts or len(plugin_facts) == 0:
            return 0.0

        total_score = 0.0
        max_plugins = 5  # Expect up to 5 plugin types (language + framework + test + infra + ...)

        # Count plugins with facts
        plugins_with_facts = len(plugin_facts.keys())
        total_score += min(plugins_with_facts / max_plugins, 1.0) * 0.5  # Up to 0.5 for count

        # Quality of facts (not just version strings)
        quality_score = 0.0
        for plugin_name, facts in plugin_facts.items():
            if isinstance(facts, dict) and len(facts) > 2:  # More than just name + version
                quality_score += 1

        if plugins_with_facts > 0:
            total_score += (quality_score / plugins_with_facts) * 0.5  # Up to 0.5 for quality

        return min(total_score, 1.0)

    @staticmethod
    def _calculate_amalgamations_coverage(amalgamations: Dict[str, str]) -> float:
        """
        Calculate code amalgamations coverage score (0.0-1.0).

        Measures:
        - How many amalgamation types exist? (classes, functions, models, views, etc.)
        - Are they comprehensive (file size > minimum threshold)?

        Args:
            amalgamations: Dictionary of amalgamation type to file path

        Returns:
            Coverage score (0.0-1.0)
        """
        if not amalgamations or len(amalgamations) == 0:
            return 0.0

        # Expected amalgamation types (varies by tech stack)
        # Minimum: classes, functions (for any language)
        # Django adds: models, views, urls, admin
        # React adds: components, hooks
        expected_types = 4  # Reasonable baseline

        actual_types = len(amalgamations.keys())
        coverage_score = min(actual_types / expected_types, 1.0)

        return coverage_score

    @staticmethod
    def _calculate_freshness_factor(freshness_days: int) -> float:
        """
        Calculate freshness factor score (0.0-1.0).

        Freshness penalties:
        - 0-7 days: 1.0 (perfect)
        - 8-30 days: 0.8 (good)
        - 31-90 days: 0.5 (stale, warning)
        - 90+ days: 0.2 (very stale, critical)

        Args:
            freshness_days: Days since last context update

        Returns:
            Freshness score (0.0-1.0)
        """
        if freshness_days <= 7:
            return 1.0  # Perfect freshness
        elif freshness_days <= 30:
            return 0.8  # Good freshness
        elif freshness_days <= 90:
            return 0.5  # Stale (warning)
        else:
            return 0.2  # Very stale (critical)

    @staticmethod
    def get_confidence_message(score: ConfidenceScore) -> str:
        """
        Get human-readable confidence message.

        Args:
            score: ConfidenceScore object

        Returns:
            Formatted message describing confidence level

        Examples:
            >>> score = ConfidenceScore(total_score=0.85, band=ConfidenceBand.GREEN, ...)
            >>> get_confidence_message(score)
            "GREEN (85%): High-quality context, agent fully enabled"
        """
        percentage = int(score.total_score * 100)

        if score.band == ConfidenceBand.GREEN:
            base_message = f"GREEN ({percentage}%): High-quality context, agent fully enabled"
        elif score.band == ConfidenceBand.YELLOW:
            base_message = f"YELLOW ({percentage}%): Adequate context, agent can operate with limitations"
        else:  # RED
            base_message = f"RED ({percentage}%): Insufficient context, agent cannot operate effectively"

        # Add factor breakdown
        breakdown = (
            f"\n  6W: {score.six_w_completeness*100:.0f}% | "
            f"Facts: {score.plugin_facts_quality*100:.0f}% | "
            f"Amalg: {score.amalgamations_coverage*100:.0f}% | "
            f"Fresh: {score.freshness_factor*100:.0f}%"
        )

        # Add warnings if any
        if score.warnings:
            warnings_text = "\n  Warnings: " + ", ".join(score.warnings)
            return base_message + breakdown + warnings_text

        return base_message + breakdown
