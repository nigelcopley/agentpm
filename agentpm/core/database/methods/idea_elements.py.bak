"""
Idea Elements CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for IdeaElement entities using:
- Pydantic models for type safety
- Adapters for model ↔ database conversion
- Validation for business rules

Idea Elements Pattern:
- Components/parts of ideas that can be broken down into tasks
- Support effort estimation and completion tracking
- Ordered within ideas for structured breakdown
- Convert to tasks when ideas become work items

Pattern: Type-safe method signatures with IdeaElement model
"""

from typing import Optional, List
import sqlite3
from datetime import datetime

from ..models import IdeaElement
from ..adapters import IdeaElementAdapter
from ..enums import TaskType


def create_idea_element(service, element: IdeaElement) -> IdeaElement:
    """
    Create a new idea element.

    Type-safe: accepts IdeaElement model, returns IdeaElement model.

    Args:
        service: DatabaseService instance
        element: IdeaElement model to create

    Returns:
        Created IdeaElement with database ID

    Raises:
        ValidationError: If element data is invalid (Pydantic validation)
        TransactionError: If database operation fails

    Example:
        element = IdeaElement(
            idea_id=1,
            title="Implement user authentication",
            description="Add OAuth2 support",
            type=TaskType.IMPLEMENTATION,
            effort_hours=8.0,
            order_index=0
        )
        created = create_idea_element(service, element)
    """
    db_data = IdeaElementAdapter.to_db(element)

    query = """
        INSERT INTO idea_elements (
            idea_id, title, description, type, effort_hours,
            order_index, is_completed, completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['idea_id'],
        db_data['title'],
        db_data['description'],
        db_data['type'],
        db_data['effort_hours'],
        db_data['order_index'],
        db_data['is_completed'],
        db_data['completed_at'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        element_id = cursor.lastrowid

    return get_idea_element(service, element_id)


def get_idea_element(service, element_id: int) -> Optional[IdeaElement]:
    """
    Get idea element by ID.

    Args:
        service: DatabaseService instance
        element_id: Element ID

    Returns:
        IdeaElement model or None if not found
    """
    query = "SELECT * FROM idea_elements WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (element_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return IdeaElementAdapter.from_db(dict(row))


def list_idea_elements(
    service,
    idea_id: int,
    include_completed: bool = True,
    order_by: str = "order_index"
) -> List[IdeaElement]:
    """
    List idea elements for a specific idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID to get elements for
        include_completed: Whether to include completed elements
        order_by: Sort field (order_index, created_at, effort_hours)

    Returns:
        List of IdeaElement models

    Example:
        # All elements for idea 5
        elements = list_idea_elements(service, idea_id=5)

        # Only incomplete elements
        incomplete = list_idea_elements(service, idea_id=5, include_completed=False)
    """
    query = "SELECT * FROM idea_elements WHERE idea_id = ?"
    params = [idea_id]

    if not include_completed:
        query += " AND is_completed = 0"

    # Add ordering
    if order_by == "order_index":
        query += " ORDER BY order_index ASC, created_at ASC"
    elif order_by == "created_at":
        query += " ORDER BY created_at ASC"
    elif order_by == "effort_hours":
        query += " ORDER BY effort_hours DESC, order_index ASC"
    else:
        query += " ORDER BY order_index ASC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

    return [IdeaElementAdapter.from_db(dict(row)) for row in rows]


def update_idea_element(service, element: IdeaElement) -> IdeaElement:
    """
    Update idea element (full model update).

    Type-safe: Pydantic validates before database update.

    Args:
        service: DatabaseService instance
        element: Updated IdeaElement model (must have id)

    Returns:
        Updated IdeaElement model

    Raises:
        ValueError: If element.id is None
        ValidationError: If element data is invalid

    Example:
        element = get_idea_element(service, 5)
        element.title = "Updated title"
        updated = update_idea_element(service, element)
    """
    if not element.id:
        raise ValueError("IdeaElement must have id for update")

    db_data = IdeaElementAdapter.to_db(element)

    query = """
        UPDATE idea_elements SET
            title = ?, description = ?, type = ?, effort_hours = ?,
            order_index = ?, is_completed = ?, completed_at = ?
        WHERE id = ?
    """
    params = (
        db_data['title'],
        db_data['description'],
        db_data['type'],
        db_data['effort_hours'],
        db_data['order_index'],
        db_data['is_completed'],
        db_data['completed_at'],
        element.id,
    )

    with service.transaction() as conn:
        conn.execute(query, params)

    # Return updated element (triggers will have updated updated_at)
    return get_idea_element(service, element.id)


def mark_element_completed(service, element_id: int) -> IdeaElement:
    """
    Mark idea element as completed.

    Args:
        service: DatabaseService instance
        element_id: Element ID

    Returns:
        Updated IdeaElement with completed status

    Raises:
        ValueError: If element not found

    Example:
        element = mark_element_completed(service, 5)
    """
    # Get element
    element = get_idea_element(service, element_id)
    if not element:
        raise ValueError(f"IdeaElement {element_id} not found")

    # Mark as completed
    element.mark_completed()

    return update_idea_element(service, element)


def mark_element_incomplete(service, element_id: int) -> IdeaElement:
    """
    Mark idea element as incomplete.

    Args:
        service: DatabaseService instance
        element_id: Element ID

    Returns:
        Updated IdeaElement with incomplete status

    Raises:
        ValueError: If element not found

    Example:
        element = mark_element_incomplete(service, 5)
    """
    # Get element
    element = get_idea_element(service, element_id)
    if not element:
        raise ValueError(f"IdeaElement {element_id} not found")

    # Mark as incomplete
    element.mark_incomplete()

    return update_idea_element(service, element)


def reorder_elements(service, idea_id: int, element_orders: List[tuple[int, int]]) -> List[IdeaElement]:
    """
    Reorder idea elements within an idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        element_orders: List of (element_id, new_order_index) tuples

    Returns:
        List of updated IdeaElement models

    Example:
        # Reorder elements 1, 2, 3 to positions 2, 0, 1
        updated = reorder_elements(service, idea_id=5, element_orders=[(1, 2), (2, 0), (3, 1)])
    """
    updated_elements = []

    with service.transaction() as conn:
        for element_id, new_order in element_orders:
            conn.execute(
                "UPDATE idea_elements SET order_index = ? WHERE id = ? AND idea_id = ?",
                (new_order, element_id, idea_id)
            )
            
            # Get updated element
            element = get_idea_element(service, element_id)
            if element:
                updated_elements.append(element)

    return updated_elements


def delete_idea_element(service, element_id: int) -> bool:
    """
    Delete idea element by ID.

    Args:
        service: DatabaseService instance
        element_id: Element ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM idea_elements WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (element_id,))
        return cursor.rowcount > 0


