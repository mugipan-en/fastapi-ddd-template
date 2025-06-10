"""Domain repositories package."""

from .post import PostRepository
from .user import UserRepository

__all__ = ["PostRepository", "UserRepository"]
