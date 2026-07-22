from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    session_id: int
    alert_type: str = Field(..., max_length=50)
    threshold: Decimal = Field(..., decimal_places=2)
    actual_score: Decimal = Field(..., decimal_places=2)
    notified_group: str = Field(..., max_length=200)
    notified_at: Optional[datetime] = None
    status: str = Field(default="failed", pattern="^(sent|failed)$")


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    alert_type: Optional[str] = Field(None, max_length=50)
    threshold: Optional[Decimal] = Field(None, decimal_places=2)
    actual_score: Optional[Decimal] = Field(None, decimal_places=2)
    notified_group: Optional[str] = Field(None, max_length=200)
    notified_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(sent|failed)$")


class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