def get_idea_completion_stats(service, idea_id: int) -> dict:
    """
    Get completion statistics for an idea's elements.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID

    Returns:
        Dictionary with completion statistics

    Example:
        stats = get_idea_completion_stats(service, idea_id=5)
        # Returns: {
        #     'total_elements': 5,
        #     'completed_elements': 2,
        #     'completion_percentage': 0.4,
        #     'total_effort_hours': 40.0,
        #     'completed_effort_hours': 16.0,
        #     'effort_completion_percentage': 0.4
        # }
    """
    query = """
        SELECT 
            COUNT(*) as total_elements,
            SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_elements,
            SUM(effort_hours) as total_effort_hours,
            SUM(CASE WHEN is_completed = 1 THEN effort_hours ELSE 0 END) as completed_effort_hours
        FROM idea_elements 
        WHERE idea_id = ?
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (idea_id,))
        row = cursor.fetchone()

    if not row:
        return {
            'total_elements': 0,
            'completed_elements': 0,
            'completion_percentage': 0.0,
            'total_effort_hours': 0.0,
            'completed_effort_hours': 0.0,
            'effort_completion_percentage': 0.0
        }

    total_elements = row['total_elements'] or 0
    completed_elements = row['completed_elements'] or 0
    total_effort = row['total_effort_hours'] or 0.0
    completed_effort = row['completed_effort_hours'] or 0.0

    completion_percentage = (completed_elements / total_elements) if total_elements > 0 else 0.0
    effort_completion_percentage = (completed_effort / total_effort) if total_effort > 0 else 0.0

    return {
        'total_elements': total_elements,
        'completed_elements': completed_elements,
        'completion_percentage': completion_percentage,
        'total_effort_hours': total_effort,
        'completed_effort_hours': completed_effort,
        'effort_completion_percentage': effort_completion_percentage
    }
