"""
AIPM Hooks System - Core AIPM Functionality

Claude Code integration hooks for seamless session continuity,
context injection, and workflow guidance.

Hook Phases:
- Phase 1 (MVP): session-start, session-end, user-prompt-submit
- Phase 2 (Enhancement): pre-tool-use, post-tool-use, pre-compact
- Phase 3 (Future): stop, subagent-stop

See README.md for complete documentation.
"""

__version__ = "1.1.0"  # Added database persistence (WI-35 Task #171)

# Hook metadata for installation
HOOKS_METADATA = {
    # Phase 1: Essential Hooks (MVP)
    "session-start": {
        "file": "session-start.py",
        "phase": 1,
        "priority": "HIGH",
        "performance_ms": 180,
        "description": "Load AIPM context on session start"
    },
    "session-end": {
        "file": "session-end.py",
        "phase": 1,
        "priority": "HIGH",
        "performance_ms": 220,
        "description": "Generate session handover (NEXT-SESSION.md)"
    },
    "user-prompt-submit": {
        "file": "user-prompt-submit.py",
        "phase": 1,
        "priority": "HIGH",
        "performance_ms": 60,
        "description": "Inject context on entity mentions"
    },

    # Phase 2: Enhancement Hooks
    "pre-tool-use": {
        "file": "pre-tool-use.py",
        "phase": 2,
        "priority": "MEDIUM",
        "performance_ms": 30,
        "description": "Proactive guidance + security boundaries (GR-007)"
    },
    "post-tool-use": {
        "file": "post-tool-use.py",
        "phase": 2,
        "priority": "MEDIUM",
        "performance_ms": 25,
        "description": "Reactive feedback after tool execution"
    },
    "pre-compact": {
        "file": "pre-compact.py",
        "phase": 2,
        "priority": "MEDIUM",
        "performance_ms": 40,
        "description": "Context preservation priorities"
    },

    # Phase 3: Future Hooks
    "stop": {
        "file": "stop.py",
        "phase": 3,
        "priority": "LOW",
        "performance_ms": 10,
        "description": "Session interruption handling"
    },
    "subagent-stop": {
        "file": "subagent-stop.py",
        "phase": 3,
        "priority": "LOW",
        "performance_ms": 15,
        "description": "Sub-agent completion tracking"
    }
}

# Phase groupings for easy access
PHASE_1_HOOKS = [name for name, meta in HOOKS_METADATA.items() if meta["phase"] == 1]
PHASE_2_HOOKS = [name for name, meta in HOOKS_METADATA.items() if meta["phase"] == 2]
PHASE_3_HOOKS = [name for name, meta in HOOKS_METADATA.items() if meta["phase"] == 3]
ALL_HOOKS = list(HOOKS_METADATA.keys())

__all__ = [
    "HOOKS_METADATA",
    "PHASE_1_HOOKS",
    "PHASE_2_HOOKS", 
    "PHASE_3_HOOKS",
    "ALL_HOOKS"
]