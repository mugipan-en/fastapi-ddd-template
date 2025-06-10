"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities.user import User, UserCreate, UserUpdate


class UserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        pass
    
    @abstractmethod
    async def verify_user(self, user_id: int) -> Optional[User]:
        """Verify user account."""
        pass
    
    @abstractmethod
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user account."""
        pass
    
    @abstractmethod
    async def get_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total user count."""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass