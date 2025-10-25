"""
Phase Gate Validators

Gate validators enforce phase transition requirements and information capture.
Each phase has specific requirements that must be met before advancement.

Gate Validation Pattern:
    1. Load work item and related data
    2. Check phase-specific requirements
    3. Calculate confidence score
    4. Return GateResult with pass/fail and missing requirements

Available Gate Validators:
    - D1GateValidator: Discovery → Planning gate
    - P1GateValidator: Planning → Implementation gate
    - I1GateValidator: Implementation → Review gate
    - R1GateValidator: Review → Operations gate
    - O1GateValidator: Operations → Evolution gate
    - E1GateValidator: Evolution gate (continuous improvement)

Usage:
    >>> from agentpm.core.workflow.phase_gates import D1GateValidator
    >>> validator = D1GateValidator()
    >>> result = validator.validate(work_item, db)
    >>> if not result.passed:
    >>>     print(f"Missing: {result.missing_requirements}")
"""

from .base_gate_validator import BaseGateValidator, GateResult
from .d1_gate_validator import D1GateValidator
from .p1_gate_validator import P1GateValidator
from .i1_gate_validator import I1GateValidator
from .r1_gate_validator import R1GateValidator
from .o1_gate_validator import O1GateValidator
from .e1_gate_validator import E1GateValidator

__all__ = [
    'BaseGateValidator',
    'GateResult',
    'D1GateValidator',
    'P1GateValidator',
    'I1GateValidator',
    'R1GateValidator',
    'O1GateValidator',
    'E1GateValidator',
]
