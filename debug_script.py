#!/usr/bin/env python
import sys
import os
from pathlib import Path
from mongomock import MongoClient
from fastapi.testclient import TestClient

# Add src directory to path BEFORE importing backend modules
# Expected layout:
#   <project_root>/
#       src/
#       test_debug.py   (this script)
#
# If this script is moved, or the project layout changes, adjust the logic
# below to point to the correct project root.
script_dir = Path(__file__).resolve().parent
src_dir = script_dir / "src"

# Fail fast if the expected src directory is not found, rather than silently
# misconfiguring the import path.
if not src_dir.is_dir():
    raise RuntimeError(
        f"Expected 'src' directory at {src_dir}. "
        "Ensure test_debug.py is located at the project root or update the "
        "path calculation accordingly."
    )

src_path = str(src_dir)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Ensure this script only runs in an explicit testing/debug context.
# Require the caller to set TESTING=true instead of mutating the environment here.
if os.environ.get('TESTING') != 'true':
    raise RuntimeError(
        "This script is intended for debugging in a test environment only. "
        "Run it with the environment variable TESTING=true set explicitly."
    )

# NOW import modules after path is configured
import backend.database as db_module
from backend.routers import auth as auth_module
from app import app

# Setup like conftest does

client = MongoClient()
test_db = client['mergington_high_test']

# Clear collections
test_db['activities'].drop()
test_db['teachers'].drop()
test_db['announcements'].drop()

# Patch the database module to use mock collections BEFORE importing app
db_module.activities_collection = test_db['activities']
db_module.teachers_collection = test_db['teachers']
db_module.announcements_collection = test_db['announcements']

# Set initial data
db_module.initial_activities = {}
db_module.initial_teachers = [
    {
        'username': 'ms_rodriguez',
        'display_name': 'Ms. Rodriguez',
        'password': 'SecurePass123',
        'role': 'teacher'
    }
]
db_module.initial_announcements = []

# Initialize BEFORE importing app
db_module.init_database()

print('Teachers in DB before app import:')
for t in db_module.teachers_collection.find():
    print(f'  - ID: {t["_id"]}, Username: {t["username"]}')

print("\nApp imported successfully")


test_client = TestClient(app)

# Check what db_module is using inside the app
print(f"\nAuth module imported successfully from backend.routers")

# Check again
print('\nTeachers in DB after app import:')
for t in db_module.teachers_collection.find():
    print(f'  - ID: {t["_id"]}, Username: {t["username"]}')

# Test login
response = test_client.post(
    '/auth/login',
    params={
        'username': 'ms_rodriguez',
        'password': 'SecurePass123'
    }
)

print(f'\nLogin Response status: {response.status_code}')
print(f'Response body: {response.json()}')
