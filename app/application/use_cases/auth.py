"""Authentication use cases."""

from datetime import timedelta
from typing import Any

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.domain.entities.user import UserCreate, UserLogin
from app.domain.repositories.user import UserRepository
from app.domain.services.user import UserService


class AuthUseCases:
    """Authentication use cases."""

    def __init__(self, user_service: UserService, user_repository: UserRepository):
        self.user_service = user_service
        self.user_repository = user_repository

    async def login(self, credentials: UserLogin) -> dict[str, Any] | None:
        """Authenticate user and return tokens."""
        user = await self.user_service.authenticate_user(
            credentials.email, credentials.password
        )

        if not user:
            return None

        # Update last login
        await self.user_repository.update_last_login(user.id)

        # Create tokens
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        )
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified,
            },
        }

    async def register(self, user_data: UserCreate) -> dict[str, Any]:
        """Register new user and return tokens."""
        # Create user
        user = await self.user_service.create_user(user_data)

        # Create tokens
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        )
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified,
            },
            "message": "User registered successfully",
        }

    async def refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
        """Refresh access token using refresh token."""
        try:
            user_id = verify_refresh_token(refresh_token)
            user = await self.user_repository.get_by_id(int(user_id))

            if not user or not user.is_active:
                return None

            # Create new access token
            access_token = create_access_token(
                subject=user.id,
                expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            }

        except Exception:
            return None

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        return await self.user_service.change_password(
            user_id, current_password, new_password
        )

    async def verify_user_account(self, user_id: int) -> bool:
        """Verify user account."""
        return await self.user_service.verify_user(user_id)

    async def get_current_user_info(self, user_id: int) -> dict[str, Any] | None:
        """Get current user information."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
