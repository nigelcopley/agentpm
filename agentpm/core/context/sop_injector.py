"""
Agent SOP Injector - Load Agent Standard Operating Procedures

Loads agent SOPs from filesystem (.claude/agents/{role}.md).
Integrates with WI-32 agent tracking for custom SOP paths.
Provides file-based caching with modification time tracking.

Pattern: Filesystem read with caching and graceful degradation
"""

from pathlib import Path
from typing import Optional, Dict, Tuple

from .models import AgentValidationError


class AgentSOPInjector:
    """
    Load agent Standard Operating Procedures (SOPs) from filesystem.

    SOP files contain agent-specific instructions, patterns, and workflows.
    Located in `.claude/agents/{role}.md` by default, with optional custom
    paths stored in database (WI-32).

    Example usage:
        injector = AgentSOPInjector(project_path)
        sop = injector.load_sop(project_id=1, agent_role='python-developer')
        # Returns SOP content as string or None if not found
    """

    def __init__(self, project_path: Path):
        """
        Initialize SOP injector.

        Args:
            project_path: Project root directory (Path object)
        """
        self.project_path = project_path
        self.sop_cache: Dict[str, Tuple[str, float]] = {}  # {role: (content, mtime)}

    def load_sop(
        self,
        project_id: int,
        agent_role: str,
        db=None
    ) -> Optional[str]:
        """
        Load agent SOP from filesystem.

        Strategy:
        1. Validate agent exists and is active (if db provided)
        2. Check database for custom SOP path (if db provided)
        3. Fallback to default location (`.claude/agents/{role}.md`)
        4. Check cache before file read (modification time validation)
        5. Return None if SOP not found (graceful degradation)

        Args:
            project_id: Project ID (for database lookup)
            agent_role: Agent role name (e.g., 'python-developer', 'specifier')
            db: Optional DatabaseService (for agent validation and custom paths)

        Returns:
            SOP content as string, or None if not found

        Raises:
            AgentValidationError: If agent assignment is invalid (not found or inactive)

        Performance: <20ms (filesystem read + cache check)

        Example:
            >>> injector.load_sop(project_id=1, agent_role='python-developer')
            '# Python Developer SOP\\n\\n## Role\\n...'
        """
        # Validate agent exists and is active (WI-32)
        if db:
            try:
                from ..database.methods import agents

                agent = agents.get_agent_by_role(db, project_id, agent_role)
                if not agent:
                    # Agent not found - this is OK for MVP (agents module not complete)
                    # Fall through to default SOP location
                    pass
                elif not agent.is_active:
                    raise AgentValidationError(
                        f"Agent role '{agent_role}' is inactive"
                    )
                else:
                    # Try custom SOP path from database
                    # ✅ FIX (Task #216): Use agent.file_path (schema field name)
                    if agent.file_path:
                        custom_sop_path = self.project_path / agent.file_path
                        if custom_sop_path.exists():
                            return self._read_sop_with_cache(custom_sop_path, agent_role)

            except (ImportError, AttributeError):
                # agents module not available or incomplete (WI-32 not fully implemented yet)
                # Fall through to default location
                pass
            except AgentValidationError:
                # Re-raise validation errors (critical)
                raise

        # Fallback to default location
        default_sop = self.project_path / '.claude' / 'agents' / f'{agent_role}.md'
        if default_sop.exists():
            return self._read_sop_with_cache(default_sop, agent_role)

        # SOP not found - return None (graceful degradation)
        return None

    def _read_sop_with_cache(self, sop_path: Path, agent_role: str) -> str:
        """
        Read SOP file with caching.

        Cache invalidation: Check file modification time (mtime).
        If mtime changed, re-read file and update cache.

        Args:
            sop_path: Path to SOP file
            agent_role: Agent role (cache key)

        Returns:
            SOP content as string

        Performance: <5ms (cache hit), <20ms (cache miss with file read)
        """
        # Check cache
        if agent_role in self.sop_cache:
            cached_content, cached_mtime = self.sop_cache[agent_role]
            current_mtime = sop_path.stat().st_mtime

            if cached_mtime == current_mtime:
                # Cache hit - mtime unchanged
                return cached_content

        # Cache miss or invalidated - read file
        content = sop_path.read_text(encoding='utf-8')

        # Store in cache with mtime
        self.sop_cache[agent_role] = (content, sop_path.stat().st_mtime)

        return content

    def clear_cache(self, agent_role: Optional[str] = None) -> None:
        """
        Clear SOP cache.

        Args:
            agent_role: Clear specific role (None = clear all)

        Example:
            >>> injector.clear_cache('python-developer')  # Clear one
            >>> injector.clear_cache()  # Clear all
        """
        if agent_role:
            self.sop_cache.pop(agent_role, None)
        else:
            self.sop_cache.clear()
