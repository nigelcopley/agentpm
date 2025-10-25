"""
Smart Error Message Builder - Context-aware error messages with fix suggestions.

Builds actionable error messages for workflow validation failures with:
- Clear problem statement
- Typo detection and suggestions
- Exact fix commands
- Available options (agents, states, etc.)

Pattern: Static builder methods for different error types
"""

from typing import List

from ...database.service import DatabaseService
from ...database.models import Task
from .agent_assignment import AgentValidationResult


class SmartErrorMessageBuilder:
    """
    Builds context-aware error messages with actionable guidance.

    Provides smart formatting for different validation failure types:
    - Agent assignment errors (with typo detection)
    - State transition errors (with valid next states)
    - Dependency errors (with resolution options)
    """

    @staticmethod
    def build_agent_error(
        validation: AgentValidationResult,
        task: Task,
        db: DatabaseService,
        project_id: int
    ) -> str:
        """
        Build comprehensive error message for agent validation failures.

        Formats error with:
        - Primary error message
        - Typo suggestions (if available)
        - Available agents list (first 5)
        - Fix commands

        Args:
            validation: AgentValidationResult with error details
            task: Task that failed validation
            db: DatabaseService instance
            project_id: Project ID for agent lookup

        Returns:
            Formatted multi-line error message

        Example:
            >>> error = SmartErrorMessageBuilder.build_agent_error(
            ...     validation, task, db, project_id
            ... )
            >>> print(error)
            ❌ Cannot start task: Agent 'pytho-dev' not found

            Did you mean:
              • python-dev
              • python-tester

            Fix: apm task accept 123 --agent python-dev
        """
        from ...database.methods import agents as agent_methods

        # Start with primary error message
        lines = [f"❌ {validation.error_message}"]
        lines.append("")  # Blank line

        # Add typo suggestions if available (error code E003)
        if validation.suggestions:
            lines.append("Did you mean:")
            for suggestion in validation.suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")  # Blank line

        # For agent not found errors, show available agents
        if validation.error_code in ["E002", "E003"]:
            all_agents = agent_methods.list_agents(db, project_id, active_only=True)

            if all_agents:
                lines.append(f"Available agents ({len(all_agents)}):")
                for agent in all_agents[:5]:  # First 5
                    lines.append(f"  • {agent.role} - {agent.display_name}")
                if len(all_agents) > 5:
                    lines.append(f"  ... and {len(all_agents) - 5} more")
                lines.append("")  # Blank line

        # Add fix commands
        if validation.error_code == "E001":
            # No agent assigned
            lines.append("Fix commands:")
            lines.append(f"  apm agents list                     # View all agents")
            lines.append(f"  apm task accept {task.id} --agent <role>  # Assign agent")
        elif validation.error_code == "E004":
            # Agent inactive
            lines.append("This agent has been deprecated or replaced.")
            lines.append("")
            lines.append("Fix commands:")
            lines.append("  apm agents list --active-only       # View active agents")
            lines.append(f"  apm task accept {task.id} --agent <new-role>")
        else:
            # Agent not found (E002, E003)
            lines.append("Fix commands:")
            lines.append("  apm agents list                     # View all agents")
            if validation.suggestions:
                # Provide exact fix with first suggestion
                lines.append(f"  apm task accept {task.id} --agent {validation.suggestions[0]}")
            else:
                lines.append(f"  apm task accept {task.id} --agent <role>")

        return "\n".join(lines)

    @staticmethod
    def build_state_transition_error(
        current_state: str,
        new_state: str,
        reason: str,
        valid_next_states: List[str],
        entity_type: str = "task"
    ) -> str:
        """
        Build error message for invalid state transitions.

        Args:
            current_state: Current state value
            new_state: Attempted new state
            reason: Why transition is invalid
            valid_next_states: List of valid next state values
            entity_type: "task" or "work-item" for commands

        Returns:
            Formatted error message with next steps

        Example:
            >>> error = SmartErrorMessageBuilder.build_state_transition_error(
            ...     "proposed", "completed", "Cannot skip validation stages",
            ...     ["validated"], "task"
            ... )
            >>> print(error)
            ❌ Forbidden transition: proposed → completed
            Reason: Cannot skip validation stages

            Next step: apm task validate <task-id>
        """
        lines = [f"❌ Forbidden transition: {current_state} → {new_state}"]
        lines.append(f"Reason: {reason}")
        lines.append("")

        if valid_next_states:
            # Show immediate next step
            next_state = valid_next_states[0]
            cmd = SmartErrorMessageBuilder._get_command_for_state(entity_type, next_state)
            lines.append(f"Next step: {cmd}")
        else:
            # Show all valid next states
            lines.append(f"Valid next states from '{current_state}':")
            for state in valid_next_states:
                lines.append(f"  • {state}")

        return "\n".join(lines)

    @staticmethod
    def build_dependency_error(
        dependency_type: str,
        incomplete_dependencies: List[str],
        task_id: int
    ) -> str:
        """
        Build error message for dependency violations.

        Args:
            dependency_type: "hard" or "blocker"
            incomplete_dependencies: List of incomplete dependency descriptions
            task_id: Task ID for fix commands

        Returns:
            Formatted error message with resolution options

        Example:
            >>> error = SmartErrorMessageBuilder.build_dependency_error(
            ...     "hard", ["#45 Implement auth schema", "#46 Add migrations"], 47
            ... )
            >>> print(error)
            ❌ Cannot start with incomplete hard dependencies: #45 ..., #46 ...

            Fix options:
              1. Complete dependencies first: apm task complete 45
              2. Remove hard dependencies: apm task remove-dependency 47 --depends-on 45
              3. Change to soft dependency: apm task update-dependency <dep-id> --type soft
        """
        deps_str = ', '.join(incomplete_dependencies[:3])
        more = f" and {len(incomplete_dependencies) - 3} more" if len(incomplete_dependencies) > 3 else ""

        lines = [f"❌ Cannot start with incomplete {dependency_type} dependencies: {deps_str}{more}"]
        lines.append("")

        if dependency_type == "hard":
            lines.append("Fix options:")
            lines.append("  1. Complete dependencies first: apm task complete <dep-id>")
            lines.append(f"  2. Remove hard dependencies: apm task remove-dependency {task_id} --depends-on <dep-id>")
            lines.append("  3. Change to soft dependency: apm task update-dependency <dep-id> --type soft")
        else:  # blocker
            lines.append("Fix:")
            lines.append("  apm task resolve-blocker <blocker-id> --notes \"Resolution details\"")

        return "\n".join(lines)

    @staticmethod
    def _get_command_for_state(entity_type: str, state: str) -> str:
        """
        Get CLI command for transitioning to state.

        Args:
            entity_type: "task" or "work-item"
            state: Target state value

        Returns:
            CLI command string
        """
        # Map common states to CLI commands
        command_map = {
            "validated": f"apm {entity_type} validate <id>",
            "accepted": f"apm {entity_type} accept <id> --agent <role>",
            "in_progress": f"apm {entity_type} start <id>",
            "review": f"apm {entity_type} submit-review <id>",
            "completed": f"apm {entity_type} complete <id>",
            "blocked": f"apm {entity_type} block <id> --reason \"<reason>\"",
            "cancelled": f"apm {entity_type} cancel <id> --reason \"<reason>\"",
        }

        return command_map.get(state.lower(), f"apm {entity_type} transition <id> --status {state}")
