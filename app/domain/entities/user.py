"""User entity."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .post import Post


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserBase(SQLModel):
    """Base user model."""
    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class User(UserBase, table=True):
    """User entity."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def is_moderator(self) -> bool:
        """Check if user is moderator."""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    def can_edit_post(self, post: "Post") -> bool:
        """Check if user can edit a post."""
        return self.is_moderator() or post.user_id == self.id
    
    def can_delete_post(self, post: "Post") -> bool:
        """Check if user can delete a post."""
        return self.is_admin() or post.user_id == self.id


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(SQLModel):
    """User update model."""
    email: Optional[str] = Field(default=None, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    is_verified: Optional[bool] = Field(default=None)


class UserResponse(UserBase):
    """User response model."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]


class UserLogin(SQLModel):
    """User login model."""
    email: str = Field(max_length=255)
    password: str = Field(max_length=100)