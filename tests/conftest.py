"""Test configuration and fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Set test environment variables before importing app modules
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["ALLOWED_HOSTS"] = '["localhost", "127.0.0.1", "test", "testserver"]'

from app.core.database import get_async_session
from app.domain.entities.post import Post, PostCreate, PostStatus
from app.domain.entities.user import User, UserCreate, UserRole
from app.infrastructure.repositories.post import SQLPostRepository
from app.infrastructure.repositories.user import SQLUserRepository
from app.main import create_app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

# Test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    return create_app()


@pytest_asyncio.fixture
async def client(app, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""

    def get_test_db():
        return db_session

    app.dependency_overrides[get_async_session] = get_test_db

    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def user_repository(db_session: AsyncSession) -> SQLUserRepository:
    """Create a test user repository."""
    return SQLUserRepository(db_session)


@pytest_asyncio.fixture
async def post_repository(db_session: AsyncSession) -> SQLPostRepository:
    """Create a test post repository."""
    return SQLPostRepository(db_session)


@pytest_asyncio.fixture
async def test_user(user_repository: SQLUserRepository) -> User:
    """Create a test user."""
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123",
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
    )
    return await user_repository.create(user_data)


@pytest_asyncio.fixture
async def test_admin(user_repository: SQLUserRepository) -> User:
    """Create a test admin user."""
    user_data = UserCreate(
        email="admin@example.com",
        password="adminpassword123",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    return await user_repository.create(user_data)


@pytest_asyncio.fixture
async def test_post(post_repository: SQLPostRepository, test_user: User) -> Post:
    """Create a test post."""
    post_data = PostCreate(
        title="Test Post",
        content="This is a test post content.",
        status=PostStatus.PUBLISHED,
        tags="test,example",
    )
    return await post_repository.create(post_data, test_user.id)


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    login_data = {"email": test_user.email, "password": "TestPassword123"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin user."""
    login_data = {"email": test_admin.email, "password": "adminpassword123"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
