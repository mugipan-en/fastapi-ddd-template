"""Post API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.post import PostStatus
from app.presentation.schemas.user import UserPublicResponse


class PostResponse(BaseModel):
    """Post response schema."""

    id: int = Field(description="Post ID")
    title: str = Field(description="Post title")
    content: str = Field(description="Post content")
    slug: str = Field(description="Post URL slug")
    excerpt: str | None = Field(description="Post excerpt")
    status: PostStatus = Field(description="Post status")
    tags: str | None = Field(description="Post tags")
    view_count: int = Field(description="Post view count")
    word_count: int = Field(description="Post word count")
    reading_time: int = Field(description="Estimated reading time in minutes")
    user_id: int = Field(description="Author user ID")
    created_at: datetime = Field(description="Post creation timestamp")
    updated_at: datetime | None = Field(description="Post last update timestamp")
    published_at: datetime | None = Field(description="Post publication timestamp")

    class Config:
        from_attributes = True


class PostWithAuthorResponse(PostResponse):
    """Post response with author information."""

    author: UserPublicResponse = Field(description="Post author information")

    class Config:
        from_attributes = True


class PostCreateRequest(BaseModel):
    """Post creation request schema."""

    title: str = Field(min_length=1, max_length=200, description="Post title")
    content: str = Field(min_length=1, max_length=10000, description="Post content")
    status: PostStatus | None = Field(
        default=PostStatus.DRAFT, description="Post status"
    )
    tags: str | None = Field(default=None, max_length=500, description="Post tags")


class PostUpdateRequest(BaseModel):
    """Post update request schema."""

    title: str | None = Field(
        default=None, min_length=1, max_length=200, description="Post title"
    )
    content: str | None = Field(
        default=None, min_length=1, max_length=10000, description="Post content"
    )
    status: PostStatus | None = Field(default=None, description="Post status")
    tags: str | None = Field(default=None, max_length=500, description="Post tags")
    excerpt: str | None = Field(
        default=None, max_length=500, description="Post excerpt"
    )


class PostSummaryResponse(BaseModel):
    """Post summary response schema (for lists)."""

    id: int = Field(description="Post ID")
    title: str = Field(description="Post title")
    slug: str = Field(description="Post URL slug")
    excerpt: str | None = Field(description="Post excerpt")
    status: PostStatus = Field(description="Post status")
    view_count: int = Field(description="Post view count")
    reading_time: int = Field(description="Estimated reading time in minutes")
    created_at: datetime = Field(description="Post creation timestamp")
    published_at: datetime | None = Field(description="Post publication timestamp")

    class Config:
        from_attributes = True


class PostStatsResponse(BaseModel):
    """Post statistics response schema."""

    total_posts: int = Field(description="Total number of posts")
    published_count: int = Field(description="Number of published posts")
    draft_count: int = Field(description="Number of draft posts")
    archived_count: int = Field(description="Number of archived posts")
    status_distribution: dict = Field(description="Post distribution by status")


class PostSearchResponse(BaseModel):
    """Post search response schema."""

    posts: list[PostSummaryResponse] = Field(description="Search results")
    query: str = Field(description="Search query")
    total_results: int = Field(description="Total number of results")


class TrendingPostsResponse(BaseModel):
    """Trending posts response schema."""

    posts: list[PostSummaryResponse] = Field(description="Trending posts")
    period_days: int = Field(description="Period in days for trending calculation")
    updated_at: datetime = Field(description="Last updated timestamp")
