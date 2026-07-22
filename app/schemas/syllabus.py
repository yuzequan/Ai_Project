from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SyllabusBase(BaseModel):
    course_id: int
    section: str = Field(..., max_length=200)
    key_points: List[str]
    required_duration: int = Field(..., ge=1)
    order: int = 0


class SyllabusCreate(SyllabusBase):
    pass


class SyllabusUpdate(BaseModel):
    course_id: Optional[int] = None
    section: Optional[str] = Field(None, max_length=200)
    key_points: Optional[List[str]] = None
    required_duration: Optional[int] = Field(None, ge=1)
    order: Optional[int] = None


class SyllabusResponse(SyllabusBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
