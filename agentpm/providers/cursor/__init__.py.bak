"""
Cursor Provider - IDE Integration for APM (Agent Project Manager)

Installable provider for Cursor IDE that integrates:
- Rules system (6 consolidated rules from WI-118)
- Memories (bi-directional sync with AIPM learnings)
- Custom modes (6 phase-specific modes)
- Guardrails (security and safety configuration)
- Indexing configuration (.cursorignore)
- Hooks (context injection)

Architecture: Database-first, three-layer (Models → Adapters → Methods)
Pattern: ServiceResult for all operations
"""

from agentpm.providers.cursor.provider import CursorProvider
from agentpm.core.database.models.provider import (
    ProviderInstallation,
    CursorConfig,
    CursorMemory,
    CustomMode,
    Guardrails,
    RuleTemplate,
    InstallResult,
    VerifyResult,
    MemorySyncResult,
)

__all__ = [
    "CursorProvider",
    "ProviderInstallation",
    "CursorConfig",
    "CursorMemory",
    "CustomMode",
    "Guardrails",
    "RuleTemplate",
    "InstallResult",
    "VerifyResult",
    "MemorySyncResult",
]

__version__ = "1.0.0"
