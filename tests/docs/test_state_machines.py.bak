"""
Verify state machine documentation matches code.

This module ensures that documentation accurately reflects the state machines
defined in enums/status.py. Any drift between code and docs is caught.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest


def extract_enum_states(enum_file: Path, enum_name: str) -> Set[str]:
    """
    Extract state values from an enum definition.

    Args:
        enum_file: Path to status.py
        enum_name: Name of enum class (e.g., 'TaskStatus')

    Returns:
        Set of state values (lowercase)
    """
    content = enum_file.read_text()
    states = set()
    in_enum = False

    for line in content.split('\n'):
        if f"class {enum_name}" in line:
            in_enum = True
            continue

        if in_enum:
            # Stop at next class or end of indentation
            if line.startswith('class ') or (line.strip() and not line[0].isspace()):
                if not line.strip().startswith('@') and not line.strip().startswith('def'):
                    break

            # Extract enum values (e.g., DRAFT = "draft")
            if '=' in line and not line.strip().startswith(('#', '@', 'def', 'return', 'valid')):
                # Only process lines that look like enum assignments (CONSTANT = "value")
                if line.strip().split()[0].isupper():
                    parts = line.split('=')
                    if len(parts) == 2:
                        value = parts[1].strip().strip('"').strip("'")
                        # Only add if it looks like a state value (simple string)
                        if value and not value.startswith('cls.') and value.islower():
                            states.add(value)

    return states


def extract_state_references_from_markdown(markdown_content: str, enum_name: str) -> Set[str]:
    """
    Extract state references from markdown documentation.

    Looks for patterns like:
    - "draft status"
    - "status: draft"
    - "draft → ready"
    - "state = 'draft'"

    Args:
        markdown_content: Raw markdown text
        enum_name: Enum name to scope search

    Returns:
        Set of referenced state values
    """
    # Common state references (extend as needed)
    common_states = {
        'draft', 'ready', 'active', 'review', 'done', 'archived',
        'blocked', 'cancelled', 'initiated', 'on_hold', 'completed'
    }

    references = set()

    # Pattern 1: status = "state" or state: state
    pattern1 = r'(?:status|state)[\s:=]+["\']?(\w+)["\']?'
    for match in re.finditer(pattern1, markdown_content, re.IGNORECASE):
        state = match.group(1).lower()
        if state in common_states:
            references.add(state)

    # Pattern 2: state → state (state transitions)
    pattern2 = r'(\w+)\s*(?:→|->|-->)\s*(\w+)'
    for match in re.finditer(pattern2, markdown_content):
        from_state = match.group(1).lower()
        to_state = match.group(2).lower()
        if from_state in common_states:
            references.add(from_state)
        if to_state in common_states:
            references.add(to_state)

    # Pattern 3: Quoted states in lists or descriptions
    pattern3 = r'["\'](\w+)["\']'
    for match in re.finditer(pattern3, markdown_content):
        state = match.group(1).lower()
        if state in common_states:
            references.add(state)

    return references


def extract_state_transitions(enum_file: Path, enum_name: str) -> List[Tuple[str, str]]:
    """
    Extract state transitions from get_next_state method.

    Args:
        enum_file: Path to status.py
        enum_name: Enum class name

    Returns:
        List of (from_state, to_state) tuples
    """
    content = enum_file.read_text()
    transitions = []
    in_next_state_method = False
    in_mapping = False

    for line in content.split('\n'):
        # Find get_next_state method
        if 'def get_next_state' in line:
            in_next_state_method = True
            continue

        if in_next_state_method:
            # Find the mapping dictionary
            if 'next_mapping = {' in line or 'next_mapping={' in line:
                in_mapping = True
                continue

            # End of method
            if line.strip().startswith('def ') or (not line.strip() and in_mapping):
                break

            if in_mapping:
                # Extract transitions: cls.STATE: cls.NEXT_STATE
                match = re.search(r'cls\.(\w+):\s*cls\.(\w+)', line)
                if match:
                    from_state = match.group(1).lower()
                    to_state = match.group(2).lower()
                    transitions.append((from_state, to_state))

                # End of mapping
                if '}' in line:
                    in_mapping = False

    return transitions


class TestTaskStatusConsistency:
    """Test TaskStatus enum consistency with documentation."""

    def test_task_status_states_match_enum(self, enum_file: Path, markdown_files: List[Path]):
        """
        Test that TaskStatus states in docs match enum definition.

        Args:
            enum_file: Path to status.py
            markdown_files: List of markdown files
        """
        # Extract states from enum
        enum_states = extract_enum_states(enum_file, 'TaskStatus')
        assert len(enum_states) > 0, "Failed to extract TaskStatus states from enum"

        # Check docs for invalid state references
        errors = []
        for md_file in markdown_files:
            content = md_file.read_text()

            # Only check files that mention TaskStatus
            if 'TaskStatus' not in content and 'task status' not in content.lower():
                continue

            doc_states = extract_state_references_from_markdown(content, 'TaskStatus')

            # Find states mentioned in docs but not in enum
            invalid_states = doc_states - enum_states
            if invalid_states:
                errors.append(
                    f"{md_file.relative_to(md_file.parent.parent.parent)}: "
                    f"References invalid TaskStatus states: {invalid_states}"
                )

        if errors:
            pytest.fail(
                "Found TaskStatus documentation drift:\n" +
                "\n".join(errors) +
                f"\n\nValid states: {sorted(enum_states)}"
            )

    def test_task_status_has_all_required_states(self, enum_file: Path):
        """
        Test that TaskStatus has all required workflow states.

        Args:
            enum_file: Path to status.py
        """
        enum_states = extract_enum_states(enum_file, 'TaskStatus')
        required_states = {'draft', 'ready', 'active', 'review', 'done', 'archived'}

        missing_states = required_states - enum_states
        assert not missing_states, f"TaskStatus missing required states: {missing_states}"

    def test_task_status_transitions_are_documented(self, enum_file: Path):
        """
        Test that TaskStatus transitions defined in code are logical.

        Args:
            enum_file: Path to status.py
        """
        transitions = extract_state_transitions(enum_file, 'TaskStatus')

        # Verify key transitions exist
        expected_transitions = [
            ('draft', 'ready'),
            ('ready', 'active'),
            ('active', 'review'),
            ('review', 'done'),
        ]

        for from_state, to_state in expected_transitions:
            assert (from_state, to_state) in transitions, \
                f"Missing expected transition: {from_state} → {to_state}"


class TestWorkItemStatusConsistency:
    """Test WorkItemStatus enum consistency with documentation."""

    def test_work_item_status_states_match_enum(self, enum_file: Path, markdown_files: List[Path]):
        """
        Test that WorkItemStatus states in docs match enum definition.

        Args:
            enum_file: Path to status.py
            markdown_files: List of markdown files
        """
        enum_states = extract_enum_states(enum_file, 'WorkItemStatus')
        assert len(enum_states) > 0, "Failed to extract WorkItemStatus states from enum"

        errors = []
        for md_file in markdown_files:
            content = md_file.read_text()

            # Only check files that mention WorkItemStatus
            if 'WorkItemStatus' not in content and 'work item status' not in content.lower():
                continue

            doc_states = extract_state_references_from_markdown(content, 'WorkItemStatus')

            invalid_states = doc_states - enum_states
            if invalid_states:
                errors.append(
                    f"{md_file.relative_to(md_file.parent.parent.parent)}: "
                    f"References invalid WorkItemStatus states: {invalid_states}"
                )

        if errors:
            pytest.fail(
                "Found WorkItemStatus documentation drift:\n" +
                "\n".join(errors) +
                f"\n\nValid states: {sorted(enum_states)}"
            )

    def test_work_item_status_has_all_required_states(self, enum_file: Path):
        """
        Test that WorkItemStatus has all required workflow states.

        Args:
            enum_file: Path to status.py
        """
        enum_states = extract_enum_states(enum_file, 'WorkItemStatus')
        required_states = {'draft', 'ready', 'active', 'review', 'done', 'archived'}

        missing_states = required_states - enum_states
        assert not missing_states, f"WorkItemStatus missing required states: {missing_states}"


class TestProjectStatusConsistency:
    """Test ProjectStatus enum consistency with documentation."""

    def test_project_status_states_match_enum(self, enum_file: Path, markdown_files: List[Path]):
        """
        Test that ProjectStatus states in docs match enum definition.

        Args:
            enum_file: Path to status.py
            markdown_files: List of markdown files
        """
        enum_states = extract_enum_states(enum_file, 'ProjectStatus')
        assert len(enum_states) > 0, "Failed to extract ProjectStatus states from enum"

        errors = []
        for md_file in markdown_files:
            content = md_file.read_text()

            # Only check files that mention ProjectStatus
            if 'ProjectStatus' not in content and 'project status' not in content.lower():
                continue

            # ProjectStatus uses different state names
            project_states = {'initiated', 'active', 'on_hold', 'completed', 'archived'}
            doc_states = extract_state_references_from_markdown(content, 'ProjectStatus')

            invalid_states = (doc_states & project_states) - enum_states
            if invalid_states:
                errors.append(
                    f"{md_file.relative_to(md_file.parent.parent.parent)}: "
                    f"References invalid ProjectStatus states: {invalid_states}"
                )

        if errors:
            pytest.fail(
                "Found ProjectStatus documentation drift:\n" +
                "\n".join(errors) +
                f"\n\nValid states: {sorted(enum_states)}"
            )

    def test_project_status_has_simple_lifecycle(self, enum_file: Path):
        """
        Test that ProjectStatus maintains simple lifecycle (not full workflow).

        Args:
            enum_file: Path to status.py
        """
        enum_states = extract_enum_states(enum_file, 'ProjectStatus')

        # ProjectStatus should NOT have workflow states like 'draft' or 'review'
        workflow_states = {'draft', 'review'}
        overlap = enum_states & workflow_states

        assert not overlap, \
            f"ProjectStatus should have simple lifecycle, found workflow states: {overlap}"


class TestStateDiagramAccuracy:
    """Test auto-generated state diagrams match code."""

    def test_generated_diagrams_exist(self, project_root: Path):
        """
        Test that state diagrams have been generated.

        Args:
            project_root: Project root directory
        """
        diagram_dir = project_root / "docs" / "reference" / "state-diagrams"

        expected_files = [
            "taskstatus-diagram.md",
            "workitemstatus-diagram.md",
            "projectstatus-diagram.md",
        ]

        for filename in expected_files:
            diagram_file = diagram_dir / filename
            assert diagram_file.exists(), \
                f"Missing generated diagram: {filename}\n" \
                f"Run: python scripts/poc_state_diagrams.py"

    def test_generated_diagrams_match_enums(self, project_root: Path, enum_file: Path):
        """
        Test that generated diagrams accurately reflect enum states.

        Args:
            project_root: Project root directory
            enum_file: Path to status.py
        """
        diagram_dir = project_root / "docs" / "reference" / "state-diagrams"

        test_cases = [
            ("taskstatus-diagram.md", "TaskStatus"),
            ("workitemstatus-diagram.md", "WorkItemStatus"),
            ("projectstatus-diagram.md", "ProjectStatus"),
        ]

        errors = []
        for diagram_file, enum_name in test_cases:
            diagram_path = diagram_dir / diagram_file

            if not diagram_path.exists():
                continue

            # Extract enum states
            enum_states = extract_enum_states(enum_file, enum_name)

            # Extract states from diagram
            diagram_content = diagram_path.read_text()
            diagram_states = extract_state_references_from_markdown(diagram_content, enum_name)

            # Check for missing states in diagram
            missing = enum_states - diagram_states
            if missing:
                errors.append(
                    f"{diagram_file}: Missing states from enum: {missing}"
                )

            # Check for extra states in diagram
            extra = diagram_states - enum_states
            if extra:
                errors.append(
                    f"{diagram_file}: Contains invalid states: {extra}"
                )

        if errors:
            pytest.fail(
                "State diagram drift detected:\n" +
                "\n".join(errors) +
                "\n\nRun: python scripts/poc_state_diagrams.py to regenerate"
            )
