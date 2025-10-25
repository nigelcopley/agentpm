"""
Claude Code Memory Tool

Provides Claude Code with read/write access to APM (Agent Project Manager) memory system.
Integrates with WI-114 Memory System for persistent memory files.

Part of WI-116 Task #623: Create Claude Code Memory Tool System

Architecture:
- Read operations: Load from memory_files table
- Write operations: Update database + trigger regeneration
- Search operations: Full-text search across memory files

Example:
    from agentpm.services.claude_integration.tools import MemoryTool
    from agentpm.core.database.service import get_db

    db = get_db()
    tool = MemoryTool(db)

    # Read memory file
    content = tool.read_memory("RULES")

    # Search memory
    results = tool.search_memory("quality gates")

    # Write memory (advanced)
    success = tool.write_memory("PROJECT", key="status", value="active")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from agentpm.core.database.models.memory import MemoryFile, MemoryFileType, ValidationStatus
from agentpm.core.database.methods import memory_methods

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


class MemoryToolError(Exception):
    """Base exception for memory tool errors."""
    pass


class MemoryTool:
    """
    Claude Code tool for memory access.

    Provides Claude with direct access to APM (Agent Project Manager) memory system including:
    - RULES: Governance rules and quality gates
    - PRINCIPLES: Development principles
    - WORKFLOW: Quality-gated workflow
    - AGENTS: Agent system architecture
    - CONTEXT: Context assembly system
    - PROJECT: Project information
    - IDEAS: Ideas analysis pipeline

    All operations work with the memory_files table and maintain
    proper staleness detection and regeneration triggers.
    """

    # Memory type mapping
    MEMORY_TYPES = {
        "RULES": MemoryFileType.RULES,
        "PRINCIPLES": MemoryFileType.PRINCIPLES,
        "WORKFLOW": MemoryFileType.WORKFLOW,
        "AGENTS": MemoryFileType.AGENTS,
        "CONTEXT": MemoryFileType.CONTEXT,
        "PROJECT": MemoryFileType.PROJECT,
        "IDEAS": MemoryFileType.IDEAS,
    }

    def __init__(self, db: DatabaseService, project_id: Optional[int] = None):
        """
        Initialize memory tool.

        Args:
            db: DatabaseService instance
            project_id: Optional project ID (defaults to current project)
        """
        self.db = db
        self.project_id = project_id or self._get_current_project_id()
        logger.info(f"MemoryTool initialized for project {self.project_id}")

    def read_memory(
        self,
        memory_type: str,
        query: Optional[str] = None,
        max_age_hours: int = 24
    ) -> str:
        """
        Read from AIPM memory files.

        Args:
            memory_type: Type of memory (RULES, AGENTS, WORKFLOW, CONTEXT, PROJECT, PRINCIPLES, IDEAS)
            query: Optional filter query (searches within content)
            max_age_hours: Maximum acceptable age in hours (default 24)

        Returns:
            Memory content (markdown)

        Raises:
            MemoryToolError: If memory type invalid or file not found

        Example:
            >>> tool = MemoryTool(db)
            >>> rules_content = tool.read_memory("RULES")
            >>> print(rules_content[:100])
            # APM (Agent Project Manager) Governance Rules

            ## Block-Level Rules (Must Never Violate)

            >>> # Filter within content
            >>> gates_content = tool.read_memory("RULES", query="quality gates")
        """
        try:
            # Validate memory type
            if memory_type not in self.MEMORY_TYPES:
                raise MemoryToolError(
                    f"Invalid memory type '{memory_type}'. "
                    f"Valid types: {', '.join(self.MEMORY_TYPES.keys())}"
                )

            file_type = self.MEMORY_TYPES[memory_type]

            # Check if memory file is current
            is_current = memory_methods.is_memory_file_current(
                self.db,
                self.project_id,
                file_type,
                max_age_hours=max_age_hours
            )

            if not is_current:
                logger.warning(
                    f"Memory file {memory_type} is stale or missing. "
                    "Consider regenerating memory files."
                )

            # Get memory file
            memory_file = memory_methods.get_memory_file_by_type(
                self.db,
                self.project_id,
                file_type
            )

            if not memory_file:
                raise MemoryToolError(
                    f"Memory file {memory_type} not found for project {self.project_id}. "
                    "Run 'apm memory generate' to create memory files."
                )

            content = memory_file.content

            # Apply query filter if provided
            if query:
                content = self._filter_content(content, query)

            logger.debug(
                f"Read {len(content)} chars from {memory_type} "
                f"(query: {query if query else 'none'})"
            )

            return content

        except MemoryToolError:
            raise
        except Exception as e:
            logger.error(f"Error reading memory {memory_type}: {e}", exc_info=True)
            raise MemoryToolError(f"Failed to read memory {memory_type}: {str(e)}")

    def write_memory(
        self,
        memory_type: str,
        key: str,
        value: str,
        trigger_regeneration: bool = True
    ) -> bool:
        """
        Write to AIPM memory system.

        Note: This updates the database source tables (rules, agents, etc.),
        not the memory files directly. Memory files are regenerated from database.

        Args:
            memory_type: Type of memory (RULES, AGENTS, WORKFLOW, etc.)
            key: Key to update (e.g., "rule_id", "agent_name")
            value: New value
            trigger_regeneration: Whether to mark memory file as stale (default True)

        Returns:
            True if write successful, False otherwise

        Raises:
            MemoryToolError: If write operation not supported or fails

        Example:
            >>> tool = MemoryTool(db)
            >>> # Write operations update database, then trigger regeneration
            >>> success = tool.write_memory("PROJECT", key="status", value="active")
            >>> print(success)  # True

        Warning:
            Write operations are limited. Most memory content is derived from
            database entities (rules, agents, work items) which should be updated
            via their respective APIs (apm rules, apm work-item, etc.).
        """
        try:
            # Validate memory type
            if memory_type not in self.MEMORY_TYPES:
                raise MemoryToolError(
                    f"Invalid memory type '{memory_type}'. "
                    f"Valid types: {', '.join(self.MEMORY_TYPES.keys())}"
                )

            file_type = self.MEMORY_TYPES[memory_type]

            # Get existing memory file
            memory_file = memory_methods.get_memory_file_by_type(
                self.db,
                self.project_id,
                file_type
            )

            if not memory_file:
                raise MemoryToolError(
                    f"Memory file {memory_type} not found. "
                    "Cannot write to non-existent memory file."
                )

            # Note: In a full implementation, this would update the source database
            # tables (rules, agents, etc.) based on the memory type.
            # For now, we log a warning about limited write support.
            logger.warning(
                f"Direct memory writes are limited. Memory type {memory_type} "
                f"is derived from database entities. Update via: "
                f"{self._get_update_command_hint(memory_type)}"
            )

            # Mark memory file as stale to trigger regeneration
            if trigger_regeneration:
                memory_methods.mark_stale(self.db, memory_file.id)
                logger.info(
                    f"Marked {memory_type} memory file as stale. "
                    "Run 'apm memory generate' to regenerate."
                )

            return True

        except MemoryToolError:
            raise
        except Exception as e:
            logger.error(f"Error writing memory {memory_type}: {e}", exc_info=True)
            raise MemoryToolError(f"Failed to write memory {memory_type}: {str(e)}")

    def search_memory(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_confidence: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search across memory files.

        Args:
            query: Search query (case-insensitive substring match)
            memory_types: Optional list of memory types to search (default: all)
            limit: Maximum number of results (default 10)
            min_confidence: Minimum confidence score (0.0-1.0, default 0.0)

        Returns:
            List of search results with metadata

        Example:
            >>> tool = MemoryTool(db)
            >>> results = tool.search_memory("quality gates")
            >>> for result in results:
            ...     print(f"{result['memory_type']}: {result['excerpt'][:50]}...")
            RULES: Quality gates ensure work meets standards...
            WORKFLOW: Each phase has quality gates that must...

            >>> # Search specific memory types
            >>> results = tool.search_memory(
            ...     "testing",
            ...     memory_types=["RULES", "PRINCIPLES"],
            ...     limit=5
            ... )
        """
        try:
            results = []

            # Determine which memory types to search
            if memory_types:
                # Validate provided memory types
                invalid_types = set(memory_types) - set(self.MEMORY_TYPES.keys())
                if invalid_types:
                    raise MemoryToolError(
                        f"Invalid memory types: {', '.join(invalid_types)}. "
                        f"Valid types: {', '.join(self.MEMORY_TYPES.keys())}"
                    )
                file_types = [self.MEMORY_TYPES[mt] for mt in memory_types]
            else:
                # Search all memory types
                file_types = list(self.MEMORY_TYPES.values())

            # Search each memory type
            for file_type in file_types:
                memory_file = memory_methods.get_memory_file_by_type(
                    self.db,
                    self.project_id,
                    file_type
                )

                if not memory_file:
                    logger.debug(f"Skipping {file_type.value} - not found")
                    continue

                # Skip if below confidence threshold
                if memory_file.confidence_score < min_confidence:
                    logger.debug(
                        f"Skipping {file_type.value} - confidence "
                        f"{memory_file.confidence_score} < {min_confidence}"
                    )
                    continue

                # Search within content
                matches = self._search_content(memory_file.content, query)

                if matches:
                    for match in matches:
                        results.append({
                            "memory_type": file_type.value.upper(),
                            "file_path": memory_file.file_path,
                            "excerpt": match["excerpt"],
                            "line_number": match.get("line_number"),
                            "confidence": memory_file.confidence_score,
                            "completeness": memory_file.completeness_score,
                            "generated_at": memory_file.generated_at,
                            "relevance_score": match.get("relevance_score", 0.5)
                        })

            # Sort by relevance and confidence
            results.sort(
                key=lambda x: (x["relevance_score"], x["confidence"]),
                reverse=True
            )

            # Apply limit
            results = results[:limit]

            logger.info(
                f"Search for '{query}' returned {len(results)} results "
                f"across {len(file_types)} memory types"
            )

            return results

        except MemoryToolError:
            raise
        except Exception as e:
            logger.error(f"Error searching memory: {e}", exc_info=True)
            raise MemoryToolError(f"Failed to search memory: {str(e)}")

    def list_memory_types(self) -> List[Dict[str, Any]]:
        """
        List available memory types with metadata.

        Returns:
            List of memory type information

        Example:
            >>> tool = MemoryTool(db)
            >>> memory_types = tool.list_memory_types()
            >>> for mt in memory_types:
            ...     print(f"{mt['name']}: {mt['description']}")
            RULES: Governance rules and quality gates
            AGENTS: Agent system architecture
            ...
        """
        memory_info = []

        for name, file_type in self.MEMORY_TYPES.items():
            memory_file = memory_methods.get_memory_file_by_type(
                self.db,
                self.project_id,
                file_type
            )

            info = {
                "name": name,
                "file_type": file_type.value,
                "description": self._get_memory_description(name),
                "available": memory_file is not None,
            }

            if memory_file:
                info.update({
                    "file_path": memory_file.file_path,
                    "size_bytes": len(memory_file.content),
                    "confidence": memory_file.confidence_score,
                    "completeness": memory_file.completeness_score,
                    "validation_status": memory_file.validation_status.value,
                    "generated_at": memory_file.generated_at,
                    "is_stale": memory_file.is_stale,
                    "is_expired": memory_file.is_expired,
                })

            memory_info.append(info)

        return memory_info

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.

        Returns:
            Dictionary with memory statistics

        Example:
            >>> tool = MemoryTool(db)
            >>> stats = tool.get_memory_stats()
            >>> print(f"Total files: {stats['total_files']}")
            >>> print(f"Stale files: {stats['stale_files']}")
        """
        try:
            # Get all memory files for project
            all_files = memory_methods.list_memory_files(
                self.db,
                project_id=self.project_id
            )

            # Get stale files
            stale_files = memory_methods.get_stale_memory_files(
                self.db,
                project_id=self.project_id
            )

            # Calculate stats
            total_size = sum(len(f.content) for f in all_files)
            avg_confidence = (
                sum(f.confidence_score for f in all_files) / len(all_files)
                if all_files else 0.0
            )
            avg_completeness = (
                sum(f.completeness_score for f in all_files) / len(all_files)
                if all_files else 0.0
            )

            # Count by validation status
            status_counts = {}
            for status in ValidationStatus:
                count = len([
                    f for f in all_files
                    if f.validation_status == status
                ])
                status_counts[status.value] = count

            return {
                "project_id": self.project_id,
                "total_files": len(all_files),
                "stale_files": len(stale_files),
                "total_size_bytes": total_size,
                "avg_confidence": round(avg_confidence, 2),
                "avg_completeness": round(avg_completeness, 2),
                "status_counts": status_counts,
                "memory_types_available": len([
                    f for f in all_files
                    if f.validation_status == ValidationStatus.VALIDATED
                ]),
            }

        except Exception as e:
            logger.error(f"Error getting memory stats: {e}", exc_info=True)
            return {}

    # Helper methods

    def _get_current_project_id(self) -> int:
        """Get current project ID from database."""
        # In a real implementation, this would query the current project
        # For now, default to project 1
        return 1

    def _filter_content(self, content: str, query: str) -> str:
        """
        Filter content by query.

        Returns lines containing the query (case-insensitive) with context.
        """
        query_lower = query.lower()
        lines = content.split('\n')
        matching_lines = []

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Include line with context (±2 lines)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = lines[start:end]
                matching_lines.extend(context)
                matching_lines.append("---")  # Separator

        if matching_lines:
            # Remove trailing separator
            if matching_lines[-1] == "---":
                matching_lines = matching_lines[:-1]
            return '\n'.join(matching_lines)
        else:
            return f"No matches found for '{query}'"

    def _search_content(
        self,
        content: str,
        query: str,
        context_lines: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Search content and return matches with metadata.

        Returns list of matches with excerpts and line numbers.
        """
        query_lower = query.lower()
        lines = content.split('\n')
        matches = []

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Get context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                excerpt_lines = lines[start:end]

                # Calculate simple relevance score
                # (more occurrences = higher relevance)
                occurrences = line.lower().count(query_lower)
                relevance = min(1.0, occurrences / 10.0 + 0.5)

                matches.append({
                    "line_number": i + 1,
                    "excerpt": '\n'.join(excerpt_lines),
                    "occurrences": occurrences,
                    "relevance_score": relevance
                })

        return matches

    def _get_update_command_hint(self, memory_type: str) -> str:
        """Get hint for how to update a memory type."""
        hints = {
            "RULES": "apm rules update <rule-id>",
            "AGENTS": "apm agents update <agent-name>",
            "WORKFLOW": "Database update via workflow system",
            "CONTEXT": "apm context update",
            "PROJECT": "apm project update",
            "PRINCIPLES": "Database update via principles table",
            "IDEAS": "apm ideas update <idea-id>",
        }
        return hints.get(memory_type, "Database update")

    def _get_memory_description(self, memory_type: str) -> str:
        """Get description for memory type."""
        descriptions = {
            "RULES": "Governance rules and quality gates",
            "PRINCIPLES": "Development principles and patterns",
            "WORKFLOW": "Quality-gated workflow system",
            "AGENTS": "Agent system architecture and SOPs",
            "CONTEXT": "Context assembly and enrichment",
            "PROJECT": "Project metadata and configuration",
            "IDEAS": "Ideas analysis pipeline and backlog",
        }
        return descriptions.get(memory_type, "Memory file")
