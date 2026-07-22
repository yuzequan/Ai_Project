from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class BehaviorRuleBase(BaseModel):
    rule_type: str = Field(..., pattern="^(attendance|professionalism|software_usage)$")
    description: str = Field(..., max_length=500)
    weight: Decimal = Field(..., decimal_places=2)
    condition: Dict[str, Any]


class BehaviorRuleCreate(BehaviorRuleBase):
    pass


class BehaviorRuleUpdate(BaseModel):
    rule_type: Optional[str] = Field(None, pattern="^(attendance|professionalism|software_usage)$")
    description: Optional[str] = Field(None, max_length=500)
    weight: Optional[Decimal] = Field(None, decimal_places=2)
    condition: Optional[Dict[str, Any]] = None


class BehaviorRuleResponse(BehaviorRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
