"""User API schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from app.domain.entities.user import UserRole


class UserResponse(BaseModel):
    """User response schema."""
    id: int = Field(description="User ID")
    email: str = Field(description="User email address")
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")
    full_name: str = Field(description="User full name")
    role: UserRole = Field(description="User role")
    is_active: bool = Field(description="User active status")
    is_verified: bool = Field(description="User verification status")
    created_at: datetime = Field(description="User creation timestamp")
    updated_at: Optional[datetime] = Field(description="User last update timestamp")
    last_login: Optional[datetime] = Field(description="User last login timestamp")

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """User creation request schema."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")
    first_name: str = Field(min_length=1, max_length=100, description="User first name")
    last_name: str = Field(min_length=1, max_length=100, description="User last name")
    role: Optional[UserRole] = Field(default=UserRole.USER, description="User role")


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    email: Optional[EmailStr] = Field(default=None, description="User email address")
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="User first name")
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="User last name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    is_active: Optional[bool] = Field(default=None, description="User active status")
    is_verified: Optional[bool] = Field(default=None, description="User verification status")


class UserPublicResponse(BaseModel):
    """Public user response schema (limited information)."""
    id: int = Field(description="User ID")
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")
    full_name: str = Field(description="User full name")
    role: UserRole = Field(description="User role")
    is_verified: bool = Field(description="User verification status")
    created_at: datetime = Field(description="User creation timestamp")

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """User statistics response schema."""
    total_users: int = Field(description="Total number of users")
    admin_count: int = Field(description="Number of admin users")
    moderator_count: int = Field(description="Number of moderator users")
    user_count: int = Field(description="Number of regular users")
    role_distribution: dict = Field(description="User distribution by role")