"""Post entity."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class PostStatus(str, Enum):
    """Post status."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PostBase(SQLModel):
    """Base post model."""

    title: str = Field(max_length=200)
    content: str = Field(max_length=10000)
    status: PostStatus = Field(default=PostStatus.DRAFT)
    tags: str | None = Field(default=None, max_length=500)


class Post(PostBase, table=True):
    """Post entity."""

    __tablename__ = "posts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    slug: str = Field(unique=True, index=True, max_length=250)
    excerpt: str | None = Field(default=None, max_length=500)
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)
    published_at: datetime | None = Field(default=None)

    # Relationships
    author: "User" = Relationship(back_populates="posts")

    @property
    def is_published(self) -> bool:
        """Check if post is published."""
        return self.status == PostStatus.PUBLISHED

    @property
    def is_draft(self) -> bool:
        """Check if post is draft."""
        return self.status == PostStatus.DRAFT

    @property
    def word_count(self) -> int:
        """Get word count of content."""
        return len(self.content.split())

    @property
    def reading_time(self) -> int:
        """Estimate reading time in minutes (250 words per minute)."""
        return max(1, self.word_count // 250)

    def publish(self) -> None:
        """Publish the post."""
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the post."""
        self.status = PostStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1


class PostCreate(PostBase):
    """Post creation model."""

    pass


class PostUpdate(SQLModel):
    """Post update model."""

    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=10000)
    status: PostStatus | None = Field(default=None)
    tags: str | None = Field(default=None, max_length=500)
    excerpt: str | None = Field(default=None, max_length=500)


class PostResponse(PostBase):
    """Post response model."""

    id: int
    user_id: int
    slug: str
    excerpt: str | None
    view_count: int
    created_at: datetime
    updated_at: datetime | None
    published_at: datetime | None
    word_count: int
    reading_time: int


class PostWithAuthor(PostResponse):
    """Post response with author information."""

    author: "UserResponse"


# Import to resolve forward references
from .user import UserResponse

PostWithAuthor.model_rebuild()
