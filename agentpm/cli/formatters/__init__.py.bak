"""Rich Output Formatters - Professional CLI output utilities

Provides Rich-based formatting for tables, progress bars, and error messages.
"""

# Table builders
from .tables import (
    build_task_table,
    build_work_item_table,
    build_dependency_table,
    build_blocker_table,
    build_generic_table,
    print_empty_state
)

# Progress indicators
from .progress import (
    init_progress,
    analysis_progress,
    show_operation_status,
    show_next_steps,
    show_multi_step_completion,
    ProgressTracker,
    format_time_estimate
)

# Error formatting
from .errors import (
    show_not_found_error,
    show_validation_error,
    show_workflow_error,
    show_dependency_error,
    show_circular_dependency_error,
    show_missing_option_error,
    show_quality_gate_info,
    format_error_with_code
)

__all__ = [
    # Tables
    'build_task_table',
    'build_work_item_table',
    'build_dependency_table',
    'build_blocker_table',
    'build_generic_table',
    'print_empty_state',
    # Progress
    'init_progress',
    'analysis_progress',
    'show_operation_status',
    'show_next_steps',
    'show_multi_step_completion',
    'ProgressTracker',
    'format_time_estimate',
    # Errors
    'show_not_found_error',
    'show_validation_error',
    'show_workflow_error',
    'show_dependency_error',
    'show_circular_dependency_error',
    'show_missing_option_error',
    'show_quality_gate_info',
    'format_error_with_code',
]
