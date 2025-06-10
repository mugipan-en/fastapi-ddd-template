# Architecture Guide

## Overview

This FastAPI application follows Domain-Driven Design (DDD) principles with a clean architecture approach. The codebase is organized into distinct layers, each with specific responsibilities.

## Architecture Layers

### 1. Domain Layer (`app/domain/`)

The core business logic layer that contains:

- **Entities** (`entities/`): Core business objects
  - `User`: User management with roles and authentication
  - `Post`: Content management with status and publishing

- **Repositories** (`repositories/`): Abstract interfaces for data access
  - `UserRepository`: User data access interface
  - `PostRepository`: Post data access interface

- **Services** (`services/`): Business logic and domain rules
  - `UserService`: User-related business operations
  - `PostService`: Post-related business operations

### 2. Application Layer (`app/application/`)

Orchestrates domain objects and implements use cases:

- **Use Cases** (`use_cases/`): Application-specific business logic
  - `AuthUseCases`: Authentication and authorization workflows
  - `UserUseCases`: User management workflows
  - `PostUseCases`: Content management workflows

### 3. Infrastructure Layer (`app/infrastructure/`)

Implements external concerns:

- **Repositories** (`repositories/`): Concrete implementations of domain repositories
  - `SQLUserRepository`: PostgreSQL/SQLite implementation
  - `SQLPostRepository`: PostgreSQL/SQLite implementation

- **Database** (`database/`): Database-specific implementations
- **External** (`external/`): Third-party service integrations
- **Tasks** (`tasks/`): Background task implementations

### 4. Presentation Layer (`app/presentation/`)

Handles external communication:

- **API** (`api/`): REST API endpoints
  - `auth.py`: Authentication endpoints
  - `users.py`: User management endpoints
  - `posts.py`: Content management endpoints

- **Schemas** (`schemas/`): Request/response models
  - Pydantic models for API validation
  - Data transfer objects (DTOs)

- **Dependencies** (`dependencies/`): Dependency injection
  - Authentication dependencies
  - Database session management

### 5. Core Layer (`app/core/`)

Cross-cutting concerns:

- `config.py`: Application configuration
- `database.py`: Database connection and session management
- `security.py`: Authentication and encryption utilities
- `logging.py`: Structured logging configuration

## Key Design Patterns

### Dependency Inversion

- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)
- Abstractions don't depend on details

### Repository Pattern

- Encapsulates data access logic
- Provides a uniform interface for data operations
- Enables easy testing with mock implementations

### Use Case Pattern

- Encapsulates application-specific business rules
- Orchestrates domain objects to fulfill specific requirements
- Provides clear entry points for application functionality

### Dependency Injection

- Dependencies are injected at runtime
- Enables loose coupling and testability
- Implemented using FastAPI's dependency system

## Data Flow

```
HTTP Request → API Router → Use Case → Domain Service → Repository → Database
                    ↓
Response Schema ← Use Case ← Domain Entity ← Repository ← Database
```

1. **Request**: HTTP request arrives at API endpoint
2. **Routing**: FastAPI routes to appropriate handler
3. **Validation**: Pydantic validates request data
4. **Use Case**: Application layer orchestrates business logic
5. **Domain**: Business rules are applied
6. **Repository**: Data is persisted or retrieved
7. **Response**: Results are formatted and returned

## Database Design

### Entity Relationships

```
User (1) → (N) Post
  ↓
  UserRole (Enum)

Post → PostStatus (Enum)
```

### Key Entities

- **User**: Authentication, authorization, profile management
- **Post**: Content creation, publishing workflow, status management

## Security Architecture

### Authentication Flow

1. User provides credentials
2. System validates against database
3. JWT tokens are generated (access + refresh)
4. Tokens are used for subsequent requests
5. Token validation on protected endpoints

### Authorization Levels

- **USER**: Basic user operations
- **MODERATOR**: Content moderation capabilities
- **ADMIN**: Full system administration

## Scalability Considerations

### Horizontal Scaling

- Stateless application design
- Database connection pooling
- Session-based authentication with JWT

### Performance Optimizations

- Async/await for I/O operations
- Database query optimization
- Caching strategies (Redis integration ready)
- Connection pooling

### Monitoring & Observability

- Structured logging with context
- Prometheus metrics integration
- Health check endpoints
- Error tracking and alerting

## Testing Strategy

### Unit Tests

- Domain logic testing
- Service layer testing
- Repository interface testing

### Integration Tests

- API endpoint testing
- Database integration testing
- External service testing

### Test Database

- SQLite for fast test execution
- Separate test fixtures and data
- Isolated test environments

## Development Principles

1. **Single Responsibility**: Each class has one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable for base types
4. **Interface Segregation**: Many specific interfaces over one general interface
5. **Dependency Inversion**: Depend on abstractions, not concretions

## Migration Strategy

### Database Migrations

- Alembic for schema versioning
- Automatic migration generation
- Rollback capabilities
- Environment-specific migrations

### Application Updates

- Blue-green deployment support
- Database migration automation
- Health check integration
- Graceful shutdown handling