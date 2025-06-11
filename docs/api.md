# API Documentation

## Overview

The FastAPI DDD Template provides a RESTful API for user and content management. All endpoints follow REST conventions and include comprehensive OpenAPI documentation.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

- **Access Token**: Short-lived token for API access (30 minutes)
- **Refresh Token**: Long-lived token for getting new access tokens (7 days)

### Authentication Header

```http
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication (`/api/v1/auth`)

#### Register User

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_verified": false
  }
}
```

#### Login

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_verified": false
  }
}
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User

```http
GET /api/v1/auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Change Password

```http
POST /api/v1/auth/change-password
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "OldPass123",
  "new_password": "NewPass123"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

#### Verify Account

```http
POST /api/v1/auth/verify
```

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Account verified successfully"
}
```

### User Management (`/api/v1/users`)

#### Get All Users (Admin Only)

```http
GET /api/v1/users?skip=0&limit=20
```

**Headers:** `Authorization: Bearer <admin_token>`

**Query Parameters:**
- `skip` (int): Number of users to skip (default: 0)
- `limit` (int): Maximum number of users to return (default: 20, max: 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

#### Get User by ID

```http
GET /api/v1/users/{user_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User Profile

```http
PUT /api/v1/users/me
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Get User Statistics (Admin Only)

```http
GET /api/v1/users/stats
```

**Headers:** `Authorization: Bearer <admin_token>`

**Response (200):**
```json
{
  "total_users": 100,
  "active_users": 95,
  "verified_users": 80,
  "admin_users": 2,
  "moderator_users": 5,
  "regular_users": 93
}
```

#### Delete User (Admin Only)

```http
DELETE /api/v1/users/{user_id}
```

**Headers:** `Authorization: Bearer <admin_token>`

**Response (200):**
```json
{
  "message": "User deleted successfully"
}
```

### Posts (`/api/v1/posts`)

#### Get All Posts

```http
GET /api/v1/posts?skip=0&limit=20&status=published
```

**Query Parameters:**
- `skip` (int): Number of posts to skip (default: 0)
- `limit` (int): Maximum number of posts to return (default: 20, max: 100)
- `status` (string): Filter by status (published, draft, archived)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Welcome to FastAPI DDD Template",
      "slug": "welcome-to-fastapi-ddd-template",
      "excerpt": "A comprehensive FastAPI template...",
      "status": "published",
      "view_count": 150,
      "tags": "fastapi,ddd,template",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "published_at": "2024-01-01T00:00:00Z",
      "author": {
        "id": 1,
        "full_name": "John Doe",
        "email": "admin@example.com"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

#### Get Post by ID

```http
GET /api/v1/posts/{post_id}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Welcome to FastAPI DDD Template",
  "content": "# Welcome to FastAPI DDD Template...",
  "slug": "welcome-to-fastapi-ddd-template",
  "excerpt": "A comprehensive FastAPI template...",
  "status": "published",
  "view_count": 151,
  "tags": "fastapi,ddd,template",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "published_at": "2024-01-01T00:00:00Z",
  "author": {
    "id": 1,
    "full_name": "John Doe",
    "email": "admin@example.com"
  }
}
```

#### Create Post

```http
POST /api/v1/posts
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "My New Post",
  "content": "This is the content of my new post...",
  "status": "draft",
  "tags": "tutorial,example"
}
```

**Response (201):**
```json
{
  "id": 2,
  "title": "My New Post",
  "slug": "my-new-post",
  "excerpt": "This is the content of my new post...",
  "status": "draft",
  "view_count": 0,
  "tags": "tutorial,example",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "published_at": null,
  "user_id": 1
}
```

#### Update Post

```http
PUT /api/v1/posts/{post_id}
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated Post Title",
  "content": "Updated content...",
  "status": "published",
  "tags": "tutorial,example,updated"
}
```

**Response (200):**
```json
{
  "id": 2,
  "title": "Updated Post Title",
  "slug": "updated-post-title",
  "excerpt": "Updated content...",
  "status": "published",
  "view_count": 0,
  "tags": "tutorial,example,updated",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z",
  "published_at": "2024-01-01T13:00:00Z",
  "user_id": 1
}
```

#### Delete Post

```http
DELETE /api/v1/posts/{post_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Post deleted successfully"
}
```

#### Publish Post

```http
POST /api/v1/posts/{post_id}/publish
```

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 2,
  "title": "My Post",
  "status": "published",
  "published_at": "2024-01-01T13:00:00Z"
}
```

#### Search Posts

```http
GET /api/v1/posts/search?q=fastapi&skip=0&limit=20
```

**Query Parameters:**
- `q` (string): Search query
- `skip` (int): Number of posts to skip (default: 0)
- `limit` (int): Maximum number of posts to return (default: 20)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Welcome to FastAPI DDD Template",
      "slug": "welcome-to-fastapi-ddd-template",
      "excerpt": "A comprehensive FastAPI template...",
      "status": "published",
      "view_count": 150,
      "tags": "fastapi,ddd,template",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

## Health Check

#### Health Status

```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Error Responses

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Authenticated**: Higher limits for authenticated users
- **Admin**: No rate limiting

## Interactive Documentation

- **Swagger UI**: `/docs` (development only)
- **ReDoc**: `/redoc` (development only)
- **OpenAPI Schema**: `/api/v1/openapi.json`
