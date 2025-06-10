"""Post repository interface."""

from abc import ABC, abstractmethod

from app.domain.entities.post import Post, PostCreate, PostStatus, PostUpdate


class PostRepository(ABC):
    """Post repository interface."""

    @abstractmethod
    async def create(self, post_data: PostCreate, user_id: int) -> Post:
        """Create a new post."""
        pass

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Post | None:
        """Get post by ID."""
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Post | None:
        """Get post by slug."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all posts with pagination."""
        pass

    @abstractmethod
    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by user."""
        pass

    @abstractmethod
    async def get_by_status(
        self, status: PostStatus, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by status."""
        pass

    @abstractmethod
    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get published posts."""
        pass

    @abstractmethod
    async def update(self, post_id: int, post_data: PostUpdate) -> Post | None:
        """Update post."""
        pass

    @abstractmethod
    async def delete(self, post_id: int) -> bool:
        """Delete post."""
        pass

    @abstractmethod
    async def publish(self, post_id: int) -> Post | None:
        """Publish post."""
        pass

    @abstractmethod
    async def archive(self, post_id: int) -> Post | None:
        """Archive post."""
        pass

    @abstractmethod
    async def increment_view_count(self, post_id: int) -> None:
        """Increment post view count."""
        pass

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[Post]:
        """Search posts by title and content."""
        pass

    @abstractmethod
    async def get_by_tags(
        self, tags: list[str], skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by tags."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get total post count."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: int) -> int:
        """Get post count by user."""
        pass

    @abstractmethod
    async def count_by_status(self, status: PostStatus) -> int:
        """Get post count by status."""
        pass
