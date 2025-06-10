"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.auth import AuthUseCases
from app.domain.entities.user import User, UserCreate, UserLogin
from app.domain.services.user import UserService
from app.infrastructure.repositories.user import SQLUserRepository
from app.presentation.dependencies.auth import get_current_active_user
from app.presentation.dependencies.database import get_db_session
from app.presentation.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
)
from app.presentation.schemas.common import SuccessResponse

router = APIRouter()


async def get_auth_use_cases(
    session: AsyncSession = Depends(get_db_session),
) -> AuthUseCases:
    """Get authentication use cases dependency."""
    user_repository = SQLUserRepository(session)
    user_service = UserService(user_repository)
    return AuthUseCases(user_service, user_repository)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Authenticate user and return access tokens.

    - **email**: User email address
    - **password**: User password

    Returns JWT access token and refresh token.
    """
    login_data = UserLogin(email=credentials.email, password=credentials.password)
    result = await auth_use_cases.login(login_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return TokenResponse(**result)


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: RegisterRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Register a new user account.

    - **email**: User email address (must be unique)
    - **password**: User password (minimum 8 characters)
    - **first_name**: User first name
    - **last_name**: User last name

    Returns JWT access token and refresh token.
    """
    try:
        create_data = UserCreate(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        result = await auth_use_cases.register(create_data)
        return TokenResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid JWT refresh token

    Returns new JWT access token.
    """
    result = await auth_use_cases.refresh_token(refresh_data.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return RefreshTokenResponse(**result)


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Change user password.

    - **current_password**: Current user password
    - **new_password**: New password (minimum 8 characters)

    Requires authentication.
    """
    try:
        success = await auth_use_cases.change_password(
            current_user.id, password_data.current_password, password_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        return SuccessResponse(message="Password changed successfully")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Get current authenticated user information.

    Requires authentication.
    """
    user_info = await auth_use_cases.get_current_user_info(current_user.id)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user_info


@router.post("/verify", response_model=SuccessResponse)
async def verify_account(
    current_user: User = Depends(get_current_active_user),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """
    Verify user account.

    This is a simplified verification endpoint.
    In production, you would typically send a verification email
    with a token and verify through that token.

    Requires authentication.
    """
    success = await auth_use_cases.verify_user_account(current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to verify account"
        )

    return SuccessResponse(message="Account verified successfully")
