from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func, Index
from pydantic import computed_field

from app.db.connection import Base

if TYPE_CHECKING:
    from app.models.vlogger import Vlogger


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)

    vlogs: Mapped[list["Vlog"]] = relationship(
        back_populates="country", cascade="all, delete-orphan"
    )


class Vlog(Base):
    __tablename__ = "vlogs"
    __table_args__ = (Index("ix_vlogs_vlogger_country", "vlogger_id", "country_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    vlogger_id: Mapped[int] = mapped_column(
        ForeignKey("vloggers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    youtube_video_id: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    vlogger: Mapped["Vlogger"] = relationship(back_populates="vlogs")
    country: Mapped["Country"] = relationship(back_populates="vlogs")

    @computed_field
    @property
    def youtube_video_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.youtube_video_id}"
