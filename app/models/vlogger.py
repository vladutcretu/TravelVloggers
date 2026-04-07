from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, ForeignKey, Integer

from app.db.connection import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vlog import Vlog


class Vlogger(Base):
    __tablename__ = "vloggers"

    # common fields
    id: Mapped[int] = mapped_column(primary_key=True)

    youtube_channel_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    youtube_channel_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    youtube_channel_url: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    youtube_avatar_url: Mapped[str] = mapped_column(String(255), nullable=False)

    # fields used in v2 only
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    youtube_subscribers_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    youtube_uploads_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )

    # audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="vlogger")
    vlogs: Mapped[list["Vlog"]] = relationship(
        back_populates="vlogger", cascade="all, delete-orphan"
    )
