from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Syllabus(Base):
    __tablename__ = "syllabus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(200), nullable=False)
    key_points: Mapped[list] = mapped_column(JSON, nullable=False)
    required_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
