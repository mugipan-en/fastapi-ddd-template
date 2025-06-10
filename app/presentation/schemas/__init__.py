"""API schemas package."""

from .auth import TokenResponse, LoginRequest, RegisterRequest
from .user import UserResponse, UserCreateRequest, UserUpdateRequest
from .post import PostResponse, PostCreateRequest, PostUpdateRequest, PostWithAuthorResponse
from .common import PaginatedResponse, ErrorResponse

__all__ = [
    "TokenResponse",
    "LoginRequest", 
    "RegisterRequest",
    "UserResponse",
    "UserCreateRequest",
    "UserUpdateRequest",
    "PostResponse",
    "PostCreateRequest",
    "PostUpdateRequest",
    "PostWithAuthorResponse",
    "PaginatedResponse",
    "ErrorResponse",
]