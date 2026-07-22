from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    user_role: Mapped[str] = mapped_column(
        Enum("teacher", "student", name="comment_user_role"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    session: Mapped["LiveSession"] = relationship("LiveSession", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment", remote_side="Comment.id", back_populates="replies"
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan"
    )
