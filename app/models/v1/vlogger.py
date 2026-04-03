from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func

from app.db.connection import Base

if TYPE_CHECKING:
    from app.models.v1.vlog import Vlog


class Vlogger(Base):
    __tablename__ = "vloggers"

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    vlogs: Mapped[list["Vlog"]] = relationship(
        back_populates="vlogger", cascade="all, delete-orphan"
    )
