from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    teacher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    threshold: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("60.00")
    )
    feishu_webhook: Mapped[str] = mapped_column(String(500), nullable=False)
    feishu_group_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
