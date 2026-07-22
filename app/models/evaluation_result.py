from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    attendance_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    professionalism_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    engagement_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    software_skill_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "completed", "failed", name="evaluation_status"),
        nullable=False,
        default="pending",
    )

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
    session: Mapped["LiveSession"] = relationship(
        "LiveSession", back_populates="evaluation_result"
    )
