"""
Agent Assignment Validator - Validates agent assignments before task transitions.

Validates:
1. Agent assigned to task
2. Agent exists in database
3. Agent is active (is_active=True)
4. [Future] Agent capabilities match task requirements

Pattern: Validator with smart error messaging and typo detection
"""

from typing import Optional, List
from dataclasses import dataclass, field

from ...database.service import DatabaseService
from ...database.models import Task
from ...database.enums import TaskStatus


@dataclass
class AgentValidationResult:
    """Result of agent assignment validation with smart error messaging."""

    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    fix_command: Optional[str] = None


class AgentAssignmentValidator:
    """
    Validates agent assignments before task state transitions.

    Integrates with WI-32 agent_methods.validate_agent_exists() for database validation.
    Provides smart error messages with typo detection and fix suggestions.
    """

    @staticmethod
    def validate_agent_assignment(
        db: DatabaseService,
        task: Task,
        new_status: TaskStatus
    ) -> AgentValidationResult:
        """
        Validate agent assignment before task transition.

        Called when task transitions to ACTIVE. Validates:
        1. Task has assigned_to field
        2. Agent exists in database
        3. Agent is active (is_active=True)

        Args:
            db: DatabaseService instance
            task: Task being transitioned
            new_status: Target status (validates when → ACTIVE)

        Returns:
            AgentValidationResult with validation status and error details

        Example:
            >>> validation = AgentAssignmentValidator.validate_agent_assignment(
            ...     db, task, TaskStatus.ACTIVE
            ... )
            >>> if not validation.valid:
            ...     print(validation.error_message)
            ...     print(validation.fix_command)
        """
        # Only validate when starting work
        if new_status != TaskStatus.ACTIVE:
            return AgentValidationResult(valid=True)

        # Skip validation if already running (resume case)
        if task.status == TaskStatus.ACTIVE:
            return AgentValidationResult(valid=True)

        # Check if agent assigned
        if not task.assigned_to:
            return AgentValidationResult(
                valid=False,
                error_code="E001",
                error_message="Cannot start task: No agent assigned",
                fix_command=f"apm task accept {task.id} --agent <role>"
            )

        # Validate agent exists and active (using WI-32)
        from ...database.methods import work_items, agents as agent_methods

        work_item = work_items.get_work_item(db, task.work_item_id)
        if not work_item:
            # Data integrity issue - shouldn't happen but handle gracefully
            return AgentValidationResult(
                valid=False,
                error_code="E000",
                error_message=f"Data integrity error: Work item {task.work_item_id} not found"
            )

        # Only validate agent existence if assigned_to is not None
        if task.assigned_to is not None:
            valid, error = agent_methods.validate_agent_exists(
                db,
                work_item.project_id,
                task.assigned_to
            )
        else:
            # This should not happen due to the check above, but handle gracefully
            return AgentValidationResult(
                valid=False,
                error_code="E001",
                error_message="Cannot start task: No agent assigned",
                fix_command=f"apm task accept {task.id} --agent <role>"
            )

        if not valid:
            # Agent validation failed - provide smart error with suggestions
            return AgentAssignmentValidator._build_smart_error(
                db,
                work_item.project_id,
                task.assigned_to,
                task.id,
                error
            )

        # [Future WI-34] Validate agent capabilities match task type
        # agent = agent_methods.get_agent_by_role(db, work_item.project_id, task.assigned_to)
        # if not AgentAssignmentValidator._capabilities_match(agent, task):
        #     return AgentValidationResult(
        #         valid=False,
        #         error_code="E005",
        #         error_message="Agent lacks required capabilities for task type"
        #     )

        return AgentValidationResult(valid=True)

    @staticmethod
    def _build_smart_error(
        db: DatabaseService,
        project_id: int,
        attempted_role: str,
        task_id: int,
        original_error: str
    ) -> AgentValidationResult:
        """
        Build smart error message with typo detection and suggestions.

        Args:
            db: DatabaseService instance
            project_id: Project ID
            attempted_role: Role that failed validation
            task_id: Task ID for fix command
            original_error: Error from agent_methods.validate_agent_exists()

        Returns:
            AgentValidationResult with error details and suggestions
        """
        # Get similar agent names for typo suggestions
        suggestions = AgentAssignmentValidator._get_similar_agents(
            db, project_id, attempted_role
        )

        # Determine error code
        if "not found" in original_error:
            error_code = "E003" if suggestions else "E002"
        else:  # "inactive"
            error_code = "E004"

        return AgentValidationResult(
            valid=False,
            error_code=error_code,
            error_message=f"Cannot start task: {original_error}",
            suggestions=suggestions,
            fix_command=f"apm task accept {task_id} --agent <role>"
        )

    @staticmethod
    def _get_similar_agents(
        db: DatabaseService,
        project_id: int,
        attempted_role: str,
        threshold: int = 3
    ) -> List[str]:
        """
        Get similar agent names using fuzzy matching (Levenshtein distance ≤3).

        Args:
            db: DatabaseService instance
            project_id: Project ID
            attempted_role: Mistyped agent role
            threshold: Max edit distance (default 3)

        Returns:
            List of similar agent roles sorted by similarity (max 3 suggestions)

        Example:
            >>> AgentAssignmentValidator._get_similar_agents(db, 1, "pytho-dev", 3)
            ["python-dev", "python-tester"]
        """
        from ...database.methods import agents as agent_methods

        # Get all active agent roles
        all_agents = agent_methods.list_agents(db, project_id, active_only=True)

        # Fuzzy match using Levenshtein distance
        suggestions = []
        for agent in all_agents:
            distance = AgentAssignmentValidator._levenshtein_distance(
                attempted_role.lower(),
                agent.role.lower()
            )
            if distance <= threshold:
                suggestions.append((agent.role, distance))

        # Sort by distance (closest first) and return top 3
        suggestions.sort(key=lambda x: x[1])
        return [role for role, _ in suggestions[:3]]

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.

        Uses dynamic programming for efficient calculation.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance (number of insertions, deletions, substitutions)

        Example:
            >>> AgentAssignmentValidator._levenshtein_distance("kitten", "sitting")
            3
        """
        # Ensure s1 is the shorter string
        if len(s1) < len(s2):
            return AgentAssignmentValidator._levenshtein_distance(s2, s1)

        # Empty string case
        if len(s2) == 0:
            return len(s1)

        # Dynamic programming approach
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
