from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


class PageResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
