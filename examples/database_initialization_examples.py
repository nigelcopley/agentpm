"""
Database Initialization Examples

Shows how to use the centralized database initialization pattern
instead of creating DatabaseService instances directly.
"""

# OLD WAY (problematic - creates multiple instances)
# db_path = 'agentpm/aipm_v2.db'
# db = DatabaseService(db_path)

# NEW WAY (recommended - centralized initialization)

# Method 1: Using DatabaseInitializer class
from agentpm.core.database import DatabaseInitializer

# Initialize at application startup
db = DatabaseInitializer.initialize()

# Get instance anywhere in your code
db_service = DatabaseInitializer.get_instance()

# Check if initialized
if DatabaseInitializer.is_initialized():
    print("Database is ready")

# Cleanup on shutdown
DatabaseInitializer.cleanup()


# Method 2: Using convenience functions
from agentpm.core.database import initialize_database, get_database, cleanup_database

# Initialize
db = initialize_database()

# Get instance
db_service = get_database()

# Cleanup
cleanup_database()


# Method 3: With explicit path
db = DatabaseInitializer.initialize(db_path="/path/to/specific/database.db")


# Method 4: Force reinitialization
db = DatabaseInitializer.initialize(force_reinit=True)


# CLI Integration Example
def cli_command():
    """Example CLI command using centralized database."""
    try:
        db = DatabaseInitializer.get_instance()
        projects = db.projects.list_projects()
        return projects
    except RuntimeError:
        # Database not initialized - handle gracefully
        print("Database not initialized. Run 'apm init' first.")
        return []


# Web App Integration Example
def web_route():
    """Example web route using centralized database."""
    try:
        db = DatabaseInitializer.get_instance()
        return db.work_items.list_work_items()
    except RuntimeError:
        # Database not initialized - return error
        return {"error": "Database not available"}, 500


# Testing Example
def test_example():
    """Example test using isolated test database."""
    from tests.utils.database import isolated_test_database
    
    with isolated_test_database() as db:
        # Test code here
        work_item = db.work_items.create_work_item(
            name="Test Item",
            description="Test Description"
        )
        assert work_item.id is not None
