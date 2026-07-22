from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BehaviorRule(Base):
    __tablename__ = "behavior_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_type: Mapped[str] = mapped_column(
        Enum("attendance", "professionalism", "software_usage", name="behavior_rule_type"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    condition: Mapped[dict] = mapped_column(JSON, nullable=False)

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
