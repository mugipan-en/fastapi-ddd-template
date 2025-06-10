"""Domain repositories package."""

from .user import UserRepository
from .post import PostRepository

__all__ = ["UserRepository", "PostRepository"]