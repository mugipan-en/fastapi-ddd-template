"""Database seeding script."""

import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, create_tables
from app.domain.entities.user import User, UserRole
from app.domain.entities.post import Post, PostStatus
from app.core.security import get_password_hash


async def create_sample_users(session: AsyncSession) -> list[User]:
    """Create sample users."""
    users_data = [
        {
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin123"),
            "first_name": "Admin",
            "last_name": "User",
            "role": UserRole.ADMIN,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "moderator@example.com", 
            "hashed_password": get_password_hash("mod123"),
            "first_name": "Moderator",
            "last_name": "User",
            "role": UserRole.MODERATOR,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "user@example.com",
            "hashed_password": get_password_hash("user123"),
            "first_name": "Regular",
            "last_name": "User", 
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "john.doe@example.com",
            "hashed_password": get_password_hash("john123"),
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": False,
        },
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    await session.commit()
    
    # Refresh to get IDs
    for user in users:
        await session.refresh(user)
    
    return users


async def create_sample_posts(session: AsyncSession, users: list[User]) -> list[Post]:
    """Create sample posts."""
    posts_data = [
        {
            "title": "Welcome to FastAPI DDD Template",
            "content": """
# Welcome to FastAPI DDD Template

This is a comprehensive FastAPI template following Domain-Driven Design principles.

## Features

- **Domain-Driven Design**: Clean architecture with separated layers
- **Authentication**: JWT-based authentication with role-based access control
- **Database**: PostgreSQL with SQLModel and Alembic migrations
- **Testing**: Comprehensive test suite with pytest
- **Security**: Security best practices and vulnerability scanning
- **CI/CD**: GitHub Actions for automated testing and deployment

## Getting Started

1. Clone the repository
2. Install dependencies with `make setup`
3. Run the development server with `make dev`
4. Visit the API documentation at http://localhost:8000/docs

Happy coding! 🚀
            """.strip(),
            "slug": "welcome-to-fastapi-ddd-template",
            "excerpt": "A comprehensive FastAPI template following Domain-Driven Design principles with authentication, testing, and CI/CD.",
            "status": PostStatus.PUBLISHED,
            "tags": "fastapi,ddd,template,python",
            "view_count": 150,
            "user_id": users[0].id,  # Admin user
            "published_at": datetime.utcnow(),
        },
        {
            "title": "Understanding Domain-Driven Design",
            "content": """
# Understanding Domain-Driven Design

Domain-Driven Design (DDD) is a software development approach that focuses on modeling software to match a domain according to input from domain experts.

## Core Concepts

### Entities
Objects that have a distinct identity and lifecycle.

### Value Objects
Objects that describe some characteristics or attributes but carry no concept of identity.

### Aggregates
A cluster of domain objects that can be treated as a single unit.

### Repositories
Mechanisms for encapsulating storage, retrieval, and search behavior.

### Services
When a significant process or transformation in the domain is not a natural responsibility of an ENTITY or VALUE OBJECT.

This template demonstrates these concepts in a practical FastAPI application.
            """.strip(),
            "slug": "understanding-domain-driven-design",
            "excerpt": "Learn about Domain-Driven Design concepts and how they're implemented in this FastAPI template.",
            "status": PostStatus.PUBLISHED,
            "tags": "ddd,architecture,design-patterns",
            "view_count": 89,
            "user_id": users[1].id,  # Moderator user
            "published_at": datetime.utcnow(),
        },
        {
            "title": "Getting Started with FastAPI",
            "content": """
# Getting Started with FastAPI

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Key Features

- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase the speed to develop features by about 200% to 300%
- **Fewer bugs**: Reduce about 40% of human (developer) induced errors
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation

This template showcases many of these features in action.
            """.strip(),
            "slug": "getting-started-with-fastapi",
            "excerpt": "Learn the basics of FastAPI and explore its key features through practical examples.",
            "status": PostStatus.PUBLISHED,
            "tags": "fastapi,python,api,tutorial",
            "view_count": 234,
            "user_id": users[2].id,  # Regular user
            "published_at": datetime.utcnow(),
        },
        {
            "title": "Draft: Advanced FastAPI Patterns",
            "content": """
# Advanced FastAPI Patterns

This is a draft post about advanced patterns in FastAPI development.

## Topics to Cover

- Dependency injection patterns
- Custom middleware
- Background tasks
- Testing strategies
- Performance optimization

More content coming soon...
            """.strip(),
            "slug": "draft-advanced-fastapi-patterns",
            "excerpt": "A draft exploring advanced patterns and techniques for FastAPI development.",
            "status": PostStatus.DRAFT,
            "tags": "fastapi,advanced,patterns",
            "view_count": 5,
            "user_id": users[3].id,  # John Doe
        },
    ]
    
    posts = []
    for post_data in posts_data:
        post = Post(**post_data)
        session.add(post)
        posts.append(post)
    
    await session.commit()
    
    # Refresh to get IDs
    for post in posts:
        await session.refresh(post)
    
    return posts


async def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    # Create tables
    await create_tables()
    print("📊 Database tables created")
    
    # Create session
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        # Create sample users
        print("👥 Creating sample users...")
        users = await create_sample_users(session)
        print(f"✅ Created {len(users)} users")
        
        # Create sample posts
        print("📝 Creating sample posts...")
        posts = await create_sample_posts(session, users)
        print(f"✅ Created {len(posts)} posts")
    
    print("🎉 Database seeding completed!")
    print("\n📋 Sample Accounts:")
    print("Admin: admin@example.com / admin123")
    print("Moderator: moderator@example.com / mod123")
    print("User: user@example.com / user123")
    print("John Doe: john.doe@example.com / john123")


if __name__ == "__main__":
    asyncio.run(seed_database())