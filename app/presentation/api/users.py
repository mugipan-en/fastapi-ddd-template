"""Users API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user import UserUseCases
from app.domain.entities.user import User
from app.domain.services.user import UserService
from app.infrastructure.repositories.user import SQLUserRepository
from app.presentation.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user,
)
from app.presentation.dependencies.database import get_db_session
from app.presentation.schemas.common import PaginatedResponse, SuccessResponse
from app.presentation.schemas.user import (
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)

router = APIRouter()


async def get_user_use_cases(
    session: AsyncSession = Depends(get_db_session),
) -> UserUseCases:
    """Get user use cases dependency."""
    user_repository = SQLUserRepository(session)
    user_service = UserService(user_repository)
    return UserUseCases(user_service, user_repository)


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile.

    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Update current user profile.

    Users can only update their own profile.
    Role changes require admin privileges.

    Requires authentication.
    """
    try:
        updated_user = await user_use_cases.update_user(
            current_user.id, user_data, current_user.id
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse.model_validate(updated_user)

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=PaginatedResponse[UserResponse])
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_admin_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get all users (admin only).

    Requires admin authentication.
    """
    skip = (page - 1) * size
    users = await user_use_cases.get_all_users(current_user.id, skip, size)

    # Get total count for pagination

    # This is simplified - in production you'd inject this properly
    total = len(users)  # Simplified count

    user_responses = [UserResponse.model_validate(user) for user in users]

    return PaginatedResponse.create(
        items=user_responses, total=total, page=page, size=size
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    current_user: User = Depends(get_current_admin_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get user statistics (admin only).

    Requires admin authentication.
    """
    stats = await user_use_cases.get_user_statistics(current_user.id)
    return UserStatsResponse(**stats)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Get user by ID.

    Users can view their own profile.
    Admins can view any profile.

    Requires authentication.
    """
    user = await user_use_cases.get_user_by_id(user_id, current_user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Delete user (admin only).

    Requires admin authentication.
    """
    try:
        success = await user_use_cases.delete_user(user_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return SuccessResponse(message="User deleted successfully")

    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
