"""User use cases."""

from typing import Any

from app.domain.entities.user import User, UserCreate, UserRole, UserUpdate
from app.domain.repositories.user import UserRepository
from app.domain.services.user import UserService


class UserUseCases:
    """User use cases."""

    def __init__(self, user_service: UserService, user_repository: UserRepository):
        self.user_service = user_service
        self.user_repository = user_repository

    async def create_user(
        self, user_data: UserCreate, admin_user_id: int | None = None
    ) -> User:
        """Create a new user."""
        # If admin_user_id is provided, check admin permissions for role assignment
        if admin_user_id and user_data.role != UserRole.USER:
            admin_user = await self.user_repository.get_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                raise PermissionError("Only admins can assign non-user roles")

        return await self.user_service.create_user(user_data)

    async def get_user_by_id(self, user_id: int, requester_id: int) -> User | None:
        """Get user by ID with privacy checks."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        # Users can view their own profile, admins can view any profile
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester:
            return None

        if user_id != requester_id and not requester.is_admin():
            # Return limited public information for non-admin users
            return self._get_public_user_info(user)

        return user

    async def get_all_users(
        self, requester_id: int, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get all users (admin only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_admin():
            raise PermissionError("Only admins can view all users")

        return await self.user_repository.get_all(skip, limit)

    async def update_user(
        self, user_id: int, user_data: UserUpdate, requester_id: int
    ) -> User | None:
        """Update user information."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester:
            raise ValueError("Requester not found")

        # Users can update their own profile, admins can update any profile
        if user_id != requester_id and not requester.is_admin():
            raise PermissionError("Users can only update their own profile")

        # Only admins can change roles
        if user_data.role is not None and not requester.is_admin():
            raise PermissionError("Only admins can change user roles")

        # Only admins can change active status
        if user_data.is_active is not None and not requester.is_admin():
            raise PermissionError("Only admins can change user active status")

        return await self.user_repository.update(user_id, user_data)

    async def delete_user(self, user_id: int, requester_id: int) -> bool:
        """Delete user (admin only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_admin():
            raise PermissionError("Only admins can delete users")

        # Prevent admins from deleting themselves
        if user_id == requester_id:
            raise ValueError("Admins cannot delete their own account")

        return await self.user_repository.delete(user_id)

    async def deactivate_user(self, user_id: int, admin_user_id: int) -> bool:
        """Deactivate user account (admin only)."""
        return await self.user_service.deactivate_user(user_id, admin_user_id)

    async def get_users_by_role(
        self, role: UserRole, requester_id: int, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get users by role (admin/moderator only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_moderator():
            raise PermissionError("Only moderators and admins can view users by role")

        return await self.user_repository.get_by_role(role, skip, limit)

    async def get_user_statistics(self, requester_id: int) -> dict[str, Any]:
        """Get user statistics (admin only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_admin():
            raise PermissionError("Only admins can view user statistics")

        total_users = await self.user_repository.count()
        admin_users = await self.user_repository.get_by_role(UserRole.ADMIN)
        moderator_users = await self.user_repository.get_by_role(UserRole.MODERATOR)
        regular_users = await self.user_repository.get_by_role(UserRole.USER)

        return {
            "total_users": total_users,
            "admin_count": len(admin_users),
            "moderator_count": len(moderator_users),
            "user_count": len(regular_users),
            "role_distribution": {
                "admin": len(admin_users),
                "moderator": len(moderator_users),
                "user": len(regular_users),
            },
        }

    async def search_users(
        self, query: str, requester_id: int, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Search users by name or email (admin/moderator only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_moderator():
            raise PermissionError("Only moderators and admins can search users")

        # Get all users and filter by query
        all_users = await self.user_repository.get_all(
            0, 1000
        )  # Get more users for search

        query_lower = query.lower()
        filtered_users = [
            user
            for user in all_users
            if (
                query_lower in user.first_name.lower()
                or query_lower in user.last_name.lower()
                or query_lower in user.email.lower()
            )
        ]

        # Apply pagination
        return filtered_users[skip : skip + limit]

    def _get_public_user_info(self, user: User) -> User:
        """Get public user information (limited fields)."""
        # Return a user object with limited public information
        public_user = User(
            id=user.id,
            email="",  # Hide email
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            hashed_password="",  # Hide password
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=None,  # Hide last login
        )
        return public_user
