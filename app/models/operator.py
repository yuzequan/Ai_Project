from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    feishu_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    responsible_subject: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    feishu_webhook: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

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

    # Relationships
    live_sessions: Mapped[list["LiveSession"]] = relationship(
        "LiveSession", back_populates="operator"
    )
