"""Unit tests for announcements router endpoints"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app import app

class TestGetAnnouncements:
    """Test GET /announcements endpoint"""

    @pytest.mark.unit
    def test_get_announcements_returns_list(self, test_client, mock_database):
        """Test that GET /announcements returns a list"""
        response = test_client.get("/announcements")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.unit
    def test_get_announcements_with_active_only_true(self, test_client, mock_database):
        """Test that active_only=true filters expired announcements (State Transition Testing)"""
        response = test_client.get("/announcements?active_only=true")

        assert response.status_code == 200
        data = response.json()

        # All returned announcements should be within valid date range
        today = datetime.now().date().isoformat()
        for announcement in data:
            if 'start_date' in announcement:
                assert announcement['start_date'] <= today
            assert announcement['expiration_date'] >= today

    @pytest.mark.unit
    def test_get_announcements_with_active_only_false(self, test_client, mock_database):
        """Test that active_only=false returns all announcements"""
        response = test_client.get("/announcements?active_only=false")

        assert response.status_code == 200
        data = response.json()

        # Should return all announcements regardless of date
        assert len(data) >= 1

    @pytest.mark.unit
    def test_announcement_has_correct_schema(self, test_client, mock_database):
        """Test that announcements have correct schema (Equivalence Partitioning)"""
        response = test_client.get("/announcements")
        data = response.json()

        if len(data) > 0:
            announcement = data[0]
            assert 'id' in announcement  # ObjectId converted to string
            assert 'message' in announcement
            assert 'expiration_date' in announcement

    @pytest.mark.unit
    def test_announcement_id_is_string(self, test_client, mock_database):
        """Test that announcement ID is a string (not ObjectId)"""
        response = test_client.get("/announcements")
        data = response.json()

        for announcement in data:
            assert isinstance(announcement['id'], str)
            assert len(announcement['id']) > 0


class TestCreateAnnouncement:
    """Test POST /announcements endpoint"""

    @pytest.mark.unit
    @pytest.mark.security
    def test_create_announcement_requires_authentication(self, test_client, mock_database):
        """Test that creation requires teacher_username"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Test announcement",
                "expiration_date": "2025-12-31"
            }
        )

        assert response.status_code == 401
        assert "Authentication required" in response.json()['detail']

    @pytest.mark.unit
    @pytest.mark.security
    def test_create_announcement_with_invalid_teacher(self, test_client, mock_database):
        """Test that creation fails with invalid teacher"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Test announcement",
                "expiration_date": "2025-12-31",
                "teacher_username": "invalid_teacher"
            }
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_create_announcement_success(self, test_client, mock_database):
        """Test successful announcement creation"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Winter Break starts on December 25",
                "expiration_date": "2026-01-05",
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert data['message'] == "Winter Break starts on December 25"
        assert data['expiration_date'] == "2026-01-05"

    @pytest.mark.unit
    def test_create_announcement_with_start_date(self, test_client, mock_database):
        """Test announcement creation with start_date (State Transition Testing)"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Future announcement",
                "start_date": "2025-12-31",
                "expiration_date": "2026-01-10",
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['start_date'] == "2025-12-31"

    @pytest.mark.unit
    def test_create_announcement_invalid_date_format(self, test_client, mock_database):
        """Test that invalid date format is rejected (Boundary Value Analysis)"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Test",
                "expiration_date": "2025-13-45",  # Invalid month and day
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 400
        assert "Invalid date format" in response.json()['detail']

    @pytest.mark.unit
    def test_create_announcement_start_after_expiration(self, test_client, mock_database):
        """Test that start_date > expiration_date is rejected (Decision Table Testing)"""
        response = test_client.post(
            "/announcements",
            params={
                "message": "Test",
                "start_date": "2026-01-05",
                "expiration_date": "2025-12-31",  # Before start_date
                "teacher_username": "ms_rodriguez"
            }
        )

        assert response.status_code == 400
        assert "Start date cannot be after expiration date" in response.json()['detail']

    @pytest.mark.unit
    def test_create_announcement_updates_database(self, test_client, mock_database):
        """Test that announcement is actually saved to database"""
        message = "Database test announcement"
        response = test_client.post(
            "/announcements",
            params={
                "message": message,
                "expiration_date": "2025-12-31",
                "teacher_username": "ms_rodriguez"
            }
        )

        announcement_id = response.json()['id']

        # Verify in database
        from bson import ObjectId
        announcement = mock_database['announcements'].find_one(
            {"_id": ObjectId(announcement_id)}
        )
        assert announcement is not None
        assert announcement['message'] == message


