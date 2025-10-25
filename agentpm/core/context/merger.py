"""
Context Merger - Hierarchical 6W Merging

Merges UnifiedSixW structures from three levels with override rules:
- Task overrides Work Item overrides Project (most specific wins)
- Lists are REPLACED, not merged
- If field is None/empty at task level, fallback to work item, then project

Pattern: Override-based merging with type-safe fallbacks
"""

from typing import Optional, List, Any, Dict
from copy import deepcopy

from ..database.models.context import UnifiedSixW


class SixWMerger:
    """
    Merge UnifiedSixW structures hierarchically.

    Rules:
    1. Task 6W overrides Work Item 6W overrides Project 6W
    2. Lists are REPLACED (not concatenated)
    3. None/empty at specific level → use parent level
    4. All 14 fields processed with same rules
    """

    @staticmethod
    def merge_hierarchical(
        project_6w: Optional[UnifiedSixW],
        work_item_6w: Optional[UnifiedSixW],
        task_6w: Optional[UnifiedSixW]
    ) -> UnifiedSixW:
        """
        Merge 6W from three levels with override rules.

        Most specific level wins. If field is None/empty at task level,
        fallback to work item, then project.

        Args:
            project_6w: Project-level 6W (broadest scope)
            work_item_6w: Work item-level 6W (medium scope)
            task_6w: Task-level 6W (most specific scope)

        Returns:
            Merged UnifiedSixW with task-level specificity where available

        Examples:
            >>> project_6w = UnifiedSixW(implementers=['@team'])
            >>> work_item_6w = UnifiedSixW(implementers=['@alice', '@bob'])
            >>> task_6w = UnifiedSixW(implementers=['@alice'])
            >>> merged = merge_hierarchical(project_6w, work_item_6w, task_6w)
            >>> merged.implementers
            ['@alice']  # Task wins
        """
        # Start with empty 6W
        merged = UnifiedSixW()

        # Merge WHO dimension (3 list fields)
        merged.end_users = SixWMerger._pick_most_specific_list(
            task_6w.end_users if task_6w else None,
            work_item_6w.end_users if work_item_6w else None,
            project_6w.end_users if project_6w else None
        )

        merged.implementers = SixWMerger._pick_most_specific_list(
            task_6w.implementers if task_6w else None,
            work_item_6w.implementers if work_item_6w else None,
            project_6w.implementers if project_6w else None
        )

        merged.reviewers = SixWMerger._pick_most_specific_list(
            task_6w.reviewers if task_6w else None,
            work_item_6w.reviewers if work_item_6w else None,
            project_6w.reviewers if project_6w else None
        )

        # Merge WHAT dimension (3 list fields)
        merged.functional_requirements = SixWMerger._pick_most_specific_list(
            task_6w.functional_requirements if task_6w else None,
            work_item_6w.functional_requirements if work_item_6w else None,
            project_6w.functional_requirements if project_6w else None
        )

        merged.technical_constraints = SixWMerger._pick_most_specific_list(
            task_6w.technical_constraints if task_6w else None,
            work_item_6w.technical_constraints if work_item_6w else None,
            project_6w.technical_constraints if project_6w else None
        )

        merged.acceptance_criteria = SixWMerger._pick_most_specific_list(
            task_6w.acceptance_criteria if task_6w else None,
            work_item_6w.acceptance_criteria if work_item_6w else None,
            project_6w.acceptance_criteria if project_6w else None
        )

        # Merge WHERE dimension (3 list fields)
        merged.affected_services = SixWMerger._pick_most_specific_list(
            task_6w.affected_services if task_6w else None,
            work_item_6w.affected_services if work_item_6w else None,
            project_6w.affected_services if project_6w else None
        )

        merged.repositories = SixWMerger._pick_most_specific_list(
            task_6w.repositories if task_6w else None,
            work_item_6w.repositories if work_item_6w else None,
            project_6w.repositories if project_6w else None
        )

        merged.deployment_targets = SixWMerger._pick_most_specific_list(
            task_6w.deployment_targets if task_6w else None,
            work_item_6w.deployment_targets if work_item_6w else None,
            project_6w.deployment_targets if project_6w else None
        )

        # Merge WHEN dimension (1 datetime + 1 list)
        merged.deadline = SixWMerger._pick_most_specific_value(
            task_6w.deadline if task_6w else None,
            work_item_6w.deadline if work_item_6w else None,
            project_6w.deadline if project_6w else None
        )

        merged.dependencies_timeline = SixWMerger._pick_most_specific_list(
            task_6w.dependencies_timeline if task_6w else None,
            work_item_6w.dependencies_timeline if work_item_6w else None,
            project_6w.dependencies_timeline if project_6w else None
        )

        # Merge WHY dimension (2 string fields)
        merged.business_value = SixWMerger._pick_most_specific_value(
            task_6w.business_value if task_6w else None,
            work_item_6w.business_value if work_item_6w else None,
            project_6w.business_value if project_6w else None
        )

        merged.risk_if_delayed = SixWMerger._pick_most_specific_value(
            task_6w.risk_if_delayed if task_6w else None,
            work_item_6w.risk_if_delayed if work_item_6w else None,
            project_6w.risk_if_delayed if project_6w else None
        )

        # Merge HOW dimension (1 string + 1 list)
        merged.suggested_approach = SixWMerger._pick_most_specific_value(
            task_6w.suggested_approach if task_6w else None,
            work_item_6w.suggested_approach if work_item_6w else None,
            project_6w.suggested_approach if project_6w else None
        )

        merged.existing_patterns = SixWMerger._pick_most_specific_list(
            task_6w.existing_patterns if task_6w else None,
            work_item_6w.existing_patterns if work_item_6w else None,
            project_6w.existing_patterns if project_6w else None
        )

        return merged

    @staticmethod
    def _pick_most_specific_list(*values: Optional[List[Any]]) -> List[Any]:
        """
        Pick most specific non-empty list.

        Returns first non-None, non-empty list from values.
        Returns empty list if all are None or empty.

        Args:
            *values: List values in priority order (task, work_item, project)

        Returns:
            Most specific list or empty list
        """
        for value in values:
            if value is not None and len(value) > 0:
                return deepcopy(value)  # Return copy to prevent mutations
        return []

    @staticmethod
    def _pick_most_specific_value(*values: Optional[Any]) -> Optional[Any]:
        """
        Pick most specific non-None value.

        Returns first non-None value from values.

        Args:
            *values: Values in priority order (task, work_item, project)

        Returns:
            Most specific value or None
        """
        for value in values:
            if value is not None:
                # For strings, also check not empty
                if isinstance(value, str) and len(value.strip()) == 0:
                    continue
                return value
        return None

    @staticmethod
    def get_merge_metadata(
        project_6w: Optional[UnifiedSixW],
        work_item_6w: Optional[UnifiedSixW],
        task_6w: Optional[UnifiedSixW]
    ) -> Dict[str, Any]:
        """
        Get metadata about merge sources (for debugging/transparency).

        Returns which level provided each field in the merged result.

        Args:
            project_6w: Project-level 6W
            work_item_6w: Work item-level 6W
            task_6w: Task-level 6W

        Returns:
            Dictionary mapping field names to source level
        """
        metadata = {}

        # WHO dimension
        metadata['end_users'] = SixWMerger._get_source(
            'end_users', task_6w, work_item_6w, project_6w
        )
        metadata['implementers'] = SixWMerger._get_source(
            'implementers', task_6w, work_item_6w, project_6w
        )
        metadata['reviewers'] = SixWMerger._get_source(
            'reviewers', task_6w, work_item_6w, project_6w
        )

        # WHAT dimension
        metadata['functional_requirements'] = SixWMerger._get_source(
            'functional_requirements', task_6w, work_item_6w, project_6w
        )
        metadata['technical_constraints'] = SixWMerger._get_source(
            'technical_constraints', task_6w, work_item_6w, project_6w
        )
        metadata['acceptance_criteria'] = SixWMerger._get_source(
            'acceptance_criteria', task_6w, work_item_6w, project_6w
        )

        # Continue for remaining dimensions...
        # (WHERE, WHEN, WHY, HOW)

        return metadata

    @staticmethod
    def _get_source(
        field_name: str,
        task_6w: Optional[UnifiedSixW],
        work_item_6w: Optional[UnifiedSixW],
        project_6w: Optional[UnifiedSixW]
    ) -> str:
        """
        Determine which level provided a field value.

        Returns:
            'task', 'work_item', 'project', or 'none'
        """
        if task_6w and hasattr(task_6w, field_name):
            value = getattr(task_6w, field_name)
            if value is not None and (not isinstance(value, list) or len(value) > 0):
                return 'task'

        if work_item_6w and hasattr(work_item_6w, field_name):
            value = getattr(work_item_6w, field_name)
            if value is not None and (not isinstance(value, list) or len(value) > 0):
                return 'work_item'

        if project_6w and hasattr(project_6w, field_name):
            value = getattr(project_6w, field_name)
            if value is not None and (not isinstance(value, list) or len(value) > 0):
                return 'project'

        return 'none'
