"""
Pytest configuration and fixtures for Mergington High School Activities API tests
"""

import backend.database as db_module
import pytest
import sys
from pathlib import Path
from mongomock import MongoClient
from datetime import datetime

# Add src directory to path for imports BEFORE any other imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Verify path setup is complete before importing backend modules
assert src_path in sys.path, f"Failed to add {src_path} to sys.path"

# Import backend modules after verifying path setup

# Replace real MongoDB client with mongomock


@pytest.fixture(scope="session")
def mock_db_client():
    """Create a mock MongoDB client using mongomock"""
    return MongoClient()


@pytest.fixture(scope="function")
def mock_database(mock_db_client):
    """Set up mock database collections for each test"""
    # Get mock database
    test_db = mock_db_client['mergington_high_test']

    # Clear collections before each test
    test_db['activities'].drop()
    test_db['teachers'].drop()
    test_db['announcements'].drop()

    # Patch the database module to use mock collections
    db_module.activities_collection = test_db['activities']
    db_module.teachers_collection = test_db['teachers']
    db_module.announcements_collection = test_db['announcements']

    # Initialize with sample data
    db_module.initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
            "schedule_details": {
                "days": ["Monday", "Friday"],
                "start_time": "15:15",
                "end_time": "16:45"
            },
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
            "schedule_details": {
                "days": ["Tuesday", "Thursday"],
                "start_time": "07:00",
                "end_time": "08:00"
            },
            "max_participants": 20,
            "participants": []
        }
    }

    db_module.initial_teachers = [
        {
            "username": "ms_rodriguez",
            "display_name": "Ms. Rodriguez",
            "password": "SecurePass123",
            "role": "teacher"
        },
        {
            "username": "mr_smith",
            "display_name": "Mr. Smith",
            "password": "TeacherPass456",
            "role": "teacher"
        }
    ]

    db_module.initial_announcements = [
        {
            "message": "School assembly tomorrow at 2 PM",
            "start_date": "2025-12-20",
            "expiration_date": "2025-12-26"
        }
    ]

    # Initialize database
    db_module.init_database()

    yield {
        'activities': test_db['activities'],
        'teachers': test_db['teachers'],
        'announcements': test_db['announcements']
    }

    # Cleanup
    test_db.drop_collection('activities')
    test_db.drop_collection('teachers')
    test_db.drop_collection('announcements')


@pytest.fixture
def test_client(mock_database):
    """
    Create a FastAPI test client with mocked database.

    **Design Pattern: Factory Pattern with Dependency Injection**

    This fixture uses a factory pattern (create_app) to instantiate a fresh app
    for each test, rather than manipulating global module state. This approach:

    1. **Avoids fragile module reloading**: Previous approach deleted modules from
       sys.modules and reloaded them, which caused:
       - Race conditions with other tests
       - Stale imports in module caches
       - Difficulty debugging import issues
       - Dependency ordering problems

    2. **Uses dependency injection**: The app receives concrete implementations
       (mocked collections) through constructor parameters via Depends() in routers,
       not through global state manipulation.

    3. **Maintains test isolation**: Each test gets a fresh app instance with
       clean state, without side effects from module reloading.

    **How It Works:**
    - conftest.py patches db_module collections with mock instances (mongomock)
    - create_app(TestingDatabaseInit()) creates a new app with testing strategy
    - Routers use Depends() to inject the already-mocked collections
    - No module reloading or sys.modules manipulation needed

    **Result:** Tests are more reliable, faster, and easier to debug.
    """
    from fastapi.testclient import TestClient
    from backend.config import create_app, TestingDatabaseInit
    import backend.database as db_module

    # Ensure database is initialized with mocked collections
    # (fixtures have already patched db_module with mock collections)
    db_module.init_database()

    # Create fresh app instance with testing strategy
    # The routers will use the already-mocked collections from db_module
    app = create_app(TestingDatabaseInit())

    return TestClient(app)


@pytest.fixture
def sample_activities(mock_database):
    """Provide sample activity data"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule_details": {
                "days": ["Monday", "Friday"],
                "start_time": "15:15",
                "end_time": "16:45"
            }
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule_details": {
                "days": ["Tuesday", "Thursday"],
                "start_time": "07:00",
                "end_time": "08:00"
            }
        }
    }


@pytest.fixture
def sample_teachers(mock_database):
    """Provide sample teacher data"""
    return {
        "ms_rodriguez": {
            "username": "ms_rodriguez",
            "display_name": "Ms. Rodriguez",
            "password": "SecurePass123",
            "role": "teacher"
        },
        "mr_smith": {
            "username": "mr_smith",
            "display_name": "Mr. Smith",
            "password": "TeacherPass456",
            "role": "teacher"
        }
    }


@pytest.fixture
def sample_announcements(mock_database):
    """Provide sample announcement data"""
    return {
        "valid": {
            "message": "Winter Sports Day on December 25th",
            "start_date": "2025-12-20",
            "expiration_date": "2025-12-26"
        },
        "expired": {
            "message": "Past event",
            "expiration_date": "2025-12-01"
        },
        "future": {
            "message": "Future event",
            "start_date": "2025-12-31",
            "expiration_date": "2026-01-05"
        }
    }


@pytest.fixture
def teacher_headers(sample_teachers):
    """Provide teacher credentials for API requests"""
    return {
        "teacher_username": "ms_rodriguez"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
