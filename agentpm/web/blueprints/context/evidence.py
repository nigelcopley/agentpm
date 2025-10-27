"""
Context Evidence Module for APM (Agent Project Manager) Web Application

Handles evidence-related context functionality including:
- Evidence listing and management
- Evidence validation and scoring
"""

from flask import render_template
import logging

from . import context_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@context_bp.route('/evidence')
def context_evidence():
    """Evidence context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get evidence contexts
    evidence_contexts = contexts.list_contexts(db, project_id=project_id) or []
    evidence_contexts = [ctx for ctx in evidence_contexts if ctx.context_type and 'evidence' in ctx.context_type.value.lower()]
    
    # Calculate evidence metrics
    evidence_metrics = {
        'total_evidence': len(evidence_contexts),
        'high_confidence_evidence': len([ctx for ctx in evidence_contexts if ctx.confidence_score and ctx.confidence_score >= 0.8]),
        'medium_confidence_evidence': len([ctx for ctx in evidence_contexts if ctx.confidence_score and 0.6 <= ctx.confidence_score < 0.8]),
        'low_confidence_evidence': len([ctx for ctx in evidence_contexts if ctx.confidence_score and ctx.confidence_score < 0.6]),
        'unvalidated_evidence': len([ctx for ctx in evidence_contexts if not ctx.confidence_score]),
    }
    
    return render_template('context/evidence.html', 
                         contexts=evidence_contexts,
                         metrics=evidence_metrics)
