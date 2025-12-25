"""Unit tests for authentication router endpoints"""

import pytest
from fastapi.testclient import TestClient
from app import app



class TestTeacherLogin:
    """Test POST /auth/login endpoint"""

    @pytest.mark.unit
    @pytest.mark.security
    def test_login_with_valid_credentials(self, test_client, mock_database):
        """Test successful login with valid credentials"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": "SecurePass123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['username'] == "ms_rodriguez"
        assert data['display_name'] == "Ms. Rodriguez"
        assert data['role'] == "teacher"
        assert 'password' not in data  # Password should not be returned

    @pytest.mark.unit
    @pytest.mark.security
    def test_login_with_invalid_password(self, test_client, mock_database):
        """Test login fails with wrong password (Boundary Value Analysis)"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": "WrongPassword"
            }
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()['detail']

    @pytest.mark.unit
    @pytest.mark.security
    def test_login_with_nonexistent_user(self, test_client, mock_database):
        """Test login fails for nonexistent user"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "nonexistent_teacher",
                "password": "AnyPassword123"
            }
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()['detail']

    @pytest.mark.unit
    @pytest.mark.security
    def test_login_with_empty_password(self, test_client, mock_database):
        """Test login fails with empty password (Edge Case)"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": ""
            }
        )

        assert response.status_code == 401

    @pytest.mark.unit
    @pytest.mark.security
    def test_login_password_case_sensitive(self, test_client, mock_database):
        """Test that password is case-sensitive"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": "securepass123"  # lowercase, should fail
            }
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_login_returns_all_required_fields(self, test_client, mock_database):
        """Test that login response includes all required fields"""
        response = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": "SecurePass123"
            }
        )

        data = response.json()
        assert 'username' in data
        assert 'display_name' in data
        assert 'role' in data


class TestCheckSession:
    """Test GET /auth/check-session endpoint"""

    @pytest.mark.unit
    def test_check_session_valid_user(self, test_client, mock_database):
        """Test session check for valid user"""
        response = test_client.get(
            "/auth/check-session",
            params={"username": "ms_rodriguez"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['username'] == "ms_rodriguez"
        assert data['display_name'] == "Ms. Rodriguez"
        assert data['role'] == "teacher"

    @pytest.mark.unit
    def test_check_session_invalid_user(self, test_client, mock_database):
        """Test session check for nonexistent user"""
        response = test_client.get(
            "/auth/check-session",
            params={"username": "nonexistent_teacher"}
        )

        assert response.status_code == 404
        assert "Teacher not found" in response.json()['detail']

    @pytest.mark.unit
    def test_check_session_multiple_users(self, test_client, mock_database):
        """Test session check works for multiple teachers"""
        usernames = ["ms_rodriguez", "mr_smith"]

        for username in usernames:
            response = test_client.get(
                "/auth/check-session",
                params={"username": username}
            )
            assert response.status_code == 200
            assert response.json()['username'] == username

    @pytest.mark.unit
    def test_check_session_returns_no_password(self, test_client, mock_database):
        """Test that session check does not return password"""
        response = test_client.get(
            "/auth/check-session",
            params={"username": "ms_rodriguez"}
        )

        data = response.json()
        assert 'password' not in data


class TestAuthenticationScenarios:
    """Test authentication scenarios (Decision Table Testing)"""

    @pytest.mark.unit
    @pytest.mark.security
    def test_auth_decision_table(self, test_client, mock_database):
        """Test authentication decision table combinations"""
        scenarios = [
            # (username, password, expected_status)
            ("ms_rodriguez", "SecurePass123", 200),
            ("ms_rodriguez", "WrongPass", 401),
            ("invalid_user", "AnyPass", 401),
            ("", "AnyPass", 401),
            ("", "SecurePass123", 401),  # Empty username with valid password
        ]

        for username, password, expected_status in scenarios:
            response = test_client.post(
                "/auth/login",
                params={
                    "username": username,
                    "password": password
                }
            )
            assert response.status_code == expected_status


class TestAuthenticationSecurity:
    """Test security aspects of authentication"""

    @pytest.mark.unit
    @pytest.mark.security
    def test_no_password_disclosure_on_login_failure(self, test_client, mock_database):
        """Test that failed login doesn't disclose whether user exists"""
        # Both should return same error message
        response1 = test_client.post(
            "/auth/login",
            params={
                "username": "nonexistent_user",
                "password": "AnyPassword"
            }
        )

        response2 = test_client.post(
            "/auth/login",
            params={
                "username": "ms_rodriguez",
                "password": "WrongPassword"
            }
        )

        # Both should return 401 with same error message
        assert response1.status_code == 401
        assert response2.status_code == 401
        assert response1.json()['detail'] == response2.json()['detail']

    @pytest.mark.unit
    @pytest.mark.security
    def test_password_never_returned_in_response(self, test_client, mock_database):
        """Test that password is never returned in any auth response"""
        endpoints = [
            ("/auth/login", "post", {"username": "ms_rodriguez", "password": "SecurePass123"}),
            ("/auth/check-session", "get", {"username": "ms_rodriguez"}),
        ]

        for endpoint, method, params in endpoints:
            if method == "post":
                response = test_client.post(endpoint, params=params)
            else:
                response = test_client.get(endpoint, params=params)

            if response.status_code == 200:
                assert 'password' not in response.json()
