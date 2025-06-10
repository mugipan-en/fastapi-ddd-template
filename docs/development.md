# Development Guide

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13+ (for production)
- Redis 6+ (for caching and background tasks)
- Git
- uv (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mugipan-en/fastapi-ddd-template.git
   cd fastapi-ddd-template
   ```

2. **Install uv (recommended):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev,lint,security]"
   ```

4. **Environment setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup:**
   ```bash
   # Create database tables
   make migrate

   # Seed sample data (optional)
   make seed
   ```

6. **Run the application:**
   ```bash
   make dev
   ```

The application will be available at `http://localhost:8000`.

## Project Structure

```
fastapi-ddd-template/
├── app/                    # Application code
│   ├── core/              # Core utilities (config, database, security)
│   ├── domain/            # Domain layer (entities, repositories, services)
│   ├── application/       # Application layer (use cases)
│   ├── infrastructure/    # Infrastructure layer (repositories, external)
│   ├── presentation/      # Presentation layer (API, schemas)
│   └── main.py           # Application entry point
├── tests/                 # Test files
├── alembic/              # Database migrations
├── docs/                 # Documentation
├── docker/               # Docker configuration
├── scripts/              # Utility scripts
├── .env.example          # Environment template
├── pyproject.toml        # Project configuration
└── Makefile              # Development commands
```

## Development Workflow

### 1. Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following the coding standards**

3. **Run tests:**
   ```bash
   make test
   ```

4. **Run linting and formatting:**
   ```bash
   make lint
   make format
   ```

### 2. Database Changes

1. **Create migration:**
   ```bash
   make migration message="Add new table"
   ```

2. **Apply migration:**
   ```bash
   make migrate
   ```

3. **Rollback if needed:**
   ```bash
   alembic downgrade -1
   ```

### 3. Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_auth_api.py

# Run specific test
pytest tests/test_auth_api.py::TestAuthAPI::test_login_success
```

### 4. Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type checking
make typecheck

# Security check
make security
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Setup development environment |
| `make dev` | Run development server |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make lint` | Run linting |
| `make format` | Format code |
| `make typecheck` | Run type checking |
| `make security` | Run security checks |
| `make migrate` | Run database migrations |
| `make migration` | Create new migration |
| `make seed` | Seed sample data |
| `make clean` | Clean cache and build files |
| `make build` | Build Docker image |
| `make docker-dev` | Run with Docker Compose |

## Environment Variables

### Required Variables

```bash
# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379
```

### Optional Variables

```bash
# Application
APP_NAME=FastAPI DDD Template
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Email (if using email features)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Python Test Explorer
- GitLens
- Thunder Client (for API testing)

Workspace settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. Set Python interpreter to `.venv/bin/python`
2. Configure code style to use Black
3. Enable pytest as test runner
4. Install Python Requirements plugin

## Debugging

### VS Code Debugging

Launch configuration (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/uvicorn",
            "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

### Logging

The application uses structured logging. Debug information can be enabled by setting:
```bash
LOG_LEVEL=DEBUG
```

## API Documentation

When running in development mode, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Administration

### Alembic Commands

```bash
# Generate migration
alembic revision --autogenerate -m "Migration message"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

### Data Seeding

```bash
# Seed sample data
python scripts/seed_data.py

# Or using make
make seed
```

## Performance Monitoring

### Local Monitoring

```bash
# Access metrics endpoint
curl http://localhost:8000/metrics

# Health check
curl http://localhost:8000/health
```

### Profiling

For performance profiling, you can use:
```bash
pip install py-spy
py-spy top --pid <process-id>
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <pid>
   ```

2. **Database connection errors:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Check database exists

3. **Migration errors:**
   - Check database connection
   - Ensure no conflicting migrations
   - Review migration files

4. **Import errors:**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check PYTHONPATH

### Getting Help

1. Check the documentation
2. Look for similar issues in GitHub Issues
3. Create a new issue with:
   - Python version
   - OS details
   - Error messages
   - Steps to reproduce

## Contributing

Please read [Contributing Guide](contributing.md) for details on our code of conduct and the process for submitting pull requests.