"""
System Blueprint for APM (Agent Project Manager) Web Application

System administration and monitoring functionality.
"""

from flask import Blueprint, render_template
import logging

# Create system blueprint
system_bp = Blueprint('system', __name__, url_prefix='/system')

logger = logging.getLogger(__name__)

@system_bp.route('/health')
def system_health():
    """
    System health monitoring.
    
    Shows system status and health metrics:
    - Database connectivity
    - System performance
    - Agent status
    - Service health
    """
    # Create mock system data
    system_data = {
        'last_db_check': '2024-01-01 12:00:00',
        'uptime': '2 days, 5 hours',
        'active_agents': 3,
        'last_security_scan': '2024-01-01 10:00:00',
        'cpu_usage': 25,
        'memory_usage': 60,
        'disk_usage': 45,
        'db_size': '2.3 MB',
        'tables_count': 12,
        'last_backup': '2024-01-01 08:00:00',
        'app_version': 'APM (Agent Project Manager).0.0',
        'environment': 'Development',
        'db_type': 'SQLite',
        'db_version': '3.42.0',
        'python_version': '3.12.0',
        'flask_version': '3.0.0',
        'start_time': '2024-01-01 00:00:00',
        'recent_activity': [
            {'description': 'System started successfully', 'timestamp': '2024-01-01 00:00:00'},
            {'description': 'Database connection established', 'timestamp': '2024-01-01 00:00:01'},
            {'description': 'All agents activated', 'timestamp': '2024-01-01 00:00:02'}
        ]
    }
    
    return render_template('system/health.html', system=system_data)

@system_bp.route('/database')
def system_database():
    """
    Database management and monitoring.
    
    Shows database information and management options:
    - Database status and metrics
    - Connection information
    - Performance metrics
    - Management tools
    """
    return render_template('system/database.html')