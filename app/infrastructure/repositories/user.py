"""SQLAlchemy implementation of UserRepository."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, update

from app.core.security import get_password_hash
from app.domain.entities.user import User, UserCreate, UserUpdate
from app.domain.repositories.user import UserRepository


class SQLUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Hash password
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_data.password)
        del user_dict["password"]
        # Create user
        user = User(**user_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update user."""
        # Get current user
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Update fields
        update_dict = user_data.model_dump(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()

            stmt = update(User).where(User.id == user_id).values(**update_dict)
            await self.session.execute(stmt)
            await self.session.commit()

            # Return updated user
            return await self.get_by_id(user_id)

        return user

    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        stmt = (
            update(User).where(User.id == user_id).values(last_login=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def verify_user(self, user_id: int) -> User | None:
        """Verify user account."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(user_id)
        return None

    async def deactivate_user(self, user_id: int) -> User | None:
        """Deactivate user account."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount > 0:
            return await self.get_by_id(user_id)
        return None

    async def get_by_role(
        self, role: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get users by role."""
        stmt = (
            select(User)
            .where(User.role == role)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Get total user count."""
        stmt = select(func.count(User.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        stmt = select(func.count(User.id)).where(User.email == email)
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0
