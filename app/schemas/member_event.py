from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemberEventBase(BaseModel):
    session_id: int
    user_id: str = Field(..., max_length=100)
    user_role: str = Field(..., pattern="^(teacher|student)$")
    event_type: str = Field(..., pattern="^(join|leave)$")
    event_time: datetime


class MemberEventCreate(MemberEventBase):
    pass


class MemberEventBulkCreate(BaseModel):
    session_id: int
    events: list = Field(..., min_length=1)


class MemberEventResponse(MemberEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
