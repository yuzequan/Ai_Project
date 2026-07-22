from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoreDimensionDetail(BaseModel):
    raw_score: Decimal
    weighted_score: Decimal
    weight: Decimal
    breakdown: Optional[Dict[str, Any]] = None


class EvaluationResultBase(BaseModel):
    session_id: int
    overall_score: Optional[Decimal] = Field(None, decimal_places=2)
    attendance_score: Optional[Decimal] = Field(None, decimal_places=2)
    professionalism_score: Optional[Decimal] = Field(None, decimal_places=2)
    engagement_score: Optional[Decimal] = Field(None, decimal_places=2)
    software_skill_score: Optional[Decimal] = Field(None, decimal_places=2)
    details: Optional[Dict[str, Any]] = None
    evaluated_at: Optional[datetime] = None
    status: str = Field(default="pending", pattern="^(pending|completed|failed)$")


class EvaluationResultCreate(EvaluationResultBase):
    pass


class EvaluationResultUpdate(BaseModel):
    overall_score: Optional[Decimal] = Field(None, decimal_places=2)
    attendance_score: Optional[Decimal] = Field(None, decimal_places=2)
    professionalism_score: Optional[Decimal] = Field(None, decimal_places=2)
    engagement_score: Optional[Decimal] = Field(None, decimal_places=2)
    software_skill_score: Optional[Decimal] = Field(None, decimal_places=2)
    details: Optional[Dict[str, Any]] = None
    evaluated_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed|failed)$")


class EvaluationResultResponse(EvaluationResultBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultDetailResponse(EvaluationResultResponse):
    dimension_details: Optional[Dict[str, ScoreDimensionDetail]] = None
