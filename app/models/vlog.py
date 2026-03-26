from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.db.connection import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
