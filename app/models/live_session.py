from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    teacher_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    operator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("operators.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    room_id: Mapped[str] = mapped_column(String(100), nullable=False)
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

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
    member_events: Mapped[List["MemberEvent"]] = relationship(
        "MemberEvent", back_populates="session", cascade="all, delete-orphan"
    )
    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript", back_populates="session", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="session", cascade="all, delete-orphan"
    )
    evaluation_result: Mapped[Optional["EvaluationResult"]] = relationship(
        "EvaluationResult", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="session", cascade="all, delete-orphan"
    )
    operator: Mapped[Optional["Operator"]] = relationship(
        "Operator", back_populates="live_sessions"
    )
