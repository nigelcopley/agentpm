"""
WebSocket Integration for Real-Time Updates - APM (Agent Project Manager)

Provides real-time event broadcasting for:
- Work item updates
- Task updates
- Rule toggles
- Project changes

Architecture:
- Flask-SocketIO for WebSocket server
- Room-based broadcasting (project-specific)
- Event protocols for entity updates
- Connection management and authentication

Usage:
    # Initialize WebSocket with Flask app
    from agentpm.web.websocket import init_websocket, broadcast_event
    socketio = init_websocket(app)

    # Broadcast events from routes
    broadcast_event('work_item_updated', {
        'work_item_id': 123,
        'project_id': 1,
        'status': 'IN_PROGRESS'
    })

    # Run with WebSocket support
    socketio.run(app, host='127.0.0.1', port=5000)

Events Protocol:
    work_item_updated:
        - work_item_id: int
        - project_id: int
        - name: str
        - status: str
        - phase: str
        - updated_at: str (ISO format)

    task_updated:
        - task_id: int
        - work_item_id: int
        - project_id: int
        - name: str
        - status: str
        - updated_at: str (ISO format)

    rule_toggled:
        - rule_id: int
        - project_id: int
        - enabled: bool
        - rule_code: str

    project_updated:
        - project_id: int
        - name: str
        - status: str
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Global SocketIO instance (initialized by init_websocket)
socketio: Optional[SocketIO] = None


# ========================================
# Event Models (Pydantic for Type Safety)
# ========================================

class WorkItemUpdatedEvent(BaseModel):
    """Work item update event payload"""
    work_item_id: int
    project_id: int
    name: str
    status: str
    phase: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "work_item_id": 123,
                "project_id": 1,
                "name": "Feature: OAuth2 Integration",
                "status": "IN_PROGRESS",
                "phase": "I1_IMPLEMENTATION",
                "updated_at": "2025-10-21T10:30:00Z"
            }
        }


class TaskUpdatedEvent(BaseModel):
    """Task update event payload"""
    task_id: int
    work_item_id: int
    project_id: int
    name: str
    status: str
    type: Optional[str] = None
    assigned_to: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 456,
                "work_item_id": 123,
                "project_id": 1,
                "name": "Implement OAuth2 provider",
                "status": "IN_PROGRESS",
                "type": "IMPLEMENTATION",
                "assigned_to": "aipm-python-cli-developer",
                "updated_at": "2025-10-21T10:30:00Z"
            }
        }


class RuleToggledEvent(BaseModel):
    """Rule toggle event payload"""
    rule_id: int
    project_id: int
    enabled: bool
    rule_code: str
    category: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": 1,
                "project_id": 1,
                "enabled": True,
                "rule_code": "DP-001",
                "category": "development",
                "updated_at": "2025-10-21T10:30:00Z"
            }
        }


class ProjectUpdatedEvent(BaseModel):
    """Project update event payload"""
    project_id: int
    name: str
    status: str
    tech_stack: Optional[List[str]] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "name": "APM (Agent Project Manager)",
                "status": "ACTIVE",
                "tech_stack": ["Python", "Flask", "SQLite"],
                "updated_at": "2025-10-21T10:30:00Z"
            }
        }


# ========================================
# Connection Management
# ========================================

class ConnectionManager:
    """
    Manages WebSocket connections and room assignments.

    Rooms are organized by project ID:
    - project:1 (all clients viewing project 1)
    - project:2 (all clients viewing project 2)
    - global (all connected clients)
    """

    def __init__(self):
        self.connections: Dict[str, List[str]] = {}  # room -> [session_ids]

    def add_connection(self, session_id: str, room: str):
        """Add connection to room"""
        if room not in self.connections:
            self.connections[room] = []
        if session_id not in self.connections[room]:
            self.connections[room].append(session_id)
        logger.info(f"Connection {session_id} joined room {room}")

    def remove_connection(self, session_id: str, room: str):
        """Remove connection from room"""
        if room in self.connections and session_id in self.connections[room]:
            self.connections[room].remove(session_id)
            logger.info(f"Connection {session_id} left room {room}")

            # Clean up empty rooms
            if not self.connections[room]:
                del self.connections[room]

    def get_room_size(self, room: str) -> int:
        """Get number of connections in room"""
        return len(self.connections.get(room, []))

    def get_all_rooms(self) -> List[str]:
        """Get all active rooms"""
        return list(self.connections.keys())


# Global connection manager
connection_manager = ConnectionManager()


# ========================================
# WebSocket Event Handlers
# ========================================

def on_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to AIPM WebSocket',
        'session_id': request.sid,
        'timestamp': datetime.utcnow().isoformat()
    })


def on_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

    # Remove from all rooms
    client_rooms = rooms(request.sid)
    for room in client_rooms:
        if room.startswith('project:'):
            connection_manager.remove_connection(request.sid, room)


def on_join_project(data: Dict[str, Any]):
    """
    Handle client joining project room.

    Args:
        data: {'project_id': int}
    """
    project_id = data.get('project_id')
    if not project_id:
        emit('error', {'message': 'Missing project_id'})
        return

    room = f"project:{project_id}"
    join_room(room)
    connection_manager.add_connection(request.sid, room)

    emit('joined_project', {
        'project_id': project_id,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    })

    logger.info(f"Client {request.sid} joined project {project_id}")


def on_leave_project(data: Dict[str, Any]):
    """
    Handle client leaving project room.

    Args:
        data: {'project_id': int}
    """
    project_id = data.get('project_id')
    if not project_id:
        emit('error', {'message': 'Missing project_id'})
        return

    room = f"project:{project_id}"
    leave_room(room)
    connection_manager.remove_connection(request.sid, room)

    emit('left_project', {
        'project_id': project_id,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    })

    logger.info(f"Client {request.sid} left project {project_id}")


def on_ping():
    """Handle keepalive ping from client"""
    emit('pong', {'timestamp': datetime.utcnow().isoformat()})


# ========================================
# Event Broadcasting API
# ========================================

def broadcast_event(event_type: str, data: Dict[str, Any], project_id: Optional[int] = None):
    """
    Broadcast event to all clients in project room or globally.

    Args:
        event_type: Event name (work_item_updated, task_updated, rule_toggled, project_updated)
        data: Event payload (dict matching event model)
        project_id: Project ID for room-based broadcasting (None = global broadcast)

    Example:
        broadcast_event('work_item_updated', {
            'work_item_id': 123,
            'project_id': 1,
            'name': 'Feature: OAuth2',
            'status': 'IN_PROGRESS',
            'phase': 'I1_IMPLEMENTATION'
        }, project_id=1)
    """
    if not socketio:
        logger.warning("SocketIO not initialized, skipping broadcast")
        return

    # Validate event data using Pydantic models
    try:
        if event_type == 'work_item_updated':
            validated_data = WorkItemUpdatedEvent(**data).model_dump()
        elif event_type == 'task_updated':
            validated_data = TaskUpdatedEvent(**data).model_dump()
        elif event_type == 'rule_toggled':
            validated_data = RuleToggledEvent(**data).model_dump()
        elif event_type == 'project_updated':
            validated_data = ProjectUpdatedEvent(**data).model_dump()
        else:
            logger.warning(f"Unknown event type: {event_type}")
            validated_data = data
    except Exception as e:
        logger.error(f"Event validation failed: {e}")
        return

    # Determine broadcast target
    if project_id:
        room = f"project:{project_id}"
        logger.info(f"Broadcasting {event_type} to room {room}")
        socketio.emit(event_type, validated_data, room=room)
    else:
        logger.info(f"Broadcasting {event_type} globally")
        socketio.emit(event_type, validated_data, broadcast=True)


def broadcast_work_item_update(work_item_id: int, project_id: int, name: str, status: str, phase: Optional[str] = None):
    """
    Convenience method for broadcasting work item updates.

    Args:
        work_item_id: Work item ID
        project_id: Project ID
        name: Work item name
        status: Work item status
        phase: Work item phase (optional)
    """
    broadcast_event('work_item_updated', {
        'work_item_id': work_item_id,
        'project_id': project_id,
        'name': name,
        'status': status,
        'phase': phase
    }, project_id=project_id)


def broadcast_task_update(task_id: int, work_item_id: int, project_id: int, name: str, status: str,
                         type: Optional[str] = None, assigned_to: Optional[str] = None):
    """
    Convenience method for broadcasting task updates.

    Args:
        task_id: Task ID
        work_item_id: Parent work item ID
        project_id: Project ID
        name: Task name
        status: Task status
        type: Task type (optional)
        assigned_to: Assigned agent (optional)
    """
    broadcast_event('task_updated', {
        'task_id': task_id,
        'work_item_id': work_item_id,
        'project_id': project_id,
        'name': name,
        'status': status,
        'type': type,
        'assigned_to': assigned_to
    }, project_id=project_id)


def broadcast_rule_toggle(rule_id: int, project_id: int, enabled: bool, rule_code: str, category: Optional[str] = None):
    """
    Convenience method for broadcasting rule toggles.

    Args:
        rule_id: Rule ID
        project_id: Project ID
        enabled: Whether rule is enabled
        rule_code: Rule code (e.g., DP-001)
        category: Rule category (optional)
    """
    broadcast_event('rule_toggled', {
        'rule_id': rule_id,
        'project_id': project_id,
        'enabled': enabled,
        'rule_code': rule_code,
        'category': category
    }, project_id=project_id)


def broadcast_project_update(project_id: int, name: str, status: str, tech_stack: Optional[List[str]] = None):
    """
    Convenience method for broadcasting project updates.

    Args:
        project_id: Project ID
        name: Project name
        status: Project status
        tech_stack: Technology stack (optional)
    """
    broadcast_event('project_updated', {
        'project_id': project_id,
        'name': name,
        'status': status,
        'tech_stack': tech_stack
    }, project_id=project_id)


# ========================================
# Initialization
# ========================================

def init_websocket(app: Flask) -> SocketIO:
    """
    Initialize Flask-SocketIO with application.

    Args:
        app: Flask application instance

    Returns:
        SocketIO instance

    Example:
        from flask import Flask
        from agentpm.web.websocket import init_websocket

        app = Flask(__name__)
        socketio = init_websocket(app)

        if __name__ == '__main__':
            socketio.run(app, host='127.0.0.1', port=5000)
    """
    global socketio

    # Initialize Flask-SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Allow all origins (restrict in production)
        async_mode='threading',  # Use threading mode (no eventlet/gevent required)
        logger=True,
        engineio_logger=True,
        ping_timeout=60,
        ping_interval=25
    )

    # Register event handlers
    socketio.on_event('connect', on_connect)
    socketio.on_event('disconnect', on_disconnect)
    socketio.on_event('join_project', on_join_project)
    socketio.on_event('leave_project', on_leave_project)
    socketio.on_event('ping', on_ping)

    logger.info("WebSocket initialized successfully")

    return socketio


# ========================================
# Health Check
# ========================================

def get_connection_stats() -> Dict[str, Any]:
    """
    Get WebSocket connection statistics.

    Returns:
        Dictionary with connection stats
    """
    return {
        'total_rooms': len(connection_manager.get_all_rooms()),
        'rooms': {
            room: connection_manager.get_room_size(room)
            for room in connection_manager.get_all_rooms()
        },
        'timestamp': datetime.utcnow().isoformat()
    }
