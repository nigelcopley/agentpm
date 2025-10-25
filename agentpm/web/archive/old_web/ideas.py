"""
Ideas Blueprint - Ideas Management and Lifecycle

Handles:
- /ideas - List all ideas
- /ideas/<id> - Get idea details
- /ideas/<id>/edit - Edit idea form
- /ideas/<id>/actions/vote - Vote on idea
- /ideas/<id>/actions/transition - Transition idea status
- /ideas/<id>/actions/convert - Convert to work item
"""

from flask import Blueprint, render_template, abort, request, jsonify
from datetime import datetime

from ...core.database.methods import ideas as idea_methods
from ...core.database.methods import projects as project_methods

# Import helper functions from app
from ..app import get_database_service

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/ideas')
def ideas_list():
    """List all ideas with filtering and voting interface."""
    db = get_database_service()

    # Get filter params
    status_filter = request.args.get('status')
    tag_filter = request.args.get('tags')
    sort_by = request.args.get('sort', 'created_at')

    # Get current project (assume project ID 1 for now, or get from session)
    project = project_methods.get_project(db, 1)
    project_id = project.id if project else 1

    # Get all ideas for this project
    all_ideas = idea_methods.list_ideas(db, project_id=project_id)

    # Apply filters
    filtered_ideas = all_ideas

    if status_filter:
        filtered_ideas = [i for i in filtered_ideas if i.status == status_filter]

    if tag_filter:
        # Parse comma-separated tags from query param
        tags = [t.strip() for t in tag_filter.split(',')]
        filtered_ideas = [
            i for i in filtered_ideas
            if i.tags and any(tag in i.tags for tag in tags)
        ]

    # Sort
    if sort_by == 'votes':
        filtered_ideas.sort(key=lambda i: i.votes or 0, reverse=True)
    elif sort_by == 'created_at':
        filtered_ideas.sort(key=lambda i: i.created_at or datetime.min, reverse=True)
    elif sort_by == 'updated_at':
        filtered_ideas.sort(key=lambda i: i.updated_at or datetime.min, reverse=True)

    # Calculate summary stats
    total_ideas = len(all_ideas)
    by_status = {}
    for idea in all_ideas:
        status = idea.status or 'idea'
        by_status[status] = by_status.get(status, 0) + 1

    # Tag cloud
    tag_counts = {}
    for idea in all_ideas:
        if idea.tags:
            for tag in idea.tags:  # tags is already a list
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort tags by frequency
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template(
        'ideas/list.html',
        ideas=filtered_ideas,
        total_ideas=total_ideas,
        status_distribution=by_status,
        popular_tags=popular_tags,
        current_status_filter=status_filter,
        current_tag_filter=tag_filter,
        current_sort=sort_by,
        show_sidebar='ideas'
    )


@ideas_bp.route('/ideas/<int:idea_id>')
def idea_detail(idea_id: int):
    """Get idea details with voting and lifecycle management."""
    db = get_database_service()

    idea = idea_methods.get_idea(db, idea_id)

    if not idea:
        abort(404, description=f"Idea {idea_id} not found")

    # Get project info
    project = project_methods.get_project(db, idea.project_id)
    project_name = project.name if project else "Unknown"

    # Tags are already a list in the model
    tags_list = idea.tags if idea.tags else []

    # Check if converted to work item
    converted_work_item = None
    if idea.converted_to_work_item_id:
        from ...core.database.methods import work_items as wi_methods
        converted_work_item = wi_methods.get_work_item(db, idea.converted_to_work_item_id)

    return render_template(
        'idea_detail.html',
        idea=idea,
        project_name=project_name,
        tags=tags_list,
        converted_work_item=converted_work_item
    )


@ideas_bp.route('/ideas/<int:idea_id>/edit')
def idea_edit(idea_id: int):
    """Edit idea form."""
    db = get_database_service()
    idea = idea_methods.get_idea(db, idea_id)
    
    if not idea:
        abort(404, description=f"Idea {idea_id} not found")
    
    return render_template('ideas/edit.html', idea=idea)


@ideas_bp.route('/ideas/<int:idea_id>/actions/vote', methods=['POST'])
def vote_on_idea(idea_id: int):
    """Vote on an idea (upvote/downvote)."""
    db = get_database_service()

    idea = idea_methods.get_idea(db, idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404

    data = request.get_json()
    direction = data.get('direction', 'up')

    # Update votes
    current_votes = idea.votes or 0
    if direction == 'up':
        new_votes = current_votes + 1
    else:  # down
        new_votes = max(0, current_votes - 1)  # Don't go negative

    # Update in database
    db.execute(
        "UPDATE ideas SET votes = ?, updated_at = ? WHERE id = ?",
        (new_votes, datetime.now(), idea_id)
    )
    db.commit()

    return jsonify({
        "success": True,
        "idea_id": idea_id,
        "votes": new_votes
    })


@ideas_bp.route('/ideas/<int:idea_id>/actions/transition', methods=['POST'])
def transition_idea(idea_id: int):
    """Transition idea through lifecycle."""
    db = get_database_service()

    idea = idea_methods.get_idea(db, idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404

    data = request.get_json()
    new_status = data.get('new_status')
    reason = data.get('reason')
    work_item_id = data.get('work_item_id')

    # Validate transition
    valid_statuses = ['idea', 'research', 'design', 'proposed', 'rejected', 'converted']
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status: {new_status}"}), 400

    # Update idea
    update_sql = "UPDATE ideas SET status = ?, updated_at = ?"
    params = [new_status, datetime.now()]

    if new_status == 'rejected' and reason:
        update_sql += ", rejection_reason = ?"
        params.append(reason)

    if new_status == 'converted' and work_item_id:
        update_sql += ", converted_to_work_item_id = ?, converted_at = ?"
        params.extend([work_item_id, datetime.now()])

    update_sql += " WHERE id = ?"
    params.append(idea_id)

    db.execute(update_sql, tuple(params))
    db.commit()

    return jsonify({
        "success": True,
        "idea_id": idea_id,
        "new_status": new_status
    })


@ideas_bp.route('/ideas/<int:idea_id>/actions/convert', methods=['POST'])
def convert_idea_to_work_item(idea_id: int):
    """Convert idea to work item."""
    db = get_database_service()

    idea = idea_methods.get_idea(db, idea_id)
    if not idea:
        return jsonify({"error": "Idea not found"}), 404

    # Get form data
    work_item_type = request.form.get('work_item_type', 'feature')
    name = request.form.get('name', idea.title)
    description = request.form.get('description', idea.description or '')
    priority = int(request.form.get('priority', 3))

    # Create work item
    from ...core.database.methods import work_items as wi_methods

    work_item = wi_methods.create_work_item(
        db=db,
        name=name,
        description=description,
        work_item_type=work_item_type,
        priority=priority,
        project_id=idea.project_id
    )

    # Update idea status
    db.execute(
        "UPDATE ideas SET status = ?, converted_to_work_item_id = ?, converted_at = ?, updated_at = ? WHERE id = ?",
        ('converted', work_item.id, datetime.now(), datetime.now(), idea_id)
    )
    db.commit()

    # Return HTMX redirect
    return f"""
    <div hx-get="/work-items/{work_item.id}" hx-target="body" hx-push-url="true"></div>
    """, 200, {'HX-Redirect': f'/work-items/{work_item.id}'}
