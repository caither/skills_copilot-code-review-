"""Unit tests for backend.database module"""

import pytest
from backend.database import (
    hash_password,
    verify_password,
    init_database,
)


class TestPasswordHashing:
    """Test password hashing and verification using Argon2"""

    @pytest.mark.unit
    def test_hash_password_creates_valid_hash(self):
        """Test that hash_password creates a valid Argon2 hash"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        # Hash should not equal plain password
        assert hashed != password
        # Hash should contain Argon2 identifier
        assert "$argon2" in hashed

    @pytest.mark.unit
    def test_verify_password_matches_valid_password(self):
        """Test that verify_password returns True for correct password"""
        password = "SecurePass123"
        hashed = hash_password(password)

        result = verify_password(hashed, password)
        assert result is True

    @pytest.mark.unit
    def test_verify_password_rejects_invalid_password(self):
        """Test that verify_password returns False for incorrect password"""
        password = "SecurePass123"
        wrong_password = "WrongPass456"
        hashed = hash_password(password)

        result = verify_password(hashed, wrong_password)
        assert result is False

    @pytest.mark.unit
    def test_verify_password_handles_invalid_hash(self):
        """Test that verify_password handles invalid hash gracefully"""
        invalid_hash = "invalid_hash_format"
        password = "TestPassword123"

        result = verify_password(invalid_hash, password)
        assert result is False

    @pytest.mark.unit
    def test_verify_password_handles_empty_inputs(self):
        """Test that verify_password handles empty inputs safely"""
        hashed = hash_password("ValidPassword")

        result = verify_password(hashed, "")
        assert result is False

    @pytest.mark.unit
    def test_hash_password_consistency(self):
        """Test that same password creates different hashes (Argon2 uses salt)"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Argon2 uses salt, so hashes should be different
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(hash1, password) is True
        assert verify_password(hash2, password) is True


class TestDatabaseInitialization:
    """Test database initialization and setup"""

    @pytest.mark.unit
    def test_init_database_creates_activities(self, mock_database):
        """Test that init_database creates activity records"""
        # Clear first
        mock_database['activities'].delete_many({})

        init_database()

        # Check that activities were created
        count = mock_database['activities'].count_documents({})
        assert count > 0

    @pytest.mark.unit
    def test_init_database_creates_teachers(self, mock_database):
        """Test that init_database creates teacher accounts"""
        # Clear first
        mock_database['teachers'].delete_many({})

        init_database()

        # Check that teachers were created
        count = mock_database['teachers'].count_documents({})
        assert count >= 2  # Should have at least 2 teachers

    @pytest.mark.unit
    def test_init_database_creates_announcements(self, mock_database):
        """Test that init_database creates announcement records"""
        # Clear first
        mock_database['announcements'].delete_many({})

        init_database()

        # Check that announcements were created
        count = mock_database['announcements'].count_documents({})
        assert count >= 1

    @pytest.mark.unit
    def test_init_database_idempotency(self, mock_database):
        """Test that running init_database twice doesn't duplicate data"""
        init_database()
        activities_count_first = mock_database['activities'].count_documents({})
        teachers_count_first = mock_database['teachers'].count_documents({})
        announcements_count_first = mock_database['announcements'].count_documents({})

        init_database()
        activities_count_second = mock_database['activities'].count_documents({})
        teachers_count_second = mock_database['teachers'].count_documents({})
        announcements_count_second = mock_database['announcements'].count_documents({})

        # Counts should be the same across all collections (idempotent)
        assert activities_count_first == activities_count_second
        assert teachers_count_first == teachers_count_second
        assert announcements_count_first == announcements_count_second


class TestDatabaseCollections:
    """Test database collections and schema"""

    @pytest.mark.unit
    def test_activities_collection_schema(self, mock_database):
        """Test that activity documents have expected schema"""
        init_database()

        activity = mock_database['activities'].find_one()

        assert activity is not None
        assert '_id' in activity  # Activity name as ID
        assert 'description' in activity
        assert 'schedule' in activity
        assert 'schedule_details' in activity
        assert 'max_participants' in activity
        assert 'participants' in activity
        assert isinstance(activity['participants'], list)

    @pytest.mark.unit
    def test_schedule_details_structure(self, mock_database):
        """Test that schedule_details has correct structure"""
        init_database()

        activity = mock_database['activities'].find_one()
        schedule_details = activity['schedule_details']

        assert 'days' in schedule_details
        assert 'start_time' in schedule_details
        assert 'end_time' in schedule_details
        assert isinstance(schedule_details['days'], list)

    @pytest.mark.unit
    def test_teachers_collection_schema(self, mock_database):
        """Test that teacher documents have expected schema"""
        init_database()

        teacher = mock_database['teachers'].find_one()

        assert teacher is not None
        assert '_id' in teacher  # Username as ID
        assert 'username' in teacher
        assert 'display_name' in teacher
        assert 'password' in teacher
        assert 'role' in teacher
        assert '$argon2' in teacher['password']  # Password should be hashed

    @pytest.mark.unit
    def test_announcements_collection_schema(self, mock_database):
        """Test that announcement documents have expected schema"""
        init_database()

        announcement = mock_database['announcements'].find_one()

        assert announcement is not None
        assert '_id' in announcement  # ObjectId
        assert 'message' in announcement
        assert 'expiration_date' in announcement
        # start_date is optional
