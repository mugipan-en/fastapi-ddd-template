"""SQLAlchemy implementation of PostRepository."""

from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, desc, select, update

from app.domain.entities.post import Post, PostCreate, PostStatus, PostUpdate
from app.domain.repositories.post import PostRepository


class SQLPostRepository(PostRepository):
    """SQLAlchemy implementation of PostRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post_data: PostCreate, user_id: int) -> Post:
        """Create a new post."""
        # Generate slug from title
        slug = self._generate_slug(post_data.title)

        # Ensure slug is unique
        existing_post = await self.get_by_slug(slug)
        if existing_post:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        # Create post
        post_dict = post_data.model_dump()
        post_dict.update(
            {
                "user_id": user_id,
                "slug": slug,
                "excerpt": self._generate_excerpt(post_data.content),
            }
        )

        post = Post(**post_dict)
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        """Get post by ID."""
        stmt = select(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Post | None:
        """Get post by slug."""
        stmt = select(Post).where(Post.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all posts with pagination."""
        stmt = select(Post).offset(skip).limit(limit).order_by(desc(Post.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by user."""
        stmt = (
            select(Post)
            .where(Post.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Post.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self, status: PostStatus, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by status."""
        stmt = (
            select(Post)
            .where(Post.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Post.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get published posts."""
        return await self.get_by_status(PostStatus.PUBLISHED, skip, limit)

    async def update(self, post_id: int, post_data: PostUpdate) -> Post | None:
        """Update post."""
        # Get current post
        post = await self.get_by_id(post_id)
        if not post:
            return None

        # Update fields
        update_dict = post_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()

            # Generate new excerpt if content is updated
            if "content" in update_dict:
                update_dict["excerpt"] = self._generate_excerpt(update_dict["content"])

            stmt = update(Post).where(Post.id == post_id).values(**update_dict)
            await self.session.execute(stmt)
            await self.session.commit()

            # Return updated post
            return await self.get_by_id(post_id)

        return post

    async def delete(self, post_id: int) -> bool:
        """Delete post."""
        stmt = delete(Post).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def publish(self, post_id: int) -> Post | None:
        """Publish post."""
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(
                status=PostStatus.PUBLISHED,
                published_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(post_id)
        return None

    async def archive(self, post_id: int) -> Post | None:
        """Archive post."""
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(status=PostStatus.ARCHIVED, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(post_id)
        return None

    async def increment_view_count(self, post_id: int) -> None:
        """Increment post view count."""
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(view_count=Post.view_count + 1)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[Post]:
        """Search posts by title and content."""
        search_term = f"%{query}%"
        stmt = (
            select(Post)
            .where(
                or_(
                    Post.title.ilike(search_term),
                    Post.content.ilike(search_term),
                    Post.tags.ilike(search_term),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(Post.created_at))
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tags(
        self, tags: list[str], skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by tags."""
        # Simple tag search - in production, you might want a separate tags table
        tag_conditions = [Post.tags.ilike(f"%{tag}%") for tag in tags]
        stmt = (
            select(Post)
            .where(or_(*tag_conditions))
            .offset(skip)
            .limit(limit)
            .order_by(desc(Post.created_at))
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Get total post count."""
        stmt = select(func.count(Post.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_user(self, user_id: int) -> int:
        """Get post count by user."""
        stmt = select(func.count(Post.id)).where(Post.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_status(self, status: PostStatus) -> int:
        """Get post count by status."""
        stmt = select(func.count(Post.id)).where(Post.status == status)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        import re

        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        slug = slug.strip("-")

        # Limit length
        return slug[:100]

    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """Generate excerpt from content."""
        import re

        # Remove HTML tags if any
        clean_content = re.sub(r"<[^>]+>", "", content)

        # Truncate and add ellipsis
        if len(clean_content) <= max_length:
            return clean_content

        # Find the last space before the limit
        truncated = clean_content[:max_length]
        last_space = truncated.rfind(" ")

        if last_space > 0:
            truncated = truncated[:last_space]

        return f"{truncated}..."