class TestUpdateAnnouncement:
    """Test PUT /announcements/{id} endpoint"""

    @pytest.mark.unit
    def test_update_announcement_message(self, test_client, mock_database):
        """Test updating announcement message"""
        # Create announcement
        create_response = test_client.post(
            "/announcements",
            params={
                "message": "Original message",
                "expiration_date": "2025-12-31",
                "teacher_username": "ms_rodriguez"
            }
        )
        announcement_id = create_response.json()['id']

        # Update announcement with JSON body
        updated_message = "Updated message"
        response = test_client.put(
            f"/announcements/{announcement_id}?teacher_username=ms_rodriguez",
            json={
                "message": updated_message
            }
        )

        assert response.status_code == 200

        # Verify update in response
        updated_data = response.json()
        assert updated_data['message'] == updated_message
        assert updated_data['id'] == announcement_id

        # Verify update in database
        from bson import ObjectId
        db_announcement = mock_database['announcements'].find_one(
            {"_id": ObjectId(announcement_id)}
        )
        assert db_announcement is not None
        assert db_announcement['message'] == updated_message

    @pytest.mark.unit
    @pytest.mark.security
    def test_update_announcement_requires_authentication(self, test_client, mock_database):
        """Test that update requires authentication"""
        response = test_client.put(
            "/announcements/fake_id",
            json={
                "message": "Updated message"
            }
        )

        assert response.status_code == 401


class TestDeleteAnnouncement:
    """Test DELETE /announcements/{id} endpoint"""

    @pytest.mark.unit
    def test_delete_announcement(self, test_client, mock_database):
        """Test successful announcement deletion"""
        # Create announcement
        create_response = test_client.post(
            "/announcements",
            params={
                "message": "To be deleted",
                "expiration_date": "2025-12-31",
                "teacher_username": "ms_rodriguez"
            }
        )
        announcement_id = create_response.json()['id']

        # Delete announcement
        response = test_client.delete(
            f"/announcements/{announcement_id}",
            params={"teacher_username": "ms_rodriguez"}
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_delete_nonexistent_announcement(self, test_client, mock_database):
        """Test deletion of nonexistent announcement (Edge Case)"""
        from bson import ObjectId
        fake_id = str(ObjectId())

        response = test_client.delete(
            f"/announcements/{fake_id}",
            params={"teacher_username": "ms_rodriguez"}
        )

        assert response.status_code == 404

    @pytest.mark.unit
    @pytest.mark.security
    def test_delete_requires_authentication(self, test_client, mock_database):
        """Test that deletion requires authentication"""
        from bson import ObjectId
        fake_id = str(ObjectId())

        response = test_client.delete(f"/announcements/{fake_id}")

        assert response.status_code == 401


class TestAnnouncementDateLogic:
    """Test announcement date visibility logic (State Transition Testing)"""

    @pytest.mark.unit
    def test_announcement_visibility_today_equals_start_date(self, test_client, mock_database):
        """Test that announcement is visible when today equals start_date"""
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()

        test_client.post(
            "/announcements",
            params={
                "message": "Today's announcement",
                "start_date": today,
                "expiration_date": tomorrow,
                "teacher_username": "ms_rodriguez"
            }
        )

        response = test_client.get("/announcements?active_only=true")
        data = response.json()

        messages = [a['message'] for a in data]
        assert "Today's announcement" in messages

    @pytest.mark.unit
    def test_announcement_visibility_today_equals_expiration_date(self, test_client, mock_database):
        """Test that announcement is visible when today equals expiration_date"""
        today = datetime.now().date().isoformat()

        test_client.post(
            "/announcements",
            params={
                "message": "Today expires",
                "expiration_date": today,
                "teacher_username": "ms_rodriguez"
            }
        )

        response = test_client.get("/announcements?active_only=true")
        data = response.json()

        messages = [a['message'] for a in data]
        assert "Today expires" in messages
