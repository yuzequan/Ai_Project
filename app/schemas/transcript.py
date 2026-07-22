from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TranscriptBase(BaseModel):
    session_id: int
    speaker_id: str = Field(..., max_length=100)
    speaker_role: str = Field(..., pattern="^(teacher|student)$")
    content: str
    start_time: datetime
    end_time: datetime
    is_teacher: bool = False


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptUpdate(BaseModel):
    speaker_id: str | None = Field(None, max_length=100)
    speaker_role: str | None = Field(None, pattern="^(teacher|student)$")
    content: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_teacher: bool | None = None


class TranscriptResponse(TranscriptBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
