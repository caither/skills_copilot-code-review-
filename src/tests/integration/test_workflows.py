"""Integration tests for complete API workflows"""

import pytest
from fastapi.testclient import TestClient


class TestTeacherAuthenticationWorkflow:
    """Integration test: Complete teacher authentication flow"""

    @pytest.mark.integration
    def test_login_and_session_verification(self, test_client, mock_database):
        """Test complete login and session verification workflow"""
        username = "ms_rodriguez"
        password = "SecurePass123"

        # Login
        login_response = test_client.post(
            "/auth/login",
            params={"username": username, "password": password}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data['username'] == username

        # Verify session
        session_response = test_client.get(
            "/auth/check-session",
            params={"username": username}
        )
        assert session_response.status_code == 200
        session_data = session_response.json()
        assert session_data['username'] == login_data['username']
        assert session_data['display_name'] == login_data['display_name']


class TestActivityManagementWorkflow:
    """Integration test: Complete activity management workflow"""

    @pytest.mark.integration
    def test_view_filter_and_signup_workflow(self, test_client, mock_database):
        """Test workflow: view activities -> filter -> signup"""
        teacher_username = "ms_rodriguez"
        student_email = "student123@mergington.edu"

        # Step 1: Get all activities
        activities_response = test_client.get("/activities")
        assert activities_response.status_code == 200
        all_activities = activities_response.json()
        assert len(all_activities) > 0

        # Step 2: Filter activities by day
        filter_response = test_client.get("/activities?day=Tuesday")
        assert filter_response.status_code == 200
        filtered = filter_response.json()
        assert len(filtered) > 0

        activity_name = list(filtered.keys())[0]

        # Step 3: Signup for activity
        signup_response = test_client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup",
            params={
                "email": student_email,
                "teacher_username": teacher_username
            }
        )
        assert signup_response.status_code == 200

        # Step 4: Verify signup in database
        activity = mock_database['activities'].find_one({"_id": activity_name})
        assert student_email in activity['participants']

    @pytest.mark.integration
    def test_signup_and_cancellation_workflow(self, test_client, mock_database):
        """Test workflow: signup -> cancel -> verify removal"""
        teacher_username = "ms_rodriguez"
        student_email = "testcancel@mergington.edu"
        activity_name = "Programming Class"

        # Signup
        test_client.post(
            "/activities/Programming%20Class/signup",
            params={
                "email": student_email,
                "teacher_username": teacher_username
            }
        )

        # Verify signup
        activity = mock_database['activities'].find_one({"_id": activity_name})
        assert student_email in activity['participants']

        # Cancel signup
        cancel_response = test_client.delete(
            "/activities/Programming%20Class/signup",
            params={
                "email": student_email,
                "teacher_username": teacher_username
            }
        )
        assert cancel_response.status_code == 200

        # Verify cancellation
        activity = mock_database['activities'].find_one({"_id": activity_name})
        assert student_email not in activity['participants']


class TestAnnouncementManagementWorkflow:
    """Integration test: Complete announcement management workflow"""

    @pytest.mark.integration
    def test_create_read_update_delete_workflow(self, test_client, mock_database):
        """Test CRUD workflow for announcements"""
        teacher_username = "ms_rodriguez"
        original_message = "School Closure Due to Weather"

        # Create
        create_response = test_client.post(
            "/announcements",
            params={
                "message": original_message,
                "expiration_date": "2025-12-31",
                "teacher_username": teacher_username
            }
        )
        assert create_response.status_code == 200
        announcement_id = create_response.json()['id']

        # Read
        read_response = test_client.get("/announcements")
        assert read_response.status_code == 200
        announcements = read_response.json()
        announcement_ids = [a['id'] for a in announcements]
        assert announcement_id in announcement_ids

        # Update
        updated_message = "School Closure Extended"
        update_response = test_client.put(
            f"/announcements/{announcement_id}",
            params={
                "message": updated_message,
                "teacher_username": teacher_username
            }
        )
        assert update_response.status_code == 200

        # Verify update
        read_again = test_client.get("/announcements")
        announcements = read_again.json()
        updated = [a for a in announcements if a['id'] == announcement_id][0]
        assert updated['message'] == updated_message

        # Delete
        delete_response = test_client.delete(
            f"/announcements/{announcement_id}",
            params={"teacher_username": teacher_username}
        )
        assert delete_response.status_code == 200

        # Verify deletion
        read_final = test_client.get("/announcements")
        announcements = read_final.json()
        announcement_ids = [a['id'] for a in announcements]
        assert announcement_id not in announcement_ids


class TestMultipleStudentSignups:
    """Integration test: Multiple students signing up for same activity"""

    @pytest.mark.integration
    def test_multiple_signups_same_activity(self, test_client, mock_database):
        """Test that multiple students can sign up for the same activity"""
        teacher_username = "ms_rodriguez"
        activity_name = "Programming Class"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]

        # Each student signs up
        for student_email in students:
            response = test_client.post(
                "/activities/Programming%20Class/signup",
                params={
                    "email": student_email,
                    "teacher_username": teacher_username
                }
            )
            assert response.status_code == 200

        # Verify all are in database
        activity = mock_database['activities'].find_one({"_id": activity_name})
        for student_email in students:
            assert student_email in activity['participants']


class TestActivityFiltersIntegration:
    """Integration test: Complex activity filtering"""

    @pytest.mark.integration
    def test_combined_day_and_time_filters(self, test_client, mock_database):
        """Test filtering by multiple criteria simultaneously"""
        # Get activities for Tuesday morning (07:00-08:00)
        response = test_client.get(
            "/activities?day=Tuesday&start_time=07:00&end_time=08:00"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all results match criteria
        for activity_name, activity_data in data.items():
            assert 'Tuesday' in activity_data['schedule_details']['days']
            assert activity_data['schedule_details']['start_time'] >= "07:00"
            assert activity_data['schedule_details']['end_time'] <= "08:00"