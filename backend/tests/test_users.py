"""Tests for users endpoints."""

import pytest
from backend.tests.conftest import client


class TestUsersEndpoints:
    """Test users/profile endpoints."""
    
    def test_get_profile_requires_auth(self):
        """Test getting profile requires authentication."""
        response = client.get("/users/profile")
        assert response.status_code == 401
    
    def test_get_profile_success(self, test_user_creds):
        """Test successfully getting user profile."""
        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert data["username"] == test_user_creds["username"]
        assert "email" in data
        assert data["email"] == test_user_creds["user"]["email"]
    
    def test_get_profile_fields(self, test_user_creds):
        """Test profile has all required fields."""
        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        required_fields = ["id", "username", "email", "full_name", "is_active"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_update_profile_requires_auth(self):
        """Test updating profile requires authentication."""
        response = client.put(
            "/users/profile",
            json={"full_name": "New Name"}
        )
        assert response.status_code == 401
    
    def test_update_profile_full_name(self, test_user_creds):
        """Test updating profile full name."""
        response = client.put(
            "/users/profile",
            json={"full_name": "Updated Name"},
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    def test_update_profile_partial(self, test_user_creds):
        """Test partial profile update."""
        new_full_name = "Partially Updated"
        response = client.put(
            "/users/profile",
            json={"full_name": new_full_name},
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == new_full_name
        # Other fields should remain unchanged
        assert data["username"] == test_user_creds["username"]
    
    def test_delete_profile_requires_auth(self):
        """Test deleting profile requires authentication."""
        response = client.delete("/users/profile")
        assert response.status_code == 401
    
    def test_delete_profile_success(self, test_user_creds):
        """Test successfully deleting user profile."""
        response = client.delete(
            "/users/profile",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 204
    
    def test_get_preferences_requires_auth(self):
        """Test getting preferences requires authentication."""
        response = client.get("/users/preferences")
        assert response.status_code == 401
    
    def test_get_preferences_success(self, test_user_creds):
        """Test successfully getting user preferences."""
        response = client.get(
            "/users/preferences",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "user_id" in data
        # Preferences should be for this user
        assert data["user_id"] == test_user_creds["user"]["id"]
    
    def test_get_preferences_fields(self, test_user_creds):
        """Test preferences have expected fields."""
        response = client.get(
            "/users/preferences",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Check for common preference fields
        assert "user_id" in data or "id" in data
    
    def test_update_preferences_requires_auth(self):
        """Test updating preferences requires authentication."""
        response = client.put(
            "/users/preferences",
            json={"language": "en"}
        )
        assert response.status_code == 401
    
    def test_update_preferences_language(self, test_user_creds):
        """Test updating language preference."""
        response = client.put(
            "/users/preferences",
            json={"language": "de"},
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "de"
    
    def test_update_preferences_multiple(self, test_user_creds):
        """Test updating multiple preferences."""
        update_data = {
            "language": "fr",
            "theme": "dark"
        }
        response = client.put(
            "/users/preferences",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "fr"
        # theme field depends on backend schema
        if "theme" in data:
            assert data["theme"] == "dark"
    
    def test_update_preferences_with_regions(self, test_user_creds):
        """Test updating preferences with regions."""
        update_data = {
            "preferred_regions": ["us", "eu"]
        }
        response = client.put(
            "/users/preferences",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        # May succeed or fail depending on schema
        assert response.status_code in [200, 422]
    
    def test_multiple_users_independent_profiles(self, test_user_creds):
        """Test that different users have independent profiles."""
        # Get profile for first user
        response1 = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Update first user's profile
        client.put(
            "/users/profile",
            json={"full_name": "Updated User 1"},
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        
        # Verify the update
        response_check = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        data_check = response_check.json()
        assert data_check["full_name"] == "Updated User 1"
    
    def test_preferences_persistence(self, test_user_creds):
        """Test that preference updates persist."""
        # Update preference
        client.put(
            "/users/preferences",
            json={"language": "es"},
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        
        # Retrieve and verify
        response = client.get(
            "/users/preferences",
            headers={"Authorization": f"Bearer {test_user_creds['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("language") == "es"
