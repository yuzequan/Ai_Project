from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    actual_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    notified_group: Mapped[str] = mapped_column(String(200), nullable=False)
    notified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum("sent", "failed", name="alert_status"),
        nullable=False,
        default="failed",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    session: Mapped["LiveSession"] = relationship("LiveSession", back_populates="alerts")
