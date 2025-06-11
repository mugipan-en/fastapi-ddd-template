"""Common API schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""

    items: list[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number", ge=1)
    size: int = Field(description="Items per page", ge=1)
    pages: int = Field(description="Total number of pages")

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        pages = (total + size - 1) // size if total > 0 else 1
        return cls(items=items, total=total, page=page, size=size, pages=pages)


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: str | None = Field(default=None, description="Detailed error information")
    timestamp: str = Field(description="Error timestamp")


class SuccessResponse(BaseModel):
    """Success response schema."""

    success: bool = Field(default=True)
    message: str = Field(description="Success message")
    data: dict[str, Any] | None = Field(default=None, description="Additional data")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Check timestamp")
    checks: dict[str, str] = Field(description="Individual service checks")
