"""Posts API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.post import PostUseCases
from app.domain.entities.user import User
from app.domain.entities.post import PostStatus
from app.domain.services.post import PostService
from app.infrastructure.repositories.post import SQLPostRepository
from app.infrastructure.repositories.user import SQLUserRepository
from app.presentation.dependencies.auth import get_current_active_user, get_optional_current_user
from app.presentation.dependencies.database import get_db_session
from app.presentation.schemas.post import (
    PostResponse,
    PostCreateRequest,
    PostUpdateRequest,
    PostStatsResponse
)
from app.presentation.schemas.common import PaginatedResponse, SuccessResponse

router = APIRouter()


async def get_post_use_cases(session: AsyncSession = Depends(get_db_session)) -> PostUseCases:
    """Get post use cases dependency."""
    post_repository = SQLPostRepository(session)
    user_repository = SQLUserRepository(session)
    post_service = PostService(post_repository, user_repository)
    return PostUseCases(post_service, post_repository, user_repository)


@router.post("", response_model=PostResponse)
async def create_post(
    post_data: PostCreateRequest,
    current_user: User = Depends(get_current_active_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Create a new post.
    
    Requires authentication.
    """
    try:
        from app.domain.entities.post import PostCreate
        create_data = PostCreate(**post_data.model_dump())
        post = await post_use_cases.create_post(create_data, current_user.id)
        return PostResponse.model_validate(post)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaginatedResponse[PostResponse])
async def get_all_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Get all posts.
    
    Authenticated users can see all posts.
    Anonymous users only see published posts.
    """
    skip = (page - 1) * size
    user_id = current_user.id if current_user else None
    posts = await post_use_cases.get_all_posts(skip, size, user_id)
    
    total = len(posts)  # Simplified count
    post_responses = [PostResponse.model_validate(post) for post in posts]
    
    return PaginatedResponse.create(
        items=post_responses,
        total=total,
        page=page,
        size=size
    )


@router.get("/stats", response_model=PostStatsResponse)
async def get_post_statistics(
    current_user: User = Depends(get_current_active_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Get post statistics.
    
    Requires authentication with moderator privileges.
    """
    try:
        stats = await post_use_cases.get_post_statistics(current_user.id)
        return PostStatsResponse(**stats)
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
    post_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Get post by ID.
    
    Increments view count for published posts.
    Only owners and moderators can view unpublished posts.
    """
    user_id = current_user.id if current_user else None
    post = await post_use_cases.get_post_by_id(post_id, user_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Update post.
    
    Only post owners and moderators can edit posts.
    Requires authentication.
    """
    try:
        from app.domain.entities.post import PostUpdate
        update_data = PostUpdate(**post_data.model_dump(exclude_unset=True))
        updated_post = await post_use_cases.update_post(post_id, update_data, current_user.id)
        
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return PostResponse.model_validate(updated_post)
    
    except (PermissionError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{post_id}", response_model=SuccessResponse)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Delete post.
    
    Only post owners and admins can delete posts.
    Requires authentication.
    """
    try:
        success = await post_use_cases.delete_post(post_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return SuccessResponse(message="Post deleted successfully")
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    post_use_cases: PostUseCases = Depends(get_post_use_cases)
):
    """
    Publish post.
    
    Only post owners and moderators can publish posts.
    Requires authentication.
    """
    try:
        published_post = await post_use_cases.publish_post(post_id, current_user.id)
        
        if not published_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return PostResponse.model_validate(published_post)
    
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )