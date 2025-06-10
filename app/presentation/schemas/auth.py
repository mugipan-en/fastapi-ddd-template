"""Authentication API schemas."""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=1, description="User password")


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")
    first_name: str = Field(min_length=1, max_length=100, description="User first name")
    last_name: str = Field(min_length=1, max_length=100, description="User last name")


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: "UserInfo" = Field(description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str = Field(description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str = Field(description="Current password")
    new_password: str = Field(min_length=8, description="New password")


class UserInfo(BaseModel):
    """User information in token response."""
    id: int = Field(description="User ID")
    email: str = Field(description="User email")
    full_name: str = Field(description="User full name")
    role: str = Field(description="User role")
    is_verified: bool = Field(description="User verification status")