"""Post domain service."""

import re
from typing import Optional, List
from datetime import datetime

from app.domain.entities.post import Post, PostCreate, PostUpdate, PostStatus
from app.domain.entities.user import User
from app.domain.repositories.post import PostRepository
from app.domain.repositories.user import UserRepository


class PostService:
    """Post domain service."""
    
    def __init__(self, post_repository: PostRepository, user_repository: UserRepository):
        self.post_repository = post_repository
        self.user_repository = user_repository
    
    async def create_post(self, post_data: PostCreate, user_id: int) -> Post:
        """Create a new post with validation."""
        # Validate user exists and is active
        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Validate post data
        if not post_data.title.strip():
            raise ValueError("Post title cannot be empty")
        
        if not post_data.content.strip():
            raise ValueError("Post content cannot be empty")
        
        # Generate slug from title
        slug = self._generate_slug(post_data.title)
        
        # Ensure slug is unique
        existing_post = await self.post_repository.get_by_slug(slug)
        if existing_post:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        # Generate excerpt if not provided
        excerpt = self._generate_excerpt(post_data.content)
        
        # Create post
        post_dict = post_data.model_dump()
        post_dict["slug"] = slug
        post_dict["excerpt"] = excerpt
        
        return await self.post_repository.create(PostCreate.model_validate(post_dict), user_id)
    
    async def update_post(self, post_id: int, post_data: PostUpdate, user_id: int) -> Optional[Post]:
        """Update post with authorization check."""
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            return None
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check authorization
        if not user.can_edit_post(post):
            raise PermissionError("User cannot edit this post")
        
        # Update excerpt if content is being updated
        if post_data.content:
            post_data.excerpt = self._generate_excerpt(post_data.content)
        
        # Update timestamp
        post_data.updated_at = datetime.utcnow()
        
        return await self.post_repository.update(post_id, post_data)
    
    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete post with authorization check."""
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            return False
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check authorization
        if not user.can_delete_post(post):
            raise PermissionError("User cannot delete this post")
        
        return await self.post_repository.delete(post_id)
    
    async def publish_post(self, post_id: int, user_id: int) -> Optional[Post]:
        """Publish post with authorization check."""
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            return None
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check authorization
        if not user.can_edit_post(post):
            raise PermissionError("User cannot publish this post")
        
        return await self.post_repository.publish(post_id)
    
    async def archive_post(self, post_id: int, user_id: int) -> Optional[Post]:
        """Archive post with authorization check."""
        post = await self.post_repository.get_by_id(post_id)
        if not post:
            return None
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check authorization (only admins and moderators can archive)
        if not user.is_moderator():
            raise PermissionError("Only moderators can archive posts")
        
        return await self.post_repository.archive(post_id)
    
    async def get_post_with_view_increment(self, post_id: int) -> Optional[Post]:
        """Get post and increment view count."""
        post = await self.post_repository.get_by_id(post_id)
        if post and post.is_published:
            await self.post_repository.increment_view_count(post_id)
            # Return updated post
            return await self.post_repository.get_by_id(post_id)
        return post
    
    async def search_posts(self, query: str, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Post]:
        """Search posts with optional user filtering."""
        posts = await self.post_repository.search(query, skip, limit)
        
        # Filter by user if specified
        if user_id:
            posts = [post for post in posts if post.user_id == user_id]
        
        # Only return published posts for non-owners
        if not user_id:
            posts = [post for post in posts if post.is_published]
        
        return posts
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        return slug[:100]
    
    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """Generate excerpt from content."""
        # Remove HTML tags if any
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Truncate and add ellipsis
        if len(clean_content) <= max_length:
            return clean_content
        
        # Find the last space before the limit
        truncated = clean_content[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return f"{truncated}..."
    
    async def get_user_posts_stats(self, user_id: int) -> dict:
        """Get statistics for user's posts."""
        total_posts = await self.post_repository.count_by_user(user_id)
        published_posts = await self.post_repository.count_by_status(PostStatus.PUBLISHED)
        draft_posts = await self.post_repository.count_by_status(PostStatus.DRAFT)
        
        return {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": draft_posts,
        }