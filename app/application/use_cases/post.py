"""Post use cases."""

from typing import Any

from app.domain.entities.post import Post, PostCreate, PostStatus, PostUpdate
from app.domain.repositories.post import PostRepository
from app.domain.repositories.user import UserRepository
from app.domain.services.post import PostService


class PostUseCases:
    """Post use cases."""

    def __init__(
        self,
        post_service: PostService,
        post_repository: PostRepository,
        user_repository: UserRepository,
    ):
        self.post_service = post_service
        self.post_repository = post_repository
        self.user_repository = user_repository

    async def create_post(self, post_data: PostCreate, user_id: int) -> Post:
        """Create a new post."""
        return await self.post_service.create_post(post_data, user_id)

    async def get_post_by_id(
        self, post_id: int, user_id: int | None = None
    ) -> Post | None:
        """Get post by ID with view count increment for published posts."""
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            return None

        # If post is not published, only allow owner and moderators to view
        if not post.is_published:
            if not user_id:
                return None

            user = await self.user_repository.get_by_id(user_id)
            if not user or (post.user_id != user_id and not user.is_moderator()):
                return None
        else:
            # Increment view count for published posts
            await self.post_repository.increment_view_count(post_id)
            # Get updated post with new view count
            post = await self.post_repository.get_by_id(post_id)

        return post

    async def get_post_by_slug(
        self, slug: str, user_id: int | None = None
    ) -> Post | None:
        """Get post by slug with view count increment."""
        post = await self.post_repository.get_by_slug(slug)
        if not post:
            return None

        # Same access control as get_by_id
        if not post.is_published:
            if not user_id:
                return None

            user = await self.user_repository.get_by_id(user_id)
            if not user or (post.user_id != user_id and not user.is_moderator()):
                return None
        else:
            # Increment view count for published posts
            await self.post_repository.increment_view_count(post.id)
            # Get updated post with new view count
            post = await self.post_repository.get_by_id(post.id)

        return post

    async def get_all_posts(
        self, skip: int = 0, limit: int = 100, user_id: int | None = None
    ) -> list[Post]:
        """Get all posts with filtering based on user permissions."""
        if user_id:
            user = await self.user_repository.get_by_id(user_id)
            if user and user.is_moderator():
                # Moderators can see all posts
                return await self.post_repository.get_all(skip, limit)

        # Regular users and anonymous users only see published posts
        return await self.post_repository.get_published(skip, limit)

    async def get_user_posts(
        self,
        author_id: int,
        requester_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Post]:
        """Get posts by specific user."""
        if requester_id == author_id:
            # Users can see all their own posts
            return await self.post_repository.get_by_user(author_id, skip, limit)

        if requester_id:
            requester = await self.user_repository.get_by_id(requester_id)
            if requester and requester.is_moderator():
                # Moderators can see all posts by any user
                return await self.post_repository.get_by_user(author_id, skip, limit)

        # Others can only see published posts
        user_posts = await self.post_repository.get_by_user(author_id, skip, limit)
        return [post for post in user_posts if post.is_published]

    async def update_post(
        self, post_id: int, post_data: PostUpdate, user_id: int
    ) -> Post | None:
        """Update post."""
        return await self.post_service.update_post(post_id, post_data, user_id)

    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete post."""
        return await self.post_service.delete_post(post_id, user_id)

    async def publish_post(self, post_id: int, user_id: int) -> Post | None:
        """Publish post."""
        return await self.post_service.publish_post(post_id, user_id)

    async def archive_post(self, post_id: int, user_id: int) -> Post | None:
        """Archive post."""
        return await self.post_service.archive_post(post_id, user_id)

    async def search_posts(
        self, query: str, user_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Search posts."""
        return await self.post_service.search_posts(query, user_id, skip, limit)

    async def get_posts_by_status(
        self, status: PostStatus, requester_id: int, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by status (moderator only for non-published status)."""
        if status != PostStatus.PUBLISHED:
            requester = await self.user_repository.get_by_id(requester_id)
            if not requester or not requester.is_moderator():
                raise PermissionError("Only moderators can view non-published posts")

        return await self.post_repository.get_by_status(status, skip, limit)

    async def get_posts_by_tags(
        self, tags: list[str], skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by tags (only published posts)."""
        all_posts = await self.post_repository.get_by_tags(tags, skip, limit)
        return [post for post in all_posts if post.is_published]

    async def get_post_statistics(self, requester_id: int) -> dict[str, Any]:
        """Get post statistics (moderator only)."""
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester or not requester.is_moderator():
            raise PermissionError("Only moderators can view post statistics")

        total_posts = await self.post_repository.count()
        published_count = await self.post_repository.count_by_status(
            PostStatus.PUBLISHED
        )
        draft_count = await self.post_repository.count_by_status(PostStatus.DRAFT)
        archived_count = await self.post_repository.count_by_status(PostStatus.ARCHIVED)

        return {
            "total_posts": total_posts,
            "published_count": published_count,
            "draft_count": draft_count,
            "archived_count": archived_count,
            "status_distribution": {
                "published": published_count,
                "draft": draft_count,
                "archived": archived_count,
            },
        }

    async def get_user_post_statistics(
        self, user_id: int, requester_id: int
    ) -> dict[str, Any]:
        """Get post statistics for a specific user."""
        # Users can view their own stats, moderators can view any user's stats
        requester = await self.user_repository.get_by_id(requester_id)
        if not requester:
            raise ValueError("Requester not found")

        if user_id != requester_id and not requester.is_moderator():
            raise PermissionError("Users can only view their own post statistics")

        return await self.post_service.get_user_posts_stats(user_id)

    async def get_trending_posts(self, days: int = 7, limit: int = 10) -> list[Post]:
        """Get trending posts based on view count (published only)."""
        # This is a simplified implementation
        # In a real system, you might want to calculate trending based on
        # views per day, engagement, etc.
        published_posts = await self.post_repository.get_published(0, 100)

        # Sort by view count and take top posts
        trending_posts = sorted(
            published_posts, key=lambda p: p.view_count, reverse=True
        )
        return trending_posts[:limit]
