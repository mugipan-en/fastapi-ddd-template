"""User domain service."""

import re

from app.core.security import get_password_hash, verify_password
from app.domain.entities.user import User, UserCreate
from app.domain.repositories.user import UserRepository


class UserService:
    """User domain service."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with validation."""
        # Validate email format
        if not self._is_valid_email(user_data.email):
            raise ValueError("Invalid email format")

        # Check if user already exists
        if await self.user_repository.exists_by_email(user_data.email):
            raise ValueError("User with this email already exists")

        # Validate password strength
        if not self._is_strong_password(user_data.password):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number"
            )

        # Hash password
        user_data_dict = user_data.model_dump()
        user_data_dict["hashed_password"] = get_password_hash(user_data.password)
        del user_data_dict["password"]

        # Create user
        user_create = UserCreate.model_validate(user_data_dict)
        return await self.user_repository.create(user_create)

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False

        # Verify current password
        if not self._verify_password(current_password, user.hashed_password):
            return False

        # Validate new password
        if not self._is_strong_password(new_password):
            raise ValueError("New password does not meet requirements")

        # Update password
        from app.domain.entities.user import UserUpdate

        user_update = UserUpdate(hashed_password=get_password_hash(new_password))
        await self.user_repository.update(user_id, user_update)
        return True

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return verify_password(plain_password, hashed_password)

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _is_strong_password(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True

    async def deactivate_user(self, user_id: int, admin_user_id: int) -> bool:
        """Deactivate user (admin only)."""
        admin_user = await self.user_repository.get_by_id(admin_user_id)
        if not admin_user or not admin_user.is_admin():
            raise PermissionError("Only admins can deactivate users")

        user = await self.user_repository.deactivate_user(user_id)
        return user is not None

    async def verify_user(self, user_id: int) -> bool:
        """Verify user account."""
        user = await self.user_repository.verify_user(user_id)
        return user is not None
