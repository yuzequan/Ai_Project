from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    session_id: int
    user_id: str = Field(..., max_length=100)
    user_role: str = Field(..., pattern="^(teacher|student)$")
    content: str
    timestamp: datetime
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    replies: List["CommentResponse"] = []

    model_config = ConfigDict(from_attributes=True)
