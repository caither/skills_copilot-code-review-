"""Unit tests for activities router endpoints"""

import pytest
from fastapi.testclient import TestClient
from app import app



class TestGetActivities:
    """Test GET /activities endpoint"""

    @pytest.mark.unit
    def test_get_activities_returns_all_activities(self, test_client, mock_database):
        """Test that GET /activities returns all activities"""
        response = test_client.get("/activities")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 2  # Should have at least 2 activities from fixtures

    @pytest.mark.unit
    def test_get_activities_returns_correct_structure(self, test_client, mock_database):
        """Test that activities have correct structure"""
        response = test_client.get("/activities")
        data = response.json()

        for activity_name, activity_data in data.items():
            assert 'description' in activity_data
            assert 'schedule' in activity_data
            assert 'schedule_details' in activity_data
            assert 'max_participants' in activity_data
            assert 'participants' in activity_data

    @pytest.mark.unit
    def test_filter_activities_by_day(self, test_client, mock_database):
        """Test filtering activities by day (Equivalence Partitioning)"""
        # Test valid day
        response = test_client.get("/activities?day=Monday")
        assert response.status_code == 200
        data = response.json()

        # Verify all returned activities have Monday
        for activity_name, activity_data in data.items():
            assert 'Monday' in activity_data['schedule_details']['days']

    @pytest.mark.unit
    def test_filter_activities_by_start_time(self, test_client, mock_database):
        """Test filtering activities by start time (Boundary Value Analysis)"""
        response = test_client.get("/activities?start_time=15:00")
        assert response.status_code == 200
        data = response.json()

        # All returned activities should start at or after 15:00
        for activity_name, activity_data in data.items():
            start_time = activity_data['schedule_details']['start_time']
            assert start_time >= "15:00"

    @pytest.mark.unit
    def test_filter_activities_by_end_time(self, test_client, mock_database):
        """Test filtering activities by end time (Boundary Value Analysis)"""
        response = test_client.get("/activities?end_time=08:00")
        assert response.status_code == 200
        data = response.json()

        # All returned activities should end at or before 08:00
        for activity_name, activity_data in data.items():
            end_time = activity_data['schedule_details']['end_time']
            assert end_time <= "08:00"

    @pytest.mark.unit
    def test_combined_filters(self, test_client, mock_database):
        """Test combining multiple filters (Decision Table Testing)"""
        response = test_client.get("/activities?day=Tuesday&start_time=07:00&end_time=08:00")
        assert response.status_code == 200
        data = response.json()

        # Verify filter combinations
        for activity_name, activity_data in data.items():
            assert 'Tuesday' in activity_data['schedule_details']['days']
            assert activity_data['schedule_details']['start_time'] >= "07:00"
            assert activity_data['schedule_details']['end_time'] <= "08:00"

    @pytest.mark.unit
    def test_empty_result_with_no_matches(self, test_client, mock_database):
        """Test that no results returns empty dict (Edge Case)"""
        response = test_client.get("/activities?day=Sunday")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestGetAvailableDays:
    """Test GET /activities/days endpoint"""

    @pytest.mark.unit
    def test_get_available_days_returns_list(self, test_client, mock_database):
        """Test that GET /activities/days returns a list of days"""
        response = test_client.get("/activities/days")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.unit
    def test_available_days_are_strings(self, test_client, mock_database):
        """Test that each day is a string"""
        response = test_client.get("/activities/days")
        data = response.json()

        for day in data:
            assert isinstance(day, str)
            assert day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @pytest.mark.unit
    def test_available_days_are_sorted(self, test_client, mock_database):
        """Test that days are returned in sorted order"""
        response = test_client.get("/activities/days")
        data = response.json()

        assert data == sorted(data)

    @pytest.mark.unit
    def test_no_duplicate_days(self, test_client, mock_database):
        """Test that each day appears only once"""
        response = test_client.get("/activities/days")
        data = response.json()

        assert len(data) == len(set(data))


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    @pytest.mark.unit
    @pytest.mark.security
    def test_signup_requires_teacher_authentication(self, test_client, mock_database):
        """Test that signup requires teacher_username (Authentication)"""
        response = test_client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 401
        assert "Authentication required" in response.json()['detail']

    @pytest.mark.unit
    @pytest.mark.security
    def test_signup_with_invalid_teacher(self, test_client, mock_database):
        """Test that signup fails with invalid teacher (Authorization)"""
        response = test_client.post(
            "/activities/Chess%20Club/signup",
            params={
                "email": "student@mergington.edu",
                "teacher_username": "invalid_teacher"
            }
        )

        assert response.status_code == 401
        assert "Invalid teacher credentials" in response.json()['detail']

    @pytest.mark.unit
    def test_signup_for_valid_activity(self, test_client, mock_database):
        """Test successful signup for a valid activity"""
        response = test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": "newstudent@mergington.edu",
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 200
        assert "successfully signed up" in response.json()['message'].lower()

    @pytest.mark.unit
    def test_signup_for_nonexistent_activity(self, test_client, mock_database):
        """Test signup fails for nonexistent activity"""
        response = test_client.post(
            "/activities/Nonexistent%20Club/signup",
            params={
                "email": "student@mergington.edu",
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 404
        assert "Activity not found" in response.json()['detail']

    @pytest.mark.unit
    def test_duplicate_signup_prevented(self, test_client, mock_database):
        """Test that duplicate signups are prevented"""
        # First signup
        test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": "student@mergington.edu",
                "teacher_username": "ms_rodriguez"
            }
        )

        # Attempt duplicate signup
        response = test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": "student@mergington.edu",
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 400
        assert "already signed up" in response.json()['detail'].lower()

    @pytest.mark.unit
    def test_signup_updates_database(self, test_client, mock_database):
        """Test that signup actually updates the database (Equivalence Partitioning)"""
        email = "teststudent@mergington.edu"
        activity_name = "Programming Class"

        test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": email,
                "teacher_username": "ms_rodriguez"
            }
        )

        # Verify in database
        activity = mock_database['activities'].find_one({"_id": activity_name})
        assert email in activity['participants']


class TestCancelSignup:
    """Test DELETE /activities/{activity_name}/signup endpoint"""

    @pytest.mark.unit
    def test_cancel_signup_requires_authentication(self, test_client, mock_database):
        """Test that cancel requires teacher_username"""
        response = test_client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_cancel_signup_success(self, test_client, mock_database):
        """Test successful cancellation of signup"""
        email = "student@mergington.edu"

        # First, add student
        test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": email,
                "teacher_username": "ms_rodriguez"
            }
        )

        # Then cancel
        response = test_client.delete(
            "/activities/Programming%20Class/signup",
            params={
                "email": email,
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_cancel_signup_removes_from_database(self, test_client, mock_database):
        """Test that cancellation actually removes from database"""
        email = "student@mergington.edu"
        activity_name = "Programming Class"

        # Signup
        test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": email,
                "teacher_username": "ms_rodriguez"
            }
        )

        # Cancel
        test_client.delete(
            "/activities/Programming%20Class/signup",
            params={
                "email": email,
                "teacher_username": "ms_rodriguez"
            }
        )

        # Verify removed from database
        activity = mock_database['activities'].find_one({"_id": activity_name})
        assert email not in activity['participants']
