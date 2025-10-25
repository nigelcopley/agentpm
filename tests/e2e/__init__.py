"""
End-to-End Tests for APM (Agent Project Manager) Memory System

This package contains comprehensive end-to-end tests that validate
the complete memory system workflow from CLI to filesystem.

Test Coverage:
- Generation workflow (CLI → Database → Filesystem)
- Session lifecycle integration (start → work → end)
- Staleness detection and recovery
- Multi-project isolation
- Error handling and recovery
- Performance validation
- Validation workflows

Part of WI-114 Task #606: End-to-End Memory System Testing
"""

__all__ = [
    'test_memory_e2e_generation',
    'test_memory_e2e_session',
    'test_memory_e2e_staleness',
    'test_memory_e2e_multiproject',
    'test_memory_e2e_errors',
    'test_memory_e2e_performance',
    'test_memory_e2e_validation',
]
