"""Tests for authentication endpoints."""

import pytest
from backend.tests.conftest import client


class TestRegistration:
    """Test user registration."""
    
    def test_register_success(self):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        # First registration
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "user1",
                "password": "Pass123456"
            }
        )
        # Second registration with same email
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "user2",
                "password": "Pass123456"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "username": "samename",
                "password": "Pass123456"
            }
        )
        response = client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "username": "samename",
                "password": "Pass123456"
            }
        )
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]


class TestLogin:
    """Test user login."""
    
    def test_login_success(self, test_user_creds):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={"username": test_user_creds["username"], "password": "TestPass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["id"] == test_user_creds["user"]["id"]

    def test_login_invalid_username(self):
        """Test login with invalid username."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401

    def test_login_invalid_password(self, test_user_creds):
        """Test login with invalid password."""
        response = client.post(
            "/auth/login",
            json={"username": test_user_creds["username"], "password": "WrongPassword"}
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, test_user_creds):
        """Test login with inactive user."""
        # Get the user from database and deactivate them
        from backend.app.models.models import User
        from backend.tests.conftest import TestingSessionLocal
        
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.username == test_user_creds["username"]).first()
            if user:
                user.is_active = False
                db.commit()
        finally:
            db.close()
            
        response = client.post(
            "/auth/login",
            json={"username": test_user_creds["username"], "password": "TestPass123"}
        )
        assert response.status_code == 401


class TestAuthProtection:
    """Test authentication protection."""
    
    def test_get_me_without_auth(self):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_get_me_with_valid_token(self, test_user_token, test_user_creds):
        """Test getting current user with valid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user_creds["user"]["id"]
        assert data["username"] == test_user_creds["username"]
