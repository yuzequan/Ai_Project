from typing import Optional

from pydantic import BaseModel, ConfigDict


class OperatorBase(BaseModel):
    name: str
    feishu_user_id: str
    department: Optional[str] = None
    responsible_subject: Optional[str] = None
    feishu_webhook: Optional[str] = None
    is_active: bool = True


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    feishu_user_id: Optional[str] = None
    department: Optional[str] = None
    responsible_subject: Optional[str] = None
    feishu_webhook: Optional[str] = None
    is_active: Optional[bool] = None


class OperatorResponse(OperatorBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
