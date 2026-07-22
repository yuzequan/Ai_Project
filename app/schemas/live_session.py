from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LiveSessionBase(BaseModel):
    course_id: int
    teacher_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    platform: str = Field(..., max_length=50)
    room_id: str = Field(..., max_length=100)
    recording_url: Optional[str] = Field(None, max_length=500)


class LiveSessionCreate(LiveSessionBase):
    pass


class LiveSessionUpdate(BaseModel):
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    platform: Optional[str] = Field(None, max_length=50)
    room_id: Optional[str] = Field(None, max_length=100)
    recording_url: Optional[str] = Field(None, max_length=500)


class LiveSessionResponse(LiveSessionBase):
    id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LiveSessionDetailResponse(LiveSessionResponse):
    member_events_count: int = 0
    transcripts_count: int = 0
    comments_count: int = 0
    overall_score: Optional[Decimal] = None
    evaluation_status: Optional[str] = None
