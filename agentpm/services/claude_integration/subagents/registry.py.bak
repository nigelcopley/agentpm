"""
Subagent Registry

Registry of AIPM subagents available for Claude Code invocation.
Provides natural language invocation guide generation.

Pattern: Singleton registry with dynamic agent loading from database
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .models import SubagentSpec, SubagentCapability


logger = logging.getLogger(__name__)


class SubagentRegistry:
    """
    Registry of AIPM subagents for Claude Code.

    Manages subagent registration and provides natural language
    invocation guides for Claude Code to understand available agents.

    Pattern: Singleton registry with lazy loading

    Example:
        registry = get_subagent_registry()

        # Register subagent
        spec = SubagentSpec(
            name="test-implementer",
            description="Creates comprehensive unit tests",
            capabilities=[SubagentCapability.TESTING],
            tier=1,
            invocation_template="Create tests for [component]"
        )
        registry.register_subagent(spec)

        # Get invocation guide
        guide = registry.get_invocation_guide()
        print(guide)  # Markdown guide for Claude Code
    """

    def __init__(self):
        """Initialize empty registry."""
        self._subagents: Dict[str, SubagentSpec] = {}
        self._initialized = False
        logger.info("SubagentRegistry initialized")

    def register_subagent(self, spec: SubagentSpec) -> None:
        """
        Register a subagent.

        Args:
            spec: Subagent specification

        Raises:
            ValueError: If subagent already registered

        Example:
            spec = SubagentSpec(
                name="code-implementer",
                description="Implements production code",
                capabilities=[SubagentCapability.IMPLEMENTATION],
                tier=1,
                invocation_template="Implement [feature]"
            )
            registry.register_subagent(spec)
        """
        if spec.name in self._subagents:
            raise ValueError(f"Subagent '{spec.name}' already registered")

        self._subagents[spec.name] = spec
        logger.info(f"Registered subagent: {spec.name} (tier {spec.tier})")

    def unregister_subagent(self, name: str) -> None:
        """
        Unregister a subagent.

        Args:
            name: Subagent name

        Raises:
            KeyError: If subagent not found
        """
        if name not in self._subagents:
            raise KeyError(f"Subagent '{name}' not found")

        del self._subagents[name]
        logger.info(f"Unregistered subagent: {name}")

    def get_subagent(self, name: str) -> Optional[SubagentSpec]:
        """
        Get subagent by name.

        Args:
            name: Subagent name

        Returns:
            Subagent spec or None if not found
        """
        return self._subagents.get(name)

    def list_subagents(self) -> List[SubagentSpec]:
        """
        List all registered subagents.

        Returns:
            List of subagent specs
        """
        return list(self._subagents.values())

    def get_subagents_by_capability(
        self, capability: SubagentCapability
    ) -> List[SubagentSpec]:
        """
        Get subagents by capability.

        Args:
            capability: Capability to filter by

        Returns:
            List of matching subagent specs

        Example:
            implementers = registry.get_subagents_by_capability(
                SubagentCapability.IMPLEMENTATION
            )
        """
        return [
            spec for spec in self._subagents.values()
            if capability in spec.capabilities
        ]

    def get_subagents_by_tier(self, tier: int) -> List[SubagentSpec]:
        """
        Get subagents by tier.

        Args:
            tier: Tier to filter by (0-3)

        Returns:
            List of matching subagent specs

        Example:
            specialists = registry.get_subagents_by_tier(1)
        """
        return [
            spec for spec in self._subagents.values()
            if spec.tier == tier
        ]

    def get_invocation_guide(self) -> str:
        """
        Generate natural language invocation guide for Claude Code.

        Creates a markdown document describing available subagents
        and how to invoke them using natural language.

        Returns:
            Markdown invocation guide

        Example:
            guide = registry.get_invocation_guide()
            # Returns formatted markdown with subagent descriptions
        """
        if not self._subagents:
            return "No subagents registered."

        # Group by capability
        by_capability: Dict[str, List[SubagentSpec]] = {}
        for spec in self._subagents.values():
            for cap in spec.capabilities:
                # Handle both enum and string values
                cap_str = cap.value if isinstance(cap, SubagentCapability) else cap
                if cap_str not in by_capability:
                    by_capability[cap_str] = []
                by_capability[cap_str].append(spec)

        # Build markdown guide
        lines = [
            "# AIPM Subagents - Natural Language Invocation Guide",
            "",
            "Available AIPM subagents for Claude Code invocation.",
            "Invoke using natural language task descriptions.",
            "",
            "## Subagents by Capability",
            ""
        ]

        for capability, specs in sorted(by_capability.items(), key=lambda x: x[0]):
            lines.append(f"### {capability.upper()}")
            lines.append("")

            for spec in sorted(specs, key=lambda x: x.name):
                lines.append(f"**{spec.name}** (tier {spec.tier})")
                lines.append(f"- Description: {spec.description}")
                lines.append(f"- Invocation: `{spec.invocation_template}`")
                lines.append("")

        # Add usage examples
        lines.extend([
            "## Usage Examples",
            "",
            "### Natural Language Invocation",
            "```",
            "Invoke code-implementer to:",
            "Implement UserService following AIPM patterns with:",
            "- CRUD operations",
            "- Error handling",
            "- Logging",
            "```",
            "",
            "### Programmatic Invocation",
            "```json",
            "{",
            '  "subagent": "test-implementer",',
            '  "action": "invoke",',
            '  "task_description": "Create unit tests for UserService",',
            '  "context": {',
            '    "service": "UserService",',
            '    "coverage_target": 0.9',
            "  }",
            "}",
            "```"
        ])

        return "\n".join(lines)

    def load_from_database(self) -> None:
        """
        Load subagents from AIPM database.

        Queries the agents table and registers all active agents
        as subagents.

        Note: This is a placeholder for future database integration.
        Current implementation uses manual registration.
        """
        # TODO: Implement database loading
        # from agentpm.core.database import get_database
        # db = get_database()
        # agents = db.query_agents(status="active")
        # for agent in agents:
        #     spec = SubagentSpec(
        #         name=agent.role,
        #         description=agent.description,
        #         capabilities=[...],  # Map from agent.type
        #         tier=agent.tier,
        #         invocation_template=agent.invocation_template
        #     )
        #     self.register_subagent(spec)

        logger.debug("Database loading not yet implemented")

    def clear(self) -> None:
        """
        Clear all registered subagents.

        Useful for testing.
        """
        self._subagents.clear()
        self._initialized = False
        logger.info("Cleared all subagents")


# Global registry instance (singleton pattern)
_registry: Optional[SubagentRegistry] = None


def get_subagent_registry() -> SubagentRegistry:
    """
    Get global subagent registry instance.

    Returns:
        Singleton SubagentRegistry instance

    Example:
        from agentpm.services.claude_integration.subagents import get_subagent_registry

        registry = get_subagent_registry()
        guide = registry.get_invocation_guide()
    """
    global _registry
    if _registry is None:
        _registry = SubagentRegistry()
    return _registry


def reset_subagent_registry() -> None:
    """
    Reset global registry to None.

    Useful for testing to ensure clean state.

    Example:
        # In test teardown
        reset_subagent_registry()
    """
    global _registry
    _registry = None
