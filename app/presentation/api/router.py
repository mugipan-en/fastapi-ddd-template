"""Main API router."""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    posts_router,
    prefix="/posts", 
    tags=["posts"]
)