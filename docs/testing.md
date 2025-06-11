# Testing Guide

## Overview

This project follows a comprehensive testing strategy with unit tests, integration tests, and end-to-end tests. The testing framework is built on pytest with async support.

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests
│   ├── domain/             # Domain layer tests
│   ├── application/        # Application layer tests
│   └── infrastructure/     # Infrastructure layer tests
├── integration/            # Integration tests
│   ├── api/               # API endpoint tests
│   ├── database/          # Database integration tests
│   └── external/          # External service tests
├── e2e/                   # End-to-end tests
└── fixtures/              # Test data fixtures
```

### Test Types

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test system performance and scalability

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_auth_api.py

# Run specific test
pytest tests/test_auth_api.py::TestAuthAPI::test_login_success

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Test Configuration

The testing configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--disable-warnings",
    "-ra",
]
testpaths = ["tests"]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## Test Environment

### Test Database

Tests use SQLite for fast execution:

```python
# tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
```

### Environment Variables

Test environment variables are set in `conftest.py`:

```python
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
```

## Test Fixtures

### Common Fixtures

```python
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture
async def client(app, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    def get_test_db():
        return db_session

    app.dependency_overrides[get_async_session] = get_test_db

    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

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
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    login_data = {"email": test_user.email, "password": "TestPassword123"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
```

## Unit Testing

### Domain Layer Tests

Test business logic and domain rules:

```python
# tests/unit/domain/test_user_service.py
import pytest
from app.domain.services.user import UserService
from app.domain.entities.user import UserCreate, UserRole

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_user_repository):
        service = UserService(mock_user_repository)
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User"
        )

        user = await service.create_user(user_data)

        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True

    def test_validate_password_strength(self):
        service = UserService(None)

        # Valid passwords
        assert service.validate_password("StrongPass123") is True

        # Invalid passwords
        assert service.validate_password("weak") is False
        assert service.validate_password("nodigits") is False
        assert service.validate_password("NOLOWERCASE123") is False
```

### Application Layer Tests

Test use cases and application logic:

```python
# tests/unit/application/test_auth_use_cases.py
import pytest
from app.application.use_cases.auth import AuthUseCases
from app.domain.entities.user import UserLogin

class TestAuthUseCases:
    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_service, mock_user_repository, test_user):
        use_cases = AuthUseCases(mock_user_service, mock_user_repository)
        credentials = UserLogin(email="test@example.com", password="TestPassword123")

        result = await use_cases.login(credentials)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_user_service, mock_user_repository):
        use_cases = AuthUseCases(mock_user_service, mock_user_repository)
        credentials = UserLogin(email="test@example.com", password="wrongpassword")

        result = await use_cases.login(credentials)

        assert result is None
```

## Integration Testing

### API Integration Tests

Test complete API workflows:

```python
# tests/integration/api/test_auth_api.py
import pytest
from httpx import AsyncClient

class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "first_name": "New",
            "last_name": "User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == user_data["email"]

    @pytest.mark.asyncio
    async def test_login_flow(self, client: AsyncClient, test_user):
        """Test complete login flow."""
        # Login
        login_data = {"email": test_user.email, "password": "TestPassword123"}
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Access protected endpoint
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        user_data = response.json()
        assert user_data["email"] == test_user.email
```

### Database Integration Tests

Test database operations and migrations:

```python
# tests/integration/database/test_user_repository.py
import pytest
from app.infrastructure.repositories.user import SQLUserRepository
from app.domain.entities.user import UserCreate, UserRole

class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_and_retrieve_user(self, db_session):
        repository = SQLUserRepository(db_session)
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User"
        )

        # Create user
        created_user = await repository.create(user_data)
        assert created_user.id is not None

        # Retrieve user
        retrieved_user = await repository.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_user_uniqueness(self, db_session):
        repository = SQLUserRepository(db_session)
        user_data = UserCreate(
            email="duplicate@example.com",
            password="TestPassword123",
            first_name="Test",
            last_name="User"
        )

        # Create first user
        await repository.create(user_data)

        # Attempt to create duplicate
        with pytest.raises(Exception):  # Should raise integrity error
            await repository.create(user_data)
```

## Mocking and Test Doubles

### Repository Mocks

```python
# tests/conftest.py
@pytest.fixture
def mock_user_repository():
    repository = Mock(spec=UserRepository)

    async def mock_create(user_data):
        return User(
            id=1,
            email=user_data.email,
            hashed_password="hashed",
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole.USER
        )

    repository.create = AsyncMock(side_effect=mock_create)
    repository.get_by_email = AsyncMock(return_value=None)

    return repository
```

### External Service Mocks

```python
# tests/conftest.py
@pytest.fixture
def mock_email_service():
    service = Mock()
    service.send_verification_email = AsyncMock(return_value=True)
    service.send_password_reset_email = AsyncMock(return_value=True)
    return service
```

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login user at start of test."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_posts(self):
        self.client.get("/api/v1/posts")

    @task(1)
    def get_user_profile(self):
        self.client.get("/api/v1/auth/me", headers=self.headers)

    @task(1)
    def create_post(self):
        self.client.post("/api/v1/posts", json={
            "title": "Test Post",
            "content": "Test content",
            "tags": "test"
        }, headers=self.headers)
```

Run performance tests:
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## Test Data Management

### Factory Pattern

```python
# tests/factories.py
import factory
from app.domain.entities.user import User, UserRole

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = UserRole.USER
    is_active = True
    is_verified = False

class AdminUserFactory(UserFactory):
    role = UserRole.ADMIN
    is_verified = True
```

### Using Factories in Tests

```python
# tests/test_example.py
from tests.factories import UserFactory, AdminUserFactory

def test_user_creation():
    user = UserFactory()
    assert user.role == UserRole.USER

def test_admin_permissions():
    admin = AdminUserFactory()
    assert admin.role == UserRole.ADMIN
    assert admin.is_verified is True
```

## Coverage Reporting

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
]
show_missing = true
precision = 2
```

### Generating Reports

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Generate XML report (for CI)
pytest --cov=app --cov-report=xml

# View coverage in terminal
pytest --cov=app --cov-report=term-missing
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install uv
        uv pip install --system -e ".[dev,lint,security]"

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
        JWT_SECRET_KEY: test-jwt-secret-key
      run: |
        pytest --cov=app --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Writing Guidelines

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **One Assertion Per Test**: Focus on testing one thing
3. **Descriptive Test Names**: Clearly describe what is being tested
4. **Test Edge Cases**: Include boundary conditions and error cases
5. **Use Fixtures**: Reduce code duplication with reusable fixtures
6. **Mock External Dependencies**: Isolate units under test
7. **Test Behavior, Not Implementation**: Focus on what, not how

### Example: Well-Structured Test

```python
class TestUserRegistration:
    @pytest.mark.asyncio
    async def test_register_user_with_valid_data_creates_user_successfully(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        }

        # Act
        response = await client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["user"]["email"] == user_data["email"]
        assert response_data["user"]["full_name"] == "John Doe"
        assert "access_token" in response_data
```

### Test Maintenance

1. **Regular Cleanup**: Remove obsolete tests
2. **Update Test Data**: Keep test data relevant
3. **Refactor Common Patterns**: Extract reusable test utilities
4. **Monitor Test Performance**: Keep tests fast
5. **Review Test Coverage**: Ensure adequate coverage of critical paths
