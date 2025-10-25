"""
Enhanced Initialization System for Complex Projects - WI-147

This module provides the enhanced initialization system that transforms APM (Agent Project Manager)
from a basic project setup to an enterprise-grade project orchestration platform.

Key Components:
- AdaptiveQuestionnaireEngine: Dynamic question generation based on project context
- AdvancedDetectionEngine: Enhanced technology detection with pattern recognition
- DynamicContextAssembler: Intelligent context assembly and merging
- IntelligentRulesEngine: Context-aware rules generation
- InitializationOrchestrator: Multi-agent coordination for complex projects

Usage:
    from agentpm.core.init import AdaptiveQuestionnaireEngine
    from agentpm.core.detection.models import DetectionResult
    
    # Create adaptive questionnaire
    engine = AdaptiveQuestionnaireEngine(detection_result, complexity_metrics)
    questions = engine.generate_questions()
    answers = engine.run_questionnaire(questions)
"""

from .adaptive_questionnaire import (
    AdaptiveQuestionnaireEngine,
    Question,
    QuestionType,
    ComplexityLevel,
    QuestionSet
)

__all__ = [
    'AdaptiveQuestionnaireEngine',
    'Question',
    'QuestionType', 
    'ComplexityLevel',
    'QuestionSet'
]


