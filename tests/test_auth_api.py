"""Authentication API tests."""

import pytest
from httpx import AsyncClient

from app.domain.entities.user import User


class TestAuthAPI:
    """Authentication API test cases."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "first_name": "New",
            "last_name": "User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["full_name"] == "New User"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "email": "newuser@example.com",
            "password": "weak",  # Too short
            "first_name": "New",
            "last_name": "User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        login_data = {"email": test_user.email, "password": "TestPassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self, client: AsyncClient, test_user: User
    ):
        """Test login with invalid credentials."""
        login_data = {"email": test_user.email, "password": "wrongpassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {"email": "nonexistent@example.com", "password": "anypassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {"email": test_user.email, "password": "TestPassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        tokens = response.json()

        # Use refresh token
        refresh_data = {"refresh_token": tokens["refresh_token"]}

        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}

        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test getting current user information."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No authorization header

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful password change."""
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NewTestPassword123",
        }

        response = await client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewTestPassword123",
        }

        response = await client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_change_password_weak_new(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test password change with weak new password."""
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "weak",  # Too short
        }

        response = await client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_verify_account(self, client: AsyncClient, auth_headers: dict):
        """Test account verification."""
        response = await client.post("/api/v1/auth/verify", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Account verified successfully"
