from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertConfigBase(BaseModel):
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    threshold: Decimal = Field(default=Decimal("60.00"), decimal_places=2)
    feishu_webhook: str = Field(..., max_length=500)
    feishu_group_name: Optional[str] = Field(None, max_length=200)
    is_active: bool = True


class AlertConfigCreate(AlertConfigBase):
    pass


class AlertConfigUpdate(BaseModel):
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    threshold: Optional[Decimal] = Field(None, decimal_places=2)
    feishu_webhook: Optional[str] = Field(None, max_length=500)
    feishu_group_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class AlertConfigResponse(AlertConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
