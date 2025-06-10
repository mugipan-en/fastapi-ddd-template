"""API schemas package."""

from .auth import LoginRequest, RegisterRequest, TokenResponse
from .common import ErrorResponse, PaginatedResponse
from .post import (
    PostCreateRequest,
    PostResponse,
    PostUpdateRequest,
    PostWithAuthorResponse,
)
from .user import UserCreateRequest, UserResponse, UserUpdateRequest

__all__ = [
    "ErrorResponse",
    "LoginRequest",
    "PaginatedResponse",
    "PostCreateRequest",
    "PostResponse",
    "PostUpdateRequest",
    "PostWithAuthorResponse",
    "RegisterRequest",
    "TokenResponse",
    "UserCreateRequest",
    "UserResponse",
    "UserUpdateRequest",
]
