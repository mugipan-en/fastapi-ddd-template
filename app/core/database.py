"""Database configuration and session management."""

from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql://").replace("postgresql+asyncpg://", "postgresql://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async engine for application
async_engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync session factory (for migrations and seeds)
SessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session() -> Session:
    """Get sync database session."""
    return SessionLocal()


async def create_tables() -> None:
    """Create database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_tables() -> None:
    """Drop database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)